import React from 'react';
import { motion } from 'framer-motion';
import Avatar from '../components/Avatar';
import './ResultsPage.css';

const ResultsPage = ({ results, onNewAssessment }) => {
  if (!results || !results.success) {
    return (
      <div className="results-page">
        <div className="results-container">
          <p style={{color: 'white', textAlign: 'center', fontSize: '18px'}}>
            {results?.error || 'Error loading results. Please try again.'}
          </p>
          <button onClick={onNewAssessment} className="new-assessment-btn">Try Again</button>
        </div>
      </div>
    );
  }

  const { best_recommendation, all_recommendations, patient_summary, ai_tips, disclaimer } = results;

  return (
    <div className="results-page">
      {/* Header */}
      <div className="results-header">
        <motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          ✨ Your Personalized Treatment Plan
        </motion.h1>
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          {patient_summary.age} years old | BP: {patient_summary.bp}
          {patient_summary.on_medication && ` | Currently on: ${patient_summary.current_medication}`}
          {patient_summary.has_allergies && ' | Has medication allergies'}
        </motion.p>
      </div>

      <div className="results-container">
        <div className="results-layout">
          {/* Left: Recommendations */}
          <div className="results-main">
            {/* Best Recommendation */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="best-card"
            >
              <h2>🎯 {best_recommendation.is_current ? 'Continue Current Medication' : 'Best Recommendation'}</h2>
              <h3>{best_recommendation.drug_name}</h3>
              <p>{best_recommendation.message}</p>
              <div className="metrics">
                <span>✓ {best_recommendation.confidence.toFixed(0)}% Match</span>
                <span>↓ {best_recommendation.expected_bp_reduction.toFixed(1)} mmHg Reduction</span>
              </div>
            </motion.div>

            {/* Alternative Options */}
            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="alternatives-title"
            >
              Alternative Treatment Options
            </motion.h2>

            {all_recommendations.slice(1).map((option, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + index * 0.1 }}
                className="option-card"
              >
                <div className="option-header">
                  <span className="option-rank">Option {option.rank}</span>
                  <span className="option-name">{option.drug_name}</span>
                </div>
                <div className="option-metrics">
                  <span>✓ {option.confidence.toFixed(0)}% Match</span>
                  <span>↓ {option.expected_bp_reduction.toFixed(1)} mmHg</span>
                </div>
                <p>{option.explanation}</p>
              </motion.div>
            ))}

            {/* Disclaimer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="disclaimer"
            >
              {disclaimer}
            </motion.div>
          </div>

          {/* Right: Avatar & AI Tips */}
          <div className="results-sidebar">
            {/* Digital Twin Avatar */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
              className="avatar-section"
            >
              <h3>Your Digital Twin</h3>
              <Avatar gender={patient_summary.gender} recommendations={all_recommendations} />
            </motion.div>

            {/* AI Tips */}
            {ai_tips && ai_tips.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="ai-tips-section"
              >
                <div className="ai-tips-header">
                  <span className="gemini-icon">✨</span>
                  <h3>AI Health Tips</h3>
                  <span className="powered-by">Powered by Gemini</span>
                </div>
                <div className="ai-tips-list">
                  {ai_tips.map((tip, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + index * 0.1 }}
                      className="ai-tip-card"
                    >
                      <span className="tip-number">{index + 1}</span>
                      <p>{tip}</p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* New Assessment Button */}
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onNewAssessment}
          className="new-assessment-btn"
        >
          Start New Assessment
        </motion.button>
      </div>
    </div>
  );
};

export default ResultsPage;
