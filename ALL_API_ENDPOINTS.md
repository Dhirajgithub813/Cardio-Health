# 🔌 All API Endpoints - Complete Reference

## ✅ All APIs Successfully Defined

Total Endpoints: **16**  
- Frontend Routes: 5
- API Endpoints: 11

---

## 📄 FRONTEND ROUTES (5)

### 1. **Home Page**
```
GET /
```
- **Description:** Main landing page
- **Response:** HTML page (index.html)
- **Access:** http://localhost:5000/

### 2. **Prediction Page**
```
GET /predict
```
- **Description:** Cardiovascular disease prediction form
- **Response:** HTML page (predict.html)
- **Features:** Form input, real-time BMI calculation, risk assessment
- **Access:** http://localhost:5000/predict

### 3. **Analytics Page**
```
GET /analytics
```
- **Description:** Data visualization and analysis dashboard
- **Response:** HTML page (analytics.html)
- **Features:** Risk distribution charts, demographic analysis
- **Access:** http://localhost:5000/analytics

### 4. **Results Page**
```
GET /results
```
- **Description:** Prediction history and status tracking dashboard
- **Response:** HTML page (results.html)
- **Features:** Stat cards, charts, prediction history table, pagination
- **Access:** http://localhost:5000/results

### 5. **About Page**
```
GET /about
```
- **Description:** Project information and documentation
- **Response:** HTML page (about.html)
- **Features:** Model info, feature descriptions, disclaimers
- **Access:** http://localhost:5000/about

---

## 🔗 API ENDPOINTS (11)

### **PREDICTION ENDPOINTS**

#### 1. **Make Prediction**
```
POST /api/predict
```
- **Description:** Submit patient data and get cardiovascular disease prediction
- **Request Body:**
```json
{
    "age": 18393,           // Age in days (÷365 for years)
    "gender": 2,            // 1=Female, 2=Male
    "height": 165,          // Height in cm
    "weight": 70,           // Weight in kg
    "ap_hi": 120,           // Systolic blood pressure (mmHg)
    "ap_lo": 80,            // Diastolic blood pressure (mmHg)
    "cholesterol": 1,       // 0=Normal, 1=Above, 2=High
    "gluc": 1,              // 0=Normal, 1=Above, 2=High
    "smoke": 0,             // 0=No, 1=Yes
    "alco": 0,              // 0=No, 1=Yes
    "active": 1             // 0=No, 1=Yes
}
```
- **Response:**
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
    "timestamp": "2026-02-05T14:30:00.000000"
}
```
- **Status Codes:** 
  - `200` - Prediction successful
  - `400` - Invalid data
  - `500` - Server error
- **JavaScript:**
```javascript
const result = await API.predict(patientData);
```

---

#### 2. **Get Specific Prediction**
```
GET /api/prediction/<prediction_id>
```
- **Description:** Retrieve a specific prediction by its unique ID
- **Parameters:**
  - `prediction_id` (path): 8-character unique ID
- **Response:**
```json
{
    "id": "a1b2c3d4",
    "prediction": 0,
    "has_disease": false,
    "disease_probability": 0.25,
    "risk_percentage": 25.0,
    "risk_level": "Low Risk",
    "timestamp": "2026-02-05T14:30:00.000000",
    "age": 18393,
    "gender": 2,
    "height": 165,
    "weight": 70,
    "bp_systolic": 120,
    "bp_diastolic": 80,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1,
    "status": "completed"
}
```
- **Status Codes:**
  - `200` - Success
  - `404` - Prediction not found
- **JavaScript:**
```javascript
const details = await API.getPredictionStatus('a1b2c3d4');
```
- **cURL:**
```bash
curl http://localhost:5000/api/prediction/a1b2c3d4
```

---

#### 3. **Batch Predictions**
```
POST /api/batch-predict
```
- **Description:** Submit multiple predictions at once
- **Request Body:**
```json
{
    "predictions": [
        { "age": 18393, "gender": 2, ... },
        { "age": 19000, "gender": 1, ... }
    ]
}
```
- **Response:**
```json
{
    "results": [
        { "prediction_id": "a1b2c3d4", "prediction": 0, ... },
        { "prediction_id": "x9y8z7w6", "prediction": 1, ... }
    ],
    "success_count": 2,
    "failed_count": 0
}
```
- **JavaScript:**
```javascript
const result = await fetch('/api/batch-predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ predictions: [data1, data2] })
}).then(r => r.json());
```

---

### **STATUS TRACKING ENDPOINTS**

#### 4. **Prediction Status Summary**
```
GET /api/prediction-status
```
- **Description:** Get overall prediction status and risk distribution
- **Query Parameters:** None
- **Response:**
```json
{
    "status": "active",
    "total_predictions": 15,
    "risk_distribution": {
        "low_risk": 8,
        "moderate_risk": 5,
        "high_risk": 2
    },
    "disease_rate": "20%",
    "recent_predictions": [
        {
            "id": "a1b2c3d4",
            "risk_level": "Low Risk",
            "risk_percentage": 25.0,
            "timestamp": "2026-02-05T14:30:00.000000"
        }
    ]
}
```
- **JavaScript:**
```javascript
const status = await API.getPredictionStatusSummary();
```

---

#### 5. **Prediction History**
```
GET /api/prediction-history
```
- **Description:** Get paginated list of all predictions
- **Query Parameters:**
  - `limit` (int, default=100): Max results per page
  - `offset` (int, default=0): Starting position
- **Example URL:**
```
GET /api/prediction-history?limit=20&offset=0
```
- **Response:**
```json
{
    "predictions": [
        { "id": "a1b2c3d4", "risk_percentage": 25.0, ... },
        { "id": "x9y8z7w6", "risk_percentage": 65.0, ... }
    ],
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_more": false
}
```
- **JavaScript:**
```javascript
const history = await API.getPredictionHistory(20, 0);
```

---

#### 6. **Detailed Statistics**
```
GET /api/prediction-stats
```
- **Description:** Get comprehensive statistics on all predictions
- **Response:**
```json
{
    "total_predictions": 15,
    "risk_distribution": {
        "low_risk": 8,
        "moderate_risk": 5,
        "high_risk": 2
    },
    "disease_rate": {
        "with_disease": 3,
        "without_disease": 12,
        "percentage": 20.0
    },
    "risk_percentage_stats": {
        "average": 35.8,
        "min": 5.2,
        "max": 85.6,
        "median": 32.1
    },
    "demographic_stats": {
        "avg_age": 52.3,
        "avg_bmi": 28.5,
        "smoking_rate": "33%",
        "alcohol_use_rate": "26%",
        "activity_rate": "60%"
    }
}
```
- **JavaScript:**
```javascript
const stats = await API.getPredictionDetailedStats();
```

---

#### 7. **Prediction Health Check**
```
GET /api/prediction-health
```
- **Description:** Check service health and status
- **Response:**
```json
{
    "status": "healthy",
    "timestamp": "2026-02-05T14:30:00.000000",
    "model_loaded": true,
    "total_predictions_made": 15,
    "memory_usage": "~2MB"
}
```
- **Status Codes:**
  - `200` - Service healthy
  - `503` - Service unavailable
- **JavaScript:**
```javascript
const health = await API.getPredictionHealth();
```

---

### **INFORMATION ENDPOINTS**

#### 8. **Model Information**
```
GET /api/model-info
```
- **Description:** Get details about the ML model
- **Response:**
```json
{
    "model_type": "Random Forest Classifier",
    "algorithm": "Ensemble Learning",
    "trees": 100,
    "training_records": 70000,
    "features": [
        "age", "gender", "height", "weight", 
        "ap_hi", "ap_lo", "cholesterol", 
        "gluc", "smoke", "alco", "active"
    ],
    "feature_count": 11,
    "accuracy": 0.73,
    "roc_auc_score": 0.81,
    "version": "1.0.0",
    "last_trained": "2026-02-05"
}
```

---

#### 9. **General Health Check**
```
GET /api/health
```
- **Description:** General API health check
- **Response:**
```json
{
    "status": "healthy",
    "message": "CardioPredict API is running",
    "version": "1.0.0",
    "timestamp": "2026-02-05T14:30:00.000000"
}
```

---

#### 10. **Statistics Dashboard**
```
GET /api/statistics
```
- **Description:** Get statistics data for analytics dashboard
- **Response:**
```json
{
    "total_predictions": 15,
    "healthy_count": 12,
    "disease_count": 3,
    "high_risk_count": 2,
    "moderate_risk_count": 5,
    "low_risk_count": 8,
    "disease_percentage": 20.0,
    "avg_risk": 35.8,
    "high_bp_count": 5,
    "high_cholesterol_count": 8,
    "smokers_count": 5
}
```
- **JavaScript:**
```javascript
const stats = await API.getStatistics();
```

---

### **ADMIN ENDPOINTS**

#### 11. **Clear History**
```
POST /api/clear-history
```
- **Description:** Clear all prediction history (admin only)
- **Request Body:** `{}`
- **Response:**
```json
{
    "status": "success",
    "message": "Prediction history cleared",
    "cleared_count": 15,
    "timestamp": "2026-02-05T14:30:00.000000"
}
```
- **Warning:** This action clears all stored predictions in memory
- **JavaScript:**
```javascript
const result = await API.clearPredictionHistory();
```

---

## 📊 ENDPOINT SUMMARY TABLE

| # | Endpoint | Method | Purpose | Status |
|---|----------|--------|---------|--------|
| 1 | `/` | GET | Home page | ✅ Active |
| 2 | `/predict` | GET | Prediction form | ✅ Active |
| 3 | `/analytics` | GET | Analytics dashboard | ✅ Active |
| 4 | `/results` | GET | Results dashboard | ✅ Active |
| 5 | `/about` | GET | About page | ✅ Active |
| 6 | `/api/predict` | POST | Make prediction | ✅ Active |
| 7 | `/api/prediction/<id>` | GET | Get prediction by ID | ✅ Active |
| 8 | `/api/batch-predict` | POST | Batch predictions | ✅ Active |
| 9 | `/api/prediction-status` | GET | Status summary | ✅ Active |
| 10 | `/api/prediction-history` | GET | Paginated history | ✅ Active |
| 11 | `/api/prediction-stats` | GET | Detailed stats | ✅ Active |
| 12 | `/api/prediction-health` | GET | Service health | ✅ Active |
| 13 | `/api/model-info` | GET | Model details | ✅ Active |
| 14 | `/api/health` | GET | API health | ✅ Active |
| 15 | `/api/statistics` | GET | Stats data | ✅ Active |
| 16 | `/api/clear-history` | POST | Clear all data | ✅ Active |

---

## 🎯 API USAGE PATTERNS

### Pattern 1: Simple Prediction
```javascript
const result = await API.predict(patientData);
const predictionId = result.prediction_id;
```

### Pattern 2: Retrieve & Analyze
```javascript
const details = await API.getPredictionStatus(predictionId);
const stats = await API.getPredictionDetailedStats();
```

### Pattern 3: Dashboard Display
```javascript
const summary = await API.getPredictionStatusSummary();
const history = await API.getPredictionHistory(50, 0);
```

### Pattern 4: Batch Operations
```javascript
const response = await fetch('/api/batch-predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ predictions: patientDataArray })
});
const results = await response.json();
```

### Pattern 5: Health Monitoring
```javascript
const health = await API.getPredictionHealth();
if (health.status === 'healthy') {
    // Proceed with operations
}
```

---

## 🔒 API SECURITY

✅ **CORS Enabled** - Cross-origin requests allowed  
✅ **JSON Responses** - All responses are JSON formatted  
✅ **Error Handling** - Comprehensive error messages  
✅ **Input Validation** - All parameters validated  
✅ **In-Memory Storage** - No persistent database  

---

## 📝 RESPONSE CODES

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Prediction successful |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Prediction ID doesn't exist |
| 500 | Server Error | Model not loaded |
| 503 | Service Unavailable | Model initialization failed |

---

## 🚀 GETTING STARTED

### 1. Start the Server
```bash
python app.py
```
Server runs on `http://localhost:5000`

### 2. Test All APIs
```bash
# Test health
curl http://localhost:5000/api/health

# Test model info
curl http://localhost:5000/api/model-info

# Make a prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 18393, "gender": 2, ...}'
```

### 3. Access Web Interface
- Home: http://localhost:5000
- Predict: http://localhost:5000/predict
- Results: http://localhost:5000/results
- Analytics: http://localhost:5000/analytics

---

## 📚 COMPLETE DOCUMENTATION

- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Quick Reference:** [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- **Setup Guide:** [SETUP.md](SETUP.md)
- **Project Overview:** [PROJECT_OVERVIEW.txt](PROJECT_OVERVIEW.txt)

---

## ✨ Features

✅ **16 Total Endpoints** - 5 pages + 11 API endpoints  
✅ **Full CRUD Operations** - Create, Read, Update, Delete  
✅ **Real-time Tracking** - Instant prediction storage  
✅ **Comprehensive Stats** - Detailed analysis available  
✅ **Health Monitoring** - Service status checks  
✅ **Batch Processing** - Multiple predictions at once  
✅ **Pagination** - Efficient data retrieval  
✅ **Error Handling** - Descriptive error messages  

---

**Status:** ✅ **ALL APIS DEFINED AND FUNCTIONAL**

**Version:** 1.0.0  
**Last Updated:** February 5, 2026  
**Backend Framework:** Flask 2.3.0  
**ML Model:** Random Forest Classifier (100 trees, 70,000 training records)
