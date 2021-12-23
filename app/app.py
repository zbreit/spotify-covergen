import logging
import secrets
import requests
from urllib.parse import urlencode
from base64 import urlsafe_b64encode
from flask import render_template, session, url_for, redirect, request, flash
from flask import Flask

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
        logger.error(f'Invalid state: {state=}, {stored_state=}')
        flash('Error logging into Spotify, please try again!', 'error')

        return redirect(url_for('index'))

    session.pop('spotify_auth_state')

    form_data = {
        'redirect_uri': app.config['SPOTIFY_REDIRECT_URI'],
        'grant_type': 'authorization_code',
        'code': code
    }

    authorization = f'{app.config["SPOTIFY_CLIENT_ID"]}:{app.config["SPOTIFY_CLIENT_SECRET"]}'
    headers = {
        'Authorization': f'Basic {urlsafe_b64encode(authorization.encode()).decode()}'
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=form_data, headers=headers)

    if response.status_code != 200:
        logger.error(f'Error with the HTTP request to Spotify: {response.text=}')
        flash('Error connecting your account with the Spotify API', 'error')

        return redirect(url_for('index'))

    response_json = response.json()
    logger.info(f'{response_json=}')

    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    session['spotify_access_token'] = access_token
    session['spotify_refresh_token'] = refresh_token
    session['authenticated'] = True

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

#         // we can also pass the token to the browser to make requests from there
#         res.redirect('/#' +
#           querystring.stringify({
#             access_token: access_token,
#             refresh_token: refresh_token
#           }));
#       } else {
#         res.redirect('/#' +
#           querystring.stringify({
#             error: 'invalid_token'
#           }));
#       }
#     });
#   }
# });

@app.route('/refresh_token', methods='POST')
def refresh_token():
  refresh_token = session.get('refresh_token')

  var authOptions = {
    url: 'https://accounts.spotify.com/api/token',
    headers: { 'Authorization': 'Basic ' + (new Buffer(client_id + ':' + client_secret).toString('base64')) },
    form: {
      grant_type: 'refresh_token',
      refresh_token: refresh_token
    },
    json: true
  };

  request.post(authOptions, function(error, response, body) {
    if (!error && response.statusCode === 200) {
      var access_token = body.access_token;
      res.send({
        'access_token': access_token
      });
    }
  });
});

if __name__ == '__main__':
    app.run()