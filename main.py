import os
import config
import requests
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips

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
def fetch_clips(streamer_id, period, limit = 35):
    base_url = "https://api.twitch.tv/helix/clips"
    now = datetime.utcnow() # Universal time standard being used and returned with ".isoformat() + "Z"

    # if comp_length in ["5", "5 minutes"]:
    #     comp_duration = 5 * 60
    # elif comp_length in ["10", "10 minutes"]:
    #     comp_duration = 10 * 60
    # elif comp_length in ["15", "15 minutes"]:
    #     comp_duration = 15 * 60
    # else:
    #     return []
    
    start_time = None # Determines the start time for clip fetching

    if period in ["24 hours", "24"]: # All these time conditions check the value of period and set the start time accordingly (i.e. 24 hours sets start time to 24 hours before 'now'.)
        start_time = (now - timedelta(days=1)).isoformat() + "Z"
    elif period in ("7 days", "7"):
        start_time = (now - timedelta(weeks=1)).isoformat() + "Z"
    elif period in ("30 days", "30"):
        start_time = (now - timedelta(days=30)).isoformat() + "Z"

    headers = { # Twitch API request for HTTP headers
        'Client-ID': config.client_id,
        'Authorization': f"Bearer {twitch_token()}"
    }

    # total_duration = 0
    # total_clips = []
    # cursor = None

    # while total_duration < comp_duration:

    params = { # Initializes a dictionary that holds streamer ID and the limit to clips allowed to be fetched.
        'broadcaster_id': streamer_id,
        'first': limit,
    }

    if start_time:
        params['started_at'] = start_time
        params['ended_at'] = now.isoformat() + "Z"

        # if cursor:
        #     params['after'] = cursor

    response = requests.get(base_url, params=params, headers=headers) # HTTP GET request to Twitch API
    return response.json().get('data', []) # Converts JSON response into Python data and returns the list of clips fetched, returns empty list if no data is found.

    # after = response.json().get('pagination', {}).get('after')

    #     print(f"Fetched {len(data)} clips. Total duration so far: {total_duration}s.")

    #     if not data:
    #         break

    #     for clip in data:
    #         clip_duration = clip.get('duration', 0)
    #         if (total_duration + clip_duration) <= comp_duration:
    #             total_clips.append(clip)
    #             total_duration += clip_duration
    #         else:
    #             break   
    
    # return total_clips

# Function that downloads all the clips fetched
def download_clips(clips):
    for index, clip in enumerate(clips[:25], start=1): # Loops through the top 25 fetched clip, as we only want to download 25 of the bunch currently
        clip_url = clip['thumbnail_url'].split('-preview', 1)[0] + '.mp4' # Extracts the URL of the clip and modifies it in order to point to the video itself
        clip_path = os.path.join('clips', f"{index}.mp4") # Creates file path to 'clips' folder

        response = requests.get(clip_url, stream=True) # GET request to download the clip
        if response.status_code == 200: # Status code 200 represents success
            with open(clip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

# Function to concatenate clips together into compilation
def concatenate_clips(streamer_name):
    existing_files = [f for f in os.listdir('compilations') if f.startswith(streamer_name)] # Creates a list of file names, indicating for it to start with the streamer name
    number = len(existing_files) + 1 # Adds a number to the end of the file name in order to consistently create unique file names for each compilation made 
    filename = f"{streamer_name}_compilation{number}.mp4"

    clip_paths = [os.path.join('clips', f"{i}.mp4") for i in range (1, len(clips) + 1)]
    video_clips = [VideoFileClip(cp) for cp in clip_paths if os.path.exists(cp)]
    final_clip = concatenate_videoclips(video_clips, method = 'compose') # Concatenates the clips
    final_clip.write_videofile(os.path.join('compilations', filename), audio_codec = 'aac') # Stitched compilation is written to compilations folder with and assigned a specific audio codec

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

# valid_lengths = ["5", "10", "15", "5 minutes", "10 minutes", "15 minutes"]
# while True:
#     comp_length = input("Choose the compilation duration of your choice (5, 10, or 15 minutes): ")
#     if comp_length in valid_lengths:
#         break
#     print("Invalid duration. Please try again.") 

print("Fetching clips from Twitch...")
clips = fetch_clips(streamer_id, time)
if not clips:
    print("Error - No clips fetched.")
else:
    print(f"Fetching complete! Starting to create your compilation.")

print("Downloading fetched clips...")
download_clips(clips[:25])

streamer_name = streamer_url.split('/')[-1]

if len(clips) > 0:
    print("Stitching downloaded clips together...")
    concatenate_clips(streamer_name)
    print("Stitching complete. The final compilation has been saved.")