import os
import config
import requests
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips
from flask import Flask, request, render_template, jsonify

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def home():
    return render_template('index.html')

app.run()