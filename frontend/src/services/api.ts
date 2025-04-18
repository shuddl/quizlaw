import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Types
export interface QuizQuestion {
  id: string;
  question_text: string;
  options: Record<string, string>;
  source_url?: string;
}

export interface AnswerCheck {
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  subscription_tier: 'Free' | 'Premium';
  learning_goal?: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserUpdateData {
  email?: string;
  password?: string;
  learning_goal?: string;
}

export interface DivisionStats {
  total_questions: number;
  correct_answers: number;
  accuracy: number;
}

export interface TopicStats {
  total_questions: number;
  correct_answers: number;
  accuracy: number;
}

export interface OverallStats {
  total_questions_answered: number;
  correct_answers: number;
  accuracy: number;
}

export interface UserStats {
  overall: OverallStats;
  by_division: Record<string, DivisionStats>;
  by_topic: Record<string, TopicStats>;
  weakest_divisions: string[];
  weakest_topics: string[];
}

export interface Suggestion {
  type: string;
  name: string;
  reason: string;
}

export interface LearningSummary {
  stats: UserStats;
  ai_feedback: string;
  suggestions: Suggestion[];
}

export interface LearningGoal {
  key: string;
  description: string;
}

// Create API client
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API functions
export const api = {
  // Quiz endpoints
  quiz: {
    getQuestions: async (
      mode: 'random' | 'sequential' | 'law_student',
      division: string,
      numQuestions: number = 10
    ): Promise<QuizQuestion[]> => {
      const response: AxiosResponse<QuizQuestion[]> = await apiClient.post('/quiz', {
        mode,
        division,
        num_questions: numQuestions,
      });
      return response.data;
    },

    checkAnswer: async (questionId: string, selectedAnswer: string): Promise<AnswerCheck> => {
      const response: AxiosResponse<AnswerCheck> = await apiClient.post('/quiz/check_answer', {
        question_id: questionId,
        selected_answer: selectedAnswer,
      });
      return response.data;
    },

    getDivisions: async (): Promise<string[]> => {
      const response: AxiosResponse<{ divisions: string[] }> = await apiClient.get('/quiz/divisions');
      return response.data.divisions;
    },
  },

  // Auth endpoints
  auth: {
    register: async (email: string, password: string): Promise<User> => {
      const response: AxiosResponse<User> = await apiClient.post('/auth/register', {
        email,
        password,
      });
      return response.data;
    },

    login: async (email: string, password: string): Promise<string> => {
      // Using FormData because the endpoint expects form data
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response: AxiosResponse<LoginResponse> = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Store token in localStorage
      const { access_token } = response.data;
      localStorage.setItem('auth_token', access_token);
      
      return access_token;
    },

    logout: (): void => {
      localStorage.removeItem('auth_token');
    },

    isAuthenticated: (): boolean => {
      return !!localStorage.getItem('auth_token');
    },
  },

  // User endpoints
  users: {
    getProfile: async (): Promise<User> => {
      const response: AxiosResponse<User> = await apiClient.get('/users/me');
      return response.data;
    },

    updateProfile: async (userData: UserUpdateData): Promise<User> => {
      const response: AxiosResponse<User> = await apiClient.put('/users/me', userData);
      return response.data;
    },

    getLearningSummary: async (): Promise<LearningSummary> => {
      const response: AxiosResponse<LearningSummary> = await apiClient.get('/users/me/learning-summary');
      return response.data;
    },

    getLearningGoals: async (): Promise<LearningGoal[]> => {
      const response: AxiosResponse<{ goals: LearningGoal[] }> = await apiClient.get('/users/learning-goals');
      return response.data.goals;
    },
  },

  // Payment endpoints
  payment: {
    createCheckoutSession: async (): Promise<string> => {
      const response: AxiosResponse<{ checkoutUrl: string }> = await apiClient.post(
        '/payment/create-checkout-session'
      );
      return response.data.checkoutUrl;
    },
  },
};