'use client';

import { useState } from 'react';

// Define types
// Updated SectorType with the complete list provided
type EquitySwingMode = 'momentum' | 'breakout' | 'reversal';
type SectorType = 
  | 'Automobile and Auto Components'
  | 'Capital Goods'
  | 'Chemicals'
  | 'Construction'
  | 'Construction Materials'
  | 'Consumer Durables'
  | 'Consumer Services'
  | 'Diversified'
  | 'Fast Moving Consumer Goods'
  | 'Financial Services'
  | 'Forest Materials'
  | 'Healthcare'
  | 'Information Technology'
  | 'Media Entertainment & Publication'
  | 'Metals & Mining'
  | 'Oil Gas & Consumable Fuels'
  | 'Power'
  | 'Realty'
  | 'Services'
  | 'Telecommunication'
  | 'Textiles';

type ScanFrequency = 'daily' | 'weekly' | 'monthly';
type MarketCapType = 'largecap' | 'midcap' | 'smallcap'; // Market cap type

interface SwingEquityData {
  enabled: boolean;
  modes: EquitySwingMode[];
  max_stocks: number;
  sectors: SectorType[];
  scan_frequency: ScanFrequency;
  market_caps: MarketCapType[]; // Field for market caps
}

interface SwingEquityProps {
  data: SwingEquityData;
  onChange: (data: SwingEquityData) => void;
}

export default function SwingEquityTrading({ data, onChange }: SwingEquityProps) {
  // Toggle enable/disable
  const toggleEnabled = () => {
    onChange({
      ...data,
      enabled: !data.enabled
    });
  };

  // Handle mode selection toggle
  const handleModeToggle = (mode: EquitySwingMode) => {
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

  // Handle max stocks change
  const handleMaxStocksChange = (value: number) => {
    onChange({
      ...data,
      max_stocks: value
    });
  };

  // Handle sector toggle
  const handleSectorToggle = (sector: SectorType) => {
    if (data.sectors.includes(sector)) {
      onChange({
        ...data,
        sectors: data.sectors.filter(s => s !== sector)
      });
    } else {
      onChange({
        ...data,
        sectors: [...data.sectors, sector]
      });
    }
  };

  // Handle market cap toggle
  const handleMarketCapToggle = (cap: MarketCapType) => {
    if (data.market_caps.includes(cap)) {
      // Don't allow removing if it's the last selected cap
      if (data.market_caps.length > 1) {
        onChange({
          ...data,
          market_caps: data.market_caps.filter(c => c !== cap)
        });
      }
    } else {
      onChange({
        ...data,
        market_caps: [...data.market_caps, cap]
      });
    }
  };

  // Handle scan frequency change
  const handleScanFrequencyChange = (frequency: ScanFrequency) => {
    onChange({
      ...data,
      scan_frequency: frequency
    });
  };

  // Complete list of sectors from the provided list
  const allSectors: SectorType[] = [
    'Automobile and Auto Components',
    'Capital Goods',
    'Chemicals',
    'Construction',
    'Construction Materials',
    'Consumer Durables',
    'Consumer Services',
    'Diversified',
    'Fast Moving Consumer Goods',
    'Financial Services',
    'Forest Materials',
    'Healthcare',
    'Information Technology',
    'Media Entertainment & Publication',
    'Metals & Mining',
    'Oil Gas & Consumable Fuels',
    'Power',
    'Realty',
    'Services',
    'Telecommunication',
    'Textiles'
  ];

  return (
    <div className={`bg-white shadow rounded-lg overflow-hidden border ${data.enabled ? 'border-blue-100' : 'border-gray-200'}`}>
      <div className={`px-4 py-3 border-b flex justify-between items-center ${data.enabled ? 'bg-blue-50 border-blue-100' : 'bg-gray-50 border-gray-200'}`}>
        <h2 className={`font-bold ${data.enabled ? 'text-blue-800' : 'text-gray-700'}`}>Swing Equity</h2>
        <div className="flex items-center">
          <span className="text-xs mr-2 text-gray-500">
            {data.enabled ? 'Enabled' : 'Disabled'}
          </span>
          <button
            type="button"
            className={`
              relative inline-flex h-5 w-10 items-center rounded-full
              ${data.enabled ? 'bg-blue-600' : 'bg-gray-300'}
            `}
            onClick={toggleEnabled}
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
      {data.enabled ? (
        <div className="p-4 space-y-6">
          {/* Swing Trading Strategy */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Strategy
              </label>
              <span className="text-xs text-gray-500">
                {data.modes.length} selected
              </span>
            </div>
            <div className="space-y-2">
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('momentum')
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('momentum')}
              >
                <span className="text-lg mr-2">🚀</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Momentum</div>
                  <div className="text-xs text-gray-500">Trend strength</div>
                </div>
                {data.modes.includes('momentum') && (
                  <div className="ml-auto bg-blue-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('breakout')
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('breakout')}
              >
                <span className="text-lg mr-2">📈</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Breakout</div>
                  <div className="text-xs text-gray-500">Pattern breaks</div>
                </div>
                {data.modes.includes('breakout') && (
                  <div className="ml-auto bg-blue-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('reversal')
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('reversal')}
              >
                <span className="text-lg mr-2">↩️</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Reversal</div>
                  <div className="text-xs text-gray-500">Counter-trend</div>
                </div>
                {data.modes.includes('reversal') && (
                  <div className="ml-auto bg-blue-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-blue-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* Market Cap Selection */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Market Capitalization
              </label>
              <span className="text-xs text-gray-500">
                {data.market_caps.length} selected
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'largecap', label: 'Largecap' },
                { id: 'midcap', label: 'Midcap' },
                { id: 'smallcap', label: 'Smallcap' }
              ].map(cap => (
                <button
                  key={cap.id}
                  type="button"
                  onClick={() => handleMarketCapToggle(cap.id as MarketCapType)}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium 
                    ${data.market_caps.includes(cap.id as MarketCapType) 
                      ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                      : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                    }`}
                >
                  {data.market_caps.includes(cap.id as MarketCapType) ? '☑️' : '☐'} {cap.label}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500">Select market cap segments to include in scans</p>
          </div>

          {/* Max Stocks Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Maximum Stocks
              </label>
              <span className="text-sm font-medium text-blue-600">
                {data.max_stocks}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              step="1"
              value={data.max_stocks}
              onChange={(e) => handleMaxStocksChange(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1</span>
              <span>5</span>
              <span>10</span>
            </div>
          </div>

          {/* Sector Preferences - Updated with full list */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Sector Preferences
            </label>
            <div className="max-h-60 overflow-y-auto p-2 border border-gray-200 rounded-md">
              <div className="flex flex-wrap gap-1">
                {allSectors.map(sector => (
                  <div 
                    key={sector}
                    className={`px-2 py-1 m-1 text-xs rounded-full border cursor-pointer ${
                      data.sectors.includes(sector) 
                        ? 'bg-blue-50 text-blue-700 border-blue-200' 
                        : 'bg-gray-50 text-gray-700 border-gray-200'
                    }`}
                    onClick={() => handleSectorToggle(sector)}
                  >
                    {sector}
                  </div>
                ))}
              </div>
            </div>
            <p className="text-xs text-gray-500">Monitoring top stocks in these sectors</p>
          </div>

          {/* Scan Frequency */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Scan Frequency
            </label>
            <div className="grid grid-cols-3 gap-1">
              <div 
                className={`text-xs p-2 rounded text-center cursor-pointer ${
                  data.scan_frequency === 'daily' 
                    ? 'bg-blue-100 text-blue-800 font-medium' 
                    : 'bg-gray-100 text-gray-800'
                }`}
                onClick={() => handleScanFrequencyChange('daily')}
              >
                Daily
              </div>
              <div 
                className={`text-xs p-2 rounded text-center cursor-pointer ${
                  data.scan_frequency === 'weekly' 
                    ? 'bg-blue-100 text-blue-800 font-medium' 
                    : 'bg-gray-100 text-gray-800'
                }`}
                onClick={() => handleScanFrequencyChange('weekly')}
              >
                Weekly
              </div>
              <div 
                className={`text-xs p-2 rounded text-center cursor-pointer ${
                  data.scan_frequency === 'monthly' 
                    ? 'bg-blue-100 text-blue-800 font-medium' 
                    : 'bg-gray-100 text-gray-800'
                }`}
                onClick={() => handleScanFrequencyChange('monthly')}
              >
                Monthly
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Show message when disabled */
        <div className="p-6 text-center text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <p className="text-sm">Swing equity trading is currently disabled.</p>
          <p className="text-xs mt-2">Toggle the switch above to enable swing equity trading features.</p>
        </div>
      )}
    </div>
  );
}