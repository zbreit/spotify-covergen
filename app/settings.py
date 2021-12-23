"""
Settings file (inspired by https://realpython.com/flask-by-example-part-1-project-setup)
"""

import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Settings(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
    SPOTIFY_REDIRECT_URI = os.environ['SPOTIFY_REDIRECT_URI']


class ProductionSettings(Settings):
    DEBUG = False


class StagingSettings(Settings):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentSettings(Settings):
    DEVELOPMENT = True
    DEBUG = True