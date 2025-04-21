import pandas as pd
import numpy as np
from typing import Dict, Union, Any

def analyze_momentum(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict:
    """
    Analyze price momentum using various indicators
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Either a DataFrame with OHLCV data or a dictionary with 'candles' key
        
    Returns:
    --------
    dict: Momentum analysis results
    """
    try:
        # Convert data to DataFrame if it's not already
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            if not candles or len(candles) < 10:  # Need sufficient history
                return {
                    "momentum_score": 50,
                    "momentum_signal": "neutral",
                    "error": "Insufficient data for momentum analysis"
                }
            
            # Convert candles to DataFrame
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return {
                "momentum_score": 50,
                "momentum_signal": "neutral",
                "error": "Invalid data format for momentum analysis"
            }
        
        # Check if we have enough data
        if df.empty or len(df) < 14:
            return {
                "momentum_score": 50,
                "momentum_signal": "neutral",
                "error": "Insufficient data points for analysis"
            }
        
        # Calculate price change percentage
        price_change_pct = (df['close'].iloc[-1] / df['close'].iloc[-10] - 1) * 100
        
        # Calculate simple momentum indicators
        
        # 1. Rate of Change (ROC)
        roc_5 = (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100
        roc_10 = (df['close'].iloc[-1] / df['close'].iloc[-11] - 1) * 100
        roc_20 = (df['close'].iloc[-1] / df['close'].iloc[-21] - 1) * 100 if len(df) >= 21 else 0
        
        # 2. Simple RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # 3. Simple MACD calculation
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = macd_histogram.iloc[-1]
        
        # 4. Volume analysis
        avg_volume = df['volume'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else df['volume'].mean()
        current_volume = df['volume'].iloc[-1]
        volume_surge = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Combine indicators into a momentum score (0-100)
        momentum_score = 50  # Start at neutral
        
        # Adjust based on RSI
        if current_rsi > 70:
            momentum_score += 20
        elif current_rsi > 60:
            momentum_score += 10
        elif current_rsi < 30:
            momentum_score -= 20
        elif current_rsi < 40:
            momentum_score -= 10
        
        # Adjust based on MACD
        if current_macd > current_signal and current_histogram > 0:
            momentum_score += 15
        elif current_macd < current_signal and current_histogram < 0:
            momentum_score -= 15
        
        # Adjust based on price change
        if price_change_pct > 5:
            momentum_score += 10
        elif price_change_pct > 2:
            momentum_score += 5
        elif price_change_pct < -5:
            momentum_score -= 10
        elif price_change_pct < -2:
            momentum_score -= 5
        
        # Volume surge adjustment
        if volume_surge > 2 and price_change_pct > 0:
            momentum_score += 5
        elif volume_surge > 2 and price_change_pct < 0:
            momentum_score -= 5
        
        # Ensure score is within 0-100 range
        momentum_score = max(0, min(100, momentum_score))
        
        # Determine momentum signal
        if momentum_score >= 80:
            momentum_signal = "strongly_bullish"
        elif momentum_score >= 60:
            momentum_signal = "bullish"
        elif momentum_score <= 20:
            momentum_signal = "strongly_bearish"
        elif momentum_score <= 40:
            momentum_signal = "bearish"
        else:
            momentum_signal = "neutral"
        
        return {
            "momentum_score": float(momentum_score),
            "momentum_signal": momentum_signal,
            "rsi": float(current_rsi),
            "macd": float(current_macd),
            "macd_signal": float(current_signal),
            "macd_histogram": float(current_histogram),
            "price_change_pct": float(price_change_pct),
            "volume_surge": float(volume_surge),
            "roc_5": float(roc_5),
            "roc_10": float(roc_10),
            "roc_20": float(roc_20)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "momentum_score": 50,
            "momentum_signal": "neutral",
            "error": str(e)
        }