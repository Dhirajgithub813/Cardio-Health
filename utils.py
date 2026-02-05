# Utility Functions Module

import numpy as np
from datetime import datetime, timedelta

class AgeConverter:
    """Convert between age in years and days"""
    
    DAYS_PER_YEAR = 365.25
    
    @staticmethod
    def years_to_days(years):
        """Convert age from years to days"""
        return round(years * AgeConverter.DAYS_PER_YEAR)
    
    @staticmethod
    def days_to_years(days):
        """Convert age from days to years"""
        return round(days / AgeConverter.DAYS_PER_YEAR)


class RiskAssessor:
    """Assess cardiovascular risk level"""
    
    RISK_THRESHOLDS = {
        'low': 30,
        'moderate': 60,
        'high': 100
    }
    
    RISK_COLORS = {
        'low': 'green',
        'moderate': 'orange',
        'high': 'red'
    }
    
    @staticmethod
    def get_risk_level(probability):
        """
        Get risk level from probability
        
        Args:
            probability (float): Probability between 0 and 1
        
        Returns:
            dict: {level, color, percentage}
        """
        percentage = probability * 100
        
        if percentage < RiskAssessor.RISK_THRESHOLDS['low']:
            level = 'Low Risk'
            risk_key = 'low'
        elif percentage < RiskAssessor.RISK_THRESHOLDS['moderate']:
            level = 'Moderate Risk'
            risk_key = 'moderate'
        else:
            level = 'High Risk'
            risk_key = 'high'
        
        return {
            'level': level,
            'color': RiskAssessor.RISK_COLORS[risk_key],
            'percentage': round(percentage, 2)
        }


class BMICalculator:
    """Calculate BMI and related metrics"""
    
    CATEGORIES = {
        'underweight': (0, 18.5),
        'normal': (18.5, 25),
        'overweight': (25, 30),
        'obese': (30, float('inf'))
    }
    
    @staticmethod
    def calculate_bmi(height_cm, weight_kg):
        """
        Calculate BMI
        
        Args:
            height_cm (float): Height in centimeters
            weight_kg (float): Weight in kilograms
        
        Returns:
            float: BMI value
        """
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)
    
    @staticmethod
    def get_category(bmi):
        """Get BMI category"""
        for category, (min_val, max_val) in BMICalculator.CATEGORIES.items():
            if min_val <= bmi < max_val:
                return category
        return 'obese'


class DataPreprocessor:
    """Data preprocessing utilities"""
    
    @staticmethod
    def normalize_input(data):
        """
        Normalize input data for prediction
        
        Args:
            data (dict): Input data from user
        
        Returns:
            list: Normalized feature array
        """
        # Convert age from years to days
        age_days = AgeConverter.years_to_days(data['age'])
        
        # Calculate BMI
        bmi = BMICalculator.calculate_bmi(data['height'], data['weight'])
        
        features = [
            age_days,
            data['gender'],
            data['height'],
            data['weight'],
            data['ap_hi'],
            data['ap_lo'],
            data['cholesterol'],
            data['gluc'],
            data['smoke'],
            data['alco'],
            data['active'],
            bmi
        ]
        
        return np.array([features])


class ResponseFormatter:
    """Format API responses"""
    
    @staticmethod
    def success(data, message=None, status_code=200):
        """Format success response"""
        response = {
            'status': 'success',
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        if message:
            response['message'] = message
        return response, status_code
    
    @staticmethod
    def error(message, status_code=400, error_code=None):
        """Format error response"""
        response = {
            'status': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if error_code:
            response['error_code'] = error_code
        return response, status_code
    
    @staticmethod
    def list_response(items, total, limit, offset):
        """Format list response with pagination"""
        return {
            'status': 'success',
            'items': items,
            'pagination': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'pages': (total + limit - 1) // limit,
                'has_next': offset + limit < total
            },
            'timestamp': datetime.now().isoformat()
        }


class HealthCheck:
    """Health check utilities"""
    
    @staticmethod
    def get_system_status(model_loaded, prediction_count):
        """Get system health status"""
        status = 'healthy' if model_loaded else 'unhealthy'
        
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'model_loaded': model_loaded,
            'predictions_made': prediction_count,
            'uptime': 'Check server logs',
            'message': 'All systems operational' if model_loaded else 'Model not loaded'
        }


class DateUtils:
    """Date/time utilities"""
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    @staticmethod
    def parse_timestamp(timestamp_str):
        """Parse timestamp string"""
        try:
            return datetime.fromisoformat(timestamp_str)
        except:
            return None
    
    @staticmethod
    def is_recent(timestamp_str, hours=24):
        """Check if timestamp is within hours"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return (datetime.now() - timestamp).total_seconds() < (hours * 3600)
        except:
            return False
