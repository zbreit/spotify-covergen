import requests
import logging
from base64 import urlsafe_b64encode

logger = logging.getLogger(__name__)

def paginated_get_request(url, max_item_count=float('inf'), params=None, **kwargs) -> list:
    '''
    Performs a paginated get request for the specified URL, fetching up to the max item count.

    ASSUMPTIONS:
        - Page offsets are specified using a query parameter called 'offset' and 'limit'
        - Pages return items in a JSON array called 'items' 

    Exits early if the API call fails (previous results will still be yielded)

    Yields the JSON-parsed responses for each 
    ''' 
    if params is None:
        params = {}

    MAX_ITEM_LIMIT = 50
    params.setdefault('limit', MAX_ITEM_LIMIT)

    items = []
    more_items_left = True
    offset = 0

    while more_items_left and offset < max_item_count:
        # Only fetch as many elements as needed based on the max item count
        params['limit'] = min(params['limit'], max_item_count - offset)
        params['offset'] = offset

        response = requests.get(url, params=params, **kwargs)

        if not response.ok:
            logger.error(f'Failed requesting the next page of results for "{url}": {response.text}')
            break
        
        json = response.json()
        items.extend(json['items'])
        offset += len(json['items'])

        more_items_left = json['next'] is not None

    return items

def urlsafe_b64_string(string: str) -> str:
    '''Converts a string to a string of (URL-safe) base64.'''
    return urlsafe_b64encode(string.encode()).decode()
