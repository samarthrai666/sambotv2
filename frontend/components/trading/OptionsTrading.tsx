'use client';

import { useState } from 'react';

// Define types
type IndexType = 'NIFTY' | 'BANKNIFTY';
type ModeType = 'scalp' | 'swing' | 'longterm';

interface OptionsData {
  enabled: boolean;      // New property to enable/disable options trading
  indexes: IndexType[];
  modes: ModeType[];
  auto_execute: boolean;
}

interface OptionsProps {
  data: OptionsData;
  onChange: (data: OptionsData) => void;
}

export default function OptionsTrading({ data, onChange }: OptionsProps) {
  // Handle the main toggle for enabling/disabling options trading
  const handleToggleEnabled = () => {
    onChange({
      ...data,
      enabled: !data.enabled
    });
  };

  // Handle index selection toggle
  const handleIndexToggle = (index: IndexType) => {
    // If already selected, remove it (but don't allow removing the last one)
    if (data.indexes.includes(index)) {
      if (data.indexes.length > 1) {
        onChange({
          ...data,
          indexes: data.indexes.filter(i => i !== index)
        });
      }
    } else {
      // Otherwise add it
      onChange({
        ...data,
        indexes: [...data.indexes, index]
      });
    }
  };

  // Handle mode selection toggle
  const handleModeToggle = (mode: ModeType) => {
    // If already selected, remove it (but don't allow removing the last one)
    if (data.modes.includes(mode)) {
      if (data.modes.length > 1) {
        onChange({
          ...data,
          modes: data.modes.filter(m => m !== mode)
        });
      }
    } else {
      // Otherwise add it
      onChange({
        ...data,
        modes: [...data.modes, mode]
      });
    }
  };

  // Handle auto execute toggle
  const handleAutoExecuteChange = () => {
    onChange({
      ...data,
      auto_execute: !data.auto_execute
    });
  };

  return (
    <div className={`bg-white shadow rounded-lg overflow-hidden border ${data.enabled ? 'border-green-100' : 'border-gray-200'}`}>
      {/* Header with main toggle */}
      <div className={`px-4 py-3 border-b flex justify-between items-center ${data.enabled ? 'bg-green-50 border-green-100' : 'bg-gray-50 border-gray-200'}`}>
        <h2 className={`font-bold ${data.enabled ? 'text-green-800' : 'text-gray-700'}`}>Options Trading</h2>
        <div className="flex items-center">
          <span className="text-xs mr-2 text-gray-500">
            {data.enabled ? 'Enabled' : 'Disabled'}
          </span>
          <button
            type="button"
            className={`
              relative inline-flex h-5 w-10 items-center rounded-full
              ${data.enabled ? 'bg-green-600' : 'bg-gray-300'}
            `}
            onClick={handleToggleEnabled}
          >
            <span
              className={`
                inline-block h-4 w-4 transform rounded-full bg-white transition
                ${data.enabled ? 'translate-x-5' : 'translate-x-1'}
              `}
            />
          </button>
        </div>
      </div>

      {/* Content - show only if enabled */}
      {data.enabled && (
        <div className="p-4 space-y-6">
          {/* Index Selection */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Choose Index
              </label>
              <span className="text-xs text-gray-500">
                {data.indexes.length} selected
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                className={`p-3 rounded-lg border-2 flex items-center justify-center ${
                  data.indexes.includes('NIFTY')
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleIndexToggle('NIFTY')}
              >
                <span className="font-medium">NIFTY</span>
              </button>
              <button
                type="button"
                className={`p-3 rounded-lg border-2 flex items-center justify-center ${
                  data.indexes.includes('BANKNIFTY')
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleIndexToggle('BANKNIFTY')}
              >
                <span className="font-medium">BANKNIFTY</span>
              </button>
            </div>
          </div>

          {/* Trading Mode Selection */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Trading Mode
              </label>
              <span className="text-xs text-gray-500">
                {data.modes.length} selected
              </span>
            </div>
            <div className="space-y-2">
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('scalp')
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('scalp')}
              >
                <span className="text-lg mr-2">🐇</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Scalping</div>
                  <div className="text-xs text-gray-500">Minutes to hours</div>
                </div>
                {data.modes.includes('scalp') && (
                  <div className="ml-auto bg-green-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('swing')
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('swing')}
              >
                <span className="text-lg mr-2">🐢</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Swing</div>
                  <div className="text-xs text-gray-500">Days to weeks</div>
                </div>
                {data.modes.includes('swing') && (
                  <div className="ml-auto bg-green-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('longterm')
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('longterm')}
              >
                <span className="text-lg mr-2">🧘</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Long-term</div>
                  <div className="text-xs text-gray-500">Months or longer</div>
                </div>
                {data.modes.includes('longterm') && (
                  <div className="ml-auto bg-green-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Selected Combinations */}
          <div className="bg-green-50 p-3 rounded-lg">
            <h3 className="text-xs font-medium text-gray-700 mb-2">Selected Combinations</h3>
            <div className="flex flex-wrap gap-1">
              {data.indexes.flatMap(index => 
                data.modes.map(mode => (
                  <div 
                    key={`${index}-${mode}`} 
                    className="bg-white px-2 py-1 text-xs rounded border border-green-200 shadow-sm"
                  >
                    {index} + {mode === 'scalp' ? '🐇' : mode === 'swing' ? '🐢' : '🧘'}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Auto-Execute Toggle */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-gray-700">Auto Execution</h3>
              <p className="text-xs text-gray-500">Place trades automatically</p>
            </div>
            <button
              type="button"
              className={`
                relative inline-flex h-5 w-10 items-center rounded-full
                ${data.auto_execute ? 'bg-green-600' : 'bg-gray-200'}
              `}
              onClick={handleAutoExecuteChange}
            >
              <span
                className={`
                  inline-block h-4 w-4 transform rounded-full bg-white transition
                  ${data.auto_execute ? 'translate-x-5' : 'translate-x-1'}
                `}
              />
            </button>
          </div>
        </div>
      )}

      {/* Show message when disabled */}
      {!data.enabled && (
        <div className="p-6 text-center text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.879 16.121A3 3 0 1012 12.879m0 0l4.242-4.242a7.029 7.029 0 00-9.9 9.9l4.242-4.242zm0 0l-4.242 4.242a7.029 7.029 0 009.9-9.9l-4.242 4.242z" />
          </svg>
          <p className="text-sm">Options trading is currently disabled.</p>
          <p className="text-xs mt-2">Toggle the switch above to enable options trading features.</p>
        </div>
      )}
    </div>
  );
}