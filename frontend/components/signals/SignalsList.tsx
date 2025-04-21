'use client';

import { Signal } from '../../types/trading';
import SignalCard from './SignalCard';
import { useAvailableSignals } from '@/components/signals/useAvailableSignal'

interface SignalsListProps {
  title: string;
  isExecuted: boolean;
  onExecute?: (id: string) => void;
  emptyMessage?: {
    primary: string;
    secondary?: string;
  };
  refreshInterval?: number;
}

export default function SignalsList({
  title,
  isExecuted,
  onExecute,
  emptyMessage = {
    primary: 'No signals available',
    secondary: 'Check back later or try refreshing'
  },
  refreshInterval = 5000
}: SignalsListProps) {
  // Use our custom hook for live signals
  const { signals, isLoading, error, refreshSignals } = useAvailableSignals(refreshInterval);

  // Format the signal title to display in the desired format
  const formatSignalTitle = (signal: Signal) => {
    // For options, include strike price, option type and expiry
    if (signal.instrumentType === 'Option') {
      const expiryDate = signal.expiryDate || 'Apr 17th'; // Use provided expiry or default
      return `${signal.symbol} ${signal.strike} ${signal.optionType} ${expiryDate}`;
    }
    
    // For futures, show futures with month
    if (signal.instrumentType === 'Future') {
      const expiryMonth = signal.expiryDate || 'Apr';
      return `${signal.symbol} FUT ${expiryMonth}`;
    }
    
    // Default to just the symbol for stocks
    return signal.symbol;
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border border-green-100 relative">
      <div className="border-b border-green-100 bg-green-50 py-3 px-4 flex justify-between items-center">
        <h2 className="font-semibold text-green-800">
          {title} ({signals.length})
        </h2>
        <button 
          onClick={refreshSignals} 
          className="text-xs text-green-600 hover:text-green-800 flex items-center"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="mr-1">
              <div className="w-3 h-3 border-t-2 border-green-500 rounded-full animate-spin"></div>
            </span>
          ) : null}
          Refresh
        </button>
      </div>
      
      <div className="p-4 max-h-[600px] overflow-y-auto">
        {error && (
          <div className="bg-red-50 text-red-600 p-2 mb-3 rounded text-sm">
            {error}
          </div>
        )}
        
        {signals.length > 0 ? (
         <div className="space-y-4">
         {signals.map((signal, idx) => (
           <SignalCard 
             key={`${signal.id}-${idx}`}
             signal={{
               ...signal,
               formattedTitle: formatSignalTitle(signal)
             }}
             isExecuted={isExecuted}
             onExecute={onExecute}
           />
         ))}
       </div>
       
        ) : (
          <div className="text-center py-10">
            <p className="text-gray-500">{emptyMessage.primary}</p>
            {emptyMessage.secondary && (
              <p className="text-sm text-gray-400 mt-2">
                {emptyMessage.secondary}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}