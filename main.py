import os
import config
import requests
from datetime import datetime, timedelta

# Twitch API Integration
client_id = config.client_id
client_secret = config.client_secret

if not os.path.exists('clips'): # If clips folder doesn't exist, create folder
    os.mkdir('clips')

if not os.path.exists('compilations'): # If compilations folder doesn't exist, create folder
    os.mkdir('compilations')

# Function that obtains OAuth token
def twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    payload = { # Payload is data being sent to Twitch through HTTP request
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'client_credentials' # Requesting OAuth token grant
    }
    response = requests.post(url, params=payload) # Sending POST request along with all the payload data
    return response.json().get('access_token', None) # Converts response from JSON into Python dictionary and attempts to get value associated with the access token

# Function that makes sure Twitch URL exists
def valid_url(streamer_url):
    streamer_name = streamer_url.split('/')[-1] # Extracts the name out of the URL
    url = f"https://api.twitch.tv/helix/users?login={streamer_name}" # Uses Twitch API to gather the data
    headers = {
        'Client-ID': config.client_id,
        'Authorization': f"Bearer {twitch_token()}"
    }
    response = requests.get(url, headers=headers)
    data = response.json().get('data', [])
    if len(data) > 0: # If the list returns with one or more items, then the streamer exists
        return data[0]['id']
    return None

# Function that fetches Twitch clips from streamer
def fetch_clips(streamer_name, period, limit = 100):
    base_url = "https://api.twitch.tv/helix/clips"
    now = datetime.utcnow() # Universal time standard being used and returned with ".isoformat() + "Z"
    if period in ["24 hours", "24"]:
        start_time = (now - timedelta(days=1)).isoformat() + "Z"
    elif period in ("7 days", "7"):
        start_time = (now - timedelta(weeks=1)).isoformat() + "Z"
    elif period in ("30 days", "30"):
        start_time = (now - timedelta(days=30)).isoformat() + "Z"
    else:
        start_time = None

    params = {
        'broadcaster_id': streamer_id,
        'first': limit
    }

    if start_time:
        params['start_time'] = start_time
        params['end_time'] = now.isoformat() + "Z"

    headers = {
        'Client-ID': config.client_id,
        'Authorization': f"Bearer {twitch_token()}"
    }

    response = requests.get(base_url, params=params, headers=headers)
    return response.json().get('data', [])

# Inputs
while True:
    streamer_url = input("Enter the URL (or username) of the Twitch streamer: ")
    streamer_id = valid_url(streamer_url)
    if streamer_id:
        break
    print("Invalid streamer. Please try again.")

valid_times = ["24 hours", "7 days", "30 days", "all time", "24", "7", "30"]
while True:
    time = input("Choose the time period of clips to compilate (24 hours, 7 days, 30 days, or all time): ")
    if time in valid_times:
        break
    print("Invalid time. Please try again.")


valid_lengths = ["5", "10", "15", "5 minutes", "10 minutes", "15 minutes"]
while True:
    comp_length = input("Choose the compilation duration of your choice (5, 10, or 15 minutes): ")
    if comp_length in valid_lengths:
        break
    print("Invalid duration. Please try again.")

print("Fetching clips from Twitch...")
clips = fetch_clips(streamer_id, time)
if not clips:
    print("Error - No clips fetched.")
else:
    print(f"Fetching complete! {len(clips)} clips have been fetched.")