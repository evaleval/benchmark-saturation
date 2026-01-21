#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "numpy",
#   "seaborn",
#   "matplotlib",
#   "statsmodels",
# ]
# ///
#
# Run with: uv run --script scripts/plot_age_testsize_relationship.py
"""
Single-figure plot: age vs saturation with LOWESS lines per test-size bin.

Outputs:
- results/visualizations/age_testsize_saturation.png
"""

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


TEST_SIZE_EDGES = [30, 993, 3000, 12086, 601728]
TEST_SIZE_LABELS = ["Small", "Medium", "Large", "Very large"]


def _to_numeric_n_test(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.replace(
        {
            "": np.nan,
            "nan": np.nan,
            "None": np.nan,
            "N/A": np.nan,
            "NA": np.nan,
            "dynamic": np.nan,
            "Dynamic": np.nan,
            "varies": np.nan,
            "Varies": np.nan,
            "-": np.nan,
        }
    )
    s = s.str.replace(",", "", regex=False).str.replace(" ", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def _format_count(n: float) -> str:
    n_int = int(round(n))
    if n_int >= 1000:
        return f"{int(round(n_int / 1000.0))}k"
    return f"{n_int}"


def _bin_test_size(n_test: pd.Series) -> pd.Series:
    # Fixed boundaries computed from dataset percentiles of log10(test size),
    # then converted back to raw test-size counts for interpretability.
    # log10 edges: [1.4771, 2.9971, 3.4771, 4.0823, 5.7794]
    # raw edges:  [30, 993, 3000, 12086, 601728]
    return pd.cut(
        n_test,
        bins=TEST_SIZE_EDGES,
        labels=TEST_SIZE_LABELS,
        include_lowest=True,
        ordered=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        default="data/manual_annotation_data.csv",
        help="Input CSV path",
    )
    ap.add_argument(
        "--out",
        default="results/visualizations/age_testsize_saturation.png",
        help="Output figure path",
    )
    ap.add_argument(
        "--months_col",
        default="Time since benchmark release (in months)",
        help="Column for months since release",
    )
    ap.add_argument(
        "--release_col",
        default="Released Date",
        help="Column for release date if months missing",
    )
    ap.add_argument(
        "--as_of",
        default="2026-01-21",
        help="Reference date for age computation (YYYY-MM-DD)",
    )
    # keep CLI minimal for LOWESS-only plot
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["Name"]).drop_duplicates(subset=["Name"])

    # Age in years
    age_years = pd.Series([np.nan] * len(df))
    if args.months_col in df.columns:
        age_years = pd.to_numeric(df[args.months_col], errors="coerce") / 12.0
    if args.release_col in df.columns:
        release_dt = pd.to_datetime(df[args.release_col], errors="coerce")
        ref_date = pd.to_datetime(args.as_of)
        age_from_release = (ref_date - release_dt).dt.days / 365.25
        age_years = age_years.where(age_years.notna(), age_from_release)

    # Saturation index
    sat = pd.to_numeric(df["Saturation Index"], errors="coerce")

    # Test size -> log10 -> bins
    n_test = _to_numeric_n_test(df["Quantity of test samples"])
    log_n = np.log10(n_test.where(n_test > 0))
    size_bin = _bin_test_size(n_test)

    plot_df = pd.DataFrame(
        {
            "Age (years)": age_years,
            "Saturation Index": sat,
            "log10(Test size)": log_n,
            "Test size bin": size_bin,
        }
    ).dropna(subset=["Age (years)", "Saturation Index", "log10(Test size)"])

    sns.set_style("whitegrid")
    palette = sns.color_palette("Set2")

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    # Build explicit legend labels with ranges and n
    counts = plot_df["Test size bin"].value_counts()
    present = [c for c in plot_df["Test size bin"].cat.categories if counts.get(c, 0) > 0]
    label_map = {}
    for i, label in enumerate(TEST_SIZE_LABELS):
        lo = TEST_SIZE_EDGES[i]
        hi = TEST_SIZE_EDGES[i + 1]
        range_str = f"{_format_count(lo)}-{_format_count(hi)}"
        label_map[label] = f"{label} ({range_str}, n={int(counts.get(label, 0))})"
    plot_df["Test size label"] = plot_df["Test size bin"].map(label_map)

    # LOWESS lines per test-size bin with light scatter
    palette = sns.color_palette("Set2", n_colors=len(present))
    order = present

    ax.scatter(
        plot_df["Age (years)"],
        plot_df["Saturation Index"],
        s=20,
        color="#9aa0a6",
        alpha=0.4,
        linewidth=0,
        zorder=1,
    )

    for i, cat in enumerate(order):
        sub = plot_df[plot_df["Test size bin"] == cat]
        if sub.shape[0] < 3:
            continue
        sns.regplot(
            data=sub,
            x="Age (years)",
            y="Saturation Index",
            scatter=False,
            lowess=True,
            line_kws={"linewidth": 2.0, "color": palette[i]},
            ax=ax,
            label=label_map.get(cat, str(cat)),
        )

    ax.set_title("Saturation vs Age, stratified by test-set size", fontweight="bold")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(title="Test size bin", frameon=False, loc="lower right")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path)


if __name__ == "__main__":
    main()
