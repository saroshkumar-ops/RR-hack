"""
Builds the Official Publication-Grade Methodology Report PDF for Unstop Submission
Using ReportLab with Rajasthan Royals branding (#EA1A80, #001D48) and embedded 300-DPI figures.
"""
import os
import sys
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Royals Brand Palette
RR_PINK = colors.HexColor("#EA1A80")
RR_BLUE = colors.HexColor("#001D48")
RR_LIGHT_BG = colors.HexColor("#F8F9FA")
RR_TEXT = colors.HexColor("#222222")
RR_GRAY = colors.HexColor("#555555")

def create_table_style(header_bg=RR_BLUE):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F9")]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ])

def build_pdf():
    fig_dir = os.path.join(REPO_ROOT, "reports/figures")
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    out_pdf = os.path.join(REPO_ROOT, "reports/SupeRR_Selector_S2_Methodology_Report.pdf")
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)

    df_bat = pd.read_csv(os.path.join(proc_dir, "ml_top10_batters_under_pressure.csv"))
    df_bowl = pd.read_csv(os.path.join(proc_dir, "ml_top10_bowlers_under_pressure.csv"))

    doc = SimpleDocTemplate(
        out_pdf,
        pagesize=A4,
        rightMargin=0.55*inch, leftMargin=0.55*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch,
        title="SupeRR Selector Season 2 - Methodology Report"
    )

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('TitleRR', parent=styles['Title'], fontSize=21, textColor=RR_PINK, spaceAfter=4, alignment=0, fontName='Helvetica-Bold')
    style_subtitle = ParagraphStyle('SubRR', parent=styles['Normal'], fontSize=10.5, textColor=RR_BLUE, spaceAfter=10, fontName='Helvetica-Bold')
    style_h1 = ParagraphStyle('H1RR', parent=styles['Heading1'], fontSize=13.5, textColor=RR_BLUE, spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')
    style_h2 = ParagraphStyle('H2RR', parent=styles['Heading2'], fontSize=10.8, textColor=RR_PINK, spaceBefore=6, spaceAfter=4, fontName='Helvetica-Bold')
    style_body = ParagraphStyle('BodyRR', parent=styles['Normal'], fontSize=9.2, leading=12.8, textColor=RR_TEXT, spaceAfter=5)
    style_bullet = ParagraphStyle('BulletRR', parent=style_body, leftIndent=14, spaceAfter=3.5)
    style_caption = ParagraphStyle('CapRR', parent=styles['Normal'], fontSize=8.3, textColor=RR_GRAY, alignment=1, spaceAfter=6, fontName='Helvetica-Oblique')
    style_box = ParagraphStyle('BoxRR', parent=style_body, backColor=RR_LIGHT_BG, borderColor=RR_PINK, borderWidth=1, borderPadding=7, spaceBefore=9, spaceAfter=9)

    story = []

    # =========================================================================
    # HEADER & EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("RAJASTHAN ROYALS | SupeRR SELECTOR SEASON 2", style_subtitle))
    story.append(Paragraph("Quantifying Clutch Reliability: A Machine Learning & Empirical Bayes Approach", style_title))
    story.append(HRFlowable(width="100%", thickness=2, color=RR_PINK, spaceBefore=4, spaceAfter=12))

    summary_text = (
        "<b>Executive Summary:</b> Using delivery-level data across <b>200,999 balls and 867 T20/T20I matches (2022–2026)</b>, "
        "we built a reproducible three-stage machine learning framework to objectively identify the players who deliver most "
        "consistently under high-pressure match situations:<br/>"
        "• <b>Stage 1 (Pressure Definition):</b> Trained a supervised Gradient-Boosted Win Probability Classifier (<b>AUC = 0.9212</b>) "
        "to calculate the counterfactual <b>Leverage Index (LI)</b> of every ball, isolating the highest-stakes 34.88% of deliveries (70,111 balls with LI ≥ 6.5).<br/>"
        "• <b>Stage 2 (Fair Normalization):</b> Eliminated format bias (IPL T20 vs. T20I) and phase mismatch via Runs Above Expected (RAE) and Runs Saved Above Expected (RSAE).<br/>"
        "• <b>Stage 3 (Bayesian Reliability &amp; Clustering):</b> Enforced symmetrical multi-season eligibility + positive-resilience gates, stabilized variance via "
        "Empirical Bayes shrinkage, incorporated match-to-match consistency, and clustered roles using K-Means (k=3)."
    )
    story.append(Paragraph(summary_text, style_box))

    # =========================================================================
    # SECTION 1: PRESSURE DEFINITION
    # =========================================================================
    story.append(Paragraph("1. Defining 'Pressure' from First Principles via ML Leverage", style_h1))
    story.append(Paragraph(
        "Traditional cricket heuristics fail to capture true match pressure. Defining pressure simply as 'overs 16–20' misclassifies "
        "dead-rubber games (where a chasing team needs 70 runs off 6 balls) as high pressure, while ignoring catastrophic collapses in the powerplay. "
        "Similarly, Required Run Rate (RRR) alone ignores wickets in hand.", style_body))
    story.append(Paragraph(
        "We adopt a first-principles definition rooted in win expectancy: <b>A delivery carries high pressure if and only if its outcome causes a "
        "significant swing in match win probability.</b> We trained a <i>HistGradientBoostingClassifier</i> on 2nd-innings chase states "
        "<i>S_t = [Innings, Runs Needed, Balls Remaining, Wickets in Hand, RRR, CRR, Overs Elapsed]</i> (<b>Log-Loss = 0.3501</b>).", style_body))
    story.append(Paragraph(
        "<b>Counterfactual Leverage Index (LI):</b> For every 2nd-innings chase ball, the model recomputes dynamic <i>RRR</i>, <i>CRR</i>, and elapsed overs under two "
        "counterfactual outcomes—a Six vs. a Wicket—and scales the win-probability swing: "
        "<b>LI_t = clip(|P(Win | Six) - P(Win | Wicket)| × 38.0, 0.5, 10.0)</b>. For 1st-innings target setting, pressure captures early collapses "
        "(≥ 3 wickets lost inside overs 1–10) and death acceleration (overs 16–20); Super Overs receive LI = 10.0. Across 200,999 balls, "
        "<b>LI ≥ 6.5</b> isolates balanced high-leverage samples in both innings: <b>33.62%</b> (35,544/105,727) in Innings 1 and <b>36.26%</b> (34,529/95,234) in Innings 2.", style_body))

    fig1_path = os.path.join(fig_dir, "fig1_rr_case_study_leverage.png")
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=6.5*inch, height=3.45*inch))
        story.append(Paragraph("Figure 1: Validation on Rajasthan Royals vs. LSG (Match 14113, target 166). ML Leverage spikes to 10.0 during both Over 1 early collapses and Kuldeep Sen's final-over defense.", style_caption))

    # =========================================================================
    # SECTION 2: FAIR COMPARISONS & ENVIRONMENT NORMALIZATION
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. Fair Comparisons: Format Bias, Phase Mismatch &amp; Eligibility", style_h1))
    story.append(Paragraph(
        "Comparing raw strike rates or economies directly across IPL and T20I competitions introduces severe statistical bias. "
        "Our exploratory audit of the supplied data pack uncovered two critical environmental discrepancies:", style_body))
    story.append(Paragraph(
        "• <b>Competition-Format Discrepancy:</b> Franchise T20 averages an implied batting Strike Rate of <b>139.46</b> (Economy <b>8.37</b>), "
        "whereas International T20Is average <b>129.34</b> (Economy <b>7.76</b>). Death-over par reaches <b>166.39 SR / 9.98 Econ</b> in T20 vs. "
        "<b>152.72 SR / 9.16 Econ</b> in T20I—making raw economy comparisons unfair without format conditioning.", style_bullet))
    story.append(Paragraph(
        "• <b>The Phase-Mismatch Trap ('The Bumrah Paradox'):</b> Elite death specialists like Jasprit Bumrah maintain a 7.01 economy in low-leverage "
        "overs and are held back specifically for high-pressure Death Overs (par ~9.98 T20 / 9.16 T20I). Comparing his 7.38 HP economy against "
        "his 7.01 baseline produces a negative raw delta (-0.37), falsely penalizing him for bowling cricket's toughest overs.", style_bullet))
    story.append(Paragraph(
        "<b>Mathematical Solution (RAE &amp; RSAE):</b> We compute <b>Runs Above Expected (RAE)</b> for batters and <b>Runs Saved Above Expected (RSAE)</b> "
        "for bowlers relative to the exact empirical par for each <b>(Match Format × Innings Phase)</b> cell. Normalized properly, Bumrah's 7.38 HP economy "
        "yields <b>+1.76 Runs Saved per Over above phase par</b>.", style_body))

    fig2_path = os.path.join(fig_dir, "fig2_format_context_bias.png")
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=5.6*inch, height=2.2*inch))
        story.append(Paragraph("Figure 2: Empirical scoring par across T20 (IPL) vs. T20I and Innings Phases, proving why format-phase normalization is essential.", style_caption))

    # =========================================================================
    # SECTION 3: PERFORMANCE MEASUREMENT, EMPIRICAL BAYES & CLUSTERING
    # =========================================================================
    story.append(Paragraph("3. Performance Measurement, Baselines &amp; Empirical Bayes Shrinkage", style_h1))
    story.append(Paragraph(
        "To eliminate small-sample flukes and distinguish genuine clutch risers from players who dip under pressure, we enforce symmetrical eligibility + resilience rules: "
        "<b>≥ 200 HP balls, ≥ 20 HP matches, and non-negative Bayesian Clutch Delta (≥ 0)</b> for batters (n=51 qualified); "
        "<b>≥ 35.0 HP overs, ≥ 20 HP matches, and non-negative Clutch Delta</b> for bowlers (n=67 qualified). Empirical Bayes Shrinkage pulls noisy estimates toward prior μ_0:", style_body))
    story.append(Paragraph(
        "<b>θ_hat_i = [ n_i / (n_i + v_0) ] × x_bar_i + [ v_0 / (n_i + v_0) ] × μ_0</b> "
        "<i>(prior weight v_0 = 80 balls for batters, 150 balls for bowlers, and 10 matches for consistency).</i>", style_box))

    story.append(Paragraph(
        "<b>Composite Scores (0–100) &amp; K-Means Archetypes:</b> Batting Score weights 40% Bayes RAE/100 + 25% Bayes Clutch Δ (HP minus baseline RAE) + "
        "20% Match Consistency + 15% Boundary Execution &amp; Survival. Bowling Score weights 35% Bayes RSAE/Over + 25% Wicket Hazard + "
        "20% Match Consistency + 20% Clutch Δ &amp; Dot Pressure. K-Means (k=3) groups players without manual rules into roles like "
        "<i>Elite Pressure Accelerator</i>, <i>High-Leverage Finisher</i>, and <i>Run-Choking Squeeze Specialist</i>.", style_body))

    fig5_path = os.path.join(fig_dir, "fig5_bayesian_shrinkage_funnel.png")
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=5.6*inch, height=2.15*inch))
        story.append(Paragraph("Figure 3: Empirical Bayes Shrinkage funnel showing how smaller HP samples shrink more conservatively toward the prior.", style_caption))

    # =========================================================================
    # SECTION 4: EVIDENCE FOR TOP 10 RANKINGS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Ordered Top 10 Rankings &amp; Empirical Evidence", style_h1))
    story.append(Paragraph("4.1 Top 10 Batters Under Pressure", style_h2))

    bat_headers = ["Rank", "Player Name", "HP M", "HP Balls", "Raw SR", "Bayes RAE", "Clutch Δ", "Cons %", "Score"]
    bat_rows = [bat_headers]
    for _, r in df_bat.iterrows():
        bat_rows.append([
            int(r['rank']), r['striker_name'], int(r['hp_matches']), int(r['hp_balls']),
            f"{r['raw_hp_sr']:.1f}", f"{r['bayes_hp_rae']:+.2f}", f"{r['bayes_clutch_delta']:+.2f}",
            f"{r['bayes_consistency_pct']:.1f}%", f"{r['batting_clutch_score']:.2f}"
        ])
    t_bat = Table(bat_rows, colWidths=[0.4*inch, 1.35*inch, 0.45*inch, 0.65*inch, 0.6*inch, 0.75*inch, 0.7*inch, 0.6*inch, 0.6*inch])
    t_bat.setStyle(create_table_style(RR_PINK))
    story.append(t_bat)
    story.append(Spacer(1, 8))

    fig3_path = os.path.join(fig_dir, "fig3_top10_batters_evidence.png")
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=6.7*inch, height=2.9*inch))
        story.append(Paragraph("Figure 4: Top 10 Batters — Shift from Normal Baseline to High-Pressure scoring alongside final Clutch Scores.", style_caption))

    story.append(Paragraph(
        "<b>Key Insights (Batters):</b> <b>Abhishek Sharma (#1)</b> leads with +37.30 Bayes RAE per 100 pressure balls "
        "at a raw 183.5 SR across 43 matches (64.5% consistency). <b>Dewald Brevis (#2, +27.39 Δ)</b> and <b>Dinesh Karthik (#7, +29.81 Δ)</b> "
        "deliver the sharpest positive pressure elevations, while <b>Yashasvi Jaiswal (#3, 67.2% cons.)</b> and high-volume anchor "
        "<b>Suryakumar Yadav (#4, 62 HP matches, 838 balls, 66.9% cons.)</b> pair explosive scoring with elite repeatability.", style_body))

    # Bowlers Table & Chart
    story.append(PageBreak())
    story.append(Paragraph("4.2 Top 10 Bowlers Under Pressure", style_h2))

    bowl_headers = ["Rank", "Player Name", "HP M", "Overs", "Wkts", "Raw Econ", "Bayes RSAE", "Bayes SR", "Cons %", "Score"]
    bowl_rows = [bowl_headers]
    for _, r in df_bowl.iterrows():
        bowl_rows.append([
            int(r['rank']), r['bowler_name'], int(r['hp_matches']), f"{r['hp_overs']:.1f}", int(r['hp_wickets']),
            f"{r['raw_hp_econ']:.2f}", f"{r['bayes_hp_rsae']:+.2f}", f"{r['bayes_hp_sr']:.1f}",
            f"{r['bayes_consistency_pct']:.1f}%", f"{r['bowling_clutch_score']:.2f}"
        ])
    t_bowl = Table(bowl_rows, colWidths=[0.4*inch, 1.35*inch, 0.45*inch, 0.5*inch, 0.45*inch, 0.65*inch, 0.75*inch, 0.65*inch, 0.6*inch, 0.55*inch])
    t_bowl.setStyle(create_table_style(RR_BLUE))
    story.append(t_bowl)
    story.append(Spacer(1, 8))

    fig4_path = os.path.join(fig_dir, "fig4_top10_bowlers_evidence.png")
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=6.7*inch, height=2.9*inch))
        story.append(Paragraph("Figure 5: Top 10 Bowlers — Phase-Normalized Runs Saved Above Expected per over and Clutch Consistency.", style_caption))

    story.append(Paragraph(
        "<b>Key Insights (Bowlers):</b> <b>Matheesha Pathirana (#1)</b> claims top rank by fusing 11.20 balls/wicket striking across 49 pressure scalps "
        "with 83.3% match consistency. <b>Sunil Narine (#2)</b> posts the highest phase-adjusted run suppression (+1.92 RSAE/over, 6.53 Econ), "
        "while <b>Jasprit Bumrah (#3, 84.2% cons., 66m)</b> and <b>Rashid Khan (#7, 85m, 151.2 ov)</b> sustain elite execution at massive volume. "
        "<b>T Natarajan (#10)</b> adds the steepest positive clutch elevation (+1.39 RSAE Δ) across 41 HP matches.", style_body))

    # =========================================================================
    # SECTION 5: RELIABILITY, LIMITATIONS & REPRODUCIBILITY
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Reliability Checks, Uncertainty Bounds &amp; Limitations", style_h1))
    story.append(Paragraph(
        "<b>Consistency &amp; Confidence Intervals (SE = σ / √N):</b> Evaluating averages without match-level variance hides streakiness. "
        "We computed per-match RAE/RSAE standard deviations across all qualifying HP matches to quantify estimation uncertainty:", style_body))

    style_tbl_hdr = ParagraphStyle('TblHdr', parent=styles['Normal'], fontSize=8.2, leading=10.5, textColor=colors.white, fontName='Helvetica-Bold')
    style_tbl_cell = ParagraphStyle('TblCell', parent=styles['Normal'], fontSize=7.8, leading=10.5, textColor=RR_TEXT, fontName='Helvetica')

    se_raw = [
        ["Cohort / Check", "Top Anchor (Tightest CI)", "Boundary / Higher-Variance", "Key Diagnostic Finding"],
        ["Top 10 Batters\n(≥20m, ≥200b, Δ≥0)", "Suryakumar Yadav\n62 matches | SE ±0.99", "Prabhsimran Singh\n21 matches | SE ±2.11", "Eliminates high-SR dips (e.g., -10.20 clutch Δ when normal baseline exceeds pressure output)."],
        ["Top 10 Bowlers\n(≥20m, ≥35ov, Δ≥0)", "Rashid Khan\n85 matches | SE ±0.71", "Matheesha Pathirana\n38 matches | SE ±1.20", "All Top 10 bowlers have ≥32 HP matches and SE ≤ ±1.20; Jasprit Bumrah holds 84.16% cons."],
        ["Consistency Peak\n(67 Qual. Bowlers)", "Nathan Ellis\n36 matches | 84.70% cons.", "Jasprit Bumrah\n66 matches | 84.16% cons.", "Empirical Bayes damps short 20-match streaks while preserving sustained 60+ match consistency."]
    ]
    se_rows = []
    for r_idx, row in enumerate(se_raw):
        st = style_tbl_hdr if r_idx == 0 else style_tbl_cell
        se_rows.append([Paragraph(cell.replace("\n", "<br/>"), st) for cell in row])
    t_se = Table(se_rows, colWidths=[1.35*inch, 1.5*inch, 1.5*inch, 2.6*inch])
    t_se.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), RR_BLUE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F9")]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_se)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Model Limitations &amp; Analytical Safeguards:", style_h2))
    story.append(Paragraph(
        "• <b>1st vs. 2nd Innings Structural Asymmetry:</b> Win probability paths are directly observable only during 2nd-innings chases, whereas 1st-innings "
        "leverage blends early collapse and death-over heuristics. Calibrating the counterfactual multiplier (× 38.0) balances HP selection rates smoothly across "
        "both innings (33.62% Innings 1 vs. 36.26% Innings 2), preventing either innings from dominating player rankings.", style_bullet))
    story.append(Paragraph(
        "• <b>Unrecorded Venue &amp; Dew Telemetry:</b> The supplied ball-by-ball tables omit evening dew factors, exact square boundary dimensions, and dropped catches, "
        "which add residual noise to single-match bowling economies. Conditioning par by (Format × Phase) and averaging over ≥ 20 matches mitigates venue outliers.", style_bullet))
    story.append(Paragraph(
        "• <b>Opposition Quality Heterogeneity in T20Is:</b> Bilateral T20Is include associate-nation fixtures where strike rates can spike. Enforcing a non-negative "
        "Clutch Delta filter alongside ≥ 200 HP balls and Empirical Bayes shrinkage prevents short bilateral streaks from displacing proven multi-season performers.", style_bullet))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Full Reproducibility &amp; Codebase:</b> The entire end-to-end codebase—including EDA audits, HistGradientBoosting training, dynamic counterfactual leverage, "
        "Empirical Bayes modules, K-Means clustering, and an interactive Streamlit explorer—is open-sourced at: "
        "<b>https://github.com/saroshkumar-ops/RR-hack</b>.", style_box))

    doc.build(story)
    print(f"[+] Successfully compiled Methodology Report PDF: {out_pdf}")

if __name__ == "__main__":
    build_pdf()
