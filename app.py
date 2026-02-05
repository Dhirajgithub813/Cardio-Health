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

@app.route('/analytics')
def analytics_page():
    """Analytics dashboard page"""
    app.logger.debug("GET /analytics - Analytics page")
    return render_template('analytics.html')

@app.route('/results')
def results_page():
    """Results and history page"""
    app.logger.debug("GET /results - Results page")
    return render_template('results.html')

@app.route('/about')
def about_page():
    """About page"""
    app.logger.debug("GET /about - About page")
    return render_template('about.html')

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
        
        # Create feature array
        features = np.array([[
            float(age_in_days),
            float(data['gender']),
            float(data['height']),
            float(data['weight']),
            float(data['ap_hi']),
            float(data['ap_lo']),
            float(data['cholesterol']),
            float(data['gluc']),
            float(data['smoke']),
            float(data['alco']),
            float(data['active']),
            bmi
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)
        probability = model.predict_proba(features_scaled)
        
        # Extract scalar values
        pred_value = int(prediction[0])
        prob_value = probability[0]
        
        # Get risk assessment
        risk_info = RiskAssessor.get_risk_level(float(prob_value[1]))
        
        # Generate unique prediction ID
        prediction_id = str(uuid.uuid4())[:8]
        
        # Create prediction record
        pred_record = PredictionRecord(
            prediction_id=prediction_id,
            prediction=pred_value,
            probability=prob_value,
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
            active=data['active']
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
            'disease_probability': float(prob_value[1]),
            'healthy_probability': float(prob_value[0]),
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

@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Get dataset statistics"""
    try:
        df = pd.read_csv('cardio_train (1).csv', sep=';')
        
        stats = {
            'total_records': len(df),
            'disease_cases': int(df['cardio'].sum()),
            'healthy_cases': int((df['cardio'] == 0).sum()),
            'disease_percentage': float(df['cardio'].mean() * 100),
            'features': {
                'age': {
                    'min': AgeConverter.days_to_years(int(df['age'].min())),
                    'max': AgeConverter.days_to_years(int(df['age'].max())),
                    'mean': AgeConverter.days_to_years(int(df['age'].mean()))
                },
                'weight': {
                    'min': float(df['weight'].min()),
                    'max': float(df['weight'].max()),
                    'mean': float(df['weight'].mean())
                },
                'height': {
                    'min': float(df['height'].min()),
                    'max': float(df['height'].max()),
                    'mean': float(df['height'].mean())
                }
            },
            'high_bp_count': int((df['ap_hi'] > 140).sum()),
            'high_cholesterol_count': int((df['cholesterol'] >= 2).sum()),
            'smokers_count': int((df['smoke'] == 1).sum())
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        log_error(app, "StatisticsError", str(e))
        response, status = ResponseFormatter.error(str(e), 400)
        return jsonify(response), status

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

@app.route('/results')
def results_page():
    """Results page"""
    return render_template('results.html')

# ==================== API ROUTES ====================

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict cardiovascular disease
    Expected JSON:
    {
        "age": 18393,
        "gender": 2,
        "height": 168,
        "weight": 62,
        "ap_hi": 110,
        "ap_lo": 80,
        "cholesterol": 1,
        "gluc": 1,
        "smoke": 0,
        "alco": 0,
        "active": 1
    }
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                          'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Calculate BMI
        bmi = BMICalculator.calculate_bmi(data['height'], data['weight'])
        
        # Create feature array in correct order
        features = np.array([[
            data['age'], data['gender'], data['height'], data['weight'],
            data['ap_hi'], data['ap_lo'], data['cholesterol'], data['gluc'],
            data['smoke'], data['alco'], data['active'], bmi
        ]])
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]
        
        # Risk assessment
        risk_percentage = probability[1] * 100
        if risk_percentage < 30:
            risk_level = "Low Risk"
            color = "green"
        elif risk_percentage < 60:
            risk_level = "Moderate Risk"
            color = "orange"
        else:
            risk_level = "High Risk"
            color = "red"
        
        # Generate unique prediction ID
        prediction_id = str(uuid.uuid4())[:8]
        
        # Store prediction in history
        prediction_record = {
            'id': prediction_id,
            'prediction': int(prediction),
            'has_disease': bool(prediction),
            'disease_probability': float(probability[1]),
            'healthy_probability': float(probability[0]),
            'risk_percentage': float(risk_percentage),
            'risk_level': risk_level,
            'color': color,
            'timestamp': datetime.now().isoformat(),
            'age_days': data['age'],
            'age_years': round(data['age'] / 365.25),
            'gender': data['gender'],
            'height': data['height'],
            'weight': data['weight'],
            'bp_systolic': data['ap_hi'],
            'bp_diastolic': data['ap_lo'],
            'cholesterol': data['cholesterol'],
            'gluc': data['gluc'],
            'smoke': data['smoke'],
            'alco': data['alco'],
            'active': data['active'],
            'status': 'completed'
        }
        
        # Track in history and statistics
        prediction_history[prediction_id] = prediction_record
        prediction_stats['total_predictions'] += 1
        
        if risk_percentage >= 60:
            prediction_stats['total_high_risk'] += 1
        elif risk_percentage >= 30:
            prediction_stats['total_moderate_risk'] += 1
        else:
            prediction_stats['total_low_risk'] += 1
        
        return jsonify({
            'prediction_id': prediction_id,
            'prediction': int(prediction),
            'has_disease': bool(prediction),
            'disease_probability': float(probability[1]),
            'healthy_probability': float(probability[0]),
            'risk_percentage': float(risk_percentage),
            'risk_level': risk_level,
            'color': color,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/model-info', methods=['GET'])
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'features': feature_names,
        'feature_count': len(feature_names),
        'model_type': 'RandomForestClassifier',
        'n_estimators': 100
    })

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """
    Batch prediction for multiple records
    Expected JSON array of prediction objects
    """
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'error': 'Expected JSON array'}), 400
        
        results = []
        
        for record in data:
            bmi = BMICalculator.calculate_bmi(record['height'], record['weight'])
            
            features = np.array([[
                record['age'], record['gender'], record['height'], record['weight'],
                record['ap_hi'], record['ap_lo'], record['cholesterol'], record['gluc'],
                record['smoke'], record['alco'], record['active'], bmi
            ]])
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0]
            
            risk_percentage = probability[1] * 100
            
            results.append({
                'prediction': int(prediction),
                'risk_percentage': float(risk_percentage)
            })
        
        return jsonify({
            'total_records': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/statistics', methods=['GET'])
def statistics():
    """Get dataset statistics"""
    try:
        df = pd.read_csv('cardio_train (1).csv', sep=';')
        
        stats = {
            'total_records': len(df),
            'disease_cases': int(df['cardio'].sum()),
            'healthy_cases': int((df['cardio'] == 0).sum()),
            'disease_percentage': float(df['cardio'].mean() * 100),
            'features': {
                'age': {
                    'min': float(df['age'].min()),
                    'max': float(df['age'].max()),
                    'mean': float(df['age'].mean())
                },
                'weight': {
                    'min': float(df['weight'].min()),
                    'max': float(df['weight'].max()),
                    'mean': float(df['weight'].mean())
                },
                'height': {
                    'min': float(df['height'].min()),
                    'max': float(df['height'].max()),
                    'mean': float(df['height'].mean())
                }
            },
            'high_bp_count': int((df['ap_hi'] > 140).sum()),
            'high_cholesterol_count': int((df['cholesterol'] >= 2).sum()),
            'smokers_count': int((df['smoke'] == 1).sum())
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== PREDICTION STATUS ENDPOINTS ====================

@app.route('/api/prediction/<prediction_id>', methods=['GET'])
def get_prediction_status(prediction_id):
    """Get status and details of a specific prediction by ID"""
    try:
        if prediction_id not in prediction_history:
            return jsonify({'error': 'Prediction not found'}), 404
        
        prediction_record = prediction_history[prediction_id]
        
        return jsonify({
            'status': 'found',
            'prediction': prediction_record,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/prediction-status', methods=['GET'])
def prediction_status_summary():
    """Get overall prediction status and statistics"""
    try:
        return jsonify({
            'status': 'active',
            'total_predictions': prediction_stats['total_predictions'],
            'risk_distribution': {
                'low_risk': prediction_stats['total_low_risk'],
                'moderate_risk': prediction_stats['total_moderate_risk'],
                'high_risk': prediction_stats['total_high_risk']
            },
            'recent_predictions': list(prediction_history.values())[-10:],  # Last 10
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/prediction-history', methods=['GET'])
def prediction_history_endpoint():
    """Get full prediction history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        history_list = list(prediction_history.values())
        total = len(history_list)
        
        # Sort by timestamp (newest first)
        history_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit and offset
        paginated = history_list[offset:offset+limit]
        
        return jsonify({
            'status': 'success',
            'total_records': total,
            'returned': len(paginated),
            'limit': limit,
            'offset': offset,
            'predictions': paginated,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/prediction-stats', methods=['GET'])
def prediction_detailed_stats():
    """Get detailed prediction statistics"""
    try:
        if not prediction_history:
            return jsonify({
                'status': 'no_data',
                'total_predictions': 0,
                'message': 'No predictions made yet'
            })
        
        predictions_list = list(prediction_history.values())
        
        # Calculate statistics
        risk_percentages = [p['risk_percentage'] for p in predictions_list]
        ages = [p['age'] for p in predictions_list]
        weights = [p['weight'] for p in predictions_list]
        
        return jsonify({
            'status': 'success',
            'total_predictions': len(predictions_list),
            'risk_distribution': {
                'low_risk': prediction_stats['total_low_risk'],
                'moderate_risk': prediction_stats['total_moderate_risk'],
                'high_risk': prediction_stats['total_high_risk']
            },
            'disease_rate': {
                'percentage': round((sum(1 for p in predictions_list if p['has_disease']) / len(predictions_list)) * 100, 2),
                'with_disease': sum(1 for p in predictions_list if p['has_disease']),
                'without_disease': sum(1 for p in predictions_list if not p['has_disease'])
            },
            'risk_percentage_stats': {
                'min': round(min(risk_percentages), 2),
                'max': round(max(risk_percentages), 2),
                'average': round(sum(risk_percentages) / len(risk_percentages), 2)
            },
            'age_stats': {
                'min': min(ages),
                'max': max(ages),
                'average': round(sum(ages) / len(ages), 2)
            },
            'weight_stats': {
                'min': round(min(weights), 2),
                'max': round(max(weights), 2),
                'average': round(sum(weights) / len(weights), 2)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/prediction-health', methods=['GET'])
def prediction_health_endpoint():
    """Check prediction service health and availability"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'prediction',
            'model_loaded': model is not None,
            'total_predictions_made': prediction_stats['total_predictions'],
            'prediction_history_count': len(prediction_history),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/clear-history', methods=['POST'])
def clear_prediction_history():
    """Clear prediction history (admin endpoint)"""
    try:
        global prediction_history, prediction_stats
        
        cleared_count = len(prediction_history)
        
        prediction_history = {}
        prediction_stats = {
            'total_predictions': 0,
            'total_high_risk': 0,
            'total_moderate_risk': 0,
            'total_low_risk': 0
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Cleared {cleared_count} predictions from history',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Cardiovascular Disease Prediction API...")
    print("Server running at http://localhost:5000")
    print("Dashboard available at http://localhost:5000/")
    print("\n[OK] Prediction Status Tracking Enabled")
    print("  - Use /api/prediction-status for overall stats")
    print("  - Use /api/prediction/<id> for specific prediction")
    print("  - Use /api/prediction-history for full history")
    print("  - Use /api/prediction-stats for detailed statistics")
    app.run(debug=True, host='0.0.0.0', port=5000)

