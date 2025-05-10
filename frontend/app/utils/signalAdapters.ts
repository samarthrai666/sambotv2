// app/utils/signalAdapters.ts
import { Signal } from '../../types/trading';

/**
 * Converts API equity signals to the format expected by SwingEquitySignals component
 */
export const convertToSwingEquityFormat = (signals: any[]) => {
  if (!signals || !Array.isArray(signals)) return [];
  
  return signals.map(signal => {
    // Extract symbol from potentially complex format
    const symbolRaw = signal.symbol || '';
    const symbol = typeof symbolRaw === 'string' && symbolRaw.includes(':') 
      ? symbolRaw.split(':')[1].split('-')[1] // Extract from format NSE:EQ-SYMBOL
      : symbolRaw;
    
    // Extract/map signal action/type
    const signalType = signal.signal || signal.action || 'UNKNOWN';
    
    // Map price properties
    const entry = signal.entry || signal.entry_price || signal.price || 0;
    const target = signal.target || signal.target_price || 0;
    const stopLoss = signal.stop_loss || 0;
    
    // Calculate risk-reward if not present
    const rrr = signal.rrr || signal.risk_reward_ratio || signal.risk_reward || 
      (stopLoss !== entry ? Math.abs((target - entry) / (entry - stopLoss)) : 0);
    
    // Handle pattern detection
    const patternsDetected = 
      (signal.pattern_analysis && signal.pattern_analysis.patterns_detected) || 
      (signal.patterns ? [].concat(signal.patterns) : []) || 
      (signal.setup_type ? [signal.setup_type] : []);

    
    // Get appropriate confidence value
    let confidence = signal.confidence || signal.confidence_score || 0;
    if (confidence > 0 && confidence <= 1) {
      // Convert decimal confidence to percentage
      confidence = confidence;
    } else if (confidence > 1) {
      // Already a percentage, normalize to decimal
      confidence = confidence / 100;
    }
    
    // Construct indicator snapshot
    const indicatorSnapshot = {
      rsi: signal.indicator_snapshot?.rsi || signal.indicators?.rsi || 'neutral',
      rsi_value: signal.indicator_snapshot?.rsi_value || signal.indicators?.rsi_value || 50,
      macd: signal.indicator_snapshot?.macd || signal.indicators?.macd || 'neutral',
      sma_50_200: signal.indicator_snapshot?.sma_50_200 || signal.indicators?.sma_50_200 || 'neutral',
      bollinger: signal.indicator_snapshot?.bollinger || signal.indicators?.bollinger || 'neutral',
      volume_trend: signal.indicator_snapshot?.volume_trend || signal.indicators?.volume_trend || 'normal'
    };
    
    // Get analysis text
    const aiReasoning = 
      (signal.ai_opinion && signal.ai_opinion.reasoning) || 
      signal.analysis || 
      signal.reasoning || 
      `${signalType} signal for ${symbol} with risk-reward ratio of ${rrr.toFixed(2)}`;
    
    return {
      // Basic identification
      id: signal.id || `equity-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
      symbol: symbol,
      company: signal.company || '',
      sector: signal.sector || 'Equity',
      market_cap: signal.market_cap || '',
      
      // Signal type and prices
      signal: signalType,
      entry: entry,
      target: target,
      stop_loss: stopLoss,
      rrr: rrr,
      
      // Trend and timeframe
      trend: signal.trend || 'neutral',
      timeframe: signal.timeframe || 'daily',
      
      // Confidence
      confidence: confidence,
      
      // Technical indicators
      indicator_snapshot: indicatorSnapshot,
      
      // Pattern analysis
      pattern_analysis: {
        patterns_detected: patternsDetected,
        strength: signal.pattern_analysis?.strength || 'moderate'
      },
      
      // AI opinion
      ai_opinion: {
        sentiment: signal.ai_opinion?.sentiment || (signalType === 'BUY' ? 'bullish' : 'bearish'),
        confidence: confidence,
        reasoning: aiReasoning
      },
      
      // Timing info
      expected_holding_period: signal.expected_holding_period || signal.holding_period || '10-15 days',
      expected_exit_date: signal.expected_exit_date || '',
      trade_time: signal.trade_time || signal.timestamp || new Date().toISOString(),
      
      // Status
      executed: signal.executed || false
    };
  });
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
  if ((signal.action || signal.signal) && 
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