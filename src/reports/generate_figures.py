"""
Generates High-Resolution Publication Figures for the Methodology Report
Styled with Rajasthan Royals branding (#EA1A80 Pink, #001D48 Blue, #FDB913 Gold).
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.ml.win_probability_model import WinProbabilityModel
from src.ml.context_normalizer import compute_context_baselines

# Styling
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CCCCCC"
plt.rcParams["axes.linewidth"] = 0.8

RR_PINK = "#EA1A80"
RR_BLUE = "#001D48"
RR_GOLD = "#FDB913"
RR_CYAN = "#0075FF"

def generate_all_figures():
    fig_dir = os.path.join(REPO_ROOT, "reports/figures")
    os.makedirs(fig_dir, exist_ok=True)
    data_dir = os.path.join(REPO_ROOT, "data/raw/extracted/SupeRR Selector Season 2 - Problem Statement - Data Pack/SupeRR Selector Season 2 - Data Pack")
    proc_dir = os.path.join(REPO_ROOT, "data/processed")

    print("[*] Loading raw data for delivery-level visualizations...")
    df_bbb = pd.read_csv(os.path.join(data_dir, "ball_by_ball.csv"))
    df_matches = pd.read_csv(os.path.join(data_dir, "matches.csv"))
    df_comp = pd.read_csv(os.path.join(data_dir, "competitions.csv"))

    wp = WinProbabilityModel()
    df_f = wp.prepare_features(df_bbb, df_matches)
    wp.fit(df_f)
    df_a = wp.compute_leverage_index(df_f)

    et = df_a['extras_type'].values
    ex2 = df_a['extras_2_runs'].fillna(0).values
    b_ex = np.zeros(len(df_a))
    b_ex[et == 'wide'] = 1 + ex2[et == 'wide']
    b_ex[et == 'Overstep'] = 1 + ex2[et == 'Overstep']
    df_a['bowler_runs'] = df_a['runs'] + b_ex

    df_ctx = compute_context_baselines(df_a, df_matches, df_comp)

    df_bat = pd.read_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"))
    df_bowl = pd.read_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"))

    # -------------------------------------------------------------------------
    # FIGURE 1: RR Case Study (Match 14113 - RR vs LSG, Won by 3 Runs)
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 1: RR Match 14113 Leverage Case Study...")
    m_balls = df_a[(df_a['match_id'] == 14113) & (df_a['innings'] == 2)].copy().reset_index(drop=True)
    m_balls['ball_idx'] = m_balls.index + 1

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax1.plot(m_balls['ball_idx'], m_balls['rrr'], color=RR_BLUE, lw=2.2, label='Required Run Rate (RRR)')
    ax1.axhline(8.3, color='gray', linestyle='--', alpha=0.8, label='Starting Target RRR (8.30)')
    ax1.set_ylabel('Required Run Rate', fontweight='bold', color=RR_BLUE)
    ax1.set_title('Case Study: Rajasthan Royals vs. LSG (Match 14113 — RR Won by 3 Runs)', fontsize=13, fontweight='bold', color=RR_BLUE)
    ax1.legend(loc='upper left', frameon=True)

    ax2.plot(m_balls['ball_idx'], m_balls['ml_pressure_index'], color=RR_PINK, lw=2.5, label='ML Pressure Index (Leverage)')
    ax2.axhline(6.5, color='black', linestyle=':', lw=1.2, label='High-Pressure Threshold (6.5)')
    ax2.fill_between(m_balls['ball_idx'], 6.5, m_balls['ml_pressure_index'],
                     where=(m_balls['ml_pressure_index'] >= 6.5), color=RR_PINK, alpha=0.25)
    ax2.set_xlabel('Legal & Extra Deliveries in 2nd Innings (Chase)', fontweight='bold')
    ax2.set_ylabel('Pressure Index (0–10)', fontweight='bold', color=RR_PINK)
    ax2.set_ylim(0, 10.6)
    ax2.legend(loc='upper left', frameon=True)

    # Annotate final over peak (Over 20 climax: Kuldeep Sen vs. Marcus Stoinis)
    fin_over = m_balls[(m_balls['overid'] == 20) & (m_balls['striker_name'] == 'Marcus Stoinis')]
    peak_idx = fin_over['ml_pressure_index'].idxmax() if not fin_over.empty else m_balls['ml_pressure_index'].idxmax()
    peak_x = m_balls.loc[peak_idx, 'ball_idx']
    peak_y = m_balls.loc[peak_idx, 'ml_pressure_index']
    ax2.annotate(f'Final Over Defense (PI = {peak_y:.1f})\nKuldeep Sen vs. Stoinis',
                 xy=(peak_x, peak_y), xytext=(max(peak_x - 42, 10), 8.0),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.2, headwidth=7),
                 fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor=RR_GOLD, alpha=0.9))

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig1_rr_case_study_leverage.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 2: Format & Phase Context Normalization Justification
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 2: Format & Phase Par Discrepancy...")
    legal = df_ctx[df_ctx['is_legal'] == True]
    par_df = legal.groupby(['match_format', 'phase']).agg(
        implied_econ=('bowler_runs', lambda x: x.mean() * 6.0),
        implied_sr=('runs', lambda x: x.mean() * 100.0)
    ).reset_index()

    phase_order = ['Powerplay', 'Middle', 'Death']
    par_df['phase'] = pd.Categorical(par_df['phase'], categories=phase_order, ordered=True)
    par_df = par_df.sort_values('phase')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    sns.barplot(data=par_df, x='phase', y='implied_sr', hue='match_format', palette=[RR_PINK, RR_BLUE], ax=ax1)
    ax1.set_title('Expected Strike Rate by Format & Phase', fontweight='bold')
    ax1.set_ylabel('Par Strike Rate (Runs / 100 Balls)')
    ax1.set_xlabel('Innings Phase')
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%.1f', padding=3, fontsize=8.5)
    ax1.set_ylim(0, 215)
    ax1.legend(title='Format', loc='upper left', fontsize=8.5, title_fontsize=8.5)

    sns.barplot(data=par_df, x='phase', y='implied_econ', hue='match_format', palette=[RR_PINK, RR_BLUE], ax=ax2)
    ax2.set_title('Expected Economy Rate by Format & Phase', fontweight='bold')
    ax2.set_ylabel('Par Economy (Runs / Over)')
    ax2.set_xlabel('Innings Phase')
    for container in ax2.containers:
        ax2.bar_label(container, fmt='%.2f', padding=3, fontsize=8.5)
    ax2.set_ylim(0, 12.8)
    ax2.legend(title='Format', loc='upper left', fontsize=8.5, title_fontsize=8.5)

    plt.suptitle('Why Context Normalization Is Mandatory: T20 (IPL) vs. T20I Scoring Environments', fontsize=12.5, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_format_context_bias.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 3: Top 10 Batters Under Pressure (Baseline vs Pressure + Consistency)
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 3: Top 10 Batters Evidence...")
    top10_bat = df_bat.head(10).sort_values('batting_clutch_score', ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    
    y_pos = np.arange(len(top10_bat))
    bar_h = 0.35

    ax1.barh(y_pos - bar_h/2, top10_bat['base_rae_per_100'], height=bar_h, color='#95a5a6', label='Normal Baseline (LI < 6.5)')
    ax1.barh(y_pos + bar_h/2, top10_bat['hp_rae_per_100'], height=bar_h, color=RR_PINK, label='High Pressure (LI >= 6.5)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"#{int(r)} {n}" for r, n in zip(top10_bat['rank'], top10_bat['striker_name'])], fontweight='bold')
    ax1.axvline(0, color='black', lw=0.8)
    ax1.set_xlabel('Runs Above Expected / 100 Balls (vs. Par)', fontweight='bold')
    ax1.set_title('Baseline vs. High-Pressure Scoring Shift', fontweight='bold', pad=26)
    ax1.set_xlim(-22, 48)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=2, fontsize=8.2, frameon=True)

    bars2 = ax2.barh(y_pos, top10_bat['batting_clutch_score'], color=RR_BLUE, height=0.55)
    ax2.set_xlabel('Composite Batting Clutch Score (0–100)', fontweight='bold')
    ax2.set_title('Final Clutch Rating & Match Consistency', fontweight='bold', pad=26)
    ax2.set_xlim(0, 108)
    for idx, (bar, cons, m_cnt) in enumerate(zip(bars2, top10_bat['bayes_consistency_pct'], top10_bat['hp_matches'])):
        ax2.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height()/2,
                 f"{bar.get_width():.1f} ({cons:.0f}% across {int(m_cnt)}m)",
                 va='center', fontsize=8.3, fontweight='bold', color=RR_BLUE)

    plt.suptitle('Top 10 Batters Under Pressure: Statistical Evidence & Ordering', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_top10_batters_evidence.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 4: Top 10 Bowlers Under Pressure (Runs Saved + Consistency + Wkts)
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 4: Top 10 Bowlers Evidence...")
    top10_bowl = df_bowl.head(10).sort_values('bowling_clutch_score', ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    y_pos = np.arange(len(top10_bowl))

    ax1.barh(y_pos - bar_h/2, top10_bowl['base_rsae_per_over'], height=bar_h, color='#95a5a6', label='Normal Baseline (LI < 6.5)')
    ax1.barh(y_pos + bar_h/2, top10_bowl['hp_rsae_per_over'], height=bar_h, color=RR_CYAN, label='High Pressure (LI >= 6.5)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"#{int(r)} {n}" for r, n in zip(top10_bowl['rank'], top10_bowl['bowler_name'])], fontweight='bold')
    ax1.axvline(0, color='black', lw=0.8)
    ax1.set_xlabel('Runs Saved Above Expected / Over (vs. Phase Par)', fontweight='bold')
    ax1.set_title('Phase-Adjusted Run Suppression Shift', fontweight='bold')
    ax1.set_xlim(-1.0, 2.75)
    ax1.legend(loc='lower right', fontsize=8.2, frameon=True)

    bars_bw = ax2.barh(y_pos, top10_bowl['bowling_clutch_score'], color=RR_PINK, height=0.55)
    ax2.set_xlabel('Composite Bowling Clutch Score (0–100)', fontweight='bold')
    ax2.set_title('Final Clutch Rating & Match Consistency', fontweight='bold')
    ax2.set_xlim(0, 124)
    for bar, cons, w_sr in zip(bars_bw, top10_bowl['bayes_consistency_pct'], top10_bowl['bayes_hp_sr']):
        ax2.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height()/2,
                 f"{bar.get_width():.1f} ({cons:.0f}% cons | SR {w_sr:.1f})",
                 va='center', fontsize=8.2, fontweight='bold', color=RR_BLUE)

    plt.suptitle('Top 10 Bowlers Under Pressure: Phase-Normalized Evidence & Ordering', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig4_top10_bowlers_evidence.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 5: Empirical Bayes Shrinkage & Reliability Funnel
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 5: Empirical Bayes Shrinkage Funnel...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    ax1.scatter(df_bat['hp_balls'], df_bat['raw_hp_sr'], alpha=0.4, color='gray', s=35, label='Raw Observed Pressure SR')
    ax1.scatter(df_bat['hp_balls'], df_bat['bayes_hp_sr'], alpha=0.85, color=RR_PINK, s=45, label='Bayesian-Shrunk Pressure SR')
    bat_offsets = [(14, 14), (10, -24), (16, -2), (-28, 14), (-88, 18)]
    for (_, r), (dx, dy) in zip(df_bat.head(5).iterrows(), bat_offsets):
        ax1.annotate(r['striker_name'], (r['hp_balls'], r['bayes_hp_sr']),
                     xytext=(dx, dy), textcoords='offset points', fontsize=7.8, fontweight='bold',
                     arrowprops=dict(arrowstyle='-', color='#666666', lw=0.7),
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.75))
    ax1.set_title('Batters: Empirical Bayes Shrinkage Funnel', fontweight='bold')
    ax1.set_xlabel('High-Pressure Balls Faced (Sample Size $n_i$)')
    ax1.set_ylabel('Strike Rate Under Pressure')
    ax1.set_xlim(df_bat['hp_balls'].min() - 60, df_bat['hp_balls'].max() + 90)
    ax1.set_ylim(df_bat['raw_hp_sr'].min() - 12, df_bat['raw_hp_sr'].max() + 18)
    ax1.legend(loc='lower right', fontsize=8.2)

    ax2.scatter(df_bowl['hp_overs'], df_bowl['hp_rsae_per_over'], alpha=0.4, color='gray', s=35, label='Raw Observed RSAE/Over')
    ax2.scatter(df_bowl['hp_overs'], df_bowl['bayes_hp_rsae'], alpha=0.85, color=RR_BLUE, s=45, label='Bayesian-Shrunk RSAE/Over')
    bowl_offsets = [(14, -6), (12, 6), (8, 16), (14, 4), (-78, 18)]
    for (_, r), (dx, dy) in zip(df_bowl.head(5).iterrows(), bowl_offsets):
        ax2.annotate(r['bowler_name'], (r['hp_overs'], r['bayes_hp_rsae']),
                     xytext=(dx, dy), textcoords='offset points', fontsize=7.8, fontweight='bold',
                     arrowprops=dict(arrowstyle='-', color='#666666', lw=0.7),
                     bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.75))
    ax2.set_title('Bowlers: Empirical Bayes Shrinkage Funnel', fontweight='bold')
    ax2.set_xlabel('High-Pressure Overs Bowled (Sample Size $n_i$)')
    ax2.set_ylabel('Runs Saved Above Expected / Over')
    ax2.set_xlim(df_bowl['hp_overs'].min() - 10, df_bowl['hp_overs'].max() + 25)
    ax2.set_ylim(df_bowl['hp_rsae_per_over'].min() - 0.35, df_bowl['hp_rsae_per_over'].max() + 0.45)
    ax2.legend(loc='lower right', fontsize=8.2)

    plt.suptitle('Stabilizing Small-Sample Variance via Empirical Bayes Shrinkage', fontsize=12.5, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig5_bayesian_shrinkage_funnel.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[+] All 5 publication figures generated in: {fig_dir}")

if __name__ == "__main__":
    generate_all_figures()
