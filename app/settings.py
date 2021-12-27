"""
Settings file (inspired by https://realpython.com/flask-by-example-part-1-project-setup)
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

class SettingsFactory:
    @staticmethod
    def get_settings(environment=None):
        if environment is None:
            environment = os.environ['FLASK_ENV']

        if environment == 'development':
            return DevelopmentSettings()
        elif environment == 'production':
            return ProductionSettings()
        else:
            return Settings()

class Settings:
    SECRET_KEY = os.environ['SECRET_KEY']
    SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
    SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
    SPOTIFY_REDIRECT_URI = os.environ['SPOTIFY_REDIRECT_URI']
    LOG_LEVEL = logging.WARN

class ProductionSettings(Settings):
    LOG_LEVEL = logging.WARN

class DevelopmentSettings(Settings):
    LOG_LEVEL = logging.DEBUG