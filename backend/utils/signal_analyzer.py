from datetime import datetime
import json
import pandas as pd
import numpy as np
from modules.build_final_signal import build_final_signal

def analyze_signal(data, index: str, mode: str):
    """
    Analyzes market data to generate real-time trading signals.
    Replaces the mock data with actual analysis by calling build_final_signal.
    
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
        # Check if we have valid data
        if not data or 'candles' not in data or not data['candles'] or len(data['candles']) < 20:
            print(f"[WARNING] Insufficient data for {index} {mode} analysis")
            return None
        
        # Convert candles to DataFrame for analysis if needed
        # (build_final_signal will handle this, but we'll prepare it here just in case)
        if isinstance(data['candles'], list) and not isinstance(data, pd.DataFrame):
            candles = data['candles']
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
            # Keep the original data structure, but add the DataFrame for modules that expect it
            data['df'] = df
        
        # Get comprehensive analysis from build_final_signal module
        comprehensive_signal = build_final_signal(data, index, mode)
        
        # Extract key data from comprehensive analysis to maintain compatibility
        # with the expected signal structure in the rest of the application
        
        # Determine signal type based on final decision
        signal_type = comprehensive_signal.get("final_decision", "SKIP")
        if signal_type == "SKIP":
            # Fall back to ML prediction if available
            ml_prediction = comprehensive_signal.get("ml_prediction", {})
            signal_type = ml_prediction.get("ml_signal", "HOLD")
        
        # Get trend info
        trend_info = comprehensive_signal.get("primary_trend", {})
        trend = trend_info.get("trend", "NEUTRAL")
        trend_strength = trend_info.get("strength", 0.5)
        
        # Get indicator data
        indicators = comprehensive_signal.get("indicators", {})
        
        # Get pattern data
        patterns = comprehensive_signal.get("patterns", {})
        
        # Calculate entry, target, stop loss
        current_price = 0
        if data['candles'] and len(data['candles']) > 0:
            # Use the most recent close price
            current_price = data['candles'][-1][4]  # Assuming [timestamp, open, high, low, close, volume]
        
        # Get support/resistance
        zones = comprehensive_signal.get("zones", {})
        support_levels = zones.get("support", [])
        resistance_levels = zones.get("resistance", [])
        
        # Find nearest support/resistance
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else current_price * 0.99
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else current_price * 1.01
        
        # Calculate target and stop loss based on signal type
        if signal_type in ["BUY", "BUY CALL", "LONG"]:
            target_price = nearest_resistance
            stop_loss = nearest_support if nearest_support < current_price else current_price * 0.995
        elif signal_type in ["SELL", "SELL CALL", "SHORT"]:
            target_price = nearest_support
            stop_loss = nearest_resistance if nearest_resistance > current_price else current_price * 1.005
        else:
            # Default for HOLD
            target_price = current_price * 1.01
            stop_loss = current_price * 0.99
        
        # Calculate RRR
        risk = abs(current_price - stop_loss)
        reward = abs(target_price - current_price)
        rrr = round(reward / risk, 2) if risk > 0 else 0
        
        # Extract pattern information
        pattern_data = patterns.get("pattern_summary", {})
        bullish_patterns = pattern_data.get("bullish_patterns", [])
        bearish_patterns = pattern_data.get("bearish_patterns", [])
        detected_patterns = bullish_patterns + bearish_patterns
        
        # Format patterns with confidence
        patterns_detected = []
        for pattern in detected_patterns[:3]:  # Limit to top 3
            pattern_name = pattern.split("(")[0].strip() if "(" in pattern else pattern
            confidence = 0.85  # Default confidence
            if "(" in pattern and ")" in pattern:
                try:
                    conf_str = pattern.split("(")[1].split(")")[0]
                    confidence = float(conf_str)
                except:
                    pass
            patterns_detected.append(f"{pattern_name} ({confidence:.2f})")
        
        # Construct final signal object (maintaining the original structure)
        signal = {
            "signal": signal_type,
            "confidence": comprehensive_signal.get("confidence_score", 0.7),
            "entry": current_price,
            "stop_loss": stop_loss,
            "target": target_price,
            "rrr": rrr,
            "index": index,
            "strike": round(current_price / 50) * 50,  # Round to nearest 50
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
                "supertrend_direction": "bullish" if trend.lower().find("up") >= 0 else "bearish",
                "ema_9_20_cross": "bullish" if indicators.get("ema_9", 0) > indicators.get("ema_20", 0) else "bearish",
                "price_above_vwap": current_price > indicators.get("vwap", 0)
            },
            
            "volume_analysis": {
                "volume_surge_pct": indicators.get("rel_volume", 1) * 100 - 100,
                "obv_trend": "up" if indicators.get("obv", 0) > 0 else "down"
            },
            
            "pattern_analysis": {
                "patterns_detected": patterns_detected,
                "bullish_patterns": [p.lower().replace(" ", "_") for p in bullish_patterns][:3],
                "bearish_patterns": [p.lower().replace(" ", "_") for p in bearish_patterns][:3],
                "pattern_zone": "support_bounce" if trend.lower().find("up") >= 0 else "resistance_rejection",
                "pattern_age_bars": 1
            },
            
            "macro_sentiment": {
                "fii_net_buy": comprehensive_signal.get("fii_dii", {}).get("fii", {}).get("net_value", 0),
                "delivery_pct": 50,
                "option_chain_support_zone": comprehensive_signal.get("option_chain", {}).get("max_pain", {}).get("price", nearest_support)
            },
            
            "confluence": {
                "with_rsi": indicators.get("rsi_14", 50) > 50 if signal_type in ["BUY", "BUY CALL", "LONG"] else indicators.get("rsi_14", 50) < 50,
                "with_vwap": current_price > indicators.get("vwap", 0) if signal_type in ["BUY", "BUY CALL", "LONG"] else current_price < indicators.get("vwap", 0),
                "with_supertrend": (trend.lower().find("up") >= 0) if signal_type in ["BUY", "BUY CALL", "LONG"] else (trend.lower().find("down") >= 0),
                "with_volume": indicators.get("rel_volume", 1) > 1.1,
                "with_pattern": len(patterns_detected) > 0,
                "overall_confluence_score": comprehensive_signal.get("confidence_score", 0.7)
            }
        }
        
        # Keep track of the original comprehensive analysis in case needed elsewhere
        signal["_comprehensive_analysis"] = comprehensive_signal
        
        return signal
        
    except Exception as e:
        print(f"[ERROR] Signal analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return None or fallback to a basic signal
        return {
            "signal": "HOLD",
            "confidence": 0.5,
            "entry": data['candles'][-1][4] if data.get('candles') and len(data['candles']) > 0 else 0,
            "stop_loss": 0,
            "target": 0,
            "rrr": 0,
            "index": index,
            "strike": 0,
            "trade_time": datetime.now().isoformat(),
            "session": "OPEN",
            "error": str(e)
        }