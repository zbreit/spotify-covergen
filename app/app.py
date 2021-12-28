import os
import secrets
from urllib.parse import urlencode
from flask import render_template, session, url_for, redirect, request, flash
from flask import Flask
from werkzeug.exceptions import Unauthorized
from app.utils.errors import SpotifyAPIError
from app.settings import SettingsFactory
from app.utils.spotify_api import get_spotify_access_token, get_spotify_profile, get_spotify_playlists, get_album_covers, playlist_has_editable_cover

app = Flask(__name__)
settings = SettingsFactory.get_settings(environment=os.environ['FLASK_ENV'])
app.config.from_object(settings)
app.logger.setLevel(app.config['LOG_LEVEL'])

@app.route('/')
def index():
    app.logger.debug("I'm in debug mode")
    return render_template('index.jinja')


@app.route('/login', methods=['POST'])
def login():
    state = secrets.token_urlsafe(16)
    session['spotify_auth_state'] = state

    params = {
        'response_type': 'code',
        'client_id': app.config['SPOTIFY_CLIENT_ID'],
        'scope': 'user-read-email ugc-image-upload playlist-read-collaborative playlist-read-private playlist-modify-public playlist-modify-private',
        'redirect_uri': app.config['SPOTIFY_REDIRECT_URI'],
        'state': state
    }

    return redirect(f'https://accounts.spotify.com/authorize?{urlencode(params)}')


@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.get('spotify_auth_state')

    session.pop('spotify_auth_state')    

    if state is None or state != stored_state:
        return Unauthorized(f'Invalid Spotify auth state: {state=}, {stored_state=}')

    access_token, refresh_token = get_spotify_access_token(code, 
        app.config['SPOTIFY_REDIRECT_URI'],
        app.config['SPOTIFY_CLIENT_ID'],
        app.config['SPOTIFY_CLIENT_SECRET'])

    session['spotify_access_token'] = access_token
    session['spotify_refresh_token'] = refresh_token
    session['user_profile'] = get_spotify_profile(access_token)

    return redirect(url_for('playlist_selector'))

@app.route('/playlist-selector')
def playlist_selector():
    if 'user_profile' not in session:
        raise Unauthorized()

    playlists = get_spotify_playlists(session['spotify_access_token'])
    playlists_with_editable_covers = []

    for playlist in playlists:
        if playlist_has_editable_cover(playlist, session['user_profile']['display_name']):
            playlists_with_editable_covers.append(playlist)
    
    return render_template('playlist_selector.jinja', playlists=playlists_with_editable_covers)

@app.route('/cover-generator')
def cover_generator():
    if 'user_profile' not in session:
        raise Unauthorized()

    playlist_id = request.args.get('target_playlist')
    album_covers = get_album_covers(playlist_id, session['spotify_access_token'])
    
    return render_template('cover_generator.jinja', album_covers=album_covers)

@app.route('/logout', methods=['POST'])
def logout():
    session['authenticated'] = False
    session.pop('user_profile')
    session.pop('spotify_access_token')
    session.pop('spotify_refresh_token')

    return redirect(url_for('index'))

@app.errorhandler(SpotifyAPIError)
def handle_spotify_error(error: SpotifyAPIError):
    app.logger.error(error)
    flash(f'Error with the Spotify API: {error.description}', 'error')

    return redirect(url_for('index'))

@app.errorhandler(Unauthorized)
def handle_unauthorized_error(error):
    app.logger.error(error)
    flash(f'Cannot access that page without signing in', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()