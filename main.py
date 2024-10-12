import os
import config
import requests
from datetime import datetime, timedelta, timezone
from moviepy.editor import VideoFileClip, concatenate_videoclips
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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
    now = datetime.now(timezone.utc) # Universal time standard being used
    
    start_time = None # Determines the start time for clip fetching

    if period in ["24 hours", "24"]: # All these time conditions check the value of period and set the start time accordingly (i.e. 24 hours sets start time to 24 hours before 'now'.)
        start_time = (now - timedelta(days=1)).isoformat().replace('+00:00', 'Z')
    elif period in ("7 days", "7"):
        start_time = (now - timedelta(weeks=1)).isoformat().replace('+00:00', 'Z')
    elif period in ("30 days", "30"):
        start_time = (now - timedelta(days=30)).isoformat().replace('+00:00', 'Z')

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
        params['ended_at'] = now.isoformat().replace('+00:00', 'Z')

    response = requests.get(base_url, params=params, headers=headers) # HTTP GET request to Twitch API
    return response.json().get('data', []) # Converts JSON response into Python data and returns the list of clips fetched, returns empty list if no data is found.

# Function to configure and return the Chrome WebDriver in headless mode
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=old')  # Ensure headless mode
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Optimize memory usage
    options.add_argument('--mute-audio')  # Disable any sound
    options.add_argument('--disable-software-rasterizer')  # Disable unnecessary graphical processing
    options.add_argument('--disable-extensions')  # Disable unnecessary extensions
    options.add_argument('--disable-infobars')  # Remove infobars that might pop up
    options.add_argument('--remote-debugging-port=9222')  # Remote debugging, no visible GUI
    options.add_argument('--disable-popup-blocking')  # Prevent popup windows from appearing

    # Suppress browser console output
    options.add_argument('--log-level=3')  # Suppress browser logs (only show fatal errors)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function that downloads all the clips fetched
def download_clips(clips):
    driver = get_driver()  # Initialize headless browser

    for index, clip in enumerate(clips[:25], start=1):  # Loop through the first 25 clips
        clip_url = clip.get('url')  # Get the clip's Twitch webpage URL

        if clip_url:
            print(f"Opening Clip {index} page: {clip_url}")
            
            driver.get(clip_url) # Load the clip page using Selenium
            
            # Extracts the .mp4 URL from the <video> tag in the HTML
            try:
                video_element = driver.find_element(By.TAG_NAME, 'video')  # Find the <video> tag
                video_url = video_element.get_attribute('src')  # Get the .mp4 file URL

                if video_url:
                    clip_path = os.path.join('clips', f"{index}.mp4") # Creates file path to 'clips' folder

                    video_response = requests.get(video_url, stream=True) # GET request to download the clip
                    if video_response.status_code == 200: # Status code 200 represents success
                        with open(clip_path, 'wb') as file:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"Clip {index} downloaded successfully.")
                    else:
                        print(f"Failed to download clip {index}, status code: {video_response.status_code}")
                else:
                    print(f"Clip {index} has no valid video source.")
            except Exception as e:
                print(f"Failed to extract video for Clip {index}: {e}")
        else:
            print(f"Clip {index} has no valid URL.")
    
    driver.quit()  # Close the Selenium browser after all downloads are complete

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
    time_period = input("Choose the time period of clips to compilate (24 hours, 7 days, 30 days, or all time): ")
    if time_period in valid_times:
        break
    print("Invalid time. Please try again.")

print("Fetching clips from Twitch...")
clips = fetch_clips(streamer_id, time_period)
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