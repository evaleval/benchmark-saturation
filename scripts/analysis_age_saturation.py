#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "numpy",
#   "pandas",
#   "matplotlib",
#   "scipy",
#   "statsmodels",
# ]
# ///
#
# Run with: uv run --script scripts/analysis_age_saturation.py
"""
Analyze whether benchmark age explains saturation and score dispersion.

Outputs:
- results/age_saturation_analysis.csv
- results/age_saturation_summary.txt
- results/visualizations/age_saturation_scatter.png

Requires: pandas, numpy, matplotlib
Optional: scipy (for p-values & Spearman), statsmodels (for LOWESS)
"""

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats  # type: ignore
except Exception:  # pragma: no cover - optional
    stats = None

try:
    from statsmodels.nonparametric.smoothers_lowess import lowess  # type: ignore
except Exception:  # pragma: no cover - optional
    lowess = None

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt


def _coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _parse_as_of(as_of: Optional[str]) -> pd.Timestamp:
    if not as_of:
        return pd.Timestamp.today().normalize()
    return pd.to_datetime(as_of, errors="raise").normalize()


def _find_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    if np.allclose(np.nanstd(x), 0) or np.allclose(np.nanstd(y), 0):
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _linear_fit(x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    if x.size < 2:
        return {"slope": float("nan"), "intercept": float("nan"), "r2": float("nan")}
    slope, intercept = np.polyfit(x, y, 1)
    y_hat = intercept + slope * x
    ss_res = np.nansum((y - y_hat) ** 2)
    ss_tot = np.nansum((y - np.nanmean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def _trend_line(x: np.ndarray, y: np.ndarray, trend: str) -> Tuple[np.ndarray, np.ndarray]:
    if x.size < 2:
        return np.array([]), np.array([])
    order = np.argsort(x)
    x_sorted, y_sorted = x[order], y[order]
    if trend == "lowess" and lowess is not None:
        smoothed = lowess(y_sorted, x_sorted, frac=0.6, return_sorted=True)
        return smoothed[:, 0], smoothed[:, 1]
    # default linear
    slope, intercept = np.polyfit(x_sorted, y_sorted, 1)
    return x_sorted, intercept + slope * x_sorted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        default="data/manual_annotation_data.csv",
        help="Input CSV path",
    )
    ap.add_argument(
        "--out_dir",
        default="results",
        help="Output directory root (default: results)",
    )
    ap.add_argument(
        "--age_source",
        choices=["months", "release_date"],
        default="months",
        help="How to compute age (default: months column)",
    )
    ap.add_argument(
        "--months_col",
        default="Time since benchmark release (in months)",
        help="Column for months since release",
    )
    ap.add_argument(
        "--release_col",
        default="Released Date",
        help="Column for benchmark release date",
    )
    ap.add_argument(
        "--as_of",
        default=None,
        help="Date for age computation when using release_date (YYYY-MM-DD)",
    )
    ap.add_argument(
        "--variance_metric",
        choices=["std", "range"],
        default="std",
        help="Top-N score dispersion metric to use",
    )
    ap.add_argument(
        "--saturation_threshold",
        type=float,
        default=0.8,
        help="Threshold for saturation index if interpreted labels unavailable",
    )
    ap.add_argument(
        "--trend",
        choices=["linear", "lowess"],
        default="linear",
        help="Trend line type (lowess requires statsmodels)",
    )
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    df.columns = [c.strip() for c in df.columns]

    # Compute benchmark age (years)
    if args.age_source == "months":
        if args.months_col not in df.columns:
            raise ValueError(f"Missing months column: {args.months_col}")
        age_years = _coerce_numeric(df[args.months_col]) / 12.0
        as_of_date = None
    else:
        if args.release_col not in df.columns:
            raise ValueError(f"Missing release date column: {args.release_col}")
        as_of_date = _parse_as_of(args.as_of)
        release_dt = pd.to_datetime(df[args.release_col], errors="coerce")
        age_years = (as_of_date - release_dt).dt.days / 365.25

    df["Benchmark age (years)"] = age_years

    # Dispersion metric (top-5)
    top_cols = [f"top model {i}" for i in range(1, 6)]
    have_top_cols = all(c in df.columns for c in top_cols)
    scores = None
    if have_top_cols:
        scores = df[top_cols].apply(_coerce_numeric)

    std_col = _find_col(df, ["Std Dev (top-5 models)", "Std Dev"])
    range_col = _find_col(
        df,
        [
            "Range of scores (s_max - s_min; top-5 models)",
            "Range of scores (s_max - s_min)",
        ],
    )

    if args.variance_metric == "std":
        if std_col is not None:
            dispersion = _coerce_numeric(df[std_col])
        elif scores is not None:
            dispersion = scores.std(axis=1, ddof=0)
        else:
            raise ValueError("Cannot compute std dev: no std column or top model columns")
        dispersion_label = "Top-5 score std dev"
    else:
        if range_col is not None:
            dispersion = _coerce_numeric(df[range_col])
        elif scores is not None:
            dispersion = scores.max(axis=1) - scores.min(axis=1)
        else:
            raise ValueError("Cannot compute range: no range column or top model columns")
        dispersion_label = "Top-5 score range"

    df[dispersion_label] = dispersion

    # Saturation index
    if "Saturation Index" not in df.columns:
        raise ValueError("Missing 'Saturation Index' column")
    saturation = _coerce_numeric(df["Saturation Index"])

    # Saturated vs unsaturated
    sat_interp_col = _find_col(df, ["Saturation Index (interpreted)"])
    if sat_interp_col is not None:
        interp = (
            df[sat_interp_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace("_", " ")
            .str.replace("-", " ")
        )
        saturated = interp.isin(["high", "very high"])
    else:
        saturated = saturation >= args.saturation_threshold
    df["Saturated"] = saturated

    # Analysis
    out_root = Path(args.out_dir)
    viz_dir = out_root / "visualizations"
    viz_dir.mkdir(parents=True, exist_ok=True)

    # Age vs saturation
    mask_sat = age_years.notna() & saturation.notna()
    x_sat = age_years[mask_sat].to_numpy(dtype=float)
    y_sat = saturation[mask_sat].to_numpy(dtype=float)

    pearson_sat = _safe_corr(x_sat, y_sat)
    spearman_sat = None
    pearson_sat_p = None
    spearman_sat_p = None
    if stats is not None and x_sat.size >= 2:
        pearson_sat, pearson_sat_p = stats.pearsonr(x_sat, y_sat)
        spearman_sat, spearman_sat_p = stats.spearmanr(x_sat, y_sat)

    lin_sat = _linear_fit(x_sat, y_sat)

    # Age vs dispersion
    mask_disp = age_years.notna() & dispersion.notna()
    x_disp = age_years[mask_disp].to_numpy(dtype=float)
    y_disp = dispersion[mask_disp].to_numpy(dtype=float)

    pearson_disp = _safe_corr(x_disp, y_disp)
    spearman_disp = None
    pearson_disp_p = None
    spearman_disp_p = None
    if stats is not None and x_disp.size >= 2:
        pearson_disp, pearson_disp_p = stats.pearsonr(x_disp, y_disp)
        spearman_disp, spearman_disp_p = stats.spearmanr(x_disp, y_disp)

    lin_disp = _linear_fit(x_disp, y_disp)

    # Save analysis table
    analysis_df = df[[
        "Name",
        "Benchmark age (years)",
        dispersion_label,
        "Saturation Index",
        "Saturated",
    ]].copy()

    analysis_path = out_root / "age_saturation_analysis.csv"
    analysis_df.to_csv(analysis_path, index=False)

    # Summary text
    summary_lines = []
    summary_lines.append("Age vs saturation index")
    summary_lines.append(f"n={x_sat.size}")
    summary_lines.append(f"pearson_r={pearson_sat:.4f}")
    if pearson_sat_p is not None:
        summary_lines.append(f"pearson_p={pearson_sat_p:.4g}")
    if spearman_sat is not None:
        summary_lines.append(f"spearman_r={spearman_sat:.4f}")
        summary_lines.append(f"spearman_p={spearman_sat_p:.4g}")
    summary_lines.append(f"linear_slope={lin_sat['slope']:.4f}")
    summary_lines.append(f"linear_r2={lin_sat['r2']:.4f}")
    summary_lines.append("")
    summary_lines.append(f"Age vs {dispersion_label}")
    summary_lines.append(f"n={x_disp.size}")
    summary_lines.append(f"pearson_r={pearson_disp:.4f}")
    if pearson_disp_p is not None:
        summary_lines.append(f"pearson_p={pearson_disp_p:.4g}")
    if spearman_disp is not None:
        summary_lines.append(f"spearman_r={spearman_disp:.4f}")
        summary_lines.append(f"spearman_p={spearman_disp_p:.4g}")
    summary_lines.append(f"linear_slope={lin_disp['slope']:.4f}")
    summary_lines.append(f"linear_r2={lin_disp['r2']:.4f}")

    if args.age_source == "release_date":
        summary_lines.append("")
        summary_lines.append(f"as_of_date={as_of_date.date().isoformat()}")

    summary_path = out_root / "age_saturation_summary.txt"
    summary_path.write_text("\n".join(summary_lines))

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=150)

    # Colors
    colors = np.where(saturated.to_numpy(), "#d95f02", "#1b9e77")
    mask_disp_np = mask_disp.to_numpy()
    mask_sat_np = mask_sat.to_numpy()

    # Age vs dispersion
    ax = axes[0]
    ax.scatter(
        x_disp,
        y_disp,
        c=colors[mask_disp_np],
        s=36,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5,
    )
    tx, ty = _trend_line(x_disp, y_disp, args.trend)
    if tx.size > 0:
        ax.plot(tx, ty, color="#4c4c4c", linewidth=1.5, linestyle="--")
    ax.set_xlabel("Benchmark age (years)")
    ax.set_ylabel(dispersion_label)
    ax.set_title("Age vs score dispersion")

    # Age vs saturation index
    ax = axes[1]
    ax.scatter(
        x_sat,
        y_sat,
        c=colors[mask_sat_np],
        s=36,
        alpha=0.8,
        edgecolor="white",
        linewidth=0.5,
    )
    tx, ty = _trend_line(x_sat, y_sat, args.trend)
    if tx.size > 0:
        ax.plot(tx, ty, color="#4c4c4c", linewidth=1.5, linestyle="--")
    ax.set_xlabel("Benchmark age (years)")
    ax.set_ylabel("Saturation Index")
    ax.set_ylim(0, 1)
    ax.set_title("Age vs saturation index")

    # Legend
    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#1b9e77", label="Unsaturated", markersize=6),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#d95f02", label="Saturated", markersize=6),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False)

    fig.tight_layout(rect=[0, 0.05, 1, 1])

    fig_path = viz_dir / "age_saturation_scatter.png"
    fig.savefig(fig_path)


if __name__ == "__main__":
    main()
