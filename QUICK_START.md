# CardioPredict Backend v2.0 - Quick Reference Card

## 🚀 One-Minute Setup

```bash
# Install
pip install -r requirements.txt

# Train (if needed)
python train_model.py

# Verify
python verify_backend.py

# Run
python app.py
```

**Server**: http://localhost:5000

---

## 📊 9 Modules at a Glance

| Module | Lines | Purpose |
|--------|-------|---------|
| app.py | 1004 | Flask app + 11 APIs |
| config.py | 70 | Configuration management |
| logger.py | 67 | Logging with rotation |
| validators.py | 150 | Input validation (11 rules) |
| models.py | 180 | Data models (2 classes) |
| utils.py | 260 | 7 utility classes |
| errors.py | 180 | Error handling (6 exceptions) |
| rate_limiter.py | 200 | Rate limiting (60/min) |
| cache.py | 300 | Caching (3 layers) |

**Total: 2501 lines**

---

## 🔌 API Endpoints (11)

### Make Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 50, "gender": 2, "height": 165, "weight": 70,
    "ap_hi": 120, "ap_lo": 80, "cholesterol": 1, "gluc": 1,
    "smoke": 0, "alco": 0, "active": 1
  }'
```

### Get Prediction
```bash
curl http://localhost:5000/api/prediction/a1b2c3d4
```

### Get History
```bash
curl "http://localhost:5000/api/prediction-history?limit=10&offset=0"
```

### Get Statistics
```bash
curl http://localhost:5000/api/prediction-stats
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

### All 11 Endpoints
1. POST /api/predict
2. GET /api/prediction/<id>
3. POST /api/batch-predict
4. GET /api/prediction-status
5. GET /api/prediction-history
6. GET /api/prediction-stats
7. GET /api/health
8. GET /api/model-info
9. GET /api/prediction-health
10. GET /api/statistics
11. POST /api/clear-history

---

## ✅ Validation Rules (11 Fields)

| Field | Range | Type |
|-------|-------|------|
| age | 1-120 years | Integer |
| gender | 1-2 | Integer |
| height | 100-250 cm | Float |
| weight | 20-300 kg | Float |
| ap_hi | 40-300 mmHg | Integer |
| ap_lo | 40-300 mmHg | Integer |
| cholesterol | 0-3 | Integer |
| gluc | 0-3 | Integer |
| smoke | 0-1 | Boolean |
| alco | 0-1 | Boolean |
| active | 0-1 | Boolean |

---

## 🛡️ Security Features

**Rate Limiting**:
- 60 requests/minute per IP
- 1000 requests/hour per IP
- X-RateLimit-* headers

**Caching**:
- Predictions: 1 hour
- Statistics: 10 minutes
- History: 30 minutes

**Error Handling**:
- 6 custom exceptions
- Consistent error format
- No sensitive data exposure

---

## 📚 Key Docs

| Document | Purpose |
|----------|---------|
| BACKEND_SETUP.md | Complete setup (2000+ lines) |
| API_DOCUMENTATION.md | Full API specs |
| API_QUICK_REFERENCE.md | Quick examples |
| QUICK_FIX_GUIDE.md | Troubleshooting |
| BACKEND_COMPLETE.md | Feature checklist |

---

## 🔧 Configuration

### .env File
```
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
API_VERSION=2.0.0
RATE_LIMIT_REQUESTS=60
```

### Load Custom Config
```python
export FLASK_ENV=production
python app.py
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t cardio-predict .

# Run
docker run -p 5000:5000 cardio-predict
```

---

## 🌐 Production (Gunicorn)

```bash
# Install
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With auto-reload
gunicorn -w 4 -b 0.0.0.0:5000 --reload app:app
```

---

## 🆘 Troubleshooting

### Model Not Loaded
```bash
python train_model.py
```

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Change in .env:
FLASK_PORT=5001
```

### Rate Limit Errors
Check X-RateLimit-* headers - wait before retrying

---

## 📊 Response Format

### Success
```json
{
  "prediction": 0,
  "disease_probability": 0.25,
  "risk_percentage": 25.0,
  "risk_level": "Low Risk"
}
```

### Error
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

---

## 📈 Performance Tips

1. **Enable caching** - Automatic, reduces db calls
2. **Use batch predict** - Process multiple at once
3. **Monitor rate limits** - Watch X-RateLimit headers
4. **Check health** - /api/health before heavy load
5. **Review logs** - logs/cardio_app.log for issues

---

## ✨ Features Matrix

| Feature | Implemented | Details |
|---------|-------------|---------|
| API | ✅ | 11 endpoints |
| Validation | ✅ | 11 rules |
| Error Handling | ✅ | 6 exceptions |
| Rate Limiting | ✅ | 60/min, 1000/hr |
| Caching | ✅ | 3 layers |
| Logging | ✅ | File rotation |
| Health Check | ✅ | 3 endpoints |
| Batch Processing | ✅ | Up to 1000 |
| Documentation | ✅ | 5000+ lines |

---

## 🎯 Testing Checklist

- [ ] Health check: `curl http://localhost:5000/api/health`
- [ ] Single prediction: POST /api/predict with test data
- [ ] Batch prediction: POST /api/batch-predict with 3+ samples
- [ ] History: GET /api/prediction-history
- [ ] Statistics: GET /api/prediction-stats
- [ ] Rate limit: Make 61+ requests in 60 seconds (expect 429)
- [ ] Error handling: Send invalid JSON
- [ ] Model info: GET /api/model-info

---

## 🚀 Deployment Checklist

- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Model trained: `python train_model.py`
- [ ] Verification passed: `python verify_backend.py`
- [ ] Environment configured: Check .env
- [ ] Logs directory created: `mkdir -p logs`
- [ ] CORS origins set: Update CORS_ORIGINS in .env
- [ ] SECRET_KEY changed: Generate new key for production
- [ ] Database ready (optional): For persistence
- [ ] Redis ready (optional): For advanced caching
- [ ] Testing complete: All endpoints verified

---

## 📞 Support

**Quick Issues**:
- Model not found → `python train_model.py`
- Dependencies → `pip install -r requirements.txt`
- Port conflict → Change FLASK_PORT
- Rate limit → Wait or check limits

**Detailed Issues**:
- See QUICK_FIX_GUIDE.md
- Check logs/cardio_app.log
- Run verify_backend.py
- Read BACKEND_SETUP.md#troubleshooting

---

## 📋 Version Info

- **Version**: 2.0.0
- **Status**: Production Ready ✅
- **Framework**: Flask 2.3.0
- **ML**: scikit-learn Random Forest
- **Python**: 3.7+
- **Lines of Code**: 2501

---

## 🎓 Next Steps

1. **Read**: BACKEND_SETUP.md (comprehensive)
2. **Test**: curl http://localhost:5000/api/health
3. **Explore**: All 11 API endpoints
4. **Deploy**: Follow production section
5. **Monitor**: Check logs and cache stats

---

**Created**: January 2024  
**Status**: ✅ Production Ready  
**Maintenance**: Active development support  

For full documentation, see INDEX_COMPLETE.md
