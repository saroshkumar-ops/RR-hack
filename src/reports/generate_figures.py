"""
Generates 6 Publication-Grade 300-DPI Figures for the Restructured Methodology Report
Reads strictly from Single-Source-of-Truth outputs in data/processed/.
Styled with Rajasthan Royals branding (#EA1A80 Pink, #001D48 Blue, #FDB913 Gold, #0075FF Cyan).
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Styling
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8

RR_PINK = "#EA1A80"
RR_BLUE = "#001D48"
RR_GOLD = "#FDB913"
RR_CYAN = "#0075FF"
RR_SLATE = "#64748B"
RR_RED = "#DC2626"


def generate_all_figures():
    fig_dir = os.path.join(REPO_ROOT, "reports/figures")
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    os.makedirs(fig_dir, exist_ok=True)

    with open(os.path.join(proc_dir, "ml_report_diagnostics.json"), "r", encoding="utf-8") as f:
        diag = json.load(f)

    df_bat = pd.read_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"))
    df_bowl = pd.read_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"))
    excl_bat = pd.read_csv(os.path.join(proc_dir, "ml_excluded_batters.csv"))
    par_df = pd.read_csv(os.path.join(proc_dir, "ml_format_phase_par.csv"))
    m_balls = pd.read_csv(os.path.join(proc_dir, "ml_match14113_inn2.csv"))

    # -------------------------------------------------------------------------
    # FIGURE 1: Pressure Definition — RR Match 14113 Proof + Corpus Separation
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 1: Pressure Definition & Corpus Separation...")
    fig = plt.figure(figsize=(12.4, 4.6))
    gs = gridspec.GridSpec(2, 2, width_ratios=[1.45, 1.0], height_ratios=[0.9, 1.3], hspace=0.14, wspace=0.25)

    ax_rrr = fig.add_subplot(gs[0, 0])
    ax_pi = fig.add_subplot(gs[1, 0], sharex=ax_rrr)
    ax_sep = fig.add_subplot(gs[:, 1])

    ax_rrr.plot(m_balls['ball_idx'], m_balls['rrr'], color=RR_BLUE, lw=2.0, label='Required Run Rate (RRR)')
    ax_rrr.axhline(8.3, color=RR_SLATE, linestyle='--', alpha=0.8, lw=1.2, label='Target RRR (8.30)')
    ax_rrr.set_ylabel('RRR', fontweight='bold', color=RR_BLUE, fontsize=9)
    ax_rrr.set_title('Case Study: RR vs. LSG (Match 14113 — Won by 3 Runs)', fontsize=10.5, fontweight='bold', color=RR_BLUE)
    ax_rrr.legend(loc='upper left', fontsize=7.8, frameon=True)
    plt.setp(ax_rrr.get_xticklabels(), visible=False)

    ax_pi.plot(m_balls['ball_idx'], m_balls['ml_pressure_index'], color=RR_PINK, lw=2.2, label='ML Leverage Index (LI)')
    ax_pi.axhline(6.5, color='#1E293B', linestyle=':', lw=1.2, label='High-Pressure Cutoff (6.5)')
    ax_pi.fill_between(
        m_balls['ball_idx'], 6.5, m_balls['ml_pressure_index'],
        where=(m_balls['ml_pressure_index'] >= 6.5), color=RR_PINK, alpha=0.25
    )
    fin_over = m_balls[(m_balls['overid'] == 20) & (m_balls['striker_name'] == 'Marcus Stoinis')]
    peak_idx = fin_over['ml_pressure_index'].idxmax() if not fin_over.empty else m_balls['ml_pressure_index'].idxmax()
    peak_x = m_balls.loc[peak_idx, 'ball_idx']
    peak_y = m_balls.loc[peak_idx, 'ml_pressure_index']
    ax_pi.annotate(
        f'Over 20 Defense (LI = {peak_y:.1f})\nKuldeep Sen vs. Stoinis',
        xy=(peak_x, peak_y), xytext=(max(peak_x - 52, 8), 7.9),
        arrowprops=dict(facecolor='black', shrink=0.05, width=1.1, headwidth=6),
        fontsize=8.0, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.32', facecolor=RR_GOLD, alpha=0.92)
    )
    ax_pi.set_xlabel('Deliveries in 2nd Innings Chase', fontweight='bold', fontsize=9)
    ax_pi.set_ylabel('Leverage Index (0–10)', fontweight='bold', color=RR_PINK, fontsize=9)
    ax_pi.set_ylim(0, 10.8)
    ax_pi.legend(loc='upper left', fontsize=7.6, frameon=True)

    # Right panel: Corpus Separation (Ordinary LI < 6.5 vs High Pressure LI >= 6.5)
    ord_m = diag['ordinary_vs_hp']['ordinary']
    hp_m = diag['ordinary_vs_hp']['high_pressure']
    cats = ['Wicket\nHazard (%)', 'Boundary\nRate (%)', 'Dot Ball\nRate (%)']
    ord_vals = [ord_m['wicket_pct'], ord_m['boundary_pct'], ord_m['dot_pct']]
    hp_vals = [hp_m['wicket_pct'], hp_m['boundary_pct'], hp_m['dot_pct']]
    x = np.arange(len(cats))
    w = 0.34

    b1 = ax_sep.bar(x - w / 2 - 0.015, ord_vals, width=w, color='#94A3B8', label=f"Ordinary (LI < 6.5 | Mean LI {ord_m['mean_li']})")
    b2 = ax_sep.bar(x + w / 2 + 0.015, hp_vals, width=w, color=RR_PINK, label=f"High Pressure (LI >= 6.5 | Mean LI {hp_m['mean_li']})")
    ax_sep.bar_label(b1, fmt='%.1f%%', padding=3, fontsize=7.6, color='#334155', fontweight='bold')
    ax_sep.bar_label(b2, fmt='%.1f%%', padding=3, fontsize=7.6, color=RR_BLUE, fontweight='bold')
    ax_sep.set_xticks(x)
    ax_sep.set_xticklabels(cats, fontsize=8.8, fontweight='bold')
    ax_sep.set_ylabel('% of Legal Deliveries', fontweight='bold', fontsize=9)
    ax_sep.set_ylim(0, 50)
    ax_sep.set_title('Corpus Separation Across 200,999 Balls', fontsize=10.5, fontweight='bold', color=RR_BLUE)
    ax_sep.legend(loc='upper left', fontsize=7.5, frameon=True)
    ax_sep.text(
        0.03, 0.74,
        f"Wicket hazard +21.8% in HP\n"
        f"({hp_m['balls_per_wkt']} vs {ord_m['balls_per_wkt']} balls/wkt)\n"
        f"Implied SR: {hp_m['implied_sr']:.1f} vs {ord_m['implied_sr']:.1f}\n"
        f"Ord RRR inflated by dead rubbers",
        transform=ax_sep.transAxes, fontsize=7.1, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#F8FAFC', edgecolor=RR_BLUE, lw=0.8)
    )

    plt.savefig(os.path.join(fig_dir, "fig1_pressure_definition_validation.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 2: Empirical Bayes Shrinkage & Reliability Funnel
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 2: Empirical Bayes Shrinkage Funnel...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.3))

    bat_mu0 = np.average(df_bat['raw_hp_sr'], weights=df_bat['hp_balls'])
    ax1.scatter(df_bat['hp_balls'], df_bat['raw_hp_sr'], alpha=0.42, color='#94A3B8', s=35, label='Raw Observed Pressure SR')
    ax1.scatter(df_bat['hp_balls'], df_bat['bayes_hp_sr'], alpha=0.88, color=RR_PINK, s=45, label='Bayesian-Shrunk Pressure SR')
    ax1.axhline(bat_mu0, color=RR_SLATE, linestyle='--', lw=1.0, label=f'Weighted Prior Mean ({bat_mu0:.1f})')
    bat_offsets = [(14, 14), (10, -24), (16, -2), (-28, 14), (-88, 18)]
    for (_, r), (dx, dy) in zip(df_bat.head(5).iterrows(), bat_offsets):
        ax1.annotate(
            r['striker_name'], (r['hp_balls'], r['bayes_hp_sr']),
            xytext=(dx, dy), textcoords='offset points', fontsize=7.6, fontweight='bold',
            arrowprops=dict(arrowstyle='-', color='#64748B', lw=0.7),
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.8)
        )
    ax1.set_title('Batters: Empirical Bayes Shrinkage Funnel (n=51)', fontweight='bold', color=RR_BLUE)
    ax1.set_xlabel('High-Pressure Balls Faced (Sample Size $n_i$)')
    ax1.set_ylabel('Strike Rate Under Pressure')
    ax1.set_xlim(df_bat['hp_balls'].min() - 60, df_bat['hp_balls'].max() + 90)
    ax1.set_ylim(df_bat['raw_hp_sr'].min() - 12, df_bat['raw_hp_sr'].max() + 18)
    ax1.legend(loc='lower right', fontsize=7.6)

    bowl_mu0 = np.average(df_bowl['hp_rsae_per_over'], weights=df_bowl['hp_balls'])
    ax2.scatter(df_bowl['hp_overs'], df_bowl['hp_rsae_per_over'], alpha=0.42, color='#94A3B8', s=35, label='Raw Observed RSAE/Over')
    ax2.scatter(df_bowl['hp_overs'], df_bowl['bayes_hp_rsae'], alpha=0.88, color=RR_BLUE, s=45, label='Bayesian-Shrunk RSAE/Over')
    ax2.axhline(bowl_mu0, color=RR_SLATE, linestyle='--', lw=1.0, label=f'Weighted Prior Mean (+{bowl_mu0:.2f})')
    bowl_offsets = [(18, -8), (12, 8), (10, 16), (-68, 22), (-76, -14)]
    for (_, r), (dx, dy) in zip(df_bowl.head(5).iterrows(), bowl_offsets):
        ax2.annotate(
            r['bowler_name'], (r['hp_overs'], r['bayes_hp_rsae']),
            xytext=(dx, dy), textcoords='offset points', fontsize=7.6, fontweight='bold',
            arrowprops=dict(arrowstyle='-', color='#64748B', lw=0.7),
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none', alpha=0.8)
        )
    ax2.set_title('Bowlers: Empirical Bayes Shrinkage Funnel (n=67)', fontweight='bold', color=RR_BLUE)
    ax2.set_xlabel('High-Pressure Overs Bowled (Sample Size $n_i$)')
    ax2.set_ylabel('Runs Saved Above Expected / Over')
    ax2.set_xlim(df_bowl['hp_overs'].min() - 10, df_bowl['hp_overs'].max() + 25)
    ax2.set_ylim(df_bowl['hp_rsae_per_over'].min() - 0.35, df_bowl['hp_rsae_per_over'].max() + 0.45)
    ax2.legend(loc='lower right', fontsize=7.6)

    plt.suptitle('Stabilizing Small-Sample Volatility via James-Stein Empirical Bayes Shrinkage', fontsize=12, fontweight='bold', color=RR_BLUE)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_bayesian_shrinkage_funnel.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 3: Format & Phase Context Normalization Justification
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 3: Format & Phase Par Discrepancy...")
    phase_order = ['Powerplay', 'Middle', 'Death']
    par_df['phase'] = pd.Categorical(par_df['phase'], categories=phase_order, ordered=True)
    par_df = par_df.sort_values('phase')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 3.9))
    sns.barplot(data=par_df, x='phase', y='par_sr', hue='match_format', palette=[RR_PINK, RR_BLUE], ax=ax1)
    ax1.set_title('Expected Strike Rate by Format & Phase', fontweight='bold', color=RR_BLUE)
    ax1.set_ylabel('Par Strike Rate (Runs / 100 Balls)')
    ax1.set_xlabel('Innings Phase')
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%.1f', padding=3, fontsize=8.5, fontweight='bold')
    ax1.set_ylim(0, 215)
    ax1.legend(title='Format', loc='upper left', fontsize=8.2, title_fontsize=8.2)

    sns.barplot(data=par_df, x='phase', y='par_econ', hue='match_format', palette=[RR_PINK, RR_BLUE], ax=ax2)
    ax2.set_title('Expected Economy Rate by Format & Phase', fontweight='bold', color=RR_BLUE)
    ax2.set_ylabel('Par Economy (Runs / Over)')
    ax2.set_xlabel('Innings Phase')
    for container in ax2.containers:
        ax2.bar_label(container, fmt='%.2f', padding=3, fontsize=8.5, fontweight='bold')
    ax2.set_ylim(0, 12.8)
    ax2.legend(title='Format', loc='upper left', fontsize=8.2, title_fontsize=8.2)

    plt.suptitle('Why Format × Phase Normalization Is Mandatory: Franchise T20 (IPL) vs. T20I Baselines', fontsize=12, fontweight='bold', color=RR_BLUE, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_format_context_bias.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 4: Top 10 Batters Under Pressure
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 4: Top 10 Batters Evidence...")
    top10_bat = df_bat.head(10).sort_values('batting_clutch_score', ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.9), sharey=True)
    y_pos = np.arange(len(top10_bat))
    bar_h = 0.35

    ax1.barh(y_pos - bar_h / 2, top10_bat['base_rae_per_100'], height=bar_h, color='#94A3B8', label='Normal Baseline (LI < 6.5)')
    ax1.barh(y_pos + bar_h / 2, top10_bat['hp_rae_per_100'], height=bar_h, color=RR_PINK, label='High Pressure (LI >= 6.5)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"#{int(r)} {n}" for r, n in zip(top10_bat['rank'], top10_bat['striker_name'])], fontweight='bold')
    ax1.axvline(0, color='black', lw=0.8)
    ax1.set_xlabel('Runs Above Expected / 100 Balls (vs. Par)', fontweight='bold')
    ax1.set_title('Baseline vs. High-Pressure Scoring Shift', fontweight='bold', pad=26, color=RR_BLUE)
    ax1.set_xlim(-22, 48)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=2, fontsize=8.0, frameon=True)

    bars2 = ax2.barh(y_pos, top10_bat['batting_clutch_score'], color=RR_BLUE, height=0.55)
    ax2.set_xlabel('Composite Batting Clutch Score (0–100)', fontweight='bold')
    ax2.set_title('Final Clutch Rating & Match Consistency', fontweight='bold', pad=26, color=RR_BLUE)
    ax2.set_xlim(0, 108)
    for bar, cons, m_cnt in zip(bars2, top10_bat['bayes_consistency_pct'], top10_bat['hp_matches']):
        ax2.text(
            bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.1f} ({cons:.0f}% across {int(m_cnt)}m)",
            va='center', fontsize=8.2, fontweight='bold', color=RR_BLUE
        )

    plt.suptitle('Top 10 Batters Under Pressure: Statistical Evidence & Final Ordering', fontsize=12.5, fontweight='bold', color=RR_BLUE)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig4_top10_batters_evidence.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 5: Top 10 Bowlers Under Pressure
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 5: Top 10 Bowlers Evidence...")
    top10_bowl = df_bowl.head(10).sort_values('bowling_clutch_score', ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.9), sharey=True)
    y_pos = np.arange(len(top10_bowl))

    ax1.barh(y_pos - bar_h / 2, top10_bowl['base_rsae_per_over'], height=bar_h, color='#94A3B8', label='Normal Baseline (LI < 6.5)')
    ax1.barh(y_pos + bar_h / 2, top10_bowl['hp_rsae_per_over'], height=bar_h, color=RR_CYAN, label='High Pressure (LI >= 6.5)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"#{int(r)} {n}" for r, n in zip(top10_bowl['rank'], top10_bowl['bowler_name'])], fontweight='bold')
    ax1.axvline(0, color='black', lw=0.8)
    ax1.set_xlabel('Runs Saved Above Expected / Over (vs. Phase Par)', fontweight='bold')
    ax1.set_title('Phase-Adjusted Run Suppression Shift', fontweight='bold', pad=26, color=RR_BLUE)
    ax1.set_xlim(-1.0, 2.75)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=2, fontsize=8.0, frameon=True)

    bars_bw = ax2.barh(y_pos, top10_bowl['bowling_clutch_score'], color=RR_PINK, height=0.55)
    ax2.set_xlabel('Composite Bowling Clutch Score (0–100)', fontweight='bold')
    ax2.set_title('Final Clutch Rating & Match Consistency', fontweight='bold', pad=26, color=RR_BLUE)
    ax2.set_xlim(0, 124)
    for bar, cons, w_sr in zip(bars_bw, top10_bowl['bayes_consistency_pct'], top10_bowl['bayes_hp_sr']):
        ax2.text(
            bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.1f} ({cons:.0f}% cons | SR {w_sr:.1f})",
            va='center', fontsize=8.2, fontweight='bold', color=RR_BLUE
        )

    plt.suptitle('Top 10 Bowlers Under Pressure: Phase-Normalized Evidence & Final Ordering', fontsize=12.5, fontweight='bold', color=RR_BLUE)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig5_top10_bowlers_evidence.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------------------
    # FIGURE 6: Resilience Exclusion Quadrant & Sampling Precision Curve
    # -------------------------------------------------------------------------
    print("[*] Generating Figure 6: Reliability & Rejection Diagnostics...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.2))

    # Left: Qualified (n=51) vs Excluded Pressure-Dip Zone (delta < 0)
    qual_rest = df_bat.iloc[10:]
    qual_top = df_bat.iloc[:10]
    neg_excl = excl_bat[excl_bat['bayes_clutch_delta'] < 0]

    ax1.axhspan(-14, 0, color='#FEE2E2', alpha=0.55, zorder=0)
    ax1.axhline(0, color=RR_RED, linestyle='--', lw=1.1, zorder=1)
    ax1.scatter(qual_rest['bayes_consistency_pct'], qual_rest['bayes_clutch_delta'], color=RR_SLATE, alpha=0.45, s=36, label='Qualified Cohort (#11–#51)')
    ax1.scatter(neg_excl['bayes_consistency_pct'], neg_excl['bayes_clutch_delta'], color=RR_RED, marker='X', s=65, zorder=3, label='Excluded: Dip Under Pressure (Δ < 0)')
    ax1.scatter(qual_top['bayes_consistency_pct'], qual_top['bayes_clutch_delta'], color=RR_PINK, edgecolor='white', lw=0.8, s=85, zorder=4, label='Final Top 10 Batters')

    label_targets_left = [
        ('Abhishek Sharma', qual_top, (14, -4)),
        ('Dewald Brevis', qual_top, (14, 0)),
        ('Dinesh Karthik', qual_top, (14, -4)),
        ('Suryakumar Yadav', qual_top, (14, 14)),
        ('Yashasvi Jaiswal', qual_top, (-82, 12)),
    ]
    for name, src, offset in label_targets_left:
        row = src[src['striker_name'] == name].iloc[0]
        ax1.annotate(
            name, (row['bayes_consistency_pct'], row['bayes_clutch_delta']),
            xytext=offset, textcoords='offset points', fontsize=7.4, fontweight='bold', color=RR_BLUE,
            arrowprops=dict(arrowstyle='-', color='#64748B', lw=0.65),
            bbox=dict(boxstyle='round,pad=0.14', facecolor='white', edgecolor='none', alpha=0.82)
        )

    excl_labels = [
        ('Vaibhav Sooryavanshi', (12, -2)),
        ('Phil Salt', (10, -10)),
    ]
    for name, offset in excl_labels:
        sub = neg_excl[neg_excl['striker_name'] == name]
        if not sub.empty:
            row = sub.iloc[0]
            ax1.annotate(
                f"{name} ({row['bayes_clutch_delta']:+.1f})",
                (row['bayes_consistency_pct'], row['bayes_clutch_delta']),
                xytext=offset, textcoords='offset points', fontsize=7.2, fontweight='bold', color='#991B1B',
                arrowprops=dict(arrowstyle='-', color='#991B1B', lw=0.65),
                bbox=dict(boxstyle='round,pad=0.14', facecolor='#FEF2F2', edgecolor='none', alpha=0.85)
            )

    ax1.text(77.3, -15.4, 'Resilience Rejection Zone (Clutch Δ < 0)', ha='right', fontsize=7.5, color='#991B1B', fontweight='bold')
    ax1.set_title('Resilience Gate: Positive Elevation vs. Match Consistency', fontweight='bold', color=RR_BLUE, pad=26)
    ax1.set_xlabel('Bayesian Match Consistency (% Positive HP Matches)')
    ax1.set_ylabel('Bayesian Clutch Δ (HP − Base RAE)')
    ax1.set_xlim(38, 78)
    ax1.set_ylim(-16.5, 35)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=3, fontsize=6.9, frameon=True)

    # Right: Standard Error Precision vs Match Volume (Top 10 Batters vs Top 10 Bowlers + Cohort)
    ax2.scatter(df_bat['hp_matches'], df_bat['uncertainty_se'], color=RR_PINK, alpha=0.25, s=30)
    ax2.scatter(df_bowl['hp_matches'], df_bowl['uncertainty_se'], color=RR_BLUE, alpha=0.25, s=30)
    t_bat10 = df_bat.head(10)
    t_bowl10 = df_bowl.head(10)
    ax2.scatter(t_bat10['hp_matches'], t_bat10['uncertainty_se'], color=RR_PINK, marker='^', s=75, edgecolor='white', lw=0.7, label='Top 10 Batters SE')
    ax2.scatter(t_bowl10['hp_matches'], t_bowl10['uncertainty_se'], color=RR_BLUE, marker='o', s=70, edgecolor='white', lw=0.7, label='Top 10 Bowlers SE')
    ax2.axvspan(20, 30, color='#FEF3C7', alpha=0.45, zorder=0)
    ax2.axhline(1.2, color=RR_SLATE, linestyle=':', lw=1.0, label='High-Precision Threshold (SE ≤ 1.20)')

    se_notes = [
        ('Prabhsimran Singh', 'Prabhsimran', t_bat10, 'striker_name', (10, 8), RR_PINK),
        ('Dewald Brevis', 'Brevis', t_bat10, 'striker_name', (10, -4), RR_PINK),
        ('Suryakumar Yadav', 'Suryakumar', t_bat10, 'striker_name', (-48, 14), RR_PINK),
        ('Jasprit Bumrah', 'Bumrah', t_bowl10, 'bowler_name', (-36, -18), RR_BLUE),
        ('Rashid Khan', 'Rashid Khan', t_bowl10, 'bowler_name', (-64, 12), RR_BLUE),
        ('Matheesha Pathirana', 'Pathirana', t_bowl10, 'bowler_name', (8, 12), RR_BLUE),
    ]
    for full_name, short_name, src, col, offset, clr in se_notes:
        row = src[src[col] == full_name].iloc[0]
        ax2.annotate(
            f"{short_name} (±{row['uncertainty_se']:.2f})",
            (row['hp_matches'], row['uncertainty_se']),
            xytext=offset, textcoords='offset points', fontsize=7.4, fontweight='bold', color=clr,
            arrowprops=dict(arrowstyle='-', color=clr, lw=0.65),
            bbox=dict(boxstyle='round,pad=0.14', facecolor='white', edgecolor='none', alpha=0.82)
        )

    ax2.text(20.6, 3.05, '20–30m\nBoundary', fontsize=7.2, color='#92400E', fontweight='bold')
    ax2.set_title('Estimation Uncertainty (SE = σ/√N) vs. Match Volume', fontweight='bold', color=RR_BLUE, pad=26)
    ax2.set_xlabel('Qualifying High-Pressure Matches ($N$)')
    ax2.set_ylabel('Run-Value Standard Error (± SE)')
    ax2.set_xlim(17, 92)
    ax2.set_ylim(0.5, 3.4)
    ax2.legend(loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=3, fontsize=6.7, frameon=True)

    plt.suptitle('Reliability Diagnostics: Resilience Filtering & Confidence Interval Tightening', fontsize=12, fontweight='bold', color=RR_BLUE)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig6_reliability_and_rejection_diagnostics.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[+] All 6 restructured publication figures generated in: {fig_dir}")


if __name__ == "__main__":
    generate_all_figures()
