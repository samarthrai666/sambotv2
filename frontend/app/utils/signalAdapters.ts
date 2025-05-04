// frontend/app/utils/signalAdapters.ts
import { Signal } from '../../types/trading';

/**
 * Converts API equity signals to the format expected by SwingEquitySignals component
 */
export const convertToSwingEquityFormat = (signals: any[]) => {
  if (!signals || !Array.isArray(signals)) return [];
  
  return signals.map(signal => ({
    id: signal.id || `equity-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    symbol: typeof signal.symbol === 'string' && signal.symbol.includes(':') 
      ? signal.symbol.split(':')[1].split('-')[1] // Extract from format NSE:EQ-SYMBOL
      : signal.symbol,
    action: signal.action as 'BUY' | 'SELL',
    entry_price: signal.entry_price || signal.price || signal.entry || 0,
    target_price: signal.target_price || signal.target || 0,
    stop_loss: signal.stop_loss || 0,
    risk_reward: signal.risk_reward_ratio || signal.risk_reward || signal.rrr || 1.5,
    potential_gain: signal.potential_gain || signal.potential_return * 100 || 
      ((signal.target_price || signal.target || 0) - (signal.entry_price || signal.price || signal.entry || 0)) / 
      (signal.entry_price || signal.price || signal.entry || 1) * 100,
    timeframe: signal.timeframe || 'Daily',
    confidence: typeof signal.confidence === 'number' && signal.confidence <= 1 
      ? signal.confidence * 100 
      : signal.confidence_score || signal.confidence || 75,
    setup_type: signal.setup_type || signal.patterns?.[0] || 
      signal.pattern_analysis?.patterns_detected?.[0] || 'Swing Trade',
    sector: signal.sector || 'Equity',
    analysis: signal.analysis || signal.aiAnalysis || signal.notes || 
      `${signal.action} signal for ${signal.symbol} with risk-reward ratio of ${signal.risk_reward_ratio || signal.risk_reward || signal.rrr || 1.5}`,
    executed: signal.executed || false
  }));
};

/**
 * Converts API intraday signals to the format expected by IntradayEquitySignals component
 */
export const convertToIntradayFormat = (signals: any[]) => {
  if (!signals || !Array.isArray(signals)) return [];
  
  return signals.map(signal => ({
    id: signal.id || `intraday-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    symbol: typeof signal.symbol === 'string' && signal.symbol.includes(':')
      ? signal.symbol.split(':')[1].split('-')[1]
      : signal.symbol,
    action: signal.action as 'BUY' | 'SELL',
    entry_price: signal.entry_price || signal.price || signal.entry || 0,
    target_price: signal.target_price || signal.target || 0,
    stop_loss: signal.stop_loss || 0,
    risk_reward: signal.risk_reward_ratio || signal.risk_reward || signal.rrr || 1.5,
    potential_gain: signal.potential_gain || signal.potential_return * 100 || 
      ((signal.target_price || signal.target || 0) - (signal.entry_price || signal.price || signal.entry || 0)) / 
      (signal.entry_price || signal.price || signal.entry || 1) * 100,
    timeframe: signal.timeframe || '5m',
    confidence: typeof signal.confidence === 'number' && signal.confidence <= 1 
      ? signal.confidence * 100 
      : signal.confidence_score || signal.confidence || 75,
    strategy: signal.strategy || 'Trend Following',
    volume_surge: signal.volume_surge || signal.volume_analysis?.volume_surge_pct || 1.2,
    key_level: signal.key_level || 
      signal.zones?.nearest_support || 
      signal.zones?.nearest_resistance || 
      signal.entry_price || 
      signal.price || 
      0,
    trigger: signal.trigger || 
      `${signal.action} signal based on ${signal.strategy || 'technical analysis'}`,
    executed: signal.executed || false
  }));
};

/**
 * Helper function to check if a signal is an equity signal
 * This helps us filter out equity signals from the API response
 */
export const isEquitySignal = (signal: any): boolean => {
  if (!signal) return false;
  
  // Check if ID includes 'equity' or matches equity signal pattern
  if (signal.id && typeof signal.id === 'string' && 
      (signal.id.includes('equity') || signal.id.includes('swing'))) {
    return true;
  }
  
  // Check for symbol format that indicates equity
  if (signal.symbol && typeof signal.symbol === 'string' && 
      (signal.symbol.includes('EQ-') || signal.symbol.includes('NSE:'))) {
    return true;
  }
  
  // Check for essential properties that would be in an equity signal
  if (signal.action && 
      (signal.entry_price || signal.price || signal.entry) && 
      (signal.target_price || signal.target) &&
      signal.stop_loss) {
    // Must NOT be an options signal (doesn't have strike and optionType)
    return !(signal.strike && signal.optionType);
  }
  
  return false;
};

/**
 * Helper function to extract equity signals from a list of generic signals
 */
export const extractEquitySignals = (signals: any[]): any[] => {
  if (!signals || !Array.isArray(signals)) return [];
  return signals.filter(isEquitySignal);
};