import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';
import { toast } from 'react-toastify';
import { User, AuthState, AuthContextType, LoginCredentials } from '../types/auth';
import { authService } from '../services/api';

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'REFRESH_TOKEN_START' }
  | { type: 'REFRESH_TOKEN_SUCCESS'; payload: User }
  | { type: 'REFRESH_TOKEN_FAILURE'; payload: string };

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true, error: null };
    case 'LOGIN_SUCCESS':
      return { 
        ...state, 
        user: action.payload, 
        isAuthenticated: true, 
        isLoading: false, 
        error: null 
      };
    case 'LOGIN_FAILURE':
      return { 
        ...state, 
        user: null, 
        isAuthenticated: false, 
        isLoading: false, 
        error: action.payload 
      };
    case 'LOGOUT':
      return { 
        ...state, 
        user: null, 
        isAuthenticated: false, 
        isLoading: false, 
        error: null 
      };
    case 'REFRESH_TOKEN_START':
      return { ...state, isLoading: true };
    case 'REFRESH_TOKEN_SUCCESS':
      return { 
        ...state, 
        user: action.payload, 
        isLoading: false 
      };
    case 'REFRESH_TOKEN_FAILURE':
      return { 
        ...state, 
        isLoading: false,
        error: action.payload
      };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const validateToken = useCallback(async (token: string) => {
    try {
      const data = await authService.getCurrentUser();
      if (data.success) {
        dispatch({ type: 'LOGIN_SUCCESS', payload: data.user });
      } else {
        dispatch({ type: 'LOGOUT' });
        Cookies.remove('accessToken');
        Cookies.remove('refreshToken');
      }
    } catch (error) {
      dispatch({ type: 'LOGOUT' });
      Cookies.remove('accessToken');
      Cookies.remove('refreshToken');
    }
  }, []);

  useEffect(() => {
    const accessToken = Cookies.get('accessToken');
    if (accessToken) {
      validateToken(accessToken);
    }
  }, [validateToken]);

  const login = useCallback(async (username: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      const data = await authService.login({ username, password });
      
      // Store tokens
      Cookies.set('accessToken', data.tokens.accessToken, { expires: 1/24 }); // 1 hour
      Cookies.set('refreshToken', data.tokens.refreshToken, { expires: 7 }); // 7 days

      dispatch({ type: 'LOGIN_SUCCESS', payload: data.user });
      toast.success('Login successful!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      dispatch({ type: 'LOGIN_FAILURE', payload: errorMessage });
      toast.error(errorMessage);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      const refreshToken = Cookies.get('refreshToken');
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: 'LOGOUT' });
      Cookies.remove('accessToken');
      Cookies.remove('refreshToken');
      toast.success('Logged out successfully');
    }
  }, []);

  const refreshToken = useCallback(async () => {
    const refreshToken = Cookies.get('refreshToken');
    if (!refreshToken) {
      dispatch({ type: 'LOGOUT' });
      return;
    }

    dispatch({ type: 'REFRESH_TOKEN_START' });

    try {
      const data = await authService.refreshToken(refreshToken);
      
      // Update tokens
      Cookies.set('accessToken', data.tokens.accessToken, { expires: 1/24 });
      Cookies.set('refreshToken', data.tokens.refreshToken, { expires: 7 });

      // Get user info with new token
      await validateToken(data.tokens.accessToken);
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Session expired';
      dispatch({ type: 'REFRESH_TOKEN_FAILURE', payload: errorMessage });
      dispatch({ type: 'LOGOUT' });
      Cookies.remove('accessToken');
      Cookies.remove('refreshToken');
      toast.error('Session expired. Please login again.');
    }
  }, [validateToken]);

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
