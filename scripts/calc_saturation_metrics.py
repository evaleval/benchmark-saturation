#!/usr/bin/env python3
"""
Add uncertainty-aware saturation metrics based on top-5 model performance.

Requires input CSV columns:
- top model 1, top model 2, top model 3, top model 4, top model 5
- Quantity of test samples  (n_test)

Adds columns:
- n_test_used                (numeric n used for SE computations)
- n_test_imputed             (1 if missing/dynamic was imputed, else 0)
- Mean (top-5 models)
- Std Dev
- Range of scores (s_max - s_min)
- Mean (top-3 models)
- Std Dev (top-3 models)
- Range of scores (top-3 s_max - s_min)
- SE_delta                   (SE of top-vs-5th difference, using n_eff)
- R_norm                     ((s1 - s5) / SE_delta)
- Saturation Index           (exp(-(R_norm**2)))

Notes:
- Assumes scores are in percentage points (0..100). Converts to proportions (0..1) for SE.
- Saturation Index is only computed when all 5 scores are present and n_test_used is valid.
"""

import argparse
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from scipy.stats import spearmanr


def to_numeric_n_test(series: pd.Series) -> pd.Series:
    """
    Convert Quantity of test samples to numeric where possible.
    Handles strings with commas/spaces; non-numeric becomes NaN.
    """
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="inp",
        help="Input CSV path",
        default="/Users/user/PycharmProjects/benchmark-saturation2/data/manual_annotation_data.csv",
    )
    ap.add_argument(
        "--out",
        dest="out",
        help="Output CSV path",
        default="/Users/user/PycharmProjects/benchmark-saturation2/data/manual_annotation_data.csv",
    )

    ap.add_argument(
        "--n_col",
        default="Quantity of test samples",
        help='Column name for n_test (default: "Quantity of test samples")',
    )
    ap.add_argument(
        "--default_n",
        type=float,
        default=1000.0,
        help="Fallback default n_test if median cannot be computed (default: 1000)",
    )
    ap.add_argument(
        "--ddof",
        type=int,
        default=0,
        help="Std dev ddof: 0=population, 1=sample (default: 0)",
    )
    ap.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Exponent for effective test size n_eff = n**alpha (default: 0.5 => sqrt(n))",
    )
    args = ap.parse_args()

    df = pd.read_csv(args.inp)

    score_cols = [f"top model {i}" for i in range(1, 6)]
    missing_scores = [c for c in score_cols if c not in df.columns]
    if missing_scores:
        raise ValueError(f"Missing required score columns: {missing_scores}")

    if args.n_col not in df.columns:
        raise ValueError(f'Missing required n_test column: "{args.n_col}"')

    # Ensure numeric scores (expected in percent points, e.g., 93.5)
    for c in score_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    scores = df[score_cols]
    n_present = scores.notna().sum(axis=1)
    has_all5 = n_present.eq(5)

    # Parse n_test
    n_numeric = to_numeric_n_test(df[args.n_col])
    n_median = float(n_numeric.dropna().median()) if n_numeric.dropna().shape[0] > 0 else np.nan
    if np.isnan(n_median) or n_median <= 0:
        n_median = float(args.default_n)

    # Impute n_test where missing/non-numeric
    n_used = n_numeric.copy()
    imputed_mask = n_used.isna() | (n_used <= 0)
    n_used.loc[imputed_mask] = n_median

    df["n_test_used"] = n_used.astype(float)
    df["n_test_imputed"] = np.where(imputed_mask, 1, 0)

    # Descriptive stats — top 5
    df["Mean (top-5 models)"] = scores.mean(axis=1, skipna=True).round(2)
    df["Std Dev"] = scores.std(axis=1, skipna=True, ddof=args.ddof).round(2)
    df["Range of scores (s_max - s_min)"] = (
        scores.max(axis=1, skipna=True) - scores.min(axis=1, skipna=True)
    ).round(2)

    # Descriptive stats — top 3
    top3_cols = [f"top model {i}" for i in range(1, 4)]
    top3_scores = df[top3_cols]
    df["Mean (top-3 models)"] = top3_scores.mean(axis=1, skipna=True).round(2)
    df["Std Dev (top-3 models)"] = top3_scores.std(axis=1, skipna=True, ddof=args.ddof).round(2)
    df["Range of scores (top-3 s_max - s_min)"] = (
        top3_scores.max(axis=1, skipna=True) - top3_scores.min(axis=1, skipna=True)
    ).round(2)

    # --- Uncertainty-aware saturation metrics ---
    # Convert scores from percent (0..100) to proportion (0..1)
    s1 = df["top model 1"] / 100.0
    s5 = df["top model 5"] / 100.0
    n = df["n_test_used"]

    # Validity for SE computations
    valid_n = n.notna() & (n > 0)
    valid_scores = has_all5 & s1.notna() & s5.notna()

    # Effective test size to reduce n impact
    # (alpha=0.5 => sqrt(n))
    n_eff = np.where(valid_n, np.power(n, args.alpha), np.nan)

    # Clip proportions to [0,1] to avoid negative SE from bad data
    s1c = s1.clip(0.0, 1.0)
    s5c = s5.clip(0.0, 1.0)

    # SE_delta = sqrt( s1(1-s1)/n_eff + s5(1-s5)/n_eff )
    se_delta = np.sqrt((s1c * (1.0 - s1c)) / n_eff + (s5c * (1.0 - s5c)) / n_eff)

    # R_norm = (s1 - s5) / SE_delta
    delta = (s1c - s5c)

    # Avoid divide-by-zero
    safe = valid_scores & valid_n & np.isfinite(se_delta) & (se_delta > 0)

    df["SE_delta"] = np.where(safe, se_delta, np.nan)
    df["R_norm"] = np.where(safe, delta / se_delta, np.nan)

    # Saturation Index = exp(-(R_norm^2))
    df["Saturation Index"] = np.where(safe, np.exp(-(df["R_norm"] ** 2)), np.nan)

    df.to_csv(args.out, index=False)


def compute_sindex(df, k=5, alpha=0.5):
    """
    Compute saturation index for arbitrary k and alpha.
    """
    score_cols = [f"top model {i}" for i in range(1, k + 1)]
    scores = df[score_cols]

    s1 = df["top model 1"] / 100.0
    sk = df[f"top model {k}"] / 100.0
    n = df["n_test_used"]

    valid = s1.notna() & sk.notna() & (n > 0)

    n_eff = np.power(n, alpha)

    s1c = s1.clip(0, 1)
    skc = sk.clip(0, 1)

    se_delta = np.sqrt((s1c * (1 - s1c)) / n_eff + (skc * (1 - skc)) / n_eff)

    delta = s1c - skc
    safe = valid & np.isfinite(se_delta) & (se_delta > 0)

    r_norm = np.where(safe, delta / se_delta, np.nan)
    s_index = np.where(safe, np.exp(-(r_norm ** 2)), np.nan)

    return pd.Series(s_index, index=df.index)


def assign_bin(s):
    """
    Assign saturation bins.
    """
    bins = []
    for val in s:
        if pd.isna(val):
            bins.append(np.nan)
        elif val < 0.01:
            bins.append("very low")
        elif val < 0.3:
            bins.append("low")
        elif val < 0.7:
            bins.append("moderate")
        elif val < 0.9:
            bins.append("high")
        else:
            bins.append("very high")
    return pd.Series(bins, index=s.index)


def run_sensitivity_analysis(df):
    print("\n=== Sensitivity Analysis ===\n")

    # --- k sensitivity ---
    print("Running k sensitivity (k=3 vs k=5)...")

    s_k3 = compute_sindex(df, k=3, alpha=0.5)
    s_k5 = compute_sindex(df, k=5, alpha=0.5)

    valid = s_k3.notna() & s_k5.notna()

    corr_k, _ = spearmanr(s_k3[valid], s_k5[valid])
    print(f"Spearman correlation (k=3 vs k=5): {corr_k:.4f}")

    bins_k3 = assign_bin(s_k3)
    bins_k5 = assign_bin(s_k5)

    same_bin = (bins_k3 == bins_k5).sum()
    total = valid.sum()

    print(f"Same bin: {same_bin}/{total} ({same_bin/total:.2%})")

    # --- alpha sensitivity ---
    print("\nRunning alpha sensitivity (0, 0.5, 1)...")

    s_a0 = compute_sindex(df, k=5, alpha=0)
    s_a05 = compute_sindex(df, k=5, alpha=0.5)
    s_a1 = compute_sindex(df, k=5, alpha=1)

    valid = s_a05.notna() & s_a0.notna() & s_a1.notna()

    corr_a0, _ = spearmanr(s_a05[valid], s_a0[valid])
    corr_a1, _ = spearmanr(s_a05[valid], s_a1[valid])

    print(f"Spearman correlation (alpha=0.5 vs 0): {corr_a0:.4f}")
    print(f"Spearman correlation (alpha=0.5 vs 1): {corr_a1:.4f}")

    bins_a05 = assign_bin(s_a05)
    bins_a0 = assign_bin(s_a0)
    bins_a1 = assign_bin(s_a1)

    same_bin_a0 = (bins_a05 == bins_a0).sum()
    same_bin_a1 = (bins_a05 == bins_a1).sum()

    print(f"Same bin (alpha=0.5 vs 0): {same_bin_a0}/{valid.sum()} ({same_bin_a0/valid.sum():.2%})")
    print(f"Same bin (alpha=0.5 vs 1): {same_bin_a1}/{valid.sum()} ({same_bin_a1/valid.sum():.2%})")

    # --- Summary table ---
    summary = pd.DataFrame({
        "benchmark": df["Name"],
        "S_k3": s_k3,
        "S_k5": s_k5,
        "S_a0": s_a0,
        "S_a05": s_a05,
        "S_a1": s_a1,
    })

    print("\nSample of sensitivity results:")
    print(summary.head())

    # --- Plot comparisons ---
    print("\nGenerating plots...")

    plt.figure()
    plt.scatter(s_k5, s_k3)
    plt.xlabel("S_index (k=5)")
    plt.ylabel("S_index (k=3)")
    plt.title("k sensitivity")
    plt.savefig("sensitivity_k.png")

    plt.figure()
    plt.scatter(s_a05, s_a0)
    plt.xlabel("S_index (alpha=0.5)")
    plt.ylabel("S_index (alpha=0)")
    plt.title("alpha sensitivity (0.5 vs 0)")
    plt.savefig("sensitivity_alpha_0.png")

    plt.figure()
    plt.scatter(s_a05, s_a1)
    plt.xlabel("S_index (alpha=0.5)")
    plt.ylabel("S_index (alpha=1)")
    plt.title("alpha sensitivity (0.5 vs 1)")
    plt.savefig("sensitivity_alpha_1.png")

    print("Plots saved as PNG files.")


def generate_saturation_score_charts(df, out_prefix="saturation_scores"):
    """
    Generate saturation score visualizations for all benchmarks:
    1. Sorted horizontal bar chart
    2. Sorted vertical bar chart
    3. Scatter plot of saturation scores
    4. Export sorted benchmark scores as CSV

    Uses benchmark colors based on:
    - Saturation Index (interpreted)

    Shortens benchmark names to the text before the first colon.
    """
    print("\n=== Generating saturation score charts ===\n")

    required_cols = ["Name", "Saturation Index", "Saturation Index (interpreted)"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for plotting: {missing}")

    score_df = df[required_cols].copy()
    score_df = score_df.dropna(subset=["Saturation Index"])
    score_df = score_df.sort_values("Saturation Index", ascending=False).reset_index(drop=True)

    # Shorten names: keep text before colon if present
    def shorten_name(name):
        if pd.isna(name):
            return name

        name = str(name)

        # --- Explicit mappings (ONLY these benchmarks) ---
        if name == "MGSM (Multilingual Grade School Math (MGSM) benchmark)":
            return "MGSM"

        if name.strip().startswith("Arena-Hard"):
            return "Arena-Hard"

        if name == "Multilingual Competition Level Math (MCLM)":
            return "MCLM"

        if name == "Multilingual Massive Multitask Language Understanding (MMMLU)":
            return "MMMLU"

        # --- Fallback (keep original behavior) ---
        if ":" in name:
            return name.split(":")[0].strip()

        return name

    score_df["Short Name"] = score_df["Name"].apply(shorten_name)

    # Color map by interpreted saturation level
    color_map = {
        "Very high": "#b2182b",
        "High": "#ef8a62",
        "Moderate": "#fddbc7",
        "Low": "#67a9cf",
        "Very low": "#2166ac",
    }

    # Fallback color for unexpected labels
    score_df["Color"] = score_df["Saturation Index (interpreted)"].map(color_map).fillna("#888888")

    # Save sorted values for appendix/table use
    csv_path = f"{out_prefix}_sorted.csv"
    score_df.to_csv(csv_path, index=False)
    print(f"Saved sorted saturation scores to: {csv_path}")

    # ---------- Horizontal bar chart ----------
    plt.figure(figsize=(12, 16))
    plt.barh(score_df["Short Name"], score_df["Saturation Index"], color=score_df["Color"])
    plt.xlabel("Saturation Index")
    plt.ylabel("Benchmark")
    plt.title("Saturation scores across benchmarks")
    plt.gca().invert_yaxis()  # highest score at top

    # Legend
    handles = [
        plt.Line2D([0], [0], marker='s', linestyle='', markersize=10, label=label, color=color)
        for label, color in color_map.items()
    ]
    plt.legend(handles=handles, title="Saturation level", loc="lower right")

    plt.tight_layout()
    barh_path = f"{out_prefix}_barh.png"
    plt.savefig(barh_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved horizontal bar chart to: {barh_path}")

    # ---------- Vertical bar chart ----------
    plt.figure(figsize=(18, 6))
    plt.bar(score_df["Short Name"], score_df["Saturation Index"], color=score_df["Color"])
    plt.ylabel("Saturation Index")
    plt.xlabel("Benchmark")
    plt.title("Saturation scores across benchmarks")
    plt.xticks(rotation=90)

    handles = [
        plt.Line2D([0], [0], marker='s', linestyle='', markersize=10, label=label, color=color)
        for label, color in color_map.items()
    ]
    plt.legend(handles=handles, title="Saturation level", loc="upper right")

    plt.tight_layout()
    barv_path = f"{out_prefix}_barv.png"
    plt.savefig(barv_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved vertical bar chart to: {barv_path}")

    # ---------- Scatter plot ----------
    plt.figure(figsize=(12, 5))
    x = np.arange(len(score_df))
    plt.scatter(x, score_df["Saturation Index"], c=score_df["Color"], s=40)

    plt.xticks(x, score_df["Short Name"], rotation=90)
    plt.ylabel("Saturation Index")
    plt.xlabel("Benchmark")
    plt.title("Saturation scores across benchmarks")

    handles = [
        plt.Line2D([0], [0], marker='o', linestyle='', markersize=8, label=label, color=color)
        for label, color in color_map.items()
    ]
    plt.legend(handles=handles, title="Saturation level", loc="upper right")

    plt.tight_layout()
    scatter_path = f"{out_prefix}_scatter.png"
    plt.savefig(scatter_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved scatter plot to: {scatter_path}")

    # ---------- Optional histogram (kept from before if useful) ----------
    plt.figure(figsize=(8, 5))
    plt.hist(score_df["Saturation Index"], bins=15)
    plt.xlabel("Saturation Index")
    plt.ylabel("Number of benchmarks")
    plt.title("Distribution of saturation scores")
    plt.tight_layout()
    hist_path = f"{out_prefix}_hist.png"
    plt.savefig(hist_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved histogram to: {hist_path}")

    # ---------- Quick summary ----------
    print("\nTop 10 most saturated benchmarks:")
    print(score_df[["Short Name", "Saturation Index", "Saturation Index (interpreted)"]].head(10).to_string(index=False))

    print("\nBottom 10 least saturated benchmarks:")
    print(score_df[["Short Name", "Saturation Index", "Saturation Index (interpreted)"]].tail(10).to_string(index=False))


if __name__ == "__main__":
    main()

    # Reload dataframe
    df = pd.read_csv(
        "/Users/user/PycharmProjects/benchmark-saturation2/data/manual_annotation_data.csv")

    # run_sensitivity_analysis
    generate_saturation_score_charts(df)
