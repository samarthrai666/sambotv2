'use client';

import { MarketData } from '../../types/trading';

interface MarketDataBarProps {
  marketData: MarketData | null;
}

export default function MarketDataBar({ marketData }: MarketDataBarProps) {
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
    <div className="bg-white rounded-lg shadow-sm border border-green-100 p-3 mb-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">NIFTY</span>
          <div className="flex items-center">
            <span className="font-bold text-lg">{marketData.nifty.price.toFixed(2)}</span>
            <span className={`ml-2 text-xs ${marketData.nifty.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {marketData.nifty.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.nifty.change).toFixed(2)} ({Math.abs(marketData.nifty.changePercent).toFixed(2)}%)
            </span>
          </div>
        </div>
        
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">BANKNIFTY</span>
          <div className="flex items-center">
            <span className="font-bold text-lg">{marketData.banknifty.price.toFixed(2)}</span>
            <span className={`ml-2 text-xs ${marketData.banknifty.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {marketData.banknifty.change >= 0 ? '▲' : '▼'} {Math.abs(marketData.banknifty.change).toFixed(2)} ({Math.abs(marketData.banknifty.changePercent).toFixed(2)}%)
            </span>
          </div>
        </div>
        
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">Market Status</span>
          <div className="flex items-center">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${marketData.marketStatus === 'open' ? 'bg-green-500' : 'bg-red-500'}`}></span>
            <span className="font-medium capitalize">{marketData.marketStatus}</span>
          </div>
        </div>
        
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">Trading Hours</span>
          <span className="font-medium text-sm">
            {marketData.marketOpenTime.substring(0, 5)} - {marketData.marketCloseTime.substring(0, 5)}
          </span>
        </div>
      </div>
    </div>
  );
}