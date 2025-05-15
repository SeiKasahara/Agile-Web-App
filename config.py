import os

# Get the absolute path to the current directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# Base configuration class for all environments
class BaseConfig:
    # Secret key for session and security
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
    # Database connection URI
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # Disable SQLAlchemy event notifications to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Email server configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    # Default sender for emails sent by the app
    MAIL_DEFAULT_SENDER = ('FuelPrice App', os.getenv('MAIL_USERNAME'))


# Development configuration with debugging enabled
class DevelopmentConfig(BaseConfig):
    DEBUG = True


# Production configuration with debugging disabled
class ProductionConfig(BaseConfig):
    DEBUG = False
