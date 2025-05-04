'use client';

import { useState, useEffect } from 'react';
import { MarketData } from '../../types/trading';
import { fetchMarketData } from '../../app/services/api';

interface MarketDataBarProps {
  marketData: MarketData | null;
  refreshInterval?: number; // in milliseconds
}

export default function MarketDataBar({ 
  marketData: initialMarketData, 
  refreshInterval = 60000 // default 5 seconds
}: MarketDataBarProps) {
  const [marketData, setMarketData] = useState<MarketData | null>(initialMarketData);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const refreshMarketData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchMarketData();
      setMarketData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to refresh market data');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Update component state when initialMarketData changes
  useEffect(() => {
    if (initialMarketData) {
      setMarketData(initialMarketData);
    }
  }, [initialMarketData]);

  useEffect(() => {
    // Skip setting up interval if refreshInterval is 0 or negative
    if (!refreshInterval || refreshInterval <= 0) {
      return;
    }
    
    // Only auto-refresh if market is open and refresh interval is positive
    if (marketData?.marketStatus === 'open') {
      console.log(`MarketDataBar: Setting up refresh interval of ${refreshInterval}ms`);
      const intervalId = setInterval(refreshMarketData, refreshInterval);
      return () => {
        console.log('MarketDataBar: Clearing refresh interval');
        clearInterval(intervalId);
      };
    }
  }, [marketData?.marketStatus, refreshInterval]);

  // Handle manual refresh
  const handleManualRefresh = (e: React.MouseEvent) => {
    e.preventDefault();
    refreshMarketData();
  };

  // Loading skeleton
  if (!marketData) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-green-100 p-3 mb-6 animate-pulse">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-green-100 p-3 mb-6 relative">
      {/* Loading indicator overlay */}
      {isLoading && (
        <div className="absolute top-0 right-0 mt-1 mr-1">
          <div className="animate-spin w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full"></div>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="absolute top-0 right-0 mt-1 mr-6 bg-red-100 text-red-600 text-xs px-2 py-1 rounded">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* NIFTY data */}
        <div className="flex flex-col">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">NIFTY</span>
          </div>
          <div className="flex items-center">
            <span className="font-bold text-lg">{marketData.nifty.price.toFixed(2)}</span>
            <span className={`ml-2 text-xs ${marketData.nifty.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {marketData.nifty.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.nifty.change).toFixed(2)} ({Math.abs(marketData.nifty.changePercent).toFixed(2)}%)
            </span>
          </div>
        </div>
        
        {/* BANKNIFTY data */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">BANKNIFTY</span>
          <div className="flex items-center">
            <span className="font-bold text-lg">{marketData.banknifty.price.toFixed(2)}</span>
            <span className={`ml-2 text-xs ${marketData.banknifty.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {marketData.banknifty.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.banknifty.change).toFixed(2)} ({Math.abs(marketData.banknifty.changePercent).toFixed(2)}%)
            </span>
          </div>
        </div>
        
        {/* Market Status */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">Market Status</span>
          <div className="flex items-center">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${marketData.marketStatus === 'open' ? 'bg-green-500' : 'bg-red-500'}`}></span>
            <span className="font-medium capitalize">{marketData.marketStatus}</span>
          </div>
        </div>
        
        {/* Trading Hours + Refresh Button */}
        <div className="flex flex-col">
          <div className="flex justify-between items-center">
            <span className="text-xs text-gray-500">Trading Hours</span>
            <button
              onClick={handleManualRefresh}
              className="text-xs text-green-600 hover:text-green-800"
              disabled={isLoading}
            >
              Refresh
            </button>
          </div>
          <span className="font-medium text-sm">
            {marketData.marketOpenTime.substring(0, 5)} - {marketData.marketCloseTime.substring(0, 5)}
          </span>
        </div>
      </div>
      
      {/* Extra Data Row - can be conditionally rendered */}
      {marketData.marketStatus === 'open' && (
        <div className="mt-2 pt-2 border-t border-gray-100 grid grid-cols-3 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Session Time:</span>
            <span className="ml-1 font-medium">
              {formatSessionTime(marketData.serverTime, marketData.marketOpenTime, marketData.marketCloseTime)}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Auto-Refresh:</span>
            <span className="ml-1 font-medium">
              Every {1000 / 1000}s
            </span>
          </div>
          <div>
            <span className="text-gray-500">Last Updated:</span>
            <span className="ml-1 font-medium">
              {lastUpdated.toLocaleTimeString()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper function to format session time
function formatSessionTime(serverTime: string, openTime: string, closeTime: string): string {
  const now = new Date(serverTime);
  
  // Parse open and close times
  const [openHour, openMin] = openTime.split(':').map(Number);
  const [closeHour, closeMin] = closeTime.split(':').map(Number);
  
  // Create Date objects for open and close times
  const marketOpen = new Date(now);
  marketOpen.setHours(openHour, openMin, 0);
  
  const marketClose = new Date(now);
  marketClose.setHours(closeHour, closeMin, 0);
  
  // Calculate elapsed time
  if (now < marketOpen) {
    return 'Pre-market';
  } else if (now > marketClose) {
    return 'Post-market';
  } else {
    // During market hours
    const elapsedMs = now.getTime() - marketOpen.getTime();
    const elapsedMinutes = Math.floor(elapsedMs / (1000 * 60));
    const hours = Math.floor(elapsedMinutes / 60);
    const mins = elapsedMinutes % 60;
    return `${hours}h ${mins}m elapsed`;
  }
}