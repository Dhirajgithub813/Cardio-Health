# Database Models Module (Ready for SQLAlchemy upgrade)

from datetime import datetime

class PredictionRecord:
    """
    Prediction record model
    Can be upgraded to SQLAlchemy ORM model
    """
    
    def __init__(self, prediction_id, prediction, probability, risk_percentage, 
                 risk_level, color, age_days, age_years, gender, height, weight,
                 ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active,
                 patient_name=None, father_name=None, blood_group=None, 
                 phone_number=None, alt_phone_number=None, doctor_name=None):
        self.id = prediction_id
        self.prediction = prediction
        self.disease_probability = probability[1] if isinstance(probability, (list, tuple)) else probability
        self.healthy_probability = probability[0] if isinstance(probability, (list, tuple)) else (1 - probability)
        self.risk_percentage = risk_percentage
        self.risk_level = risk_level
        self.color = color
        self.age_days = age_days
        self.age_years = age_years
        self.gender = gender
        self.height = height
        self.weight = weight
        self.bp_systolic = ap_hi
        self.bp_diastolic = ap_lo
        self.cholesterol = cholesterol
        self.gluc = gluc
        self.smoke = smoke
        self.alco = alco
        self.active = active
        # Patient Information Fields
        self.patient_name = patient_name
        self.father_name = father_name
        self.blood_group = blood_group
        self.phone_number = phone_number
        self.alt_phone_number = alt_phone_number
        self.doctor_name = doctor_name
        self.timestamp = datetime.now().isoformat()
        self.status = 'completed'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'prediction': self.prediction,
            'has_disease': bool(self.prediction),
            'disease_probability': float(self.disease_probability),
            'healthy_probability': float(self.healthy_probability),
            'risk_percentage': float(self.risk_percentage),
            'risk_level': self.risk_level,
            'color': self.color,
            'age_days': self.age_days,
            'age_years': self.age_years,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'bp_systolic': self.bp_systolic,
            'bp_diastolic': self.bp_diastolic,
            'cholesterol': self.cholesterol,
            'gluc': self.gluc,
            'smoke': self.smoke,
            'alco': self.alco,
            'active': self.active,
            'patient_name': self.patient_name,
            'father_name': self.father_name,
            'blood_group': self.blood_group,
            'phone_number': self.phone_number,
            'alt_phone_number': self.alt_phone_number,
            'doctor_name': self.doctor_name,
            'timestamp': self.timestamp,
            'status': self.status
        }


class StatisticsRecord:
    """
    Statistics record for tracking prediction stats
    """
    
    def __init__(self):
        self.total_predictions = 0
        self.total_high_risk = 0
        self.total_moderate_risk = 0
        self.total_low_risk = 0
        self.total_disease = 0
        self.total_healthy = 0
        self.predictions = []
    
    def add_prediction(self, prediction_record):
        """Add prediction to statistics"""
        self.total_predictions += 1
        
        if prediction_record.risk_percentage >= 60:
            self.total_high_risk += 1
        elif prediction_record.risk_percentage >= 30:
            self.total_moderate_risk += 1
        else:
            self.total_low_risk += 1
        
        if prediction_record.prediction == 1:
            self.total_disease += 1
        else:
            self.total_healthy += 1
        
        self.predictions.append(prediction_record)
    
    def get_summary(self):
        """Get statistics summary"""
        return {
            'total_predictions': self.total_predictions,
            'risk_distribution': {
                'low_risk': self.total_low_risk,
                'moderate_risk': self.total_moderate_risk,
                'high_risk': self.total_high_risk
            },
            'disease_rate': {
                'with_disease': self.total_disease,
                'without_disease': self.total_healthy,
                'percentage': round((self.total_disease / self.total_predictions * 100), 2) if self.total_predictions > 0 else 0
            }
        }


# SQLAlchemy model template (for future database migration)
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.String(8), primary_key=True)
    prediction = db.Column(db.Integer)
    disease_probability = db.Column(db.Float)
    healthy_probability = db.Column(db.Float)
    risk_percentage = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    color = db.Column(db.String(10))
    age_days = db.Column(db.Integer)
    age_years = db.Column(db.Integer)
    gender = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    bp_systolic = db.Column(db.Integer)
    bp_diastolic = db.Column(db.Integer)
    cholesterol = db.Column(db.Integer)
    gluc = db.Column(db.Integer)
    smoke = db.Column(db.Integer)
    alco = db.Column(db.Integer)
    active = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='completed')
    
    def to_dict(self):
        return {
            'id': self.id,
            'prediction': self.prediction,
            'risk_percentage': self.risk_percentage,
            'risk_level': self.risk_level,
            'timestamp': self.timestamp.isoformat()
        }
"""
