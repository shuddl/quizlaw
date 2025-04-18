import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

import { useAuth } from '@/context/AuthContext';

const HomePage: React.FC = () => {
  const { isAuthenticated, isPremium } = useAuth();
  
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-white py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              Master Legal Concepts with <span className="text-primary">Interactive</span> MCQs
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              Enhance your understanding of complex legal codes through targeted multiple-choice questions designed to test and reinforce key concepts.
            </p>
            <div className="mt-10 flex justify-center">
              <Link to="/quiz-setup" className="btn-primary text-base px-8 py-3 rounded-md shadow">
                Start Practicing Now
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="bg-gray-50 py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
              Our platform uses advanced AI to generate high-quality questions from legal codes and regulations
            </p>
          </div>
          
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            <motion.div
              className="bg-white p-6 rounded-lg shadow"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-white text-xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Choose Your Focus</h3>
              <p className="text-gray-600">
                Select from various legal divisions and customize your quiz settings.
              </p>
            </motion.div>
            
            <motion.div
              className="bg-white p-6 rounded-lg shadow"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-white text-xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Test Your Knowledge</h3>
              <p className="text-gray-600">
                Answer challenging multiple-choice questions with immediate feedback.
              </p>
            </motion.div>
            
            <motion.div
              className="bg-white p-6 rounded-lg shadow"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.3 }}
            >
              <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-white text-xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Review & Learn</h3>
              <p className="text-gray-600">
                Get detailed explanations and track your progress over time.
              </p>
            </motion.div>
          </div>
        </div>
      </section>
      
      {/* Premium Features Section */}
      <section className="py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="premium-badge">Premium</span>
            <h2 className="mt-2 text-3xl font-bold text-gray-900">Upgrade Your Learning Experience</h2>
            <p className="mt-4 text-gray-600 max-w-2xl mx-auto">
              Unlock powerful features designed to help you master legal concepts faster
            </p>
          </div>
          
          <div className="mt-12 grid gap-8 md:grid-cols-2">
            <motion.div
              className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <h3 className="text-xl font-semibold mb-4">Detailed Explanations</h3>
              <p className="text-gray-600 mb-4">
                Get in-depth explanations for every answer, citing specific sections of legal code.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Clear reasoning for correct answers</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Analysis of why incorrect options are wrong</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Direct citations from source material</span>
                </li>
              </ul>
            </motion.div>
            
            <motion.div
              className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <h3 className="text-xl font-semibold mb-4">Progress Tracking</h3>
              <p className="text-gray-600 mb-4">
                Monitor your performance over time with detailed analytics and insights.
              </p>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Track scores across different legal divisions</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Identify areas for improvement</span>
                </li>
                <li className="flex items-start">
                  <svg className="h-5 w-5 text-primary mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Visualize progress over time</span>
                </li>
              </ul>
            </motion.div>
          </div>
          
          <div className="mt-12 text-center">
            {isPremium ? (
              <div className="bg-green-50 text-green-700 p-4 rounded-lg inline-block">
                <p className="font-semibold">You're enjoying premium features!</p>
              </div>
            ) : (
              <Link to={isAuthenticated ? '/premium' : '/register'} className="btn-primary text-base px-8 py-3 rounded-md shadow">
                {isAuthenticated ? 'Upgrade to Premium' : 'Sign Up for Premium'}
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;