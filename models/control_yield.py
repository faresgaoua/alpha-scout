"""Build control and passing metrics from match events."""

import pandas as pd
from statsbombpy import sb
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def calculate_control_yield(team_matches, master_squad, player_minutes):
    print("Calculating control metrics...")

    player_miscontrols = {pid: 0 for pid in master_squad['player_id']}
    player_dispossessed = {pid: 0 for pid in master_squad['player_id']}
    player_incomplete_passes = {pid: 0 for pid in master_squad['player_id']}
    player_attempted_passes = {pid: 0 for pid in master_squad['player_id']}

    for match_id in team_matches['match_id']:
        events = sb.events(match_id=match_id)
        team_events = events[events['team'] == config.TEAM_NAME]

        for _, event in team_events.iterrows():
            pid = event.get('player_id')
            if pd.isna(pid) or pid not in player_miscontrols:
                continue

            ev_type = event['type']

            if ev_type == 'Miscontrol':
                player_miscontrols[pid] += 1
            elif ev_type == 'Dispossessed':
                player_dispossessed[pid] += 1
            elif ev_type == 'Pass':
                player_attempted_passes[pid] += 1
                if pd.notna(event.get('pass_outcome')):
                    player_incomplete_passes[pid] += 1

    df = master_squad[['player_id', 'player_name']].copy()
    df['total_minutes'] = df['player_id'].map(player_minutes).fillna(0)

    df['total_miscontrols'] = df['player_id'].map(player_miscontrols)
    df['total_dispossessed'] = df['player_id'].map(player_dispossessed)
    df['total_incomplete_passes'] = df['player_id'].map(player_incomplete_passes)
    df['total_attempted_passes'] = df['player_id'].map(player_attempted_passes)

    df = df[df['total_minutes'] >= 450].copy()

    goalkeepers = ['Marc-André ter Stegen', 'Norberto Murara Neto', 'Arnau Tenas Ureña', 'Ignacio Peña Sotorres']
    df = df[~df['player_name'].isin(goalkeepers)].copy()

    df['miscontrols_per_90'] = (df['total_miscontrols'] / df['total_minutes']) * 90
    df['dispossessed_per_90'] = (df['total_dispossessed'] / df['total_minutes']) * 90
    df['incomplete_passes_per_90'] = (df['total_incomplete_passes'] / df['total_minutes']) * 90
    df['passes_attempted_per_90'] = (df['total_attempted_passes'] / df['total_minutes']) * 90

    return df