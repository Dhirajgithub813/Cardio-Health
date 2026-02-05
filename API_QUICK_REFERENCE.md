# 🔌 Prediction Status API - Quick Reference

## ✅ API Setup Complete!

The CardioPredict system now includes **7 new prediction status tracking endpoints** for monitoring and managing predictions.

---

## 📊 Quick Endpoint Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/predict` | POST | Make a prediction |
| `/api/prediction/<id>` | GET | Get specific prediction |
| `/api/prediction-status` | GET | Overall status summary |
| `/api/prediction-history` | GET | Full prediction history |
| `/api/prediction-stats` | GET | Detailed statistics |
| `/api/prediction-health` | GET | Service health check |
| `/api/clear-history` | POST | Clear all history |

---

## 🚀 Getting Started

### 1. Start the Server
```bash
python app.py
```

### 2. Make a Prediction
**Using Browser/Fetch:**
```javascript
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

console.log(result.prediction_id);  // Save this ID!
```

### 3. Track Prediction
**Get Status by ID:**
```javascript
const status = await API.getPredictionStatus('a1b2c3d4');
console.log(status.prediction);
```

### 4. View All Predictions
```javascript
const history = await API.getPredictionHistory(20, 0);
console.log(history.predictions);
```

---

## 📋 Prediction Object Structure

Every prediction stored includes:

```json
{
    "id": "a1b2c3d4",              // Unique prediction ID
    "prediction": 0,                // 0 = healthy, 1 = disease
    "has_disease": false,           // Boolean
    "disease_probability": 0.25,    // 0-1 scale
    "healthy_probability": 0.75,    // 0-1 scale
    "risk_percentage": 25.0,        // 0-100 scale
    "risk_level": "Low Risk",       // Low/Moderate/High
    "color": "green",               // green/orange/red
    "timestamp": "2024-02-05T14:30:00.000000",
    "age": 18393,                   // Input data
    "gender": 2,
    "height": 165,
    "weight": 70,
    "bp_systolic": 120,
    "bp_diastolic": 80,
    "status": "completed"
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Make & Track Prediction
```javascript
// Step 1: Make prediction
const result = await API.predict(patientData);
const predictionId = result.prediction_id;

// Step 2: Later, retrieve it
const details = await API.getPredictionStatus(predictionId);

// Step 3: Check result
if (details.prediction.risk_percentage > 60) {
    console.log('High risk - refer to doctor');
}
```

### Use Case 2: Monitor System Status
```javascript
// Check if service is healthy
const health = await API.getPredictionHealth();

if (health.status === 'healthy') {
    console.log(`${health.total_predictions_made} predictions made`);
} else {
    console.log('Service unavailable');
}
```

### Use Case 3: Analyze Predictions
```javascript
// Get detailed statistics
const stats = await API.getPredictionDetailedStats();

console.log(`Total predictions: ${stats.total_predictions}`);
console.log(`High risk cases: ${stats.risk_distribution.high_risk}`);
console.log(`Average risk: ${stats.risk_percentage_stats.average}%`);
console.log(`Disease rate: ${stats.disease_rate.percentage}%`);
```

### Use Case 4: View Recent Predictions
```javascript
// Get last 10 predictions
const status = await API.getPredictionStatusSummary();

status.recent_predictions.forEach(pred => {
    console.log(`${pred.id}: ${pred.risk_level} (${pred.risk_percentage}%)`);
});
```

---

## 🌐 Browser API Helper Usage

All endpoints are accessible through the built-in `API` object:

```javascript
// Available methods:
API.predict(data)                    // Make prediction
API.getPredictionStatus(id)          // Get by ID
API.getPredictionStatusSummary()     // Get summary
API.getPredictionHistory(limit, offset)  // Get history
API.getPredictionDetailedStats()     // Get stats
API.getPredictionHealth()            // Check health
API.clearPredictionHistory()         // Clear data
```

---

## 🔌 Using Prediction ID

Each prediction returns a **unique 8-character ID**:

```javascript
// Example IDs:
"a1b2c3d4"
"f8e7d6c5"
"x9y8z7w6"
```

Use the ID to:
- Retrieve that exact prediction later
- Track specific patient cases
- Build patient histories
- Generate reports

---

## 📊 Response Examples

### Prediction Response
```json
{
    "prediction_id": "a1b2c3d4",
    "risk_percentage": 25.0,
    "risk_level": "Low Risk",
    "disease_probability": 0.25,
    "timestamp": "2024-02-05T14:30:00.000000"
}
```

### Status Summary Response
```json
{
    "status": "active",
    "total_predictions": 15,
    "risk_distribution": {
        "low_risk": 8,
        "moderate_risk": 5,
        "high_risk": 2
    }
}
```

### Statistics Response
```json
{
    "total_predictions": 15,
    "disease_rate": {
        "percentage": 20.0,
        "with_disease": 3,
        "without_disease": 12
    },
    "risk_percentage_stats": {
        "average": 35.8,
        "min": 5.2,
        "max": 85.6
    }
}
```

---

## ⚡ Real-Time Features

✅ **Instant Storage** - Predictions saved immediately  
✅ **Unique IDs** - Every prediction gets unique identifier  
✅ **Auto Tracking** - Statistics updated automatically  
✅ **Full History** - All data retained in memory  
✅ **Detailed Stats** - Comprehensive analysis available  
✅ **Health Monitoring** - Check service status anytime  

---

## 🔐 Data Privacy

- ✅ In-memory storage (no database)
- ✅ Cleared on server restart
- ✅ No external storage
- ✅ No data logging
- ✅ Safe for testing/development

---

## 🚀 Access Points

| Feature | URL |
|---------|-----|
| Web Interface | http://localhost:5000 |
| Results Page | http://localhost:5000/results |
| Prediction Page | http://localhost:5000/predict |
| Analytics | http://localhost:5000/analytics |
| API Docs | See API_DOCUMENTATION.md |

---

## 📱 Results Page Features

The new **Results Page** (`/results`) provides:

✅ Statistics cards (Total, High/Moderate/Low Risk)  
✅ Risk distribution chart  
✅ Detailed statistics table  
✅ Full prediction history table  
✅ Load more functionality  
✅ Clear history option  

---

## 🧪 Testing the API

### Quick Test Script
```javascript
// Open browser console (F12) and paste:

// Test 1: Make prediction
const pred = await API.predict({
    age: 18393, gender: 2, height: 165, weight: 70,
    ap_hi: 120, ap_lo: 80, cholesterol: 1, gluc: 1,
    smoke: 0, alco: 0, active: 1
});
console.log('✓ Prediction made:', pred.prediction_id);

// Test 2: Get status
const status = await API.getPredictionStatusSummary();
console.log('✓ Total predictions:', status.total_predictions);

// Test 3: Get statistics
const stats = await API.getPredictionDetailedStats();
console.log('✓ Disease rate:', stats.disease_rate.percentage + '%');

// Test 4: Check health
const health = await API.getPredictionHealth();
console.log('✓ Service health:', health.status);
```

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `app.py` | Backend with all endpoints |
| `templates/results.html` | Results dashboard page |
| `static/script.js` | JavaScript API helpers |
| `API_DOCUMENTATION.md` | Complete API docs |
| `QUICK_REFERENCE.md` | This file |

---

## 🎯 Key Features

1. **Automatic Tracking** - Every prediction automatically stored
2. **Unique IDs** - Easy retrieval and reference
3. **Comprehensive Stats** - Detailed analysis available
4. **Easy Integration** - Built-in API helpers
5. **Real-time Updates** - Instant data availability
6. **Results Dashboard** - Visual tracking interface

---

## 💡 Pro Tips

1. **Save IDs** - Store prediction IDs for later reference
2. **Monitor Stats** - Check `/api/prediction-stats` regularly
3. **Use Pagination** - For large datasets, use limit/offset
4. **Check Health** - Verify service before batch operations
5. **Clear Periodically** - Use clear-history for testing

---

## 📞 Support

- Full docs: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Setup help: [SETUP.md](SETUP.md)
- Quick guide: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- In-app help: http://localhost:5000/about

---

## ✨ Summary

You now have a complete **Prediction Status API** with:

✅ 7 tracking endpoints  
✅ Real-time prediction storage  
✅ Comprehensive statistics  
✅ Results dashboard page  
✅ JavaScript helpers for easy access  
✅ Full documentation  

**Ready to track predictions!** 🎯

---

**Version:** 1.0.0  
**API Status:** ✅ Production Ready  
**Last Updated:** February 5, 2024
