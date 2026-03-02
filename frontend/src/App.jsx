import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import WelcomePage from './pages/WelcomePage';
import AssessmentPage from './pages/AssessmentPage';
import ResultsPage from './pages/ResultsPage';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('welcome');
  const [userData, setUserData] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // SLOWER page transitions - 0.8 seconds
  const pageVariants = {
    initial: { opacity: 0, x: -30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 30 }
  };

  const pageTransition = {
    type: 'tween',
    ease: 'easeInOut',
    duration: 0.8  // SLOWER: was 0.4, now 0.8
  };

  const goToAssessment = () => {
    setCurrentPage('assessment');
  };

  const goToResults = async (data) => {
    console.log('Submitting data:', data);
    setUserData(data);
    setLoading(true);
    setError(null);
    
    try {
      console.log('Calling API at http://localhost:5000/api/predict');
      
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Received results:', result);
      
      setResults(result);
      setCurrentPage('results');
    } catch (error) {
      console.error('API Error:', error);
      setError(error.message);
      alert(`Error: ${error.message}\n\nPlease check:\n1. Backend is running (python3 app.py)\n2. Models are trained (python3 train.py)\n3. Check backend terminal for errors`);
    } finally {
      setLoading(false);
    }
  };

  const goToWelcome = () => {
    setCurrentPage('welcome');
    setUserData({});
    setResults(null);
    setError(null);
  };

  return (
    <div className="app">
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Analyzing your health profile...</p>
        </div>
      )}
      
      <AnimatePresence mode="wait">
        {currentPage === 'welcome' && (
          <motion.div
            key="welcome"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <WelcomePage onStart={goToAssessment} />
          </motion.div>
        )}

        {currentPage === 'assessment' && (
          <motion.div
            key="assessment"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <AssessmentPage onSubmit={goToResults} />
          </motion.div>
        )}

        {currentPage === 'results' && results && (
          <motion.div
            key="results"
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={pageTransition}
          >
            <ResultsPage results={results} onNewAssessment={goToWelcome} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
