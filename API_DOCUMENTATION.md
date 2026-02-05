# CardioPredict - Prediction Status API Documentation

## Overview

The Prediction Status API allows you to track, retrieve, and manage cardiovascular disease predictions made through the CardioPredict system. All endpoints return JSON responses.

---

## Base URL

```
http://localhost:5000/api
```

---

## API Endpoints

### 1. Make a Single Prediction
**Endpoint:** `POST /api/predict`

**Description:** Submit patient health data to receive a cardiovascular disease prediction

**Request:**
```json
{
    "age": 18393,
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
}
```

**Response:**
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
    "timestamp": "2024-02-05T14:30:00.000000"
}
```

**Status Code:** 200 OK

---

### 2. Get Prediction by ID
**Endpoint:** `GET /api/prediction/{prediction_id}`

**Description:** Retrieve a specific prediction result using its unique ID

**Example:** `GET /api/prediction/a1b2c3d4`

**Response:**
```json
{
    "status": "found",
    "prediction": {
        "id": "a1b2c3d4",
        "prediction": 0,
        "has_disease": false,
        "disease_probability": 0.25,
        "healthy_probability": 0.75,
        "risk_percentage": 25.0,
        "risk_level": "Low Risk",
        "color": "green",
        "timestamp": "2024-02-05T14:30:00.000000",
        "age": 18393,
        "gender": 2,
        "height": 165,
        "weight": 70,
        "bp_systolic": 120,
        "bp_diastolic": 80,
        "status": "completed"
    },
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK (or 404 if not found)

---

### 3. Get Prediction Status Summary
**Endpoint:** `GET /api/prediction-status`

**Description:** Get overall prediction statistics and the 10 most recent predictions

**Response:**
```json
{
    "status": "active",
    "total_predictions": 25,
    "risk_distribution": {
        "low_risk": 12,
        "moderate_risk": 8,
        "high_risk": 5
    },
    "recent_predictions": [
        {
            "id": "a1b2c3d4",
            "risk_percentage": 25.0,
            "risk_level": "Low Risk",
            "timestamp": "2024-02-05T14:30:00.000000"
        }
        // ... more predictions
    ],
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK

---

### 4. Get Full Prediction History
**Endpoint:** `GET /api/prediction-history`

**Description:** Retrieve paginated list of all predictions with optional limit and offset

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Example:** `GET /api/prediction-history?limit=20&offset=0`

**Response:**
```json
{
    "status": "success",
    "total_records": 25,
    "returned": 20,
    "limit": 20,
    "offset": 0,
    "predictions": [
        {
            "id": "a1b2c3d4",
            "prediction": 0,
            "has_disease": false,
            "disease_probability": 0.25,
            "healthy_probability": 0.75,
            "risk_percentage": 25.0,
            "risk_level": "Low Risk",
            "color": "green",
            "timestamp": "2024-02-05T14:30:00.000000",
            "age": 18393,
            "gender": 2,
            "height": 165,
            "weight": 70,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "status": "completed"
        }
        // ... more predictions
    ],
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK

---

### 5. Get Detailed Prediction Statistics
**Endpoint:** `GET /api/prediction-stats`

**Description:** Get comprehensive statistics about all predictions made

**Response:**
```json
{
    "status": "success",
    "total_predictions": 25,
    "risk_distribution": {
        "low_risk": 12,
        "moderate_risk": 8,
        "high_risk": 5
    },
    "disease_rate": {
        "percentage": 20.0,
        "with_disease": 5,
        "without_disease": 20
    },
    "risk_percentage_stats": {
        "min": 5.2,
        "max": 85.6,
        "average": 35.8
    },
    "age_stats": {
        "min": 10950,
        "max": 25550,
        "average": 18293.5
    },
    "weight_stats": {
        "min": 55.0,
        "max": 95.5,
        "average": 72.4
    },
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK

---

### 6. Get Prediction Service Health
**Endpoint:** `GET /api/prediction-health`

**Description:** Check if the prediction service is running and available

**Response:**
```json
{
    "status": "healthy",
    "service": "prediction",
    "model_loaded": true,
    "total_predictions_made": 25,
    "prediction_history_count": 25,
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK

---

### 7. Clear Prediction History
**Endpoint:** `POST /api/clear-history`

**Description:** Delete all stored predictions and reset statistics (admin only)

**Request:** No body required

**Response:**
```json
{
    "status": "success",
    "message": "Cleared 25 predictions from history",
    "timestamp": "2024-02-05T14:35:00.000000"
}
```

**Status Code:** 200 OK

---

## Other Available Endpoints

### Batch Predictions
**Endpoint:** `POST /api/batch-predict`

Submit multiple predictions at once for processing

**Request:**
```json
[
    {
        "age": 18393,
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
    },
    // ... more predictions
]
```

### Dataset Statistics
**Endpoint:** `GET /api/statistics`

Get statistics about the training dataset

### Model Information
**Endpoint:** `GET /api/model-info`

Get information about the ML model

### Health Check
**Endpoint:** `GET /api/health`

Basic server health check

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Missing field: age"
}
```

### 404 Not Found
```json
{
    "error": "Not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error"
}
```

---

## Input Parameters Reference

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| age | Integer | 0-35000 | Age in days (divide years by 365) |
| gender | Integer | 1-2 | 1=Male, 2=Female |
| height | Integer | 140-210 | Height in centimeters |
| weight | Float | 40-150 | Weight in kilograms |
| ap_hi | Integer | 90-180 | Systolic blood pressure (mmHg) |
| ap_lo | Integer | 60-120 | Diastolic blood pressure (mmHg) |
| cholesterol | Integer | 0-3 | 0=Normal, 1=Above Normal, 2=Well Above, 3=High |
| gluc | Integer | 0-3 | 0=Normal, 1=Above Normal, 2=Well Above, 3=High |
| smoke | Integer | 0-1 | 0=Non-smoker, 1=Current smoker |
| alco | Integer | 0-1 | 0=No consumption, 1=Yes |
| active | Integer | 0-1 | 0=Inactive, 1=Physically active |

---

## JavaScript Client Examples

### Using the Built-in API Helper

```javascript
// Make a prediction
const result = await API.predict({
    age: 18393,
    gender: 2,
    height: 165,
    weight: 70,
    ap_hi: 120,
    ap_lo: 80,
    cholesterol: 1,
    gluc: 1,
    smoke: 0,
    alco: 0,
    active: 1
});

// Get prediction status summary
const status = await API.getPredictionStatusSummary();

// Get specific prediction
const prediction = await API.getPredictionStatus('a1b2c3d4');

// Get full history
const history = await API.getPredictionHistory(50, 0);

// Get detailed statistics
const stats = await API.getPredictionDetailedStats();

// Check service health
const health = await API.getPredictionHealth();

// Clear history
const cleared = await API.clearPredictionHistory();
```

---

## cURL Examples

### Make a Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 18393,
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

### Get Prediction Status
```bash
curl http://localhost:5000/api/prediction-status
```

### Get Prediction History
```bash
curl "http://localhost:5000/api/prediction-history?limit=20&offset=0"
```

### Get Statistics
```bash
curl http://localhost:5000/api/prediction-stats
```

### Check Health
```bash
curl http://localhost:5000/api/prediction-health
```

---

## Python Examples

```python
import requests

API_BASE = 'http://localhost:5000/api'

# Make a prediction
data = {
    "age": 18393,
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
}

response = requests.post(f'{API_BASE}/predict', json=data)
result = response.json()
prediction_id = result['prediction_id']

# Get prediction status
response = requests.get(f'{API_BASE}/prediction/{prediction_id}')
prediction = response.json()

# Get all predictions
response = requests.get(f'{API_BASE}/prediction-history?limit=50')
history = response.json()

# Get statistics
response = requests.get(f'{API_BASE}/prediction-stats')
stats = response.json()
```

---

## Response Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

---

## Rate Limiting

No rate limiting is currently implemented. For production use, consider adding rate limiting.

---

## Authentication

No authentication is required for these endpoints. For production, implement proper authentication.

---

## CORS

CORS is enabled. Requests from any origin are accepted.

---

## Data Retention

- Predictions are stored in memory during server runtime
- Restarting the server will clear all history
- For persistent storage, upgrade to use a database

---

## Best Practices

1. **Error Handling**: Always check response status and handle errors
2. **Pagination**: Use limit and offset for large datasets
3. **IDs**: Save prediction IDs for later reference
4. **Timestamps**: Use timestamps to track when predictions were made
5. **Batch Operations**: Use batch-predict for multiple records

---

## Support & Documentation

For more information:
- Visit http://localhost:5000/about
- Check README.md
- Review SETUP.md

---

**Version:** 1.0.0  
**Last Updated:** February 5, 2024  
**Status:** Production Ready
