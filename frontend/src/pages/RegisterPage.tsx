import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { useAuth } from '@/context/AuthContext';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password || !confirmPassword) {
      setError('Please fill in all fields.');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      await register(email, password);
      
      // Redirect to home after successful registration
      navigate('/');
    } catch (err: any) {
      if (err.response && err.response.status === 400) {
        setError('This email is already registered. Please use a different email or log in.');
      } else {
        setError('Registration failed. Please try again later.');
      }
      console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="container-narrow py-12">
      <motion.div
        className="card max-w-md mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="text-2xl font-bold mb-6 text-center">Create Account</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">Email</label>
            <input
              type="email"
              id="email"
              className="form-input"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password" className="form-label">Password</label>
            <input
              type="password"
              id="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              minLength={8}
            />
            <p className="text-xs text-gray-600 mt-1">
              Must be at least 8 characters long
            </p>
          </div>
          
          <div className="form-group">
            <label htmlFor="confirm-password" className="form-label">Confirm Password</label>
            <input
              type="password"
              id="confirm-password"
              className="form-input"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          
          <button
            type="submit"
            className="btn-primary w-full py-2 mt-4"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                Creating account...
              </span>
            ) : 'Sign Up'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default RegisterPage;