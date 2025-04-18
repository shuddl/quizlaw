import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api, User } from '@/services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isPremium: boolean;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isPremium: false,
});

// Hook to use auth context
export const useAuth = () => useContext(AuthContext);

// Mock function to get user data with token
// In a real app, you'd make an API call to get the user profile
const getUserProfile = async (): Promise<User | null> => {
  try {
    // This is a placeholder - in a real app, you'd fetch the user profile
    // For now, we'll return a mock user based on whether we have a token
    if (api.auth.isAuthenticated()) {
      return {
        id: 'mock-id',
        email: 'user@example.com',
        is_active: true,
        is_superuser: false,
        subscription_tier: 'Free',
        created_at: new Date().toISOString(),
      };
    }
    return null;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    return null;
  }
};

// Auth provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      const userProfile = await getUserProfile();
      setUser(userProfile);
      setIsLoading(false);
    };

    initAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    try {
      await api.auth.login(email, password);
      const userProfile = await getUserProfile();
      setUser(userProfile);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Register function
  const register = async (email: string, password: string) => {
    try {
      const user = await api.auth.register(email, password);
      // Automatically login after registration
      await login(email, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    api.auth.logout();
    setUser(null);
  };

  // Computed values
  const isAuthenticated = !!user;
  const isPremium = user?.subscription_tier === 'Premium';

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        isPremium,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};