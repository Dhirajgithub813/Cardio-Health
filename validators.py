# Request Validation Module

class PredictionValidator:
    """Validate prediction request data"""
    
    # Valid ranges for input parameters
    AGE_RANGE = (1, 120)  # Years
    HEIGHT_RANGE = (100, 250)  # cm
    WEIGHT_RANGE = (20, 300)  # kg
    BP_RANGE = (40, 300)  # mmHg
    GENDER_OPTIONS = (1, 2)  # 1=Female, 2=Male
    CHOLESTEROL_OPTIONS = (0, 1, 2, 3)
    GLUCOSE_OPTIONS = (0, 1, 2, 3)
    BOOL_OPTIONS = (0, 1)
    BLOOD_GROUP_OPTIONS = ("O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-")
    
    REQUIRED_FIELDS = [
        'age', 'gender', 'height', 'weight',
        'ap_hi', 'ap_lo', 'cholesterol', 'gluc',
        'smoke', 'alco', 'active'
    ]
    
    OPTIONAL_FIELDS = [
        'patientName', 'fatherName', 'bloodGroup', 
        'phoneNumber', 'altPhoneNumber', 'doctorName'
    ]
    
    @staticmethod
    def validate(data):
        """
        Validate prediction request data
        
        Returns:
            (is_valid, error_message) tuple
        """
        
        # Check all required fields present
        for field in PredictionValidator.REQUIRED_FIELDS:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate age (in years)
        age = data.get('age')
        if not isinstance(age, (int, float)):
            return False, "Age must be a number"
        if isinstance(age, (list, tuple)) and len(age) != 1:
            return False, "Age must be a single value, not an array"
        if not (PredictionValidator.AGE_RANGE[0] <= age <= PredictionValidator.AGE_RANGE[1]):
            return False, f"Age must be between {PredictionValidator.AGE_RANGE[0]} and {PredictionValidator.AGE_RANGE[1]} years"
        
        # Validate gender
        gender = data.get('gender')
        if gender not in PredictionValidator.GENDER_OPTIONS:
            return False, f"Gender must be {PredictionValidator.GENDER_OPTIONS}"
        
        # Validate height
        height = data.get('height')
        if not isinstance(height, (int, float)):
            return False, "Height must be a number"
        if isinstance(height, (list, tuple)) and len(height) != 1:
            return False, "Height must be a single value"
        if not (PredictionValidator.HEIGHT_RANGE[0] <= height <= PredictionValidator.HEIGHT_RANGE[1]):
            return False, f"Height must be between {PredictionValidator.HEIGHT_RANGE[0]} and {PredictionValidator.HEIGHT_RANGE[1]} cm"
        
        # Validate weight
        weight = data.get('weight')
        if not isinstance(weight, (int, float)):
            return False, "Weight must be a number"
        if isinstance(weight, (list, tuple)) and len(weight) != 1:
            return False, "Weight must be a single value"
        if not (PredictionValidator.WEIGHT_RANGE[0] <= weight <= PredictionValidator.WEIGHT_RANGE[1]):
            return False, f"Weight must be between {PredictionValidator.WEIGHT_RANGE[0]} and {PredictionValidator.WEIGHT_RANGE[1]} kg"
        
        # Validate blood pressure
        ap_hi = data.get('ap_hi')
        ap_lo = data.get('ap_lo')
        
        if not isinstance(ap_hi, (int, float)) or not isinstance(ap_lo, (int, float)):
            return False, "Blood pressure values must be numbers"
        
        if isinstance(ap_hi, (list, tuple)) or isinstance(ap_lo, (list, tuple)):
            return False, "Blood pressure values must be single numbers, not arrays"
        
        if not (PredictionValidator.BP_RANGE[0] <= ap_hi <= PredictionValidator.BP_RANGE[1]):
            return False, f"Systolic BP must be between {PredictionValidator.BP_RANGE[0]} and {PredictionValidator.BP_RANGE[1]}"
        
        if not (PredictionValidator.BP_RANGE[0] <= ap_lo <= PredictionValidator.BP_RANGE[1]):
            return False, f"Diastolic BP must be between {PredictionValidator.BP_RANGE[0]} and {PredictionValidator.BP_RANGE[1]}"
        
        if ap_lo >= ap_hi:
            return False, "Diastolic BP must be less than Systolic BP"
        
        # Validate cholesterol and glucose
        cholesterol = data.get('cholesterol')
        gluc = data.get('gluc')
        
        if cholesterol not in PredictionValidator.CHOLESTEROL_OPTIONS:
            return False, f"Cholesterol must be one of {PredictionValidator.CHOLESTEROL_OPTIONS}"
        
        if gluc not in PredictionValidator.GLUCOSE_OPTIONS:
            return False, f"Glucose must be one of {PredictionValidator.GLUCOSE_OPTIONS}"
        
        # Validate boolean fields
        smoke = data.get('smoke')
        alco = data.get('alco')
        active = data.get('active')
        
        if smoke not in PredictionValidator.BOOL_OPTIONS:
            return False, "Smoke must be 0 or 1"
        
        if alco not in PredictionValidator.BOOL_OPTIONS:
            return False, "Alco must be 0 or 1"
        
        if active not in PredictionValidator.BOOL_OPTIONS:
            return False, "Active must be 0 or 1"
        
        # Validate optional patient information fields
        blood_group = data.get('bloodGroup')
        if blood_group and blood_group not in PredictionValidator.BLOOD_GROUP_OPTIONS:
            return False, f"Blood group must be one of {PredictionValidator.BLOOD_GROUP_OPTIONS}"
        
        phone_number = data.get('phoneNumber')
        if phone_number and not isinstance(phone_number, str):
            return False, "Phone number must be a string"
        
        alt_phone_number = data.get('altPhoneNumber')
        if alt_phone_number and not isinstance(alt_phone_number, str):
            return False, "Alternative phone number must be a string"
        
        patient_name = data.get('patientName')
        if patient_name and not isinstance(patient_name, str):
            return False, "Patient name must be a string"
        
        father_name = data.get('fatherName')
        if father_name and not isinstance(father_name, str):
            return False, "Father name must be a string"
        
        doctor_name = data.get('doctorName')
        if doctor_name and not isinstance(doctor_name, str):
            return False, "Doctor name must be a string"
        
        return True, None
    
    @staticmethod
    def validate_batch(predictions):
        """Validate batch predictions"""
        if not isinstance(predictions, list):
            return False, "Predictions must be a list"
        
        if len(predictions) == 0:
            return False, "Predictions list cannot be empty"
        
        if len(predictions) > 1000:
            return False, "Maximum 1000 predictions per batch"
        
        errors = []
        for idx, pred in enumerate(predictions):
            is_valid, error = PredictionValidator.validate(pred)
            if not is_valid:
                errors.append(f"Record {idx}: {error}")
        
        if errors:
            return False, "; ".join(errors[:3])  # Return first 3 errors
        
        return True, None
