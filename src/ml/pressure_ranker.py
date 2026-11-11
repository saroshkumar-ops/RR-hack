"""
Machine Learning Component 3 (Final Production Engine):
Context-Normalized Clutch, Empirical Bayes Shrinkage, Match Consistency, & Unsupervised Clustering
Ranks the Top 10 Batters and Top 10 Bowlers under pressure for SupeRR Selector Season 2.
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
from src.ml.archetype_clusterer import cluster_batter_archetypes, cluster_bowler_archetypes

def run_full_ml_pipeline():
    data_dir = os.path.join(REPO_ROOT, "data/raw/extracted/SupeRR Selector Season 2 - Problem Statement - Data Pack/SupeRR Selector Season 2 - Data Pack")
    
    print("[*] Loading raw delivery and match tables...")
    df_bbb = pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"))
    df_matches = pd.read_csv(os.path.join(data_dir, "matches.csv"))
    df_comp = pd.read_csv(os.path.join(data_dir, "competitions.csv"))

    # 1. Train Win Probability Model & Compute ML Leverage Index
    wp_engine = WinProbabilityModel()
    df_features = wp_engine.prepare_features(df_bbb, df_matches)
    wp_engine.fit(df_features)
    df_annotated = wp_engine.compute_leverage_index(df_features)

    # Calculate bowler runs cleanly
    et = df_annotated['extras_type'].values
    ex2 = df_annotated['extras_2_runs'].fillna(0).values
    is_w = (et == 'wide')
    is_nb = (et == 'Overstep')
    b_extras = np.zeros(len(df_annotated))
    b_extras[is_w] = 1 + ex2[is_w]
    b_extras[is_nb] = 1 + ex2[is_nb]
    df_annotated['bowler_runs'] = df_annotated['runs'] + b_extras

    # 2. Apply Context Normalization (Format x Phase)
    print("[*] Applying Context Normalization across (Format x Phase)...")
    df_ctx = compute_context_baselines(df_annotated, df_matches, df_comp)
    is_hp = df_ctx['is_high_pressure']

    # =========================================================================
    # 3. BATTER EVALUATION + MATCH CONSISTENCY + K-MEANS CLUSTERING
    # =========================================================================
    print("[*] Computing Batting Clutch Metrics, Match Consistency & Clustering...")
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

    # Match-by-match consistency in high-pressure situations (min 5 HP balls in a match)
    bat_m = df_ctx[is_hp].groupby(['striker_name', 'match_id']).agg(
        m_balls=('runs', 'count'),
        m_rae=('bat_rae', 'sum')
    ).reset_index()
    bat_cons = bat_m[bat_m['m_balls'] >= 5].groupby('striker_name').agg(
        hp_matches=('match_id', 'nunique'),
        pos_matches=('m_rae', lambda x: (x > 0).sum()),
        rae_std=('m_rae', 'std')
    )
    bat_cons['raw_consistency_pct'] = (bat_cons['pos_matches'] / bat_cons['hp_matches'] * 100).round(2)

    bat = bat_hp.join(bat_base, how='inner').join(bat_cons, how='left')
    bat['hp_matches'] = bat['hp_matches'].fillna(0).astype(int)
    bat['raw_consistency_pct'] = bat['raw_consistency_pct'].fillna(50.0)
    bat['rae_std'] = bat['rae_std'].fillna(10.0).round(2)

    # Context-Adjusted Performance
    bat['hp_rae_per_100'] = (bat['hp_rae'] / bat['hp_balls'] * 100).round(2)
    bat['base_rae_per_100'] = (bat['base_rae'] / bat['base_balls'] * 100).round(2)
    bat['raw_hp_sr'] = (bat['hp_runs'] / bat['hp_balls'] * 100).round(2)
    bat['raw_base_sr'] = (bat['base_runs'] / bat['base_balls'] * 100).round(2)
    bat['raw_clutch_delta'] = (bat['hp_rae_per_100'] - bat['base_rae_per_100']).round(2)
    bat['hp_boundary_pct'] = (((bat['hp_fours'] * 4) + (bat['hp_sixes'] * 6)) / bat['hp_runs'].replace(0, np.nan) * 100).fillna(0).round(2)
    bat['hp_survival_rate'] = (1.0 - (bat['hp_wickets'] / bat['hp_balls'])).round(4)

    # Empirical Bayes Shrinkage
    bat['bayes_hp_rae'] = empirical_bayes_shrinkage(bat['hp_rae_per_100'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_clutch_delta'] = empirical_bayes_shrinkage(bat['raw_clutch_delta'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_hp_sr'] = empirical_bayes_shrinkage(bat['raw_hp_sr'], bat['hp_balls'], prior_weight=80.0)
    bat['bayes_survival'] = empirical_bayes_shrinkage(bat['hp_survival_rate'] * 100, bat['hp_balls'], prior_weight=80.0)
    bat['bayes_consistency_pct'] = empirical_bayes_shrinkage(bat['raw_consistency_pct'], bat['hp_matches'], prior_weight=10.0)

    # Uncertainty / Confidence Standard Error
    bat['uncertainty_se'] = (bat['rae_std'] / np.sqrt(np.maximum(bat['hp_matches'], 1))).round(2)

    # Composite Batting Clutch & Reliability Score (0 - 100):
    # 40% Context-Adjusted Pressure Value (bayes_hp_rae)
    # 25% Relative Clutch Elevation vs. Baseline (bayes_clutch_delta)
    # 20% Match-to-Match Consistency (bayes_consistency_pct)
    # 15% Boundary Execution + Wicket Preservation
    rae_norm = ((bat['bayes_hp_rae'] + 10.0) / 55.0).clip(0, 1.2) * 40
    delta_norm = ((bat['bayes_clutch_delta'] + 15.0) / 45.0).clip(0, 1.2) * 25
    cons_norm = (bat['bayes_consistency_pct'] / 80.0).clip(0, 1.15) * 20
    exec_norm = ((bat['hp_boundary_pct'] / 70.0).clip(0, 1.1) * 7.5) + (((bat['bayes_survival'] - 90.0) / 8.0).clip(0, 1.1) * 7.5)

    bat['batting_clutch_score'] = (rae_norm + delta_norm + cons_norm + exec_norm).round(2)

    # Filter qualified batters (>= 150 HP balls and >= 10 HP matches)
    qual_bat = bat[(bat['hp_balls'] >= 150) & (bat['hp_matches'] >= 10)].copy()
    qual_bat = cluster_batter_archetypes(qual_bat)
    top_batters = qual_bat.sort_values(by='batting_clutch_score', ascending=False).reset_index()
    top_batters['rank'] = top_batters.index + 1

    # =========================================================================
    # 4. BOWLER EVALUATION + MATCH CONSISTENCY + K-MEANS CLUSTERING
    # =========================================================================
    print("[*] Computing Bowling Clutch Metrics, Match Consistency & Clustering...")
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

    # Match-by-match consistency in high-pressure situations (min 4 HP balls in a match)
    bowl_m = df_ctx[is_hp].groupby(['bowler_name', 'match_id']).agg(
        m_balls=('is_legal', 'sum'),
        m_rsae=('bowl_rsae', 'sum'),
        m_wkts=('is_wicket', 'sum')
    ).reset_index()
    bowl_m_qual = bowl_m[bowl_m['m_balls'] >= 4].copy()
    bowl_m_qual['is_pos'] = (bowl_m_qual['m_rsae'] > 0) | (bowl_m_qual['m_wkts'] >= 1)

    bowl_cons = bowl_m_qual.groupby('bowler_name').agg(
        hp_matches=('match_id', 'nunique'),
        pos_matches=('is_pos', 'sum'),
        rsae_std=('m_rsae', 'std')
    )
    bowl_cons['raw_consistency_pct'] = (bowl_cons['pos_matches'] / bowl_cons['hp_matches'] * 100).round(2)

    bowl = bowl_hp.join(bowl_base, how='inner').join(bowl_cons, how='left')
    bowl['hp_matches'] = bowl['hp_matches'].fillna(0).astype(int)
    bowl['raw_consistency_pct'] = bowl['raw_consistency_pct'].fillna(50.0)
    bowl['rsae_std'] = bowl['rsae_std'].fillna(6.0).round(2)

    bowl['hp_overs'] = (bowl['hp_balls'] / 6.0).round(1)
    bowl['hp_rsae_per_over'] = (bowl['hp_rsae'] / (bowl['hp_balls'] / 6.0)).round(2)
    bowl['base_rsae_per_over'] = (bowl['base_rsae'] / (bowl['base_balls'] / 6.0)).round(2)
    bowl['raw_hp_econ'] = (bowl['hp_runs'] / (bowl['hp_balls'] / 6.0)).round(2)
    bowl['raw_base_econ'] = (bowl['base_runs'] / (bowl['base_balls'] / 6.0)).round(2)
    bowl['raw_clutch_delta'] = (bowl['hp_rsae_per_over'] - bowl['base_rsae_per_over']).round(2)
    bowl['hp_wkt_per_100'] = (bowl['hp_wickets'] / bowl['hp_balls'] * 100).round(2)
    bowl['hp_dot_pct'] = (bowl['hp_dots'] / bowl['hp_balls'] * 100).round(2)

    # Empirical Bayes Shrinkage
    bowl['bayes_hp_rsae'] = empirical_bayes_shrinkage(bowl['hp_rsae_per_over'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_clutch_delta'] = empirical_bayes_shrinkage(bowl['raw_clutch_delta'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_wkt_rate'] = empirical_bayes_shrinkage(bowl['hp_wkt_per_100'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_dot_pct'] = empirical_bayes_shrinkage(bowl['hp_dot_pct'], bowl['hp_balls'], prior_weight=150.0)
    bowl['bayes_hp_sr'] = (100.0 / bowl['bayes_wkt_rate']).round(2)
    bowl['bayes_consistency_pct'] = empirical_bayes_shrinkage(bowl['raw_consistency_pct'], bowl['hp_matches'], prior_weight=10.0)
    bowl['uncertainty_se'] = (bowl['rsae_std'] / np.sqrt(np.maximum(bowl['hp_matches'], 1))).round(2)

    # Composite Bowling Clutch & Reliability Score (0 - 100):
    # 35% Phase-Normalized Runs Saved (bayes_hp_rsae)
    # 25% Bayesian Wicket-Taking Frequency (bayes_wkt_rate)
    # 20% Match-to-Match Consistency (bayes_consistency_pct)
    # 20% Clutch Delta + Dot Ball Choke (bayes_clutch_delta + bayes_dot_pct)
    rsae_norm = ((bowl['bayes_hp_rsae'] + 1.0) / 3.5).clip(0, 1.2) * 35
    wkt_norm = (bowl['bayes_wkt_rate'] / 9.5).clip(0, 1.2) * 25
    bcons_norm = (bowl['bayes_consistency_pct'] / 95.0).clip(0, 1.1) * 20
    cd_dot_norm = (((bowl['bayes_clutch_delta'] + 1.0) / 2.5).clip(0, 1.2) * 10) + ((bowl['bayes_dot_pct'] / 45.0).clip(0, 1.1) * 10)

    bowl['bowling_clutch_score'] = (rsae_norm + wkt_norm + bcons_norm + cd_dot_norm).round(2)

    # Filter qualified bowlers (>= 30 HP overs and >= 15 HP matches)
    qual_bowl = bowl[(bowl['hp_overs'] >= 30.0) & (bowl['hp_matches'] >= 15)].copy()
    qual_bowl = cluster_bowler_archetypes(qual_bowl)
    top_bowlers = qual_bowl.sort_values(by='bowling_clutch_score', ascending=False).reset_index()
    top_bowlers['rank'] = top_bowlers.index + 1

    # Export updated files
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    os.makedirs(proc_dir, exist_ok=True)
    top_batters.head(10).to_csv(os.path.join(proc_dir, "ml_top10_batters_under_pressure.csv"), index=False)
    top_bowlers.head(10).to_csv(os.path.join(proc_dir, "ml_top10_bowlers_under_pressure.csv"), index=False)
    top_batters.to_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"), index=False)
    top_bowlers.to_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"), index=False)

    print("\n" + "=" * 105)
    print("  🏆 TOP 10 BATTERS UNDER PRESSURE (CONTEXT + BAYES + CONSISTENCY + K-MEANS ARCHETYPE)")
    print("=" * 105)
    bat_cols = ['rank', 'striker_name', 'hp_matches', 'bayes_hp_rae', 'bayes_clutch_delta', 'bayes_consistency_pct', 'batting_clutch_score', 'ml_archetype']
    print(top_batters.head(10)[bat_cols].to_string(index=False))

    print("\n" + "=" * 105)
    print("  🎯 TOP 10 BOWLERS UNDER PRESSURE (PHASE-NORMALIZED + BAYES + CONSISTENCY + K-MEANS ARCHETYPE)")
    print("=" * 105)
    bowl_cols = ['rank', 'bowler_name', 'hp_matches', 'hp_overs', 'bayes_hp_rsae', 'bayes_hp_sr', 'bayes_consistency_pct', 'bowling_clutch_score', 'ml_archetype']
    print(top_bowlers.head(10)[bowl_cols].to_string(index=False))
    print("=" * 105)

    return top_batters, top_bowlers

if __name__ == "__main__":
    run_full_ml_pipeline()
