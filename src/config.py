"""
Configuration and Parameters for Rajasthan Royals Talent Identification Engine
"""

# Rajasthan Royals Team Archetypes & Needs Priority for IPL 2027
RR_TACTICAL_PRIORITIES = {
    "FINISHER_PACE_HITTER": {
        "title": "Death-Overs Power Finisher",
        "priority_level": "HIGH",
        "description": "Indian batter capable of striking at 170+ from ball 1, especially in overs 16-20 against express pace.",
        "key_metrics": ["death_sr", "sr_vs_pace", "boundary_pct"]
    },
    "DEATH_SPECIALIST_PACER": {
        "title": "Death-Overs Enforcer / Yorker Specialist",
        "priority_level": "VERY HIGH",
        "description": "Domestic fast bowler who can execute yorkers, hard lengths, and keep death economy under 9.0 in overs 16-20.",
        "key_metrics": ["death_econ", "dot_pct_bowl", "boundary_conceded_pct"]
    },
    "MYSTERY_WRIST_SPINNER": {
        "title": "Middle-Overs Attacking Spinner",
        "priority_level": "MEDIUM-HIGH",
        "description": "Wrist-spinner or mystery spinner capable of picking wickets between overs 7-15 with economy under 7.2.",
        "key_metrics": ["mid_econ", "bowling_sr", "dot_pct_bowl"]
    },
    "ALL_ROUNDER_BALANCE": {
        "title": "Lower-Order Power All-Rounder",
        "priority_level": "HIGH",
        "description": "Multi-utility domestic cricketer offering 2-4 reliable overs and high strike-rate lower-order batting.",
        "key_metrics": ["death_sr", "bowling_econ", "wickets"]
    },
    "DYNAMIC_TOP_ORDER": {
        "title": "High-Tempo Opening / No.3 Batter",
        "priority_level": "MEDIUM",
        "description": "Batter who maximizes the 6-over Powerplay with strike rate >155 while minimizing dot-ball consumption.",
        "key_metrics": ["pp_sr", "dot_pct_bat", "batting_avg"]
    }
}

# Age-Ceiling Multiplier (Rewards youth with higher development runway)
AGE_CEILING_WEIGHTS = {
    "TEEN_PRODIGY": {"max_age": 19, "multiplier": 1.25, "tier": "Exceptional Runway (<20)"},
    "EARLY_PRIME": {"max_age": 22, "multiplier": 1.15, "tier": "High Development Runway (20-22)"},
    "MID_20S": {"max_age": 24, "multiplier": 1.05, "tier": "Moderate Runway (23-24)"},
    "MATURE": {"max_age": 100, "multiplier": 0.95, "tier": "Immediate Plug & Play (25+)"}
}

# Baseline League Benchmarks for T20 normalization
BENCHMARKS = {
    "batting": {
        "avg_strike_rate": 138.0,
        "pp_sr": 135.0,
        "middle_sr": 132.0,
        "death_sr": 170.0,
        "boundary_runs_pct": 58.0,
        "dot_pct": 36.0
    },
    "bowling": {
        "avg_economy": 8.10,
        "pp_econ": 7.40,
        "middle_econ": 7.60,
        "death_econ": 10.20,
        "dot_pct": 42.0,
        "boundary_conceded_pct": 16.0
    }
}
