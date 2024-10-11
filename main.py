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

    params = { # Initializes a dictionary that holds streamer ID and the limit to clips allowed to be fetched.
        'broadcaster_id': streamer_id,
        'first': limit,
    }

    if start_time:
        params['started_at'] = start_time
        params['ended_at'] = now.isoformat() + "Z"

    response = requests.get(base_url, params=params, headers=headers) # HTTP GET request to Twitch API
    return response.json().get('data', []) # Converts JSON response into Python data and returns the list of clips fetched, returns empty list if no data is found.

# Function that downloads all the clips fetched
def download_clips(clips, max_retries=50):
    downloaded_clips = []

    for index, clip in enumerate(clips[:25], start=1): # Loops through the top 25 fetched clip, as we only want to download 25 of the bunch currently
        clip_url = clip['thumbnail_url'].split('-preview', 1)[0] + '.mp4' # Extracts the URL of the clip and modifies it in order to point to the video itself
        clip_path = os.path.join('clips', f"{index}.mp4") # Creates file path to 'clips' folder

        # Retry logic
        success = False
        attempts = 0

        while not success and attempts < max_retries: # Attempt to download each clip up to 'max_retries' times
            response = requests.get(clip_url, stream=True) # GET request to download the clip
            if response.status_code == 200: # Status code 200 represents success
                with open(clip_path, 'wb') as file: # Writing the clip data into the file
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                # Verify that the file size is reasonable
                if os.path.getsize(clip_path) > 1 * 1024 * 1024: # File should be at least 1MB to ensure it's not corrupted
                    success = True
                    downloaded_clips.append(clip_path) # Add to list of downloaded clips
                    print(f"Downloaded clip {index}: {clip_path}")
                else:
                    print(f"Clip {index} seems corrupted (too small), retrying...")
                    os.remove(clip_path)  # Delete the incomplete file
            else:
                print(f"Failed to download clip {index}: HTTP Status Code {response.status_code}")

            attempts += 1

        if not success:
            print(f"Failed to download clip {index} after {max_retries} attempts.")

    return downloaded_clips

# Function to concatenate clips together into compilation
def concatenate_clips(streamer_name, clip_paths):
    existing_files = [f for f in os.listdir('compilations') if f.startswith(streamer_name)] # Check existing compilation files to determine unique filename
    number = len(existing_files) + 1 # Adds a number to the end of the file name in order to consistently create unique file names for each compilation made 
    filename = f"{streamer_name}_compilation{number}.mp4" # Generate unique filename

    video_clips = []

    for cp in clip_paths: # Loop through each downloaded clip path
        if os.path.exists(cp): # Ensure the clip exists before attempting to load it
            try:
                video_clips.append(VideoFileClip(cp)) # Append clip to list of video clips
            except OSError as e:
                print(f"Error loading clip {cp}: {e}")  # Skip corrupted clips

    if video_clips:
        final_clip = concatenate_videoclips(video_clips, method='compose') # Concatenate all clips together into a single video
        final_clip.write_videofile(os.path.join('compilations', filename), audio_codec='aac') # Stitched compilation is written to compilations folder with and assigned a specific audio codec
        print("Stitching complete. The final compilation has been saved.")
    else:
        print("No valid clips to stitch together.")

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

print("Fetching clips from Twitch...")
clips = fetch_clips(streamer_id, time)
if not clips:
    print("Error - No clips fetched.")
else:
    print(f"Fetching complete! Starting to create your compilation.")

print("Downloading fetched clips...")
downloaded_clips = download_clips(clips[:25])

if len(downloaded_clips) > 0:
    streamer_name = streamer_url.split('/')[-1]
    print("Stitching downloaded clips together...")
    concatenate_clips(streamer_name, downloaded_clips)
else:
    print("No clips downloaded successfully. Compilation aborted.")