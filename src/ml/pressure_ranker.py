"""
Machine Learning Component 3: End-to-End Pressure & Clutch Ranker
Integrates Win Probability Leverage ML + Empirical Bayes Shrinkage to rank Top 10 Batters & Bowlers.
"""
import os
import sys
import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.ml.win_probability_model import WinProbabilityModel
from src.ml.bayesian_shrinkage import empirical_bayes_shrinkage

def run_ml_pressure_ranking():
    data_dir = os.path.join(REPO_ROOT, "data/raw/extracted/SupeRR Selector Season 2 - Problem Statement - Data Pack/SupeRR Selector Season 2 - Data Pack")
    
    print("[*] Loading datasets for ML training...")
    df_bbb = pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"))
    df_matches = pd.read_csv(os.path.join(data_dir, "matches.csv"))

    # 1. Train Win Probability Model & Compute ML Leverage Index
    print("[*] Training Supervised ML Win Probability Model (HistGradientBoosting)...")
    wp_engine = WinProbabilityModel()
    df_features = wp_engine.prepare_features(df_bbb, df_matches)
    wp_engine.fit(df_features)

    print("[*] Generating ML Delivery-Level Leverage Index & Pressure States...")
    df_annotated = wp_engine.compute_leverage_index(df_features)

    is_hp = df_annotated['is_high_pressure']

    # 2. BATTER EVALUATION
    print("[*] Computing Batting Clutch & Bayesian Shrinkage Metrics...")
    bat_hp = df_annotated[is_hp].groupby('striker_name').agg(
        hp_runs=('runs', 'sum'),
        hp_balls=('runs', 'count'),
        hp_fours=('is_four', 'sum'),
        hp_sixes=('is_six', 'sum'),
        hp_dots=('runs', lambda x: (x == 0).sum()),
        hp_wickets=('is_wicket', 'sum')
    )

    bat_base = df_annotated[~is_hp].groupby('striker_name').agg(
        base_runs=('runs', 'sum'),
        base_balls=('runs', 'count'),
        base_wickets=('is_wicket', 'sum')
    )

    bat = bat_hp.join(bat_base, how='inner')
    
    # Raw metrics
    bat['raw_hp_sr'] = (bat['hp_runs'] / bat['hp_balls'] * 100).round(2)
    bat['raw_base_sr'] = (bat['base_runs'] / bat['base_balls'] * 100).round(2)
    bat['raw_sr_delta'] = (bat['raw_hp_sr'] - bat['raw_base_sr']).round(2)
    bat['hp_boundary_pct'] = (((bat['hp_fours'] * 4) + (bat['hp_sixes'] * 6)) / bat['hp_runs'].replace(0, np.nan) * 100).fillna(0).round(2)
    bat['hp_dot_pct'] = (bat['hp_dots'] / bat['hp_balls'] * 100).round(2)

    # ML Shrinkage: Empirical Bayes on Pressure Strike Rate (prior weight = 50 balls)
    bat['bayes_hp_sr'] = empirical_bayes_shrinkage(bat['raw_hp_sr'], bat['hp_balls'], prior_weight=50.0)
    bat['bayes_sr_delta'] = empirical_bayes_shrinkage(bat['raw_sr_delta'], bat['hp_balls'], prior_weight=50.0)

    # Batting Clutch Score (0 - 100):
    # 45% Bayes Pressure SR + 25% Bayes Clutch Delta + 20% Boundary Execution + 10% Low Dot%
    sr_norm = (bat['bayes_hp_sr'] / 185.0).clip(0, 1.2) * 45
    delta_norm = ((bat['bayes_sr_delta'] + 30.0) / 60.0).clip(0, 1.2) * 25
    bnd_norm = (bat['hp_boundary_pct'] / 70.0).clip(0, 1.2) * 20
    dot_norm = ((50.0 - bat['hp_dot_pct']) / 30.0).clip(0, 1.2) * 10

    bat['batting_clutch_score'] = (sr_norm + delta_norm + bnd_norm + dot_norm).round(2)

    # Qualification filter: Minimum 120 balls faced under high pressure for statistical credibility
    top_batters = bat[bat['hp_balls'] >= 120].sort_values(by='batting_clutch_score', ascending=False).reset_index()
    top_batters['rank'] = top_batters.index + 1

    # 3. BOWLER EVALUATION
    print("[*] Computing Bowling Clutch & Bayesian Shrinkage Metrics...")
    # Calculate bowler runs (batter runs + wide + noball)
    et = df_annotated['extras_type'].values
    ex2 = df_annotated['extras_2_runs'].fillna(0).values
    is_w = (et == 'wide')
    is_nb = (et == 'Overstep')
    b_extras = np.zeros(len(df_annotated))
    b_extras[is_w] = 1 + ex2[is_w]
    b_extras[is_nb] = 1 + ex2[is_nb]
    df_annotated['bowler_runs'] = df_annotated['runs'] + b_extras

    bowl_hp = df_annotated[is_hp].groupby('bowler_name').agg(
        hp_runs=('bowler_runs', 'sum'),
        hp_balls=('is_legal', 'sum'),
        hp_wickets=('is_wicket', 'sum'),
        hp_dots=('bowler_runs', lambda x: (x == 0).sum())
    )

    bowl_base = df_annotated[~is_hp].groupby('bowler_name').agg(
        base_runs=('bowler_runs', 'sum'),
        base_balls=('is_legal', 'sum')
    )

    bowl = bowl_hp.join(bowl_base, how='inner')
    bowl['hp_overs'] = (bowl['hp_balls'] / 6.0).round(1)
    bowl['raw_hp_econ'] = (bowl['hp_runs'] / (bowl['hp_balls'] / 6.0)).round(2)
    bowl['raw_base_econ'] = (bowl['base_runs'] / (bowl['base_balls'] / 6.0)).round(2)
    bowl['raw_econ_delta'] = (bowl['raw_base_econ'] - bowl['raw_hp_econ']).round(2) # Positive means conceded fewer under pressure
    bowl['hp_sr'] = (bowl['hp_balls'] / bowl['hp_wickets'].replace(0, np.nan)).round(2)
    bowl['hp_dot_pct'] = (bowl['hp_dots'] / bowl['hp_balls'] * 100).round(2)

    # ML Shrinkage: Empirical Bayes on Pressure Economy (prior weight = 15 overs = 90 balls)
    bowl['bayes_hp_econ'] = empirical_bayes_shrinkage(bowl['raw_hp_econ'], bowl['hp_balls'], prior_weight=90.0)
    bowl['bayes_econ_delta'] = empirical_bayes_shrinkage(bowl['raw_econ_delta'], bowl['hp_balls'], prior_weight=90.0)

    # Bowling Clutch Score (0 - 100):
    # 40% Economy Suppression under pressure + 30% Wicket-taking frequency + 15% Economy Delta + 15% Dot Ball %
    econ_norm = ((10.0 - bowl['bayes_hp_econ']) / 4.0).clip(0, 1.2) * 40
    wkt_norm = ((25.0 - bowl['hp_sr'].fillna(35.0)) / 15.0).clip(0, 1.2) * 30
    edelta_norm = ((bowl['bayes_econ_delta'] + 1.0) / 2.0).clip(0, 1.2) * 15
    bdot_norm = (bowl['hp_dot_pct'] / 50.0).clip(0, 1.2) * 15

    bowl['bowling_clutch_score'] = (econ_norm + wkt_norm + edelta_norm + bdot_norm).round(2)

    # Qualification filter: Minimum 20 overs (120 balls) bowled under high pressure
    top_bowlers = bowl[bowl['hp_overs'] >= 20.0].sort_values(by='bowling_clutch_score', ascending=False).reset_index()
    top_bowlers['rank'] = top_bowlers.index + 1

    # 4. EXPORT RANKINGS
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    os.makedirs(proc_dir, exist_ok=True)

    top_batters.head(10).to_csv(os.path.join(proc_dir, "ml_top10_batters_under_pressure.csv"), index=False)
    top_bowlers.head(10).to_csv(os.path.join(proc_dir, "ml_top10_bowlers_under_pressure.csv"), index=False)
    top_batters.to_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"), index=False)
    top_bowlers.to_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"), index=False)

    print("\n" + "=" * 80)
    print("  🏆 TOP 10 BATTERS UNDER PRESSURE (ML WIN PROBABILITY + BAYESIAN SHRINKAGE)")
    print("=" * 80)
    bat_cols = ['rank', 'striker_name', 'hp_balls', 'raw_hp_sr', 'bayes_hp_sr', 'raw_sr_delta', 'batting_clutch_score']
    print(top_batters.head(10)[bat_cols].to_string(index=False))

    print("\n" + "=" * 80)
    print("  🎯 TOP 10 BOWLERS UNDER PRESSURE (ML WIN PROBABILITY + BAYESIAN SHRINKAGE)")
    print("=" * 80)
    bowl_cols = ['rank', 'bowler_name', 'hp_overs', 'hp_wickets', 'raw_hp_econ', 'bayes_hp_econ', 'hp_sr', 'bowling_clutch_score']
    print(top_bowlers.head(10)[bowl_cols].to_string(index=False))
    print("=" * 80)

    return top_batters, top_bowlers

if __name__ == "__main__":
    run_ml_pressure_ranking()
