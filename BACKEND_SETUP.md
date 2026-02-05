# CardioPredict Backend v2.0 - Complete Setup Guide

## Overview

The CardioPredict backend is a production-ready Flask API with comprehensive error handling, rate limiting, caching, and logging. This guide covers all backend components and integration.

## Project Structure

```
├── app.py                    # Main Flask application (1004 lines)
├── config.py                 # Configuration management (70 lines)
├── logger.py                 # Logging system (67 lines)
├── validators.py             # Input validation (150 lines)
├── models.py                 # Data models (180 lines)
├── utils.py                  # Utility functions (260 lines)
├── errors.py                 # Error handling (NEW - 180 lines)
├── rate_limiter.py           # Rate limiting (NEW - 200 lines)
├── cache.py                  # Caching layer (NEW - 300 lines)
├── train_model.py            # Model training
├── cardio_train (1).csv      # Training dataset (70K records)
├── cardio_model.pkl          # Trained ML model
├── scaler.pkl                # Feature scaler
├── feature_names.pkl         # Feature list
├── requirements.txt          # Dependencies
├── .env                       # Environment config
├── templates/                # HTML templates (5 files)
└── static/                   # Frontend assets (JS, CSS)
```

## Backend Modules (v2.0)

### 1. app.py (Main Application - 1004 lines)

**Purpose**: Core Flask application with all API endpoints

**Key Components**:
- Flask app initialization with CORS
- Configuration loading from config.py
- Logging setup
- ML model loading
- Global state management (prediction history, statistics)
- 16 API endpoints (see below)
- Error handlers
- Frontend routes (5 pages)

**Core Endpoints**:
```
POST   /api/predict              - Single prediction
GET    /api/prediction/<id>      - Retrieve prediction
POST   /api/batch-predict        - Batch predictions
GET    /api/prediction-status    - Overall status
GET    /api/prediction-history   - Paginated history
GET    /api/prediction-stats     - Detailed statistics
GET    /api/model-info           - Model information
GET    /api/health               - Health check
GET    /api/prediction-health    - Service health
GET    /api/statistics           - Dataset statistics
POST   /api/clear-history        - Clear history (admin)
```

### 2. config.py (Configuration Management - 70 lines)

**Purpose**: Environment-based configuration

**Classes**:
- `Config` - Base configuration
- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings
- `TestingConfig` - Test settings

**Key Settings**:
```python
SQLALCHEMY_DATABASE_URI      # Database URL
CORS_ORIGINS                 # CORS allowed origins
MAX_CONTENT_LENGTH           # Upload limit (16MB)
API_VERSION                  # API version (2.0.0)
LOG_LEVEL                    # Logging level
MODEL_FILE                   # Model file path
PREDICTION_RETENTION_HOURS   # Cache retention
```

### 3. logger.py (Logging System - 67 lines)

**Purpose**: Production logging with file rotation

**Functions**:
- `setup_logging(app, config)` - Initialize logging
- `log_prediction(app, id, data, risk)` - Log predictions
- `log_api_call(app, method, endpoint, status)` - Log API calls
- `log_error(app, error_type, message, context)` - Log errors

**Features**:
- Console and file handlers
- 10MB file rotation
- 10 backup files
- ISO format timestamps
- Automatic startup logging

### 4. validators.py (Input Validation - 150 lines)

**Purpose**: Comprehensive input validation

**Class**: `PredictionValidator`

**Validation Rules**:
```python
age          # 1-120 years (user input)
gender       # 1-2 (Female/Male)
height       # 100-250 cm
weight       # 20-300 kg
ap_hi        # 40-300 mmHg (systolic > diastolic)
ap_lo        # 40-300 mmHg
cholesterol  # 0-3
gluc         # 0-3
smoke        # 0-1 boolean
alco         # 0-1 boolean
active       # 0-1 boolean
```

**Methods**:
- `validate(data)` - Returns (is_valid, error_message)
- `validate_batch(predictions)` - Validate up to 1000 predictions

### 5. models.py (Data Models - 180 lines)

**Purpose**: Data model classes for predictions and statistics

**Classes**:
- `PredictionRecord` - Individual prediction record
- `StatisticsRecord` - Aggregated statistics

**Features**:
- `to_dict()` method for JSON serialization
- SQLAlchemy ORM template for database migration
- Complete field tracking (age, demographics, health metrics)

### 6. utils.py (Utility Functions - 260 lines)

**Purpose**: Reusable backend operations

**Classes**:
- `AgeConverter` - Years ↔ Days conversion
- `RiskAssessor` - Probability → Risk level mapping
- `BMICalculator` - BMI calculation and categorization
- `DataPreprocessor` - Normalize input for ML model
- `ResponseFormatter` - Format API responses
- `HealthCheck` - System health status
- `DateUtils` - Timestamp utilities

### 7. errors.py (Error Handling - 180 lines) - NEW

**Purpose**: Centralized error handling and custom exceptions

**Custom Exceptions**:
- `PredictionError` - Base exception
- `ValidationError` - Input validation errors
- `ModelError` - ML model errors
- `DatabaseError` - Database errors
- `NotFoundError` - Resource not found
- `RateLimitError` - Rate limit exceeded

**ErrorHandler Class**:
- `register_handlers(app)` - Register error handlers
- `format_error_response()` - Format error responses

**Decorators**:
- `@handle_errors` - Catch common exceptions
- `@require_json` - Ensure JSON request

### 8. rate_limiter.py (Rate Limiting - 200 lines) - NEW

**Purpose**: Protect API from abuse

**RateLimiter Class**:
- 60 requests/minute per IP
- 1000 requests/hour per IP
- IP-based tracking
- Automatic cleanup

**Features**:
- `is_rate_limited()` - Check if client exceeded limits
- `get_limit_info()` - Get current limits
- `reset_client()` - Reset for specific IP

**Decorators**:
- `@rate_limit()` - Apply rate limiting to endpoints
- `@rate_limit_per_endpoint()` - Custom per-endpoint limits

**Manager**:
- RateLimitManager for centralized management
- X-RateLimit-* response headers

### 9. cache.py (Caching Layer - 300 lines) - NEW

**Purpose**: Improve performance with result caching

**CacheManager**:
- In-memory cache with TTL
- Automatic expiration cleanup
- Hit rate statistics

**Specialized Caches**:
- `PredictionCache` - Cache prediction results (1 hour)
- `StatisticsCache` - Cache statistics (10 minutes)
- `HistoryCache` - Cache paginated history (30 minutes)

**Decorators**:
- `@cache_result()` - Cache function results
- `@cache_prediction_result()` - Cache predictions

**Manager Functions**:
- `configure()` - Set up caching
- `get_all_stats()` - Cache statistics
- `cleanup_all()` - Remove expired entries
- `clear_all()` - Clear all caches

## Installation & Setup

### 1. Prerequisites

- Python 3.7+
- pip package manager
- Virtual environment (recommended)

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy and customize .env file
cp .env .env.local
# Edit .env.local with your settings
```

### 4. Train ML Model

```bash
# Train the model (if not already trained)
python train_model.py
```

### 5. Start Backend Server

```bash
# Development mode (with auto-reload)
python app.py

# Or using Flask CLI
FLASK_ENV=development FLASK_APP=app.py flask run

# Production mode
FLASK_ENV=production python app.py

# Using Gunicorn (production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Server will run at `http://localhost:5000`

## API Usage Examples

### 1. Single Prediction

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 50,
    "gender": 2,
    "height": 165,
    "weight": 70,
    "ap_hi": 120,
    "ap_lo": 80,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1
  }'
```

**Response**:
```json
{
  "prediction_id": "a1b2c3d4",
  "prediction": 0,
  "has_disease": false,
  "disease_probability": 0.25,
  "healthy_probability": 0.75,
  "risk_percentage": 25.0,
  "risk_level": "Low Risk",
  "color": "green",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. Batch Predictions

```bash
curl -X POST http://localhost:5000/api/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {"age": 45, "gender": 1, ...},
      {"age": 55, "gender": 2, ...}
    ]
  }'
```

### 3. Get Prediction History

```bash
curl "http://localhost:5000/api/prediction-history?limit=10&offset=0"
```

### 4. Get Statistics

```bash
curl "http://localhost:5000/api/prediction-stats"
```

### 5. Health Check

```bash
curl "http://localhost:5000/api/health"
```

## Configuration

### Environment Variables (.env)

**Application**:
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
```

**Server**:
```
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

**Logging**:
```
LOG_LEVEL=DEBUG
LOG_FILE=logs/cardio_app.log
LOG_MAX_SIZE=10485760
```

**API**:
```
API_VERSION=2.0.0
MAX_CONTENT_LENGTH=16777216
```

**Rate Limiting**:
```
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_PERIOD=3600
```

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Age must be between 1 and 120 years",
    "status_code": 400
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Invalid input |
| MODEL_NOT_LOADED | 503 | ML model not available |
| MODEL_ERROR | 503 | Model prediction failed |
| NOT_FOUND | 404 | Resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Rate Limiting

**Limits**:
- 60 requests/minute per IP
- 1000 requests/hour per IP

**Response Headers**:
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 45
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 950
```

**Rate Limit Error (HTTP 429)**:
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "status_code": 429,
    "limits": {
      "limit_per_minute": 60,
      "remaining_minute": 0
    }
  }
}
```

## Caching

**Cache Layers**:
- Prediction cache: 1 hour TTL
- Statistics cache: 10 minutes TTL
- History cache: 30 minutes TTL

**Cache Statistics Endpoint** (add to app.py if needed):
```python
@app.route('/api/cache-stats', methods=['GET'])
def cache_stats():
    return jsonify(CacheManager.get_all_stats()), 200
```

## Logging

**Log Files**:
- `logs/cardio_app.log` - Application logs
- `logs/errors.log` - Error logs (production)

**Log Format**:
```
2024-01-01 12:00:00,123 - cardio_app - INFO - Message
```

**Log Levels**:
- DEBUG - Detailed debug information
- INFO - General informational messages
- WARNING - Warning messages
- ERROR - Error messages
- CRITICAL - Critical errors

## Database Integration (Future)

The models.py includes SQLAlchemy template for database integration:

```python
# Uncomment in models.py when upgrading to database:
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

# class PredictionRecord(db.Model):
#     id = db.Column(db.String(50), primary_key=True)
#     prediction = db.Column(db.Integer, nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

## Monitoring & Maintenance

### Check Health
```bash
curl http://localhost:5000/api/health
```

### Monitor Cache
```bash
# Add endpoint to app.py:
@app.route('/api/cache/stats', methods=['GET'])
def cache_stats():
    return jsonify(CacheManager.get_all_stats()), 200
```

### Clean Up Expired Cache
```bash
# Add background task or manual endpoint:
CacheManager.cleanup_all()
```

### Monitor Rate Limiting
```bash
# Get rate limit stats
RateLimitManager.get_stats()

# Reset client limit
RateLimitManager.reset_limit(client_ip)
```

## Troubleshooting

### Issue: Model not loaded
**Solution**: Run `python train_model.py` to train the model

### Issue: Rate limit errors
**Solution**: Reduce request frequency or configure higher limits in .env

### Issue: Cache size grows
**Solution**: Increase cleanup frequency or reduce TTL values

### Issue: Database connection errors
**Solution**: Check DATABASE_URL in .env is correct

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with production settings
gunicorn -w 4 -b 0.0.0.0:5000 -t 60 app:app

# With auto-reload monitoring
gunicorn -w 4 -b 0.0.0.0:5000 --reload app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Using uWSGI

```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

## Performance Optimization

1. **Enable Caching**: All cache layers enabled by default
2. **Rate Limiting**: Protects against abuse
3. **Connection Pooling**: Use with database (future)
4. **Compression**: Enable gzip in reverse proxy
5. **CDN**: Use for static files (CSS, JS)

## Security Considerations

1. **CORS**: Configure allowed origins in config.py
2. **Rate Limiting**: Enabled by default
3. **Input Validation**: All inputs validated
4. **Error Messages**: Don't expose internal details
5. **Logging**: Sensitive data excluded from logs
6. **Environment Variables**: Keep secrets in .env

## API Documentation

For complete API documentation, see:
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [ALL_API_ENDPOINTS.md](ALL_API_ENDPOINTS.md)
- [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)

## Support & Debugging

### Enable Debug Logging

```python
# In app.py or .env:
LOG_LEVEL=DEBUG
FLASK_DEBUG=True
```

### Test Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Model info
curl http://localhost:5000/api/model-info

# Statistics
curl http://localhost:5000/api/statistics

# Rate limit headers
curl -i http://localhost:5000/api/health
```

## Version History

- **v2.0.0** (Current) - Enhanced backend with error handling, rate limiting, caching
- **v1.0.0** - Initial release with basic API endpoints

---

**Last Updated**: January 2024
**Maintainer**: AI Development Team
