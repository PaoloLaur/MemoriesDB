import os 
from datetime import timedelta

class Config: 

    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # for performance
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Generate a strong secret
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer' 
    JWT_COOKIE_CSRF_PROTECT = False  # Disables CSRF protection for cookies
    JWT_CSRF_CHECK_FORM = False      # Disables CSRF checks in form submissions
