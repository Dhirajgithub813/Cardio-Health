# CardioPredict - Quick Reference Guide

## 📋 Project Summary

**Cardiovascular Disease Prediction System** - A complete AI/ML web application using Python Flask backend and modern HTML/CSS/JavaScript frontend.

### Key Stats
- 🤖 **ML Model**: Random Forest Classifier (100 trees)
- 📊 **Training Data**: 70,000+ patient records
- 🎯 **Features**: 11 health metrics
- 🎨 **Pages**: 4 main pages (Home, Predict, Analytics, About)
- 🔗 **API Endpoints**: 9 endpoints
- 📱 **Responsive**: Mobile, Tablet, Desktop

## 🚀 Quick Start (Choose One)

### Method 1: Windows (Fastest)
```
1. Double-click: run.bat
2. Wait for completion
3. Browser opens to: http://localhost:5000
```

### Method 2: Command Line
```bash
pip install -r requirements.txt
python train_model.py
python app.py
```

### Method 3: Linux/Mac
```bash
bash run.sh
```

## 📁 Project File Structure

```
CardioPredict/
│
├── Backend Python Files
│   ├── app.py                 ← Flask server (Start here!)
│   └── train_model.py         ← Train ML model
│
├── Frontend Files
│   └── templates/
│       ├── index.html         ← Home page
│       ├── predict.html       ← Prediction form
│       ├── analytics.html     ← Data visualizations
│       └── about.html         ← Documentation
│
├── Static Assets
│   └── static/
│       ├── style.css          ← All styling
│       ├── script.js          ← Shared utilities
│       ├── predict.js         ← Prediction logic
│       └── analytics.js       ← Charts logic
│
├── Data
│   └── cardio_train (1).csv   ← Dataset
│
├── Config & Docs
│   ├── requirements.txt       ← Dependencies
│   ├── README.md              ← Full docs
│   ├── SETUP.md               ← Setup guide
│   ├── PROJECT_CHECKLIST.md   ← Feature checklist
│   ├── run.bat                ← Windows starter
│   └── run.sh                 ← Linux/Mac starter
```

## 🌐 Page Navigation Map

```
┌─────────────────────────────────────────┐
│           NAVBAR (All Pages)            │
│ CardioPredict | Home | Predict | About  │
└─────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ HOME (/)                                 │
├──────────────────────────────────────────┤
│ ✓ Hero Section                           │
│ ✓ Feature Cards                          │
│ ✓ How It Works                           │
│ ✓ Call-to-Action Buttons                 │
│   ├→ "Start Prediction" → /predict       │
│   └→ "View Analytics" → /analytics       │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ PREDICT (/predict)                       │
├──────────────────────────────────────────┤
│ Left Side: Input Form                    │
│ ├─ Age, Gender, Height, Weight           │
│ ├─ Blood Pressure (Systolic/Diastolic)  │
│ ├─ Cholesterol & Glucose Levels          │
│ ├─ Lifestyle (Smoking, Alcohol, Active)  │
│ └─ BMI Auto-Calculator                   │
│                                          │
│ Right Side: Results (After Submit)       │
│ ├─ Risk Meter Chart (Doughnut)          │
│ ├─ Risk Summary Box                      │
│ ├─ Probability Details                   │
│ └─ Personalized Recommendations          │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ ANALYTICS (/analytics)                   │
├──────────────────────────────────────────┤
│ ✓ Statistics Cards (4)                   │
│   ├─ Total Records                       │
│   ├─ Disease Cases                       │
│   ├─ Healthy Cases                       │
│   └─ Disease Percentage                  │
│                                          │
│ ✓ Charts                                 │
│   ├─ Disease Distribution (Doughnut)    │
│   └─ Age Analysis (Bar Chart)            │
│                                          │
│ ✓ Feature Statistics Table               │
│ ✓ Key Insights List                      │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ ABOUT (/about)                           │
├──────────────────────────────────────────┤
│ ✓ Project Overview                       │
│ ✓ Model & Technology Info                │
│ ✓ Input Parameters Table                 │
│ ✓ How Predictions Work (5 Steps)         │
│ ✓ Risk Assessment Levels                 │
│ ✓ Medical Disclaimer                     │
│ ✓ Dataset Information                    │
└──────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           FOOTER (All Pages)            │
│              Copyright Info              │
└─────────────────────────────────────────┘
```

## 🔌 API Endpoints

### Frontend Routes (HTML Pages)
| Route | Purpose | Method |
|-------|---------|--------|
| `/` | Home page | GET |
| `/predict` | Prediction form | GET |
| `/analytics` | Analytics dashboard | GET |
| `/about` | About & docs | GET |

### API Routes (JSON Responses)
| Endpoint | Purpose | Method | Input |
|----------|---------|--------|-------|
| `/api/predict` | Single prediction | POST | JSON object |
| `/api/batch-predict` | Multiple predictions | POST | JSON array |
| `/api/statistics` | Dataset stats | GET | None |
| `/api/model-info` | Model details | GET | None |
| `/api/health` | Server health | GET | None |

## 🤖 How the ML Model Works

```
TRAINING (One-time: train_model.py)
┌──────────────────────────────────┐
│ 1. Load CSV (70,000 records)     │
│ 2. Feature Engineering           │
│ 3. Data Preprocessing            │
│ 4. Train/Test Split (80/20)      │
│ 5. Feature Scaling               │
│ 6. Train Random Forest           │
│ 7. Evaluate Performance          │
│ 8. Save Model to Disk            │
└──────────────────────────────────┘

PREDICTION (Per request: app.py)
┌──────────────────────────────────┐
│ 1. User enters health data       │
│ 2. Form submitted to API         │
│ 3. Data validation               │
│ 4. Feature scaling               │
│ 5. Model prediction              │
│ 6. Calculate probability         │
│ 7. Assess risk level             │
│ 8. Return JSON response          │
└──────────────────────────────────┘
```

## 📊 Input Parameters (11 Total)

| # | Parameter | Type | Range | Example |
|---|-----------|------|-------|---------|
| 1 | age | Integer | 0-35000 days | 10950 (30 years) |
| 2 | gender | Integer | 1-2 | 2 (Female) |
| 3 | height | Integer | 140-210 cm | 165 |
| 4 | weight | Float | 40-150 kg | 65.5 |
| 5 | ap_hi | Integer | 90-180 mmHg | 120 |
| 6 | ap_lo | Integer | 60-120 mmHg | 80 |
| 7 | cholesterol | Integer | 0-3 | 1 (Normal) |
| 8 | gluc | Integer | 0-3 | 1 (Normal) |
| 9 | smoke | Binary | 0 or 1 | 0 (No) |
| 10 | alco | Binary | 0 or 1 | 0 (No) |
| 11 | active | Binary | 0 or 1 | 1 (Yes) |

## 🎯 Output & Risk Levels

### Output Data
```json
{
  "prediction": 0 or 1,
  "has_disease": true/false,
  "disease_probability": 0.0-1.0,
  "healthy_probability": 0.0-1.0,
  "risk_percentage": 0-100,
  "risk_level": "Low/Moderate/High Risk",
  "color": "green/orange/red"
}
```

### Risk Assessment

| Risk Level | Range | Color | Action |
|-----------|-------|-------|--------|
| 🟢 Low | 0-30% | Green | Maintain lifestyle |
| 🟡 Moderate | 30-60% | Orange | Consult doctor |
| 🔴 High | 60%+ | Red | Seek medical help |

## 🔧 Installation Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| ModuleNotFoundError | Packages not installed | `pip install -r requirements.txt` |
| Model not loaded | Files not found | Run `python train_model.py` |
| Port 5000 in use | Another app using it | Change port in app.py |
| CORS errors | Missing extension | `pip install flask-cors` |
| Slow first prediction | Model loading | Normal - cache builds |

## 💾 Key Files Explanation

### app.py (Flask Backend)
- Contains all routes and API endpoints
- Loads trained ML model
- Handles predictions
- Serves HTML templates
- Returns JSON responses

### train_model.py (ML Training)
- Loads cardiovascular dataset
- Preprocesses data
- Trains Random Forest model
- Saves model files (pickle format)
- Prints performance metrics

### predict.html (Prediction Page)
- Interactive form with validation
- Real-time BMI calculation
- Connects to API
- Displays results with charts
- Shows recommendations

### analytics.html (Dashboard)
- Fetches dataset statistics
- Renders distribution charts
- Shows feature statistics
- Displays insights
- Uses Chart.js for visualization

### style.css (Styling)
- Complete responsive design
- Gradient backgrounds
- Animations and transitions
- Mobile-first approach
- Dark color scheme

## 🎨 Color Scheme

```
Primary Color:      #FF6B6B (Red - Disease/Risk)
Secondary Color:    #4ECDC4 (Teal - Health/Info)
Success Color:      #2ecc71 (Green - Healthy)
Warning Color:      #f39c12 (Orange - Caution)
Danger Color:       #e74c3c (Red - Alert)
Dark Color:         #2c3e50 (Dark Blue - Text)
Light Color:        #ecf0f1 (Light Gray - Background)
```

## 📱 Responsive Breakpoints

```
Desktop:     1200px and above
Tablet:      768px to 1199px
Mobile:      480px to 767px
Small Mobile: Below 480px
```

## 🔒 Security Notes

✅ No data stored or logged  
✅ No user accounts needed  
✅ All computation local  
✅ CORS properly configured  
✅ Input validation on server  
✅ Error handling implemented  

⚠️ Medical Disclaimer:  
This is an **EDUCATIONAL** tool, not a medical diagnostic system. Always consult healthcare professionals.

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Comprehensive documentation |
| SETUP.md | Detailed setup guide |
| PROJECT_CHECKLIST.md | Feature verification |
| QUICK_REFERENCE.md | This file |

## 🎯 Common Tasks

### Make a Prediction
1. Go to `/predict`
2. Fill form with health data
3. Click "Get Prediction"
4. View results and recommendations

### View Analytics
1. Go to `/analytics`
2. See dataset statistics
3. Analyze charts and insights

### Check API
1. Open browser console
2. Run: `API.predict({...data...})`
3. See response in console

### Change Server Port
Edit app.py line: `app.run(port=5001)`

### Debug Issues
1. Press F12 → Console tab
2. Check error messages
3. Verify server is running
4. Check network tab for API calls

## 🚀 Performance Tips

- First prediction loads model (slower)
- Subsequent predictions are fast
- Charts render on first load
- Use modern browser for best experience
- Close unused tabs for performance

## 📞 Support Checklist

- ✅ Check About page
- ✅ Read README.md
- ✅ Check SETUP.md
- ✅ Review PROJECT_CHECKLIST.md
- ✅ Check browser console (F12)
- ✅ Verify Python installation
- ✅ Confirm all files present

## 🎓 Learning Path

1. **Understand the Data**: Check CSV structure
2. **Train the Model**: Run train_model.py
3. **Explore Backend**: Read app.py comments
4. **Test API**: Use Postman or cURL
5. **Learn Frontend**: Check HTML templates
6. **Study Styling**: Review style.css
7. **Examine Logic**: Read JavaScript files

## 🏆 Success Metrics

After setup, you should see:
- ✅ Server running message
- ✅ Model training complete
- ✅ Zero errors on startup
- ✅ All pages load correctly
- ✅ Form submissions work
- ✅ Results display properly
- ✅ Charts render correctly

## 🎉 You're Ready!

All files are created and organized. The project is:
- ✅ **Complete**: All features implemented
- ✅ **Documented**: Full documentation provided
- ✅ **Tested**: Ready to run
- ✅ **Professional**: Production-quality code
- ✅ **Educational**: Great for learning

### Next Steps:
1. Install dependencies: `pip install -r requirements.txt`
2. Train model: `python train_model.py`
3. Start server: `python app.py`
4. Open browser: `http://localhost:5000`
5. Enjoy the app! 🎊

---

**Questions?** Check the About page in the app for full documentation.

**Ready?** Let's predict! 🚀
