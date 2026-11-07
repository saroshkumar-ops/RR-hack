"""
Composite Talent Ranker and Youngest Uncapped Star Scoring Engine
"""
import pandas as pd
from src.config import AGE_CEILING_WEIGHTS
from src.metrics.batting_metrics import compute_batting_metrics
from src.metrics.bowling_metrics import compute_bowling_metrics
from src.models.rr_squad_fit import assign_tactical_archetype, estimate_auction_bracket

def get_age_multiplier(age: int) -> tuple[float, str]:
    """Returns age multiplier and age runway classification."""
    if age <= 19:
        w = AGE_CEILING_WEIGHTS["TEEN_PRODIGY"]
    elif age <= 22:
        w = AGE_CEILING_WEIGHTS["EARLY_PRIME"]
    elif age <= 24:
        w = AGE_CEILING_WEIGHTS["MID_20S"]
    else:
        w = AGE_CEILING_WEIGHTS["MATURE"]
    return w["multiplier"], w["tier"]

def rank_uncapped_players(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    End-to-end talent identification pipeline:
    1. Computes phase-specific batting metrics
    2. Computes situational bowling metrics
    3. Calculates role-weighted base impact
    4. Applies Youth Development / Age-Ceiling curve
    5. Evaluates RR Tactical Archetype fit
    6. Outputs sorted rankings and auction valuations
    """
    df = df_raw.copy()

    # 1. Compute Base Metrics
    df = compute_batting_metrics(df)
    df = compute_bowling_metrics(df)

    # 2. Base Composite Capability Score
    # For pure batters: 90% batting, 10% bowling
    # For pure bowlers: 90% bowling, 10% batting
    # For all-rounders: 55% primary, 45% secondary
    base_scores = []
    age_multipliers = []
    age_tiers = []
    archetypes = []
    fit_scores = []
    tactical_reasons = []

    for _, row in df.iterrows():
        b_score = row['batting_impact_score']
        bw_score = row['bowling_impact_score']

        if b_score > 0 and bw_score > 0:
            # All-rounder
            composite_base = (max(b_score, bw_score) * 0.55) + (min(b_score, bw_score) * 0.45)
        elif b_score > 0:
            composite_base = b_score
        else:
            composite_base = bw_score

        # Age runway adjustment
        mult, tier = get_age_multiplier(row['age'])
        age_multipliers.append(mult)
        age_tiers.append(tier)

        # Tactical fit
        arch_info = assign_tactical_archetype(row)
        archetypes.append(arch_info['title'])
        fit_scores.append(arch_info['fit_score'])
        tactical_reasons.append(arch_info['tactical_reasoning'])

        # Blend base capability (70%) with tactical fit (30%), then multiply by age runway
        blended = (composite_base * 0.70) + (arch_info['fit_score'] * 0.30)
        final_rating = round(blended * mult, 2)
        base_scores.append(final_rating)

    df['age_multiplier'] = age_multipliers
    df['age_runway_tier'] = age_tiers
    df['rr_tactical_archetype'] = archetypes
    df['tactical_fit_score'] = fit_scores
    df['tactical_reasoning'] = tactical_reasons
    df['royals_composite_score'] = base_scores

    # Auction brackets
    df['estimated_auction_bracket'] = [
        estimate_auction_bracket(score, age)
        for score, age in zip(df['royals_composite_score'], df['age'])
    ]

    # Sort descending by composite score, prioritizing younger age on ties
    df = df.sort_values(by=['royals_composite_score', 'age'], ascending=[False, True]).reset_index(drop=True)
    df['rank'] = df.index + 1

    return df
