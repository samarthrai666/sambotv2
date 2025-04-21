import pandas as pd

def get_fib_levels(data: pd.DataFrame, mode="intraday") -> dict:
    """
    Calculate Fibonacci retracement levels from recent high/low.
    
    data: OHLCV DataFrame (latest last)
    mode: 'intraday' or 'swing'
    """

    # Use last 30–50 candles (for intraday mode)
    window = 30 if mode == "intraday" else 100
    df = data.tail(window)

    recent_high = df["high"].max()
    recent_low = df["low"].min()

    fib_levels = {}

    # Detect trend
    trend = "uptrend" if recent_high > df.iloc[0]["high"] else "downtrend"

    # Calculate retracement levels (Fib is always high to low)
    if trend == "uptrend":
        diff = recent_high - recent_low
        fib_levels = {
            "0.0%": recent_high,
            "23.6%": recent_high - 0.236 * diff,
            "38.2%": recent_high - 0.382 * diff,
            "50.0%": recent_high - 0.500 * diff,
            "61.8%": recent_high - 0.618 * diff,
            "78.6%": recent_high - 0.786 * diff,
            "100%": recent_low
        }
    else:  # downtrend
        diff = recent_high - recent_low
        fib_levels = {
            "0.0%": recent_low,
            "23.6%": recent_low + 0.236 * diff,
            "38.2%": recent_low + 0.382 * diff,
            "50.0%": recent_low + 0.500 * diff,
            "61.8%": recent_low + 0.618 * diff,
            "78.6%": recent_low + 0.786 * diff,
            "100%": recent_high
        }

    return {
        "trend": trend,
        "swing_high": float(recent_high),
        "swing_low": float(recent_low),
        "retracement_levels": {k: round(v, 2) for k, v in fib_levels.items()}
    }
