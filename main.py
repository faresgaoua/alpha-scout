"""Main entry point for the valuation workflow."""

import pandas as pd
import config
import data_engine
import master_valuation
from models import creative_yield, finishing_yield, defensive_yield, control_yield, creative_score, finishing_score, defensive_score, control_score

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 120)
pd.set_option('display.max_colwidth', 25)
pd.set_option('display.max_rows', 15)


def main():
    print("Starting valuation run...")

    team_matches = data_engine.fetch_matches()
    master_squad, player_minutes = data_engine.build_master_squad(team_matches)

    creative_df = creative_yield.calculate_creative_yield(team_matches, master_squad, player_minutes)
    creative_final = creative_score.calculate_creative_indicator(creative_df)

    finishing_df = finishing_yield.calculate_finishing_yield(team_matches, master_squad, player_minutes)
    finishing_final = finishing_score.calculate_finishing_indicator(finishing_df)

    defensive_df = defensive_yield.calculate_defensive_yield(team_matches, master_squad, player_minutes)
    defensive_final = defensive_score.calculate_defensive_indicator(defensive_df)

    control_df = control_yield.calculate_control_yield(team_matches, master_squad, player_minutes)
    control_final = control_score.calculate_control_indicator(control_df)

    master_portfolio = master_valuation.calculate_financial_fair_value(
        creative_final, finishing_final, defensive_final, control_final, master_squad
    )

    print("\nTop estimated values:")
    top_players = master_portfolio.sort_values(by='fair_market_value', ascending=False).head(10).copy()
    top_players['fair_market_value_millions'] = (top_players['fair_market_value'] / 1_000_000).round(1)
    display_columns = [
        'player_name', 'primary_position', 'age', 'fair_market_value_millions',
        'creative_indicator_raw', 'finishing_indicator_raw',
        'control_indicator_raw', 'defensive_indicator_raw'
    ]
    print(top_players[display_columns].to_string(index=False))


if __name__ == "__main__":
    main()