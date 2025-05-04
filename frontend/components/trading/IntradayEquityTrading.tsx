'use client';

import { useState } from 'react';

// Define types
type EquityIntradayMode = 'opening_range' | 'trend_following' | 'mean_reversion';
type Timeframe = '1m' | '5m' | '15m' | '1h';
type RiskLevel = '0.5' | '1.0' | '1.5' | '2.0';
type Sector = 'IT' | 'Auto' | 'Pharma' | 'FMCG' | 'Banking' | 'Infra' | 'Energy';
type StockUniverse = 'nifty50' | 'fno' | 'midcap' | 'penny' | 'custom';

interface IntradayEquityData {
  enabled: boolean;
  modes: EquityIntradayMode[];
  max_stocks: number;
  timeframes: Timeframe[];
  risk_per_trade: RiskLevel;
  sectors: Sector[];           // New field for sector filter
  stock_universe: StockUniverse[]; // New field for stock universe filter
  smart_filter: boolean;       // Whether to use smart filtering
}

interface IntradayEquityProps {
  data: IntradayEquityData;
  onChange: (data: IntradayEquityData) => void;
}

export default function IntradayEquityTrading({ data, onChange }: IntradayEquityProps) {
  // Toggle enable/disable
  const toggleEnabled = () => {
    onChange({
      ...data,
      enabled: !data.enabled
    });
  };

  // Handle mode selection toggle
  const handleModeToggle = (mode: EquityIntradayMode) => {
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

  // Handle timeframe toggle
  const handleTimeframeToggle = (timeframe: Timeframe) => {
    if (data.timeframes.includes(timeframe)) {
      // Don't allow removing the last timeframe
      if (data.timeframes.length > 1) {
        onChange({
          ...data,
          timeframes: data.timeframes.filter(t => t !== timeframe)
        });
      }
    } else {
      onChange({
        ...data,
        timeframes: [...data.timeframes, timeframe]
      });
    }
  };

  // Handle risk per trade change
  const handleRiskPerTradeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({
      ...data,
      risk_per_trade: e.target.value as RiskLevel
    });
  };

  // Handle sector toggle
  const handleSectorToggle = (sector: Sector) => {
    if (data.sectors.includes(sector)) {
      // Allow removing if there's more than one sector selected
      if (data.sectors.length > 1) {
        onChange({
          ...data,
          sectors: data.sectors.filter(s => s !== sector)
        });
      }
    } else {
      onChange({
        ...data,
        sectors: [...data.sectors, sector]
      });
    }
  };

  // Handle stock universe toggle
  const handleStockUniverseToggle = (universe: StockUniverse) => {
    // Special handling for penny stocks if smart filter is enabled
    if (universe === 'penny' && data.smart_filter) {
      return; // Don't allow penny stocks when smart filter is on
    }

    if (data.stock_universe.includes(universe)) {
      // Allow removing if there's more than one universe selected
      if (data.stock_universe.length > 1) {
        onChange({
          ...data,
          stock_universe: data.stock_universe.filter(u => u !== universe)
        });
      }
    } else {
      onChange({
        ...data,
        stock_universe: [...data.stock_universe, universe]
      });
    }
  };

  // Toggle smart filter
  const toggleSmartFilter = () => {
    const newSmartFilter = !data.smart_filter;
    
    // If enabling smart filter, remove penny stocks from universe
    let newUniverse = [...data.stock_universe];
    if (newSmartFilter && newUniverse.includes('penny')) {
      newUniverse = newUniverse.filter(u => u !== 'penny');
    }
    
    onChange({
      ...data,
      smart_filter: newSmartFilter,
      stock_universe: newUniverse
    });
  };

  return (
    <div className={`bg-white shadow rounded-lg overflow-hidden border ${data.enabled ? 'border-purple-100' : 'border-gray-200'}`}>
      <div className={`px-4 py-3 border-b flex justify-between items-center ${data.enabled ? 'bg-purple-50 border-purple-100' : 'bg-gray-50 border-gray-200'}`}>
        <h2 className={`font-bold ${data.enabled ? 'text-purple-800' : 'text-gray-700'}`}>Intraday Equity</h2>
        <div className="flex items-center">
          <span className="text-xs mr-2 text-gray-500">
            {data.enabled ? 'Enabled' : 'Disabled'}
          </span>
          <button
            type="button"
            className={`
              relative inline-flex h-5 w-10 items-center rounded-full
              ${data.enabled ? 'bg-purple-600' : 'bg-gray-300'}
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
          {/* Intraday Trading Strategy */}
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
                  data.modes.includes('opening_range')
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('opening_range')}
              >
                <span className="text-lg mr-2">🔔</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Opening Range</div>
                  <div className="text-xs text-gray-500">First 30min breakouts</div>
                </div>
                {data.modes.includes('opening_range') && (
                  <div className="ml-auto bg-purple-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('trend_following')
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('trend_following')}
              >
                <span className="text-lg mr-2">📊</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Trend Following</div>
                  <div className="text-xs text-gray-500">Intraday momentum</div>
                </div>
                {data.modes.includes('trend_following') && (
                  <div className="ml-auto bg-purple-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
              
              <button
                type="button"
                className={`w-full p-2 rounded-lg border flex items-center ${
                  data.modes.includes('mean_reversion')
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
                onClick={() => handleModeToggle('mean_reversion')}
              >
                <span className="text-lg mr-2">🔄</span>
                <div className="text-left">
                  <div className="font-medium text-sm">Mean Reversion</div>
                  <div className="text-xs text-gray-500">Oversold/overbought</div>
                </div>
                {data.modes.includes('mean_reversion') && (
                  <div className="ml-auto bg-purple-100 rounded-full p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* 🧭 Sector Filter */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                🧭 Sector Filter
              </label>
              <span className="text-xs text-gray-500">
                {data.sectors.length} selected
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {(['IT', 'Auto', 'Pharma', 'FMCG', 'Banking', 'Infra', 'Energy'] as Sector[]).map(sector => (
                <button
                  key={sector}
                  type="button"
                  onClick={() => handleSectorToggle(sector)}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium 
                    ${data.sectors.includes(sector) 
                      ? 'bg-purple-100 text-purple-800 border border-purple-300' 
                      : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                    }`}
                >
                  {data.sectors.includes(sector) ? '☑️' : '☐'} {sector}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500">Restrict scanning to trending sectors only</p>
          </div>

          {/* 🔎 Stock Universe Filter */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                🔎 Stock Universe
              </label>
              <span className="text-xs text-gray-500">
                {data.stock_universe.length} selected
              </span>
            </div>
            <div className="space-y-2">
              {[
                { id: 'nifty50', label: 'NIFTY 50' },
                { id: 'fno', label: 'F&O Listed' },
                { id: 'midcap', label: 'Midcaps' },
                { id: 'penny', label: 'Penny Stocks', disabled: data.smart_filter }
              ].map(item => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleStockUniverseToggle(item.id as StockUniverse)}
                  disabled={item.disabled}
                  className={`flex w-full items-center px-3 py-2 rounded-md text-sm
                    ${data.stock_universe.includes(item.id as StockUniverse)
                      ? 'bg-purple-50 text-purple-800 border border-purple-200'
                      : 'bg-gray-50 text-gray-700 border border-gray-200 hover:bg-gray-100'
                    }
                    ${item.disabled ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <span className="mr-2">
                    {data.stock_universe.includes(item.id as StockUniverse) ? '☑️' : '☐'}
                  </span>
                  {item.label}
                  {item.id === 'penny' && data.smart_filter && (
                    <span className="ml-auto text-red-500">❌ Disabled by Smart Filter</span>
                  )}
                </button>
              ))}
            </div>
            
            {/* Smart Filter Toggle */}
            <div className="flex items-center justify-between mt-2 p-2 bg-gray-50 rounded-md">
              <div>
                <h3 className="text-sm font-medium text-gray-700">Smart Filter</h3>
                <p className="text-xs text-gray-500">Exclude high-risk stocks</p>
              </div>
              <button
                type="button"
                className={`
                  relative inline-flex h-5 w-10 items-center rounded-full
                  ${data.smart_filter ? 'bg-purple-600' : 'bg-gray-200'}
                `}
                onClick={toggleSmartFilter}
              >
                <span
                  className={`
                    inline-block h-4 w-4 transform rounded-full bg-white transition
                    ${data.smart_filter ? 'translate-x-5' : 'translate-x-1'}
                  `}
                />
              </button>
            </div>
          </div>

          {/* Max Stocks Slider */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="block text-sm font-medium text-gray-700">
                Maximum Stocks
              </label>
              <span className="text-sm font-medium text-purple-600">
                {data.max_stocks}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="1"
              value={data.max_stocks}
              onChange={(e) => handleMaxStocksChange(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>1</span>
              <span>3</span>
              <span>5</span>
            </div>
          </div>

          {/* Timeframe */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Timeframe
            </label>
            <div className="grid grid-cols-4 gap-1">
              {(['1m', '5m', '15m', '1h'] as Timeframe[]).map(timeframe => (
                <div
                  key={timeframe}
                  className={`text-xs p-2 rounded text-center cursor-pointer ${
                    data.timeframes.includes(timeframe)
                      ? 'bg-purple-100 text-purple-800 font-medium'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                  onClick={() => handleTimeframeToggle(timeframe)}
                >
                  {timeframe}
                </div>
              ))}
            </div>
          </div>

          {/* Risk Management */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Risk per Trade
            </label>
            <select 
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5"
              value={data.risk_per_trade}
              onChange={handleRiskPerTradeChange}
            >
              <option value="0.5">0.5% of Capital</option>
              <option value="1.0">1.0% of Capital</option>
              <option value="1.5">1.5% of Capital</option>
              <option value="2.0">2.0% of Capital</option>
            </select>
            <p className="text-xs text-gray-500">Maximum risk per intraday trade</p>
          </div>
        </div>
      ) : (
        /* Show message when disabled */
        <div className="p-6 text-center text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm">Intraday equity trading is currently disabled.</p>
          <p className="text-xs mt-2">Toggle the switch above to enable intraday equity trading features.</p>
        </div>
      )}
    </div>
  );
}