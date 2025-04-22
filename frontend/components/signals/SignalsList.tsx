'use client';

import { Signal } from '../../types/trading';
import SignalCard from './SignalCard';

interface SignalsListProps {
  title: string;
  isExecuted: boolean;
  onExecute?: (id: string) => void;
  emptyMessage?: {
    primary: string;
    secondary?: string;
  };
  refreshInterval?: number;
  signals: Signal[]; // Now required as a prop
}

export default function SignalsList({
  title,
  isExecuted,
  onExecute,
  emptyMessage = {
    primary: 'No signals available',
    secondary: 'Check back later or try refreshing'
  },
  refreshInterval = 0,
  signals = []
}: SignalsListProps) {
  // We're now receiving signals directly as props instead of fetching them

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
      </div>
      
      <div className="p-4 max-h-[600px] overflow-y-auto">
        {signals.length > 0 ? (
          <div className="space-y-4">
            {signals.map((signal, idx) => (
              <SignalCard 
                key={`${signal.id}-${idx}`}
                signal={signal}
                title={formatSignalTitle(signal)}
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