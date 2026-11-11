"""
Machine Learning Component: Competition & Phase Context Normalization
Adjusts batting and bowling values relative to expected baselines across IPL (T20) vs T20I environments.
"""
import numpy as np
import pandas as pd

def compute_context_baselines(df_annotated: pd.DataFrame, df_matches: pd.DataFrame, df_comp: pd.DataFrame) -> pd.DataFrame:
    """
    Merges competition format (T20 vs T20I) and calculates expected runs per ball
    conditioned on (match_format, innings_phase, is_high_pressure).
    """
    df = df_annotated.copy()

    # Map match_id -> match_format (T20 vs T20I) & comp_name
    m_comp = df_matches[['match_id', 'comp_id']].merge(
        df_comp[['comp_id', 'match_format', 'comp_name', 'season']], on='comp_id', how='left'
    )
    df = df.merge(m_comp, on='match_id', how='left')

    # Define Match Phase: Powerplay (1-6), Middle (7-15), Death (16-20)
    df['phase'] = np.select(
        [df['overid'] <= 6, df['overid'] <= 15, df['overid'] >= 16],
        ['Powerplay', 'Middle', 'Death'],
        default='Middle'
    )

    # Calculate expected runs per ball and wicket rate by (match_format, phase)
    # Using legal deliveries for clean run rate baseline
    legal = df[df['is_legal'] == True]
    par_table = legal.groupby(['match_format', 'phase']).agg(
        par_runs_per_ball=('runs', 'mean'),
        par_bowler_runs_per_ball=('bowler_runs', 'mean') if 'bowler_runs' in legal.columns else ('delivery_runs', 'mean'),
        par_wicket_rate=('is_wicket', 'mean')
    ).reset_index()

    df = df.merge(par_table, on=['match_format', 'phase'], how='left')

    # Runs Above Expected (RAE) for batters
    df['bat_rae'] = df['runs'] - df['par_runs_per_ball']

    # Runs Saved Above Expected (RSAE) for bowlers (positive = conceded fewer than par)
    if 'bowler_runs' in df.columns:
        df['bowl_rsae'] = df['par_bowler_runs_per_ball'] - df['bowler_runs']
    else:
        df['bowl_rsae'] = df['par_runs_per_ball'] - df['delivery_runs']

    return df
