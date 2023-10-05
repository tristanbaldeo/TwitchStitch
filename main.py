import os
import config
import requests

# Twitch API Integration
client_id = config.client_id
client_secret = config.client_secret

if not os.path.exists('clips'): # If clips folder doesn't exist, create folder
    os.mkdir('clips')

if not os.path.exists('compilations'): # If compilations folder doesn't exist, create folder
    os.mkdir('compilations')

# Function that obtains OAuth token
def twitchToken():
    url = "https://id.twitch.tv/oauth2/token"
    payload = { # Payload is data being sent to Twitch through HTTP request
        'client_id': config.client_id,
        'client_secret': config.client_secret,
        'grant_type': 'client_credentials' # Requesting OAuth token grant
    }
    response = requests.post(url, params=payload) # Sending POST request along with all the payload data
    return response.json().get('access_token', None) # Converts response from JSON into Python dictionary and attempts to get value associated with the access token

# Function that makes sure Twitch URL exists
def validURL(streamerURL):
    streamerName = streamerURL.split('/')[-1] # Extracts the name out of the URL
    url = f"https://api.twitch.tv/helix/users?login={streamerName}" # Uses Twitch API to gather the data
    headers = {
        'Client-ID': config.client_id,
        'Authorization': f"Bearer {twitchToken()}"
    }
    response = requests.get(url, headers=headers)
    data = response.json().get('data', [])
    return len(data) > 0 # If the list returns with one or more items, then the streamer exists

# Inputs
while True:
    streamerURL = input("Enter the URL (or username) of the Twitch streamer: ")
    if validURL(streamerURL):
        break
    print("Invalid streamer. Please try again.")

validTimes = ["24 hours", "7 days", "30 days", "all time", "24", "7", "30"]
while True:
    time = input("Choose the time period of clips to compilate (24 hours, 7 days, 30 days, or all time): ")
    if time in validTimes:
        break
    print("Invalid time. Please try again.")

validLengths = ["5", "10", "15", "5 minutes", "10 minutes", "15 minutes"]
while True:
    compLength = input("Choose the compilation duration of your choice (5, 10, or 15 minutes): ")
    if compLength in validLengths:
        break
    print("Invalid duration. Please try again.")