"""
Cardiovascular Disease Prediction - Flask Backend API v2.0
Enhanced production-ready API with logging, validation, and monitoring
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import os
import uuid
import logging

# Import custom modules
from config import app_config
from logger import setup_logging, log_prediction, log_api_call, log_error
from validators import PredictionValidator
from models import PredictionRecord, StatisticsRecord
from utils import AgeConverter, RiskAssessor, BMICalculator, DataPreprocessor, ResponseFormatter, HealthCheck, DateUtils

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load configuration
app.config.from_object(app_config)

# Enable CORS
CORS(app)

# Setup logging with the custom config class
setup_logging(app, app_config)

# ==================== GLOBAL STATE ====================

# Prediction history storage
prediction_history = {}
prediction_stats = StatisticsRecord()

# Model and scaler
model = None
scaler = None
feature_names = None
model_loaded = False

# ==================== MODEL INITIALIZATION ====================

def load_model():
    """Load ML model and scaler"""
    global model, scaler, feature_names, model_loaded
    
    try:
        model_file = app.config.get('MODEL_FILE', 'cardio_model.pkl')
        scaler_file = app.config.get('SCALER_FILE', 'scaler.pkl')
        features_file = app.config.get('FEATURES_FILE', 'feature_names.pkl')
        
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_file, 'rb') as f:
            scaler = pickle.load(f)
        
        with open(features_file, 'rb') as f:
            feature_names = pickle.load(f)
        
        model_loaded = True
        app.logger.info("[OK] ML Model loaded successfully!")
        app.logger.info(f"  - Model type: {type(model).__name__}")
        app.logger.info(f"  - Features: {len(feature_names)}")
        
    except FileNotFoundError as e:
        model_loaded = False
        app.logger.error(f"⚠ Model files not found: {e}")
        app.logger.error("  Run: python train_model.py")
    except Exception as e:
        model_loaded = False
        app.logger.error(f"⚠ Error loading model: {e}")

# Load model on startup
load_model()

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    app.logger.debug("GET / - Home page")
    return render_template('index.html')

@app.route('/predict')
def predict_page():
    """Prediction form page"""
    app.logger.debug("GET /predict - Prediction page")
    return render_template('predict.html')

@app.route('/dashboard')
def dashboard_page():
    """Merged Analytics & Results with analytics and results"""
    app.logger.debug("GET /dashboard - Analytics & Results page")
    return render_template('dashboard.html')

@app.route('/analytics')
def analytics_page():
    """Analytics page (redirect to merged Analytics & Results)"""
    app.logger.debug("GET /analytics - Analytics page (redirected to Analytics & Results)")
    return render_template('dashboard.html')

@app.route('/results')
def results_page():
    """Results and history page (redirect to merged Analytics & Results)"""
    app.logger.debug("GET /results - Results page (redirected to Analytics & Results)")
    return render_template('dashboard.html')

@app.route('/about')
def about_page():
    """About page"""
    app.logger.debug("GET /about - About page")
    return render_template('about.html')

@app.route('/test-dashboard')
def test_dashboard():
    """Test dashboard button functionality"""
    app.logger.debug("GET /test-dashboard - Test page")
    return render_template('test_dashboard.html')

@app.route('/faq')
def faq_page():
    """FAQ - Frequently Asked Questions page"""
    app.logger.debug("GET /faq - FAQ page")
    return render_template('faq.html')

@app.route('/documentation')
def documentation_page():
    """Documentation and API reference page"""
    app.logger.debug("GET /documentation - Documentation page")
    return render_template('documentation.html')

@app.route('/privacy')
def privacy_page():
    """Privacy Policy page"""
    app.logger.debug("GET /privacy - Privacy Policy page")
    return render_template('privacy.html')

@app.route('/terms')
def terms_page():
    """Terms of Service page"""
    app.logger.debug("GET /terms - Terms of Service page")
    return render_template('terms.html')

@app.route('/feedback')
def feedback_page():
    """Patient feedback and service rating page"""
    app.logger.debug("GET /feedback - Patient Feedback page")
    return render_template('feedback.html')

# ==================== API ENDPOINTS ====================

# @app.before_request
# def before_request():
#     """Log all requests (uncomment for debugging)"""
#     app.logger.debug(f"{request.method} {request.path}")

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Make a cardiovascular disease prediction
    
    Request body:
    {
        "age": 50,                  # Years (converted to days internally)
        "gender": 2,                # 1=Female, 2=Male
        "height": 165,              # cm
        "weight": 70,               # kg
        "ap_hi": 120,               # Systolic BP
        "ap_lo": 80,                # Diastolic BP
        "cholesterol": 1,           # 0-3
        "gluc": 1,                  # 0-3
        "smoke": 0,                 # 0 or 1
        "alco": 0,                  # 0 or 1
        "active": 1                 # 0 or 1
    }
    """
    try:
        if not model_loaded:
            log_error(app, "ModelNotLoaded", "ML model not loaded")
            response, status = ResponseFormatter.error(
                'Model not loaded. Please train the model first.',
                status_code=503,
                error_code='MODEL_NOT_LOADED'
            )
            return jsonify(response), status
        
        # Get and validate JSON data
        data = request.get_json()
        if not data:
            return jsonify(ResponseFormatter.error('No JSON data provided', 400)[0]), 400
        
        # Validate input
        is_valid, error_message = PredictionValidator.validate(data)
        if not is_valid:
            app.logger.warning(f"Validation error: {error_message}")
            response, status = ResponseFormatter.error(error_message, 400, 'VALIDATION_ERROR')
            return jsonify(response), status
        
        # Convert age from years to days
        age_in_years = int(data['age'])
        age_in_days = int(AgeConverter.years_to_days(age_in_years))
        
        # Calculate BMI
        bmi = float(BMICalculator.calculate_bmi(data['height'], data['weight']))
        
        # Create feature array with proper scalar conversion
        try:
            features = np.array([[
                np.float64(age_in_days),
                np.float64(data['gender']),
                np.float64(data['height']),
                np.float64(data['weight']),
                np.float64(data['ap_hi']),
                np.float64(data['ap_lo']),
                np.float64(data['cholesterol']),
                np.float64(data['gluc']),
                np.float64(data['smoke']),
                np.float64(data['alco']),
                np.float64(data['active']),
                np.float64(bmi)
            ]])
        except Exception as e:
            app.logger.error(f"Feature array creation error: {str(e)}, Data types: {[(k, type(v)) for k, v in data.items()]}")
            raise
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)
        probability = model.predict_proba(features_scaled)
        
        # Extract scalar values - ensure they are Python scalars, not numpy arrays
        pred_value = int(np.asarray(prediction).flatten()[0])
        prob_array = np.asarray(probability).flatten()
        prob_healthy = float(prob_array[0])
        prob_disease = float(prob_array[1])
        
        # Get risk assessment
        risk_info = RiskAssessor.get_risk_level(prob_disease)
        
        # Generate unique prediction ID
        prediction_id = str(uuid.uuid4())[:8]
        
        # Create prediction record
        pred_record = PredictionRecord(
            prediction_id=prediction_id,
            prediction=pred_value,
            probability=[prob_healthy, prob_disease],
            risk_percentage=risk_info['percentage'],
            risk_level=risk_info['level'],
            color=risk_info['color'],
            age_days=age_in_days,
            age_years=age_in_years,
            gender=data['gender'],
            height=data['height'],
            weight=data['weight'],
            ap_hi=data['ap_hi'],
            ap_lo=data['ap_lo'],
            cholesterol=data['cholesterol'],
            gluc=data['gluc'],
            smoke=data['smoke'],
            alco=data['alco'],
            active=data['active'],
            patient_name=data.get('patientName'),
            father_name=data.get('fatherName'),
            blood_group=data.get('bloodGroup'),
            phone_number=data.get('phoneNumber'),
            alt_phone_number=data.get('altPhoneNumber'),
            doctor_name=data.get('doctorName')
        )
        
        # Store prediction
        prediction_history[prediction_id] = pred_record.to_dict()
        prediction_stats.add_prediction(pred_record)
        
        # Log prediction
        log_prediction(app, prediction_id, data, risk_info)
        
        # Return response
        return jsonify({
            'prediction_id': prediction_id,
            'prediction': pred_value,
            'has_disease': bool(pred_value),
            'disease_probability': prob_disease,
            'healthy_probability': prob_healthy,
            'risk_percentage': risk_info['percentage'],
            'risk_level': risk_info['level'],
            'color': risk_info['color'],
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "PredictionError", str(e), f"Data: {data if 'data' in locals() else 'N/A'}")
        response, status = ResponseFormatter.error(f'Prediction error: {str(e)}', 400, 'PREDICTION_ERROR')
        return jsonify(response), status

@app.route('/api/prediction/<prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get specific prediction by ID"""
    try:
        if prediction_id not in prediction_history:
            response, status = ResponseFormatter.error('Prediction not found', 404, 'NOT_FOUND')
            return jsonify(response), status
        
        prediction = prediction_history[prediction_id]
        return jsonify({
            'status': 'success',
            'data': prediction,
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "GetPredictionError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Process multiple predictions at once"""
    try:
        data = request.get_json()
        
        if 'predictions' not in data:
            return jsonify(ResponseFormatter.error('Missing predictions field', 400)[0]), 400
        
        # Validate batch
        is_valid, error_msg = PredictionValidator.validate_batch(data['predictions'])
        if not is_valid:
            return jsonify(ResponseFormatter.error(error_msg, 400)[0]), 400
        
        results = []
        failed = []
        
        for idx, pred_data in enumerate(data['predictions']):
            try:
                # Validate individual prediction
                is_valid, error = PredictionValidator.validate(pred_data)
                if not is_valid:
                    failed.append({'index': idx, 'error': error})
                    continue
                
                # Process prediction
                age_in_years = int(pred_data['age'])
                age_in_days = AgeConverter.years_to_days(age_in_years)
                bmi = BMICalculator.calculate_bmi(pred_data['height'], pred_data['weight'])
                
                features = np.array([[
                    age_in_days, pred_data['gender'], pred_data['height'], pred_data['weight'],
                    pred_data['ap_hi'], pred_data['ap_lo'], pred_data['cholesterol'],
                    pred_data['gluc'], pred_data['smoke'], pred_data['alco'], pred_data['active'], bmi
                ]])
                
                features_scaled = scaler.transform(features)
                prediction = model.predict(features_scaled)[0]
                probability = model.predict_proba(features_scaled)[0]
                
                risk_info = RiskAssessor.get_risk_level(probability[1])
                prediction_id = str(uuid.uuid4())[:8]
                
                results.append({
                    'prediction_id': prediction_id,
                    'prediction': int(prediction),
                    'risk_percentage': risk_info['percentage'],
                    'risk_level': risk_info['level']
                })
            
            except Exception as e:
                failed.append({'index': idx, 'error': str(e)})
        
        return jsonify({
            'status': 'success',
            'results': results,
            'success_count': len(results),
            'failed_count': len(failed),
            'failed': failed if failed else None,
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "BatchPredictError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/prediction-status', methods=['GET'])
def prediction_status():
    """Get overall prediction status"""
    try:
        summary = prediction_stats.get_summary()
        
        return jsonify({
            'status': 'active',
            'total_predictions': summary['total_predictions'],
            'risk_distribution': summary['risk_distribution'],
            'disease_rate': summary['disease_rate'],
            'recent_predictions': list(prediction_history.values())[-10:],
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "StatusError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/prediction-history', methods=['GET'])
def prediction_history_endpoint():
    """Get prediction history with pagination"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate pagination params
        limit = min(limit, 1000)  # Max 1000 per request
        offset = max(0, offset)
        
        history_list = list(prediction_history.values())
        history_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        total = len(history_list)
        paginated = history_list[offset:offset+limit]
        
        response_data = {
            'status': 'success',
            'total_records': total,
            'returned': len(paginated),
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total,
            'predictions': paginated,
            'timestamp': DateUtils.get_timestamp()
        }
        
        return jsonify(response_data), 200
    
    except Exception as e:
        log_error(app, "HistoryError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/prediction-stats', methods=['GET'])
def prediction_stats_endpoint():
    """Get detailed prediction statistics"""
    try:
        if not prediction_history:
            return jsonify({
                'status': 'no_data',
                'total_predictions': 0,
                'message': 'No predictions made yet'
            }), 200
        
        predictions_list = list(prediction_history.values())
        
        risk_percentages = [p['risk_percentage'] for p in predictions_list]
        ages_days = [p['age_days'] for p in predictions_list]
        ages_years = [p['age_years'] for p in predictions_list]
        weights = [p['weight'] for p in predictions_list]
        
        disease_count = sum(1 for p in predictions_list if p['has_disease'])
        
        return jsonify({
            'status': 'success',
            'total_predictions': len(predictions_list),
            'risk_distribution': prediction_stats.get_summary()['risk_distribution'],
            'disease_rate': prediction_stats.get_summary()['disease_rate'],
            'risk_percentage_stats': {
                'min': round(min(risk_percentages), 2),
                'max': round(max(risk_percentages), 2),
                'average': round(sum(risk_percentages) / len(risk_percentages), 2)
            },
            'age_stats': {
                'min': min(ages_years),
                'max': max(ages_years),
                'average': round(sum(ages_years) / len(ages_years), 2)
            },
            'weight_stats': {
                'min': round(min(weights), 2),
                'max': round(max(weights), 2),
                'average': round(sum(weights) / len(weights), 2)
            },
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "StatsError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/prediction-health', methods=['GET'])
def prediction_health():
    """Check prediction service health"""
    try:
        health_status = HealthCheck.get_system_status(model_loaded, len(prediction_history))
        return jsonify(health_status), 200
    
    except Exception as e:
        log_error(app, "HealthError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    try:
        return jsonify({
            'status': 'success',
            'model_type': type(model).__name__ if model_loaded else 'Not Loaded',
            'model_loaded': model_loaded,
            'features': list(feature_names) if feature_names is not None else [],
            'feature_count': len(feature_names) if feature_names is not None else 0,
            'version': app.config.get('API_VERSION', '2.0.0'),
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "ModelInfoError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'degraded',
        'message': 'API is running' if model_loaded else 'API running but model not loaded',
        'version': app.config.get('API_VERSION', '2.0.0'),
        'timestamp': DateUtils.get_timestamp()
    }), 200

@app.route('/api/test-prediction', methods=['GET'])
def test_prediction():
    """Test endpoint to verify the model is working correctly"""
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 503
        
        # Test with two very different patients
        patient_healthy = np.array([[
            25 * 365,  # age: 25 years in days
            1,         # gender: Male
            170,       # height: 170 cm
            70,        # weight: 70 kg
            110,       # ap_hi: 110 mmHg
            70,        # ap_lo: 70 mmHg
            1,         # cholesterol: Above Normal
            1,         # gluc: Above Normal
            0,         # smoke: No
            0,         # alco: No
            1          # active: Yes
        ]])
        
        patient_risky = np.array([[
            65 * 365,  # age: 65 years in days
            2,         # gender: Female
            160,       # height: 160 cm
            95,        # weight: 95 kg
            180,       # ap_hi: 180 mmHg
            110,       # ap_lo: 110 mmHg
            3,         # cholesterol: High
            3,         # gluc: High
            1,         # smoke: Yes
            1,         # alco: Yes
            0          # active: No
        ]])
        
        # Scale and predict
        patient_healthy_scaled = scaler.transform(patient_healthy)
        patient_risky_scaled = scaler.transform(patient_risky)
        
        pred1 = model.predict_proba(patient_healthy_scaled)
        pred2 = model.predict_proba(patient_risky_scaled)
        
        return jsonify({
            'model_type': str(type(model).__name__),
            'healthy_patient_risk': float(pred1[0][1] * 100),
            'risky_patient_risk': float(pred2[0][1] * 100),
            'model_working': True
        }), 200
    
    except Exception as e:
        app.logger.error(f"Test prediction error: {str(e)}")
        return jsonify({'error': str(e), 'model_working': False}), 500

@app.route('/api/analytics', methods=['GET'])
def analytics_data():
    """Get analytics data for dashboard"""
    try:
        df = pd.read_csv('cardio_train (1).csv', sep=';')
        
        # Calculate age distribution
        age_buckets = {}
        for age_days in df['age']:
            age_years = age_days // 365
            bucket = f"{(age_years // 10) * 10}-{(age_years // 10) * 10 + 10}"
            age_buckets[bucket] = age_buckets.get(bucket, 0) + 1
        
        stats = {
            'total_records': len(df),
            'disease_count': int(df['cardio'].sum()),
            'healthy_count': int((df['cardio'] == 0).sum()),
            'disease_percentage': float(df['cardio'].mean() * 100),
            'age_stats': {
                'min': int(df['age'].min()),
                'max': int(df['age'].max()),
                'mean': float(df['age'].mean())
            },
            'weight_stats': {
                'min': float(df['weight'].min()),
                'max': float(df['weight'].max()),
                'mean': float(df['weight'].mean())
            },
            'height_stats': {
                'min': float(df['height'].min()),
                'max': float(df['height'].max()),
                'mean': float(df['height'].mean())
            },
            'age_distribution': age_buckets,
            'high_bp_count': int((df['ap_hi'] > 140).sum()),
            'high_cholesterol_count': int((df['cholesterol'] >= 2).sum()),
            'smokers_count': int((df['smoke'] == 1).sum())
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        log_error(app, "AnalyticsError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Get dataset statistics (legacy endpoint - calls /api/analytics)"""
    return analytics_data()

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear prediction history (admin function)"""
    try:
        global prediction_history, prediction_stats
        
        cleared_count = len(prediction_history)
        prediction_history = {}
        prediction_stats = StatisticsRecord()
        
        app.logger.warning(f"Prediction history cleared - {cleared_count} records removed")
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction history cleared',
            'cleared_count': cleared_count,
            'timestamp': DateUtils.get_timestamp()
        }), 200
    
    except Exception as e:
        log_error(app, "ClearError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    app.logger.warning(f"404 Error: {request.path}")
    response, status = ResponseFormatter.error('Endpoint not found', 404, 'NOT_FOUND')
    return jsonify(response), status

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f"500 Error: {error}")
    response, status = ResponseFormatter.error('Internal server error', 500, 'INTERNAL_ERROR')
    return jsonify(response), status

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    app.logger.warning(f"400 Error: {error}")
    response, status = ResponseFormatter.error('Bad request', 400, 'BAD_REQUEST')
    return jsonify(response), status

# ==================== STARTUP ====================

if __name__ == '__main__':
    app.logger.info("=" * 60)
    app.logger.info("[START] CardioPredict Backend v2.0 Starting...")
    app.logger.info("=" * 60)
    app.logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    app.logger.info(f"Debug Mode: {app.debug}")
    app.logger.info(f"Model Loaded: {model_loaded}")
    app.logger.info("=" * 60)
    app.logger.info("Server running at http://localhost:5000")
    app.logger.info("API Documentation at http://localhost:5000")
    app.logger.info("=" * 60)
    
    app.run(
        debug=app.debug,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )

