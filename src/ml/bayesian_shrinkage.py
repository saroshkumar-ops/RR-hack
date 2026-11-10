"""
Machine Learning Component 2: Empirical Bayes Shrinkage
Stabilizes player performance estimates under pressure against small-sample noise.
"""
import numpy as np
import pandas as pd

def empirical_bayes_shrinkage(
    observed_values: pd.Series,
    sample_sizes: pd.Series,
    prior_weight: float = 60.0
) -> pd.Series:
    """
    Computes Empirical Bayes posterior mean estimates:
    theta_i = (n_i / (n_i + prior_weight)) * x_i + (prior_weight / (n_i + prior_weight)) * mu_0

    Parameters:
    - observed_values: The raw observed metric (e.g. Strike Rate or Economy)
    - sample_sizes: The number of deliveries / trials (e.g. pressure balls faced or overs bowled)
    - prior_weight: The pseudo-observation weight of the population prior (v_0)
    """
    # Population prior mean (weighted by sample size to avoid skewed unweighted averages)
    valid_mask = (sample_sizes > 0) & observed_values.notna()
    if valid_mask.sum() == 0:
        return observed_values

    mu_0 = np.average(observed_values[valid_mask], weights=sample_sizes[valid_mask])

    # Shrinkage factor (1 - B_i)
    weight_on_data = sample_sizes / (sample_sizes + prior_weight)
    shrunk_values = (weight_on_data * observed_values) + ((1.0 - weight_on_data) * mu_0)
    return shrunk_values.round(2)
