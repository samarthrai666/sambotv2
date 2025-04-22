from datetime import datetime
import pandas as pd
from modules.build_final_signal import build_final_signal

def analyze_signal(data, index: str, mode: str):
    """
    Analyzes market data to generate real-time trading signals.
    
    Parameters:
    -----------
    data : dict
        Dictionary containing candle data from fetch_data.py
    index : str
        Index being analyzed (NIFTY or BANKNIFTY)
    mode : str
        Trading mode (scalp, swing, longterm)
        
    Returns:
    --------
    dict: Signal analysis with entry, target, stop_loss and other metrics
    """
    try:
        if not data or 'candles' not in data or not data['candles'] or len(data['candles']) < 20:
            print(f"[WARNING] Insufficient data for {index} {mode} analysis")
            return None

        candles = data['candles']
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        data['df'] = df

        signal_data = build_final_signal(data, index, mode)

        final_decision = signal_data.get("final_decision", "SKIP")
        ml_signal = signal_data.get("ml_prediction", {}).get("ml_signal", "HOLD")
        signal_type = final_decision if final_decision != "SKIP" else ml_signal

        trend_info = signal_data.get("primary_trend", {})
        trend = trend_info.get("trend", "NEUTRAL")
        trend_strength = trend_info.get("strength", 0.5)

        indicators = signal_data.get("indicators", {})
        patterns = signal_data.get("patterns", {}).get("pattern_summary", {})
        bullish_patterns = patterns.get("bullish_patterns", [])
        bearish_patterns = patterns.get("bearish_patterns", [])
        detected_patterns = bullish_patterns + bearish_patterns

        current_price = candles[-1][4] if candles else 0

        zones = signal_data.get("zones", {})
        support_levels = zones.get("support", [])
        resistance_levels = zones.get("resistance", [])
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else current_price * 0.99
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else current_price * 1.01

        if signal_type in ["BUY", "BUY CALL", "LONG"]:
            target_price = nearest_resistance
            stop_loss = nearest_support if nearest_support < current_price else current_price * 0.995
        elif signal_type in ["SELL", "SELL CALL", "SHORT"]:
            target_price = nearest_support
            stop_loss = nearest_resistance if nearest_resistance > current_price else current_price * 1.005
        else:
            target_price = current_price * 1.01
            stop_loss = current_price * 0.99

        risk = abs(current_price - stop_loss)
        reward = abs(target_price - current_price)
        rrr = round(reward / risk, 2) if risk > 0 else 0

        def extract_confidence(p):
            if "(" in p and ")" in p:
                try:
                    return float(p.split("(")[1].split(")")[0])
                except:
                    return 0.85
            return 0.85

        patterns_detected = [
            f"{p.split('(')[0].strip()} ({extract_confidence(p):.2f})" for p in detected_patterns[:3]
        ]

        def safe_last(val):
            return val.iloc[-1] if hasattr(val, 'iloc') else val

        signal = {
            "signal": signal_type,
            "confidence": signal_data.get("confidence_score", 0.7),
            "entry": current_price,
            "stop_loss": stop_loss,
            "target": target_price,
            "rrr": rrr,
            "index": index,
            "strike": round(current_price / 50) * 50,
            "trade_time": datetime.now().isoformat(),
            "session": "OPEN",

            "trend": trend,
            "trend_strength": trend_strength,
            "market_regime": trend.lower(),
            "volatility_state": "high" if trend_strength > 0.8 else "normal",
            "vix": indicators.get("vix", 14.5),

            "indicator_snapshot": {
                "rsi": indicators.get("rsi_14", 50),
                "macd": indicators.get("macd", 0),
                "macd_signal": indicators.get("macd_signal", 0),
                "supertrend_direction": "bullish" if "up" in trend.lower() else "bearish",
                "ema_9_20_cross": "bullish" if safe_last(indicators.get("ema_9", 0)) > safe_last(indicators.get("ema_20", 0)) else "bearish",
                "price_above_vwap": current_price > indicators.get("vwap", 0)
            },

            "volume_analysis": {
                "volume_surge_pct": indicators.get("rel_volume", 1) * 100 - 100,
                "obv_trend": "up" if safe_last(indicators.get("obv", 0)) > 0 else "down"
            },

            "pattern_analysis": {
                "patterns_detected": patterns_detected,
                "bullish_patterns": [p.lower().replace(" ", "_") for p in bullish_patterns][:3],
                "bearish_patterns": [p.lower().replace(" ", "_") for p in bearish_patterns][:3],
                "pattern_zone": "support_bounce" if "up" in trend.lower() else "resistance_rejection",
                "pattern_age_bars": 1
            },

            "macro_sentiment": {
                "fii_net_buy": signal_data.get("fii_dii", {}).get("fii", {}).get("net_value", 0),
                "delivery_pct": 50,
                "option_chain_support_zone": signal_data.get("option_chain", {}).get("max_pain", {}).get("price", nearest_support)
            },

            "confluence": {
                "with_rsi": indicators.get("rsi_14", 50) > 50 if signal_type.startswith("BUY") else indicators.get("rsi_14", 50) < 50,
                "with_vwap": current_price > indicators.get("vwap", 0) if signal_type.startswith("BUY") else current_price < indicators.get("vwap", 0),
                "with_supertrend": "up" in trend.lower() if signal_type.startswith("BUY") else "down" in trend.lower(),
                "with_volume": indicators.get("rel_volume", 1) > 1.1,
                "with_pattern": len(patterns_detected) > 0,
                "overall_confluence_score": signal_data.get("confidence_score", 0.7)
            },

            "_comprehensive_analysis": signal_data
        }

        return signal

    except Exception as e:
        print(f"[ERROR] Signal analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
