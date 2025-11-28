import axios from 'axios';
import { useAuth } from './auth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

console.log('API BASE URL:', api.defaults.baseURL);

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    // Only add token if it exists and is not null/undefined
    if (token && token !== 'null' && token !== 'undefined') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API functions
export const login = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
  }
  return response.data;
};

export const getDashboardStats = async (token) => {
  const response = await api.get('/dashboard/stats');
  return response.data;
};

export const uploadWeatherCSV = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload/weather/', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadProductionCSV = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload/production/', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const uploadImages = async (files, panelId, token) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('images', file);
  });
  if (panelId) {
    formData.append('panel_id', panelId);
  }
  const response = await api.post('/upload/images/', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const trainModel = async (modelType, token) => {
  const response = await api.post(
    '/training/',
    { model_type: modelType },
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return response.data;
};

export const getTrainingStatus = async (token) => {
  const response = await api.get('/training/status/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const getDailyPredictions = async (days, token) => {
  const response = await api.get(`/predictions/daily/?days=${days}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const getHourlyPredictions = async (hours, token) => {
  const response = await api.get(`/predictions/hourly/?hours=${hours}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const getHealthStatus = async (token) => {
  const response = await api.get('/health/status/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const fetchSolarForecast = async ({ lat, lon }, token) => {
  const response = await api.get(`/forecast/solar?lat=${lat}&lon=${lon}`);
  return response.data;
};

export const searchLocation = async (query, token) => {
  const response = await api.get(`/geocode/search?q=${encodeURIComponent(query)}`); 
  return response.data?.results || [];
};

export default api;



