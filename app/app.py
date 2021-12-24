import logging
import secrets
import requests
from urllib.parse import urlencode
from flask import render_template, session, url_for, redirect, request, flash
from flask import Flask
from werkzeug.exceptions import Unauthorized
from utils.errors import SpotifyAPIError
from utils.urls import to_b64_string

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.config.from_object('settings.Settings')

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    state = secrets.token_urlsafe(16)
    session['spotify_auth_state'] = state

    params = {
        'response_type': 'code',
        'client_id': app.config['SPOTIFY_CLIENT_ID'],
        'scope': 'user-read-private user-read-email',
        'redirect_uri': app.config['SPOTIFY_REDIRECT_URI'],
        'state': state
    }

    return redirect(f'https://accounts.spotify.com/authorize?{urlencode(params)}')


@app.route('/callback')
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
        headers={'Authorization': f'Basic {to_b64_string(authorization)}'}
    )

    if not response.ok:
        raise SpotifyAPIError(response)

    response_json = response.json()
    logger.info(f'{response_json=}')

    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    session['spotify_access_token'] = access_token
    session['spotify_refresh_token'] = refresh_token
    session['authenticated'] = True

    session['user_profile'] = get_spotify_profile()

    return redirect(url_for('cover_generator'))

    
def get_spotify_profile():
    response = requests.get(
        'https://api.spotify.com/v1/me',
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

@app.route('/cover-generator')
def cover_generator():
    if not ('authenticated' in session and session['authenticated'] and 'user_profile' in session):
        raise Unauthorized()

    return render_template('cover_generator.html')

@app.errorhandler(SpotifyAPIError)
def handle_spotify_error(error: SpotifyAPIError):
    logger.error(error)
    flash(f'Error with the Spotify API: {error.description}', 'error')

    return redirect(url_for('index'))

@app.errorhandler(Unauthorized)
def handle_unauthorized_error(error):
    logger.error(error)
    flash(f'Cannot access that page without signing in', 'error')
    
    return redirect(url_for('index'))

#         var options = {
#           url: 'https://api.spotify.com/v1/me',
#           headers: { 'Authorization': 'Bearer ' + access_token },
#           json: true
#         };

#         // use the access token to access the Spotify Web API
#         request.get(options, function(error, response, body) {
#           console.log(body);
#         });

# @app.route('/refresh_token', methods='POST')
# def refresh_token():
#   refresh_token = session.get('refresh_token')

#   var authOptions = {
#     url: 'https://accounts.spotify.com/api/token',
#     headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
#     form: {
#       grant_type: 'refresh_token',
#       refresh_token: refresh_token
#     },
#     json: true
#   };

#   request.post(authOptions, function(error, response, body) {
#     if (!error && response.statusCode === 200) {
#       var access_token = body.access_token;
#       res.send({
#         'access_token': access_token
#       });
#     }
#   });
# });

if __name__ == '__main__':
    app.run()