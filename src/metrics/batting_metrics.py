"""
Batting Feature Engineering and Metric Calculations for T20 Cricket
"""
import numpy as np
import pandas as pd
from src.config import BENCHMARKS

def compute_batting_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes situational and modern T20 batting metrics.
    """
    df = df.copy()
    b_bench = BENCHMARKS["batting"]

    # 1. Boundary Runs Percentage
    total_runs = df['runs'].replace(0, np.nan)
    boundary_runs = (df['fours'] * 4) + (df['sixes'] * 6)
    df['boundary_runs_pct'] = (boundary_runs / total_runs * 100).fillna(0).round(2)

    # 2. Balls Per Boundary
    boundaries_count = (df['fours'] + df['sixes']).replace(0, np.nan)
    df['balls_per_boundary'] = (df['balls'] / boundaries_count).fillna(99.0).round(2)

    # 3. True Strike Rate (TSR Index relative to baseline 138.0)
    df['true_strike_rate'] = (df['strike_rate'] - b_bench['avg_strike_rate']).round(2)

    # 4. Phase-Specific Strike Rate Indices
    df['death_over_acceleration'] = (df['death_sr'] - b_bench['death_sr']).round(2)
    df['powerplay_intent_index'] = (df['pp_sr'] - b_bench['pp_sr']).round(2)

    # 5. Non-Boundary Strike Rate (Ability to rotate strike & punish dots)
    non_boundary_runs = (df['runs'] - boundary_runs).clip(lower=0)
    non_boundary_balls = (df['balls'] - (df['fours'] + df['sixes'])).replace(0, np.nan)
    df['non_boundary_sr'] = (non_boundary_runs / non_boundary_balls * 100).fillna(0).round(2)

    # 6. Pace vs Spin Versatility Differential
    df['pace_spin_diff'] = (df['sr_vs_pace'] - df['sr_vs_spin']).round(2)
    # Balanced scorer is someone who can hit both pace and spin
    df['adaptability_score'] = (
        (df['sr_vs_pace'].clip(upper=200) + df['sr_vs_spin'].clip(upper=200)) / 2.0
    ).round(2)

    # 7. Batting Impact Rating (0 to 100 scale)
    # Weights: SR (35%), Death SR / Finisher power (25%), Boundary % (20%), Avg (10%), Low dot % (10%)
    sr_factor = (df['strike_rate'] / 180.0).clip(0, 1.2) * 35
    death_factor = (df['death_sr'] / 220.0).clip(0, 1.2) * 25
    boundary_factor = (df['boundary_runs_pct'] / 75.0).clip(0, 1.1) * 20
    avg_factor = (df['batting_avg'] / 45.0).clip(0, 1.1) * 10
    dot_penalty = ((50.0 - df['dot_pct_bat']) / 30.0).clip(0, 1.1) * 10

    df['batting_impact_score'] = (
        sr_factor + death_factor + boundary_factor + avg_factor + dot_penalty
    ).round(2)

    # If player hasn't batted or has fewer than 20 balls, zero out score
    df.loc[df['balls'] < 20, 'batting_impact_score'] = 0.0

    return df
