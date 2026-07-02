"""Combine finishing metrics into a raw score."""

import pandas as pd
import numpy as np


def calculate_finishing_indicator(finishing_df):
    df = finishing_df.copy()
    df['goals_per_90'] = (df['total_goals'] / df['total_minutes']) * 90

    positive_overperformance = np.maximum(df['xg_overperformance'], 0)
    adjusted_alpha = np.where(df['xg_overperformance'] > 0, np.sqrt(positive_overperformance), df['xg_overperformance'])

    df['finishing_indicator_raw'] = (
        (df['xg_per_90'] * 3.5) +
        (df['goals_per_90'] * 4.5) +
        (df['shots_per_90'] * 0.2) +
        (adjusted_alpha * 1.5)
    )
    return df