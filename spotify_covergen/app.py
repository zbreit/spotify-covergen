# app.py
from flask import Flask, render_template, redirect, flash
import spotipy
from werkzeug.utils import redirect
from . import settings
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Landing Page
@app.route('/')
def index():
    return render_template("index.html")

# Connect to the user's Spotify account
@app.route('/connect-to-spotify')
def spotify_auth():
    scope = "user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])
    return "Hi"

# Callback
@app.route("/connect-to-spotipy/callback")
def spotify_auth_callback():
    return redirect("/")