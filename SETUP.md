# CardioPredict - Complete Setup & Usage Guide

## 🎯 Quick Start (5 Minutes)

### Option 1: Automated Setup (Windows)
1. Double-click `run.bat`
2. Wait for the script to complete
3. Open browser and go to `http://localhost:5000`

### Option 2: Automated Setup (Linux/Mac)
1. Open Terminal and navigate to project directory
2. Run: `bash run.sh`
3. Open browser and go to `http://localhost:5000`

### Option 3: Manual Setup

#### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

Expected packages:
- Flask==2.3.0
- scikit-learn==1.2.2
- pandas==1.5.3
- numpy==1.24.3
- Flask-CORS==4.0.0

#### Step 2: Train the ML Model
```bash
python train_model.py
```

This will:
- Load cardiovascular disease data (70,000+ records)
- Train Random Forest classifier
- Save model files: `cardio_model.pkl`, `scaler.pkl`, `feature_names.pkl`
- Display performance metrics

**Expected Output:**
```
Loading data...
Dataset shape: (70000, 13)

Preprocessing data...
Training Random Forest model...

Evaluating model...
Accuracy: 0.7234
Precision: 0.6543
Recall: 0.5678
F1-Score: 0.6078

Saving model and scaler...
✓ Model trained and saved successfully!
Files saved: cardio_model.pkl, scaler.pkl, feature_names.pkl
```

#### Step 3: Start the Flask Server
```bash
python app.py
```

**Expected Output:**
```
Starting Cardiovascular Disease Prediction API...
Server running at http://localhost:5000
Dashboard available at http://localhost:5000/
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

#### Step 4: Open Your Browser
Navigate to: `http://localhost:5000`

## 📖 Using the Application

### Home Page
- Overview of the project
- Quick links to prediction and analytics
- Feature highlights

### Prediction Page (`/predict`)

#### How to Make a Prediction:

1. **Fill in your health information:**
   - **Age**: Enter your age in days (multiply years by 365)
     - Example: 30 years = 10,950 days
   - **Gender**: Select Male or Female
   - **Height**: Enter in centimeters (150-210 cm)
   - **Weight**: Enter in kilograms (40-150 kg)
   - **Blood Pressure**: Enter systolic (top) and diastolic (bottom)
     - Systolic: 90-180 mmHg
     - Diastolic: 60-120 mmHg
   - **Cholesterol**: Select level (0=Normal to 3=High)
   - **Glucose**: Select level (0=Normal to 3=High)
   - **Lifestyle Factors**:
     - Check if you smoke
     - Check if you consume alcohol
     - Check if you're physically active

2. **Click "Get Prediction"**

3. **View Results:**
   - Risk percentage (0-100%)
   - Risk level (Low/Moderate/High)
   - Disease probability
   - Personalized recommendations

#### Example Prediction:
```
Input: 35-year-old female, 165cm, 65kg
       Blood pressure: 120/80
       Normal cholesterol and glucose
       Non-smoker, occasional alcohol, active

Output: 
- Risk: 25% (Low Risk)
- Disease Probability: 25%
- Healthy Probability: 75%
- Recommendation: Maintain current healthy habits
```

### Analytics Page (`/analytics`)

View comprehensive dataset statistics:
- Total records in training data
- Disease prevalence rate
- Age distribution
- Feature statistics (min, max, average)
- Disease distribution chart
- Age analysis chart

### About Page (`/about`)

Detailed information:
- Project overview
- Technology stack
- Input parameter descriptions
- How predictions work
- Risk assessment explanation
- Medical disclaimer
- Dataset information

## ⚙️ Configuration

### Change Server Port
Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Enable/Disable Debug Mode
Edit `app.py`:
```python
app.run(debug=False)  # Set to False for production
```

### Customize API Response
Edit the `/api/predict` endpoint in `app.py` to add more details or modify risk calculations.

## 🔧 Troubleshooting

### Error: ModuleNotFoundError
**Problem**: Python packages not installed
**Solution**:
```bash
pip install -r requirements.txt
```

### Error: "Model not loaded"
**Problem**: Model files not found
**Solution**:
1. Ensure you ran `python train_model.py`
2. Check that these files exist in project root:
   - `cardio_model.pkl`
   - `scaler.pkl`
   - `feature_names.pkl`

### Port Already in Use
**Problem**: Port 5000 is already in use
**Solution**:
```bash
# Change port in app.py
python app.py  # or change port configuration
```

### Slow Predictions
**Problem**: First prediction is slow
**Solution**: This is normal - the model is loading. Subsequent predictions are faster.

### CORS Errors in Console
**Problem**: Cross-origin requests blocked
**Solution**: 
- Ensure Flask-CORS is installed
- Check that app.py has `CORS(app)`

### CSV File Not Found
**Problem**: Error loading dataset
**Solution**:
- Ensure `cardio_train (1).csv` is in project root
- Don't rename the CSV file

## 📊 Understanding Your Results

### Risk Levels Explanation

| Risk Level | Percentage | Meaning | Action |
|-----------|-----------|---------|--------|
| 🟢 Low | 0-30% | Minimal cardiovascular risk | Maintain healthy lifestyle |
| 🟡 Moderate | 30-60% | Some risk factors present | Consult healthcare provider |
| 🔴 High | 60-100% | Significant risk factors | Seek immediate medical advice |

### Factors That Increase Risk

- **Age**: Older age increases risk
- **High Blood Pressure**: Systolic > 140 or Diastolic > 90 mmHg
- **Cholesterol**: Level 2-3 indicates increased risk
- **Glucose**: Level 2-3 indicates increased risk
- **Smoking**: Significantly increases risk
- **Physical Inactivity**: Increases risk
- **High Weight/BMI**: Increases risk

### Factors That Decrease Risk

- **Physical Activity**: Regular exercise reduces risk
- **Normal Blood Pressure**: Less than 120/80 mmHg
- **Healthy Weight**: BMI 18.5-24.9
- **No Smoking**: Non-smoker status
- **Moderate Alcohol**: Limits consumption
- **Young Age**: Lower age reduces baseline risk

## 🔒 Security & Privacy

- ✅ No data is stored or logged
- ✅ Predictions are processed in real-time
- ✅ No user accounts or authentication required
- ✅ All computations done locally on server
- ✅ No external data sharing

## 📝 Important Notes

### Medical Disclaimer
This system is **NOT** a medical diagnostic tool. It provides educational predictions based on machine learning patterns. Always consult qualified healthcare professionals for medical advice.

### Data Accuracy
- The model is trained on historical patient data
- Predictions are probabilistic, not 100% accurate
- Individual factors not in the model may affect your actual risk
- Use as a screening tool, not a diagnostic tool

### Limitations
- Model works best for adult populations
- May not account for all health conditions
- Requires accurate health information input
- Does not consider medication effects
- Does not account for genetic factors

## 🆘 Getting Help

### Check the About Page
Full documentation is available at `/about`

### Review the README
Comprehensive project information in `README.md`

### Check Browser Console
For technical issues:
1. Press F12 (Developer Tools)
2. Go to Console tab
3. Look for error messages

### Verify Installation
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "Flask|scikit-learn|pandas"

# Test Flask
python -c "import flask; print(flask.__version__)"
```

## 🚀 Advanced Usage

### Making Predictions via API

#### Using cURL:
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 18393,
    "gender": 2,
    "height": 168,
    "weight": 62.0,
    "ap_hi": 110,
    "ap_lo": 80,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1
  }'
```

#### Using Python:
```python
import requests

data = {
    "age": 18393,
    "gender": 2,
    "height": 168,
    "weight": 62.0,
    "ap_hi": 110,
    "ap_lo": 80,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1
}

response = requests.post('http://localhost:5000/api/predict', json=data)
print(response.json())
```

### Getting Dataset Statistics
```bash
curl http://localhost:5000/api/statistics
```

## 📦 Project Files Overview

```
MAJOR PROJECT 4/
├── app.py                    # Main Flask application
├── train_model.py            # Model training script
├── README.md                 # Full documentation
├── SETUP.md                  # This file
├── requirements.txt          # Python dependencies
├── run.bat                   # Windows quick start
├── run.sh                    # Linux/Mac quick start
├── cardio_train (1).csv      # Training data
├── templates/
│   ├── index.html           # Home page
│   ├── predict.html         # Prediction form
│   ├── analytics.html       # Analytics dashboard
│   └── about.html           # About & documentation
└── static/
    ├── style.css            # All styling
    ├── script.js            # Shared utilities
    ├── predict.js           # Prediction logic
    └── analytics.js         # Analytics logic
```

## ✨ Features Summary

- ✅ Machine Learning predictions
- ✅ Real-time results
- ✅ Interactive web interface
- ✅ Data analytics dashboard
- ✅ RESTful API
- ✅ Responsive design
- ✅ No database required
- ✅ Easy installation
- ✅ Comprehensive documentation
- ✅ Educational tool

## 🎓 Learning Outcomes

By using this project, you'll understand:
- Machine learning model development
- Flask web framework
- RESTful API design
- Frontend-backend integration
- Data visualization
- HTML/CSS/JavaScript
- Model training and evaluation
- Feature scaling and preprocessing

---

**Need help?** Check the About page in the application or review the README.md file.

**Ready to start?** Run `python app.py` or double-click `run.bat` (Windows) / `run.sh` (Linux/Mac)

**Happy predicting!** 🎯
