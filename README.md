# 🏏 Rajasthan Royals - SupeRR Selector Season 2

> **Data-Driven Uncapped Talent Identification & IPL 2027 Auction Strategy**  
> Built for the official Rajasthan Royals analytics hackathon on Unstop.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![Rajasthan Royals](https://img.shields.io/badge/Franchise-Rajasthan%20Royals-EA1A80.svg)](https://www.rajasthanroyals.com/)

---

## 📌 Project Overview

In high-stakes IPL auction dynamics, marquee capped players command upwards of ₹15–25 Crore. The true competitive advantage of championship teams lies in **uncapped talent efficiency**—identifying high-ceiling domestic prodigies at controlled price points (₹30 Lakh – ₹1.5 Crore) who solve specific tactical gaps.

This repository implements a talent-scouting and valuation framework tailored to Rajasthan Royals' think tank (Head Coach **Kumar Sangakkara** & Director of Strategy and Analytics **Giles Lindsay**). It pinpoints the **Top 10 youngest uncapped domestic players** for the upcoming auction by synthesizing:
1. **Phase-Specific Situational Metrics** (Powerplay, Middle Overs, Death Overs 16–20).
2. **Age-Ceiling Runway Curve** (Quantifying developmental acceleration for teen and early-20s prospects).
3. **RR Tactical Archetype Fit** (Direct alignment with the Royals' playing XI and home-ground pitch dynamics).

---

## 🏗️ Repository Architecture

```text
RR-hack/
├── data/
│   ├── raw/                # Drop official RR Data Pack here (releasing Nov 8)
│   ├── sample/             # Benchmark domestic player dataset (20 prospects)
│   └── processed/          # Model outputs & Top 10 target profiles
├── src/
│   ├── config.py           # RR tactical priorities, league benchmarks, age weights
│   ├── metrics/
│   │   ├── batting_metrics.py  # True SR, Phase acceleration, Dot-ball penalty
│   │   └── bowling_metrics.py  # True Econ, Death overs suppression, Wicket SR
│   ├── models/
│   │   ├── talent_ranker.py    # Composite talent ranking algorithm
│   │   └── rr_squad_fit.py     # RR archetype matching & auction valuation
│   └── run_pipeline.py     # End-to-end command-line runner
├── dashboard/
│   └── app.py              # Interactive Streamlit Scouting Board & Pitch Deck
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb # Jupyter EDA template
├── requirements.txt
└── README.md
```

---

## 🔬 Analytical Framework & Methodology

### 1. Rejecting "Vanity Metrics"
Traditional metrics (aggregate batting average or overall economy) mask match context. A strike rate of 140 in the powerplay is below par, but a strike rate of 190 in overs 16–20 against 145km/h bowling is invaluable.

### 2. Core Formulations

* **True Strike Rate (TSR) & True Economy Rate (TER):**  
  $$\text{TSR} = \text{Strike Rate} - \text{Benchmark}_{\text{phase}}$$
  $$\text{TER} = \text{Benchmark}_{\text{phase}} - \text{Economy}$$

* **Death-Overs Acceleration Index ($DOAI$):**  
  Measures scoring efficiency in overs 16–20 and boundary percentage against high pace.

* **Dot-Ball Pressure & Boundary Suppression:**  
  $$\text{Pressure Score} = \left(\frac{\text{Dot}\%}{50}\right) \times 50 + \left(\frac{20 - \text{Boundary Conceded}\%}{10}\right) \times 50$$

* **Youth Development Runway Multiplier:**  
  Younger players have steeper developmental curves under RR's High-Performance Centre:
  * **Age $\le$ 19:** `1.25x` (Teen Prodigy Tier)
  * **Age 20–22:** `1.15x` (Early Prime Development Tier)
  * **Age 23–24:** `1.05x` (High-Runway Tier)
  * **Age $\ge$ 25:** `0.95x` (Immediate Plug & Play)

* **Composite Royals Talent Rating:**  
  $$\text{Score} = \Big(0.70 \times \text{Base Impact} + 0.30 \times \text{Tactical Fit Score}\Big) \times \text{Age Multiplier}$$

---

## 🎯 Rajasthan Royals Tactical Archetypes (IPL 2027)

1. **Death-Overs Power Finisher:** Indian batters striking at 175+ from ball one against high pace.
2. **Death-Overs Enforcer Pacer:** Fast bowlers executing hard lengths/yorkers with death economy $\le 8.8$.
3. **Middle-Overs Attacking Spinner:** Wrist/mystery spinners choking overs 7–15 with sub-7.0 economy.
4. **Lower-Order Power All-Rounder:** Multi-utility cricketers providing 2–4 overs and high-SR lower-order runs.
5. **Dynamic Powerplay Batter:** High-tempo openers capitalizing on the initial 6 overs without consuming dot balls.

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/saroshkumar-ops/RR-hack.git
cd RR-hack

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run the Ranking Pipeline
To process the dataset and generate the Top 10 uncapped targets:
```bash
python src/run_pipeline.py
```
Outputs will be saved in `data/processed/top10_uncapped_stars.csv`.

### 3. Launch the Interactive Scouting Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to explore:
* Top 10 Uncapped Leaderboard
* Individual Player Skill Radars vs League Baselines
* RR Tactical Squad Gap Matrix
* Auction War-Room Pitch Summary

---

## 📅 Hackathon Action Plan (Nov 8 – Nov 18)

- [x] **Day 0 (Nov 7):** Repository initialization, core metric engineering, ranking algorithms, and interactive Streamlit board.
- [ ] **Day 1 (Nov 8):** Download official RR proprietary data pack from Unstop and drop into `data/raw/`.
- [ ] **Day 2–4:** Feature extraction on real domestic player data, outlier handling, and role validation.
- [ ] **Day 5–7:** Finalize Top 10 player profiles, radar visualizations, and auction valuation strategy.
- [ ] **Day 8–10:** Export presentation deck / interactive dashboard link and submit on Unstop before Nov 18, 6:29 PM IST.
