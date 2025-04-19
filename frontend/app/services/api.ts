// app/services/api.ts
import { SignalResponse, MarketData } from '../../types/trading';

// Mock API functions
export const executeSignal = async (signalId: string) => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    order_id: `ORD-${Math.floor(Math.random() * 1000000)}`,
    status: 'success',
    message: 'Trade executed successfully'
  };
};

export const refreshSignals = async (): Promise<SignalResponse> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Return some demo signals
  return {
    executed_signals: [
      {
        id: '2',
        symbol: 'NIFTY',
        instrumentType: 'Option',
        strike: 23400,
        optionType: 'CE',
        action: 'BUY',
        price: 250.75,
        target_price: 290.50,
        stop_loss: 220.00,
        quantity: 50,
        potential_return: 0.1584,
        risk_reward_ratio: 1.8,
        timeframe: '5min',
        confidence_score: 78,
        indicators: ['RSI Oversold', 'MACD Bullish', 'Support Test'],
        patterns: ['Bullish Engulfing', 'Double Bottom', 'Golden Cross'],
        strategy: 'scalp',
        aiAnalysis: 'Strong bullish momentum detected after a period of consolidation. Price recently broke out of a key resistance level with increased volume. Short-term technical indicators support a bullish bias.',
        notes: 'Strong support level with volume confirmation',
        timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
        executed: true,
        order_id: 'ORD-123456',
        executed_at: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: '4',
        symbol: 'NIFTY',
        instrumentType: 'Future',
        action: 'SELL',
        price: 23450.25,
        target_price: 23350.00,
        stop_loss: 23550.00,
        quantity: 25,
        potential_return: 0.0043,
        risk_reward_ratio: 2.2,
        timeframe: '15min',
        confidence_score: 76,
        indicators: ['RSI Divergence', 'MACD Crossover', 'Volume Spike'],
        patterns: ['Evening Star', 'Lower High', 'Death Cross'],
        strategy: 'swing',
        aiAnalysis: 'Detected a bearish reversal pattern near key resistance level. Price has formed a lower high with RSI divergence, suggesting weakening momentum. Swing trade opportunity with favorable risk-reward.',
        notes: 'Key resistance zone rejection',
        timestamp: new Date(Date.now() - 5400000).toISOString(), // 90 minutes ago
        executed: true,
        order_id: 'ORD-234567',
        executed_at: new Date(Date.now() - 5400000).toISOString()
      }
    ],
    non_executed_signals: [
      {
        id: '3',
        symbol: 'BANKNIFTY',
        instrumentType: 'Option',
        strike: 48700,
        optionType: 'PE',
        action: 'SELL',
        price: 320.25,
        target_price: 250.00,
        stop_loss: 380.00,
        quantity: 25,
        potential_return: 0.2194,
        risk_reward_ratio: 2.0,
        timeframe: '15min',
        confidence_score: 82,
        indicators: ['RSI Overbought', 'MACD Bearish', 'Resistance Test'],
        patterns: ['Bearish Engulfing', 'Head and Shoulders', 'Evening Star'],
        strategy: 'swing',
        aiAnalysis: 'Bank Nifty has reached an over-extended position with RSI in overbought territory. Historical data suggests a high probability of reversion to the mean from these levels. Swing trade setup with clear entry/exit levels.',
        notes: 'Strong resistance with divergence on RSI',
        timestamp: new Date().toISOString(),
        executed: false
      },
      {
        id: '5',
        symbol: 'NIFTY',
        instrumentType: 'Stock',
        action: 'BUY',
        price: 23400.50,
        target_price: 24000.00,
        stop_loss: 23000.00,
        quantity: 10,
        potential_return: 0.0256,
        risk_reward_ratio: 3.0,
        timeframe: '1day',
        confidence_score: 88,
        indicators: ['Golden Cross', '200 EMA Support', 'Trend Line Bounce'],
        patterns: ['Inverse Head & Shoulders', 'Cup and Handle', 'Ascending Triangle'],
        strategy: 'longterm',
        aiAnalysis: 'Long-term bullish trend confirmed by multiple technical indicators. Recent pullback provides an attractive entry point with favorable risk-reward for positional traders. Strong fundamental outlook supports continued upward momentum.',
        notes: 'Long-term accumulation zone with institutional buying',
        timestamp: new Date().toISOString(),
        executed: false
      }
    ]
  };
};

export const fetchMarketData = async (): Promise<MarketData> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Get current date
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  
  // Simulate market being open during normal trading hours (9:15 AM to 3:30 PM)
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
};