// services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Submit trading preferences to get signals
export const submitTradingPreference = async (data) => {
  try {
    const response = await apiClient.post('/signals/request', data);
    return response.data;
  } catch (error) {
    console.error('API Error in submitTradingPreference:', error);
    throw error;
  }
};

// Execute a signal manually
export const executeSignal = async (signalId) => {
  try {
    const response = await apiClient.post(`/signals/execute/${signalId}`);
    return response.data;
  } catch (error) {
    console.error('API Error in executeSignal:', error);
    throw error;
  }
};

// Cancel an executed trade
export const cancelTrade = async (tradeId) => {
  try {
    const response = await apiClient.post(`/trades/cancel/${tradeId}`);
    return response.data;
  } catch (error) {
    console.error('API Error in cancelTrade:', error);
    throw error;
  }
};

// Get updated information about signals and trades
export const refreshSignals = async () => {
  try {
    const response = await apiClient.get('/signals/refresh');
    return response.data;
  } catch (error) {
    console.error('API Error in refreshSignals:', error);
    throw error;
  }
};