"""
FIXED Flask API with debugging
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import os
import requests
import sys

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for development

# Configuration
DRUG_CLASSES = ['ACE_Inhibitor', 'ARB', 'Calcium_Channel_Blocker', 'Diuretic', 
                'Beta_Blocker', 'Alpha_Blocker', 'Central_Acting']

DRUG_NAMES = {
    'ACE_Inhibitor': 'ACE Inhibitor (Lisinopril)',
    'ARB': 'ARB (Losartan)',
    'Calcium_Channel_Blocker': 'Calcium Channel Blocker (Amlodipine)',
    'Diuretic': 'Diuretic (Hydrochlorothiazide)',
    'Beta_Blocker': 'Beta Blocker (Metoprolol)',
    'Alpha_Blocker': 'Alpha Blocker (Doxazosin)',
    'Central_Acting': 'Central Acting Agent (Clonidine)'
}

DRUG_COMPONENTS = {
    'ACE_Inhibitor': ['lisinopril', 'ace inhibitor', 'enalapril'],
    'ARB': ['losartan', 'valsartan', 'arb', 'sartan'],
    'Calcium_Channel_Blocker': ['amlodipine', 'calcium channel blocker', 'nifedipine', 'dipine'],
    'Diuretic': ['hydrochlorothiazide', 'furosemide', 'diuretic', 'thiazide'],
    'Beta_Blocker': ['metoprolol', 'atenolol', 'beta blocker', 'olol'],
    'Alpha_Blocker': ['doxazosin', 'prazosin', 'alpha blocker', 'zosin'],
    'Central_Acting': ['clonidine', 'methyldopa', 'central acting']
}

class ModelLoader:
    def __init__(self):
        self.xgb = None
        self.rf = None
        self.gb = None
        self.load_models()
    
    def load_models(self):
        try:
            models_dir = "models"
            print(f"Loading models from {os.path.abspath(models_dir)}")
            
            self.xgb = xgb.XGBClassifier()
            self.xgb.load_model(os.path.join(models_dir, "xgb.json"))
            
            with open(os.path.join(models_dir, "rf.pkl"), 'rb') as f:
                self.rf = pickle.load(f)
            
            with open(os.path.join(models_dir, "gb.pkl"), 'rb') as f:
                self.gb = pickle.load(f)
            
            print("✓ Models loaded successfully")
        except Exception as e:
            print(f"✗ Model loading error: {e}")
            print("Please run: python3 train.py")
    
    def predict(self, features):
        if not all([self.xgb, self.rf, self.gb]):
            return None, None
        
        xgb_probs = self.xgb.predict_proba(features)
        rf_probs = self.rf.predict_proba(features)
        gb_probs = self.gb.predict_proba(features)
        
        probs = xgb_probs * 0.4 + rf_probs * 0.35 + gb_probs * 0.25
        top_5 = np.argsort(probs, axis=1)[:, ::-1][:, :5]
        
        return top_5[0], probs[0]

model_loader = ModelLoader()

def extract_features(data):
    """Extract features with validation"""
    try:
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        bmi = weight / ((height/100) ** 2)
        
        features = np.array([[
            int(data.get('age', 50)),
            int(data.get('systolic', 140)),
            int(data.get('diastolic', 90)),
            bmi,
            int(data.get('exercise', 1)),
            int(data.get('diet', 1)),
            int(data.get('stress', 1)),
            1 if data.get('diabetes') else 0,
            1 if data.get('kidney') else 0,
            1 if data.get('pregnancy') else 0,
            1 if data.get('depression') else 0,
            1 if data.get('smoker') else 0,
            int(data.get('alcohol', 0))
        ]])
        
        return features
    except Exception as e:
        print(f"Feature extraction error: {e}")
        raise

def check_allergy(drug_class, allergies):
    """Check if drug conflicts with allergies"""
    if not allergies:
        return False
    
    allergies_lower = allergies.lower()
    drug_components = DRUG_COMPONENTS.get(drug_class, [])
    
    for component in drug_components:
        if component in allergies_lower:
            return True
    
    return False

def get_ai_tips(patient_data):
    """Get AI tips or fallback"""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    if not api_key:
        return get_default_tips(patient_data)
    
    try:
        prompt = f"""Provide 5 brief lifestyle tips for a hypertension patient:
Age: {patient_data.get('age')}
BP: {patient_data.get('systolic')}/{patient_data.get('diastolic')}
Exercise: {patient_data.get('exercise', 1)}/3
Smoker: {'Yes' if patient_data.get('smoker') else 'No'}
Alcohol: {['None', 'Moderate', 'Heavy'][patient_data.get('alcohol', 0)]}

Give 5 short actionable tips."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            tips = []
            for line in text.split('\n'):
                line = line.strip()
                if line and len(line) > 20:
                    tip = line.lstrip('0123456789.-•) ').strip()
                    if tip:
                        tips.append(tip)
            return tips[:5] if tips else get_default_tips(patient_data)
        else:
            return get_default_tips(patient_data)
            
    except Exception as e:
        print(f"Gemini API error: {e}")
        return get_default_tips(patient_data)

def get_default_tips(patient_data):
    """Fallback tips"""
    tips = [
        "Exercise regularly: Aim for 30 minutes of moderate activity 5 days per week to naturally lower blood pressure.",
        "Follow DASH diet: Increase fruits, vegetables, and whole grains while reducing sodium to less than 2,300mg daily.",
        "Monitor your blood pressure at home regularly and keep a log to share with your healthcare provider.",
        "Reduce stress through meditation, deep breathing exercises, or yoga for 10-15 minutes each day.",
        "Maintain a healthy weight: Even losing 5-10 pounds can significantly reduce blood pressure."
    ]
    
    if patient_data.get('alcohol', 0) > 0:
        tips[1] = "Limit alcohol: No more than 1 drink daily for women, 2 for men. Excessive alcohol raises blood pressure."
    
    if patient_data.get('smoker'):
        tips[2] = "Quit smoking immediately: Smoking damages blood vessels and significantly raises cardiovascular risk."
    
    return tips[:5]

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Main prediction endpoint"""
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        print("\n=== New Prediction Request ===")
        data = request.json
        print(f"Received data: {data}")
        
        # Extract features
        features = extract_features(data)
        print(f"Extracted features shape: {features.shape}")
        
        # Get predictions
        top_5, probs = model_loader.predict(features)
        
        if top_5 is None:
            return jsonify({'error': 'Models not loaded. Please run: python3 train.py'}), 500
        
        print(f"Predictions: {top_5}")
        print(f"Probabilities: {probs}")
        
        # Get inputs
        current_medication_type = data.get('currentMedicationType', '')
        allergies = data.get('allergies', '')
        is_on_medication = data.get('isOnMedication', False)
        
        # Build recommendations
        recommendations = []
        
        for idx in top_5:
            drug_class = DRUG_CLASSES[idx]
            
            # Check allergy
            has_allergy = check_allergy(drug_class, allergies)
            if has_allergy:
                continue
            
            # Check if current
            is_current = (drug_class == current_medication_type and is_on_medication)
            
            confidence = float(probs[idx] * 100)
            
            recommendations.append({
                'drug_name': DRUG_NAMES[drug_class],
                'drug_class': drug_class,
                'confidence': confidence,
                'is_current': is_current,
                'has_allergy': False,
                'message': 'Continue your current medication' if is_current else 'Recommended alternative',
                'expected_bp_reduction': 12 + (confidence / 8),
                'explanation': get_explanation(drug_class, data)
            })
        
        if len(recommendations) < 3:
            return jsonify({'error': 'Limited recommendations due to allergies'}), 400
        
        top_recommendations = recommendations[:3]
        
        # Get AI tips
        ai_tips = get_ai_tips(data)
        
        # Response
        response = {
            'success': True,
            'best_recommendation': top_recommendations[0],
            'all_recommendations': top_recommendations,
            'ai_tips': ai_tips,
            'patient_summary': {
                'age': data.get('age'),
                'gender': data.get('gender', 'male'),
                'bp': f"{data.get('systolic')}/{data.get('diastolic')} mmHg",
                'on_medication': is_on_medication,
                'current_medication': DRUG_NAMES.get(current_medication_type) if is_on_medication else None,
                'has_allergies': bool(allergies)
            },
            'disclaimer': 'This is an AI recommendation for informational purposes only. Always consult a healthcare provider before starting, stopping, or changing any medication.'
        }
        
        print("Response prepared successfully")
        return jsonify(response)
        
    except Exception as e:
        print(f"ERROR in predict: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

def get_explanation(drug_class, data):
    """Get explanation"""
    explanations = {
        'ACE_Inhibitor': 'Kidney protective, excellent for diabetic patients' if data.get('diabetes') else 'Effective first-line treatment',
        'ARB': 'Safe alternative with similar benefits',
        'Calcium_Channel_Blocker': 'Safe for kidney disease and pregnancy' if data.get('kidney') or data.get('pregnancy') else 'Well-tolerated option',
        'Diuretic': 'Excellent first-line therapy',
        'Beta_Blocker': 'Ideal for anxiety and stress management',
        'Alpha_Blocker': 'Beneficial for resistant hypertension',
        'Central_Acting': 'Effective for complex cases'
    }
    return explanations.get(drug_class, 'Clinically proven treatment')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    models_loaded = all([model_loader.xgb, model_loader.rf, model_loader.gb])
    return jsonify({
        'status': 'healthy' if models_loaded else 'models not loaded',
        'models_loaded': models_loaded
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("STARTING BACKEND API SERVER")
    print("="*60)
    print(f"Models loaded: {all([model_loader.xgb, model_loader.rf, model_loader.gb])}")
    print("API: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
