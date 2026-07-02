"""Collect match data and build the squad table used by the valuation models."""

import pandas as pd
from statsbombpy import sb
import warnings
import config

warnings.filterwarnings("ignore", message="credentials were not supplied")


def fetch_matches():
    """Fetch all matches for the selected team."""
    matches = sb.matches(competition_id=config.COMP_ID, season_id=config.SEASON_ID)
    team_matches = matches[(matches['home_team'] == config.TEAM_NAME) | (matches['away_team'] == config.TEAM_NAME)]
    return team_matches


def build_master_squad(team_matches):
    """Build a squad table with minutes played and basic player metadata."""
    master_players = {}
    player_minutes = {}

    player_x_sum = {}
    player_x_count = {}
    player_positions = {}

    print(f"Preparing squad data for {config.TEAM_NAME}...")

    for match_id in team_matches['match_id']:
        lineups = sb.lineups(match_id=match_id)
        if config.TEAM_NAME in lineups:
            for _, row in lineups[config.TEAM_NAME].iterrows():
                master_players[row['player_id']] = row['player_name']

        events = sb.events(match_id=match_id)
        team_events = events[events['team'] == config.TEAM_NAME]

        for _, event in team_events.iterrows():
            pid = event.get('player_id')
            loc = event.get('location')
            pos = event.get('position')

            if pd.notna(pid):
                if isinstance(loc, list) and len(loc) >= 2:
                    player_x_sum[pid] = player_x_sum.get(pid, 0) + loc[0]
                    player_x_count[pid] = player_x_count.get(pid, 0) + 1

                if pd.notna(pos):
                    if pid not in player_positions:
                        player_positions[pid] = {}
                    player_positions[pid][pos] = player_positions[pid].get(pos, 0) + 1

        match_length = events['minute'].max()
        starters_event = events[(events['type'] == 'Starting XI') & (events['team'] == config.TEAM_NAME)]

        on_pitch = {}
        for _, event in starters_event.iterrows():
            tactics = event.get('tactics', {})
            for player in tactics.get('lineup', []):
                pid = player['player']['id']
                on_pitch[pid] = 0

        subs = events[(events['type'] == 'Substitution') & (events['team'] == config.TEAM_NAME)]
        for _, sub in subs.iterrows():
            sub_minute = sub['minute']
            player_off = sub['player_id']
            player_on = sub.get('substitution_replacement_id')

            if player_off in on_pitch:
                time_played = sub_minute - on_pitch[player_off]
                player_minutes[player_off] = player_minutes.get(player_off, 0) + time_played
                del on_pitch[player_off]

            if pd.notna(player_on):
                on_pitch[player_on] = sub_minute

        for pid, start_min in on_pitch.items():
            time_played = match_length - start_min
            player_minutes[pid] = player_minutes.get(pid, 0) + time_played

    player_avg_x = {}
    player_primary_pos = {}

    for pid in master_players.keys():
        if player_x_count.get(pid, 0) > 0:
            player_avg_x[pid] = player_x_sum[pid] / player_x_count[pid]
        else:
            player_avg_x[pid] = 0.0

        if pid in player_positions and player_positions[pid]:
            primary = max(player_positions[pid], key=player_positions[pid].get)
            player_primary_pos[pid] = primary
        else:
            player_primary_pos[pid] = 'Unknown'

    age_lookup = {
        'Lionel Andrés Messi Cuccittini': 33,
        'Gerard Piqué Bernabéu': 34,
        'Sergio Busquets i Burgos': 32,
        'Jordi Alba Ramos': 31,
        'Antoine Griezmann': 29,
        'Marc-André ter Stegen': 28,
        'Clément Lenglet': 25,
        'Sergi Roberto Carnicer': 28,
        'Frenkie de Jong': 23,
        'Ousmane Dembélé': 23,
        'Martin Braithwaite Christensen': 29,
        'Sergino Dest': 20,
        'Ronald Federico Araújo da Silva': 21,
        'Óscar Mingueza García': 21,
        'Pedro González López': 18
    }

    master_squad = pd.DataFrame({
        'player_id': list(master_players.keys()),
        'player_name': list(master_players.values())
    })

    master_squad['average_x_height'] = master_squad['player_id'].map(player_avg_x)
    master_squad['primary_position'] = master_squad['player_id'].map(player_primary_pos)
    master_squad['age'] = master_squad['player_name'].map(age_lookup).fillna(25).astype(int)

    print(f"Loaded {len(master_squad)} players.")
    return master_squad, player_minutes