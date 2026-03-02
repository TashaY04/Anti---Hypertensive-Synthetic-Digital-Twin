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
            models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
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

def validate_patient_data(data):
    """Validate patient inputs and raise ValueError for invalid entries."""
    age = int(data.get('age', 50))
    height = float(data.get('height', 170))
    weight = float(data.get('weight', 70))
    systolic = int(data.get('systolic', 140))
    diastolic = int(data.get('diastolic', 90))
    gender = str(data.get('gender', 'male')).lower()
    pregnancy = bool(data.get('pregnancy', False))

    if age < 13 or age > 100:
        raise ValueError("Age must be between 13 and 100.")
    if height < 120 or height > 220:
        raise ValueError("Height must be between 120 cm and 220 cm.")
    if weight < 35 or weight > 250:
        raise ValueError("Weight must be between 35 kg and 250 kg.")
    if systolic < 80 or systolic > 260:
        raise ValueError("Systolic BP must be between 80 and 260 mmHg.")
    if diastolic < 40 or diastolic > 160:
        raise ValueError("Diastolic BP must be between 40 and 160 mmHg.")
    if diastolic >= systolic:
        raise ValueError("Diastolic BP must be lower than systolic BP.")
    if gender not in {'male', 'female'}:
        raise ValueError("Gender must be either male or female.")
    if gender == 'male' and pregnancy:
        raise ValueError("Pregnancy cannot be selected for male patients.")

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


def build_recommendations(data, top_n=3):
    """Run model prediction and build filtered recommendations."""
    validate_patient_data(data)
    features = extract_features(data)
    top_5, probs = model_loader.predict(features)

    if top_5 is None:
        return None

    current_medication_type = data.get('currentMedicationType', '')
    allergies = data.get('allergies', '')
    is_on_medication = data.get('isOnMedication', False)

    recommendations = []
    for idx in top_5:
        drug_class = DRUG_CLASSES[idx]
        if check_allergy(drug_class, allergies):
            continue

        is_current = (drug_class == current_medication_type and is_on_medication)
        confidence = float(probs[idx] * 100)

        recommendations.append({
            'rank': len(recommendations) + 1,
            'drug_name': DRUG_NAMES[drug_class],
            'drug_class': drug_class,
            'confidence': confidence,
            'is_current': is_current,
            'has_allergy': False,
            'message': 'Continue your current medication' if is_current else 'Recommended alternative',
            'expected_bp_reduction': 12 + (confidence / 8),
            'explanation': get_explanation(drug_class, data)
        })

    return recommendations[:top_n]


def prioritize_forced_drug(recommendations, forced_drug_class):
    """Move a selected drug class to the top of recommendation list."""
    if not forced_drug_class:
        return recommendations

    forced = [rec for rec in recommendations if rec.get('drug_class') == forced_drug_class]
    others = [rec for rec in recommendations if rec.get('drug_class') != forced_drug_class]
    ordered = forced + others

    # Refresh ranks after reordering
    for idx, rec in enumerate(ordered, start=1):
        rec['rank'] = idx

    return ordered

def _build_tip_context(patient_data, recommendations):
    """Build compact context string for personalized AI tips."""
    alcohol_map = {0: 'None', 1: 'Moderate', 2: 'Heavy'}
    exercise_map = {0: 'Rarely / Never', 1: '1-2 days/week', 2: '3-4 days/week', 3: 'Daily / almost daily'}
    diet_map = {0: 'Needs improvement', 1: 'Moderate', 2: 'Healthy'}
    stress_map = {0: 'Low', 1: 'Moderate', 2: 'High', 3: 'Very high'}

    conditions = []
    if patient_data.get('diabetes'):
        conditions.append('Diabetes')
    if patient_data.get('kidney'):
        conditions.append('Kidney disease')
    if patient_data.get('pregnancy'):
        conditions.append('Pregnancy')
    if patient_data.get('depression'):
        conditions.append('Depression / Anxiety')
    if patient_data.get('smoker'):
        conditions.append('Smoker')

    recommendation_lines = []
    for idx, rec in enumerate(recommendations[:3], start=1):
        recommendation_lines.append(
            f"{idx}. {rec.get('drug_name')} ({rec.get('confidence', 0):.1f}% match) - {rec.get('explanation', '')}"
        )

    return f"""
Patient Profile:
- Age: {patient_data.get('age')}
- Gender: {patient_data.get('gender', 'male')}
- Blood Pressure: {patient_data.get('systolic')}/{patient_data.get('diastolic')} mmHg
- BMI inputs: Weight {patient_data.get('weight')} kg, Height {patient_data.get('height')} cm
- Exercise: {exercise_map.get(int(patient_data.get('exercise', 1)), 'Unknown')}
- Diet quality: {diet_map.get(int(patient_data.get('diet', 1)), 'Unknown')}
- Stress level (0-3): {stress_map.get(int(patient_data.get('stress', 1)), 'Moderate')}
- Alcohol use: {alcohol_map.get(int(patient_data.get('alcohol', 0)), 'None')}
- Current BP medication: {"Yes" if patient_data.get('isOnMedication') else "No"} {patient_data.get('currentMedicationType', '')}
- Reported allergies: {patient_data.get('allergies') or 'None'}
- Conditions/risk factors: {', '.join(conditions) if conditions else 'None reported'}

Top Medication Options Predicted:
{chr(10).join(recommendation_lines) if recommendation_lines else '- Not available'}
""".strip()


def get_ai_tips(patient_data, recommendations):
    """Generate structured 5-factor personalized AI tips."""
    api_key = os.environ.get('GEMINI_API_KEY', '')

    fallback_tips = get_default_tips(patient_data, recommendations)
    if not api_key:
        return fallback_tips

    try:
        prompt = f"""You are a clinical hypertension co-pilot.
Create exactly 5 personalized recommendations in this exact order and format:
1. Weight/BMI:
2. Dietary Measures:
3. Medication Measures:
4. Workout Measures:
5. Special Measures:

Rules:
- Personalize each line using the patient's actual values.
- For Weight/BMI, include ideal BMI target and current/target direction.
- For Special Measures:
  - if smoker or alcohol use present, include quitting advice specific to selected habits.
  - else if pregnancy is true, include pregnancy-specific blood pressure precautions.
  - if stress is moderate/high, include yoga recommendation.
- Keep each line concise and actionable.
- Return only 5 numbered lines.

{_build_tip_context(patient_data, recommendations)}
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)

        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            tips = []
            for line in text.split('\n'):
                line = line.strip()
                if line and len(line) > 12:
                    tip = line.lstrip('0123456789.-•) ').strip()
                    if tip:
                        tips.append(tip)
            if len(tips) >= 5:
                return tips[:5]
            return fallback_tips
        else:
            return fallback_tips

    except Exception as e:
        print(f"Gemini API error: {e}")
        return fallback_tips

def get_default_tips(patient_data, recommendations):
    """Structured 5-factor personalized fallback when Gemini is unavailable."""
    height_cm = float(patient_data.get('height', 170))
    weight_kg = float(patient_data.get('weight', 70))
    height_m = max(1.2, height_cm / 100.0)
    bmi = weight_kg / (height_m ** 2)
    target_bmi = 22.0
    target_weight = target_bmi * (height_m ** 2)
    weight_delta = target_weight - weight_kg

    if bmi > 24.9:
        bmi_tip = (
            f"Weight/BMI: Your BMI is {bmi:.1f}; target BMI is around {target_bmi:.1f}, "
            f"so aim to lose about {abs(weight_delta):.1f} kg gradually."
        )
    elif bmi < 18.5:
        bmi_tip = (
            f"Weight/BMI: Your BMI is {bmi:.1f}; target BMI is around {target_bmi:.1f}, "
            f"so aim to gain about {abs(weight_delta):.1f} kg with clinician-guided nutrition."
        )
    else:
        bmi_tip = (
            f"Weight/BMI: Your BMI is {bmi:.1f}; keep it near the ideal target range around BMI {target_bmi:.1f} with stable weight habits."
        )

    diet_level = int(patient_data.get('diet', 1))
    sodium_reduction = float(patient_data.get('sodiumReductionPercent', 0))
    if diet_level == 0:
        diet_tip = "Dietary Measures: Shift to a DASH-style plan and reduce sodium to below 2300 mg/day by removing packaged salty foods."
    elif diet_level == 1:
        diet_tip = "Dietary Measures: Improve to a strict DASH pattern with more vegetables, fruits, and potassium-rich foods while reducing sodium."
    else:
        diet_tip = "Dietary Measures: Continue your healthy diet and keep daily sodium consistently low to sustain blood pressure response."
    if sodium_reduction > 0:
        diet_tip = diet_tip[:-1] + f"; current scenario includes {int(sodium_reduction)}% sodium reduction."

    top_drug = recommendations[0]['drug_name'] if recommendations else 'the recommended medication'
    medication_tip = (
        f"Medication Measures: Use {top_drug} exactly as prescribed, monitor home BP twice daily, and review response with your physician in 2-4 weeks."
    )

    exercise = int(patient_data.get('exercise', 1))
    stress = int(patient_data.get('stress', 1))
    if exercise <= 1:
        workout_tip = "Workout Measures: Build toward 150 minutes/week of moderate activity, starting with 20-30 minutes most days."
    else:
        workout_tip = "Workout Measures: Maintain regular activity and add 2 weekly strength sessions to improve blood pressure control."
    if stress >= 1:
        workout_tip = workout_tip[:-1] + " and include 10-15 minutes of yoga daily for stress control."

    smoker = bool(patient_data.get('smoker'))
    alcohol = int(patient_data.get('alcohol', 0))
    pregnancy = bool(patient_data.get('pregnancy'))
    if smoker or alcohol > 0:
        parts = []
        if smoker:
            parts.append("start a smoking cessation plan immediately")
        if alcohol == 1:
            parts.append("limit alcohol to guideline levels")
        elif alcohol == 2:
            parts.append("stop heavy alcohol intake and plan alcohol-free days")
        special_tip = f"Special Measures: {', and '.join(parts).capitalize()} to reduce cardiovascular risk and improve BP response."
    elif pregnancy:
        special_tip = (
            "Special Measures: During pregnancy, monitor BP closely, attend frequent obstetric reviews, and seek urgent care for headache, vision changes, or swelling."
        )
    else:
        special_tip = (
            "Special Measures: Continue avoiding tobacco and excess alcohol, and keep weekly BP logs for proactive follow-up."
        )

    return [bmi_tip, diet_tip, medication_tip, workout_tip, special_tip]


def classify_bp_risk(systolic, diastolic):
    """Classify BP stage for simulation output."""
    if systolic >= 180 or diastolic >= 120:
        return 'Hypertensive Crisis'
    if systolic >= 140 or diastolic >= 90:
        return 'High'
    if systolic >= 130 or diastolic >= 80:
        return 'Moderate'
    if systolic >= 120 and diastolic < 80:
        return 'Elevated'
    return 'Normal'


def calculate_lifestyle_effect(patient_data):
    """Estimate additional BP effect from lifestyle profile."""
    effect = 0.0
    exercise = int(patient_data.get('exercise', 1))
    diet = int(patient_data.get('diet', 1))
    alcohol = int(patient_data.get('alcohol', 0))
    stress = int(patient_data.get('stress', 1))
    sodium_reduction = float(patient_data.get('sodiumReductionPercent', 0))
    adherence_percent = float(patient_data.get('adherencePercent', 100))
    stress_intervention = float(patient_data.get('stressInterventionPercent', 0))
    sleep_hours = float(patient_data.get('sleepHours', 7))
    sleep_quality = int(patient_data.get('sleepQuality', 1))
    salt_intake_mg = float(patient_data.get('saltIntakeMg', 3400))

    if exercise >= 2:
        effect += 2.0
    elif exercise == 0:
        effect -= 1.5

    if diet == 2:
        effect += 2.0
    elif diet == 0:
        effect -= 1.5

    if alcohol == 2:
        effect -= 2.0
    elif alcohol == 1:
        effect -= 0.6

    if patient_data.get('smoker'):
        effect -= 2.0

    if stress >= 2:
        effect -= 1.2

    if sodium_reduction > 0:
        # 0-40% sodium reduction contributes up to ~2.5 mmHg
        effect += min(2.5, (sodium_reduction / 40.0) * 2.5)

    # 1800-5000mg intake mapped to approx +2.5 to -2.0 mmHg contribution
    if salt_intake_mg <= 2000:
        effect += 2.5
    elif salt_intake_mg >= 4500:
        effect -= 2.0
    else:
        effect += (3200 - salt_intake_mg) / 1300.0

    # Better stress intervention reduces penalty
    if stress_intervention > 0:
        effect += min(2.0, (stress_intervention / 100.0) * 2.0)

    # Sleep effect
    if sleep_hours < 6:
        effect -= 1.8
    elif sleep_hours >= 7:
        effect += 0.8

    if sleep_quality == 2:
        effect += 0.9
    elif sleep_quality == 0:
        effect -= 0.9

    weight = float(patient_data.get('weight', 70))
    height = float(patient_data.get('height', 170))
    bmi = weight / ((height / 100.0) ** 2)
    if bmi >= 30:
        effect -= 1.5
    elif bmi < 25:
        effect += 0.8

    return effect


def get_drug_effect_mmHg(drug_class):
    """Approximate systolic BP reduction range mid-points by class."""
    effect_map = {
        'ACE_Inhibitor': 11.5,
        'ARB': 10.5,
        'Calcium_Channel_Blocker': 10.0,
        'Diuretic': 9.5,
        'Beta_Blocker': 8.5,
        'Alpha_Blocker': 7.5,
        'Central_Acting': 9.0
    }
    return effect_map.get(drug_class, 9.0)


def simulate_trajectory(patient_data, recommendation, weeks=4):
    """Simulate weekly BP trajectory for one recommendation."""
    baseline_sys = float(patient_data.get('systolic', 140))
    baseline_dia = float(patient_data.get('diastolic', 90))
    drug_class = recommendation.get('drug_class', '')
    confidence = float(recommendation.get('confidence', 70.0))
    dosage_multiplier = float(patient_data.get('dosageMultiplier', 1.0))
    dosage_multiplier = float(np.clip(dosage_multiplier, 0.6, 1.4))
    adherence_percent = float(np.clip(float(patient_data.get('adherencePercent', 100)), 40, 100))

    drug_effect = get_drug_effect_mmHg(drug_class)
    drug_effect *= dosage_multiplier
    drug_effect *= (0.65 + (adherence_percent / 100.0) * 0.35)
    confidence_factor = 0.75 + (min(max(confidence, 0.0), 100.0) / 100.0) * 0.35
    lifestyle_effect = calculate_lifestyle_effect(patient_data)

    total_sys_drop = max(3.0, drug_effect * confidence_factor + lifestyle_effect)
    total_dia_drop = max(2.0, total_sys_drop * 0.55)

    trajectory = []
    for week in range(0, weeks + 1):
        # Saturating response over time (faster in early weeks, then plateaus)
        progress = 1.0 - np.exp(-0.65 * week)
        sys_noise = np.sin(week + baseline_sys / 50.0) * 0.8
        dia_noise = np.cos(week + baseline_dia / 50.0) * 0.5

        systolic = baseline_sys - (total_sys_drop * progress) + sys_noise
        diastolic = baseline_dia - (total_dia_drop * progress) + dia_noise

        systolic = float(np.clip(systolic, 100, 220))
        diastolic = float(np.clip(diastolic, 60, 130))

        trajectory.append({
            'week': week,
            'systolic': round(systolic, 1),
            'diastolic': round(diastolic, 1),
            'risk': classify_bp_risk(systolic, diastolic)
        })

    return trajectory


def simulate_drug_comparisons(patient_data, recommendations):
    """Generate trajectories for each recommended drug option."""
    comparisons = []
    for rec in recommendations:
        comparisons.append({
            'drug_name': rec.get('drug_name'),
            'drug_class': rec.get('drug_class'),
            'trajectory': simulate_trajectory(patient_data, rec, weeks=4)
        })
    return comparisons


def apply_what_if_scenario(patient_data, scenario):
    """Apply what-if intervention settings to patient profile."""
    updated = dict(patient_data or {})

    dosage_multiplier = float(scenario.get('dosage_multiplier', 1.0))
    updated['dosageMultiplier'] = float(np.clip(dosage_multiplier, 0.6, 1.4))

    if 'exercise_level' in scenario:
        updated['exercise'] = int(np.clip(int(scenario.get('exercise_level', updated.get('exercise', 1))), 0, 3))

    sodium_reduction = float(scenario.get('sodium_reduction_percent', 0))
    updated['sodiumReductionPercent'] = float(np.clip(sodium_reduction, 0, 50))
    if 'salt_intake_mg' in scenario:
        updated['saltIntakeMg'] = float(np.clip(float(scenario.get('salt_intake_mg', 3400)), 1500, 6000))
    else:
        updated['saltIntakeMg'] = float(updated.get('saltIntakeMg', 3400))

    # Translate sodium improvement into diet quality lift when meaningful
    if updated['sodiumReductionPercent'] >= 30:
        updated['diet'] = max(int(updated.get('diet', 1)), 2)
    elif updated['sodiumReductionPercent'] >= 15:
        updated['diet'] = max(int(updated.get('diet', 1)), 1)

    if 'bmi_delta' in scenario:
        bmi_delta = float(np.clip(float(scenario.get('bmi_delta', 0)), -8, 8))
        height_cm = float(updated.get('height', 170))
        height_m = max(1.2, height_cm / 100.0)
        base_weight = float(updated.get('weight', 70))
        updated['weight'] = max(35.0, round(base_weight + (bmi_delta * (height_m ** 2)), 1))

    if 'weight_change_kg' in scenario:
        weight_change_kg = float(np.clip(float(scenario.get('weight_change_kg', 0)), -20, 20))
        updated['weight'] = max(35.0, round(float(updated.get('weight', 70)) + weight_change_kg, 1))

    if 'smoker' in scenario:
        updated['smoker'] = bool(scenario.get('smoker'))

    if 'adherence_percent' in scenario:
        updated['adherencePercent'] = float(np.clip(float(scenario.get('adherence_percent', 100)), 40, 100))

    if 'stress_intervention_percent' in scenario:
        updated['stressInterventionPercent'] = float(np.clip(float(scenario.get('stress_intervention_percent', 0)), 0, 100))

    if 'sleep_hours' in scenario:
        updated['sleepHours'] = float(np.clip(float(scenario.get('sleep_hours', 7)), 4, 10))

    if 'sleep_quality' in scenario:
        updated['sleepQuality'] = int(np.clip(int(scenario.get('sleep_quality', 1)), 0, 2))

    if 'forced_drug_class' in scenario and scenario.get('forced_drug_class'):
        updated['forcedDrugClass'] = scenario.get('forced_drug_class')
    else:
        updated['forcedDrugClass'] = ''

    # Safety: keep pregnancy false for male profile.
    if str(updated.get('gender', 'male')).lower() == 'male':
        updated['pregnancy'] = False

    return updated

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

        top_recommendations = build_recommendations(data, top_n=3)

        if top_recommendations is None:
            return jsonify({'error': 'Models not loaded. Please run: python3 train.py'}), 500

        if len(top_recommendations) < 3:
            return jsonify({'error': 'Limited recommendations due to allergies'}), 400

        is_on_medication = data.get('isOnMedication', False)
        current_medication_type = data.get('currentMedicationType', '')
        allergies = data.get('allergies', '')
        
        # Get AI tips
        ai_tips = get_ai_tips(data, top_recommendations)
        best_trajectory = simulate_trajectory(data, top_recommendations[0], weeks=4)
        drug_comparisons = simulate_drug_comparisons(data, top_recommendations)
        
        # Response
        response = {
            'success': True,
            'best_recommendation': top_recommendations[0],
            'all_recommendations': top_recommendations,
            'ai_tips': ai_tips,
            'simulation': {
                'weeks': 4,
                'best_trajectory': best_trajectory,
                'drug_comparisons': drug_comparisons,
                'assumptions': [
                    'Trajectory combines estimated drug class effect with lifestyle contribution.',
                    'Weekly progression follows a saturating response over 4 weeks.',
                    'Outputs are simulation estimates for planning and discussion, not prescriptions.'
                ]
            },
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
        if isinstance(e, ValueError):
            return jsonify({'error': str(e), 'type': 'ValidationError'}), 400
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


@app.route('/api/what-if', methods=['POST', 'OPTIONS'])
def what_if():
    """Counterfactual scenario simulation endpoint."""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        payload = request.json or {}
        base_patient_data = payload.get('patient_data') or {}
        scenario = payload.get('scenario') or {}

        if not base_patient_data:
            return jsonify({'error': 'patient_data is required'}), 400

        simulated_data = apply_what_if_scenario(base_patient_data, scenario)
        all_recommendations = build_recommendations(simulated_data, top_n=5)
        forced_drug_class = simulated_data.get('forcedDrugClass', '')
        ordered_recommendations = prioritize_forced_drug(all_recommendations or [], forced_drug_class)
        top_recommendations = ordered_recommendations[:3]

        if top_recommendations is None:
            return jsonify({'error': 'Models not loaded. Please run: python3 train.py'}), 500
        if len(top_recommendations) < 3:
            return jsonify({'error': 'Limited recommendations due to allergies'}), 400

        best_trajectory = simulate_trajectory(simulated_data, top_recommendations[0], weeks=4)
        drug_comparisons = simulate_drug_comparisons(simulated_data, top_recommendations)
        ai_tips = get_ai_tips(simulated_data, top_recommendations)
        week4 = best_trajectory[-1]

        response = {
            'success': True,
            'best_recommendation': top_recommendations[0],
            'all_recommendations': top_recommendations,
            'ai_tips': ai_tips,
            'simulation': {
                'weeks': 4,
                'best_trajectory': best_trajectory,
                'drug_comparisons': drug_comparisons,
                'assumptions': [
                    'What-if simulation reruns model recommendations on adjusted patient state.',
                    'Dose multiplier scales estimated class effect within bounded range.',
                    'Sodium and BMI changes affect lifestyle contribution and projected BP trend.'
                ]
            },
            'risk_summary': {
                'baseline': classify_bp_risk(float(base_patient_data.get('systolic', 140)), float(base_patient_data.get('diastolic', 90))),
                'projected_week4': week4.get('risk'),
                'projected_bp': f"{week4.get('systolic')}/{week4.get('diastolic')} mmHg"
            },
            'patient_summary': {
                'age': simulated_data.get('age'),
                'gender': simulated_data.get('gender', 'male'),
                'bp': f"{simulated_data.get('systolic')}/{simulated_data.get('diastolic')} mmHg",
                'on_medication': simulated_data.get('isOnMedication', False),
                'current_medication': DRUG_NAMES.get(simulated_data.get('currentMedicationType')) if simulated_data.get('isOnMedication') else None,
                'has_allergies': bool(simulated_data.get('allergies'))
            },
            'scenario_applied': {
                'dosage_multiplier': simulated_data.get('dosageMultiplier', 1.0),
                'exercise_level': simulated_data.get('exercise', 1),
                'sodium_reduction_percent': simulated_data.get('sodiumReductionPercent', 0),
                'salt_intake_mg': simulated_data.get('saltIntakeMg', 3400),
                'adherence_percent': simulated_data.get('adherencePercent', 100),
                'stress_intervention_percent': simulated_data.get('stressInterventionPercent', 0),
                'sleep_hours': simulated_data.get('sleepHours', 7),
                'sleep_quality': simulated_data.get('sleepQuality', 1),
                'bmi_adjusted_weight': simulated_data.get('weight'),
                'forced_drug_class': forced_drug_class,
                'smoker': simulated_data.get('smoker', False)
            },
            'disclaimer': 'What-if outputs are simulated estimates for decision support and must be clinically validated.'
        }

        return jsonify(response)

    except Exception as e:
        if isinstance(e, ValueError):
            return jsonify({'error': str(e), 'type': 'ValidationError'}), 400
        print(f"ERROR in what-if: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500

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
