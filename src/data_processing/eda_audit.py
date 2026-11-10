"""
Phase 1: Exploratory Data Analysis & Data Anatomy Audit
Reconstructs ball-by-ball match physics, audits anomalies, and logs foundational distributions.
"""
import os
import sys
import json
import pandas as pd
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_DIR = os.path.join(REPO_ROOT, "data/raw/extracted/SupeRR Selector Season 2 - Problem Statement - Data Pack/SupeRR Selector Season 2 - Data Pack")

def run_eda_audit():
    print("=" * 80)
    print("  PHASE 1: EXPLORATORY DATA ANALYSIS (EDA) & DATA ANATOMY AUDIT")
    print("=" * 80)

    # 1. Load Data
    print("[*] Ingesting relational tables...")
    df_comp = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
    df_matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    df_players = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
    df_bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"))

    print(f"  • Competitions:  {len(df_comp)} tournaments ({df_comp['match_format'].value_counts().to_dict()})")
    print(f"  • Matches:       {len(df_matches)} matches ({len(df_matches[df_matches['knock_out']==1])} knockouts)")
    print(f"  • Master Players:{len(df_players)} mappings ({df_players['player_name'].nunique()} unique names)")
    print(f"  • Deliveries:    {len(df_bbb):,} ball events")

    # 2. Audit Extras and Runs
    print("\n[*] Auditing Event Schema & Extras Mechanics...")
    et = df_bbb['extras_type'].values
    ex2 = df_bbb['extras_2_runs'].fillna(0).values

    is_wide = (et == 'wide')
    is_nb = (et == 'Overstep')
    is_bye_lb = np.isin(et, ['byes', 'legbyes', 'other'])

    team_extras = np.zeros(len(df_bbb))
    team_extras[is_wide] = 1 + ex2[is_wide]
    team_extras[is_nb] = 1 + ex2[is_nb]
    team_extras[is_bye_lb] = np.where(ex2[is_bye_lb] > 0, ex2[is_bye_lb], 1)

    bowler_extras = np.zeros(len(df_bbb))
    bowler_extras[is_wide] = 1 + ex2[is_wide]
    bowler_extras[is_nb] = 1 + ex2[is_nb]

    total_bat_runs = int(df_bbb['runs'].sum())
    total_team_runs = int(total_bat_runs + team_extras.sum())
    total_bowler_runs = int(total_bat_runs + bowler_extras.sum())
    total_legal_balls = int((~np.isin(et, ['wide', 'Overstep'])).sum())
    total_wickets = int(df_bbb['is_wicket'].sum())

    print(f"  • Total Bat Runs:      {total_bat_runs:,}")
    print(f"  • Total Team Runs:     {total_team_runs:,}")
    print(f"  • Total Bowler Runs:   {total_bowler_runs:,}")
    print(f"  • Legal Deliveries:    {total_legal_balls:,} ({total_legal_balls/len(df_bbb)*100:.2f}%)")
    print(f"  • Total Wickets Taken: {total_wickets:,} ({total_wickets/len(df_bbb)*100:.2f}% wicket hazard)")

    # 3. Export Audit Summary
    os.makedirs(os.path.join(REPO_ROOT, "data/processed"), exist_ok=True)
    audit_summary = {
        "competitions_count": len(df_comp),
        "matches_count": len(df_matches),
        "total_balls": len(df_bbb),
        "legal_balls": total_legal_balls,
        "total_team_runs": total_team_runs,
        "total_bowler_runs": total_bowler_runs,
        "total_wickets": total_wickets,
        "dot_ball_count": int(((df_bbb['runs'] == 0) & (~df_bbb['is_wicket']) & (team_extras == 0)).sum()),
        "fours_count": int((df_bbb['is_four'] == True).sum()),
        "sixes_count": int((df_bbb['is_six'] == True).sum()),
        "innings_distribution": df_bbb['innings'].value_counts().to_dict()
    }

    out_path = os.path.join(REPO_ROOT, "data/processed/eda_audit_summary.json")
    with open(out_path, "w") as f:
        json.dump(audit_summary, f, indent=4)

    print(f"\n[+] Audit summary saved to: {out_path}")
    print("=" * 80)
    return audit_summary

if __name__ == "__main__":
    run_eda_audit()
