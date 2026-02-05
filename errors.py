"""
Error Handling and Exception Management
Provides consistent error formatting, custom exceptions, and error logging
"""

import logging
from functools import wraps
from flask import jsonify, request

# ==================== CUSTOM EXCEPTIONS ====================

class PredictionError(Exception):
    """Base prediction error"""
    def __init__(self, message, status_code=400, error_code='PREDICTION_ERROR'):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ValidationError(PredictionError):
    """Input validation error"""
    def __init__(self, message, field=None):
        super().__init__(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR'
        )
        self.field = field

class ModelError(PredictionError):
    """ML model operation error"""
    def __init__(self, message):
        super().__init__(
            message=message,
            status_code=503,
            error_code='MODEL_ERROR'
        )

class DatabaseError(PredictionError):
    """Database operation error"""
    def __init__(self, message):
        super().__init__(
            message=message,
            status_code=503,
            error_code='DATABASE_ERROR'
        )

class NotFoundError(PredictionError):
    """Resource not found error"""
    def __init__(self, resource='Resource'):
        super().__init__(
            message=f'{resource} not found',
            status_code=404,
            error_code='NOT_FOUND'
        )

class RateLimitError(PredictionError):
    """Rate limit exceeded error"""
    def __init__(self):
        super().__init__(
            message='Rate limit exceeded. Please try again later.',
            status_code=429,
            error_code='RATE_LIMIT_EXCEEDED'
        )

# ==================== ERROR HANDLERS ====================

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def register_handlers(app):
        """Register all error handlers with Flask app"""
        
        @app.errorhandler(ValidationError)
        def handle_validation_error(error):
            return ErrorHandler.format_error_response(
                error.message,
                error.status_code,
                error.error_code,
                {'field': error.field} if error.field else None
            ), error.status_code
        
        @app.errorhandler(ModelError)
        def handle_model_error(error):
            app.logger.error(f"Model Error: {error.message}")
            return ErrorHandler.format_error_response(
                error.message,
                error.status_code,
                error.error_code
            ), error.status_code
        
        @app.errorhandler(DatabaseError)
        def handle_database_error(error):
            app.logger.error(f"Database Error: {error.message}")
            return ErrorHandler.format_error_response(
                error.message,
                error.status_code,
                error.error_code
            ), error.status_code
        
        @app.errorhandler(NotFoundError)
        def handle_not_found(error):
            return ErrorHandler.format_error_response(
                error.message,
                error.status_code,
                error.error_code
            ), error.status_code
        
        @app.errorhandler(RateLimitError)
        def handle_rate_limit(error):
            return ErrorHandler.format_error_response(
                error.message,
                error.status_code,
                error.error_code
            ), error.status_code
        
        @app.errorhandler(400)
        def handle_bad_request(error):
            return ErrorHandler.format_error_response(
                'Bad request - Invalid input format',
                400,
                'BAD_REQUEST'
            ), 400
        
        @app.errorhandler(404)
        def handle_not_found_default(error):
            return ErrorHandler.format_error_response(
                f'Endpoint not found: {request.path}',
                404,
                'NOT_FOUND'
            ), 404
        
        @app.errorhandler(500)
        def handle_internal_error(error):
            app.logger.error(f"Internal Server Error: {error}")
            return ErrorHandler.format_error_response(
                'Internal server error - Please contact support',
                500,
                'INTERNAL_ERROR'
            ), 500
        
        @app.errorhandler(Exception)
        def handle_generic_error(error):
            app.logger.error(f"Unhandled Exception: {str(error)}")
            return ErrorHandler.format_error_response(
                'An unexpected error occurred',
                500,
                'INTERNAL_ERROR'
            ), 500
    
    @staticmethod
    def format_error_response(message, status_code=400, error_code='ERROR', extra_data=None):
        """Format error response with consistent structure"""
        response = {
            'status': 'error',
            'error': {
                'code': error_code,
                'message': message,
                'status_code': status_code
            }
        }
        
        if extra_data:
            response['error'].update(extra_data)
        
        return response

# ==================== DECORATORS ====================

def handle_errors(f):
    """Decorator to handle common errors in endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return ErrorHandler.format_error_response(
                e.message, e.status_code, e.error_code
            ), e.status_code
        except ModelError as e:
            return ErrorHandler.format_error_response(
                e.message, e.status_code, e.error_code
            ), e.status_code
        except Exception as e:
            logging.error(f"Error in {f.__name__}: {str(e)}")
            return ErrorHandler.format_error_response(
                'An error occurred processing your request',
                500,
                'INTERNAL_ERROR'
            ), 500
    
    return decorated_function

def require_json(f):
    """Decorator to ensure request has JSON data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return ErrorHandler.format_error_response(
                'Content-Type must be application/json',
                400,
                'INVALID_CONTENT_TYPE'
            ), 400
        
        if not request.get_json():
            return ErrorHandler.format_error_response(
                'Request body is empty',
                400,
                'EMPTY_REQUEST_BODY'
            ), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== ERROR LOGGING ====================

def setup_error_logging(app):
    """Configure error logging for the application"""
    logger = logging.getLogger('cardio_errors')
    
    # Create error log file handler
    if not app.debug:
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger
