import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any

def run_market_open_analysis(data: Union[pd.DataFrame, Dict[str, Any]]):
    """
    Analyze opening market data to identify price range and direction
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Either a DataFrame with OHLCV data or a dictionary with 'candles' key
        
    Returns:
    --------
    dict: Opening analysis information
    """
    # Convert data to DataFrame if it's not already
    if isinstance(data, dict) and 'candles' in data:
        candles = data['candles']
        if not candles or len(candles) < 3:
            return {
                "error": "Insufficient data for opening range analysis"
            }
        
        # Convert candles to DataFrame
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        return {
            "error": "Invalid data format for opening range analysis"
        }
    
    if df.empty or len(df) < 3:
        return {
            "error": "Insufficient data for opening range analysis"
        }
    
    # First 15 minutes (assuming 5-min candles)
    opening_range = df.iloc[:3]  
    
    high = opening_range["high"].max()
    low = opening_range["low"].min()
    open_price = opening_range["open"].iloc[0]
    close_price = opening_range["close"].iloc[2]
    
    # Calculate volatility
    volatility = (high - low) / low * 100
    
    # Volume analysis
    opening_volume = opening_range["volume"].sum()
    avg_daily_volume = df["volume"].mean() * 3  # Comparable 15-min volume
    high_volume_open = opening_volume > avg_daily_volume
    
    # Trend direction with more granularity
    if close_price > high * 0.9975:  # Within 0.25% of high
        direction = "strongly_bullish"
    elif close_price > open_price:
        direction = "bullish"
    elif close_price < low * 1.0025:  # Within 0.25% of low
        direction = "strongly_bearish"
    elif close_price < open_price:
        direction = "bearish"
    else:
        direction = "neutral"
    
    # VWAP relationship (check if vwap column exists)
    if "vwap" in df.columns:
        vwap_current = df["vwap"].iloc[2]
    else:
        # Calculate simplified VWAP if not available
        vwap_current = (df["high"].iloc[2] + df["low"].iloc[2] + df["close"].iloc[2]) / 3
        
    vwap_relation = "above" if close_price > vwap_current else "below"
    vwap_distance = abs(close_price - vwap_current) / vwap_current * 100
    
    return {
        "opening_high": float(high),
        "opening_low": float(low),
        "opening_range_width": float(high - low),
        "volatility_pct": float(volatility),
        "opening_direction": direction,
        "open_close_change_pct": float((close_price - open_price) / open_price * 100),
        "high_volume_opening": bool(high_volume_open),
        "vwap_relation": vwap_relation,
        "vwap_distance_pct": float(vwap_distance),
        "opening_range_time": "first_15min"
    }