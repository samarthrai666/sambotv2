// app/services/api.ts
import axios from 'axios';
import { SignalResponse, MarketData } from '../../types/trading';

// Get the API URL from environment variables or use a default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

export const refreshSignals = async (): Promise<SignalResponse> => {
  try {
    // Get user preferences from localStorage
    const preferencesStr = localStorage.getItem('tradingPreferences');
    console.log('Raw preferences string:', preferencesStr); // Add this
    
    let nifty = [];
    let banknifty = [];
    
    // Use stored preferences if available
    if (preferencesStr) {
      try {
        const storedPrefs = JSON.parse(preferencesStr);
        console.log('Parsed preferences:', storedPrefs); // Add this
        nifty = storedPrefs.nifty || [];
        banknifty = storedPrefs.banknifty || [];
      } catch (e) {
        console.error('Error parsing trading preferences:', e);
      }
    }
    
    console.log('Extracted preferences:', { nifty, banknifty }); // Add this
    
    // Build query params
    const params = new URLSearchParams();
    if (nifty.length > 0) {
      params.append('nifty', nifty.join(','));
    }
    if (banknifty.length > 0) {
      params.append('banknifty', banknifty.join(','));
    }
    
    console.log('Query params:', params.toString()); // Add this
    
    // Send the request with the user's preferences as query params
    const url = `/signals/available?${params.toString()}`;
    console.log('Request URL:', url); // Add this
    
    const response = await apiClient.get(url);
    
    return {
      executed_signals: [],
      non_executed_signals: response.data || []
    };
  } catch (error) {
    console.error('Error refreshing signals:', error);
    throw error;
  }
};

export const executeSignal = async (signalId: string) => {
  try {
    // You'll need to implement this endpoint in your backend
    const response = await apiClient.post(`/signal/execute/${signalId}`);
    return response.data;
  } catch (error) {
    console.error('Error executing signal:', error);
    throw error;
  }
};

export const fetchMarketData = async (): Promise<MarketData> => {
  try {
    // You'll need to implement this endpoint in your backend
    const response = await apiClient.get('/market/data');
    return response.data;
  } catch (error) {
    console.error('Error fetching market data:', error);
    
    // Fallback to mock data if the API fails
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const isMarketOpen = (hours > 9 || (hours === 9 && minutes >= 15)) && hours < 15 || (hours === 15 && minutes <= 30);
    
    return {
      nifty: {
        price: 23412.65,
        change: 142.50,
        changePercent: 0.61
      },
      banknifty: {
        price: 48723.90,
        change: -104.80,
        changePercent: -0.21
      },
      marketStatus: isMarketOpen ? 'open' : 'closed',
      marketOpenTime: '09:15:00',
      marketCloseTime: '15:30:00',
      serverTime: now.toISOString()
    };
  }
};

export const fetchAvailableSignals = async () => {
  try {
    // Get user preferences from localStorage
    const preferencesStr = localStorage.getItem('tradingPreferences');
    let nifty = [];
    let banknifty = [];
    
    // Use stored preferences if available
    if (preferencesStr) {
      try {
        const storedPrefs = JSON.parse(preferencesStr);
        nifty = storedPrefs.nifty || [];
        banknifty = storedPrefs.banknifty || [];
      } catch (e) {
        console.error('Error parsing trading preferences:', e);
      }
    }
    
    // Build query params
    const params = new URLSearchParams();
    if (nifty.length > 0) {
      params.append('nifty', nifty.join(','));
    }
    if (banknifty.length > 0) {
      params.append('banknifty', banknifty.join(','));
    }
    
    console.log('Using trading preferences:', { nifty, banknifty });
    console.log('Query params:', params.toString());
    
    // Send the request with query params
    const response = await apiClient.get(`/signals/available?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching available signals:', error);
    throw error;
  }
};

export const refreshSignalAnalysis = async (signals: Signal[]) => {
  try {
    const response = await apiClient.post('/signals/refresh-analysis', signals);
    return response.data;
  } catch (error) {
    console.error('Error refreshing signal analysis:', error);
    throw error;
  }
};