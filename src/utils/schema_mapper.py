"""
Dynamic Schema Mapper and Data Preprocessing Utilities
Auto-detects varied column nomenclature across cricket datasets.
"""
import re
import pandas as pd

# Canonical internal schema mapping
CANONICAL_COLUMNS = {
    'name': ['name', 'player', 'player_name', 'batsman', 'bowler', 'cricketer'],
    'age': ['age', 'player_age', 'dob_age', 'current_age'],
    'role': ['role', 'player_role', 'primary_role', 'specialization', 'type'],
    'domestic_league': ['domestic_league', 'tournament', 'competition', 'league', 'team_league'],
    'state_team': ['state_team', 'state', 'team', 'state_association'],
    'batting_style': ['batting_style', 'bat_style', 'batting_hand', 'bat_hand'],
    'bowling_style': ['bowling_style', 'bowl_style', 'bowling_type', 'bowl_type'],
    
    # Batting
    'runs': ['runs', 'r', 'runs_scored', 'total_runs'],
    'balls': ['balls', 'b', 'balls_faced', 'bf'],
    'strike_rate': ['strike_rate', 'sr', 'batting_sr', 'str_rate'],
    'batting_avg': ['batting_avg', 'avg', 'average', 'bat_avg'],
    'fours': ['fours', '4s', 'fours_hit'],
    'sixes': ['sixes', '6s', 'sixes_hit'],
    'dot_pct_bat': ['dot_pct_bat', 'dot_pct', 'dot_percentage', 'bat_dot_pct', 'dot%_bat'],
    'pp_sr': ['pp_sr', 'powerplay_sr', 'sr_pp', 'sr_overs_1_6'],
    'mid_sr': ['mid_sr', 'middle_sr', 'sr_mid', 'sr_overs_7_15'],
    'death_sr': ['death_sr', 'death_overs_sr', 'sr_death', 'sr_overs_16_20'],
    'sr_vs_pace': ['sr_vs_pace', 'pace_sr', 'sr_pace'],
    'sr_vs_spin': ['sr_vs_spin', 'spin_sr', 'sr_spin'],
    
    # Bowling
    'overs': ['overs', 'ov', 'overs_bowled'],
    'wickets': ['wickets', 'w', 'wkts', 'total_wickets'],
    'bowling_econ': ['bowling_econ', 'econ', 'economy', 'economy_rate'],
    'bowling_avg': ['bowling_avg', 'bowl_avg', 'bowling_average'],
    'bowling_sr': ['bowling_sr', 'bowl_sr', 'bowling_strike_rate'],
    'dot_pct_bowl': ['dot_pct_bowl', 'bowl_dot_pct', 'dot%_bowl', 'bowling_dot_pct'],
    'pp_econ': ['pp_econ', 'powerplay_econ', 'econ_pp', 'econ_overs_1_6'],
    'mid_econ': ['mid_econ', 'middle_econ', 'econ_mid', 'econ_overs_7_15'],
    'death_econ': ['death_econ', 'death_overs_econ', 'econ_death', 'econ_overs_16_20'],
    'boundary_conceded_pct': ['boundary_conceded_pct', 'boundary_conceded%', 'bnd_conceded_pct']
}

def clean_column_name(col: str) -> str:
    """Standardizes column names for pattern matching."""
    return re.sub(r'[^a-z0-9]', '', str(col).lower())

def standardize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-detects and renames incoming columns to canonical names.
    Provides fallback defaults for any non-mandatory missing columns.
    """
    df = df.copy()
    cleaned_cols = {col: clean_column_name(col) for col in df.columns}
    rename_map = {}

    for canonical, aliases in CANONICAL_COLUMNS.items():
        matched = False
        for col, cleaned in cleaned_cols.items():
            if cleaned in [clean_column_name(a) for a in aliases]:
                rename_map[col] = canonical
                matched = True
                break
        
        # If not found directly, check substring matching
        if not matched:
            for col, cleaned in cleaned_cols.items():
                if any(clean_column_name(a) == cleaned for a in aliases):
                    rename_map[col] = canonical
                    break

    df = df.rename(columns=rename_map)

    # Provide safe fallback numeric defaults if optional split metrics are absent
    numeric_defaults = {
        'runs': 0, 'balls': 0, 'strike_rate': 0.0, 'batting_avg': 0.0,
        'fours': 0, 'sixes': 0, 'dot_pct_bat': 40.0,
        'pp_sr': 130.0, 'mid_sr': 130.0, 'death_sr': 150.0,
        'sr_vs_pace': 135.0, 'sr_vs_spin': 130.0,
        'overs': 0.0, 'wickets': 0, 'bowling_econ': 8.5,
        'bowling_avg': 30.0, 'bowling_sr': 20.0, 'dot_pct_bowl': 38.0,
        'pp_econ': 7.5, 'mid_econ': 7.8, 'death_econ': 10.5,
        'boundary_conceded_pct': 16.0, 'age': 22
    }

    for col, default_val in numeric_defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default_val)

    if 'role' not in df.columns:
        df['role'] = 'Cricketer'
    if 'domestic_league' not in df.columns:
        df['domestic_league'] = 'Indian Domestic'
    if 'name' not in df.columns:
        df['name'] = [f"Player {i+1}" for i in range(len(df))]

    return df

def apply_sample_size_filter(df: pd.DataFrame, min_balls: int = 40, min_overs: float = 10.0) -> pd.DataFrame:
    """
    Filters out statistical noise caused by micro-sample sizes
    (e.g., players with 1 innings who struck at 250 on 4 balls).
    """
    qualifies_bat = df['balls'] >= min_balls
    qualifies_bowl = df['overs'] >= min_overs
    # Keep if player qualifies in either discipline
    return df[qualifies_bat | qualifies_bowl].copy()
