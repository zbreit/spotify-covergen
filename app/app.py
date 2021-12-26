from functools import lru_cache
import secrets
import requests
from urllib.parse import urlencode
from flask import render_template, session, url_for, redirect, request, flash
from flask import Flask
from werkzeug.exceptions import Unauthorized
from app.utils.http import paginated_get_request, urlsafe_b64_string
from app.utils.errors import SpotifyAPIError

app = Flask(__name__)
app.config.from_object('app.settings.Settings')

SPOTIFY_API_URL = 'https://api.spotify.com/v1'

@app.route('/')
def index():
    return render_template('index.jinja')


@app.route('/login', methods=['POST'])
def login():
    state = secrets.token_urlsafe(16)
    session['spotify_auth_state'] = state

    params = {
        'response_type': 'code',
        'client_id': app.config['SPOTIFY_CLIENT_ID'],
        'scope': 'user-read-email user-read-private playlist-modify-public playlist-modify-private ugc-image-upload',
        'redirect_uri': app.config['SPOTIFY_REDIRECT_URI'],
        'state': state
    }

    return redirect(f'https://accounts.spotify.com/authorize?{urlencode(params)}')


@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    stored_state = session.get('spotify_auth_state')

    if state is None or state != stored_state:
        return Unauthorized(f'Invalid Spotify auth state: {state=}, {stored_state=}')

    session.pop('spotify_auth_state')

    # Request spotify API token for the user if they gave the correct permissions to this app
    authorization = f'{app.config["SPOTIFY_CLIENT_ID"]}:{app.config["SPOTIFY_CLIENT_SECRET"]}'
    response = requests.post(
        'https://accounts.spotify.com/api/token', 
        data={
            'redirect_uri': app.config['SPOTIFY_REDIRECT_URI'],
            'grant_type': 'authorization_code',
            'code': code
        }, 
        headers={'Authorization': f'Basic {urlsafe_b64_string(authorization)}'}
    )

    if not response.ok:
        raise SpotifyAPIError(response)

    response_json = response.json()
    app.logger.info(f'{response_json=}')

    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    session['spotify_access_token'] = access_token
    session['spotify_refresh_token'] = refresh_token
    session['user_profile'] = get_spotify_profile()

    return redirect(url_for('playlist_selector'))

@app.route('/playlist-selector')
def playlist_selector():
    if 'user_profile' not in session:
        raise Unauthorized()

    playlists = get_spotify_playlists()
    
    return render_template('playlist_selector.jinja', playlists=playlists)

@app.route('/cover-generator')
def cover_generator():
    if 'user_profile' not in session:
        raise Unauthorized()

    playlist_id = request.args.get('target_playlist')
    album_covers = get_album_covers(playlist_id)
    
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

def get_spotify_profile():
    response = requests.get(
        f'{SPOTIFY_API_URL}/me',
        headers={'Authorization': f'Bearer {session["spotify_access_token"]}'}
    )

    if not response.ok:
        raise SpotifyAPIError(response)

    json = response.json()

    # Only select useful user profile attributes
    return {
        'image': json['images'][0]['url'],
        'display_name': json['display_name']
    }

def get_spotify_playlists():
    return paginated_get_request(
            f'{SPOTIFY_API_URL}/me/playlists',
            params={'limit': 2},
            headers={'Authorization': f'Bearer {session["spotify_access_token"]}'},
        )

@lru_cache(maxsize=2048)
def get_album_covers(playlist_id, max_item_count=float('inf')):
    playlist_items = paginated_get_request(
        f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks',
        params={'fields': 'items(track(album(images),name)),next'},
        max_item_count=max_item_count,
        headers={'Authorization': f'Bearer {session["spotify_access_token"]}'},
    )

    # Note: might be cool to grab `item['track']['artists'][0]['images'][0]['url']`
    album_covers = set()
    for item in playlist_items:
        try:
            album_covers.add(item['track']['album']['images'][0]['url'])
        except IndexError:
            app.logger.warn(f'{item["track"]["name"]} has no cover image!')

    return list(album_covers)

if __name__ == '__main__':
    app.run()