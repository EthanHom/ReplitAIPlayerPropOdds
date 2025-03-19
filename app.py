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
        with open('data/mock_prizepicks.json', 'r') as f:
            prizepicks_data = json.load(f)
        with open('data/mock_pinnacle.json', 'r') as f:
            pinnacle_data = json.load(f)
        return prizepicks_data, pinnacle_data
    except Exception as e:
        st.error(f"Error loading mock data: {str(e)}")
        return None, None

def main():
    st.set_page_config(layout="wide")
    st.title("NBA Props Analyzer")

    # Add auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=False)
    if auto_refresh:
        st.experimental_rerun()

    # Load data
    prizepicks_data, pinnacle_data = load_data()

    if not prizepicks_data or not pinnacle_data:
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

            # Use fair odds for edge calculation
            relevant_fair_odds = fair_over if pp_prop['over_under'] == 'over' else fair_under
            edge = calculate_edge(pp_prop['line'], relevant_fair_odds)

            # Calculate implied probability
            implied_prob = american_to_probability(relevant_fair_odds) * 100
            recommendation, status = get_recommendation(edge)

            data_rows.append({
                'Track': '',  # Empty column for tracking
                'Player': pp_prop['player'],
                'O/U': pp_prop['over_under'].upper(),
                'Stat': f"{pp_prop['stat_type'].title()} {pp_prop['line']}",
                'Chance': f"{implied_prob:.1f}%",
                'PrizePicks': '-120',
                'Fair Odds': relevant_fair_odds,
                'Edge': f"{edge:.1f}%",
                'Status': status
            })

    if data_rows:
        df = pd.DataFrame(data_rows)

        # Style the dataframe
        def color_status(val):
            if val == 'success':
                return 'background-color: #90EE90'
            elif val == 'error':
                return 'background-color: #FFB6C6'
            elif val == 'warning':
                return 'background-color: #FFE5B4'
            return ''

        styled_df = df.style.apply(lambda x: ['background-color: #1E1E1E' for _ in x], axis=0)\
                          .apply(lambda x: [color_status(x['Status']) if i == 7 else '' for i in range(len(x))], axis=1)

        # Display the table
        st.dataframe(
            styled_df,
            hide_index=True,
            column_config={
                'Track': st.column_config.CheckboxColumn(default=False),
                'Edge': st.column_config.NumberColumn(format="%.1f%%"),
                'Status': None  # Hide status column used for styling
            },
            use_container_width=True
        )
    else:
        st.warning("No props found matching the selected criteria")

if __name__ == "__main__":
    main()