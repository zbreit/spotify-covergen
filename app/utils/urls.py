from base64 import urlsafe_b64encode

def to_b64_string(string: str) -> str:
    '''Converts a string to (URL-safe) base64. '''
    return urlsafe_b64encode(string.encode()).decode()
