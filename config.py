import os 
from datetime import timedelta

class Config: 
    SECRET_KEY = os.getenv('SECRET_KEY') #Flask uses SECRET_KEY to sign session cookies. This prevents users from tampering with the session data stored in their browser.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') # used to sign JWT tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer' 
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_CHECK_FORM = False

    REDIS_URL = os.getenv('REDIS_URL')
    RATELIMIT_STORAGE_URL = REDIS_URL