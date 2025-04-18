import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import { AuthProvider, useAuth } from '@/context/AuthContext';
import Navbar from '@/components/Navbar';
import HomePage from '@/pages/HomePage';
import QuizSetupPage from '@/pages/QuizSetupPage';
import QuizPage from '@/pages/QuizPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div className="p-8 text-center">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Main App component
const AppRoutes: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/quiz-setup" element={<QuizSetupPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <div className="container-narrow py-12">
                  <div className="card">
                    <h2 className="text-2xl font-bold mb-4">My Profile</h2>
                    <p>Profile page content will go here.</p>
                  </div>
                </div>
              </ProtectedRoute>
            } 
          />
          
          {/* 404 route */}
          <Route 
            path="*" 
            element={
              <div className="container-narrow py-12 text-center">
                <h2 className="text-2xl font-bold mb-4">Page Not Found</h2>
                <p>The page you're looking for doesn't exist.</p>
              </div>
            } 
          />
        </Routes>
      </main>
      <footer className="bg-gray-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-600 text-sm">
            &copy; {new Date().getFullYear()} QuizLaw. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

// Wrap the app with the auth provider
const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
};

export default App;