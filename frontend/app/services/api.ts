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
 * Refresh trading signals based on user preferences
 * This function is used by the signals page to fetch updated signals
 */
export const refreshSignals = async (): Promise<SignalResponse> => {
  try {
    // Get user preferences from localStorage
    const prefs = getTradingPreferences();
    
    // Build query params based on the new structure
    const params = new URLSearchParams();
    
    // Options trading preferences
    if (prefs.options?.enabled) {
      if (prefs.options.indexes.includes('NIFTY')) {
        params.append('nifty', prefs.options.modes.join(','));
      }
      if (prefs.options.indexes.includes('BANKNIFTY')) {
        params.append('banknifty', prefs.options.modes.join(','));
      }
    }
    
    // Intraday preferences
    if (prefs.intraday?.enabled) {
      params.append('intraday', 'true');
    }
    
    // Equity preferences
    if (prefs.equity?.enabled) {
      params.append('equity_swing', 'true');
    }
    
    console.log('Query params for refreshing signals:', params.toString());
    
    // Send the request with the user's preferences as query params
    const url = `/signals/available?${params.toString()}`;
    console.log('Refresh signals URL:', url);
    
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

/**
 * Fetch all available signals based on user preferences
 */
export const fetchAvailableSignals = async (): Promise<SignalResponse> => {
  try {
    // Get user preferences from localStorage
    const prefs = getTradingPreferences();
    
    // Build query params based on the new structure
    const params = new URLSearchParams();
    
    // Options trading preferences
    if (prefs.options?.enabled) {
      if (prefs.options.indexes.includes('NIFTY')) {
        params.append('nifty', prefs.options.modes.join(','));
      }
      if (prefs.options.indexes.includes('BANKNIFTY')) {
        params.append('banknifty', prefs.options.modes.join(','));
      }
    }
    
    // Intraday preferences
    if (prefs.intraday?.enabled) {
      params.append('intraday', 'true');
    }
    
    // Equity preferences
    if (prefs.equity?.enabled) {
      params.append('equity_swing', 'true');
    }
    
    console.log('Query params:', params.toString());
    
    // Send the request with the user's preferences as query params
    const url = `/signals/available?${params.toString()}`;
    console.log('Request URL:', url);
    
    const response = await apiClient.get(url);
    
    return {
      executed_signals: [],
      non_executed_signals: response.data || []
    };
  } catch (error) {
    console.error('Error fetching available signals:', error);
    throw error;
  }
};

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
export const fetchEquitySignals = async () => {
  try {
    // Get user preferences
    const prefs = getTradingPreferences();
    
    // Only fetch if equity is enabled
    if (!prefs.equity?.enabled) {
      return [];
    }
    
    // Make API request
    const response = await apiClient.get('/signals/equity');
    return response.data;
  } catch (error) {
    console.error('Error fetching equity signals:', error);
    throw error;
  }
};

/**
 * Refresh signal analysis
 */
export const refreshSignalAnalysis = async (signals: any[]) => {
  try {
    const response = await apiClient.post('/signals/refresh-analysis', signals);
    return response.data;
  } catch (error) {
    console.error('Error refreshing signal analysis:', error);
    throw error;
  }
};

/**
 * Save user trading preferences to localStorage
 */
export const saveTradingPreferences = (preferences: TradingPreferences): boolean => {
  try {
    localStorage.setItem('tradingPreferences', JSON.stringify(preferences));
    return true;
  } catch (error) {
    console.error('Error saving trading preferences:', error);
    return false;
  }
};

/**
 * Get user trading preferences from localStorage
 */
export const getTradingPreferences = (): TradingPreferences => {
  const defaultPreferences: TradingPreferences = {
    options: {
      enabled: false,
      indexes: [],
      modes: [],
      auto_execute: false
    },
    intraday: {
      enabled: false,
      equity: {
        enabled: false,
        modes: [],
        max_stocks: 3,
        timeframes: [],
        risk_per_trade: '1.0',
        sectors: [],
        stock_universe: [],
        smart_filter: true
      }
    },
    equity: {
      enabled: false,
      swing: {
        enabled: false,
        modes: [],
        max_stocks: 5,
        sectors: [],
        scan_frequency: 'weekly',
        market_caps: []
      }
    },
    auto_execute: false,
    log_enabled: true
  };
  
  try {
    const preferencesStr = localStorage.getItem('tradingPreferences');
    if (!preferencesStr) {
      return defaultPreferences;
    }
    
    const storedPrefs = JSON.parse(preferencesStr);
    
    // Ensure all fields are present by merging with default preferences
    const mergedPreferences = {
      ...defaultPreferences,
      ...storedPrefs,
      options: {
        ...defaultPreferences.options,
        ...(storedPrefs.options || {})
      },
      intraday: {
        ...defaultPreferences.intraday,
        ...(storedPrefs.intraday || {}),
        equity: {
          ...defaultPreferences.intraday.equity,
          ...(storedPrefs.intraday?.equity || {})
        }
      },
      equity: {
        ...defaultPreferences.equity,
        ...(storedPrefs.equity || {}),
        swing: {
          ...defaultPreferences.equity.swing,
          ...(storedPrefs.equity?.swing || {})
        }
      }
    };
    
    return mergedPreferences;
  } catch (error) {
    console.error('Error retrieving trading preferences:', error);
    return defaultPreferences;
  }
};