"""
Builds the Restructured, Publication-Grade 6-Page Methodology Report PDF for Unstop Submission.
Follows the exact Round 1 Problem Statement rubric order with custom Rajasthan Royals
Navy/Pink/Gold branding, page templates, KPI strips, structured comparison cards,
proper HTML subscripts, and 6 300-DPI diagnostic figures read dynamically from data/processed/.
"""
import os
import json
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, NextPageTemplate,
    Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Royals Brand Palette
RR_PINK = colors.HexColor("#EA1A80")
RR_PINK_PALE = colors.HexColor("#FDF2F8")
RR_BLUE = colors.HexColor("#001D48")
RR_BLUE_MID = colors.HexColor("#0F2D5C")
RR_GOLD = colors.HexColor("#FDB913")
RR_CYAN = colors.HexColor("#0075FF")
RR_LIGHT_BG = colors.HexColor("#F8FAFC")
RR_CARD_BG = colors.HexColor("#F4F6FA")
RR_TEXT = colors.HexColor("#1E293B")
RR_GRAY = colors.HexColor("#475569")
RR_BORDER = colors.HexColor("#CBD5E1")
RR_RED_BG = colors.HexColor("#FEF2F2")
RR_RED_TEXT = colors.HexColor("#991B1B")


class NumberedCanvas(canvas.Canvas):
    """Draws exact 'Page X of Y' footers without overlapping content frames."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        page_w, _ = A4
        self.saveState()
        margin_x = 0.52 * inch
        y_line = 0.42 * inch
        self.setStrokeColor(RR_BORDER)
        self.setLineWidth(0.6)
        self.line(margin_x, y_line, page_w - margin_x, y_line)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(RR_GRAY)
        self.drawString(
            margin_x, 0.27 * inch,
            "Rajasthan Royals • SupeRR Selector Season 2 • Reproducible Pipeline: github.com/saroshkumar-ops/RR-hack"
        )
        self.setFont("Helvetica-Bold", 7.8)
        self.setFillColor(RR_BLUE)
        self.drawRightString(page_w - margin_x, 0.27 * inch, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def draw_first_page_chrome(c, doc):
    """Draws the full-bleed Rajasthan Royals Navy/Pink/Gold Cover Masthead on Page 1."""
    page_w, page_h = A4
    banner_h = 1.24 * inch
    c.saveState()

    # Navy Masthead Background
    c.setFillColor(RR_BLUE)
    c.rect(0, page_h - banner_h, page_w, banner_h, stroke=0, fill=1)

    # Signature Pink Bottom Stripe & Top Thin Gold Trim
    c.setFillColor(RR_PINK)
    c.rect(0, page_h - banner_h, page_w, 3.5, stroke=0, fill=1)
    c.setFillColor(RR_GOLD)
    c.rect(0, page_h - 3, page_w, 3, stroke=0, fill=1)

    margin_x = 0.52 * inch
    # Gold Kicker Tag
    c.setFillColor(RR_GOLD)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(margin_x, page_h - 0.30 * inch, "RAJASTHAN ROYALS  |  SupeRR SELECTOR SEASON 2  •  ROUND 1 METHODOLOGY DOSSIER")

    # Right-aligned Telemetry Stamp
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("Helvetica", 8.0)
    c.drawRightString(page_w - margin_x, page_h - 0.30 * inch, "IPL & T20I Corpus (2022–2026)")

    # Main Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 19.5)
    c.drawString(margin_x, page_h - 0.65 * inch, "Quantifying Clutch Reliability Under Pressure")

    # Subtitle
    c.setFillColor(colors.HexColor("#F8BBD0"))
    c.setFont("Helvetica", 9.8)
    c.drawString(
        margin_x, page_h - 0.92 * inch,
        "A Three-Stage Machine Learning, Context-Par & Empirical Bayes Framework for Identifying T20 Match-Winners"
    )
    c.restoreState()


def draw_later_page_chrome(c, doc):
    """Draws clean running top header bar on Pages 2–6."""
    page_w, page_h = A4
    margin_x = 0.52 * inch
    c.saveState()
    c.setFillColor(RR_BLUE)
    c.setFont("Helvetica-Bold", 7.8)
    c.drawString(margin_x, page_h - 0.34 * inch, "RAJASTHAN ROYALS  |  SupeRR SELECTOR SEASON 2")
    c.setFillColor(RR_PINK)
    c.setFont("Helvetica-Bold", 7.8)
    c.drawRightString(page_w - margin_x, page_h - 0.34 * inch, "Quantifying Clutch Reliability Under Pressure")
    c.setStrokeColor(RR_PINK)
    c.setLineWidth(1.0)
    c.line(margin_x, page_h - 0.42 * inch, page_w - margin_x, page_h - 0.42 * inch)
    c.restoreState()


def make_section_banner(num_str: str, title_str: str, content_w: float) -> Table:
    """Creates a bold numbered section pill header spanning content width."""
    st_num = ParagraphStyle(f'SecNum{num_str}', fontSize=9.5, leading=11, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
    st_tit = ParagraphStyle(f'SecTit{num_str}', fontSize=12.2, leading=14, textColor=RR_BLUE, fontName='Helvetica-Bold')
    tbl = Table(
        [[Paragraph(num_str, st_num), Paragraph(title_str, st_tit)]],
        colWidths=[0.36 * inch, content_w - 0.36 * inch]
    )
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_PINK),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#F1F5F9")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 4),
        ('RIGHTPADDING', (0, 0), (0, 0), 4),
        ('LEFTPADDING', (1, 0), (1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 1.2, RR_BLUE),
    ]))
    return tbl


def make_ranking_table(df_top: pd.DataFrame, is_batter: bool, content_w: float) -> Table:
    """Builds the ordered Top 10 ranking table including Archetype badge & Standard Error."""
    short_arch = {
        "Elite Pressure Accelerator": "Accelerator",
        "High-Leverage Finisher": "Finisher",
        "Ice-Cold Chase Anchor": "Chase Anchor",
        "Run-Choking Squeeze Specialist": "Squeeze Spec.",
        "Clutch Wicket Hunter": "Wkt Hunter",
        "Balanced Pressure Enforcer": "Enforcer",
    }

    st_hdr = ParagraphStyle('RkHdr', fontSize=7.8, leading=9.5, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
    st_hdr_l = ParagraphStyle('RkHdrL', parent=st_hdr, alignment=0)
    st_cell = ParagraphStyle('RkCell', fontSize=7.8, leading=9.5, textColor=RR_TEXT, fontName='Helvetica', alignment=1)
    st_cell_b = ParagraphStyle('RkCellB', parent=st_cell, fontName='Helvetica-Bold', textColor=RR_BLUE)
    st_name = ParagraphStyle('RkName', fontSize=8.0, leading=9.5, textColor=RR_BLUE, fontName='Helvetica-Bold', alignment=0)
    st_arch = ParagraphStyle('RkArch', fontSize=7.2, leading=9.2, textColor=RR_GRAY, fontName='Helvetica-Oblique', alignment=1)

    if is_batter:
        headers = ["Rank", "Player Name", "K-Means Role", "HP M", "Balls", "Raw SR", "Bayes RAE", "Clutch Δ", "Cons %", "± SE", "Score"]
        col_w = [0.38*inch, 1.32*inch, 0.78*inch, 0.42*inch, 0.46*inch, 0.56*inch, 0.70*inch, 0.62*inch, 0.54*inch, 0.48*inch, 0.54*inch]
        rows = [[Paragraph(h, st_hdr_l if i in (1, 2) else st_hdr) for i, h in enumerate(headers)]]
        for _, r in df_top.iterrows():
            rows.append([
                Paragraph(str(int(r['rank'])), st_cell_b),
                Paragraph(r['striker_name'], st_name),
                Paragraph(short_arch.get(r['ml_archetype'], r['ml_archetype']), st_arch),
                Paragraph(str(int(r['hp_matches'])), st_cell),
                Paragraph(str(int(r['hp_balls'])), st_cell),
                Paragraph(f"{r['raw_hp_sr']:.1f}", st_cell),
                Paragraph(f"{r['bayes_hp_rae']:+.2f}", st_cell_b),
                Paragraph(f"{r['bayes_clutch_delta']:+.2f}", st_cell),
                Paragraph(f"{r['bayes_consistency_pct']:.1f}%", st_cell),
                Paragraph(f"±{r['uncertainty_se']:.2f}", st_cell),
                Paragraph(f"{r['batting_clutch_score']:.2f}", st_cell_b),
            ])
        hdr_color = RR_PINK
    else:
        headers = ["Rank", "Player Name", "K-Means Role", "HP M", "Overs", "Wkts", "Raw Econ", "Bayes RSAE", "Bayes SR", "Cons %", "± SE", "Score"]
        col_w = [0.36*inch, 1.24*inch, 0.78*inch, 0.38*inch, 0.46*inch, 0.38*inch, 0.56*inch, 0.68*inch, 0.56*inch, 0.52*inch, 0.46*inch, 0.46*inch]
        rows = [[Paragraph(h, st_hdr_l if i in (1, 2) else st_hdr) for i, h in enumerate(headers)]]
        for _, r in df_top.iterrows():
            rows.append([
                Paragraph(str(int(r['rank'])), st_cell_b),
                Paragraph(r['bowler_name'], st_name),
                Paragraph(short_arch.get(r['ml_archetype'], r['ml_archetype']), st_arch),
                Paragraph(str(int(r['hp_matches'])), st_cell),
                Paragraph(f"{r['hp_overs']:.1f}", st_cell),
                Paragraph(str(int(r['hp_wickets'])), st_cell),
                Paragraph(f"{r['raw_hp_econ']:.2f}", st_cell),
                Paragraph(f"{r['bayes_hp_rsae']:+.2f}", st_cell_b),
                Paragraph(f"{r['bayes_hp_sr']:.1f}", st_cell),
                Paragraph(f"{r['bayes_consistency_pct']:.1f}%", st_cell),
                Paragraph(f"±{r['uncertainty_se']:.2f}", st_cell),
                Paragraph(f"{r['bowling_clutch_score']:.2f}", st_cell_b),
            ])
        hdr_color = RR_BLUE

    # Scale col_w smoothly to exact content_w
    scale = content_w / sum(col_w)
    col_w = [w * scale for w in col_w]

    tbl = Table(rows, colWidths=col_w)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), hdr_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 4), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0, 1), (-1, 3), RR_PINK_PALE if is_batter else colors.HexColor("#EFF6FF")),
        ('GRID', (0, 0), (-1, -1), 0.4, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, 0), 5.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5.5),
        ('TOPPADDING', (0, 1), (-1, -1), 4.0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


def build_pdf():
    fig_dir = os.path.join(REPO_ROOT, "reports/figures")
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    out_pdf = os.path.join(REPO_ROOT, "reports/SupeRR_Selector_S2_Methodology_Report.pdf")
    os.makedirs(os.path.dirname(out_pdf), exist_ok=True)

    with open(os.path.join(proc_dir, "ml_report_diagnostics.json"), "r", encoding="utf-8") as f:
        diag = json.load(f)
    df_bat_top = pd.read_csv(os.path.join(proc_dir, "ml_top10_batters_under_pressure.csv"))
    df_bowl_top = pd.read_csv(os.path.join(proc_dir, "ml_top10_bowlers_under_pressure.csv"))
    df_bat_full = pd.read_csv(os.path.join(proc_dir, "ml_full_batters_under_pressure.csv"))
    df_bowl_full = pd.read_csv(os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv"))
    df_excl_bat = pd.read_csv(os.path.join(proc_dir, "ml_excluded_batters.csv"))
    df_excl_bowl = pd.read_csv(os.path.join(proc_dir, "ml_excluded_bowlers.csv"))
    df_par = pd.read_csv(os.path.join(proc_dir, "ml_format_phase_par.csv"))

    page_w, page_h = A4
    margin_x = 0.52 * inch
    content_w = page_w - 2 * margin_x

    doc = BaseDocTemplate(
        out_pdf, pagesize=A4,
        title="SupeRR Selector Season 2 - Methodology Report",
        author="Rajasthan Royals Hackathon Analytics Team"
    )
    frame_first = Frame(margin_x, 0.54 * inch, content_w, page_h - 1.38 * inch - 0.54 * inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_later = Frame(margin_x, 0.54 * inch, content_w, page_h - 0.58 * inch - 0.54 * inch, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id='FirstPage', frames=[frame_first], onPage=draw_first_page_chrome),
        PageTemplate(id='LaterPages', frames=[frame_later], onPage=draw_later_page_chrome),
    ])

    styles = getSampleStyleSheet()
    st_body = ParagraphStyle('BodyRR', parent=styles['Normal'], fontSize=8.9, leading=12.4, textColor=RR_TEXT, spaceAfter=4.5)
    st_bullet = ParagraphStyle('BulletRR', parent=st_body, leftIndent=12, spaceAfter=3.5)
    st_cap = ParagraphStyle('CapRR', parent=styles['Normal'], fontSize=8.0, leading=10.5, textColor=RR_GRAY, alignment=1, spaceAfter=5, fontName='Helvetica-Oblique')
    st_h2 = ParagraphStyle('H2RR', parent=styles['Normal'], fontSize=10.2, leading=13, textColor=RR_PINK, spaceBefore=5, spaceAfter=3, fontName='Helvetica-Bold')
    st_card_hdr = ParagraphStyle('CardHdr', fontSize=8.8, leading=11, textColor=RR_BLUE, fontName='Helvetica-Bold', spaceAfter=2.5)
    st_card_body = ParagraphStyle('CardBody', fontSize=8.2, leading=11.4, textColor=RR_TEXT)
    st_formula = ParagraphStyle('FormulaBox', fontSize=9.0, leading=13.0, textColor=RR_BLUE, alignment=1)

    story = []

    # =========================================================================
    # PAGE 1: KPI STRIP, PIPELINE ARCHITECTURE & 01. PRESSURE DEFINITION
    # =========================================================================
    st_kpi_val = ParagraphStyle('KpiVal', fontSize=14.5, leading=17, textColor=RR_PINK, fontName='Helvetica-Bold', alignment=1)
    st_kpi_lbl = ParagraphStyle('KpiLbl', fontSize=7.4, leading=9.5, textColor=RR_GRAY, fontName='Helvetica-Bold', alignment=1)
    kpi_items = [
        (f"{diag['total_balls']:,}", f"DELIVERIES AUDITED\n({diag['unique_matches_bbb']} Matches)"),
        (f"{diag['train_auc']:.4f}", f"WIN-PROB MODEL AUC\n(Log-Loss {diag['train_loss']:.4f})"),
        (f"{diag['hp_pct_total']:.2f}%", f"HIGH-LEVERAGE SHARE\n(I1 {diag['inn1_hp_pct']:.1f}% | I2 {diag['inn2_hp_pct']:.1f}%)"),
        (f"{diag['qualified_batters_count']} / {diag['qualified_bowlers_count']}", "QUALIFIED COHORT\n(Batters / Bowlers ≥20m)"),
    ]
    kpi_row = [[Paragraph(f"<b>{v}</b><br/><font size='7.2' color='#475569'>{l.replace(chr(10), '<br/>')}</font>", st_kpi_val) for v, l in kpi_items]]
    t_kpi = Table(kpi_row, colWidths=[content_w / 4.0] * 4)
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RR_CARD_BG),
        ('LINEABOVE', (0, 0), (-1, 0), 2.0, RR_PINK),
        ('BOX', (0, 0), (0, 0), 0.5, RR_BORDER),
        ('BOX', (1, 0), (1, 0), 0.5, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.5, RR_BORDER),
        ('BOX', (3, 0), (3, 0), 0.5, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 7))

    # 3-Stage Architecture Strip
    st_pipe = ParagraphStyle('PipeTxt', fontSize=7.9, leading=10.5, textColor=colors.white, alignment=0)
    pipe_cells = [
        Paragraph("<b>STAGE 1 • PRESSURE DEFINITION</b><br/><font size='7.4'><i>HistGradientBoosting</i> Win-Prob Classifier computes ball-level counterfactual Leverage Index (<i>LI</i><sub>t</sub> ≥ 6.5).</font>", st_pipe),
        Paragraph("<b>STAGE 2 • FAIR CONTEXT PAR</b><br/><font size='7.4'>Normalizes runs &amp; economy against (<i>Format × Phase</i>) empirical par via RAE &amp; RSAE.</font>", st_pipe),
        Paragraph("<b>STAGE 3 • BAYES &amp; RELIABILITY</b><br/><font size='7.4'>≥20m eligibility + positive delta gate, Empirical Bayes shrinkage, match consistency &amp; K-Means.</font>", st_pipe),
    ]
    t_pipe = Table([pipe_cells], colWidths=[content_w / 3.0] * 3)
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_BLUE),
        ('BACKGROUND', (1, 0), (1, 0), RR_BLUE_MID),
        ('BACKGROUND', (2, 0), (2, 0), RR_PINK),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_pipe)
    story.append(Spacer(1, 8))

    story.append(make_section_banner("01", "Pressure Definition: First-Principles Win Expectancy Leverage", content_w))
    story.append(Spacer(1, 5))

    story.append(Paragraph(
        "Heuristic definitions—such as calling overs 16–20 'pressure' or filtering by raw Required Run Rate (RRR)—routinely misclassify dead-rubber chases "
        "(e.g., needing 70 off 6 balls where win probability is near zero) as high pressure while overlooking early powerplay collapses. "
        "Instead, we define pressure from win expectancy: <b>a delivery is high-pressure if and only if its outcome drives a steep swing in win probability.</b>",
        st_body
    ))
    story.append(Paragraph(
        "We trained a supervised <i>HistGradientBoostingClassifier</i> on 2nd-innings chase state vectors "
        "<i>S</i><sub>t</sub> = [Innings, Runs Needed, Balls Remaining, Wickets in Hand, RRR, CRR, Overs Elapsed] "
        f"(<b>AUC = {diag['train_auc']:.4f}</b>, <b>Log-Loss = {diag['train_loss']:.4f}</b>). For every chase delivery, we simulate counterfactual "
        "next states under a <b>Six</b> vs. a <b>Wicket</b>—dynamically updating <i>RRR</i>, <i>CRR</i>, and elapsed overs—to compute the "
        "<b>Leverage Index (<i>LI</i><sub>t</sub>) = clip(|<i>P</i>(Win | Six) − <i>P</i>(Win | Wicket)| × 38.0, 0.5, 10.0)</b>. "
        "First-innings leverage combines top-order collapse pressure (≥3 wickets in overs 1–10) and death acceleration (overs 16–20); Super Overs receive <i>LI</i> = 10.0. "
        f"Setting cutoff <b><i>LI</i> ≥ 6.5</b> isolates <b>{diag['hp_balls_total']:,}</b> decisive deliveries ({diag['hp_pct_total']:.2f}%): "
        f"<b>{diag['inn1_hp_pct']:.2f}%</b> in Innings 1 and <b>{diag['inn2_hp_pct']:.2f}%</b> in Innings 2.",
        st_body
    ))

    fig1_path = os.path.join(fig_dir, "fig1_pressure_definition_validation.png")
    story.append(Image(fig1_path, width=7.15 * inch, height=2.65 * inch))
    story.append(Paragraph(
        "Figure 1: Left — Match 14113 (RR vs. LSG, target 166) showing LI peaking at 10.0 during Over 20 defense; Right — Empirical proof across 200,999 balls that LI ≥ 6.5 isolates +21.8% higher wicket hazard than ordinary overs.",
        st_cap
    ))

    ord_m = diag['ordinary_vs_hp']['ordinary']
    hp_m = diag['ordinary_vs_hp']['high_pressure']
    sep_box = Table([[Paragraph(
        f"<b>Why Naive RRR Cutoffs Fail (Corpus Separation Audit):</b> Ordinary chases (<i>LI</i> &lt; 6.5) average a higher 2nd-innings RRR "
        f"(<b>{ord_m['inn2_mean_rrr']:.2f}</b> vs. <b>{hp_m['inn2_mean_rrr']:.2f}</b>) only because hopeless dead-rubber games pull the mean upward. "
        f"By contrast, our ML Leverage filter isolates genuine crunch balls (Mean <i>LI</i> <b>{hp_m['mean_li']:.2f}</b> vs. <b>{ord_m['mean_li']:.2f}</b>) "
        f"with sharper wicket intensity (<b>{hp_m['wicket_pct']:.2f}%</b> vs. <b>{ord_m['wicket_pct']:.2f}%</b>) and higher scoring tempo "
        f"(<b>{hp_m['implied_sr']:.1f}</b> vs. <b>{ord_m['implied_sr']:.1f}</b> Strike Rate).",
        st_card_body
    )]], colWidths=[content_w])
    sep_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RR_LIGHT_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, RR_BLUE),
        ('BOX', (0, 0), (-1, -1), 0.5, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sep_box)

    # =========================================================================
    # PAGE 2: 02. PERFORMANCE MEASUREMENT, BASELINES & SCORING LOGIC
    # =========================================================================
    story.append(NextPageTemplate('LaterPages'))
    story.append(PageBreak())
    story.append(make_section_banner("02", "Performance Measurement, Baselines & Empirical Bayes Logic", content_w))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "Evaluating raw strike rates or economies mixes player skill with match phase and league scoring rates. "
        "Instead, every delivery is scored relative to its <b>empirical context par</b>: batters earn <b>Runs Above Expected (RAE = Runs − Par<sub>format,phase</sub>)</b> "
        "per 100 balls, while bowlers earn <b>Runs Saved Above Expected (RSAE = Par<sub>format,phase</sub> − Bowler Runs)</b> per over (positive = tighter than par). "
        "Each player's high-pressure output (<i>LI</i> ≥ 6.5) is then compared directly against their own normal baseline (<i>LI</i> &lt; 6.5) to yield a net <b>Clutch Delta (Δ = HP − Baseline)</b>.",
        st_body
    ))

    story.append(Spacer(1, 4))
    formula_box = Table([[Paragraph(
        "<b>James-Stein Empirical Bayes Shrinkage:</b> &nbsp; "
        "<i>θ</i><sub>i</sub><sup>Bayes</sup> = [ <i>n</i><sub>i</sub> / (<i>n</i><sub>i</sub> + <i>v</i><sub>0</sub>) ] · <i>x</i><sub>i</sub><sup>obs</sup> + "
        "[ <i>v</i><sub>0</sub> / (<i>n</i><sub>i</sub> + <i>v</i><sub>0</sub>) ] · <i>μ</i><sub>0</sub>"
        "<br/><font size='8.0' color='#475569'><i>Shrinks noisy small-sample averages toward sample-weighted population prior μ</i><sub>0</sub> "
        "<i>using prior weights v</i><sub>0</sub> = <i>80 balls (batters), v</i><sub>0</sub> = <i>150 balls (bowlers), and v</i><sub>0</sub> = <i>10 matches (consistency).</i></font>",
        st_formula
    )]], colWidths=[content_w])
    formula_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RR_LIGHT_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, RR_PINK),
        ('BOX', (0, 0), (-1, -1), 0.6, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(formula_box)
    story.append(Spacer(1, 7))

    # 2-Column Composite Rating Logic Cards
    col_half = (content_w - 0.14 * inch) / 2.0
    bat_card = [
        Paragraph("Batting Clutch Score Architecture (0–100 Scale)", st_card_hdr),
        Paragraph(
            "• <b>40% Context-Adjusted RAE/100 (Bayes):</b> Expected-runs value added per 100 pressure balls vs. par.<br/>"
            "• <b>25% Clutch Elevation Δ (Bayes):</b> Net scoring uplift under pressure relative to the batter's own baseline.<br/>"
            "• <b>20% Match Consistency (Bayes):</b> % of HP matches (≥5 balls) finishing with positive RAE.<br/>"
            "• <b>15% Boundary Execution &amp; Survival:</b> Boundary run share combined with Bayesian wicket preservation.",
            st_card_body
        )
    ]
    bowl_card = [
        Paragraph("Bowling Clutch Score Architecture (0–100 Scale)", st_card_hdr),
        Paragraph(
            "• <b>35% Phase-Adjusted RSAE/Over (Bayes):</b> Runs saved per over relative to exact (Format × Phase) par.<br/>"
            "• <b>25% Wicket Hazard Rate (Bayes):</b> Shrinkage-stabilized wickets per 100 pressure balls bowled.<br/>"
            "• <b>20% Match Consistency (Bayes):</b> % of HP matches (≥4 balls) with positive RSAE or ≥1 scalp.<br/>"
            "• <b>20% Clutch Δ &amp; Dot Pressure:</b> Elevation in run suppression under crunch leverage + dot-ball choke %.",
            st_card_body
        )
    ]
    t_weights = Table([[bat_card, "", bowl_card]], colWidths=[col_half, 0.14 * inch, col_half])
    t_weights.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_PINK_PALE),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor("#EFF6FF")),
        ('LINEABOVE', (0, 0), (0, 0), 2.2, RR_PINK),
        ('LINEABOVE', (2, 0), (2, 0), 2.2, RR_BLUE),
        ('BOX', (0, 0), (0, 0), 0.5, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.5, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_weights)
    story.append(Spacer(1, 6))

    # K-Means Archetype Matrix
    st_km_h = ParagraphStyle('KmH', fontSize=8.0, leading=10, textColor=colors.white, fontName='Helvetica-Bold', alignment=0)
    st_km_c = ParagraphStyle('KmC', fontSize=7.9, leading=10.8, textColor=RR_TEXT)
    b_arch = diag['batter_archetype_counts']
    bw_arch = diag['bowler_archetype_counts']
    km_rows = [
        [Paragraph("Unsupervised Role", st_km_h), Paragraph("Standardized K-Means (k=3) Features", st_km_h), Paragraph("Identified Tactical Archetypes across Qualified Pool", st_km_h)],
        [
            Paragraph(f"<b>Batters</b> (n={diag['qualified_batters_count']})", st_km_c),
            Paragraph("Bayes HP RAE, Bayes Clutch Δ, HP Boundary %, Bayes Wicket Survival", st_km_c),
            Paragraph(f"<i>Elite Pressure Accelerator</i> ({b_arch['Elite Pressure Accelerator']}) • <i>Ice-Cold Chase Anchor</i> ({b_arch['Ice-Cold Chase Anchor']}) • <i>High-Leverage Finisher</i> ({b_arch['High-Leverage Finisher']})", st_km_c)
        ],
        [
            Paragraph(f"<b>Bowlers</b> (n={diag['qualified_bowlers_count']})", st_km_c),
            Paragraph("Bayes HP RSAE/Over, Bayes Wicket Rate, Bayes Dot-Ball %", st_km_c),
            Paragraph(f"<i>Clutch Wicket Hunter</i> ({bw_arch['Clutch Wicket Hunter']}) • <i>Run-Choking Squeeze Specialist</i> ({bw_arch['Run-Choking Squeeze Specialist']}) • <i>Balanced Pressure Enforcer</i> ({bw_arch['Balanced Pressure Enforcer']})", st_km_c)
        ],
    ]
    t_km = Table(km_rows, colWidths=[1.05 * inch, 2.35 * inch, content_w - 3.40 * inch])
    t_km.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), RR_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.4, RR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_km)
    story.append(Spacer(1, 6))

    fig2_path = os.path.join(fig_dir, "fig2_bayesian_shrinkage_funnel.png")
    story.append(Image(fig2_path, width=7.05 * inch, height=2.53 * inch))
    story.append(Paragraph(
        "Figure 2: Empirical Bayes Shrinkage across 51 qualified batters (left) and 67 qualified bowlers (right), damping extreme small-sample volatility toward the population prior.",
        st_cap
    ))

    # =========================================================================
    # PAGE 3: 03. FAIR COMPARISONS — FORMAT BIAS, PHASE MISMATCH & ELIGIBILITY
    # =========================================================================
    story.append(PageBreak())
    story.append(make_section_banner("03", "Fair Comparisons: Format Bias, Phase Mismatch & Eligibility Gates", content_w))
    story.append(Spacer(1, 6))

    t20_s = diag['format_summary']['T20']
    t20i_s = diag['format_summary']['T20I']
    bumrah_row = df_bowl_top[df_bowl_top['bowler_name'] == 'Jasprit Bumrah'].iloc[0]

    card_fmt = [
        Paragraph("Competition Discrepancy: IPL (T20) vs. T20I", st_card_hdr),
        Paragraph(
            f"Across clean legal deliveries, franchise <b>T20</b> ({t20_s['total_balls']:,} balls) averages a Strike Rate of <b>{t20_s['implied_sr']:.2f}</b> "
            f"(<b>{t20_s['implied_econ']:.2f} Econ</b>), whereas <b>T20I</b> ({t20i_s['total_balls']:,} balls) averages <b>{t20i_s['implied_sr']:.2f}</b> "
            f"(<b>{t20i_s['implied_econ']:.2f} Econ</b>). Unadjusted raw metrics artificially inflate IPL batters and penalize IPL bowlers by <b>+0.66 runs/over</b>.",
            st_card_body
        )
    ]
    card_bumrah = [
        Paragraph("Phase-Mismatch Trap ('The Bumrah Paradox')", st_card_hdr),
        Paragraph(
            f"<b>Jasprit Bumrah</b> maintains a <b>{bumrah_row['raw_base_econ']:.2f}</b> economy in ordinary overs and is held back for Death Overs "
            f"(par ~10.0 T20 / 9.2 T20I). Comparing his <b>{bumrah_row['raw_hp_econ']:.2f}</b> HP economy directly against baseline gives a false negative "
            f"delta ({bumrah_row['raw_hp_econ'] - bumrah_row['raw_base_econ']:.2f}), whereas context par reveals <b>+{bumrah_row['bayes_hp_rsae']:.2f} RSAE/over</b>.",
            st_card_body
        )
    ]
    t_bias = Table([[card_fmt, "", card_bumrah]], colWidths=[col_half, 0.14 * inch, col_half])
    t_bias.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_CARD_BG),
        ('BACKGROUND', (2, 0), (2, 0), RR_PINK_PALE),
        ('LINEABOVE', (0, 0), (0, 0), 2.2, RR_BLUE),
        ('LINEABOVE', (2, 0), (2, 0), 2.2, RR_PINK),
        ('BOX', (0, 0), (0, 0), 0.5, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.5, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_bias)
    story.append(Spacer(1, 6))

    # Empirical Format x Phase Par Benchmark Table
    par_pivot = df_par.pivot(index='phase', columns='match_format', values=['legal_balls', 'par_sr', 'par_econ']).loc[['Powerplay', 'Middle', 'Death']]
    st_ph = ParagraphStyle('ParH', fontSize=7.8, leading=9.5, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
    st_pc = ParagraphStyle('ParC', fontSize=7.9, leading=9.8, textColor=RR_TEXT, alignment=1)
    par_rows = [[
        Paragraph("Innings Phase", st_ph),
        Paragraph("T20 Legal Balls", st_ph), Paragraph("T20 Par SR", st_ph), Paragraph("T20 Par Econ", st_ph),
        Paragraph("T20I Legal Balls", st_ph), Paragraph("T20I Par SR", st_ph), Paragraph("T20I Par Econ", st_ph),
    ]]
    for ph in ['Powerplay', 'Middle', 'Death']:
        par_rows.append([
            Paragraph(f"<b>{ph}</b>", st_pc),
            Paragraph(f"{int(par_pivot.loc[ph, ('legal_balls', 'T20')]):,}", st_pc),
            Paragraph(f"<b>{par_pivot.loc[ph, ('par_sr', 'T20')]:.2f}</b>", st_pc),
            Paragraph(f"<b>{par_pivot.loc[ph, ('par_econ', 'T20')]:.2f}</b>", st_pc),
            Paragraph(f"{int(par_pivot.loc[ph, ('legal_balls', 'T20I')]):,}", st_pc),
            Paragraph(f"{par_pivot.loc[ph, ('par_sr', 'T20I')]:.2f}", st_pc),
            Paragraph(f"{par_pivot.loc[ph, ('par_econ', 'T20I')]:.2f}", st_pc),
        ])
    t_par = Table(par_rows, colWidths=[1.05*inch] + [(content_w - 1.05*inch) / 6.0] * 6)
    t_par.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), RR_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.4, RR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.2),
    ]))
    story.append(t_par)
    story.append(Spacer(1, 6))

    fig3_path = os.path.join(fig_dir, "fig3_format_context_bias.png")
    story.append(Image(fig3_path, width=7.0 * inch, height=2.37 * inch))
    story.append(Paragraph(
        "Figure 3: Empirical baseline scoring par across T20 (IPL) vs. T20I phases, showing the +0.82 RPO death-over inflation controlled by (Format × Phase) normalization.",
        st_cap
    ))

    # Eligibility & Exclusion Box
    vaibhav = df_excl_bat[df_excl_bat['striker_name'] == 'Vaibhav Sooryavanshi'].iloc[0]
    salt = df_excl_bat[df_excl_bat['striker_name'] == 'Phil Salt'].iloc[0]
    rasikh = df_excl_bowl[df_excl_bowl['bowler_name'] == 'Rasikh Salam'].iloc[0]
    excl_card = Table([[Paragraph(
        "<b>Symmetrical Eligibility &amp; Positive-Resilience Gates (Who Gets Excluded &amp; Why):</b><br/>"
        f"• <b>Batters (n={diag['qualified_batters_count']} qualified):</b> Require <b>≥ 200 HP balls</b>, <b>≥ 20 HP matches</b>, and <b>Bayes Clutch Δ ≥ 0</b>. "
        f"This filters out high-SR performers whose output actually <i>dips</i> under pressure—such as <b>Vaibhav Sooryavanshi</b> "
        f"({vaibhav['raw_hp_sr']:.1f} raw SR, yet <b>{vaibhav['bayes_clutch_delta']:.2f} Δ</b> across {int(vaibhav['hp_matches'])}m / {int(vaibhav['hp_balls'])}b) "
        f"and <b>Phil Salt</b> ({salt['bayes_clutch_delta']:.2f} Δ, {int(salt['hp_matches'])}m).<br/>"
        f"• <b>Bowlers (n={diag['qualified_bowlers_count']} qualified):</b> Require <b>≥ 35.0 HP overs</b>, <b>≥ 20 HP matches</b>, and <b>Bayes Clutch Δ ≥ 0</b>, "
        f"removing small-sample bursts (e.g., <b>Rasikh Salam</b>, {int(rasikh['hp_matches'])}m / {rasikh['hp_overs']:.1f} ov) in favor of 40–85 match veterans.",
        st_card_body
    )]], colWidths=[content_w])
    excl_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RR_LIGHT_BG),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, RR_PINK),
        ('BOX', (0, 0), (-1, -1), 0.5, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(excl_card)

    # =========================================================================
    # PAGE 4: 04. ORDERED TOP 10 BATTERS UNDER PRESSURE & EVIDENCE
    # =========================================================================
    story.append(PageBreak())
    story.append(make_section_banner("04", "Ordered Top 10 Batters Under Pressure & Empirical Evidence", content_w))
    story.append(Spacer(1, 6))

    story.append(make_ranking_table(df_bat_top, is_batter=True, content_w=content_w))
    story.append(Spacer(1, 7))

    fig4_path = os.path.join(fig_dir, "fig4_top10_batters_evidence.png")
    story.append(Image(fig4_path, width=7.1 * inch, height=2.90 * inch))
    story.append(Paragraph(
        "Figure 4: Top 10 Batters — Scoring shift from normal baseline (LI < 6.5) to high pressure (LI ≥ 6.5) alongside composite scores and match consistency.",
        st_cap
    ))

    # 3-Column Batter Spotlight Cards
    b1 = df_bat_top.iloc[0]
    b2 = df_bat_top.iloc[1]
    b3 = df_bat_top.iloc[2]
    b4 = df_bat_top.iloc[3]
    b7 = df_bat_top.iloc[6]
    col_third = (content_w - 0.16 * inch) / 3.0
    b_spot = [[
        [Paragraph("#1 Abhishek Sharma (Score 73.42)", st_card_hdr),
         Paragraph(f"Unmatched scoring pace under leverage: <b>+{b1['bayes_hp_rae']:.2f}</b> Bayes RAE/100 at <b>{b1['raw_hp_sr']:.1f} SR</b> across {int(b1['hp_matches'])} HP matches ({b1['bayes_consistency_pct']:.1f}% cons.).", st_card_body)],
        "",
        [Paragraph("#2 Brevis &amp; #7 Karthik (+Δ Gear)", st_card_hdr),
         Paragraph(f"Steepest positive clutch gears in the dataset: <b>{b2['striker_name']} (+{b2['bayes_clutch_delta']:.2f} Δ)</b> and <b>{b7['striker_name']} (+{b7['bayes_clutch_delta']:.2f} Δ)</b> elevate sharply when stakes peak.", st_card_body)],
        "",
        [Paragraph("#3 Jaiswal &amp; #4 Suryakumar", st_card_hdr),
         Paragraph(f"Elite repeatability anchors: <b>{b3['striker_name']} ({b3['bayes_consistency_pct']:.1f}% cons.)</b> and <b>{b4['striker_name']} ({int(b4['hp_matches'])}m, {int(b4['hp_balls'])}b, ±{b4['uncertainty_se']:.2f} SE)</b>.", st_card_body)],
    ]]
    t_bspot = Table(b_spot, colWidths=[col_third, 0.08*inch, col_third, 0.08*inch, col_third])
    t_bspot.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_PINK_PALE),
        ('BACKGROUND', (2, 0), (2, 0), RR_CARD_BG),
        ('BACKGROUND', (4, 0), (4, 0), RR_CARD_BG),
        ('LINEABOVE', (0, 0), (0, 0), 2.0, RR_PINK),
        ('LINEABOVE', (2, 0), (2, 0), 2.0, RR_BLUE),
        ('LINEABOVE', (4, 0), (4, 0), 2.0, RR_GOLD),
        ('BOX', (0, 0), (0, 0), 0.4, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.4, RR_BORDER),
        ('BOX', (4, 0), (4, 0), 0.4, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('LEFTPADDING', (3, 0), (3, -1), 0),
        ('RIGHTPADDING', (3, 0), (3, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_bspot)

    # =========================================================================
    # PAGE 5: 05. ORDERED TOP 10 BOWLERS UNDER PRESSURE & EVIDENCE
    # =========================================================================
    story.append(PageBreak())
    story.append(make_section_banner("05", "Ordered Top 10 Bowlers Under Pressure & Empirical Evidence", content_w))
    story.append(Spacer(1, 6))

    story.append(make_ranking_table(df_bowl_top, is_batter=False, content_w=content_w))
    story.append(Spacer(1, 7))

    fig5_path = os.path.join(fig_dir, "fig5_top10_bowlers_evidence.png")
    story.append(Image(fig5_path, width=7.1 * inch, height=2.90 * inch))
    story.append(Paragraph(
        "Figure 5: Top 10 Bowlers — Phase-normalized Runs Saved Above Expected per over vs. normal overs alongside composite scores and Bayesian wicket strike rates.",
        st_cap
    ))

    bw1 = df_bowl_top.iloc[0]
    bw2 = df_bowl_top.iloc[1]
    bw3 = df_bowl_top.iloc[2]
    bw7 = df_bowl_top.iloc[6]
    bw10 = df_bowl_top.iloc[9]
    bw_spot = [[
        [Paragraph(f"#1 Matheesha Pathirana ({bw1['bowling_clutch_score']:.2f})", st_card_hdr),
         Paragraph(f"Lethal strike frequency (<b>{bw1['bayes_hp_sr']:.1f} balls/wkt</b> across {int(bw1['hp_wickets'])} HP scalps) fused with <b>{bw1['bayes_consistency_pct']:.1f}%</b> consistency and +{bw1['bayes_hp_rsae']:.2f} RSAE/ov.", st_card_body)],
        "",
        [Paragraph(f"#2 Sunil Narine (+{bw2['bayes_hp_rsae']:.2f} RSAE)", st_card_hdr),
         Paragraph(f"Highest run-suppression margin in the entire corpus across {int(bw2['hp_matches'])} HP matches ({bw2['hp_overs']:.1f} overs at <b>{bw2['raw_hp_econ']:.2f} raw Econ</b>).", st_card_body)],
        "",
        [Paragraph("#3 Bumrah, #7 Rashid &amp; #10 Natarajan", st_card_hdr),
         Paragraph(f"<b>{bw3['bowler_name']}</b> ({bw3['bayes_consistency_pct']:.1f}% cons., 66m) &amp; <b>{bw7['bowler_name']}</b> ({int(bw7['hp_matches'])}m, ±{bw7['uncertainty_se']:.2f} SE) anchor volume; <b>{bw10['bowler_name']}</b> posts +{bw10['bayes_clutch_delta']:.2f} Δ.", st_card_body)],
    ]]
    t_bwspot = Table(bw_spot, colWidths=[col_third, 0.08*inch, col_third, 0.08*inch, col_third])
    t_bwspot.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (2, 0), (2, 0), RR_CARD_BG),
        ('BACKGROUND', (4, 0), (4, 0), RR_CARD_BG),
        ('LINEABOVE', (0, 0), (0, 0), 2.0, RR_BLUE),
        ('LINEABOVE', (2, 0), (2, 0), 2.0, RR_PINK),
        ('LINEABOVE', (4, 0), (4, 0), 2.0, RR_CYAN),
        ('BOX', (0, 0), (0, 0), 0.4, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.4, RR_BORDER),
        ('BOX', (4, 0), (4, 0), 0.4, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('LEFTPADDING', (3, 0), (3, -1), 0),
        ('RIGHTPADDING', (3, 0), (3, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_bwspot)

    # =========================================================================
    # PAGE 6: 06. RELIABILITY DIAGNOSTICS, LIMITATIONS & REPRODUCIBILITY
    # =========================================================================
    story.append(PageBreak())
    story.append(make_section_banner("06", "Reliability Diagnostics, Uncertainty Bounds & Limitations", content_w))
    story.append(Spacer(1, 5))

    fig6_path = os.path.join(fig_dir, "fig6_reliability_and_rejection_diagnostics.png")
    story.append(Image(fig6_path, width=7.15 * inch, height=2.46 * inch))
    story.append(Paragraph(
        "Figure 6: Left — Resilience filter separating positive clutch risers from pressure dips (Clutch Δ < 0, e.g., Vaibhav Sooryavanshi -10.2); Right — Standard Error convergence across match volume N.",
        st_cap
    ))

    # Dynamic SE Diagnostics Table
    bat_low_se = df_bat_top.sort_values('uncertainty_se').iloc[0]
    bat_hi_se = df_bat_top.sort_values('uncertainty_se', ascending=False).iloc[0]
    bw_low_se = df_bowl_top.sort_values('uncertainty_se').iloc[0]
    bw_hi_se = df_bowl_top.sort_values('uncertainty_se', ascending=False).iloc[0]
    top_cons_bw = df_bowl_full.sort_values('bayes_consistency_pct', ascending=False).iloc[0]

    st_th = ParagraphStyle('SeH', fontSize=7.9, leading=10, textColor=colors.white, fontName='Helvetica-Bold')
    st_tc = ParagraphStyle('SeC', fontSize=7.8, leading=10.5, textColor=RR_TEXT)
    se_raw = [
        ["Diagnostic Check", "Tightest Confidence Anchor", "Higher-Variance Boundary Profile", "Key Statistical Finding"],
        [
            "Top 10 Batters\n(≥20m, ≥200b, Δ≥0)",
            f"{bat_low_se['striker_name']}\n{int(bat_low_se['hp_matches'])} matches | SE ±{bat_low_se['uncertainty_se']:.2f}",
            f"{bat_hi_se['striker_name']}\n{int(bat_hi_se['hp_matches'])} matches | SE ±{bat_hi_se['uncertainty_se']:.2f}",
            f"Precision tightens sharply above 40 HP matches; positive Δ gate rejects {len(df_excl_bat[df_excl_bat['bayes_clutch_delta'] < 0])} pressure-dip profiles."
        ],
        [
            "Top 10 Bowlers\n(≥20m, ≥35ov, Δ≥0)",
            f"{bw_low_se['bowler_name']}\n{int(bw_low_se['hp_matches'])} matches | SE ±{bw_low_se['uncertainty_se']:.2f}",
            f"{bw_hi_se['bowler_name']}\n{int(bw_hi_se['hp_matches'])} matches | SE ±{bw_hi_se['uncertainty_se']:.2f}",
            f"All Top 10 bowlers span ≥{int(df_bowl_top['hp_matches'].min())} HP matches with narrow error bands (SE ≤ ±{bw_hi_se['uncertainty_se']:.2f})."
        ],
        [
            f"Consistency Peak\n({diag['qualified_bowlers_count']} Qual. Bowlers)",
            f"{top_cons_bw['bowler_name']}\n{int(top_cons_bw['hp_matches'])} matches | {top_cons_bw['bayes_consistency_pct']:.2f}%",
            f"Jasprit Bumrah (#3)\n{int(bw3['hp_matches'])} matches | {bw3['bayes_consistency_pct']:.2f}%",
            "Empirical Bayes damps 20-match hot streaks while rewarding sustained 60+ match reliability."
        ],
    ]
    se_rows = [[Paragraph(c.replace("\n", "<br/>"), st_th if r_i == 0 else st_tc) for c in row] for r_i, row in enumerate(se_raw)]
    t_se = Table(se_rows, colWidths=[1.30*inch, 1.50*inch, 1.65*inch, content_w - 4.45*inch])
    t_se.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), RR_BLUE),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, RR_LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.4, RR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_se)
    story.append(Spacer(1, 7))

    story.append(Paragraph("Model Limitations &amp; Analytical Safeguards", st_h2))
    lim_cards = [[
        [Paragraph("1. Innings 1 vs. 2 Asymmetry", st_card_hdr),
         Paragraph(f"Chases observe exact win-probability gradients, whereas Innings 1 relies on collapse &amp; death heuristics. Calibrating the swing scale (×38.0) balances HP rates ({diag['inn1_hp_pct']:.1f}% vs. {diag['inn2_hp_pct']:.1f}%).", st_card_body)],
        "",
        [Paragraph("2. Missing Venue / Dew / Drops", st_card_hdr),
         Paragraph("Supplied CSVs omit live dew, exact square dimensions, and dropped catches—adding single-match noise. Format × Phase par conditioning + ≥20m averaging dampens venue variance.", st_card_body)],
        "",
        [Paragraph("3. T20I Opposition Variance", st_card_hdr),
         Paragraph("Bilateral T20Is against associate nations can inflate raw strike rates. Requiring ≥200 HP balls, ≥20 HP matches, Bayes shrinkage, and Δ ≥ 0 guards against weak-opposition spikes.", st_card_body)],
    ]]
    t_lim = Table(lim_cards, colWidths=[col_third, 0.08*inch, col_third, 0.08*inch, col_third])
    t_lim.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), RR_CARD_BG),
        ('BACKGROUND', (2, 0), (2, 0), RR_CARD_BG),
        ('BACKGROUND', (4, 0), (4, 0), RR_CARD_BG),
        ('LINEABOVE', (0, 0), (0, 0), 2.0, RR_BLUE),
        ('LINEABOVE', (2, 0), (2, 0), 2.0, RR_PINK),
        ('LINEABOVE', (4, 0), (4, 0), 2.0, RR_GOLD),
        ('BOX', (0, 0), (0, 0), 0.4, RR_BORDER),
        ('BOX', (2, 0), (2, 0), 0.4, RR_BORDER),
        ('BOX', (4, 0), (4, 0), 0.4, RR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('LEFTPADDING', (3, 0), (3, -1), 0),
        ('RIGHTPADDING', (3, 0), (3, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_lim)
    story.append(Spacer(1, 8))

    repro_box = Table([[Paragraph(
        "<font color='#FFFFFF'><b>Full End-to-End Reproducibility:</b> All stages run deterministically via "
        "</font><font color='#FDB913' face='Courier' size='8.0'>win_probability_model.py → context_normalizer.py → "
        "bayesian_shrinkage.py → archetype_clusterer.py → pressure_ranker.py</font><font color='#FFFFFF'> "
        "(plus Streamlit explorer </font><font color='#FDB913' face='Courier' size='8.0'>dashboard/app.py</font>"
        "<font color='#FFFFFF'>) open-sourced at <b>https://github.com/saroshkumar-ops/RR-hack</b>.</font>",
        st_card_body
    )]], colWidths=[content_w])
    repro_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RR_BLUE),
        ('LINEABOVE', (0, 0), (-1, 0), 2.5, RR_PINK),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ]))
    story.append(repro_box)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully compiled restructured Methodology Report PDF: {out_pdf}")


if __name__ == "__main__":
    build_pdf()
