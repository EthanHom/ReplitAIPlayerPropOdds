import numpy as np

def american_to_probability(american_odds):
    """Convert American odds to probability"""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)

def calculate_edge(prizepicks_line, pinnacle_odds):
    """Calculate the edge between PrizePicks and Pinnacle odds"""
    # PrizePicks uses a -120 implied probability for all bets
    prizepicks_probability = american_to_probability(-120)
    
    # Convert Pinnacle odds to probability
    pinnacle_probability = american_to_probability(pinnacle_odds)
    
    # Calculate the edge (difference in probabilities)
    edge = (prizepicks_probability - pinnacle_probability) * 100
    
    return round(edge, 2)

def get_recommendation(edge):
    """Get a recommendation based on the calculated edge"""
    if edge > 5:
        return "Strong Value", "success"
    elif edge > 2:
        return "Slight Value", "info"
    elif edge < -5:
        return "Poor Value", "error"
    elif edge < -2:
        return "Below Average Value", "warning"
    else:
        return "Fair Value", "primary"
