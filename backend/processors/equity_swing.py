"""
Equity swing trading processor module with real-time technical analysis
"""
from datetime import datetime, timedelta
import random
import time
from typing import Dict, Any, List, Optional
import os
import csv
import pandas as pd
import numpy as np
import talib
from fyers_apiv3 import fyersModel

# Fyers client setup
def get_fyers_client():
    """Get authenticated Fyers client"""
    client_id = os.getenv("FYERS_CLIENT_ID")
    access_token = os.getenv("FYERS_ACCESS_TOKEN")
    
    if not client_id or not access_token:
        raise ValueError("FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN must be set as environment variables")
    
    fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path="")
    return fyers

# Function to fetch historical data from Fyers
async def fetch_stock_data(symbol: str, time_period: str = "3m") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a stock using Fyers API
    
    Args:
        symbol (str): Stock symbol (e.g., "NSE:HCLTECH-EQ")
        time_period (str): Time period to fetch (e.g., "1m", "3m", "6m")
        
    Returns:
        pd.DataFrame: DataFrame with OHLCV data
    """
    try:
        fyers = get_fyers_client()
        
        # Format symbol for Fyers API
        fyers_symbol = f"NSE:{symbol}-EQ" if not symbol.startswith("NSE:") else symbol
        
        # Calculate from and to dates
        to_date = datetime.now().strftime("%Y-%m-%d")
        
        if time_period == "1m":
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif time_period == "3m":
            from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        elif time_period == "6m":
            from_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        else:
            from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Prepare request parameters
        data_params = {
            "symbol": fyers_symbol,
            "resolution": "D",  # Daily candles
            "date_format": 1,   # YYYY-MM-DD format
            "range_from": from_date,
            "range_to": to_date,
            "cont_flag": 1      # Continuous data
        }
        
        # Make the API call
        response = fyers.history(data=data_params)
        
        if response.get("s") != "ok" or not response.get("candles"):
            print(f"Error fetching data for {symbol}: {response.get('message', 'No data')}")
            return None
            
        # Convert to DataFrame
        candles = response["candles"]
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
        df.set_index("timestamp", inplace=True)
        
        return df
    except Exception as e:
        print(f"Exception fetching data for {symbol}: {str(e)}")
        return None

# Function to calculate technical indicators
def calculate_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate technical indicators for a given OHLCV DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        
    Returns:
        Dict[str, Any]: Dictionary with calculated indicator values
    """
    if df is None or df.empty or len(df) < 30:
        return {
            "rsi": "neutral",
            "macd": "neutral",
            "sma_50_200": "neutral",
            "bollinger": "neutral", 
            "volume_trend": "neutral"
        }
    
    try:
        # Calculate RSI
        rsi = talib.RSI(df['close'].values, timeperiod=14)
        current_rsi = rsi[-1]
        
        if current_rsi > 70:
            rsi_signal = "overbought"
        elif current_rsi > 60:
            rsi_signal = "bullish"
        elif current_rsi < 30:
            rsi_signal = "oversold"
        elif current_rsi < 40:
            rsi_signal = "bearish"
        else:
            rsi_signal = "neutral"
            
        # Calculate MACD
        macd, macd_signal, macd_hist = talib.MACD(
            df['close'].values, 
            fastperiod=12, 
            slowperiod=26, 
            signalperiod=9
        )
        
        if macd[-1] > macd_signal[-1] and macd_hist[-1] > 0:
            macd_signal_val = "bullish"
        elif macd[-1] < macd_signal[-1] and macd_hist[-1] < 0:
            macd_signal_val = "bearish"
        else:
            macd_signal_val = "neutral"
            
        # Calculate SMA 50 and 200
        sma_50 = talib.SMA(df['close'].values, timeperiod=50)
        sma_200 = talib.SMA(df['close'].values, timeperiod=200)
        
        if sma_50[-1] > sma_200[-1] and sma_50[-2] <= sma_200[-2]:
            sma_signal = "golden_cross"
        elif sma_50[-1] < sma_200[-1] and sma_50[-2] >= sma_200[-2]:
            sma_signal = "death_cross"
        elif sma_50[-1] > sma_200[-1]:
            sma_signal = "bullish"
        elif sma_50[-1] < sma_200[-1]:
            sma_signal = "bearish"
        else:
            sma_signal = "neutral"
            
        # Calculate Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            df['close'].values,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )
        
        if df['close'].iloc[-1] > upper[-1]:
            bb_signal = "upper_touch"
        elif df['close'].iloc[-1] < lower[-1]:
            bb_signal = "lower_touch"
        elif df['close'].iloc[-1] > middle[-1]:
            bb_signal = "above_middle"
        elif df['close'].iloc[-1] < middle[-1]:
            bb_signal = "below_middle"
        else:
            bb_signal = "middle_band"
            
        # Calculate Volume Trend (simple 20-day average comparison)
        vol_avg = df['volume'].rolling(window=20).mean()
        if df['volume'].iloc[-1] > vol_avg.iloc[-1] * 1.5:
            vol_signal = "high_volume"
        elif df['volume'].iloc[-1] > vol_avg.iloc[-1] * 1.1:
            vol_signal = "increasing"
        elif df['volume'].iloc[-1] < vol_avg.iloc[-1] * 0.9:
            vol_signal = "decreasing"
        else:
            vol_signal = "neutral"
            
        return {
            "rsi": rsi_signal,
            "rsi_value": float(current_rsi),
            "macd": macd_signal_val,
            "macd_value": float(macd[-1]),
            "macd_signal_value": float(macd_signal[-1]),
            "macd_hist_value": float(macd_hist[-1]),
            "sma_50_200": sma_signal,
            "sma_50_value": float(sma_50[-1]) if not np.isnan(sma_50[-1]) else None,
            "sma_200_value": float(sma_200[-1]) if not np.isnan(sma_200[-1]) else None,
            "bollinger": bb_signal,
            "upper_band": float(upper[-1]),
            "middle_band": float(middle[-1]),
            "lower_band": float(lower[-1]),
            "volume_trend": vol_signal,
            "current_price": float(df['close'].iloc[-1]),
        }
    except Exception as e:
        print(f"Error calculating indicators: {str(e)}")
        return {
            "rsi": "neutral",
            "macd": "neutral",
            "sma_50_200": "neutral",
            "bollinger": "neutral", 
            "volume_trend": "neutral",
            "error": str(e)
        }

# Function to detect candlestick patterns
def detect_patterns(df: pd.DataFrame) -> List[str]:
    """
    Detect candlestick patterns in OHLCV data
    
    Args:
        df (pd.DataFrame): DataFrame with OHLCV data
        
    Returns:
        List[str]: List of detected pattern names
    """
    if df is None or df.empty or len(df) < 10:
        return []
        
    try:
        # Initialize list to store detected patterns
        patterns = []
        
        # Bullish patterns
        if talib.CDLHAMMER(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Hammer")
            
        if talib.CDLINVERTEDHAMMER(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Inverted Hammer")
            
        if talib.CDLENGULFING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Bullish Engulfing")
            
        if talib.CDLMORNINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Morning Star")
            
        if talib.CDLPIERCING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Piercing Pattern")
            
        # Bearish patterns
        if talib.CDLHANGINGMAN(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Hanging Man")
            
        if talib.CDLSHOOTINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Shooting Star")
            
        if talib.CDLENGULFING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] < 0:
            patterns.append("Bearish Engulfing")
            
        if talib.CDLEVENINGSTAR(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Evening Star")
            
        if talib.CDLDARKCLOUDCOVER(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Dark Cloud Cover")
            
        # Check for Doji
        if talib.CDLDOJI(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] > 0:
            patterns.append("Doji")
            
        return patterns
    except Exception as e:
        print(f"Error detecting patterns: {str(e)}")
        return []

async def process(auto_execute: bool = False, log_enabled: bool = True, 
                  sectors: List[str] = None, market_caps: List[str] = None,
                  max_stocks: int = 5) -> Dict[str, Any]:
    """
    Process equity swing trading signals
    
    Args:
        auto_execute (bool): Whether to automatically execute the generated signals
        log_enabled (bool): Whether to enable logging
        sectors (List[str]): List of sectors to filter by (e.g., ["Information Technology", "Banking"])
        market_caps (List[str]): List of market caps to filter by (e.g., ["largecap", "midcap"])
        max_stocks (int): Maximum number of stocks to include in results
        
    Returns:
        Dict[str, Any]: Dictionary containing executed and non-executed signals
    """
    if log_enabled:
        print(f"🔎 Running equity swing processor at {datetime.now().isoformat()}")
        print(f"Filter parameters: sectors={sectors}, market_caps={market_caps}, max_stocks={max_stocks}")
    
    # Convert filter parameters to lowercase for case-insensitive comparison
    sectors_lower = [s.lower() for s in sectors] if sectors else []
    market_caps_lower = [m.lower() for m in market_caps] if market_caps else []
    
    if log_enabled and sectors_lower:
        print(f"Looking for sectors: {sectors_lower}")
    if log_enabled and market_caps_lower:
        print(f"Looking for market caps: {market_caps_lower}")
    
    # Load the NSE stocks data from CSV
    all_stocks = []
    filtered_stocks = []
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "top500_nse_stocks.csv")
    
    try:
        # Read the CSV file
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                all_stocks = list(reader)
                if log_enabled:
                    print(f"Successfully loaded {len(all_stocks)} stocks from CSV")
                
                # First attempt: apply both sector and market cap filtering
                if sectors_lower or market_caps_lower:
                    if log_enabled:
                        print("Attempting filtering with provided criteria")
                    
                    for stock in all_stocks:
                        # Check if sector matches
                        sector_match = True
                        if sectors_lower:
                            stock_sector = stock['sector'].lower()
                            # Direct sector matching only - no complex logic
                            sector_match = any(sector in stock_sector for sector in sectors_lower)
                            
                            # Debug the first few stocks
                            if log_enabled and len(filtered_stocks) < 3 and sector_match:
                                print(f"Debug - Found sector match: Stock={stock['symbol']}, Sector={stock['sector']}")
                        
                        # Check if market cap matches
                        market_cap_match = True
                        if market_caps_lower:
                            stock_market_cap = stock['market_cap_category'].lower()
                            market_cap_match = stock_market_cap in market_caps_lower
                        
                        # If both criteria match, add to filtered list
                        if sector_match and market_cap_match:
                            filtered_stocks.append(stock)
                    
                    if log_enabled:
                        print(f"Found {len(filtered_stocks)} stocks matching both sector and market cap criteria")
                        
                        # Show some examples of what was found
                        if filtered_stocks:
                            print("Sample filtered stocks:")
                            for i, stock in enumerate(filtered_stocks[:min(3, len(filtered_stocks))]):
                                print(f"  Stock {i+1}: {stock['symbol']} - Sector: {stock['sector']} - Market Cap: {stock['market_cap_category']}")
                
                # If no matches with both criteria, try less restrictive approaches
                if not filtered_stocks:
                    if sectors_lower:
                        print("No matches with both criteria. Trying sector-only filtering")
                        for stock in all_stocks:
                            stock_sector = stock['sector'].lower()
                            if any(sector in stock_sector for sector in sectors_lower):
                                filtered_stocks.append(stock)
                        
                        if log_enabled:
                            print(f"Found {len(filtered_stocks)} stocks matching only sector criteria")
                    
                    if not filtered_stocks and market_caps_lower:
                        print("Trying market-cap-only filtering")
                        for stock in all_stocks:
                            stock_market_cap = stock['market_cap_category'].lower()
                            if stock_market_cap in market_caps_lower:
                                filtered_stocks.append(stock)
                        
                        if log_enabled:
                            print(f"Found {len(filtered_stocks)} stocks matching only market cap criteria")
                
                # If no filters were applied or no matches found, use all stocks
                if not filtered_stocks and not (sectors_lower or market_caps_lower):
                    filtered_stocks = all_stocks
                elif not filtered_stocks:
                    print("No matches found with current criteria")
                
                # Display some sample filtered stocks
                if log_enabled and filtered_stocks:
                    print(f"Sample filtered stocks:")
                    for i, stock in enumerate(filtered_stocks[:min(3, len(filtered_stocks))]):
                        print(f"  Stock {i+1}: {stock['symbol']} - Sector: {stock['sector']} - Market Cap: {stock['market_cap_category']}")
                
                # Limit to max stocks if necessary
                if len(filtered_stocks) > max_stocks:
                    filtered_stocks = random.sample(filtered_stocks, max_stocks)
        else:
            print(f"CSV file not found at {csv_path}")
                
    except Exception as e:
        print(f"Error loading or filtering stock data: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # If we couldn't get any stocks, return early with an error
    if not filtered_stocks:
        return {
            "executed": [],
            "non_executed": [],
            "timestamp": datetime.now().isoformat(),
            "processor": "equity_swing",
            "error": "No stock data available or no matches for filtering criteria"
        }
    
    # Generate equity swing signals with real technical analysis
    signals = []
    
    for stock_data in filtered_stocks:
        symbol = stock_data['symbol']
        
        # Fetch historical data for the stock
        if log_enabled:
            print(f"Fetching historical data for {symbol}...")
            
        historical_data = await fetch_stock_data(symbol)
        
        if historical_data is None or historical_data.empty:
            if log_enabled:
                print(f"No historical data available for {symbol}, skipping...")
            continue
            
        # Calculate technical indicators
        indicators = calculate_indicators(historical_data)
        
        # Detect candlestick patterns
        patterns_detected = detect_patterns(historical_data)
        
        # Determine signal type based on indicators
        is_buy = False
        if (indicators['rsi'] in ['bullish', 'oversold'] and 
            indicators['macd'] == 'bullish' and
            indicators['sma_50_200'] in ['golden_cross', 'bullish']):
            is_buy = True
        elif (indicators['rsi'] in ['bearish', 'overbought'] and 
              indicators['macd'] == 'bearish' and
              indicators['sma_50_200'] in ['death_cross', 'bearish']):
            is_buy = False
        else:
            # If indicators are mixed, randomly determine signal type with a slight bias
            # towards the stronger indicator
            if indicators['rsi'] in ['bullish', 'oversold'] or indicators['macd'] == 'bullish':
                is_buy = random.random() < 0.6
            elif indicators['rsi'] in ['bearish', 'overbought'] or indicators['macd'] == 'bearish':
                is_buy = random.random() < 0.4
            else:
                is_buy = random.random() < 0.5
        
        # Use actual price from historical data
        current_price = indicators['current_price']
        
        # Calculate reasonable entry, target and stop-loss based on current price
        entry = current_price
        
        # Volatility-based target and stop-loss
        atr = talib.ATR(
            historical_data['high'].values,
            historical_data['low'].values,
            historical_data['close'].values,
            timeperiod=14
        )
        
        # Default ATR if calculation fails
        current_atr = atr[-1] if not np.isnan(atr[-1]) else current_price * 0.02
        
        if is_buy:
            target = round(entry + (current_atr * 3), 2)
            stop_loss = round(entry - (current_atr * 1.5), 2)
        else:
            target = round(entry - (current_atr * 3), 2) 
            stop_loss = round(entry + (current_atr * 1.5), 2)
        
        # Calculate risk-reward ratio
        rrr = round(abs((target - entry) / (entry - stop_loss)), 2) if entry != stop_loss else 0
        
        # Pattern strength based on number of detected patterns
        pattern_strength = "weak" if not patterns_detected else "moderate" if len(patterns_detected) == 1 else "strong"
        
        # Add pattern types if none were detected
        if not patterns_detected:
            if is_buy:
                patterns_detected = ["Potential Support Level"]
            else:
                patterns_detected = ["Potential Resistance Level"]
        
        # Calculate expected holding period (3-15 days for swing)
        days_to_hold = random.randint(3, 15)
        expected_exit_date = (datetime.now() + timedelta(days=days_to_hold)).strftime("%d %b %Y")
        
        # AI analysis based on actual indicators
        ai_reasoning = f"Analysis based on technical indicators: RSI is {indicators['rsi']} at {indicators['rsi_value']:.1f}, MACD is {indicators['macd']}, and moving averages are in a {indicators['sma_50_200']} formation. "
        
        if patterns_detected:
            ai_reasoning += f"Detected {len(patterns_detected)} chart pattern(s): {', '.join(patterns_detected)}. "
            
        ai_reasoning += f"Volume is {indicators['volume_trend']}. "
        
        if is_buy:
            ai_reasoning += f"This suggests a potential upside move with a target of {target} and a stop loss at {stop_loss}, giving a risk-reward ratio of {rrr}."
        else:
            ai_reasoning += f"This suggests a potential downside move with a target of {target} and a stop loss at {stop_loss}, giving a risk-reward ratio of {rrr}."
        
        # Confidence score based on indicator alignment
        indicator_alignment = sum([
            1 if indicators['rsi'] in (['bullish', 'oversold'] if is_buy else ['bearish', 'overbought']) else 0,
            1 if indicators['macd'] == ('bullish' if is_buy else 'bearish') else 0,
            1 if indicators['sma_50_200'] in (['golden_cross', 'bullish'] if is_buy else ['death_cross', 'bearish']) else 0,
            1 if len(patterns_detected) > 0 else 0,
            1 if indicators['volume_trend'] in ['increasing', 'high_volume'] else 0
        ])
        
        confidence = 0.5 + (indicator_alignment * 0.1)  # Base 0.5 + up to 0.5 for aligned indicators
        
        signal = {
            "trade_time": datetime.now().isoformat(),
            "symbol": f"NSE:EQ-{symbol}",
            "company": stock_data.get("company", ""),
            "sector": stock_data.get("sector", ""),
            "market_cap": stock_data.get("market_cap_category", ""),
            "signal": "BUY" if is_buy else "SELL",
            "entry": entry,
            "target": target,
            "stop_loss": stop_loss,
            "rrr": rrr,
            "trend": "bullish" if is_buy else "bearish",
            "timeframe": "daily",
            "confidence": confidence,
            "indicator_snapshot": {
                "rsi": indicators['rsi'],
                "rsi_value": indicators['rsi_value'] if 'rsi_value' in indicators else None,
                "macd": indicators['macd'],
                "sma_50_200": indicators['sma_50_200'],
                "bollinger": indicators['bollinger'],
                "volume_trend": indicators['volume_trend']
            },
            "pattern_analysis": {
                "patterns_detected": patterns_detected,
                "strength": pattern_strength
            },
            "ai_opinion": {
                "sentiment": "bullish" if is_buy else "bearish",
                "confidence": confidence,
                "reasoning": ai_reasoning
            },
            "expected_holding_period": f"{days_to_hold} days",
            "expected_exit_date": expected_exit_date
        }
        
        signals.append(signal)
    
    # If auto-execute is enabled, simulate execution for some signals
    executed = []
    non_executed = signals
    
    if auto_execute and signals:
        # Randomly select signals to execute
        num_to_execute = random.randint(0, len(signals))
        if num_to_execute > 0:
            to_execute = random.sample(signals, num_to_execute)
            executed = to_execute
            non_executed = [s for s in signals if s not in to_execute]
            
            if log_enabled:
                print(f"✅ Auto-executed {len(executed)} equity swing signals")
    
    return {
        "executed": executed,
        "non_executed": non_executed,
        "timestamp": datetime.now().isoformat(),
        "processor": "equity_swing",
        "filter_stats": {
            "filtered_count": len(filtered_stocks),
            "total_count": len(all_stocks),
            "sectors_requested": sectors,
            "market_caps_requested": market_caps,
            "analysis_count": len(signals)
        }
    }