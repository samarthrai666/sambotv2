'use client';

import { useState } from 'react';

// Updated interface to match the adapter format
interface SwingEquitySignal {
  id: string;
  symbol: string;
  signal?: 'BUY' | 'SELL';
  action?: 'BUY' | 'SELL';
  entry?: number;
  entry_price?: number;
  target?: number;
  target_price?: number;
  stop_loss?: number;
  rrr?: number;
  risk_reward?: number;
  trend?: string;
  timeframe?: string;
  confidence?: number;
  company?: string;
  sector?: string;
  market_cap?: string;
  indicator_snapshot?: {
    rsi?: string;
    rsi_value?: number;
    macd?: string;
    sma_50_200?: string;
    bollinger?: string;
    volume_trend?: string;
  };
  pattern_analysis?: {
    patterns_detected?: string[];
    strength?: string;
  };
  ai_opinion?: {
    sentiment?: string;
    confidence?: number;
    reasoning?: string;
  };
  expected_holding_period?: string;
  expected_exit_date?: string;
  trade_time?: string;
  potential_gain?: number;
  setup_type?: string;
  analysis?: string;
  executed?: boolean;
}

interface SwingEquitySignalsProps {
  signals: SwingEquitySignal[];
  onExecute: (id: string) => void;
  isLoading?: boolean;
}

export default function SwingEquitySignals({ 
  signals, 
  onExecute,
  isLoading = false
}: SwingEquitySignalsProps) {
  const [expandedDetails, setExpandedDetails] = useState<{[key: string]: boolean}>({});
  
  // Helper functions for safely accessing data
  const getSignalAction = (signal: SwingEquitySignal): string => {
    return signal.signal || signal.action || 'UNKNOWN';
  };
  
  const getEntryPrice = (signal: SwingEquitySignal): number => {
    return signal.entry || signal.entry_price || 0;
  };
  
  const getTargetPrice = (signal: SwingEquitySignal): number => {
    return signal.target || signal.target_price || 0;
  };
  
  const getRiskReward = (signal: SwingEquitySignal): number => {
    return signal.rrr || signal.risk_reward || 0;
  };
  
  // Calculate potential gain percentage
  const getPotentialGain = (signal: SwingEquitySignal): string => {
    if (signal.potential_gain) {
      return signal.potential_gain > 0 ? `+${signal.potential_gain.toFixed(2)}%` : `${signal.potential_gain.toFixed(2)}%`;
    }
    
    const entry = getEntryPrice(signal);
    const target = getTargetPrice(signal);
    
    if (entry && target) {
      const gainPct = ((target - entry) / entry) * 100;
      return gainPct > 0 ? `+${gainPct.toFixed(2)}%` : `${gainPct.toFixed(2)}%`;
    }
    
    return '+0.00%';
  };

  // Format date
  const formatDate = (dateStr?: string): string => {
    if (!dateStr) return '-';
    
    if (dateStr.includes('T')) {
      return new Date(dateStr).toLocaleString();
    }
    return dateStr;
  };
  
  // Get analysis text
  const getAnalysisText = (signal: SwingEquitySignal): string => {
    if (signal.ai_opinion && signal.ai_opinion.reasoning) {
      return signal.ai_opinion.reasoning;
    }
    if (signal.analysis) {
      return signal.analysis;
    }
    return `${getSignalAction(signal)} signal for ${signal.symbol} with risk-reward ratio of ${getRiskReward(signal).toFixed(2)}`;
  };
  
  // Get patterns
  const getPatterns = (signal: SwingEquitySignal): string[] => {
    if (signal.pattern_analysis && signal.pattern_analysis.patterns_detected) {
      return signal.pattern_analysis.patterns_detected;
    }
    if (signal.setup_type) {
      return [signal.setup_type];
    }
    return [];
  };
  
  // Toggle details expansion
  const toggleDetails = (id: string) => {
    setExpandedDetails(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };
  
  // Get confidence level badge
  const getConfidenceBadge = (confidence: number): JSX.Element => {
    const confidenceValue = typeof confidence === 'number' && confidence <= 1 
      ? confidence * 100 
      : confidence;
    
    let color = "bg-gray-200 text-gray-700";
    if (confidenceValue >= 80) color = "bg-green-600 text-white";
    else if (confidenceValue >= 70) color = "bg-green-500 text-white";
    else if (confidenceValue >= 60) color = "bg-green-400 text-white";
    else if (confidenceValue >= 50) color = "bg-yellow-400 text-black";
    else color = "bg-orange-400 text-white";
    
    return (
      <div className={`px-2 py-1 rounded-lg text-xs font-medium ${color}`}>
        {confidenceValue.toFixed(0)}% confidence
      </div>
    );
  };
  
  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      {isLoading ? (
        <div className="flex justify-center py-6">
          <div className="animate-pulse space-y-3 w-full">
            <div className="h-4 bg-green-100 rounded w-3/4"></div>
            <div className="h-4 bg-green-100 rounded"></div>
            <div className="h-4 bg-green-100 rounded w-5/6"></div>
          </div>
        </div>
      ) : signals.length > 0 ? (
        <div className="space-y-4 p-4">
          {signals.map((signal) => (
            <div 
              key={signal.id}
              className={`border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 ${
                getSignalAction(signal) === 'BUY' ? 'border-l-4 border-l-green-500' : 'border-l-4 border-l-red-500'
              }`}
            >
              {/* Compact Signal Header */}
              <div className="px-3 py-2 flex justify-between items-center bg-white">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-lg">{signal.symbol}</span>
                  
                  <div className={`font-bold text-xs px-2 py-1 rounded-lg ${
                    getSignalAction(signal) === 'BUY' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {getSignalAction(signal)}
                  </div>
                  
                  {signal.confidence !== undefined && (
                    <div className="ml-2">
                      {getConfidenceBadge(signal.confidence)}
                    </div>
                  )}
                </div>
                
                {!signal.executed ? (
                  <button
                    onClick={() => onExecute(signal.id)}
                    className={`text-xs px-3 py-1 font-medium rounded-lg ${
                      getSignalAction(signal) === 'BUY'
                        ? 'bg-green-600 text-white hover:bg-green-700'
                        : 'bg-red-600 text-white hover:bg-red-700'
                    }`}
                  >
                    Execute
                  </button>
                ) : (
                  <span className="text-xs px-3 py-1 bg-blue-100 text-blue-800 font-medium rounded-lg">
                    Active
                  </span>
                )}
              </div>
              
              {/* Signal Metadata */}
              <div className="bg-gray-100 px-3 py-1 flex flex-wrap gap-x-4 gap-y-1 text-xs">
                {signal.sector && (
                  <span className="text-gray-700">
                    <span className="font-medium">Sector:</span> {signal.sector}
                  </span>
                )}
                {signal.market_cap && (
                  <span className="text-gray-700">
                    <span className="font-medium">Cap:</span> {signal.market_cap}
                  </span>
                )}
                {signal.trade_time && (
                  <span className="text-gray-700">
                    <span className="font-medium">Signal time:</span> {formatDate(signal.trade_time)}
                  </span>
                )}
              </div>
              
              {/* Price Cards - Creative Design */}
              <div className="p-3 bg-white">
                <div className="grid grid-cols-3 gap-2">
                  {/* Entry Card - with arrow symbol */}
                  <div className="rounded-lg border border-gray-200 overflow-hidden">
                    <div className="bg-gray-50 py-1 px-2">
                      <div className="text-xs text-gray-500">Entry</div>
                    </div>
                    <div className="p-2 flex justify-between items-center">
                      <div className="text-lg font-bold text-gray-800">{getEntryPrice(signal).toFixed(2)}</div>
                      <div className={`w-6 h-6 flex items-center justify-center rounded-full ${
                        getSignalAction(signal) === 'BUY' ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        {getSignalAction(signal) === 'BUY' ? (
                          <span className="text-green-600">↵</span>
                        ) : (
                          <span className="text-red-600">↵</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Target Card - with upward arrow for BUY, downward for SELL */}
                  <div className="rounded-lg border border-gray-200 overflow-hidden">
                    <div className="bg-gray-50 py-1 px-2">
                      <div className="text-xs text-gray-500">Target</div>
                    </div>
                    <div className="p-2">
                      <div className="flex justify-between items-center">
                        <div className="text-lg font-bold text-green-600">{getTargetPrice(signal).toFixed(2)}</div>
                        <div className={`w-6 h-6 flex items-center justify-center rounded-full ${
                          getSignalAction(signal) === 'BUY' ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {getSignalAction(signal) === 'BUY' ? (
                            <span className="text-green-600">↑</span>
                          ) : (
                            <span className="text-red-600">↓</span>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-green-600">{getPotentialGain(signal)}</div>
                    </div>
                  </div>
                  
                  {/* Stop Loss Card - with barrier symbol */}
                  <div className="rounded-lg border border-gray-200 overflow-hidden">
                    <div className="bg-gray-50 py-1 px-2">
                      <div className="text-xs text-gray-500">Stop Loss</div>
                    </div>
                    <div className="p-2 flex justify-between items-center">
                      <div className="text-lg font-bold text-red-600">{signal.stop_loss ? signal.stop_loss.toFixed(2) : '0.00'}</div>
                      <div className="w-6 h-6 flex items-center justify-center rounded-full bg-red-100">
                        <span className="text-red-600">⊘</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Trade Details Pills */}
                <div className="flex flex-wrap gap-2 mt-3">
                  <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
                    <span className="font-medium">R:R:</span> {getRiskReward(signal).toFixed(2)}
                  </div>
                  
                  {signal.trend && (
                    <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
                      <span className="font-medium">Trend:</span> {signal.trend}
                    </div>
                  )}
                  
                  {signal.expected_holding_period && (
                    <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
                      <span className="font-medium">Hold:</span> {signal.expected_holding_period}
                    </div>
                  )}
                  
                  {signal.expected_exit_date && (
                    <div className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700">
                      <span className="font-medium">Exit:</span> {signal.expected_exit_date}
                    </div>
                  )}
                </div>
                
                {/* Show More Button */}
                <button 
                  onClick={() => toggleDetails(signal.id)}
                  className={`mt-3 w-full flex items-center justify-center py-1.5 rounded-lg border text-sm transition-colors ${
                    expandedDetails[signal.id] 
                      ? 'bg-gray-100 border-gray-300 text-gray-700' 
                      : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <span>{expandedDetails[signal.id] ? 'Hide details' : 'Show more details'}</span>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className={`h-4 w-4 ml-1 transition-transform duration-300 ${expandedDetails[signal.id] ? 'rotate-180' : ''}`} 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {/* Expanded Details Section */}
                {expandedDetails[signal.id] && (
                  <div className="mt-3 space-y-3 border-t pt-3 border-gray-100">
                    {/* Pattern Analysis */}
                    {getPatterns(signal).length > 0 && (
                      <div className="rounded-lg overflow-hidden">
                        <div className="bg-gray-100 py-1.5 px-3">
                          <h4 className="text-sm font-medium text-gray-700">Pattern Analysis</h4>
                        </div>
                        <div className="p-3 bg-white border border-gray-100">
                          <div className="flex flex-wrap gap-2 mb-2">
                            {getPatterns(signal).map((pattern, index) => (
                              <span key={index} className={`px-3 py-1 text-xs rounded-full ${
                                getSignalAction(signal) === 'BUY'
                                  ? 'bg-green-50 text-green-700 border border-green-100'
                                  : 'bg-red-50 text-red-700 border border-red-100'
                              }`}>
                                {pattern}
                              </span>
                            ))}
                          </div>
                          {signal.pattern_analysis?.strength && (
                            <div className="text-xs text-gray-600">
                              <span className="font-medium">Pattern strength:</span> {signal.pattern_analysis.strength}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Technical Indicators */}
                    {signal.indicator_snapshot && (
                      <div className="rounded-lg overflow-hidden">
                        <div className="bg-gray-100 py-1.5 px-3">
                          <h4 className="text-sm font-medium text-gray-700">Technical Indicators</h4>
                        </div>
                        <div className="p-3 bg-white border border-gray-100">
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-2">
                            {signal.indicator_snapshot.rsi && (
                              <div>
                                <div className="text-xs text-gray-500">RSI</div>
                                <div className={`text-sm font-medium ${
                                  signal.indicator_snapshot.rsi === 'bullish' 
                                    ? 'text-green-600' 
                                    : signal.indicator_snapshot.rsi === 'bearish'
                                      ? 'text-red-600'
                                      : 'text-gray-700'
                                }`}>
                                  {signal.indicator_snapshot.rsi}
                                  {signal.indicator_snapshot.rsi_value !== undefined && 
                                    ` (${signal.indicator_snapshot.rsi_value.toFixed(2)})`}
                                </div>
                              </div>
                            )}
                            
                            {signal.indicator_snapshot.macd && (
                              <div>
                                <div className="text-xs text-gray-500">MACD</div>
                                <div className={`text-sm font-medium ${
                                  signal.indicator_snapshot.macd === 'bullish' 
                                    ? 'text-green-600' 
                                    : signal.indicator_snapshot.macd === 'bearish'
                                      ? 'text-red-600'
                                      : 'text-gray-700'
                                }`}>
                                  {signal.indicator_snapshot.macd}
                                </div>
                              </div>
                            )}
                            
                            {signal.indicator_snapshot.sma_50_200 && (
                              <div>
                                <div className="text-xs text-gray-500">MA Cross</div>
                                <div className={`text-sm font-medium ${
                                  signal.indicator_snapshot.sma_50_200 === 'golden_cross' 
                                    ? 'text-green-600' 
                                    : signal.indicator_snapshot.sma_50_200 === 'death_cross'
                                      ? 'text-red-600'
                                      : 'text-gray-700'
                                }`}>
                                  {signal.indicator_snapshot.sma_50_200}
                                </div>
                              </div>
                            )}
                            
                            {signal.indicator_snapshot.bollinger && (
                              <div>
                                <div className="text-xs text-gray-500">Bollinger</div>
                                <div className="text-sm font-medium text-gray-700">
                                  {signal.indicator_snapshot.bollinger}
                                </div>
                              </div>
                            )}
                            
                            {signal.indicator_snapshot.volume_trend && (
                              <div>
                                <div className="text-xs text-gray-500">Volume</div>
                                <div className="text-sm font-medium text-gray-700">
                                  {signal.indicator_snapshot.volume_trend}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* AI Analysis */}
                    <div className="rounded-lg overflow-hidden">
                      <div className="bg-gray-100 py-1.5 px-3">
                        <h4 className="text-sm font-medium text-gray-700">AI Analysis</h4>
                      </div>
                      <div className="p-3 bg-white border border-gray-100">
                        <p className="text-sm text-gray-700">{getAnalysisText(signal)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500">No swing trading signals available</p>
          <p className="text-sm text-gray-400 mt-2">
            Signals will appear when trading conditions are favorable
          </p>
        </div>
      )}
    </div>
  );
}