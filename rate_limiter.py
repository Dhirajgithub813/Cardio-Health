"""
Rate Limiting and Request Throttling
Protects API from abuse and ensures fair resource usage
"""

from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify
import logging

# ==================== RATE LIMITER ====================

class RateLimiter:
    """Simple rate limiting based on IP address"""
    
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_history = {}  # {ip: [(timestamp, endpoint)]}
        self.logger = logging.getLogger('cardio_rate_limit')
    
    def get_client_ip(self):
        """Get client IP address from request"""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        return request.remote_addr
    
    def is_rate_limited(self, endpoint=None):
        """Check if client exceeds rate limit"""
        client_ip = self.get_client_ip()
        now = datetime.now()
        
        # Initialize tracking for new IP
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        
        # Clean up old entries
        cutoff_time = now - timedelta(hours=1)
        self.request_history[client_ip] = [
            (timestamp, ep) for timestamp, ep in self.request_history[client_ip]
            if timestamp > cutoff_time
        ]
        
        # Check minute limit
        recent_requests = [
            (timestamp, ep) for timestamp, ep in self.request_history[client_ip]
            if (now - timestamp).total_seconds() < 60
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            self.logger.warning(
                f"Rate limit (minute) exceeded for IP {client_ip}: "
                f"{len(recent_requests)} requests in last minute"
            )
            return True
        
        # Check hour limit
        if len(self.request_history[client_ip]) >= self.requests_per_hour:
            self.logger.warning(
                f"Rate limit (hour) exceeded for IP {client_ip}: "
                f"{len(self.request_history[client_ip])} requests in last hour"
            )
            return True
        
        # Record this request
        self.request_history[client_ip].append((now, endpoint))
        return False
    
    def get_limit_info(self):
        """Get rate limit information for current client"""
        client_ip = self.get_client_ip()
        now = datetime.now()
        
        if client_ip not in self.request_history:
            return {
                'limit_per_minute': self.requests_per_minute,
                'limit_per_hour': self.requests_per_hour,
                'current_minute': 0,
                'current_hour': 0,
                'remaining_minute': self.requests_per_minute,
                'remaining_hour': self.requests_per_hour
            }
        
        # Count recent requests
        all_requests = self.request_history[client_ip]
        minute_requests = len([
            (t, ep) for t, ep in all_requests
            if (now - t).total_seconds() < 60
        ])
        hour_requests = len(all_requests)
        
        return {
            'limit_per_minute': self.requests_per_minute,
            'limit_per_hour': self.requests_per_hour,
            'current_minute': minute_requests,
            'current_hour': hour_requests,
            'remaining_minute': max(0, self.requests_per_minute - minute_requests),
            'remaining_hour': max(0, self.requests_per_hour - hour_requests)
        }
    
    def reset_client(self):
        """Reset rate limit for current client (admin function)"""
        client_ip = self.get_client_ip()
        if client_ip in self.request_history:
            del self.request_history[client_ip]
            self.logger.info(f"Rate limit reset for IP {client_ip}")
            return True
        return False

# ==================== GLOBAL RATE LIMITER ====================
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)

# ==================== DECORATORS ====================

def rate_limit(limit_per_minute=60, limit_per_hour=1000):
    """Decorator to apply rate limiting to endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if rate_limiter.is_rate_limited(f.__name__):
                limit_info = rate_limiter.get_limit_info()
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many requests. Please try again later.',
                        'status_code': 429,
                        'limits': limit_info
                    }
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit_per_endpoint(minute=60, hour=1000):
    """Alternative rate limiter with custom limits per endpoint"""
    def decorator(f):
        limiter = RateLimiter(requests_per_minute=minute, requests_per_hour=hour)
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if limiter.is_rate_limited(f.__name__):
                limit_info = limiter.get_limit_info()
                return jsonify({
                    'status': 'error',
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Too many requests for this endpoint.',
                        'status_code': 429,
                        'limits': limit_info
                    }
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# ==================== RATE LIMIT MANAGEMENT ====================

class RateLimitManager:
    """Manager for rate limiting across the application"""
    
    @staticmethod
    def configure_limits(app, config):
        """Configure rate limiting based on environment"""
        requests_per_minute = config.get('RATE_LIMIT_REQUESTS', 60)
        requests_per_hour = config.get('RATE_LIMIT_REQUESTS_HOUR', 1000)
        
        global rate_limiter
        rate_limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour
        )
        
        app.logger.info(
            f"Rate limiter configured: "
            f"{requests_per_minute} req/min, {requests_per_hour} req/hour"
        )
    
    @staticmethod
    def get_stats():
        """Get rate limiting statistics"""
        total_ips = len(rate_limiter.request_history)
        total_requests = sum(
            len(requests) for requests in rate_limiter.request_history.values()
        )
        
        return {
            'total_ips_tracked': total_ips,
            'total_requests_tracked': total_requests,
            'requests_per_minute_limit': rate_limiter.requests_per_minute,
            'requests_per_hour_limit': rate_limiter.requests_per_hour
        }
    
    @staticmethod
    def get_client_stats(client_ip=None):
        """Get rate limit stats for specific client"""
        if client_ip is None:
            client_ip = request.remote_addr
        
        if client_ip not in rate_limiter.request_history:
            return None
        
        requests = rate_limiter.request_history[client_ip]
        return {
            'client_ip': client_ip,
            'total_requests': len(requests),
            'requests': [(t.isoformat(), ep) for t, ep in requests]
        }
    
    @staticmethod
    def reset_limit(client_ip=None):
        """Reset rate limit for client"""
        if client_ip is None:
            client_ip = request.remote_addr
        
        if client_ip in rate_limiter.request_history:
            del rate_limiter.request_history[client_ip]
            return True
        return False

# ==================== MIDDLEWARE ====================

def apply_rate_limit_headers(app):
    """Apply rate limit headers to all responses"""
    @app.after_request
    def add_rate_limit_headers(response):
        limit_info = rate_limiter.get_limit_info()
        
        response.headers['X-RateLimit-Limit-Minute'] = str(limit_info['limit_per_minute'])
        response.headers['X-RateLimit-Remaining-Minute'] = str(limit_info['remaining_minute'])
        response.headers['X-RateLimit-Limit-Hour'] = str(limit_info['limit_per_hour'])
        response.headers['X-RateLimit-Remaining-Hour'] = str(limit_info['remaining_hour'])
        
        return response
