# 🗺️ Master Execution Roadmap & Timeline

> **Rajasthan Royals - SupeRR Selector Season 2**  
> **IPL 2027 Auction Strategy • Uncapped Talent Identification**

---

## 🎯 The Winning Philosophy

The evaluation panel is led by **Kumar Sangakkara** (Head Coach) and **Giles Lindsay** (Director of Strategy & Analytics). Winning this hackathon requires satisfying two distinct minds:
* **The Tactician (Sangakkara):** Clarity of role, situational composure, how the player executes under pressure, and how they slot into the Royals' playing XI.
* **The Analyst (Lindsay):** Rigorous methodology, contextual normalization (ground sizes, match state, phase of play), sample size controls, and absence of vanity statistics.

---

## ⏱️ Detailed 10-Day Execution Timeline

```
Nov 8 (T-10h) ───► Nov 8 (T-0h) ───► Nov 9-11 ───► Nov 12-14 ───► Nov 15-16 ───► Nov 17-18
Pre-Drop Prep     Data Drop & Triage  Deep Modeling   Archetype Fit   Deck/Dashboard   Final Submission
```

### Stage 0: The Final Hours (Pre-Release Prep — Today until ~6 PM IST)
- [x] Scaffold repository architecture and commit to GitHub.
- [x] Build core phase metrics engine (True Strike Rate, True Economy, Dot Ball Pressure).
- [x] Create working Streamlit dashboard prototype with radar visualizations.
- [ ] Build **Dynamic Schema Ingestion Engine** (`src/utils/schema_mapper.py`) to auto-adapt to whatever column format RR provides.
- [ ] Implement sample size filters (minimum balls faced / overs bowled thresholding).

### Stage 1: Data Drop & Triage (Tonight / Nov 8-9)
- [ ] Download official RR data pack from Unstop under **"Brief / Case"**.
- [ ] Place files in `data/raw/` and inspect format (Ball-by-Ball vs Tournament Aggregates).
- [ ] Run automated ingestion and inspect column distributions.
- [ ] Generate initial baseline ranking and push commit to GitHub.

### Stage 2: Deep Modeling & Validation (Nov 10-12)
- [ ] Calculate phase-specific scores (Powerplay, Middle Overs, Death 16–20).
- [ ] Apply **Age-Ceiling Runway Multipliers** (<20, 20-22, 23-24, 25+).
- [ ] Filter out statistical noise via sample-size thresholding.
- [ ] Cross-validate against recent domestic tournaments (Syed Mushtaq Ali, DPL, UP T20, TNPL).

### Stage 3: Squad Fit & Top 10 Quotas (Nov 13-14)
- [ ] Map candidates to the 5 RR tactical archetypes.
- [ ] Select balanced Top 10:
  * 3x Death-Overs Power Finishers
  * 3x Death Enforcer Seamers
  * 2x Middle-Overs Mystery/Wrist Spinners
  * 2x Dynamic Multi-Utility All-Rounders
- [ ] Formulate estimated auction bidding brackets (₹30L base price steals vs ₹1.5Cr+ bidding targets).

### Stage 4: High-Impact Deliverables (Nov 15-16)
- [ ] **Dual-Delivery Strategy:**
  1. **Executive Pitch Deck (PDF/PPT):** 10–12 visual slides styled in Royals Pink & Blue.
  2. **Live Public Dashboard (Streamlit Cloud):** Free hosted web app with clickable player radars.
- [ ] Write detailed player scouting dossiers with tactical justifications for RR.

### Stage 5: Final Audit & Submission (Nov 17-18)
- [ ] Verify uncapped eligibility and exact official ages for all 10 players.
- [ ] Conduct slide-by-slide review against Unstop rubric.
- [ ] Submit on Unstop 24 hours prior to deadline (target: Nov 17 evening).
