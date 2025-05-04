'use client';

import { useState } from 'react';
import { Signal } from '../../types/trading';

interface SwingEquitySignal {
  id: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  entry_price: number;
  target_price: number;
  stop_loss: number;
  risk_reward: number;
  potential_gain: number;
  timeframe: string;
  confidence: number;
  setup_type: string;
  sector: string;
  analysis: string;
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
  const [expandedSignalId, setExpandedSignalId] = useState<string | null>(null);

  const toggleExpandSignal = (id: string) => {
    if (expandedSignalId === id) {
      setExpandedSignalId(null);
    } else {
      setExpandedSignalId(id);
    }
  };
  
  // Calculate potential gain percentage
  const getPotentialGain = (signal: SwingEquitySignal): string => {
    const gainPct = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100;
    return gainPct > 0 ? `+${gainPct.toFixed(2)}%` : `${gainPct.toFixed(2)}%`;
  };

  // Determine color based on confidence
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-blue-600';
    return 'text-yellow-600';
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden border border-blue-100">
      <div className="bg-blue-50 py-3 px-4 border-b border-blue-100">
        <h2 className="font-semibold text-blue-800">
          Swing Equity Trading ({signals.length})
        </h2>
      </div>
      
      <div className="p-4">
        {isLoading ? (
          <div className="flex justify-center py-6">
            <div className="animate-pulse flex space-x-4">
              <div className="flex-1 space-y-4 py-1">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                </div>
              </div>
            </div>
          </div>
        ) : signals.length > 0 ? (
          <div className="space-y-4">
            {signals.map((signal) => (
              <div 
                key={signal.id}
                className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
              >
                {/* Signal Header */}
                <div className={`px-4 py-3 ${signal.action === 'BUY' ? 'bg-blue-50' : 'bg-red-50'} flex justify-between items-center`}>
                  <div className="flex items-center">
                    <span className={`font-medium ${signal.action === 'BUY' ? 'text-blue-700' : 'text-red-700'}`}>
                      {signal.symbol}
                    </span>
                    <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-800">
                      {signal.sector}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`text-xs font-medium ${getConfidenceColor(signal.confidence)}`}>
                      {signal.confidence}% confidence
                    </span>
                    <button
                      onClick={() => toggleExpandSignal(signal.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedSignalId === signal.id ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
                
                {/* Signal Summary */}
                <div className="px-4 py-3 border-b border-gray-100">
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div>
                      <div className="text-xs text-gray-500">Entry</div>
                      <div className="font-medium">{signal.entry_price.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Target</div>
                      <div className="font-medium text-green-600">{signal.target_price.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500">Stop Loss</div>
                      <div className="font-medium text-red-600">{signal.stop_loss.toFixed(2)}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-2 text-xs text-gray-600">
                    <div>Potential: <span className="font-medium text-green-600">{getPotentialGain(signal)}</span></div>
                    <div>R:R: <span className="font-medium">{signal.risk_reward.toFixed(2)}</span></div>
                    <div>Setup: <span className="font-medium">{signal.setup_type}</span></div>
                  </div>
                </div>
                
                {/* Expanded Content */}
                {expandedSignalId === signal.id && (
                  <div className="px-4 py-3 bg-gray-50">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis</h4>
                    <p className="text-sm text-gray-600">{signal.analysis}</p>
                    
                    <div className="mt-3 flex justify-end">
                      {!signal.executed ? (
                        <button
                          onClick={() => onExecute(signal.id)}
                          className="px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 transition-colors"
                        >
                          Execute Trade
                        </button>
                      ) : (
                        <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                          Position Active
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <p className="text-gray-500">No swing trading signals available</p>
            <p className="text-sm text-gray-400 mt-2">
              Available when swing equity trading is enabled
            </p>
          </div>
        )}
      </div>
    </div>
  );
}