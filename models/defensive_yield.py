"""Build defensive metrics from match events."""

import pandas as pd
from statsbombpy import sb
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def calculate_defensive_yield(team_matches, master_squad, player_minutes):
    """Calculate defensive volume, aerial wins, and emergency actions."""
    print("Computing defensive metrics...")

    player_recoveries = {pid: 0 for pid in master_squad['player_id']}
    player_interceptions = {pid: 0 for pid in master_squad['player_id']}
    player_tackles = {pid: 0 for pid in master_squad['player_id']}
    player_blocks = {pid: 0 for pid in master_squad['player_id']}
    player_clearances = {pid: 0 for pid in master_squad['player_id']}
    player_aerial_wons = {pid: 0 for pid in master_squad['player_id']}
    player_last_man = {pid: 0 for pid in master_squad['player_id']}

    for match_id in team_matches['match_id']:
        events = sb.events(match_id=match_id)
        team_events = events[events['team'] == config.TEAM_NAME]

        for _, event in team_events.iterrows():
            pid = event.get('player_id')
            if pd.isna(pid) or pid not in player_recoveries:
                continue

            ev_type = event['type']
            loc = event.get('location')
            is_in_danger_zone = isinstance(loc, list) and len(loc) >= 1 and loc[0] <= 30.0

            if ev_type == 'Block':
                player_blocks[pid] += 1
                if is_in_danger_zone and (event.get('block_save_to_post') == True or event.get('block_offensive') == True):
                    player_last_man[pid] += 1

            elif ev_type == 'Ball Recovery':
                player_recoveries[pid] += 1
            elif ev_type == 'Interception':
                player_interceptions[pid] += 1
            elif ev_type == 'Clearance':
                player_clearances[pid] += 1

            elif ev_type == 'Duel':
                duel_type = event.get('duel_type')
                duel_outcome = event.get('duel_outcome')

                if duel_type == 'Tackle' and duel_outcome in ['Success', 'Won']:
                    player_tackles[pid] += 1
                    if is_in_danger_zone and event.get('counterpress') != True:
                        player_last_man[pid] += 1

                elif duel_type == 'Aerial Lost':
                    continue

            if event.get('duel_type') == 'Aerial' or pd.notna(event.get('aerial_won')):
                if event.get('duel_outcome') in ['Success', 'Won'] or event.get('aerial_won') == True:
                    player_aerial_wons[pid] += 1

    df = master_squad[['player_id', 'player_name', 'primary_position']].copy()
    df['total_minutes'] = df['player_id'].map(player_minutes).fillna(0)

    df['total_recoveries'] = df['player_id'].map(player_recoveries)
    df['total_interceptions'] = df['player_id'].map(player_interceptions)
    df['total_tackles'] = df['player_id'].map(player_tackles)
    df['total_blocks'] = df['player_id'].map(player_blocks)
    df['total_clearances'] = df['player_id'].map(player_clearances)
    df['total_aerial_won'] = df['player_id'].map(player_aerial_wons)
    df['total_last_man'] = df['player_id'].map(player_last_man)

    df = df[df['total_minutes'] >= 450].copy()

    metrics = ['recoveries', 'interceptions', 'tackles', 'blocks', 'clearances', 'aerial_won', 'last_man']
    for m in metrics:
        df[f'{m}_per_90'] = (df[f'total_{m}'] / df['total_minutes']) * 90

    return df[[
        'player_id', 'player_name', 'primary_position', 'total_minutes',
        'recoveries_per_90', 'interceptions_per_90', 'tackles_per_90',
        'blocks_per_90', 'clearances_per_90', 'aerial_won_per_90', 'last_man_per_90'
    ]]