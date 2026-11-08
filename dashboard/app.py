"""
Rajasthan Royals - SupeRR Selector Season 2
Interactive Scouting & Auction Strategy Dashboard
"""
import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Setup system path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.models.talent_ranker import rank_uncapped_players
from src.utils.schema_mapper import standardize_dataframe, apply_sample_size_filter
from src.config import RR_TACTICAL_PRIORITIES, BENCHMARKS

# Page configuration
st.set_page_config(
    page_title="SupeRR Selector S2 | Rajasthan Royals Scouting",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Royals Pink #EA1A80, Royals Blue #001D48, Accent Gold #FDB913)
st.markdown("""
<style>
    .main-title {
        color: #EA1A80;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8C9BAE;
        font-size: 1.1rem;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #0c1829;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #EA1A80;
    }
    .badge-pink {
        background-color: #EA1A80;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    raw_path = os.path.join(REPO_ROOT, "data/raw")
    csv_files = [os.path.join(raw_path, f) for f in os.listdir(raw_path) if f.endswith(('.csv', '.xlsx'))] if os.path.exists(raw_path) else []
    
    if csv_files:
        f = csv_files[0]
        df = pd.read_excel(f) if f.endswith('.xlsx') else pd.read_csv(f)
    else:
        sample_path = os.path.join(REPO_ROOT, "data/sample/uncapped_players_sample.csv")
        df = pd.read_csv(sample_path)
    
    df_clean = standardize_dataframe(df)
    df_filtered = apply_sample_size_filter(df_clean, min_balls=15, min_overs=4.0)
    return rank_uncapped_players(df_filtered)

df_all = get_data()

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="main-title">🏏 Rajasthan Royals: SupeRR Selector S2</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">IPL 2027 Auction Strategy • Uncapped Talent Identification Framework</div>', unsafe_allow_html=True)
with col2:
    st.markdown(
        """<div style='text-align: right; padding-top: 15px;'>
        <span class='badge-pink'>OFFICIAL RR FRAMEWORK</span>
        </div>""", unsafe_allow_html=True
    )

# Sidebar filters
st.sidebar.header("🎯 Scouting Filters")
max_age = st.sidebar.slider("Maximum Age", min_value=17, max_value=26, value=25)
role_filter = st.sidebar.multiselect(
    "Filter by Role",
    options=list(df_all['role'].unique()),
    default=list(df_all['role'].unique())
)
archetype_filter = st.sidebar.multiselect(
    "Tactical Archetype",
    options=list(df_all['rr_tactical_archetype'].unique()),
    default=list(df_all['rr_tactical_archetype'].unique())
)

filtered_df = df_all[
    (df_all['age'] <= max_age) &
    (df_all['role'].isin(role_filter)) &
    (df_all['rr_tactical_archetype'].isin(archetype_filter))
].copy()

# Summary Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Prospects Scouted", len(filtered_df))
with m2:
    top10_slice = filtered_df.head(10)
    avg_age = top10_slice['age'].mean() if not top10_slice.empty else 0
    st.metric("Top 10 Average Age", f"{avg_age:.1f} yrs")
with m3:
    teen_count = len(filtered_df[filtered_df['age'] < 20])
    st.metric("Teen Prodigies (<20 yrs)", teen_count)
with m4:
    finisher_count = len(filtered_df[filtered_df['rr_tactical_archetype'].str.contains('Finisher|Enforcer', na=False)])
    st.metric("High-Leverage Specialists", finisher_count)

st.markdown("---")

# Main Content Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Top 10 Youngest Uncapped Board",
    "🎯 Player Radar & Deep Dive",
    "📈 Tactical Archetypes & Needs Fit",
    "📋 Auction War-Room Pitch"
])

# TAB 1: Top 10 Board
with tab1:
    st.subheader("⭐ The Top 10 Youngest Uncapped Picks for RR")
    st.caption("Ranked by Royals Composite Score (combines phase performance, ceiling multiplier, and tactical archetype fit).")

    top10 = filtered_df.head(10).copy()
    
    display_df = top10[[
        'rank', 'name', 'age', 'role', 'domestic_league', 
        'royals_composite_score', 'rr_tactical_archetype', 'estimated_auction_bracket'
    ]].rename(columns={
        'rank': 'Rank',
        'name': 'Player',
        'age': 'Age',
        'role': 'Role',
        'domestic_league': 'Tournament/League',
        'royals_composite_score': 'RR Composite Score',
        'rr_tactical_archetype': 'Tactical Archetype',
        'estimated_auction_bracket': 'Projected Auction Bracket'
    })

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # Visual Bar Chart of Top 10
    fig = px.bar(
        top10,
        x='name',
        y='royals_composite_score',
        color='rr_tactical_archetype',
        hover_data=['age', 'domestic_league', 'estimated_auction_bracket'],
        title="Top 10 Prospects Ranked by Royals Composite Score",
        labels={'name': 'Player Name', 'royals_composite_score': 'Score', 'rr_tactical_archetype': 'Tactical Role'},
        color_discrete_sequence=['#EA1A80', '#0075FF', '#00C49F', '#FFBB28', '#FF8042']
    )
    fig.update_layout(xaxis_tickangle=-30, height=420)
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: Player Radar & Deep Dive
with tab2:
    st.subheader("🔍 Scout an Individual Player Profile")
    selected_player = st.selectbox("Select Player for Detailed Radar Analysis:", options=filtered_df['name'].tolist())

    if selected_player:
        p_row = filtered_df[filtered_df['name'] == selected_player].iloc[0]

        pcol1, pcol2 = st.columns([1, 1])

        with pcol1:
            st.markdown(f"### **{p_row['name']}** ({p_row['age']} yrs)")
            st.markdown(f"**Primary Role:** {p_row['role']} | **State/League:** {p_row['domestic_league']}")
            st.markdown(f"**Tactical Archetype:** `{p_row['rr_tactical_archetype']}`")
            st.markdown(f"**Age Runway Tier:** {p_row['age_runway_tier']} (Multiplier: `x{p_row['age_multiplier']}`)")
            st.markdown(f"**Projected Auction Target:** `{p_row['estimated_auction_bracket']}`")
            
            st.info(f"💡 **Tactical Fit Rationale:**\n{p_row['tactical_reasoning']}")

            # Key Numbers Grid
            kpi_c1, kpi_c2, kpi_c3 = st.columns(3)
            with kpi_c1:
                st.metric("Strike Rate", f"{p_row['strike_rate']:.1f}" if p_row['balls'] > 0 else "N/A")
                st.metric("Death SR", f"{p_row['death_sr']:.1f}" if p_row['balls'] > 0 else "N/A")
            with kpi_c2:
                st.metric("Economy", f"{p_row['bowling_econ']:.2f}" if p_row['overs'] > 0 else "N/A")
                st.metric("Death Economy", f"{p_row['death_econ']:.2f}" if p_row['overs'] > 0 else "N/A")
            with kpi_c3:
                st.metric("Dot Ball %", f"{p_row['dot_pct_bat']:.1f}%" if p_row['balls'] > 0 else f"{p_row['dot_pct_bowl']:.1f}%")
                st.metric("RR Score", f"{p_row['royals_composite_score']:.1f}")

        with pcol2:
            # Radar Chart of attributes normalized to 100
            radar_categories = ['Death Execution', 'Powerplay Impact', 'Strike/Dot Efficiency', 'Versatility', 'Ceiling Potential']
            
            # Normalization logic
            death_val = (p_row['death_sr'] / 220.0 * 100) if p_row['balls'] > 20 else ((12.0 - p_row['death_econ']) / 4.0 * 100)
            pp_val = (p_row['pp_sr'] / 180.0 * 100) if p_row['balls'] > 20 else ((9.0 - p_row['pp_econ']) / 3.0 * 100)
            dot_val = (100 - p_row['dot_pct_bat']) if p_row['balls'] > 20 else (p_row['dot_pct_bowl'] * 1.8)
            adapt_val = p_row.get('adaptability_score', 70) / 2.0
            ceiling_val = p_row['age_multiplier'] * 75

            player_values = [
                min(max(float(death_val), 10), 100),
                min(max(float(pp_val), 10), 100),
                min(max(float(dot_val), 10), 100),
                min(max(float(adapt_val), 10), 100),
                min(max(float(ceiling_val), 10), 100)
            ]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=player_values,
                theta=radar_categories,
                fill='toself',
                name=p_row['name'],
                line=dict(color='#EA1A80', width=2),
                fillcolor='rgba(234, 26, 128, 0.3)'
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=[60, 60, 60, 60, 60],
                theta=radar_categories,
                name='League Baseline',
                line=dict(color='#8C9BAE', dash='dash', width=1.5)
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title=f"Tactical Skill Radar: {p_row['name']}",
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

# TAB 3: Tactical Archetypes & Needs Fit
with tab3:
    st.subheader("🎯 Rajasthan Royals Tactical Squad Gaps & Archetypes")
    
    st.write("For IPL 2027, the Royals' war room prioritizes filling 5 core domestic archetypes:")
    
    arch_cols = st.columns(len(RR_TACTICAL_PRIORITIES))
    for i, (key, info) in enumerate(RR_TACTICAL_PRIORITIES.items()):
        with arch_cols[i]:
            st.markdown(f"**{info['title']}**")
            st.caption(f"Priority: `{info['priority_level']}`")
            st.write(info['description'])

    st.markdown("---")
    st.subheader("📊 Prospect Distribution by Archetype")
    
    fig_pie = px.pie(
        filtered_df,
        names='rr_tactical_archetype',
        title="Distribution of Scouted Players Across RR Tactical Roles",
        color_discrete_sequence=['#EA1A80', '#001D48', '#0075FF', '#00C49F', '#FFBB28']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# TAB 4: Auction War-Room Pitch
with tab4:
    st.subheader("📋 Executive Pitch Summary for Kumar Sangakkara & Giles Lindsay")
    
    st.markdown("""
    ### **Strategic Blueprint: Rajasthan Royals IPL 2027 Talent Acquisition**
    
    **1. Problem Statement & Franchise Context:**
    * In IPL auction dynamics, marquee capped stars command upwards of ₹15–25 Crore. 
    * The differentiator between playoff teams and champions is **uncapped efficiency**—securing high-ceiling, role-specific domestic players at baseline/controlled prices (₹30L – ₹1.5Cr) who perform in high-leverage phases.
    
    **2. Scouting Methodology:**
    * **No Vanity Metrics:** We reject raw averages and aggregate strike rates.
    * **Phase Weighting:** Every ball is evaluated contextually: Powerplay boundary rate, Middle overs strike rotation & spin choke, and Death overs (16–20) acceleration and execution.
    * **Age-Ceiling Curve:** Youth (<21) receives a deliberate analytical multiplier to reflect rapid biological and skill development curves under RR's High-Performance Centre.

    **3. Core Recommendations for the War Room:**
    * Target **Swastik Chikara** or **Sameer Rizvi** to secure explosive Indian finishing power against 145kmph+ pace.
    * Secure young mystery spinners like **Digvesh Rathi** or multi-format spin all-rounders like **Manav Suthar** to control middle overs at the Sawai Mansingh Stadium.
    * Target death-overs enforcers like **Abhinandan Singh** for hard-length yorker suppression in tight finishes.
    """)
    
    st.success("✅ Ready for export into presentation pitch deck (PPT/PDF).")
