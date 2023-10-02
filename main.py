import os
import config
import requests
import youtube_dl
from moviepy.editor import concatenate_videoclips

# Twitch API Integration
client_id = config.client_id
client_secret = config.client_secret

if not os.path.exists('clips'): # If clips folder doesn't exist, create folder
    os.mkdir('clips')

if not os.path.exists('compilations'): # If compilations folder doesn't exist, create folder
    os.mkdir('compilations')

# CDL Inputs
streamerURL = input("Enter the URL of the Twitch streamer: ")
time = input("Choose the time period of clips to compilate (24 hours, 7 days, 30 days, all time): ")
compLength = int(input("Choose the compilation duration of your choice (5, 10, or 15 minutes): "))