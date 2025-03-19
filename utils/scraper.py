import trafilatura
import json
import requests
from datetime import datetime
import time
import os
from bs4 import BeautifulSoup

def fetch_prizepicks_props():
    """
    Scrape live NBA props from PrizePicks website.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        url = "https://app.prizepicks.com/board"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extract the props data from the page
        props = []
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all NBA prop containers
        prop_containers = soup.find_all('div', {'class': 'projection'})

        for container in prop_containers:
            # Only process NBA props
            sport_tag = container.find('div', {'class': 'sport'})
            if not sport_tag or 'NBA' not in sport_tag.text:
                continue

            # Extract prop details
            player_name = container.find('div', {'class': 'name'}).text.strip()
            team_info = container.find('div', {'class': 'team'}).text.strip()
            stat_type = container.find('div', {'class': 'stat'}).text.strip()
            line = float(container.find('div', {'class': 'score'}).text.strip())

            props.append({
                'player': player_name,
                'team': team_info.split(' vs ')[0].strip(),
                'opponent': team_info.split(' vs ')[1].strip(),
                'nba': True,
                'game_time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'stat_type': stat_type,
                'line': line,
                'over_under': 'Over'  # Default to Over
            })

        return {'props': props}

    except Exception as e:
        print(f"Error scraping PrizePicks: {str(e)}")
        # Return mock data as fallback
        with open('data/mock_prizepicks.json', 'r') as f:
            return json.load(f)

def fetch_pinnacle_odds():
    """
    Scrape NBA player props odds from Pinnacle website.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        url = "https://www.pinnacle.com/en/basketball/nba/player-props/"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extract the odds data from the page
        odds = []
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all player prop containers
        prop_containers = soup.find_all('div', {'class': 'market'})

        for container in prop_containers:
            # Extract odds details
            player_name = container.find('div', {'class': 'player'}).text.strip()
            team_info = container.find('div', {'class': 'teams'}).text.strip()
            stat_type = container.find('div', {'class': 'prop-type'}).text.strip()
            line = float(container.find('div', {'class': 'line'}).text.strip())
            over_odds = int(container.find('div', {'class': 'over'}).text.strip())
            under_odds = int(container.find('div', {'class': 'under'}).text.strip())

            odds.append({
                'player': player_name,
                'team': team_info.split(' vs ')[0].strip(),
                'opponent': team_info.split(' vs ')[1].strip(),
                'stat_type': stat_type,
                'line': line,
                'over_odds': over_odds,
                'under_odds': under_odds
            })

        return {'odds': odds}

    except Exception as e:
        print(f"Error scraping Pinnacle: {str(e)}")
        # Return mock data as fallback
        with open('data/mock_pinnacle.json', 'r') as f:
            return json.load(f)

def get_api_keys():
    """Get API keys from environment variables"""
    prizepicks_key = os.getenv('PRIZEPICKS_API_KEY')
    pinnacle_key = os.getenv('PINNACLE_API_KEY')

    if not prizepicks_key or not pinnacle_key:
        raise Exception("Missing API keys")

    return prizepicks_key, pinnacle_key