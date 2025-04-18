import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { api } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

// Types for learning summary
interface DivisionStats {
  total_questions: number;
  correct_answers: number;
  accuracy: number;
}

interface TopicStats {
  total_questions: number;
  correct_answers: number;
  accuracy: number;
}

interface OverallStats {
  total_questions_answered: number;
  correct_answers: number;
  accuracy: number;
}

interface UserStats {
  overall: OverallStats;
  by_division: Record<string, DivisionStats>;
  by_topic: Record<string, TopicStats>;
  weakest_divisions: string[];
  weakest_topics: string[];
}

interface Suggestion {
  type: string;
  name: string;
  reason: string;
}

interface LearningSummary {
  stats: UserStats;
  ai_feedback: string;
  suggestions: Suggestion[];
}

// Types for learning goals
interface LearningGoal {
  key: string;
  description: string;
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // State for learning summary
  const [learningSummary, setLearningSummary] = useState<LearningSummary | null>(null);
  const [learningGoals, setLearningGoals] = useState<LearningGoal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<string>(user?.learning_goal || '');
  
  // Fetch learning summary and goals
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch learning summary
        const summary = await api.users.getLearningSummary();
        setLearningSummary(summary);
        
        // Fetch available learning goals
        const goals = await api.users.getLearningGoals();
        setLearningGoals(goals);
        
        // Set selected goal if user has one
        if (user?.learning_goal) {
          setSelectedGoal(user.learning_goal);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load your learning data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [user]);
  
  // Handle setting a new learning goal
  const handleSaveGoal = async () => {
    try {
      await api.users.updateProfile({ learning_goal: selectedGoal });
      setShowGoalModal(false);
      
      // Refresh data
      const summary = await api.users.getLearningSummary();
      setLearningSummary(summary);
    } catch (err) {
      console.error('Error updating learning goal:', err);
      setError('Failed to update your learning goal. Please try again.');
    }
  };
  
  // Function to navigate to quiz setup with pre-filled parameters
  const handleSuggestionClick = (suggestion: Suggestion) => {
    // Prepare parameters based on suggestion type
    const params: any = {
      mode: "sequential",  // Default mode
      numQuestions: 10,    // Default question count
    };
    
    if (suggestion.type === "division") {
      params.division = suggestion.name;
    } else if (suggestion.type === "topic") {
      params.topic = suggestion.name;
    } else if (suggestion.type === "bar_section") {
      params.mode = "law_student";
      const divisionParts = suggestion.name.split(' - ');
      if (divisionParts.length > 0) {
        params.division = divisionParts[0];
      }
    }
    
    // Navigate to quiz setup with these parameters
    navigate("/quiz-setup", { state: { params } });
  };
  
  if (isLoading) {
    return (
      <div className="container-narrow py-12">
        <div className="card text-center py-12">
          <h2 className="text-2xl font-bold mb-4">Loading Dashboard...</h2>
          <div className="w-16 h-16 border-4 border-gray-300 border-t-primary rounded-full animate-spin mx-auto"></div>
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
          <button
            className="btn-primary w-full"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container-narrow py-12">
      <h1 className="text-3xl font-bold mb-8">Your Learning Dashboard</h1>
      
      <div className="grid gap-8 md:grid-cols-2">
        {/* Overall Stats Card */}
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h2 className="text-xl font-bold mb-4">Overall Performance</h2>
          
          {learningSummary?.stats.overall.total_questions_answered > 0 ? (
            <div>
              <div className="flex justify-between items-center mb-2">
                <span>Accuracy</span>
                <span className="font-bold">
                  {(learningSummary.stats.overall.accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className="progress-bar mb-4">
                <div 
                  className="progress-bar-fill"
                  style={{ width: `${learningSummary.stats.overall.accuracy * 100}%` }}
                ></div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold">
                    {learningSummary.stats.overall.total_questions_answered}
                  </div>
                  <div className="text-sm text-gray-600">Questions Answered</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {learningSummary.stats.overall.correct_answers}
                  </div>
                  <div className="text-sm text-gray-600">Correct Answers</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              <p>No quiz data yet. Start practicing to see your stats!</p>
              <Link to="/quiz-setup" className="btn-primary mt-4 inline-block">
                Take Your First Quiz
              </Link>
            </div>
          )}
        </motion.div>
        
        {/* Learning Goal Card */}
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <h2 className="text-xl font-bold mb-4">Your Learning Goal</h2>
          
          {user?.learning_goal ? (
            <div>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <div className="font-medium text-lg">
                  {learningGoals.find(g => g.key === user.learning_goal)?.description || user.learning_goal}
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                Your learning path is tailored to help you achieve this goal.
              </p>
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">
              <p>No learning goal set yet.</p>
              <p className="text-sm mb-4">Setting a goal helps us personalize your learning path.</p>
            </div>
          )}
          
          <button 
            className="btn-outline w-full mt-2"
            onClick={() => setShowGoalModal(true)}
          >
            {user?.learning_goal ? 'Change Goal' : 'Set Learning Goal'}
          </button>
        </motion.div>
      </div>
      
      {/* AI Insights Section */}
      {learningSummary && learningSummary.stats.overall.total_questions_answered > 0 && (
        <motion.div
          className="card mt-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-xl font-bold">AI-Powered Insights</h2>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="whitespace-pre-line">
              {learningSummary.ai_feedback}
            </p>
          </div>
          
          {learningSummary.stats.weakest_divisions.length > 0 && (
            <div className="mt-6">
              <h3 className="font-bold mb-2">Areas to Focus On</h3>
              <div className="grid grid-cols-2 gap-3">
                {learningSummary.stats.weakest_divisions.map((division) => (
                  <div key={division} className="text-sm border border-gray-200 rounded p-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary flex-shrink-0"></span>
                    <span>{division}</span>
                  </div>
                ))}
                {learningSummary.stats.weakest_topics.map((topic) => (
                  <div key={topic} className="text-sm border border-gray-200 rounded p-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary flex-shrink-0"></span>
                    <span>{topic}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
      
      {/* Suggested Next Steps */}
      {learningSummary && learningSummary.suggestions && learningSummary.suggestions.length > 0 && (
        <motion.div
          className="card mt-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white mr-3">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
            <h2 className="text-xl font-bold">Suggested Next Steps</h2>
          </div>
          
          <div className="space-y-4">
            {learningSummary.suggestions.map((suggestion, index) => (
              <motion.div
                key={`${suggestion.type}-${suggestion.name}`}
                className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow"
                whileHover={{ scale: 1.01 }}
                onClick={() => handleSuggestionClick(suggestion)}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: 0.1 * index }}
              >
                <div className="flex justify-between">
                  <div>
                    <div className="font-semibold">{suggestion.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{suggestion.reason}</div>
                  </div>
                  <div className="text-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="mt-6 text-center">
            <Link to="/quiz-setup" className="btn-primary">
              Create Custom Quiz
            </Link>
          </div>
        </motion.div>
      )}
      
      {/* Learning Goal Modal */}
      {showGoalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            className="bg-white rounded-lg p-6 w-full max-w-md"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
          >
            <h3 className="text-xl font-bold mb-4">Set Your Learning Goal</h3>
            
            <p className="text-gray-600 mb-4">
              Your learning goal helps us personalize your quiz experience and recommendations.
            </p>
            
            <div className="space-y-3 mb-6">
              {learningGoals.map((goal) => (
                <div key={goal.key} className="flex items-start">
                  <input
                    type="radio"
                    id={`goal-${goal.key}`}
                    name="learning-goal"
                    value={goal.key}
                    checked={selectedGoal === goal.key}
                    onChange={() => setSelectedGoal(goal.key)}
                    className="mt-1 mr-3"
                  />
                  <label htmlFor={`goal-${goal.key}`} className="cursor-pointer">
                    <div className="font-medium">{goal.description}</div>
                  </label>
                </div>
              ))}
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                className="btn-secondary"
                onClick={() => setShowGoalModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleSaveGoal}
                disabled={!selectedGoal}
              >
                Save Goal
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;