import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import Cookies from 'js-cookie';
import { User } from '../types';
import { authAPI } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      console.log('🔍 AuthContext: Starting authentication check...');
      const token = Cookies.get('adminToken');
      console.log('🔍 AuthContext: Token found:', !!token);
      
      if (token) {
        try {
          console.log('🔍 AuthContext: Validating token with profile call...');
          const response = await authAPI.getProfile();
          console.log('🔍 AuthContext: Profile response:', response);
          setUser(response.admin);
          console.log('✅ AuthContext: User authenticated:', response.admin);
        } catch (err) {
          console.error('❌ AuthContext: Token validation failed:', err);
          // Token invalid, clear it
          Cookies.remove('adminToken');
          console.log('🔍 AuthContext: Invalid token cleared');
        }
      } else {
        console.log('🔍 AuthContext: No token found, user not authenticated');
      }
      setIsLoading(false);
      console.log('🔍 AuthContext: Authentication check completed');
    };

    checkAuth();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authAPI.login(username, password);
      
      // Store token
      Cookies.set('adminToken', response.token, { expires: 1 });
      
      // Set user from response
      setUser(response.admin);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      // Ignore logout errors
    }
    setUser(null);
    Cookies.remove('adminToken');
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      error
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
