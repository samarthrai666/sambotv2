'use client';

import { useState } from 'react';

interface IntradayEquitySignal {
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
  strategy: 'Opening Range' | 'Trend Following' | 'Mean Reversion';
  volume_surge: number;
  key_level: number;
  trigger: string;
  executed?: boolean;
}

interface IntradayEquitySignalsProps {
  signals: IntradayEquitySignal[];
  onExecute: (id: string) => void;
  isLoading?: boolean;
}

export default function IntradayEquitySignals({
  signals,
  onExecute,
  isLoading = false
}: IntradayEquitySignalsProps) {
  const [expandedSignalId, setExpandedSignalId] = useState<string | null>(null);

  const toggleExpandSignal = (id: string) => {
    if (expandedSignalId === id) {
      setExpandedSignalId(null);
    } else {
      setExpandedSignalId(id);
    }
  };

  // Get icon for strategy type
  const getStrategyIcon = (strategy: string): string => {
    switch (strategy) {
      case 'Opening Range':
        return '🔔';
      case 'Trend Following':
        return '📈';
      case 'Mean Reversion':
        return '🔄';
      default:
        return '📊';
    }
  };

  // Format time remaining for intraday signals
  const getTimeRemaining = (): string => {
    const now = new Date();
    const marketClose = new Date();
    marketClose.setHours(15, 30, 0, 0); // 3:30 PM

    if (now > marketClose) return 'Market Closed';

    const diffMs = marketClose.getTime() - now.getTime();
    const diffHrs = Math.floor(diffMs / 1000 / 60 / 60);
    const diffMins = Math.floor((diffMs / 1000 / 60) % 60);

    return `${diffHrs}h ${diffMins}m remaining`;
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden border border-purple-100">
      <div className="bg-purple-50 py-3 px-4 border-b border-purple-100 flex justify-between items-center">
        <h2 className="font-semibold text-purple-800">
          Intraday Equity Trading ({signals.length})
        </h2>
        <span className="text-xs text-purple-600 font-medium">
          {getTimeRemaining()}
        </span>
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
          <div className="space-y-3">
            {signals.map((signal) => (
              <div
                key={signal.id}
                className="border rounded-lg overflow-hidden shadow-sm transition-all"
              >
                {/* Signal Header */}
                <div className={`flex justify-between items-center px-3 py-2 ${signal.action === 'BUY' ? 'bg-green-50' : 'bg-red-50'}`}>
                  <div className="flex items-center">
                    <span className={`text-base font-medium ${signal.action === 'BUY' ? 'text-green-700' : 'text-red-700'}`}>
                      {signal.symbol}
                    </span>
                    <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-white shadow-sm">
                      {getStrategyIcon(signal.strategy)} {signal.strategy}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-medium bg-gray-100 px-2 py-0.5 rounded">
                      {signal.timeframe}
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

                {/* Price Levels */}
                <div className="px-3 py-2 grid grid-cols-3 gap-2 text-sm border-b">
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

                {/* Signal Details - Always visible */}
                <div className="px-3 py-2 text-xs border-b">
                  <div className="flex justify-between mb-1">
                    <div>Trigger: <span className="font-medium">{signal.trigger}</span></div>
                    <div>Risk:Reward: <span className="font-medium">{signal.risk_reward.toFixed(2)}</span></div>
                  </div>
                  <div className="flex justify-between">
                    <div>Key Level: <span className="font-medium">{signal.key_level.toFixed(2)}</span></div>
                    <div>Vol Surge: <span className="font-medium">{signal.volume_surge.toFixed(1)}x</span></div>
                  </div>
                </div>

                {/* Expanded Content */}
                {expandedSignalId === signal.id && (
                  <div className="px-3 py-2 bg-gray-50">
                    <div className="text-sm flex justify-between mb-2">
                      <div>
                        <span className="text-gray-500 mr-1">Confidence:</span>
                        <span className={`font-medium ${signal.confidence >= 80 ? 'text-green-600' : 'text-yellow-600'}`}>
                          {signal.confidence}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500 mr-1">Potential:</span>
                        <span className="text-green-600 font-medium">
                          +{signal.potential_gain.toFixed(2)}%
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 flex justify-end">
                      {!signal.executed ? (
                        <button
                          onClick={() => onExecute(signal.id)}
                          className="px-3 py-1 bg-purple-600 text-white text-xs font-medium rounded hover:bg-purple-700 transition-colors"
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
            <p className="text-gray-500">No intraday signals available</p>
            <p className="text-sm text-gray-400 mt-2">
              Available when intraday equity trading is enabled
            </p>
          </div>
        )}
      </div>
    </div>
  );
}