"""Build finishing metrics from shot data."""

import pandas as pd
import numpy as np
from statsbombpy import sb
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def calculate_finishing_yield(team_matches, master_squad, player_minutes):
    """Calculate finishing metrics across the squad."""
    print("Computing finishing metrics...")

    player_shots = {pid: 0 for pid in master_squad['player_id']}
    player_goals = {pid: 0 for pid in master_squad['player_id']}
    player_xg = {pid: 0.0 for pid in master_squad['player_id']}
    player_sot = {pid: 0 for pid in master_squad['player_id']}
    player_first_time = {pid: 0 for pid in master_squad['player_id']}

    for match_id in team_matches['match_id']:
        events = sb.events(match_id=match_id)
        shots = events[(events['team'] == config.TEAM_NAME) & (events['type'] == 'Shot')]

        for _, shot in shots.iterrows():
            pid = shot['player_id']
            if pid not in player_shots:
                continue

            player_shots[pid] += 1

            xg_val = shot.get('shot_statsbomb_xg', 0)
            if pd.notna(xg_val):
                player_xg[pid] += xg_val

            outcome = shot.get('shot_outcome', '')
            if outcome == 'Goal':
                player_goals[pid] += 1
                player_sot[pid] += 1
            elif outcome in ['Saved', 'Saved Twice', 'Saved to Post']:
                player_sot[pid] += 1

            if shot.get('shot_first_time') == True:
                player_first_time[pid] += 1

    df = master_squad[['player_id', 'player_name']].copy()
    df['total_minutes'] = df['player_id'].map(player_minutes).fillna(0)

    df['total_shots'] = df['player_id'].map(player_shots)
    df['total_goals'] = df['player_id'].map(player_goals)
    df['total_xg'] = df['player_id'].map(player_xg)
    df['total_sot'] = df['player_id'].map(player_sot)
    df['first_time_shots'] = df['player_id'].map(player_first_time)

    df = df[df['total_minutes'] >= 450].copy()

    df['shots_per_90'] = (df['total_shots'] / df['total_minutes']) * 90
    df['xg_per_90'] = (df['total_xg'] / df['total_minutes']) * 90
    df['xg_overperformance'] = df['total_goals'] - df['total_xg']
    df['sot_percentage'] = np.where(df['total_shots'] > 0, (df['total_sot'] / df['total_shots']) * 100, 0)
    df['first_time_shots_per_90'] = (df['first_time_shots'] / df['total_minutes']) * 90

    return df[[
        'player_id', 'player_name', 'total_minutes', 'total_goals',
        'shots_per_90', 'xg_per_90', 'xg_overperformance',
        'sot_percentage', 'first_time_shots_per_90'
    ]]