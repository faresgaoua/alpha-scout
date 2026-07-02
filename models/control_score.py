"""
models/control_score.py
Alpha Scout Project: Absolute Control Scoring Core
--------------------------------------------------
Calculates asset possession security using raw volume and execution density.
"""

import pandas as pd
import numpy as np

def calculate_control_indicator(control_df):
    df = control_df.copy()
    
    df['pass_completion_rate'] = 1 - (df['total_incomplete_passes'] / df['total_attempted_passes'].replace(0, 1))
    
    # Utilisation d'une pénalisation logarithmique pour le déchet technique 
    # Évite l'effondrement du score si un joueur prend des risques créatifs
    turnover_penalty = np.log1p(df['miscontrols_per_90'] + df['dispossessed_per_90']) * 3.5
    
    df['control_indicator_raw'] = (
        (df['passes_attempted_per_90'] * (df['pass_completion_rate'] ** 1.8)) - turnover_penalty
    )
    
    df['control_indicator_raw'] = df['control_indicator_raw'].clip(lower=0) * 0.15
    return df