import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './AssessmentPage.css';

const AssessmentPage = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    age: 45,
    gender: 'male',
    weight: 70,
    height: 170,
    systolic: 145,
    diastolic: 92,
    exercise: 1,
    diet: 1,
    stress: 1,
    alcohol: 0,  // NEW
    diabetes: false,
    kidney: false,
    pregnancy: false,
    depression: false,
    smoker: false,
    isOnMedication: false,
    currentMedicationType: '',  // NEW: Dropdown instead of text
    allergies: ''  // NEW
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.1 }
    })
  };

  return (
    <div className="assessment-page">
      <div className="assessment-container">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="assessment-header"
        >
          <h1>✨ Complete Health Assessment</h1>
          <p>Your personalized treatment journey starts here</p>
        </motion.div>

        <form onSubmit={handleSubmit} className="assessment-form">
          {/* Demographics */}
          <motion.div custom={0} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card">
            <div className="card-header gradient-blue">
              <span className="card-icon"></span>
              <h2>About You</h2>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>Age (years)</label>
                <input type="number" value={formData.age} onChange={(e) => handleChange('age', parseInt(e.target.value))} min="13" max="100" />
              </div>

              <div className="form-group">
                <label>Gender</label>
                <div className="radio-group horizontal">
                  <label className="radio-option">
                    <input type="radio" checked={formData.gender === 'male'} onChange={() => handleChange('gender', 'male')} />
                    <span>👨 Male</span>
                  </label>
                  <label className="radio-option">
                    <input type="radio" checked={formData.gender === 'female'} onChange={() => handleChange('gender', 'female')} />
                    <span>👩 Female</span>
                  </label>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Weight (kg)</label>
                  <input type="number" value={formData.weight} onChange={(e) => handleChange('weight', parseFloat(e.target.value))} />
                </div>
                <div className="form-group">
                  <label>Height (cm)</label>
                  <input type="number" value={formData.height} onChange={(e) => handleChange('height', parseFloat(e.target.value))} />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Vitals */}
          <motion.div custom={1} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card">
            <div className="card-header gradient-red">
              <span className="card-icon"></span>
              <h2>Vital Signs</h2>
            </div>
            <div className="card-content">
              <div className="form-row">
                <div className="form-group">
                  <label>Systolic BP (mmHg)</label>
                  <input type="number" value={formData.systolic} onChange={(e) => handleChange('systolic', parseInt(e.target.value))} />
                </div>
                <div className="form-group">
                  <label>Diastolic BP (mmHg)</label>
                  <input type="number" value={formData.diastolic} onChange={(e) => handleChange('diastolic', parseInt(e.target.value))} />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Current Medication - ENHANCED */}
          <motion.div custom={2} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card medication-card">
            <div className="card-header gradient-orange">
              <span className="card-icon"></span>
              <h2>Current Medication</h2>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label className="checkbox-label primary">
                  <input type="checkbox" checked={formData.isOnMedication} onChange={(e) => handleChange('isOnMedication', e.target.checked)} />
                  <span>I am currently taking blood pressure medication</span>
                </label>
              </div>

              {formData.isOnMedication && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="form-group medication-select"
                >
                  <label>What type of medication are you currently taking?</label>
                  <select
                    value={formData.currentMedicationType}
                    onChange={(e) => handleChange('currentMedicationType', e.target.value)}
                    className="medication-dropdown"
                  >
                    <option value="">Select medication type...</option>
                    <option value="ACE_Inhibitor">ACE Inhibitor (Lisinopril, Enalapril)</option>
                    <option value="ARB">ARB (Losartan, Valsartan)</option>
                    <option value="Calcium_Channel_Blocker">Calcium Channel Blocker (Amlodipine)</option>
                    <option value="Diuretic">Diuretic (Hydrochlorothiazide)</option>
                    <option value="Beta_Blocker">Beta Blocker (Metoprolol, Atenolol)</option>
                    <option value="Alpha_Blocker">Alpha Blocker (Doxazosin)</option>
                    <option value="Central_Acting">Central Acting Agent (Clonidine)</option>
                  </select>
                  <small className="help-text">Select the category that matches your current medication</small>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Allergies - NEW */}
          <motion.div custom={3} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card allergy-card">
            <div className="card-header gradient-purple">
              <span className="card-icon"></span>
              <h2>Allergies & Sensitivities</h2>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>Do you have any medication allergies?</label>
                <textarea
                  value={formData.allergies}
                  onChange={(e) => handleChange('allergies', e.target.value)}
                  placeholder="E.g., ACE inhibitors cause dry cough, allergic to sulfa drugs, etc."
                  rows="3"
                  className="allergy-input"
                />
                <small className="help-text">List any medications you cannot take and why. This helps us avoid harmful recommendations.</small>
              </div>
            </div>
          </motion.div>

          {/* Lifestyle - ENHANCED */}
          <motion.div custom={4} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card">
            <div className="card-header gradient-green">
              <span className="card-icon"></span>
              <h2>Lifestyle Factors</h2>
            </div>
            <div className="card-content">
              <div className="form-group">
                <label>Exercise Frequency</label>
                <select value={formData.exercise} onChange={(e) => handleChange('exercise', parseInt(e.target.value))}>
                  <option value={0}>Rarely / Never</option>
                  <option value={1}>1-2 times per week</option>
                  <option value={2}>3-4 times per week</option>
                  <option value={3}>Daily or almost daily</option>
                </select>
              </div>

              <div className="form-group">
                <label>Diet Quality</label>
                <select value={formData.diet} onChange={(e) => handleChange('diet', parseInt(e.target.value))}>
                  <option value={0}>Needs improvement (high sodium, processed foods)</option>
                  <option value={1}>Moderate (balanced but not optimal)</option>
                  <option value={2}>Healthy (DASH diet, low sodium, fruits & vegetables)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Alcohol Consumption</label>
                <div className="radio-group">
                  <label className="radio-option">
                    <input type="radio" checked={formData.alcohol === 0} onChange={() => handleChange('alcohol', 0)} />
                    <span>🚫 None</span>
                  </label>
                  <label className="radio-option">
                    <input type="radio" checked={formData.alcohol === 1} onChange={() => handleChange('alcohol', 1)} />
                    <span>🍷 Moderate (1-2 drinks occasionally)</span>
                  </label>
                  <label className="radio-option">
                    <input type="radio" checked={formData.alcohol === 2} onChange={() => handleChange('alcohol', 2)} />
                    <span>🍺 Heavy (3+ drinks regularly)</span>
                  </label>
                </div>
              </div>

              <div className="checkbox-group">
                <label className="checkbox-label">
                  <input type="checkbox" checked={formData.smoker} onChange={(e) => handleChange('smoker', e.target.checked)} />
                  <span>🚬 I smoke tobacco</span>
                </label>
              </div>
            </div>
          </motion.div>

          {/* Medical History */}
          <motion.div custom={5} initial="hidden" animate="visible" variants={cardVariants} className="assessment-card">
            <div className="card-header gradient-teal">
              <span className="card-icon"></span>
              <h2>Medical History</h2>
            </div>
            <div className="card-content">
              <div className="checkbox-group">
                {[
                  { key: 'diabetes', label: 'Diabetes', icon: '💉' },
                  { key: 'kidney', label: 'Kidney Disease', icon: '🫘' },
                  { key: 'depression', label: 'Depression/Anxiety', icon: '🧠' },
                  { key: 'pregnancy', label: 'Pregnancy (if applicable)', icon: '🤰' }
                ].map(({ key, label, icon }) => (
                  <label key={key} className="checkbox-label">
                    <input type="checkbox" checked={formData[key]} onChange={(e) => handleChange(key, e.target.checked)} />
                    <span>{icon} {label}</span>
                  </label>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Submit */}
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            whileHover={{ scale: 1.02, boxShadow: '0 15px 40px rgba(16, 185, 129, 0.4)' }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="submit-button"
          >
            ✨ Get My Personalized Treatment Plan
          </motion.button>
        </form>
      </div>
    </div>
  );
};

export default AssessmentPage;
