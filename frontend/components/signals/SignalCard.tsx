'use client';

import { Signal } from '../../types/trading';

interface SignalCardProps {
  signal: Signal;
  isExecuted?: boolean;
  onExecute?: (id: string) => void;
  title?: string; // Optional title prop to receive formatted title from parent
}

export default function SignalCard({ 
  signal, 
  isExecuted = false, 
  onExecute,
  title
}: SignalCardProps) {
  // Determine signal type icon and colors
  const getSignalTypeProps = () => {
    if (signal.action === 'BUY') {
      return {
        bgColor: 'bg-green-100',
        textColor: 'text-green-800',
        borderColor: 'border-green-200',
        icon: '↗️'
      };
    } 
    return {
      bgColor: 'bg-red-100', 
      textColor: 'text-red-800',
      borderColor: 'border-red-200',
      icon: '↘️'
    };
  };

  const { bgColor, textColor, borderColor, icon } = getSignalTypeProps();

  // Format percentages with 2 decimal places and + sign for positive values
  const formatPercent = (value: number) => {
    const formatted = (value * 100).toFixed(2);
    return value > 0 ? `+${formatted}%` : `${formatted}%`;
  };

  // Helper to format the symbol with strike and option type if applicable
  const getFormattedSymbol = () => {
    // If title is provided by parent, use it
    if (title) {
      return title;
    }
    
    // For options, display as NIFTY 23400 CE Apr 17th
    if (signal.instrumentType === 'Option') {
      // Ensure we have values for all parts, with fallbacks
      const strike = signal.strike || '23500';
      const optionType = signal.optionType || 'CE';
      const expiryDate = signal.expiryDate || 'Apr 17th';
      
      return `${signal.symbol} ${strike} ${optionType} ${expiryDate}`;
    } else if (signal.instrumentType === 'Future') {
      const expiryMonth = signal.expiryDate || 'Apr';
      return `${signal.symbol} FUT ${expiryMonth}`;
    }
    
    // Default to just the symbol for stocks
    return signal.symbol;
  };

  // Get strategy emoji
  const getStrategyEmoji = () => {
    switch(signal.strategy) {
      case 'scalp': return '🐇';
      case 'swing': return '🐢';
      case 'longterm': return '🧘';
      default: return '';
    }
  };

  return (
    <div className={`border rounded-lg overflow-hidden ${borderColor}`}>
      <div className="p-4">
        <div className="flex justify-between">
          <div className="flex items-center">
            <span className="text-lg mr-2">{icon}</span>
            <div>
              <div className="flex items-center">
                <h3 className="font-medium">{getFormattedSymbol()}</h3>
                <span className="ml-2 text-xs px-2 py-0.5 bg-gray-100 rounded-full">
                  {getStrategyEmoji()} {signal.action} {signal.strategy}
                </span>
              </div>
              <p className="text-xs text-gray-500">
                {new Date(signal.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="text-right">
            <div className={`font-bold ${textColor}`}>
              ₹{signal.price.toFixed(2)}
            </div>
            <div className="text-xs text-gray-500">
              Target: ₹{signal.target_price.toFixed(2)} 
              ({formatPercent(signal.potential_return)})
            </div>
          </div>
        </div>
        
        {/* Always show this basic info */}
        <div className="mt-3 pt-2 border-t border-gray-100 grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
          <div>
            <span className="text-gray-500">Stop Loss:</span> 
            <span className="ml-1 font-medium">₹{signal.stop_loss.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-gray-500">Confidence:</span> 
            <span className="ml-1 font-medium">{signal.confidence_score}%</span>
          </div>
        </div>
        
        {/* Show patterns always */}
        <div className="mt-2 text-xs">
          <div className="flex flex-wrap gap-1">
            {signal.patterns.map((pattern, idx) => (
              <span 
                key={idx} 
                className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full"
              >
                {pattern}
              </span>
            ))}
          </div>
        </div>
        
        {/* Always shown expanded content */}
        <div className="mt-3 pt-2 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Risk/Reward:</span> 
              <span className="ml-2">{signal.risk_reward_ratio.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-gray-500">Timeframe:</span> 
              <span className="ml-2">{signal.timeframe}</span>
            </div>
            <div>
              <span className="text-gray-500">Quantity:</span> 
              <span className="ml-2">{signal.quantity}</span>
            </div>
            <div>
              <span className="text-gray-500">Type:</span> 
              <span className="ml-2">{signal.instrumentType || 'Stock'}</span>
            </div>
          </div>
          
          {/* Indicators */}
          <div className="mt-3 text-sm">
            <p className="text-gray-500 mb-1">Indicators:</p>
            <div className="flex flex-wrap gap-1">
              {signal.indicators.map((indicator, idx) => (
                <span 
                  key={idx} 
                  className={`${bgColor} ${textColor} px-2 py-1 rounded-full text-xs`}
                >
                  {indicator}
                </span>
              ))}
            </div>
          </div>
          
          {/* AI Analysis */}
          {signal.aiAnalysis && (
            <div className="mt-3 text-sm">
              <p className="text-gray-500 mb-1">AI Analysis:</p>
              <div className="bg-blue-50 border-l-2 border-blue-300 text-blue-900 p-2 rounded text-xs italic">
                "{signal.aiAnalysis}"
              </div>
            </div>
          )}
          
          {/* Notes */}
          {signal.notes && (
            <div className="mt-3 text-sm">
              <p className="text-gray-500">Notes:</p>
              <p className="mt-1 text-xs">{signal.notes}</p>
            </div>
          )}
          
          {/* Order details if executed */}
          {isExecuted && signal.order_id && (
            <div className="mt-3 text-sm">
              <p className="text-gray-500">Order Details:</p>
              <div className="bg-green-50 p-2 rounded text-xs mt-1">
                <div><span className="font-medium">Order ID:</span> {signal.order_id}</div>
                <div><span className="font-medium">Executed:</span> {new Date(signal.executed_at || '').toLocaleString()}</div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="border-t">
        {!isExecuted && onExecute && (
          <button
            onClick={() => onExecute(signal.id)}
            className="w-full py-2 text-xs text-white bg-green-500 hover:bg-green-600"
          >
            Execute Trade
          </button>
        )}
        
        {isExecuted && (
          <button
            className="w-full py-2 text-xs text-white bg-red-500 hover:bg-red-600"
          >
            Close Position
          </button>
        )}
      </div>
    </div>
  );
}