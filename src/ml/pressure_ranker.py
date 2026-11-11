"""
Machine Learning Component 3 (Upgraded): Context-Normalized Clutch & Empirical Bayes Ranker
Fixes the Phase-Mismatch Trap (comparing Death vs Powerplay) and applies Empirical Bayes Shrinkage
across all rate stats (Scoring Rate, Economy, Wicket Hazard, and Clutch Delta).
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
from src.ml.context_normalizer import compute_context_baselines
from src.ml.bayesian_shrinkage import empirical_bayes_shrinkage

def run_context_normalized_ml_ranking():
    data_dir = os.path.join(REPO_ROOT, "data/raw/extracted/SupeRR Selector Season 2 - Problem Statement - Data Pack/SupeRR Selector Season 2 - Data Pack")
    
    print("[*] Loading datasets...")
    df_bbb = pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"))
    df_matches = pd.read_csv(os.path.join(data_dir, "matches.csv"))
    df_comp = pd.read_csv(os.path.join(data_dir, "competitions.csv"))

    # 1. Train Win Probability Model & Compute ML Leverage Index
    wp_engine = WinProbabilityModel()
    df_features = wp_engine.prepare_features(df_bbb, df_matches)
    wp_engine.fit(df_features)
    df_annotated = wp_engine.compute_leverage_index(df_features)

    # Calculate bowler runs cleanly before context baselines
    et = df_annotated['extras_type'].values
    ex2 = df_annotated['extras_2_runs'].fillna(0).values
    is_w = (et == 'wide')
    is_nb = (et == 'Overstep')
    b_extras = np.zeros(len(df_annotated))
    b_extras[is_w] = 1 + ex2[is_w]
    b_extras[is_nb] = 1 + ex2[is_nb]
    df_annotated['bowler_runs'] = df_annotated['runs'] + b_extras

    # 2. Apply Context Normalization (T20 vs T20I and Powerplay vs Middle vs Death)
    print("[*] Applying Context Normalization across (Format x Phase)...")
    df_ctx = compute_context_baselines(df_annotated, df_matches, df_comp)

    is_hp = df_ctx['is_high_pressure']

    # =========================================================================
    # 3. BATTER EVALUATION (Runs Above Expected + Bayesian Shrinkage)
    # =========================================================================
    print("[*] Evaluating Batters with Bayesian Shrinkage & Context Adjustment...")
    bat_hp = df_ctx[is_hp].groupby('striker_name').agg(
        hp_runs=('runs', 'sum'),
        hp_balls=('runs', 'count'),
        hp_rae=('bat_rae', 'sum'),
        hp_fours=('is_four', 'sum'),
        hp_sixes=('is_six', 'sum'),
        hp_dots=('runs', lambda x: (x == 0).sum()),
        hp_wickets=('is_wicket', 'sum')
    )

    bat_base = df_ctx[~is_hp].groupby('striker_name').agg(
        base_runs=('runs', 'sum'),
        base_balls=('runs', 'count'),
        base_rae=('bat_rae', 'sum'),
        base_wickets=('is_wicket', 'sum')
    )

    bat = bat_hp.join(bat_base, how='inner')

    # Context-Adjusted Runs Above Expected per 100 balls (Normalized SR Differential vs Par)
    bat['hp_rae_per_100'] = (bat['hp_rae'] / bat['hp_balls'] * 100).round(2)
    bat['base_rae_per_100'] = (bat['base_rae'] / bat['base_balls'] * 100).round(2)
    
    # Raw Strike Rates for readability
    bat['raw_hp_sr'] = (bat['hp_runs'] / bat['hp_balls'] * 100).round(2)
    bat['raw_base_sr'] = (bat['base_runs'] / bat['base_balls'] * 100).round(2)
    
    # Context-Adjusted Clutch Delta: How much MORE above par do they score under pressure vs normal?
    bat['raw_clutch_delta'] = (bat['hp_rae_per_100'] - bat['base_rae_per_100']).round(2)
    bat['hp_boundary_pct'] = (((bat['hp_fours'] * 4) + (bat['hp_sixes'] * 6)) / bat['hp_runs'].replace(0, np.nan) * 100).fillna(0).round(2)
    bat['hp_survival_rate'] = (1.0 - (bat['hp_wickets'] / bat['hp_balls'])).round(4)

    # Empirical Bayes Shrinkage (prior weight = 80 balls for robust stability)
    bat['bayes_hp_rae'] = empirical_bayes_shrinkage(bat['hp_rae_per_100'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_clutch_delta'] = empirical_bayes_shrinkage(bat['raw_clutch_delta'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_hp_sr'] = empirical_bayes_shrinkage(bat['raw_hp_sr'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_survival'] = empirical_bayes_shrinkage(bat['hp_survival_rate'] * 100, bat['hp_balls'], prior_weight=80.0)

    # Batting Clutch Rating (0 - 100 scale):
    # 45% Context-Adjusted Runs Above Expected (bayes_hp_rae)
    # 25% Relative Clutch Elevation (bayes_clutch_delta)
    # 15% Boundary Execution under pressure
    # 15% Wicket Preservation under pressure (survival rate)
    rae_norm = ((bat['bayes_hp_rae'] + 10.0) / 55.0).clip(0, 1.2) * 45
    delta_norm = ((bat['bayes_clutch_delta'] + 15.0) / 45.0).clip(0, 1.2) * 25
    bnd_norm = (bat['hp_boundary_pct'] / 70.0).clip(0, 1.1) * 15
    surv_norm = ((bat['bayes_survival'] - 90.0) / 8.0).clip(0, 1.2) * 15

    bat['batting_clutch_score'] = (rae_norm + delta_norm + bnd_norm + surv_norm).round(2)

    # Minimum 150 balls under high pressure to qualify
    top_batters = bat[bat['hp_balls'] >= 150].sort_values(by='batting_clutch_score', ascending=False).reset_index()
    top_batters['rank'] = top_batters.index + 1

    # =========================================================================
    # 4. BOWLER EVALUATION (Runs Saved Above Phase Par + Bayesian Shrinkage)
    # =========================================================================
    print("[*] Evaluating Bowlers with Phase-Normalized Runs Saved & Bayesian Shrinkage...")
    bowl_hp = df_ctx[is_hp].groupby('bowler_name').agg(
        hp_runs=('bowler_runs', 'sum'),
        hp_balls=('is_legal', 'sum'),
        hp_rsae=('bowl_rsae', 'sum'),
        hp_wickets=('is_wicket', 'sum'),
        hp_dots=('bowler_runs', lambda x: (x == 0).sum())
    )

    bowl_base = df_ctx[~is_hp].groupby('bowler_name').agg(
        base_runs=('bowler_runs', 'sum'),
        base_balls=('is_legal', 'sum'),
        base_rsae=('bowl_rsae', 'sum'),
        base_wickets=('is_wicket', 'sum')
    )

    bowl = bowl_hp.join(bowl_base, how='inner')
    bowl['hp_overs'] = (bowl['hp_balls'] / 6.0).round(1)
    
    # Runs Saved Above Expected per Over (Context-Normalized Economy Advantage!)
    bowl['hp_rsae_per_over'] = (bowl['hp_rsae'] / (bowl['hp_balls'] / 6.0)).round(2)
    bowl['base_rsae_per_over'] = (bowl['base_rsae'] / (bowl['base_balls'] / 6.0)).round(2)

    # Raw economy for readability
    bowl['raw_hp_econ'] = (bowl['hp_runs'] / (bowl['hp_balls'] / 6.0)).round(2)
    bowl['raw_base_econ'] = (bowl['base_runs'] / (bowl['base_balls'] / 6.0)).round(2)

    # Context-Adjusted Clutch Delta: Do they save MORE runs relative to phase par under pressure?
    bowl['raw_clutch_delta'] = (bowl['hp_rsae_per_over'] - bowl['base_rsae_per_over']).round(2)
    
    # Wicket Rate per 100 balls (More mathematically stable for shrinkage than balls/wicket!)
    bowl['hp_wkt_per_100'] = (bowl['hp_wickets'] / bowl['hp_balls'] * 100).round(2)
    bowl['hp_dot_pct'] = (bowl['hp_dots'] / bowl['hp_balls'] * 100).round(2)

    # Empirical Bayes Shrinkage across ALL key rate metrics (prior weight = 25 overs = 150 balls)
    bowl['bayes_hp_rsae'] = empirical_bayes_shrinkage(bowl['hp_rsae_per_over'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_clutch_delta'] = empirical_bayes_shrinkage(bowl['raw_clutch_delta'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_wkt_rate'] = empirical_bayes_shrinkage(bowl['hp_wkt_per_100'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_dot_pct'] = empirical_bayes_shrinkage(bowl['hp_dot_pct'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_hp_sr'] = (100.0 / bowl['bayes_wkt_rate']).round(2)

    # Bowling Clutch Rating (0 - 100 scale):
    # 40% Phase-Normalized Runs Saved Above Expected (bayes_hp_rsae)
    # 30% Bayesian Wicket-Taking Rate (bayes_wkt_rate)
    # 15% Context-Normalized Clutch Delta (bayes_clutch_delta)
    # 15% Bayesian Dot Ball % under pressure
    rsae_norm = ((bowl['bayes_hp_rsae'] + 1.0) / 3.5).clip(0, 1.2) * 40
    wkt_norm = (bowl['bayes_wkt_rate'] / 9.5).clip(0, 1.2) * 30
    delta_norm = ((bowl['bayes_clutch_delta'] + 1.0) / 2.5).clip(0, 1.2) * 15
    dot_norm = (bowl['bayes_dot_pct'] / 45.0).clip(0, 1.1) * 15

    bowl['bowling_clutch_score'] = (rsae_norm + wkt_norm + delta_norm + dot_norm).round(2)

    # Minimum 30 overs (180 balls) bowled under high pressure to qualify
    top_bowlers = bowl[bowl['hp_overs'] >= 30.0].sort_values(by='bowling_clutch_score', ascending=False).reset_index()
    top_bowlers['rank'] = top_bowlers.index + 1

    # Export updated files
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    os.makedirs(proc_dir, exist_ok=True)
    top_batters.head(10).to_csv(os.path.join(proc_dir, "ml_top10_batters_under_pressure.csv"), index=False)
    top_bowlers.head(10).to_csv(os.path.join(proc_dir, "ml_top10_bowlers_under_pressure.csv"), index=False)
    top_batters.to_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"), index=False)
    top_bowlers.to_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"), index=False)

    print("\n" + "=" * 95)
    print("  🏆 TOP 10 BATTERS UNDER PRESSURE (CONTEXT-NORMALIZED + EMPIRICAL BAYES)")
    print("=" * 95)
    bat_cols = ['rank', 'striker_name', 'hp_balls', 'raw_hp_sr', 'bayes_hp_rae', 'bayes_clutch_delta', 'batting_clutch_score']
    print(top_batters.head(10)[bat_cols].to_string(index=False))

    print("\n" + "=" * 95)
    print("  🎯 TOP 10 BOWLERS UNDER PRESSURE (PHASE-NORMALIZED RUNS SAVED + EMPIRICAL BAYES)")
    print("=" * 95)
    bowl_cols = ['rank', 'bowler_name', 'hp_overs', 'hp_wickets', 'raw_hp_econ', 'bayes_hp_rsae', 'bayes_hp_sr', 'bowling_clutch_score']
    print(top_bowlers.head(10)[bowl_cols].to_string(index=False))
    print("=" * 95)

    return top_batters, top_bowlers

if __name__ == "__main__":
    run_context_normalized_ml_ranking()
