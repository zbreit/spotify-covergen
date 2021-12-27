import logging
import requests
from functools import lru_cache
from flask import url_for
from app.utils.http import paginated_get_request, urlsafe_b64_string
from app.utils.errors import SpotifyAPIError

SPOTIFY_API_URL = 'https://api.spotify.com/v1'
logger = logging.getLogger(__name__)

def get_spotify_playlists(access_token):
    return paginated_get_request(
            f'{SPOTIFY_API_URL}/me/playlists',
            params={'limit': 2},
            headers={'Authorization': f'Bearer {access_token}'},
        )

@lru_cache(maxsize=2048)
def get_album_covers(playlist_id, access_token, max_item_count=float('inf')):
    playlist_items = paginated_get_request(
        f'{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks',
        params={'fields': 'items(track(album(images),name)),next'},
        max_item_count=max_item_count,
        headers={'Authorization': f'Bearer {access_token}'},
    )

    # Note: might be cool to grab `item['track']['artists'][0]['images'][0]['url']`
    album_covers = set()
    for item in playlist_items:
        try:
            album_covers.add(item['track']['album']['images'][0]['url'])
        except IndexError:
            logger.warn(f'{item["track"]["name"]} has no cover image!')

    return list(album_covers)



def get_spotify_profile(access_token):
    response = requests.get(
        f'{SPOTIFY_API_URL}/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if not response.ok:
        raise SpotifyAPIError(response)

    json = response.json()

    try:
        image = json['images'][0]['url']
    except IndexError:
        image = url_for('static', filename='img/backup-img.jpg')

    return {
        'image': image,
        'display_name': json['display_name']
    }

def playlist_has_editable_cover(playlist, user_display_name):
    '''
    Checks that a playlist is owned by the current user and has enough tracks
    '''
    playlist_owner = playlist.get('owner', {}).get('display_name')

    return playlist_owner == user_display_name and playlist['tracks']['total'] >= 4

def get_spotify_access_token(authorization_code, redirect_uri, spotify_client_id, spotify_client_secret):
    # Request spotify API token for the user if they gave the correct permissions to this app
    authorization = f'{spotify_client_id}:{spotify_client_secret}'    
    response = requests.post(
        'https://accounts.spotify.com/api/token', 
        data={
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
            'code': authorization_code
        }, 
        headers={'Authorization': f'Basic {urlsafe_b64_string(authorization)}'}
    )

    if not response.ok:
        raise SpotifyAPIError(response)

    response_json = response.json()

    return response_json['access_token'], response_json['refresh_token']