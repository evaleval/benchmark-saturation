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
        default="/Users/user/PycharmProjects/benchmark-saturation/data/manual_benchmark_annotations/benchmark_annotations.csv",
    )
    ap.add_argument(
        "--out",
        dest="out",
        help="Output CSV path",
        default="/Users/user/PycharmProjects/benchmark-saturation/data/manual_benchmark_annotations/benchmark_annotations.csv",
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


if __name__ == "__main__":
    main()
