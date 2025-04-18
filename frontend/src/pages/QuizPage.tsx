import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { api, QuizQuestion as QuizQuestionType, AnswerCheck } from '@/services/api';
import QuizQuestion from '@/components/QuizQuestion';
import { useAuth } from '@/context/AuthContext';

interface QuizParams {
  mode: 'random' | 'sequential' | 'law_student';
  division: string;
  numQuestions: number;
}

const QuizPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isPremium } = useAuth();
  
  // Get quiz parameters from location state or use defaults
  const params: QuizParams = location.state?.params || {
    mode: 'random',
    division: 'Default Division',
    numQuestions: 10,
  };
  
  const [questions, setQuestions] = useState<QuizQuestionType[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quizComplete, setQuizComplete] = useState(false);
  
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const fetchedQuestions = await api.quiz.getQuestions(
          params.mode,
          params.division,
          params.numQuestions
        );
        
        if (fetchedQuestions.length === 0) {
          setError('No questions available for the selected criteria.');
        } else {
          setQuestions(fetchedQuestions);
        }
      } catch (err) {
        setError('Failed to load questions. Please try again later.');
        console.error('Error fetching questions:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchQuestions();
  }, [params.mode, params.division, params.numQuestions]);
  
  const handleAnswer = async (answer: string): Promise<AnswerCheck> => {
    try {
      const currentQuestion = questions[currentQuestionIndex];
      const result = await api.quiz.checkAnswer(currentQuestion.id, answer);
      
      if (result.is_correct) {
        setScore(prevScore => prevScore + 1);
      }
      
      return result;
    } catch (err) {
      console.error('Error checking answer:', err);
      throw err;
    }
  };
  
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prevIndex => prevIndex + 1);
    } else {
      setQuizComplete(true);
    }
  };
  
  const handleRestartQuiz = async () => {
    try {
      setIsLoading(true);
      
      const fetchedQuestions = await api.quiz.getQuestions(
        params.mode,
        params.division,
        params.numQuestions
      );
      
      setQuestions(fetchedQuestions);
      setCurrentQuestionIndex(0);
      setScore(0);
      setQuizComplete(false);
    } catch (err) {
      setError('Failed to restart quiz. Please try again later.');
      console.error('Error restarting quiz:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSetupNewQuiz = () => {
    navigate('/quiz-setup');
  };
  
  // Display loading state
  if (isLoading) {
    return (
      <div className="container-narrow py-12">
        <div className="card text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Loading Quiz...</h2>
          <div className="w-16 h-16 border-4 border-gray-300 border-t-primary rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }
  
  // Display error state
  if (error) {
    return (
      <div className="container-narrow py-12">
        <div className="card text-center">
          <h2 className="text-2xl font-bold mb-4">Error</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button
            className="btn-primary"
            onClick={handleSetupNewQuiz}
          >
            Return to Quiz Setup
          </button>
        </div>
      </div>
    );
  }
  
  // Display quiz completion state
  if (quizComplete) {
    const percentage = Math.round((score / questions.length) * 100);
    const isPassing = percentage >= 70;
    
    return (
      <div className="container-narrow py-12">
        <motion.div
          className="card"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-2xl font-bold mb-4 text-center">Quiz Complete!</h2>
          
          <div className="text-center mb-8">
            <div className="inline-block rounded-full p-1 bg-gray-100">
              <div 
                className={`text-white rounded-full w-32 h-32 flex items-center justify-center ${
                  isPassing ? 'bg-green-500' : 'bg-red-500'
                }`}
              >
                <span className="text-4xl font-bold">{percentage}%</span>
              </div>
            </div>
            <p className="mt-4 text-xl">
              You scored <span className="font-bold">{score}</span> out of <span className="font-bold">{questions.length}</span>
            </p>
            
            {isPremium ? (
              <p className="mt-2 text-sm text-gray-600">
                Your results have been saved to your profile
              </p>
            ) : (
              <p className="mt-2 text-sm text-gray-600">
                Upgrade to Premium to save your quiz history and track progress
              </p>
            )}
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <button 
              className="btn-primary flex-1"
              onClick={handleRestartQuiz}
            >
              Retry This Quiz
            </button>
            <button 
              className="btn-outline flex-1"
              onClick={handleSetupNewQuiz}
            >
              New Quiz
            </button>
          </div>
          
          {!isPremium && (
            <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h3 className="text-center font-bold mb-2">Upgrade to Premium</h3>
              <p className="text-center text-sm mb-4">
                Get access to explanations, progress tracking, and more
              </p>
              <button className="btn-primary w-full">
                Upgrade Now
              </button>
            </div>
          )}
        </motion.div>
      </div>
    );
  }
  
  // Display current question
  const currentQuestion = questions[currentQuestionIndex];
  
  return (
    <div className="container-narrow py-8">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-gray-600">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
          <span className="text-sm text-gray-600">
            Score: {score}/{currentQuestionIndex}
          </span>
        </div>
        <div className="progress-bar">
          <div 
            className="progress-bar-fill"
            style={{ width: `${((currentQuestionIndex) / questions.length) * 100}%` }}
          ></div>
        </div>
      </div>
      
      {currentQuestion && (
        <QuizQuestion
          question={currentQuestion}
          onAnswer={handleAnswer}
          onNext={handleNextQuestion}
        />
      )}
    </div>
  );
};

export default QuizPage;