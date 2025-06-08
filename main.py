import json
import os
import requests
from datetime import date
import tweepy

def get_players():
    url = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb/seasons/2025/players?scoringPeriodId=0&view=players_wl"
    headers = {
        "X-Fantasy-Filter": json.dumps({"filterActive": {"value": True}}),
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    players = []
    for player_info in data:
        player_id = player_info.get("id")
        full_name = player_info.get("fullName")
        if player_id and full_name:
            players.append({"id": player_id, "name": full_name})

    players.sort(key=lambda x: x['id'])
    return players

def load_previous_players(file='players.json'):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_players(players, file='players.json'):
    with open(file, 'w') as f:
        json.dump(players, f, indent=2)

def post_to_twitter(message):
    auth = tweepy.OAuth1UserHandler(
        os.environ["API_KEY"], os.environ["API_SECRET"],
        os.environ["ACCESS_TOKEN"], os.environ["ACCESS_SECRET"]
    )
    api = tweepy.API(auth)
    api.update_status(message)

def main():
    current_players = get_players()
    previous_players = load_previous_players()

    previous_ids = {p['id'] for p in previous_players}
    new_players = [p for p in current_players if p['id'] not in previous_ids]

    if new_players:
        lines = [f"{p['name']} (ID: {p['id']})" for p in new_players]
        tweet_text = f"🆕 New Fantasy Baseball Players as of {date.today()}:\n" + "\n".join(lines[:5])
        if len(lines) > 5:
            tweet_text += f"\n+{len(lines)-5} more..."

        print(tweet_text)
        # post_to_twitter(tweet_text)
    else:
        print("No new players")

    save_players(current_players)

if __name__ == "__main__":
    main()
