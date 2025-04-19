// app/types/trading.ts

export interface Signal {
    id: string;
    symbol: string;
    instrumentType?: string; // Stock, Option, Future
    strike?: number; // For options
    optionType?: 'CE' | 'PE'; // Call or Put
    action: 'BUY' | 'SELL';
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
    strategy: 'scalp' | 'swing' | 'longterm';
    aiAnalysis?: string;
    notes?: string;
    timestamp: string;
    executed: boolean;
    order_id?: string;
    executed_at?: string;
    expiryDate?: string;
    formattedTitle?: string; // 👈 Add this!

  }
  
  export interface SignalResponse {
    executed_signals: Signal[];
    non_executed_signals: Signal[];
  }
  
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
    marketStatus: 'open' | 'closed';
    marketOpenTime: string;
    marketCloseTime: string;
    serverTime: string;
  }
  
  export interface LogEntry {
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    message: string;
    timestamp: string;
  }