# TwitchStitch
TwitchStitch is a Flask-based web application that downloads the most popular Twitch clips from a given streamer within a specified time period (24 hours, 7 days, 30 days, or all time) and compiles them into a single video

## Features
- **Streamlined User Input**: Users can input a Twitch streamer's name or URL and select a time period to fetch clips from (24 hours, 7 days, 30 days, or all time)
- **Automatic Clip Downloading**: The app fetches and downloads clips from Twitch via Selenium for the selected time period
- **Compilation**: The downloaded clips are stitched together into a single video using MoviePy
- **Progress Tracking**: The app shows real-time progress updates while downloading clips

## Requirements
To set up this project locally, you will need Python and the following dependencies. You can install these by running the commands in the installation process below

### Installation
First, clone the repository:
```bash
git clone https://github.com/yourusername/twitchstitch.git
cd twitchstitch
```

Then, install the required packages by running (make sure you are using a virtual environment such as `.venv`):
```bash
pip install -r requirements.txt
```

## Setup
1. **Twitch API Credentials**: Obtain your Twitch API `client_id` and `client_secret` from the Twitch Developer Console and add them to the `config.py` file
```bash
client_id = 'YOUR_CLIENT_ID_HERE'
client_secret = 'YOUR_CLIENT_SECRET_HERE'
```

2. **Start Flask App**:
```bash
python app.py
```

3. **Access the Web Interface**:
Open your browser and navigate to `http://127.0.0.1:5000` to access TwitchStitch

## Usage
1. **Enter the Twitch Streamer URL**: Provide the URL or username of the Twitch streamer
2. **Select Time Period**: Choose the time period from which clips will be fetched (24 hours, 7 days, or 30 days)
3. **Download Clips**: Click on the download button, and the application will automatically fetch the clips, download them, and stitch them together into a single video
4. **Track Progress**: The progress of downloading and compilation is displayed on the web interface

### Video Compilation
- Once the clips are downloaded, they will be compiled into a video and stored in the compilations folder
- The video will be named based on the streamer's name, followed by the compilation number (e.g., streamername_compilation1.mp4)

## Troubleshooting
### Selenium Errors
- Make sure you have a stable version of Google Chrome installed, as `webdriver-manager` will use it to automate the browser

### Progress Not Updating
- If the progress stops or the application gets stuck, check the terminal for any error logs or exceptions. If necessary, rerun the app and ensure the Twitch API is accessible