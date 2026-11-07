"""
Rajasthan Royals Tactical Squad Fit and Valuation Engine
"""
import pandas as pd
from src.config import RR_TACTICAL_PRIORITIES

def assign_tactical_archetype(row: pd.Series) -> dict:
    """
    Classifies player into specific Rajasthan Royals Tactical Archetypes
    and scores their fit for RR.
    """
    role = str(row.get('role', '')).lower()
    death_sr = row.get('death_sr', 0)
    sr_pace = row.get('sr_vs_pace', 0)
    death_econ = row.get('death_econ', 99)
    mid_econ = row.get('mid_econ', 99)
    overs = row.get('overs', 0)
    runs = row.get('runs', 0)
    pp_sr = row.get('pp_sr', 0)

    # 1. Death-Overs Power Finisher
    if death_sr >= 190 and sr_pace >= 165:
        return {
            "archetype": "FINISHER_PACE_HITTER",
            "title": RR_TACTICAL_PRIORITIES["FINISHER_PACE_HITTER"]["title"],
            "fit_score": 95.0,
            "tactical_reasoning": "High-velocity power hitter who executes in overs 16-20; provides RR with late-innings fireworks."
        }
    
    # 2. Death-Overs Enforcer Pacer
    if overs >= 10 and death_econ <= 8.8 and ("pacer" in role or "fast" in str(row.get('bowling_style', '')).lower()):
        return {
            "archetype": "DEATH_SPECIALIST_PACER",
            "title": RR_TACTICAL_PRIORITIES["DEATH_SPECIALIST_PACER"]["title"],
            "fit_score": 96.0,
            "tactical_reasoning": "Exceptional death-overs execution with sub-8.8 economy; directly solves RR's closing bowling needs."
        }

    # 3. Middle-Overs Wrist/Mystery Spinner (must actively bowl)
    if overs >= 10 and ("spin" in role or "break" in str(row.get('bowling_style', '')).lower()) and mid_econ <= 7.2:
        return {
            "archetype": "MYSTERY_WRIST_SPINNER",
            "title": RR_TACTICAL_PRIORITIES["MYSTERY_WRIST_SPINNER"]["title"],
            "fit_score": 92.0,
            "tactical_reasoning": "High middle-overs choke ability with wicket threat; anchors dry spells between overs 7-15."
        }

    # 4. Multi-utility All-Rounder
    if overs >= 10 and runs >= 100:
        return {
            "archetype": "ALL_ROUNDER_BALANCE",
            "title": RR_TACTICAL_PRIORITIES["ALL_ROUNDER_BALANCE"]["title"],
            "fit_score": 88.0,
            "tactical_reasoning": "Two-way cricketer providing playing XI balance and depth without occupying an overseas slot."
        }

    # 5. Dynamic Powerplay Batter
    if pp_sr >= 150 or "open" in role or "top-order" in role:
        return {
            "archetype": "DYNAMIC_TOP_ORDER",
            "title": RR_TACTICAL_PRIORITIES["DYNAMIC_TOP_ORDER"]["title"],
            "fit_score": 85.0,
            "tactical_reasoning": "Explosive powerplay striker capable of setting high-scoring foundations inside the first 6 overs."
        }

    return {
        "archetype": "SQUAD_DEPTH",
        "title": "Domestic Squad Depth",
        "fit_score": 75.0,
        "tactical_reasoning": "Solid domestic profile offering dependable backup utility across match conditions."
    }

def estimate_auction_bracket(score: float, age: int) -> str:
    """
    Estimates realistic IPL auction bidding bracket based on composite rating and age runway.
    """
    if score >= 90 and age <= 21:
        return "₹1.50 Cr - ₹4.00 Cr (High Bidding War Target)"
    elif score >= 82:
        return "₹50 Lakh - ₹1.50 Cr (Mid-Tier Steal)"
    elif score >= 75:
        return "₹30 Lakh - ₹50 Lakh (Base Price Value Pick)"
    else:
        return "₹30 Lakh (Base Price Backup)"
