// app/services/api.ts
import axios from 'axios';
import { SignalResponse, MarketData, TradingPreferences } from '../../types/trading';

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


/**
 * Execute a trading signal
 */
export const executeSignal = async (signalId: string, quantity?: number, price?: number) => {
  try {
    const payload = {
      signal_id: signalId,
      quantity: quantity || 1,
      price: price || 0,
      user_id: localStorage.getItem('userId') || undefined
    };
    
    const response = await apiClient.post(`/signal/execute/${signalId}`, payload);
    return response.data;
  } catch (error) {
    console.error('Error executing signal:', error);
    throw error;
  }
};

/**
 * Fetch current market data
 */
export const fetchMarketData = async (): Promise<MarketData> => {
  try {
    const response = await apiClient.get('/market/data');
    return response.data;
  } catch (error) {
    console.error('❌ Error fetching market data:', error);
    throw new Error('Failed to fetch market data. Please try again later.');
  }
};

/**
 * Fetch options trading signals
 */
export const fetchOptionsSignals = async () => {
  try {
    // Get user preferences
    const prefs = getTradingPreferences();
    
    // Build query params
    const params = new URLSearchParams();
    if (prefs.options?.enabled) {
      if (prefs.options.indexes.includes('NIFTY')) {
        params.append('nifty', prefs.options.modes.join(','));
      }
      if (prefs.options.indexes.includes('BANKNIFTY')) {
        params.append('banknifty', prefs.options.modes.join(','));
      }
    }
    
    console.log('Options query params:', params.toString());
    
    // Make API request
    const response = await apiClient.get(`/signals/options?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching options signals:', error);
    throw error;
  }
};

/**
 * Fetch intraday trading signals
 */
export const fetchIntradaySignals = async () => {
  try {
    // Get user preferences
    const prefs = getTradingPreferences();
    
    // Only fetch if intraday is enabled
    if (!prefs.intraday?.enabled) {
      return [];
    }
    
    // Make API request
    const response = await apiClient.get('/signals/intraday');
    return response.data;
  } catch (error) {
    console.error('Error fetching intraday signals:', error);
    throw error;
  }
};

/**
 * Fetch equity trading signals
 */

export const refreshSignals = async () => {
  try {
    // Get user preferences
    const prefs = getTradingPreferences();
    // Only fetch if equity is enabled
    if (!prefs.equity?.enabled) {
      return [];
    }
    // Build query params
    const params = new URLSearchParams();
    // Add sectors if available
    if (prefs.equity.swing?.sectors && prefs.equity.swing.sectors.length > 0) {
      params.append('sectors', prefs.equity.swing.sectors.join(','));
    }
    // Add market caps if available
    if (prefs.equity.swing?.market_caps && prefs.equity.swing.market_caps.length > 0) {
      params.append('market_caps', prefs.equity.swing.market_caps.join(','));
    }
    // Add max stocks if available
    if (prefs.equity.swing?.max_stocks) {
      params.append('max_stocks', prefs.equity.swing.max_stocks.toString());
    }
    // Make API request with filter params
    const response = await apiClient.get(`/signals/equity?${params.toString()}`);
    return {
      executed_signals: [],
      non_executed_signals: response.data || []
    };
  } catch (error) {
    throw error;
  }
};


/**
 * Get user trading preferences from localStorage
 */
export const getTradingPreferences = (): TradingPreferences => {
  try {
    const preferencesStr = localStorage.getItem('tradingPreferences');
   
    const storedPrefs = JSON.parse(preferencesStr);
    
    return storedPrefs;
  } catch (error) {
    console.error('Error retrieving trading preferences:', error);
  }
};