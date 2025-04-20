from datetime import datetime

def analyze_signal(data, index: str, mode: str):
    # Return a fully mocked signal object — will be replaced by real logic later
    return {
        "signal": "BUY CALL",
        "confidence": 0.91,
        "entry": 17865.50,
        "stop_loss": 17785.25,
        "target": 17985.88,
        "rrr": 1.5,
        "index": index,
        "strike": 17850,
        "trade_time": datetime.now().isoformat(),
        "session": "OPEN",

        "trend": "UPTREND",
        "trend_strength": 0.84,
        "market_regime": "uptrend",
        "volatility_state": "normal",
        "vix": 11.2,

        "indicator_snapshot": {
            "rsi": 38.75,
            "macd": 25.64,
            "macd_signal": 18.92,
            "supertrend_direction": "bullish",
            "ema_9_20_cross": "bullish",
            "price_above_vwap": True
        },

        "volume_analysis": {
            "volume_surge_pct": 32.5,
            "obv_trend": "up"
        },

        "pattern_analysis": {
            "patterns_detected": [
                "Bullish Engulfing (0.92)",
                "Hammer (0.85)"
            ],
            "bullish_patterns": ["bullish_engulfing", "hammer"],
            "bearish_patterns": [],
            "pattern_zone": "support_bounce",
            "pattern_age_bars": 1
        },

        "macro_sentiment": {
            "fii_net_buy": 856.23,
            "delivery_pct": 52.7,
            "option_chain_support_zone": 17800
        },

        "confluence": {
            "with_rsi": True,
            "with_vwap": True,
            "with_supertrend": True,
            "with_volume": True,
            "with_pattern": True,
            "overall_confluence_score": 0.93
        }
    }
