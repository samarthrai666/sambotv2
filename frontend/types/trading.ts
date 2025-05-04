// types/trading.ts

/**
 * Options Trading preferences
 */
export interface OptionsPreferences {
  enabled: boolean;
  indexes: ('NIFTY' | 'BANKNIFTY')[];
  modes: ('scalp' | 'swing' | 'longterm')[];
  auto_execute: boolean;
}

/**
 * Intraday Equity trading preferences
 */
export interface IntradayEquityPreferences {
  enabled: boolean;
  modes: ('opening_range' | 'trend_following' | 'mean_reversion')[];
  max_stocks: number;
  timeframes: ('1m' | '5m' | '15m' | '1h')[];
  risk_per_trade: '0.5' | '1.0' | '1.5' | '2.0';
  sectors: ('IT' | 'Auto' | 'Pharma' | 'FMCG' | 'Banking' | 'Infra' | 'Energy')[];
  stock_universe: ('nifty50' | 'fno' | 'midcap' | 'penny' | 'custom')[];
  smart_filter: boolean;
}

/**
 * Intraday trading preferences (container for all intraday trading types)
 */
export interface IntradayPreferences {
  enabled: boolean;
  equity: IntradayEquityPreferences;
}

/**
 * Equity Swing trading preferences
 */
export interface EquitySwingPreferences {
  enabled: boolean;
  modes: ('momentum' | 'breakout' | 'reversal')[];
  max_stocks: number;
  sectors: ('IT' | 'Banking' | 'Auto' | 'Pharma' | 'FMCG')[];
  scan_frequency: 'daily' | 'weekly' | 'monthly';
  market_caps: ('largecap' | 'midcap' | 'smallcap')[];
}

/**
 * Equity trading preferences (container for all equity trading types)
 */
export interface EquityPreferences {
  enabled: boolean;
  swing: EquitySwingPreferences;
}

/**
 * Combined user's trading preferences
 */
export interface TradingPreferences {
  // Trading type specific preferences
  options: OptionsPreferences;
  intraday: IntradayPreferences;
  equity: EquityPreferences;
  
  // Legacy/global settings
  auto_execute?: boolean;
  log_enabled?: boolean;
}

/**
 * Response format for signal-related API calls
 */
export interface SignalResponse {
  executed_signals: Signal[];
  non_executed_signals: Signal[];
}

/**
 * Market data for indices
 */
export interface MarketData {
  nifty: {
    price: number;
    change: number;
    changePercent: number;
  };
  banknifty: {
    price: number;
    change: number;
    changePercent: number;
  };
  marketStatus: string;
  marketOpenTime: string;
  marketCloseTime: string;
  serverTime: string;
}

/**
 * Base trading signal interface
 */
export interface Signal {
  id: string;
  symbol: string;
  instrumentType: string;  // "Option", "Equity", etc.
  action: string;          // "BUY", "SELL", etc.
  price: number;
  target_price: number;
  stop_loss: number;
  quantity: number;
  potential_return: number;
  risk_reward_ratio: number;
  timeframe: string;
  confidence_score: number;
  indicators: string[];
  patterns: string[];
  strategy: string;        // "scalp", "swing", "longterm", "intraday", etc.
  aiAnalysis?: string;
  notes?: string;
  timestamp: string;
  executed: boolean;
  expiryDate?: string;
}

/**
 * Options trading signal
 */
export interface OptionsSignal extends Signal {
  strike: number;
  optionType: string;  // "CE" or "PE"
}

/**
 * Equity trading signal
 */
export interface EquitySignal extends Signal {
  holdingPeriod: string;
  sector?: string;
  marketCap?: string;
  fundamentalRating?: string;
}

/**
 * Intraday trading signal
 */
export interface IntradaySignal extends Signal {
  entryTime: string;
  exitBeforeTime?: string;
}

/**
 * Signal execution request
 */
export interface ExecuteSignalRequest {
  signal_id: string;
  quantity: number;
  price: number;
  user_id?: string;
}

/**
 * Signal execution response
 */
export interface ExecuteSignalResponse {
  status: string;
  message: string;
  order_id: string;
  execution_time: string;
  execution_price: number;
  quantity: number;
}