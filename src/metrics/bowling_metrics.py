"""
Bowling Feature Engineering and Metric Calculations for T20 Cricket
"""
import numpy as np
import pandas as pd
from src.config import BENCHMARKS

def compute_bowling_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes situational and modern T20 bowling metrics.
    """
    df = df.copy()
    bw_bench = BENCHMARKS["bowling"]

    # 1. True Economy Rate (Difference from benchmark: negative is better, so invert)
    df['true_economy_rate'] = (bw_bench['avg_economy'] - df['bowling_econ']).round(2)

    # 2. Phase-Wise Suppression Indices
    # In death overs, keeping economy under 9.5 is gold
    df['death_control_index'] = (bw_bench['death_econ'] - df['death_econ']).round(2)
    df['middle_squeeze_index'] = (bw_bench['middle_econ'] - df['mid_econ']).round(2)
    df['pp_threat_index'] = (bw_bench['pp_econ'] - df['pp_econ']).round(2)

    # 3. Dot Ball Frequency & Boundary Suppression Score
    # Dot balls build pressure; low boundary conceded prevents big overs
    df['pressure_building_score'] = (
        (df['dot_pct_bowl'] / 50.0).clip(0, 1.2) * 50 +
        ((20.0 - df['boundary_conceded_pct']) / 10.0).clip(0, 1.2) * 50
    ).round(2)

    # 4. Wicket-Taking Efficiency (Strike Rate & Average)
    df['balls_per_wicket'] = df['bowling_sr'].replace(0, 99.0)

    # 5. Bowling Impact Rating (0 to 100 scale)
    # Weights: Econ Suppression (30%), Death/Clutch Economy (25%), Dot % (20%), Wicket Strike Rate (25%)
    econ_factor = ((10.0 - df['bowling_econ']) / 4.0).clip(0, 1.2) * 30
    death_factor = ((11.0 - df['death_econ']) / 4.0).clip(0, 1.2) * 25
    dot_factor = (df['dot_pct_bowl'] / 55.0).clip(0, 1.2) * 20
    wicket_factor = ((25.0 - df['balls_per_wicket']) / 12.0).clip(0, 1.2) * 25

    df['bowling_impact_score'] = (
        econ_factor + death_factor + dot_factor + wicket_factor
    ).round(2)

    # If player hasn't bowled or fewer than 5 overs, zero out
    df.loc[df['overs'] < 5.0, 'bowling_impact_score'] = 0.0

    return df
