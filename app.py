import streamlit as st
import json
import pandas as pd
from utils.odds_calculator import calculate_edge, get_recommendation, american_to_probability, remove_vig
from utils.scraper import fetch_prizepicks_props, fetch_pinnacle_odds

def load_data():
    """Load live data from PrizePicks and Pinnacle"""
    try:
        prizepicks_data = fetch_prizepicks_props()
        pinnacle_data = fetch_pinnacle_odds()
        return prizepicks_data, pinnacle_data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Fallback to mock data for development
        return load_mock_data()

def load_mock_data():
    """Load mock data from JSON files"""
    try:
        st.write("Loading mock data...")  # Debug log
        with open('data/mock_prizepicks.json', 'r') as f:
            prizepicks_data = json.load(f)
            st.write(f"PrizePicks data loaded: {len(prizepicks_data['props'])} props found")  # Debug log

        with open('data/mock_pinnacle.json', 'r') as f:
            pinnacle_data = json.load(f)
            st.write(f"Pinnacle data loaded: {len(pinnacle_data['odds'])} odds found")  # Debug log

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

    # Display raw data for debugging
    with st.expander("Debug Data"):
        st.write("PrizePicks Data:", prizepicks_data)
        st.write("Pinnacle Data:", pinnacle_data)

    # Create filters in sidebar
    st.sidebar.header("Filters")

    # Filter by stat type
    all_stat_types = list(set([prop['stat_type'] for prop in prizepicks_data['props']]))
    st.write(f"Available stat types: {all_stat_types}")  # Debug log

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

            # Use fair odds for edge calculation
            relevant_fair_odds = fair_over if pp_prop['over_under'] == 'over' else fair_under
            edge = calculate_edge(pp_prop['line'], relevant_fair_odds)

            # Calculate implied probability
            implied_prob = american_to_probability(relevant_fair_odds) * 100
            recommendation, status = get_recommendation(edge)

            data_rows.append({
                'Track': False,  # Checkbox column
                'Player': pp_prop['player'],
                'Team': pp_prop['team'],
                'Opponent': pp_prop['opponent'],
                'O/U': pp_prop['over_under'].upper(),
                'Stat': f"{pp_prop['stat_type']} {pp_prop['line']}",
                'Chance': f"{implied_prob:.1f}%",
                'PrizePicks': '-120',
                'Fair Odds': relevant_fair_odds,
                'Edge': edge,
                'Status': status
            })

    if data_rows:
        df = pd.DataFrame(data_rows)

        # Configure column settings
        column_config = {
            'Track': st.column_config.CheckboxColumn(default=False),
            'Edge': st.column_config.NumberColumn(format="%.1f%%"),
            'Fair Odds': st.column_config.NumberColumn(format="%.0f"),
            'Status': None  # Hide status column used for styling
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
        st.write("Debug info:")
        st.write(f"Selected stats: {selected_stats}")
        st.write(f"Number of props: {len(prizepicks_data['props'])}")

if __name__ == "__main__":
    main()