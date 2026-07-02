"""Create creative output metrics from match events."""

import pandas as pd
import numpy as np
from statsbombpy import sb
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

xt_grid = np.array([
    [0.0035, 0.0038, 0.0044, 0.0049, 0.0057, 0.0067, 0.0084, 0.0099, 0.0121, 0.0145, 0.0175, 0.0199, 0.0245, 0.0298, 0.0354, 0.0401],
    [0.0039, 0.0042, 0.0049, 0.0055, 0.0064, 0.0076, 0.0095, 0.0113, 0.0138, 0.0166, 0.0199, 0.0228, 0.0279, 0.0340, 0.0405, 0.0458],
    [0.0045, 0.0049, 0.0057, 0.0065, 0.0076, 0.0091, 0.0114, 0.0136, 0.0166, 0.0201, 0.0241, 0.0276, 0.0337, 0.0411, 0.0489, 0.0553],
    [0.0052, 0.0057, 0.0066, 0.0075, 0.0089, 0.0107, 0.0135, 0.0162, 0.0198, 0.0241, 0.0289, 0.0331, 0.0404, 0.0494, 0.0588, 0.0664],
    [0.0058, 0.0064, 0.0074, 0.0085, 0.0101, 0.0123, 0.0155, 0.0187, 0.0230, 0.0280, 0.0337, 0.0387, 0.0471, 0.0577, 0.0687, 0.0776],
    [0.0063, 0.0070, 0.0081, 0.0094, 0.0112, 0.0137, 0.0174, 0.0211, 0.0260, 0.0317, 0.0383, 0.0441, 0.0538, 0.0661, 0.0788, 0.0891],
    [0.0063, 0.0070, 0.0081, 0.0094, 0.0112, 0.0137, 0.0174, 0.0211, 0.0260, 0.0317, 0.0383, 0.0441, 0.0538, 0.0661, 0.0788, 0.0891],
    [0.0058, 0.0064, 0.0074, 0.0085, 0.0101, 0.0123, 0.0155, 0.0187, 0.0230, 0.0280, 0.0337, 0.0387, 0.0471, 0.0577, 0.0687, 0.0776],
    [0.0052, 0.0057, 0.0066, 0.0075, 0.0089, 0.0107, 0.0135, 0.0162, 0.0198, 0.0241, 0.0289, 0.0331, 0.0404, 0.0494, 0.0588, 0.0664],
    [0.0045, 0.0049, 0.0057, 0.0065, 0.0076, 0.0091, 0.0114, 0.0136, 0.0166, 0.0201, 0.0241, 0.0276, 0.0337, 0.0411, 0.0489, 0.0553],
    [0.0039, 0.0042, 0.0049, 0.0055, 0.0064, 0.0076, 0.0095, 0.0113, 0.0138, 0.0166, 0.0199, 0.0228, 0.0279, 0.0340, 0.0405, 0.0458],
    [0.0035, 0.0038, 0.0044, 0.0049, 0.0057, 0.0067, 0.0084, 0.0099, 0.0121, 0.0145, 0.0175, 0.0199, 0.0245, 0.0298, 0.0354, 0.0401]
])


def get_xt_value(x, y):
    """Map pitch coordinates to the expected-threat grid."""
    col = int(min(x // (120 / 16), 15))
    row = int(min(y // (80 / 12), 11))
    return xt_grid[row, col]


def calculate_creative_yield(team_matches, master_squad, player_minutes):
    """Calculate creative metrics from passes and carries."""
    print("Computing creative metrics...")

    player_xt = {pid: 0 for pid in master_squad['player_id']}
    player_sca = {pid: 0 for pid in master_squad['player_id']}
    player_prog_carries = {pid: 0 for pid in master_squad['player_id']}
    player_deep_comps = {pid: 0 for pid in master_squad['player_id']}
    player_through_balls = {pid: 0 for pid in master_squad['player_id']}

    for match_id in team_matches['match_id']:
        events = sb.events(match_id=match_id)
        team_events = events[events['team'] == config.TEAM_NAME]

        passes = team_events[(team_events['type'] == 'Pass')]
        carries = team_events[(team_events['type'] == 'Carry')]

        for _, p in passes.iterrows():
            pid = p['player_id']
            if pid not in player_xt:
                continue

            if pd.isna(p.get('pass_outcome')):
                start_x, start_y = p['location']
                end_x, end_y = p['pass_end_location']
                xt_delta = get_xt_value(end_x, end_y) - get_xt_value(start_x, start_y)
                if xt_delta > 0:
                    player_xt[pid] += xt_delta

                if start_x < 100 and end_x >= 100:
                    player_deep_comps[pid] += 1

                if 'pass_through_ball' in team_events.columns and p.get('pass_through_ball') == True:
                    player_through_balls[pid] += 1

            if 'pass_shot_assist' in team_events.columns and p.get('pass_shot_assist') == True:
                player_sca[pid] += 1

        for _, carry in carries.iterrows():
            pid = carry['player_id']
            if pid in player_prog_carries:
                start_loc = carry.get('location')
                end_loc = carry.get('carry_end_location')

                if isinstance(start_loc, list) and isinstance(end_loc, list):
                    start_x = start_loc[0]
                    end_x = end_loc[0]

                    if end_x - start_x >= 10:
                        player_prog_carries[pid] += 1

    creative_df = master_squad[['player_id', 'player_name']].copy()
    creative_df['total_minutes'] = creative_df['player_id'].map(player_minutes).fillna(0)

    creative_df['total_xt'] = creative_df['player_id'].map(player_xt)
    creative_df['total_sca'] = creative_df['player_id'].map(player_sca)
    creative_df['total_carries'] = creative_df['player_id'].map(player_prog_carries)
    creative_df['total_deep_comps'] = creative_df['player_id'].map(player_deep_comps)
    creative_df['total_through_balls'] = creative_df['player_id'].map(player_through_balls)

    creative_df = creative_df[creative_df['total_minutes'] >= 900].copy()

    metrics = ['xt', 'sca', 'carries', 'deep_comps', 'through_balls']
    for m in metrics:
        creative_df[f'{m}_per_90'] = (creative_df[f'total_{m}'] / creative_df['total_minutes']) * 90

    return creative_df[['player_id', 'player_name', 'total_minutes', 'xt_per_90', 'sca_per_90', 'carries_per_90', 'deep_comps_per_90', 'through_balls_per_90']]
