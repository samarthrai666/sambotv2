'use client';

import { Signal } from '../../types/trading';
import SignalCard from './SignalCard';

interface OptionsSignalsProps {
  availableSignals: Signal[];
  executedSignals: Signal[];
  onExecute: (id: string) => void;
  isLoading?: boolean;
}

export default function OptionsSignals({ 
  availableSignals, 
  executedSignals, 
  onExecute,
  isLoading = false
}: OptionsSignalsProps) {
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
    <div className="bg-white shadow rounded-lg overflow-hidden border border-green-100">
      <div className="bg-green-50 py-3 px-4 border-b border-green-100">
        <h2 className="font-semibold text-green-800">
          Options Trading ({availableSignals.length + executedSignals.length})
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
        ) : (
          <div className="space-y-4">
            {/* Executed Signals Section */}
            {executedSignals.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-500 mb-2 border-b pb-1">Active Positions</h3>
                <div className="space-y-3">
                  {executedSignals.map((signal) => (
                    <SignalCard
                      key={signal.id}
                      signal={signal}
                      isExecuted={true}
                      title={formatSignalTitle(signal)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Available Signals Section */}
            {availableSignals.length > 0 ? (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2 border-b pb-1">New Signals</h3>
                <div className="space-y-3">
                  {availableSignals.map((signal) => (
                    <SignalCard
                      key={signal.id}
                      signal={signal}
                      isExecuted={false}
                      onExecute={onExecute}
                      title={formatSignalTitle(signal)}
                    />
                  ))}
                </div>
              </div>
            ) : executedSignals.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-gray-500">No options signals available</p>
                <p className="text-sm text-gray-400 mt-2">
                  Try refreshing or changing your selection criteria
                </p>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}