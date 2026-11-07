# Data Directory

### Instructions for Nov 8 (Data Pack Release)
1. Log into your **Unstop** account and go to **SupeRR Selector Season 2**.
2. Click the **"Brief / Case"** button to download Rajasthan Royals' official proprietary data pack.
3. Place the downloaded files (CSV / Excel format) into this directory (`data/raw/`).
4. The preprocessing pipeline and Streamlit dashboard will automatically detect and ingest files placed here.

### Expected Data Schemas
The data typically contains:
- **Player Details**: Name, Age / DOB, State Team / Franchise, Primary Role, Batting Hand, Bowling Style.
- **Batting Stats**: Matches, Innings, Runs, Balls Faced, Strike Rate, Average, Boundaries (4s & 6s), Dot Ball %, Phase breakdowns (Powerplay, Middle, Death), Splits vs Pace/Spin.
- **Bowling Stats**: Matches, Overs, Runs Conceded, Wickets, Economy, Strike Rate, Dot Ball %, Phase Economy (PP, Middle, Death), Yorker execution.
