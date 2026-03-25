import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8004';
const AUTH_BASE_URL = process.env.REACT_APP_AUTH_URL || 'http://localhost:3001';

// Create axios instance for admin API
const adminApi: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Create axios instance for auth API
const authApi: AxiosInstance = axios.create({
  baseURL: AUTH_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor to add auth token
const addAuthToken = (config: AxiosRequestConfig): AxiosRequestConfig => {
  const token = Cookies.get('adminToken');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

adminApi.interceptors.request.use(addAuthToken);
authApi.interceptors.request.use(addAuthToken);

// Response interceptor for error handling
const handleError = (error: any) => {
  if (error.response?.status === 401) {
    // Token expired or invalid
    Cookies.remove('adminToken');
    window.location.href = '/login';
  }
  return Promise.reject(error);
};

adminApi.interceptors.response.use((response) => response, handleError);
authApi.interceptors.response.use((response) => response, handleError);

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await authApi.post('/auth/admin/login', { username, password });
    return response.data;
  },
  
  getProfile: async () => {
    const response = await authApi.get('/auth/admin/profile');
    return response.data;
  },
  
  logout: async () => {
    const response = await authApi.post('/auth/admin/logout');
    return response.data;
  },
  
  // Admin user management (superadmin only)
  getUsers: async () => {
    const response = await authApi.get('/auth/admin/users');
    return response.data;
  },
  
  createUser: async (userData: any) => {
    const response = await authApi.post('/auth/admin/users', userData);
    return response.data;
  },
};

// Client API
export const clientAPI = {
  getClients: async (filters?: { status?: string; plan?: string }) => {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.plan) params.append('plan', filters.plan);
    
    const response = await adminApi.get(`/api/admin/clients?${params.toString()}`);
    return response.data;
  },
  
  getClient: async (id: string) => {
    const response = await adminApi.get(`/api/admin/clients/${id}`);
    return response.data;
  },
  
  createClient: async (clientData: any) => {
    const response = await adminApi.post('/api/admin/clients', clientData);
    return response.data;
  },
  
  updateClient: async (id: string, clientData: any) => {
    const response = await adminApi.put(`/api/admin/clients/${id}`, clientData);
    return response.data;
  },
  
  deleteClient: async (id: string) => {
    const response = await adminApi.delete(`/api/admin/clients/${id}`);
    return response.data;
  },
  
  getClientFleet: async (id: string) => {
    const response = await adminApi.get(`/api/admin/clients/${id}/fleet`);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async () => {
    const response = await adminApi.get('/api/admin/dashboard/stats');
    return response.data;
  },
};

// System Health API
export const systemAPI = {
  getHealth: async () => {
    const response = await adminApi.get('/api/admin/health');
    return response.data;
  },
  
  getAlerts: async (filters?: { acknowledged?: boolean; severity?: string }) => {
    const params = new URLSearchParams();
    if (filters?.acknowledged !== undefined) params.append('acknowledged', String(filters.acknowledged));
    if (filters?.severity) params.append('severity', filters.severity);
    
    const response = await adminApi.get(`/api/admin/alerts?${params.toString()}`);
    return response.data;
  },
  
  acknowledgeAlert: async (alertId: string) => {
    const response = await adminApi.post(`/api/admin/alerts/${alertId}/acknowledge`);
    return response.data;
  },
};

export { adminApi, authApi };
