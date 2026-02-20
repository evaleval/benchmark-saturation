"""
Statistical utilities for computing saturation metrics.

This module provides functions for calculating saturation indices based on
the statistical framework for benchmark saturation analysis.
"""

import math
from typing import List, Tuple


def compute_n_eff(n: int, alpha: float = 0.5) -> float:
    """
    Compute effective sample size.
    
    Args:
        n: Actual test set size
        alpha: Exponent for effective sample size (default 0.5)
               alpha ∈ [0,1], where alpha=0.5 gives n_eff = sqrt(n)
    
    Returns:
        Effective sample size n_eff = n^alpha
    """
    if n <= 0:
        raise ValueError(f"Test set size must be positive, got {n}")
    if not 0 <= alpha <= 1:
        raise ValueError(f"Alpha must be in [0, 1], got {alpha}")
    
    return n ** alpha


def compute_standard_error(score: float, n_eff: float) -> float:
    """
    Compute standard error for a model score.
    
    Args:
        score: Model performance score (assumed to be in [0, 1])
        n_eff: Effective sample size
    
    Returns:
        Standard error SE(s) ≈ sqrt(s(1-s) / n_eff)
    """
    if not 0 <= score <= 1:
        raise ValueError(f"Score must be in [0, 1], got {score}")
    if n_eff <= 0:
        raise ValueError(f"Effective sample size must be positive, got {n_eff}")
    
    # For scores at boundaries (0 or 1), variance is 0
    if score == 0 or score == 1:
        return 0.0
    
    return math.sqrt(score * (1 - score) / n_eff)


def compute_se_delta(s1: float, s5: float, n_eff: float) -> float:
    """
    Compute standard error of the difference between top and 5th model.
    
    Args:
        s1: Top model score
        s5: 5th model score
        n_eff: Effective sample size
    
    Returns:
        SE_Δ ≈ sqrt(SE(s1)^2 + SE(s5)^2)
    """
    se1 = compute_standard_error(s1, n_eff)
    se5 = compute_standard_error(s5, n_eff)
    
    return math.sqrt(se1**2 + se5**2)


def compute_normalized_range(s1: float, s5: float, se_delta: float) -> float:
    """
    Compute normalized score range.
    
    Args:
        s1: Top model score
        s5: 5th model score
        se_delta: Standard error of the difference
    
    Returns:
        R_norm = (s1 - s5) / SE_Δ
        
    Note:
        When se_delta is 0 (all models have identical scores at boundaries),
        returns 0.0 to indicate maximum compression.
    """
    if se_delta == 0:
        # Edge case: both s1 and s5 are at 0 or 1, no variation possible
        return 0.0
    
    return (s1 - s5) / se_delta


def compute_saturation_index(r_norm: float) -> float:
    """
    Compute saturation index from normalized range.
    
    Args:
        r_norm: Normalized score range
    
    Returns:
        S_index = exp(-R_norm^2) ∈ [0, 1]
        
    Higher values indicate stronger saturation (top models are clustered
    within evaluation uncertainty).
    """
    return math.exp(-(r_norm ** 2))


def categorize_saturation(s_index: float) -> str:
    """
    Categorize saturation level based on S_index value.
    
    Args:
        s_index: Saturation index in [0, 1]
    
    Returns:
        One of: "very_low", "low", "moderate", "high", "very_high"
        
    Categories:
        - very_low: S_index < 0.01 (strong discriminative power)
        - low: 0.01 ≤ S_index < 0.3 (some clustering, meaningful separations remain)
        - moderate: 0.3 ≤ S_index < 0.7 (compression observed, sensitivity weakening)
        - high: 0.7 ≤ S_index < 0.9 (models largely indistinguishable)
        - very_high: S_index ≥ 0.9 (no reliable signal for comparison)
    """
    if not 0 <= s_index <= 1:
        raise ValueError(f"S_index must be in [0, 1], got {s_index}")
    
    if s_index < 0.01:
        return "very_low"
    elif s_index < 0.3:
        return "low"
    elif s_index < 0.7:
        return "moderate"
    elif s_index < 0.9:
        return "high"
    else:
        return "very_high"


def compute_saturation_metrics(
    scores: List[float],
    test_set_size: int,
    alpha: float = 0.5,
    z: float = 1.96
) -> dict:
    """
    Compute comprehensive saturation metrics for a group of models.
    
    Args:
        scores: List of model scores (should be at least 5 scores)
        test_set_size: Size of the test set
        alpha: Exponent for effective sample size (default 0.5)
        z: Standard normal quantile for confidence (default 1.96 for 95%)
    
    Returns:
        Dictionary containing:
            - s1, s5: Top and 5th model scores
            - score_range: s1 - s5
            - mean_score: Average of all scores
            - n_eff: Effective sample size
            - se_delta: Standard error of difference
            - r_norm: Normalized score range
            - s_index: Saturation index
            - category: Saturation category
            - is_statistically_similar: Whether Δ ≤ z * SE_Δ
    """
    if len(scores) < 5:
        raise ValueError(f"Need at least 5 scores, got {len(scores)}")
    
    # Sort scores in descending order to get top 5
    sorted_scores = sorted(scores, reverse=True)
    s1 = sorted_scores[0]
    s5 = sorted_scores[4]
    
    # Compute metrics
    n_eff = compute_n_eff(test_set_size, alpha)
    se_delta = compute_se_delta(s1, s5, n_eff)
    r_norm = compute_normalized_range(s1, s5, se_delta)
    s_index = compute_saturation_index(r_norm)
    category = categorize_saturation(s_index)
    
    # Check statistical similarity
    delta = s1 - s5
    is_statistically_similar = delta <= z * se_delta
    
    return {
        "s1": s1,
        "s5": s5,
        "score_range": delta,
        "mean_score": sum(scores) / len(scores),
        "n_eff": n_eff,
        "se_delta": se_delta,
        "r_norm": r_norm,
        "s_index": s_index,
        "category": category,
        "is_statistically_similar": is_statistically_similar,
    }
