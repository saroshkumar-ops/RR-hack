"""
Machine Learning Component 4: Unsupervised K-Means Clustering for Pressure Archetypes
Segments players into distinct tactical clutch identities based on standardized feature embeddings.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def cluster_batter_archetypes(df_bat: pd.DataFrame) -> pd.DataFrame:
    """
    Applies K-Means clustering (k=3) on qualified batters using:
    - bayes_hp_rae (scoring above par under pressure)
    - bayes_clutch_delta (elevation over normal baseline)
    - hp_boundary_pct (boundary reliance)
    - bayes_survival (wicket preservation)
    """
    df = df_bat.copy()
    features = ['bayes_hp_rae', 'bayes_clutch_delta', 'hp_boundary_pct', 'bayes_survival']
    
    if len(df) < 5:
        df['ml_archetype'] = 'Clutch Batter'
        return df

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features].fillna(0))

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(X_scaled)

    # Identify cluster centroids in original space to assign meaningful cricket labels
    centers = df.groupby('cluster_id')[features].mean()
    
    # Highest RAE + Boundary % -> "Elite Power Accelerator"
    # Highest Survival + Positive RAE -> "Ice-Cold Chase Anchor"
    # Remaining -> "Situational Clutch Finisher"
    accel_cluster = centers['bayes_hp_rae'].idxmax()
    remaining = [c for c in centers.index if c != accel_cluster]
    anchor_cluster = centers.loc[remaining, 'bayes_survival'].idxmax()
    finisher_cluster = [c for c in remaining if c != anchor_cluster][0]

    label_map = {
        accel_cluster: "Elite Pressure Accelerator",
        anchor_cluster: "Ice-Cold Chase Anchor",
        finisher_cluster: "High-Leverage Finisher"
    }
    df['ml_archetype'] = df['cluster_id'].map(label_map)
    return df

def cluster_bowler_archetypes(df_bowl: pd.DataFrame) -> pd.DataFrame:
    """
    Applies K-Means clustering (k=3) on qualified bowlers using:
    - bayes_hp_rsae (economy suppression vs phase par)
    - bayes_wkt_rate (wicket-taking frequency under pressure)
    - bayes_dot_pct (dot ball choke ability)
    """
    df = df_bowl.copy()
    features = ['bayes_hp_rsae', 'bayes_wkt_rate', 'bayes_dot_pct']

    if len(df) < 5:
        df['ml_archetype'] = 'Clutch Bowler'
        return df

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features].fillna(0))

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['cluster_id'] = kmeans.fit_predict(X_scaled)

    centers = df.groupby('cluster_id')[features].mean()

    # Highest RSAE + Dot % -> "Run-Choking Squeeze Specialist"
    # Highest Wicket Rate -> "Death/Clutch Wicket Hunter"
    # Remaining -> "All-Phase Two-Way Enforcer"
    squeeze_cluster = centers['bayes_hp_rsae'].idxmax()
    remaining = [c for c in centers.index if c != squeeze_cluster]
    hunter_cluster = centers.loc[remaining, 'bayes_wkt_rate'].idxmax()
    enforcer_cluster = [c for c in remaining if c != hunter_cluster][0]

    label_map = {
        squeeze_cluster: "Run-Choking Squeeze Specialist",
        hunter_cluster: "Clutch Wicket Hunter",
        enforcer_cluster: "Balanced Pressure Enforcer"
    }
    df['ml_archetype'] = df['cluster_id'].map(label_map)
    return df
