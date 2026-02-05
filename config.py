# Backend Configuration Module

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JSON_SORT_KEYS = False
    
    # Database settings (for future upgrades)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///cardio_predictions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:*", "http://127.0.0.1:*"]
    
    # API settings
    API_VERSION = "2.0.0"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    JSON_ACCEPT_ENCODING = 'gzip'
    
    # Prediction settings
    MAX_PREDICTIONS_IN_MEMORY = 10000
    PREDICTION_RETENTION_HOURS = 24
    
    # Model settings
    MODEL_FILE = 'cardio_model.pkl'
    SCALER_FILE = 'scaler.pkl'
    FEATURES_FILE = 'feature_names.pkl'
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com').split(',')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Load appropriate config
config_name = os.getenv('FLASK_ENV', 'development')
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

app_config = config_dict.get(config_name, DevelopmentConfig)
