"""
Rajasthan Royals - SupeRR Selector Season 2
Interactive ML Clutch & Pressure Analytics Dashboard
"""
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Page configuration
st.set_page_config(
    page_title="SupeRR Selector S2 | Pressure Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Royals Styling
st.markdown("""
<style>
    .main-title {
        color: #EA1A80;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8C9BAE;
        font-size: 1.05rem;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .badge-pink {
        background-color: #EA1A80;
        color: white;
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_ml_rankings():
    proc_dir = os.path.join(REPO_ROOT, "data/processed")
    bat_path = os.path.join(proc_dir, "ml_full_batters_under_pressure.csv")
    bowl_path = os.path.join(proc_dir, "ml_full_bowlers_under_pressure.csv")

    if not os.path.exists(bat_path) or not os.path.exists(bowl_path):
        st.error("ML Ranking files not found. Please run `python src/ml/pressure_ranker.py` first.")
        st.stop()

    df_bat = pd.read_csv(bat_path)
    df_bowl = pd.read_csv(bowl_path)
    return df_bat, df_bowl

df_bat, df_bowl = load_ml_rankings()

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="main-title">🏏 Rajasthan Royals: SupeRR Selector S2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Machine Learning Win Probability Leverage & Empirical Bayes Pressure Rankings (2022–2026)</div>', unsafe_allow_html=True)
with col2:
    st.markdown(
        """<div style='text-align: right; padding-top: 15px;'>
        <span class='badge-pink'>AUC: 0.9212 | 200,999 BALLS</span>
        </div>""", unsafe_allow_html=True
    )

# Sidebar controls
st.sidebar.header("⚙️ ML Filter Controls")
min_bat_matches = st.sidebar.slider("Min High-Pressure Matches (Batters)", min_value=10, max_value=30, value=10)
min_bowl_matches = st.sidebar.slider("Min High-Pressure Matches (Bowlers)", min_value=15, max_value=35, value=15)

bat_arch_filter = st.sidebar.multiselect(
    "Batter Clutch Archetype",
    options=list(df_bat['ml_archetype'].unique()),
    default=list(df_bat['ml_archetype'].unique())
)
bowl_arch_filter = st.sidebar.multiselect(
    "Bowler Clutch Archetype",
    options=list(df_bowl['ml_archetype'].unique()),
    default=list(df_bowl['ml_archetype'].unique())
)

f_bat = df_bat[(df_bat['hp_matches'] >= min_bat_matches) & (df_bat['ml_archetype'].isin(bat_arch_filter))].copy()
f_bowl = df_bowl[(df_bowl['hp_matches'] >= min_bowl_matches) & (df_bowl['ml_archetype'].isin(bowl_arch_filter))].copy()

# KPI Summary Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Qualified Pressure Batters", len(f_bat))
with m2:
    st.metric("Qualified Pressure Bowlers", len(f_bowl))
with m3:
    top_b = f_bat.iloc[0]['striker_name'] if not f_bat.empty else "N/A"
    st.metric("#1 Batter Under Pressure", top_b)
with m4:
    top_bw = f_bowl.iloc[0]['bowler_name'] if not f_bowl.empty else "N/A"
    st.metric("#1 Bowler Under Pressure", top_bw)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Top 10 Leaderboards",
    "📊 Consistency & Clustering Explorer",
    "🔍 Player Deep-Dive & Baseline Delta",
    "📋 Methodology Summary"
])

# TAB 1: Top 10 Leaderboards
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🏏 Top 10 Batters Under Pressure")
        st.caption("Ranked by Context-Normalized RAE, Clutch Delta, Match Consistency & Bayesian Shrinkage.")
        top10_bat = f_bat.head(10)[['rank', 'striker_name', 'hp_matches', 'raw_hp_sr', 'bayes_hp_rae', 'bayes_clutch_delta', 'bayes_consistency_pct', 'batting_clutch_score', 'ml_archetype']].rename(columns={
            'rank': 'Rank', 'striker_name': 'Batter', 'hp_matches': 'HP Matches',
            'raw_hp_sr': 'HP SR', 'bayes_hp_rae': 'Bayes RAE/100',
            'bayes_clutch_delta': 'Clutch Δ', 'bayes_consistency_pct': 'Consistency %',
            'batting_clutch_score': 'Score', 'ml_archetype': 'ML Archetype'
        })
        st.dataframe(top10_bat, use_container_width=True, hide_index=True)

        fig_bat = px.bar(
            f_bat.head(10), x='batting_clutch_score', y='striker_name', orientation='h',
            color='ml_archetype', title="Top 10 Batters: Clutch Score",
            labels={'batting_clutch_score': 'Batting Clutch Score', 'striker_name': ''},
            color_discrete_sequence=['#EA1A80', '#0075FF', '#FDB913']
        )
        fig_bat.update_layout(yaxis={'categoryorder': 'total ascending'}, height=380)
        st.plotly_chart(fig_bat, use_container_width=True)

    with c2:
        st.subheader("🎯 Top 10 Bowlers Under Pressure")
        st.caption("Ranked by Phase-Normalized Runs Saved (RSAE), Wicket Rate, Match Consistency & Bayesian Shrinkage.")
        top10_bowl = f_bowl.head(10)[['rank', 'bowler_name', 'hp_matches', 'hp_overs', 'bayes_hp_rsae', 'bayes_hp_sr', 'bayes_consistency_pct', 'bowling_clutch_score', 'ml_archetype']].rename(columns={
            'rank': 'Rank', 'bowler_name': 'Bowler', 'hp_matches': 'HP Matches',
            'hp_overs': 'HP Overs', 'bayes_hp_rsae': 'Bayes RSAE/Ov',
            'bayes_hp_sr': 'Bayes Wkt SR', 'bayes_consistency_pct': 'Consistency %',
            'bowling_clutch_score': 'Score', 'ml_archetype': 'ML Archetype'
        })
        st.dataframe(top10_bowl, use_container_width=True, hide_index=True)

        fig_bowl = px.bar(
            f_bowl.head(10), x='bowling_clutch_score', y='bowler_name', orientation='h',
            color='ml_archetype', title="Top 10 Bowlers: Clutch Score",
            labels={'bowling_clutch_score': 'Bowling Clutch Score', 'bowler_name': ''},
            color_discrete_sequence=['#001D48', '#EA1A80', '#00C49F']
        )
        fig_bowl.update_layout(yaxis={'categoryorder': 'total ascending'}, height=380)
        st.plotly_chart(fig_bowl, use_container_width=True)

# TAB 2: Consistency & Clustering
with tab2:
    st.subheader("📈 Reliability vs. Impact Across High-Pressure Matches")
    sc1, sc2 = st.columns(2)

    with sc1:
        fig_sc_bat = px.scatter(
            f_bat, x='bayes_hp_rae', y='bayes_consistency_pct',
            size='hp_balls', color='ml_archetype', hover_name='striker_name',
            hover_data=['hp_matches', 'batting_clutch_score', 'uncertainty_se'],
            title="Batters: Pressure Consistency (%) vs. Bayesian Runs Above Expected",
            labels={'bayes_hp_rae': 'Bayesian Pressure RAE / 100 Balls', 'bayes_consistency_pct': 'Positive Impact Matches (%)'}
        )
        st.plotly_chart(fig_sc_bat, use_container_width=True)

    with sc2:
        fig_sc_bowl = px.scatter(
            f_bowl, x='bayes_hp_rsae', y='bayes_consistency_pct',
            size='hp_overs', color='ml_archetype', hover_name='bowler_name',
            hover_data=['hp_matches', 'bowling_clutch_score', 'uncertainty_se'],
            title="Bowlers: Pressure Consistency (%) vs. Bayesian Runs Saved Above Expected",
            labels={'bayes_hp_rsae': 'Bayesian Runs Saved / Over', 'bayes_consistency_pct': 'Positive Impact Matches (%)'}
        )
        st.plotly_chart(fig_sc_bowl, use_container_width=True)

# TAB 3: Player Deep Dive
with tab3:
    st.subheader("🔍 Player Baseline vs. Pressure Comparison")
    mode = st.radio("Select Discipline:", ["Batter", "Bowler"], horizontal=True)

    if mode == "Batter":
        player = st.selectbox("Select Qualified Batter:", options=f_bat['striker_name'].tolist())
        row = f_bat[f_bat['striker_name'] == player].iloc[0]

        pcol1, pcol2 = st.columns([1, 1])
        with pcol1:
            st.markdown(f"### **{row['striker_name']}** (Rank #{int(row['rank'])})")
            st.markdown(f"**ML Archetype:** `{row['ml_archetype']}`")
            st.markdown(f"**Sample Size:** {int(row['hp_balls'])} High-Pressure Balls across {int(row['hp_matches'])} Matches (SE: `±{row['uncertainty_se']}`)")
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Normal Baseline SR", f"{row['raw_base_sr']:.1f}")
            k2.metric("High-Pressure SR", f"{row['raw_hp_sr']:.1f}", delta=f"{row['raw_hp_sr'] - row['raw_base_sr']:+.1f}")
            k3.metric("Bayesian Clutch Δ", f"{row['bayes_clutch_delta']:+.1f} RAE")

            k4, k5, k6 = st.columns(3)
            k4.metric("Boundary % (HP)", f"{row['hp_boundary_pct']:.1f}%")
            k5.metric("Consistency %", f"{row['bayes_consistency_pct']:.1f}%")
            k6.metric("Clutch Score", f"{row['batting_clutch_score']:.1f}/100")

        with pcol2:
            fig_comp = go.Figure(data=[
                go.Bar(name='Normal Baseline (LI < 6.5)', x=['Context RAE / 100'], y=[row['base_rae_per_100']], marker_color='#8C9BAE'),
                go.Bar(name='High Pressure (LI >= 6.5)', x=['Context RAE / 100'], y=[row['hp_rae_per_100']], marker_color='#EA1A80')
            ])
            fig_comp.update_layout(title=f"Context-Adjusted Performance Shift: {player}", barmode='group', height=340)
            st.plotly_chart(fig_comp, use_container_width=True)

    else:
        player = st.selectbox("Select Qualified Bowler:", options=f_bowl['bowler_name'].tolist())
        row = f_bowl[f_bowl['bowler_name'] == player].iloc[0]

        pcol1, pcol2 = st.columns([1, 1])
        with pcol1:
            st.markdown(f"### **{row['bowler_name']}** (Rank #{int(row['rank'])})")
            st.markdown(f"**ML Archetype:** `{row['ml_archetype']}`")
            st.markdown(f"**Sample Size:** {row['hp_overs']} High-Pressure Overs across {int(row['hp_matches'])} Matches (SE: `±{row['uncertainty_se']}`)")
            
            k1, k2, k3 = st.columns(3)
            k1.metric("Normal Economy", f"{row['raw_base_econ']:.2f}")
            k2.metric("High-Pressure Econ", f"{row['raw_hp_econ']:.2f}")
            k3.metric("Bayes RSAE / Over", f"{row['bayes_hp_rsae']:+.2f}")

            k4, k5, k6 = st.columns(3)
            k4.metric("Bayes Wicket SR", f"{row['bayes_hp_sr']:.1f} balls")
            k5.metric("Consistency %", f"{row['bayes_consistency_pct']:.1f}%")
            k6.metric("Clutch Score", f"{row['bowling_clutch_score']:.1f}/100")

        with pcol2:
            fig_comp = go.Figure(data=[
                go.Bar(name='Normal Baseline (LI < 6.5)', x=['Runs Saved / Over vs Par'], y=[row['base_rsae_per_over']], marker_color='#8C9BAE'),
                go.Bar(name='High Pressure (LI >= 6.5)', x=['Runs Saved / Over vs Par'], y=[row['hp_rsae_per_over']], marker_color='#001D48')
            ])
            fig_comp.update_layout(title=f"Phase-Adjusted Runs Saved Shift: {player}", barmode='group', height=340)
            st.plotly_chart(fig_comp, use_container_width=True)

# TAB 4: Methodology Summary
with tab4:
    st.subheader("📋 Analytical Architecture Summary")
    st.markdown("""
    ### **1. Defining Pressure via Machine Learning (Win Probability Leverage)**
    * Trained a **HistGradientBoosting Classifier** across **200,999 ball-by-ball deliveries** (`AUC = 0.9212`).
    * Calculated counterfactual win probability swing ($|\\hat{P}(\\text{Win} \\mid \\text{Six}) - \\hat{P}(\\text{Win} \\mid \\text{Wicket})|$) to derive a continuous **Leverage Index ($LI \\in [0, 10]$)**.
    * Deliveries with **$LI \\ge 6.5$** capture the top **29.4% most decisive moments** (tight chases, death overs, top-order collapses, Super Overs).

    ### **2. Fair Comparisons & Context Normalization**
    * Addressed format discrepancy (**IPL implied SR 139.5 vs T20I 129.3**) and phase bias (**Death par ~10.3 vs Powerplay ~7.5**) using **Runs Above Expected (RAE)** and **Runs Saved Above Expected (RSAE)** stratified by `(Match Format × Innings Phase)`.

    ### **3. Empirical Bayes Shrinkage & Reliability**
    * Eliminated small-sample flukes using **Empirical Bayes Shrinkage** ($v_0 = 80$ balls for batters; $v_0 = 150$ balls for bowlers; $v_0 = 10$ matches for consistency).
    * Integrated **Match-to-Match Consistency Rate** directly into the composite Clutch Score so players must deliver *repeatedly* across high-stakes contests.
    """)
