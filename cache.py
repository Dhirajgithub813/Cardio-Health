"""
Caching Layer for Prediction Results
Improves performance by caching prediction results and statistics
"""

from datetime import datetime, timedelta
import hashlib
import json
import logging

# ==================== CACHE MANAGER ====================

class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, default_ttl_seconds=3600):
        self.cache = {}  # {key: {'value': obj, 'created_at': datetime, 'ttl': seconds}}
        self.default_ttl = default_ttl_seconds
        self.logger = logging.getLogger('cardio_cache')
        self.hit_count = 0
        self.miss_count = 0
    
    def set(self, key, value, ttl=None):
        """Store value in cache with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'created_at': datetime.now(),
            'ttl': ttl
        }
        
        self.logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def get(self, key):
        """Retrieve value from cache if not expired"""
        if key not in self.cache:
            self.miss_count += 1
            self.logger.debug(f"Cache MISS: {key}")
            return None
        
        entry = self.cache[key]
        age = (datetime.now() - entry['created_at']).total_seconds()
        
        if age > entry['ttl']:
            # Expired, remove and return None
            del self.cache[key]
            self.miss_count += 1
            self.logger.debug(f"Cache EXPIRED: {key} (age: {age}s, TTL: {entry['ttl']}s)")
            return None
        
        self.hit_count += 1
        self.logger.debug(f"Cache HIT: {key} (age: {age:.1f}s)")
        return entry['value']
    
    def delete(self, key):
        """Remove value from cache"""
        if key in self.cache:
            del self.cache[key]
            self.logger.debug(f"Cache DELETE: {key}")
            return True
        return False
    
    def clear(self):
        """Clear entire cache"""
        count = len(self.cache)
        self.cache.clear()
        self.logger.info(f"Cache CLEARED: {count} entries removed")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            age = (now - entry['created_at']).total_seconds()
            if age > entry['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleanup removed {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hit_count,
            'misses': self.miss_count,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2),
            'ttl_seconds': self.default_ttl
        }

# ==================== SPECIALIZED CACHES ====================

class PredictionCache(CacheManager):
    """Cache for prediction results"""
    
    def __init__(self):
        super().__init__(default_ttl_seconds=3600)  # 1 hour
    
    def generate_key(self, age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active):
        """Generate cache key from prediction input"""
        data = f"{age}-{gender}-{height}-{weight}-{ap_hi}-{ap_lo}-{cholesterol}-{gluc}-{smoke}-{alco}-{active}"
        return f"pred_{hashlib.md5(data.encode()).hexdigest()}"
    
    def cache_prediction(self, inputs, result, ttl=3600):
        """Cache a prediction result"""
        key = self.generate_key(**inputs)
        self.set(key, {
            'inputs': inputs,
            'result': result,
            'cached_at': datetime.now().isoformat()
        }, ttl)
        return key
    
    def get_cached_prediction(self, inputs):
        """Retrieve cached prediction"""
        key = self.generate_key(**inputs)
        return self.get(key)

class StatisticsCache(CacheManager):
    """Cache for statistics and aggregated data"""
    
    def __init__(self):
        super().__init__(default_ttl_seconds=600)  # 10 minutes
    
    def cache_stats(self, stats_type, data, ttl=600):
        """Cache statistics"""
        key = f"stats_{stats_type}"
        self.set(key, {
            'type': stats_type,
            'data': data,
            'cached_at': datetime.now().isoformat()
        }, ttl)
        return key
    
    def get_cached_stats(self, stats_type):
        """Retrieve cached statistics"""
        key = f"stats_{stats_type}"
        return self.get(key)

class HistoryCache(CacheManager):
    """Cache for prediction history"""
    
    def __init__(self):
        super().__init__(default_ttl_seconds=1800)  # 30 minutes
    
    def cache_history(self, limit, offset, data, ttl=1800):
        """Cache paginated history"""
        key = f"history_{limit}_{offset}"
        self.set(key, {
            'limit': limit,
            'offset': offset,
            'data': data,
            'cached_at': datetime.now().isoformat()
        }, ttl)
        return key
    
    def get_cached_history(self, limit, offset):
        """Retrieve cached history"""
        key = f"history_{limit}_{offset}"
        return self.get(key)
    
    def invalidate_history(self):
        """Invalidate all history cache (when new prediction added)"""
        keys_to_delete = [k for k in self.cache.keys() if k.startswith('history_')]
        for key in keys_to_delete:
            self.delete(key)
        return len(keys_to_delete)

# ==================== GLOBAL CACHE INSTANCES ====================

prediction_cache = PredictionCache()
statistics_cache = StatisticsCache()
history_cache = HistoryCache()

# ==================== CACHE DECORATORS ====================

def cache_result(cache_manager, ttl=None):
    """Decorator to cache function results"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"func_{f.__name__}_{json.dumps([args, kwargs], default=str, sort_keys=True)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Compute and cache result
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def cache_prediction_result(ttl=3600):
    """Decorator specifically for caching prediction results"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, dict) and 'inputs' in result:
                key = prediction_cache.cache_prediction(result['inputs'], result, ttl)
            return result
        return wrapper
    return decorator

# ==================== CACHE MANAGEMENT ====================

class CacheManager:
    """Centralized cache management"""
    
    @staticmethod
    def configure(app, config):
        """Configure caching based on settings"""
        cache_type = config.get('CACHE_TYPE', 'simple')
        ttl = config.get('CACHE_DEFAULT_TIMEOUT', 300)
        
        if cache_type == 'redis':
            app.logger.info(f"Configuring Redis cache (TTL: {ttl}s)")
            # TODO: Implement Redis caching
        else:
            app.logger.info(f"Using in-memory cache (TTL: {ttl}s)")
    
    @staticmethod
    def get_all_stats():
        """Get statistics for all caches"""
        return {
            'prediction_cache': prediction_cache.get_stats(),
            'statistics_cache': statistics_cache.get_stats(),
            'history_cache': history_cache.get_stats()
        }
    
    @staticmethod
    def cleanup_all():
        """Clean up expired entries in all caches"""
        stats = {
            'prediction': prediction_cache.cleanup_expired(),
            'statistics': statistics_cache.cleanup_expired(),
            'history': history_cache.cleanup_expired()
        }
        return stats
    
    @staticmethod
    def clear_all():
        """Clear all caches"""
        prediction_cache.clear()
        statistics_cache.clear()
        history_cache.clear()
    
    @staticmethod
    def invalidate_dependent_caches():
        """Invalidate caches when model or data changes"""
        # Clear statistics caches (depend on predictions)
        stats_keys = [k for k in statistics_cache.cache.keys() if k.startswith('stats_')]
        for key in stats_keys:
            statistics_cache.delete(key)
        
        # Clear history caches
        history_cache.invalidate_history()

# ==================== WARMUP ====================

def warmup_cache(app, prediction_stats):
    """Warm up cache with initial statistics"""
    try:
        summary = prediction_stats.get_summary()
        statistics_cache.cache_stats('summary', summary, ttl=600)
        app.logger.info("Cache warmed up with initial statistics")
    except Exception as e:
        app.logger.warning(f"Failed to warm cache: {e}")
