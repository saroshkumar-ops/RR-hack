"""
Execution Pipeline: Ingests data, runs ranking engine, and outputs Top 10 Picks
"""
import os
import sys
import glob

# Ensure repo root is in python path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from tabulate import tabulate
from src.models.talent_ranker import rank_uncapped_players

def load_data() -> pd.DataFrame:
    """Loads raw data pack if available, otherwise falls back to sample dataset."""
    raw_files = glob.glob(os.path.join(REPO_ROOT, "data/raw/*.csv")) + glob.glob(os.path.join(REPO_ROOT, "data/raw/*.xlsx"))
    if raw_files:
        filepath = raw_files[0]
        print(f"[+] Found official data pack file: {filepath}")
        if filepath.endswith('.xlsx'):
            return pd.read_excel(filepath)
        return pd.read_csv(filepath)
    
    sample_path = os.path.join(REPO_ROOT, "data/sample/uncapped_players_sample.csv")
    print(f"[*] No raw data pack found in data/raw/. Using sample benchmark dataset ({sample_path})...")
    return pd.read_csv(sample_path)

def main():
    print("=" * 80)
    print("  RAJASTHAN ROYALS - SupeRR Selector Season 2: Talent Identification Engine")
    print("=" * 80)

    df_raw = load_data()
    print(f"[+] Ingested {len(df_raw)} domestic player records.")

    print("[*] Running analytical models & tactical squad fit algorithms...")
    df_ranked = rank_uncapped_players(df_raw)

    # Save processed rankings
    processed_dir = os.path.join(REPO_ROOT, "data/processed")
    os.makedirs(processed_dir, exist_ok=True)
    df_ranked.to_csv(os.path.join(processed_dir, "ranked_uncapped_players.csv"), index=False)
    
    top10 = df_ranked.head(10).copy()
    top10.to_csv(os.path.join(processed_dir, "top10_uncapped_stars.csv"), index=False)

    print("\n" + "=" * 80)
    print("  TOP 10 YOUNGEST UNCAPPED TARGETS FOR RAJASTHAN ROYALS (IPL 2027)")
    print("=" * 80)
    
    display_cols = ['rank', 'name', 'age', 'role', 'domestic_league', 'royals_composite_score', 'rr_tactical_archetype']
    print(tabulate(top10[display_cols], headers='keys', tablefmt='fancy_grid', showindex=False))

    print("\n[+] Top 10 player profiles saved to: data/processed/top10_uncapped_stars.csv")
    print("[+] Full rankings saved to: data/processed/ranked_uncapped_players.csv")

if __name__ == "__main__":
    main()
