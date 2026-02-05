# Logging Configuration Module

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(app, config):
    """
    Setup application logging
    
    Args:
        app: Flask application instance
        config: Configuration object
    """
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set logging level
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
    
    # App logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Log startup info
    app.logger.info("=" * 50)
    app.logger.info("[OK] CardioPredict Backend Started")
    app.logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    app.logger.info(f"Debug Mode: {app.debug}")
    app.logger.info(f"Timestamp: {datetime.now()}")
    app.logger.info("=" * 50)

def log_prediction(app, prediction_id, input_data, result):
    """Log a prediction event"""
    app.logger.info(f"Prediction Made: {prediction_id}")
    app.logger.debug(f"Input: {input_data}")
    app.logger.debug(f"Result: {result}")

def log_api_call(app, method, endpoint, status_code):
    """Log API call"""
    app.logger.debug(f"API Call: {method} {endpoint} - Status: {status_code}")

def log_error(app, error_type, error_message, context=""):
    """Log error event"""
    app.logger.error(f"Error: {error_type} - {error_message}")
    if context:
        app.logger.error(f"Context: {context}")
