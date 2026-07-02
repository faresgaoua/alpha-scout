"""Convert defensive metrics into a single raw score."""

import pandas as pd


def calculate_defensive_indicator(defensive_df):
    """Score defenders differently depending on their position."""
    print("Calculating defensive score...")
    df = defensive_df.copy()

    if 'aerial_won_per_90' not in df.columns:
        df['aerial_won_per_90'] = df['clearances_per_90'] * 0.6

    df['defensive_indicator_raw'] = 0.0

    for idx, row in df.iterrows():
        pos = row.get('primary_position', 'Unknown')

        rec = row['recoveries_per_90']
        inter = row['interceptions_per_90']
        tack = row['tackles_per_90']
        block = row['blocks_per_90']
        aer = row['aerial_won_per_90']
        clear = row['clearances_per_90']

        if 'Center Back' in pos or 'Defensive Midfield' in pos:
            raw_score = (
                (rec * 0.3) +
                (inter * 1.0) +
                (tack * 1.0) +
                (block * 1.2) +
                (aer * 1.4) +
                (clear * 0.3) +
                (row.get('last_man_per_90', 0) * 4.0)
            )
            stoppeur_ratio = (tack + block) / max(rec, 1)
            if stoppeur_ratio > 0.5:
                raw_score *= 1.25

        elif 'Back' in pos or 'Wing' in pos:
            raw_score = (
                (rec * 1.2) +
                (inter * 1.4) +
                (tack * 1.2) +
                (block * 0.6) +
                (aer * 0.4) +
                (clear * 0.2)
            )

        else:
            raw_score = (
                (rec * 0.8) +
                (inter * 0.8) +
                (tack * 0.8) +
                (block * 0.4) +
                (aer * 0.4) +
                (clear * 0.1)
            )

        df.at[idx, 'defensive_indicator_raw'] = raw_score

    return df