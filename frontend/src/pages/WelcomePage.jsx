import React from 'react';
import { motion } from 'framer-motion';
import './WelcomePage.css';

const WelcomePage = ({ onStart }) => {
  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="welcome-badge"
        >
          DIGITAL TWIN HEALTH
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
        >
          Welcome to Your Health Journey
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="welcome-subtitle"
        >
          AI-Powered Personalized Hypertension Care
        </motion.p>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="welcome-features"
        >
          {[
            { title: 'Personalized', desc: 'Tailored to your unique health profile' },
            { title: 'AI-Powered', desc: 'Advanced machine learning analysis' },
            { title: 'Evidence-Based', desc: 'Research-backed recommendations' }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 + index * 0.15, duration: 0.8 }}
              className="feature-card"
            >
              <h3>{feature.title}</h3>
              <p>{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.8 }}
          whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(249, 115, 22, 0.42)' }}
          whileTap={{ scale: 0.95 }}
          onClick={onStart}
          className="start-button"
        >
          Begin Assessment
        </motion.button>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.8 }}
          className="welcome-footer"
        >
          Takes 3-5 minutes - Completely confidential
        </motion.p>
      </div>
    </div>
  );
};

export default WelcomePage;
