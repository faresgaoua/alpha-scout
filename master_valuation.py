"""Estimate fair market values from the core performance indicators."""

import pandas as pd
import numpy as np

MARKET_FACTOR_PRICES = {
    'creative_unit': 4500000,
    'finishing_unit': 5500000,
    'control_unit': 2200000,
    'defensive_unit': 2500000
}

POSITION_BETAS = {
    'Center Forward': {'creative': 0.7, 'finishing': 1.0, 'control': 0.6, 'defensing': 0.1},
    'Left Wing': {'creative': 0.9, 'finishing': 0.8, 'control': 0.7, 'defensing': 0.2},
    'Right Wing': {'creative': 0.9, 'finishing': 0.8, 'control': 0.7, 'defensing': 0.2},
    'Center Attacking Midfield': {'creative': 1.0, 'finishing': 0.6, 'control': 0.9, 'defensing': 0.3},
    'Left Center Midfield': {'creative': 0.8, 'finishing': 0.3, 'control': 1.0, 'defensing': 0.6},
    'Right Center Midfield': {'creative': 0.8, 'finishing': 0.3, 'control': 1.0, 'defensing': 0.6},
    'Center Defensive Midfield': {'creative': 0.6, 'finishing': 0.1, 'control': 0.9, 'defensing': 1.0},
    'Left Back': {'creative': 0.6, 'finishing': 0.1, 'control': 0.7, 'defensing': 0.8},
    'Right Back': {'creative': 0.6, 'finishing': 0.1, 'control': 0.7, 'defensing': 0.8},
    'Center Back': {'creative': 0.2, 'finishing': 0.0, 'control': 0.5, 'defensing': 1.0},
    'Right Center Back': {'creative': 0.2, 'finishing': 0.0, 'control': 0.5, 'defensing': 1.0},
    'Left Center Back': {'creative': 0.2, 'finishing': 0.0, 'control': 0.5, 'defensing': 1.0},
    'Left Center Forward': {'creative': 0.8, 'finishing': 0.8, 'control': 0.6, 'defensing': 0.2},
    'Goalkeeper': {'creative': 0.1, 'finishing': 0.0, 'control': 0.3, 'defensing': 1.0}
}


def _get_age_multiplier(age, total_production):
    """Reduce value for older players and protect elite players slightly."""
    is_elite_asset = total_production > 22.0

    if age <= 25:
        return float(1.35 - (age - 18) * 0.05)
    elif 26 <= age <= 30:
        return 1.00
    else:
        standard_decay = float(1.00 - (age - 30) * 0.12)
        floor = 0.75 if is_elite_asset else 0.15
        return float(max(floor, standard_decay))


def _get_minutes_multiplier(minutes, max_squad_minutes):
    """Scale value by the share of available minutes played."""
    minute_ratio = minutes / max_squad_minutes
    return float(min(1.0, np.power(minute_ratio / 0.55, 1.1)))


def calculate_financial_fair_value(creative, finishing, defensive, control, master_squad):
    print("Calculating estimated values...")

    df = creative[['player_name', 'creative_indicator_raw', 'total_minutes']].copy()
    df = df.merge(finishing[['player_name', 'finishing_indicator_raw']], on='player_name', how='left')
    df = df.merge(defensive[['player_name', 'defensive_indicator_raw']], on='player_name', how='left')
    df = df.merge(control[['player_name', 'control_indicator_raw']], on='player_name', how='left')

    df = df.merge(master_squad[['player_name', 'primary_position', 'age']], on='player_name', how='left')
    df = df.fillna(0)

    df['finishing_indicator_raw'] = df['finishing_indicator_raw'].clip(lower=0)
    df['control_indicator_raw'] = df['control_indicator_raw'].clip(lower=0)

    max_squad_minutes = df['total_minutes'].max()

    fair_values = []
    age_mults = []
    min_mults = []

    for _, row in df.iterrows():
        pos = row['primary_position']
        age = int(row['age'])
        mins = row['total_minutes']

        betas = POSITION_BETAS.get(pos, {'creative': 0.5, 'finishing': 0.5, 'control': 0.5, 'defensing': 0.5})

        r_creative = row['creative_indicator_raw']
        r_finishing = row['finishing_indicator_raw']
        r_control = row['control_indicator_raw']
        r_defensing = row['defensive_indicator_raw']

        v_creative = r_creative * MARKET_FACTOR_PRICES['creative_unit'] * betas['creative']
        v_finishing = r_finishing * MARKET_FACTOR_PRICES['finishing_unit'] * betas['finishing']
        v_control = r_control * MARKET_FACTOR_PRICES['control_unit'] * betas['control']
        v_defense = r_defensing * MARKET_FACTOR_PRICES['defensive_unit'] * betas['defensing']

        intrinsic_value = v_creative + v_finishing + v_control + v_defense

        total_production = r_creative + r_finishing + r_control + r_defensing

        if total_production > 16.0:
            scarcity_premium = 1.0 + min(0.45, (total_production - 16.0) * 0.06)
            intrinsic_value *= scarcity_premium

        m_age = _get_age_multiplier(age, total_production)
        m_mins = _get_minutes_multiplier(mins, max_squad_minutes)

        risk_adjusted_value = intrinsic_value * m_age * m_mins

        fair_values.append(risk_adjusted_value)
        age_mults.append(m_age)
        min_mults.append(m_mins)

    df['age_multiplier'] = age_mults
    df['minutes_multiplier'] = min_mults
    df['fair_market_value'] = fair_values

    return df.sort_values(by='fair_market_value', ascending=False)[[
        'player_name', 'primary_position', 'age', 'total_minutes', 'fair_market_value',
        'age_multiplier', 'minutes_multiplier', 'creative_indicator_raw',
        'finishing_indicator_raw', 'control_indicator_raw', 'defensive_indicator_raw'
    ]]