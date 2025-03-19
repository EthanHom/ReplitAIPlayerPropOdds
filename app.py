import streamlit as st
import json
import pandas as pd
from utils.odds_calculator import calculate_edge, get_recommendation

def load_mock_data():
    """Load mock data from JSON files"""
    try:
        with open('data/mock_prizepicks.json', 'r') as f:
            prizepicks_data = json.load(f)
        with open('data/mock_pinnacle.json', 'r') as f:
            pinnacle_data = json.load(f)
        return prizepicks_data, pinnacle_data
    except FileNotFoundError:
        st.error("Error: Mock data files not found")
        return None, None
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format in mock data files")
        return None, None

def main():
    st.title("PrizePicks vs Pinnacle Odds Comparison")
    
    # Load data
    prizepicks_data, pinnacle_data = load_mock_data()
    
    if not prizepicks_data or not pinnacle_data:
        return

    # Create filters
    st.sidebar.header("Filters")
    
    # Get unique players
    all_players = list(set([prop['player'] for prop in prizepicks_data['props']]))
    selected_player = st.sidebar.selectbox("Select Player", all_players)
    
    # Get unique stat types for selected player
    stat_types = list(set([
        prop['stat_type'] for prop in prizepicks_data['props']
        if prop['player'] == selected_player
    ]))
    selected_stat = st.sidebar.selectbox("Select Stat Type", stat_types)

    # Find matching propositions
    prizepicks_prop = next(
        (prop for prop in prizepicks_data['props']
         if prop['player'] == selected_player and prop['stat_type'] == selected_stat),
        None
    )
    
    pinnacle_prop = next(
        (prop for prop in pinnacle_data['odds']
         if prop['player'] == selected_player and prop['stat_type'] == selected_stat),
        None
    )

    if prizepicks_prop and pinnacle_prop:
        st.header(f"{selected_player} - {selected_stat.title()}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("PrizePicks")
            st.write(f"Line: {prizepicks_prop['line']}")
            st.write(f"Type: {prizepicks_prop['over_under'].title()}")
            st.write("Fixed Odds: -120")

        with col2:
            st.subheader("Pinnacle")
            st.write(f"Line: {pinnacle_prop['line']}")
            st.write(f"Over Odds: {pinnacle_prop['over_odds']}")
            st.write(f"Under Odds: {pinnacle_prop['under_odds']}")

        # Calculate edge
        relevant_pinnacle_odds = (
            pinnacle_prop['over_odds'] if prizepicks_prop['over_under'] == 'over'
            else pinnacle_prop['under_odds']
        )
        
        edge = calculate_edge(prizepicks_prop['line'], relevant_pinnacle_odds)
        recommendation, status = get_recommendation(edge)
        
        st.markdown("---")
        st.subheader("Analysis")
        st.metric(
            label="Edge",
            value=f"{edge}%",
            delta=recommendation
        )
        
        st.info(f"Recommendation: {recommendation}")
        
    else:
        st.warning("No matching proposition found for selected criteria")

if __name__ == "__main__":
    main()
