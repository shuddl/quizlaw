import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { api } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const QuizSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isPremium } = useAuth();
  
  const [divisions, setDivisions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [selectedDivision, setSelectedDivision] = useState<string>('');
  const [selectedMode, setSelectedMode] = useState<string>('random');
  const [numQuestions, setNumQuestions] = useState<number>(10);
  
  useEffect(() => {
    const fetchDivisions = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const fetchedDivisions = await api.quiz.getDivisions();
        
        if (fetchedDivisions.length === 0) {
          setError('No legal divisions available. Please try again later.');
        } else {
          setDivisions(fetchedDivisions);
          setSelectedDivision(fetchedDivisions[0]);
        }
      } catch (err) {
        setError('Failed to load legal divisions. Please try again later.');
        console.error('Error fetching divisions:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDivisions();
  }, []);
  
  const handleModeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedMode(e.target.value);
  };
  
  const handleNumQuestionsChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setNumQuestions(parseInt(e.target.value, 10));
  };
  
  const handleDivisionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDivision(e.target.value);
  };
  
  const handleStartQuiz = () => {
    if (!selectedDivision) {
      setError('Please select a legal division.');
      return;
    }
    
    // Navigate to quiz page with parameters
    navigate('/quiz', {
      state: {
        params: {
          mode: selectedMode,
          division: selectedDivision,
          numQuestions,
        },
      },
    });
  };
  
  if (isLoading) {
    return (
      <div className="container-narrow py-12">
        <div className="card text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Loading...</h2>
          <div className="w-12 h-12 border-4 border-gray-300 border-t-primary rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container-narrow py-12">
        <div className="card">
          <h2 className="text-2xl font-bold mb-4 text-center">Error</h2>
          <p className="text-red-600 mb-6 text-center">{error}</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container-narrow py-12">
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Quiz Setup</h2>
        
        {!isAuthenticated && !isPremium && (
          <div className="mb-6 p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-center">
            <p className="mb-2">
              <span className="font-semibold">Sign in or upgrade to Premium</span> to track your scores and get detailed explanations
            </p>
            <div className="flex gap-2 justify-center">
              <button
                className="btn-outline text-sm px-3 py-1"
                onClick={() => navigate('/login')}
              >
                Sign In
              </button>
              <button
                className="btn-primary text-sm px-3 py-1"
                onClick={() => navigate('/premium')}
              >
                Go Premium
              </button>
            </div>
          </div>
        )}
        
        <div className="space-y-6">
          {/* Division Selection */}
          <div className="form-group">
            <label htmlFor="division" className="form-label">Legal Division</label>
            <select
              id="division"
              className="form-input"
              value={selectedDivision}
              onChange={handleDivisionChange}
            >
              {divisions.map(division => (
                <option key={division} value={division}>
                  {division}
                </option>
              ))}
            </select>
          </div>
          
          {/* Quiz Mode */}
          <div className="form-group">
            <label className="form-label">Quiz Mode</label>
            <div className="space-y-2 mt-2">
              <div className="flex items-center">
                <input
                  type="radio"
                  id="mode-random"
                  name="mode"
                  value="random"
                  checked={selectedMode === 'random'}
                  onChange={handleModeChange}
                  className="mr-2"
                />
                <label htmlFor="mode-random">
                  <span className="font-medium">Random</span>
                  <span className="block text-sm text-gray-600">Questions in random order from the selected division</span>
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="radio"
                  id="mode-sequential"
                  name="mode"
                  value="sequential"
                  checked={selectedMode === 'sequential'}
                  onChange={handleModeChange}
                  className="mr-2"
                />
                <label htmlFor="mode-sequential">
                  <span className="font-medium">Sequential</span>
                  <span className="block text-sm text-gray-600">Questions in order by section number</span>
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="radio"
                  id="mode-law-student"
                  name="mode"
                  value="law_student"
                  checked={selectedMode === 'law_student'}
                  onChange={handleModeChange}
                  className="mr-2"
                />
                <label htmlFor="mode-law-student">
                  <span className="font-medium">Bar Prep</span>
                  <span className="block text-sm text-gray-600">Focus on sections frequently tested on the bar exam</span>
                </label>
              </div>
            </div>
          </div>
          
          {/* Number of Questions */}
          <div className="form-group">
            <label htmlFor="num-questions" className="form-label">Number of Questions</label>
            <select
              id="num-questions"
              className="form-input"
              value={numQuestions}
              onChange={handleNumQuestionsChange}
            >
              <option value={5}>5 questions</option>
              <option value={10}>10 questions</option>
              <option value={25}>25 questions</option>
              <option value={50}>50 questions</option>
            </select>
          </div>
          
          <button
            className="btn-primary w-full py-3 text-lg"
            onClick={handleStartQuiz}
            disabled={!selectedDivision}
          >
            Start Quiz
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default QuizSetupPage;