
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-dev-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/email_tracker'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Render deployment specific
    if os.environ.get('RENDER'):
        # Add any Render specific configs here
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Ensure strong secrets in production!
