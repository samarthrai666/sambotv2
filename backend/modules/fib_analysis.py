import pandas as pd
from typing import Dict, Union, Any

def get_fib_levels(data: Union[pd.DataFrame, Dict[str, Any]], mode: str = "intraday") -> Dict:
    """
    Calculate Fibonacci retracement levels from recent high/low.
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Either a DataFrame with OHLCV data or a dictionary with 'candles' key
    mode : str
        'intraday' or 'swing'
        
    Returns:
    --------
    Dict: Dictionary with trend and Fibonacci levels
    """
    try:
        # Convert data to DataFrame if it's not already
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            if not candles or len(candles) < 10:  # Need sufficient history
                return {
                    "trend": "neutral",
                    "swing_high": 0,
                    "swing_low": 0,
                    "retracement_levels": {},
                    "error": "Insufficient data for Fibonacci analysis"
                }
            
            # Convert candles to DataFrame
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return {
                "trend": "neutral",
                "swing_high": 0,
                "swing_low": 0,
                "retracement_levels": {},
                "error": "Invalid data format for Fibonacci analysis"
            }

        # Use last 30–50 candles (for intraday mode)
        window = 30 if mode == "intraday" else 100
        df_window = df.tail(min(window, len(df)))

        recent_high = df_window["high"].max()
        recent_low = df_window["low"].min()

        # Detect trend
        trend = "uptrend" if recent_high > df_window.iloc[0]["high"] else "downtrend"

        # Calculate retracement levels (Fib is always high to low)
        fib_levels = {}
        diff = recent_high - recent_low

        if trend == "uptrend":
            fib_levels = {
                "0.0%": float(recent_high),
                "23.6%": float(recent_high - 0.236 * diff),
                "38.2%": float(recent_high - 0.382 * diff),
                "50.0%": float(recent_high - 0.500 * diff),
                "61.8%": float(recent_high - 0.618 * diff),
                "78.6%": float(recent_high - 0.786 * diff),
                "100%": float(recent_low)
            }
        else:  # downtrend
            fib_levels = {
                "0.0%": float(recent_low),
                "23.6%": float(recent_low + 0.236 * diff),
                "38.2%": float(recent_low + 0.382 * diff),
                "50.0%": float(recent_low + 0.500 * diff),
                "61.8%": float(recent_low + 0.618 * diff),
                "78.6%": float(recent_low + 0.786 * diff),
                "100%": float(recent_high)
            }

        return {
            "trend": trend,
            "swing_high": float(recent_high),
            "swing_low": float(recent_low),
            "retracement_levels": fib_levels
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "trend": "neutral",
            "swing_high": 0,
            "swing_low": 0,
            "retracement_levels": {},
            "error": str(e)
        }