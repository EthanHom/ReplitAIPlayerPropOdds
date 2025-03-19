import streamlit as st
import json
import pandas as pd
from utils.odds_calculator import calculate_edge, get_recommendation, american_to_probability, remove_vig

def load_mock_data():
    """Load mock data from JSON files"""
    try:
        with open('data/mock_prizepicks.json', 'r') as f:
            prizepicks_data = json.load(f)

        with open('data/mock_pinnacle.json', 'r') as f:
            pinnacle_data = json.load(f)

        return prizepicks_data, pinnacle_data
    except Exception as e:
        st.error(f"Error loading mock data: {str(e)}")
        return None, None

def main():
    # Page config
    st.set_page_config(layout="wide", page_title="NBA Props Analyzer")

    st.title("NBA Props Analyzer")

    # Load data
    prizepicks_data, pinnacle_data = load_mock_data()

    if not prizepicks_data or not pinnacle_data:
        st.error("Failed to load data")
        return

    # Create filters in sidebar
    st.sidebar.header("Filters")

    # Filter by stat type
    all_stat_types = list(set([prop['stat_type'] for prop in prizepicks_data['props']]))
    selected_stats = st.sidebar.multiselect(
        "Select Stat Types",
        all_stat_types,
        default=all_stat_types
    )

    # Create the main table
    data_rows = []
    for pp_prop in prizepicks_data['props']:
        if pp_prop['stat_type'] not in selected_stats:
            continue

        # Find matching Pinnacle prop
        pinn_prop = next(
            (prop for prop in pinnacle_data['odds']
             if prop['player'] == pp_prop['player'] and prop['stat_type'] == pp_prop['stat_type']),
            None
        )

        if pinn_prop:
            # Calculate fair odds (no vig)
            fair_over, fair_under = remove_vig(pinn_prop['over_odds'], pinn_prop['under_odds'])

            # Convert fair odds to probabilities
            fair_over_prob = american_to_probability(fair_over) * 100
            fair_under_prob = american_to_probability(fair_under) * 100

            # Get the relevant probability based on over/under selection
            fair_prob = fair_over_prob if pp_prop['over_under'].lower() == 'over' else fair_under_prob
            relevant_fair_odds = fair_over if pp_prop['over_under'].lower() == 'over' else fair_under

            # Calculate edge using fair odds
            edge = calculate_edge(pp_prop['line'], relevant_fair_odds)

            data_rows.append({
                'Track': False,  # Checkbox column
                'Player': pp_prop['player'],
                'Team': pp_prop['team'],
                'Opponent': pp_prop['opponent'],
                'O/U': pp_prop['over_under'].upper(),
                'Stat': f"{pp_prop['stat_type']} {pp_prop['line']}",
                'PrizePicks': '-120',
                'Over': pinn_prop['over_odds'],
                'Under': pinn_prop['under_odds'],
                'Fair %': fair_prob,
                'Edge': edge
            })

    if data_rows:
        df = pd.DataFrame(data_rows)

        # Configure column settings
        column_config = {
            'Track': st.column_config.CheckboxColumn(default=False),
            'Fair %': st.column_config.NumberColumn(format="%.1f%%"),
            'Edge': st.column_config.NumberColumn(format="%.1f%%"),
            'Over': st.column_config.NumberColumn(format="%.0f"),
            'Under': st.column_config.NumberColumn(format="%.0f")
        }

        # Display the table
        st.dataframe(
            df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No props found matching the selected criteria")

if __name__ == "__main__":
    main()