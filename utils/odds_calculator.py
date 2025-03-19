import numpy as np

def american_to_probability(american_odds):
    """Convert American odds to probability"""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)

def probability_to_american(probability):
    """Convert probability to American odds"""
    if probability >= 0.5:
        return -(probability * 100) / (1 - probability)
    else:
        return (100 - probability * 100) / probability

def remove_vig(over_odds, under_odds):
    """Calculate no-vig fair odds"""
    # Convert odds to probabilities
    over_prob = american_to_probability(over_odds)
    under_prob = american_to_probability(under_odds)

    # Remove the vig
    total_probability = over_prob + under_prob
    fair_over_prob = over_prob / total_probability
    fair_under_prob = under_prob / total_probability

    # Convert back to American odds
    fair_over_odds = probability_to_american(fair_over_prob)
    fair_under_odds = probability_to_american(fair_under_prob)

    return round(fair_over_odds), round(fair_under_odds)

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