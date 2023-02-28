"""
    Flask configurations and other configurations
"""
import os
from dotenv import load_dotenv
# Load Configs from .env
load_dotenv()


class Config():
    # App Directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    JSON_SORT_KEYS = False
    # Configs loaded from env
    SECRET_KEY = os.getenv('SECRET_KEY')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('noreply@weconnect.muhozi.dev')


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    TESTING = False
    # SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True
    # SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True
    # SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') + '_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


api_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
