"""Combine the creative metrics into a single raw score."""

import pandas as pd


def calculate_creative_indicator(creative_df):
    print("Calculating creative score...")
    df = creative_df.copy()

    df['creative_indicator_raw'] = (
        (df['xt_per_90'] * 12.0) +
        (df['sca_per_90'] * 0.8) +
        (df['carries_per_90'] * 0.2) +
        (df['deep_comps_per_90'] * 0.6) +
        (df['through_balls_per_90'] * 1.5)
    )
    return df