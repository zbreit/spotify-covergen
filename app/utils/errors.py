from json.decoder import JSONDecodeError
from werkzeug.exceptions import HTTPException
from requests import Response

class SpotifyAPIError(HTTPException):
    def __init__(self, response: Response):
        self.endpoint = response.request.url
        self.code = response.status_code
        self.description = self.get_error_message(response)
        
    
    def __str__(self):
        return f'SpotifyAPIError<{self.endpoint=}, {self.code=}, {self.description=}'

    @staticmethod
    def get_error_message(response: Response) -> str:
        # The Spotify API returns different error format depending on whether
        # the request is accessing an API endpoint or a credentials-request endpoint
        # (see https://developer.spotify.com/documentation/web-api/#authentication-error-object)        
        try:
            json = response.json()
        except JSONDecodeError:
            return response.text

        if 'api.spotify.com' in response.request.url:
            return json['error']['message']   # Regular error response
        elif 'error_description' in json:
            return json['error_description']  # Access error response (with extra detail)
        
        return json['error']  # Access error response (with limited detail)