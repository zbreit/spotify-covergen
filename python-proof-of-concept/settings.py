"""
Settings file (inspired by https://realpython.com/flask-by-example-part-1-project-setup)
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))
from dotenv import load_dotenv

# Load Spotipy and other environment configs from `.env`
load_dotenv()

class Settings(object):
    # Flask Settings
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']

    # Spotipy Settings
    SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
    SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
    SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']


class ProductionSettings(Settings):
    DEBUG = False


class StagingSettings(Settings):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentSettings(Settings):
    DEVELOPMENT = True
    DEBUG = True