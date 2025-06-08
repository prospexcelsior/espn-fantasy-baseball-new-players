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

def chunk_tweets(lines, header=""):
    chunks = []
    tweet = header
    for line in lines:
        if len(tweet + "\n" + line) <= 280:
            tweet += "\n" + line
        else:
            chunks.append(tweet)
            tweet = line
    chunks.append(tweet)
    return chunks

def post_thread(tweets):
    client = tweepy.Client(
        os.environ["BEARER_TOKEN"], 
        os.environ["API_KEY"], 
        os.environ["API_SECRET"],
        os.environ["ACCESS_TOKEN"], 
        os.environ["ACCESS_SECRET"],
    )

    response = client.create_tweet(text=tweets[0])
    thread_id = response.data["id"]
    for tweet in tweets[1:]:
        response = client.create_tweet(text=tweet, in_reply_to_tweet_id=thread_id)
        thread_id = response.data["id"]

def main():
    current_players = get_players()
    previous_players = load_previous_players()

    previous_ids = {p['id'] for p in previous_players}
    new_players = [p for p in current_players if p['id'] not in previous_ids]

    if new_players:
        lines = [f"{p['name']}" for p in new_players]
        header = f"🆕 New Fantasy Baseball Players as of {date.today()}:"
        tweets = chunk_tweets(lines, header)

        for tweet in tweets:
            print("===")
            print(tweet)
        try:
            post_thread(tweets)
        except:
            traceback.print_exc()
    else:
        print("No new players")

    save_players(current_players)

if __name__ == "__main__":
    main()
