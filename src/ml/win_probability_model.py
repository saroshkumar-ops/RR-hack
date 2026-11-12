"""
Machine Learning Component 1: Win Probability Added (WPA) & Leverage Index Engine
Trains a predictive ML model to output P(Win | Match State) and calculates delivery-level Leverage Index.
"""
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import log_loss, roc_auc_score

class WinProbabilityModel:
    def __init__(self):
        self.model = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=31,
            min_samples_leaf=30,
            random_state=42
        )
        self.feature_cols = [
            'innings', 'balls_remaining', 'runs_needed',
            'wickets_in_hand', 'rrr', 'crr', 'cum_runs', 'overs_elapsed'
        ]
        self.is_trained = False

    def prepare_features(self, df_bbb: pd.DataFrame, df_matches: pd.DataFrame) -> pd.DataFrame:
        """Constructs match context and target labels for supervised training."""
        df = df_bbb.copy()

        # 1. Match outcome mapping
        match_winners = df_matches.set_index('match_id')['win_team_id'].to_dict()
        df['batting_team_won'] = (df['batting_team_id'] == df['match_id'].map(match_winners)).astype(int)

        # 2. Extras & runs physics
        et = df['extras_type'].values
        ex2 = df['extras_2_runs'].fillna(0).values
        is_wide = (et == 'wide')
        is_nb = (et == 'Overstep')
        is_bye_lb = np.isin(et, ['byes', 'legbyes', 'other'])

        extras = np.zeros(len(df))
        extras[is_wide] = 1 + ex2[is_wide]
        extras[is_nb] = 1 + ex2[is_nb]
        extras[is_bye_lb] = np.where(ex2[is_bye_lb] > 0, ex2[is_bye_lb], 1)

        df['delivery_runs'] = df['runs'] + extras
        df['is_legal'] = ~np.isin(et, ['wide', 'Overstep'])

        # 3. Cumulative state
        df['cum_runs'] = df.groupby(['match_id', 'innings'])['delivery_runs'].cumsum() - df['delivery_runs']
        df['cum_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum() - df['is_wicket'].astype(int)
        df['cum_legal_balls'] = df.groupby(['match_id', 'innings'])['is_legal'].cumsum() - df['is_legal'].astype(int)

        df['wickets_in_hand'] = 10 - df['cum_wickets']
        df['balls_remaining'] = np.maximum(120 - df['cum_legal_balls'], 0)
        df['overs_elapsed'] = df['cum_legal_balls'] / 6.0

        # CRR
        df['crr'] = np.where(df['overs_elapsed'] > 0, df['cum_runs'] / df['overs_elapsed'], 8.0)

        # Innings 2 Chase Context
        inn1_totals = df[df['innings'] == 1].groupby('match_id')['delivery_runs'].sum().to_dict()
        m_dict = df_matches.set_index('match_id')[['knock_out', 'stage', 'revised_target']].to_dict('index')

        targets = []
        for mid, inn in zip(df['match_id'], df['innings']):
            if inn == 2:
                rev = m_dict.get(mid, {}).get('revised_target')
                targets.append(rev if pd.notna(rev) and rev > 0 else inn1_totals.get(mid, 160) + 1)
            else:
                targets.append(0)

        df['target'] = targets
        df['runs_needed'] = np.where(df['innings'] == 2, np.maximum(df['target'] - df['cum_runs'], 0), 0)

        # RRR
        df['rrr'] = np.where(
            (df['innings'] == 2) & (df['balls_remaining'] > 0),
            np.clip(df['runs_needed'] / (df['balls_remaining'] / 6.0), 0, 36),
            0.0
        )
        return df

    def fit(self, df_features: pd.DataFrame):
        """Trains the ML model on 2nd innings chasing win probabilities."""
        chase_mask = (df_features['innings'] == 2) & (df_features['balls_remaining'] > 0)
        X = df_features.loc[chase_mask, self.feature_cols]
        y = df_features.loc[chase_mask, 'batting_team_won']

        self.model.fit(X, y)
        self.is_trained = True

        preds = self.model.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, preds)
        loss = log_loss(y, preds)
        self.train_auc = round(float(auc), 4)
        self.train_loss = round(float(loss), 4)
        print(f"[+] Trained Win Probability Model: AUC = {auc:.4f}, Log-Loss = {loss:.4f}")

    def compute_leverage_index(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Computes the Machine Learning Leverage Index (LI):
        Measures the gradient/spread in Win Probability across potential outcomes:
        P(Win | Wicket) vs P(Win | Dot Ball) vs P(Win | Six).
        """
        df = df_features.copy()
        chase_mask = (df['innings'] == 2) & (df['balls_remaining'] > 0)
        
        # Default baseline pressure
        pressure = np.full(len(df), 3.0)

        # Predict current state win prob
        current_p = self.model.predict_proba(df.loc[chase_mask, self.feature_cols])[:, 1]
        
        # State under potential Wicket
        w_state = df.loc[chase_mask, self.feature_cols].copy()
        w_state['wickets_in_hand'] = np.maximum(w_state['wickets_in_hand'] - 1, 0)
        w_state['balls_remaining'] = np.maximum(w_state['balls_remaining'] - 1, 0)
        w_state['overs_elapsed'] = w_state['overs_elapsed'] + (1.0 / 6.0)
        w_state['rrr'] = np.where(
            w_state['balls_remaining'] > 0,
            np.clip(w_state['runs_needed'] / (w_state['balls_remaining'] / 6.0), 0, 36),
            0.0
        )
        w_state['crr'] = np.where(w_state['overs_elapsed'] > 0, w_state['cum_runs'] / w_state['overs_elapsed'], 8.0)
        p_wicket = self.model.predict_proba(w_state)[:, 1]

        # State under potential Boundary (Six)
        b_state = df.loc[chase_mask, self.feature_cols].copy()
        b_state['runs_needed'] = np.maximum(b_state['runs_needed'] - 6, 0)
        b_state['cum_runs'] = b_state['cum_runs'] + 6
        b_state['balls_remaining'] = np.maximum(b_state['balls_remaining'] - 1, 0)
        b_state['overs_elapsed'] = b_state['overs_elapsed'] + (1.0 / 6.0)
        b_state['rrr'] = np.where(
            b_state['balls_remaining'] > 0,
            np.clip(b_state['runs_needed'] / (b_state['balls_remaining'] / 6.0), 0, 36),
            0.0
        )
        b_state['crr'] = np.where(b_state['overs_elapsed'] > 0, b_state['cum_runs'] / b_state['overs_elapsed'], 8.0)
        p_boundary = self.model.predict_proba(b_state)[:, 1]

        # Expected Swing (Max Win Prob Swing between boundary and wicket)
        # Scaled by 38.0 so the ~70th percentile of chase leverage aligns symmetrically with 6.5 cutoff
        swing = np.abs(p_boundary - p_wicket)
        pressure[chase_mask] = np.clip(swing * 38.0, 0.5, 10.0)

        # 1st Innings: Crisis + Death overs
        inn1_mask = (df['innings'] == 1)
        collapse = inn1_mask & (df['overs_elapsed'] <= 10.0) & (df['cum_wickets'] >= 3)
        death = inn1_mask & (df['overid'] >= 16)
        
        inn1_pressure = np.full(inn1_mask.sum(), 2.5)
        inn1_pressure += np.where(collapse[inn1_mask], 3.5 + df.loc[inn1_mask, 'cum_wickets'] * 0.8, 0)
        inn1_pressure += np.where(death[inn1_mask], 4.0 + (df.loc[inn1_mask, 'overid'] - 15) * 0.9, 0)
        pressure[inn1_mask] = np.clip(inn1_pressure, 1.0, 9.5)

        # Super overs
        pressure[df['innings'].isin([3, 4])] = 10.0

        df['ml_pressure_index'] = np.round(pressure, 2)
        df['is_high_pressure'] = df['ml_pressure_index'] >= 6.5
        return df
