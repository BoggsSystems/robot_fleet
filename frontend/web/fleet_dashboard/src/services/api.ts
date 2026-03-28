import axios from 'axios';
import Cookies from 'js-cookie';
import { LoginCredentials, AuthResponse, TokenResponse } from '../types/auth';

const API_BASE_URL = process.env.REACT_APP_AUTH_URL || 'https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = Cookies.get('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refreshToken,
          });

          const { tokens } = response.data as TokenResponse;
          Cookies.set('accessToken', tokens.accessToken, { expires: 1/24 }); // 1 hour
          Cookies.set('refreshToken', tokens.refreshToken, { expires: 7 }); // 7 days

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${tokens.accessToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        Cookies.remove('accessToken');
        Cookies.remove('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    console.log('🔍 DEBUG: Auth service login called with:', credentials);
    console.log('🔍 DEBUG: API base URL:', API_BASE_URL);
    try {
      const response = await api.post('/api/auth/login', credentials);
      console.log('🔍 DEBUG: Login response:', response.data);
      return response.data;
    } catch (error: any) {
      console.log('🔍 DEBUG: Login error:', error);
      console.log('🔍 DEBUG: Login error response:', error.response?.data);
      throw error;
    }
  },

  async logout(refreshToken: string): Promise<void> {
    await api.post('/api/auth/logout', { refreshToken });
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
      refreshToken,
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  async setupAuth() {
    const response = await api.post('/api/auth/setup');
    return response.data;
  },

  // Magic Link Methods
  async validateMagicToken(token: string) {
    const response = await axios.get(`${API_BASE_URL}/api/admin/validate-magic-token?token=${token}`);
    return response.data;
  },

  async setPassword(token: string, password: string) {
    const response = await axios.post(`${API_BASE_URL}/api/admin/set-password`, {
      token,
      password
    });
    return response.data;
  },

  async requestPasswordReset(email: string) {
    const response = await axios.post(`${API_BASE_URL}/api/request-password-reset`, {
      email
    });
    return response.data;
  },

  async validateResetToken(token: string) {
    const response = await axios.get(`${API_BASE_URL}/api/reset-password?token=${token}`);
    return response.data;
  },

  async resetPassword(token: string, password: string) {
    const response = await axios.post(`${API_BASE_URL}/api/set-password`, {
      token,
      password
    });
    return response.data;
  },
};

export default api;
