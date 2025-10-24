import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  getProfile: () => api.get('/auth/profile'),
  setupCredentials: (email, password) => api.post('/auth/setup-credentials', { email, password }),
  getCredentials: () => api.get('/auth/credentials'),
  testConnection: () => api.post('/auth/test-connection'),
};

// Schedules API
export const schedulesAPI = {
  getSchedules: () => api.get('/schedules/'),
  createSchedule: (scheduleData) => api.post('/schedules/', scheduleData),
  getSchedule: (id) => api.get(`/schedules/${id}`),
  updateSchedule: (id, scheduleData) => api.put(`/schedules/${id}`, scheduleData),
  deleteSchedule: (id) => api.delete(`/schedules/${id}`),
  toggleSchedule: (id) => api.post(`/schedules/${id}/toggle`),
};

// Mattress API
export const mattressAPI = {
  getStatus: () => api.get('/mattress/status'),
  adjustFirmness: (adjustmentData) => api.post('/mattress/adjust', adjustmentData),
  testConnection: () => api.post('/mattress/test'),
};

// Logs API
export const logsAPI = {
  getLogs: (params = {}) => api.get('/logs/', { params }),
  getLogStats: (days = 30) => api.get('/logs/stats', { params: { days } }),
  getLog: (id) => api.get(`/logs/${id}`),
  clearLogs: (days = 90) => api.post('/logs/clear', { days }),
};

export default api;
