# backend/modules/pattern_detector.py
import pandas as pd
import numpy as np
from typing import Dict, Union, Any


def convert_numpy_types(obj):
    """
    Recursively convert numpy types to Python native types for JSON serialization.
    
    Parameters:
    -----------
    obj : Any
        Object to convert
        
    Returns:
    --------
    Any: Converted object with no numpy types
    """
    import numpy as np
    import pandas as pd
    
    # Handle Pandas DataFrame
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    
    # Handle Pandas Series
    if isinstance(obj, pd.Series):
        return obj.to_dict()
    
    # Handle NumPy scalars
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    # Handle dictionaries
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    # Handle lists and tuples
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    # Return as is if no conversion needed
    return obj


def detect_patterns(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect chart patterns in price data
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Market data to analyze for patterns
        
    Returns:
    --------
    dict: Detected patterns and their characteristics
    """
    try:
        # Convert data to DataFrame if it's not already
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            if not candles or len(candles) < 10:
                return {
                    "pattern_summary": {
                        "bullish_patterns": [],
                        "bearish_patterns": [],
                        "pattern_bias": "neutral",
                        "pattern_strength": 0
                    },
                    "error": "Insufficient data for pattern detection"
                }
            
            # Convert candles to DataFrame
            df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return {
                "pattern_summary": {
                    "bullish_patterns": [],
                    "bearish_patterns": [],
                    "pattern_bias": "neutral",
                    "pattern_strength": 0
                },
                "error": "Invalid data format for pattern detection"
            }
        
        # Check if we have enough data
        if df.empty or len(df) < 10:
            return {
                "pattern_summary": {
                    "bullish_patterns": [],
                    "bearish_patterns": [],
                    "pattern_bias": "neutral",
                    "pattern_strength": 0
                },
                "error": "Insufficient data points for analysis"
            }
        
        # Simplified pattern detection logic
        # In a real implementation, you would use talib or a custom algorithm
        
        # Sample patterns to detect
        patterns = {
            # Bullish patterns
            "bullish_engulfing": detect_bullish_engulfing(df),
            "hammer": detect_hammer(df),
            "morning_star": detect_morning_star(df),
            "piercing_line": detect_piercing_line(df),
            "three_white_soldiers": detect_three_white_soldiers(df),
            
            # Bearish patterns
            "bearish_engulfing": detect_bearish_engulfing(df),
            "shooting_star": detect_shooting_star(df),
            "evening_star": detect_evening_star(df),
            "dark_cloud_cover": detect_dark_cloud_cover(df),
            "three_black_crows": detect_three_black_crows(df),
            
            # Continuation patterns
            "doji": detect_doji(df),
            "inside_bar": detect_inside_bar(df)
        }
        
        # Group into bullish and bearish
        bullish_patterns = []
        bearish_patterns = []
        
        # Bullish pattern group
        for pattern, result in patterns.items():
            if "bullish" in pattern or pattern in ["hammer", "morning_star", "piercing_line", "three_white_soldiers"]:
                if result["detected"]:
                    bullish_patterns.append(f"{pattern.replace('_', ' ').title()} ({result['confidence']:.2f})")
        
        # Bearish pattern group
        for pattern, result in patterns.items():
            if "bearish" in pattern or pattern in ["shooting_star", "evening_star", "dark_cloud_cover", "three_black_crows"]:
                if result["detected"]:
                    bearish_patterns.append(f"{pattern.replace('_', ' ').title()} ({result['confidence']:.2f})")
        
        # Calculate pattern bias
        pattern_bias = "neutral"
        if len(bullish_patterns) > len(bearish_patterns):
            pattern_bias = "bullish"
            if len(bullish_patterns) >= 3:
                pattern_bias = "strongly_bullish"
        elif len(bearish_patterns) > len(bullish_patterns):
            pattern_bias = "bearish"
            if len(bearish_patterns) >= 3:
                pattern_bias = "strongly_bearish"
        
        # Calculate pattern strength (0-100)
        total_patterns = len(bullish_patterns) + len(bearish_patterns)
        pattern_strength = min(100, total_patterns * 25)  # 25 points per pattern, max 100
        
        # Determine if at support/resistance
        last_close = df['close'].iloc[-1]
        last_low = df['low'].iloc[-1]
        last_high = df['high'].iloc[-1]
        
        at_support = last_low <= min(df['low'].iloc[-10:-1]) * 1.01  # Within 1% of recent lows
        at_resistance = last_high >= max(df['high'].iloc[-10:-1]) * 0.99  # Within 1% of recent highs
        
        # Determine pattern zone
        pattern_zone = "neutral"
        if at_support and pattern_bias.find("bull") >= 0:
            pattern_zone = "support_bounce"
        elif at_resistance and pattern_bias.find("bear") >= 0:
            pattern_zone = "resistance_rejection"
        elif at_support:
            pattern_zone = "at_support"
        elif at_resistance:
            pattern_zone = "at_resistance"
        
        result = {
            "pattern_summary": {
                "bullish_patterns": bullish_patterns,
                "bearish_patterns": bearish_patterns,
                "pattern_bias": pattern_bias,
                "pattern_strength": pattern_strength,
                "pattern_zone": pattern_zone,
                "pattern_age_bars": 1  # How many bars ago the pattern formed
            },
            "individual_patterns": patterns,
            "at_support": at_support,
            "at_resistance": at_resistance
        }
        
        # Convert any NumPy types to Python native types
        return convert_numpy_types(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return {
            "pattern_summary": {
                "bullish_patterns": [],
                "bearish_patterns": [],
                "pattern_bias": "neutral",
                "pattern_strength": 0
            },
            "error": str(e)
        }

# Pattern detection helper functions

def detect_bullish_engulfing(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect bullish engulfing pattern"""
    try:
        # Get last two candles
        if len(df) < 2:
            return {"detected": False, "confidence": 0}
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        # Check if previous candle is bearish (close < open)
        prev_bearish = prev_candle['close'] < prev_candle['open']
        
        # Check if current candle is bullish (close > open)
        curr_bullish = curr_candle['close'] > curr_candle['open']
        
        # Check if current candle engulfs previous candle
        engulfing = (
            curr_candle['open'] <= prev_candle['close'] and
            curr_candle['close'] >= prev_candle['open']
        )
        
        # Calculate confidence based on size of engulfing
        confidence = 0
        if prev_bearish and curr_bullish and engulfing:
            # Calculate size of engulfing relative to previous candle
            prev_size = abs(prev_candle['open'] - prev_candle['close'])
            curr_size = abs(curr_candle['open'] - curr_candle['close'])
            
            # Higher confidence if engulfing candle is much larger
            size_ratio = curr_size / max(prev_size, 0.001)  # Avoid division by zero
            
            confidence = min(0.95, 0.7 + 0.25 * min(1, size_ratio - 1))
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_bearish_engulfing(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect bearish engulfing pattern"""
    try:
        # Get last two candles
        if len(df) < 2:
            return {"detected": False, "confidence": 0}
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        # Check if previous candle is bullish (close > open)
        prev_bullish = prev_candle['close'] > prev_candle['open']
        
        # Check if current candle is bearish (close < open)
        curr_bearish = curr_candle['close'] < curr_candle['open']
        
        # Check if current candle engulfs previous candle
        engulfing = (
            curr_candle['open'] >= prev_candle['close'] and
            curr_candle['close'] <= prev_candle['open']
        )
        
        # Calculate confidence based on size of engulfing
        confidence = 0
        if prev_bullish and curr_bearish and engulfing:
            # Calculate size of engulfing relative to previous candle
            prev_size = abs(prev_candle['open'] - prev_candle['close'])
            curr_size = abs(curr_candle['open'] - curr_candle['close'])
            
            # Higher confidence if engulfing candle is much larger
            size_ratio = curr_size / max(prev_size, 0.001)  # Avoid division by zero
            
            confidence = min(0.95, 0.7 + 0.25 * min(1, size_ratio - 1))
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_hammer(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect hammer pattern (bullish)"""
    try:
        # Get last candle
        if len(df) < 1:
            return {"detected": False, "confidence": 0}
        
        curr_candle = df.iloc[-1]
        
        # Check for downtrend (at least 3 lower closes out of last 5)
        if len(df) >= 6:
            closes = df['close'].iloc[-6:-1]
            downtrend = sum(closes.iloc[i] > closes.iloc[i+1] for i in range(4)) >= 3
        else:
            downtrend = True  # Assume downtrend if not enough history
        
        # Calculate candle parts
        body_size = abs(curr_candle['open'] - curr_candle['close'])
        upper_shadow = curr_candle['high'] - max(curr_candle['open'], curr_candle['close'])
        lower_shadow = min(curr_candle['open'], curr_candle['close']) - curr_candle['low']
        
        # Check hammer criteria:
        # 1. Small body (top 1/3 of range)
        # 2. Little or no upper shadow
        # 3. Long lower shadow (at least 2x body)
        # 4. Body is bullish (close > open) for ideal hammer
        
        total_range = curr_candle['high'] - curr_candle['low']
        
        small_body = body_size <= total_range / 3
        small_upper_shadow = upper_shadow <= body_size / 2
        long_lower_shadow = lower_shadow >= body_size * 2
        bullish_body = curr_candle['close'] >= curr_candle['open']
        
        # Calculate confidence
        confidence = 0
        if small_body and small_upper_shadow and long_lower_shadow and downtrend:
            confidence = 0.7  # Base confidence
            if bullish_body:
                confidence += 0.15  # Bonus for bullish body
            if lower_shadow >= body_size * 3:
                confidence += 0.1  # Bonus for very long lower shadow
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_shooting_star(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect shooting star pattern (bearish)"""
    try:
        # Get last candle
        if len(df) < 1:
            return {"detected": False, "confidence": 0}
        
        curr_candle = df.iloc[-1]
        
        # Check for uptrend (at least 3 higher closes out of last 5)
        if len(df) >= 6:
            closes = df['close'].iloc[-6:-1]
            uptrend = sum(closes.iloc[i] < closes.iloc[i+1] for i in range(4)) >= 3
        else:
            uptrend = True  # Assume uptrend if not enough history
        
        # Calculate candle parts
        body_size = abs(curr_candle['open'] - curr_candle['close'])
        upper_shadow = curr_candle['high'] - max(curr_candle['open'], curr_candle['close'])
        lower_shadow = min(curr_candle['open'], curr_candle['close']) - curr_candle['low']
        
        # Check shooting star criteria:
        # 1. Small body (bottom 1/3 of range)
        # 2. Long upper shadow (at least 2x body)
        # 3. Little or no lower shadow
        # 4. Body is bearish (close < open) for ideal shooting star
        
        total_range = curr_candle['high'] - curr_candle['low']
        
        small_body = body_size <= total_range / 3
        long_upper_shadow = upper_shadow >= body_size * 2
        small_lower_shadow = lower_shadow <= body_size / 2
        bearish_body = curr_candle['close'] <= curr_candle['open']
        
        # Calculate confidence
        confidence = 0
        if small_body and long_upper_shadow and small_lower_shadow and uptrend:
            confidence = 0.7  # Base confidence
            if bearish_body:
                confidence += 0.15  # Bonus for bearish body
            if upper_shadow >= body_size * 3:
                confidence += 0.1  # Bonus for very long upper shadow
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_doji(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect doji pattern (neutral)"""
    try:
        # Get last candle
        if len(df) < 1:
            return {"detected": False, "confidence": 0}
        
        curr_candle = df.iloc[-1]
        
        # Calculate candle parts
        body_size = abs(curr_candle['open'] - curr_candle['close'])
        upper_shadow = curr_candle['high'] - max(curr_candle['open'], curr_candle['close'])
        lower_shadow = min(curr_candle['open'], curr_candle['close']) - curr_candle['low']
        total_range = curr_candle['high'] - curr_candle['low']
        
        # Check doji criteria:
        # 1. Very small body compared to total range
        # 2. Shadows on both sides
        
        very_small_body = body_size <= total_range * 0.1
        has_shadows = upper_shadow > 0 and lower_shadow > 0
        
        # Calculate confidence
        confidence = 0
        if very_small_body and has_shadows:
            # Purer doji has even smaller body
            confidence = 0.7 + 0.25 * (1 - (body_size / (total_range * 0.1)))
            confidence = min(0.95, confidence)
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_inside_bar(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect inside bar pattern (continuation)"""
    try:
        # Get last two candles
        if len(df) < 2:
            return {"detected": False, "confidence": 0}
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        # Check inside bar criteria:
        # 1. Current high is lower than previous high
        # 2. Current low is higher than previous low
        
        inside_high = curr_candle['high'] < prev_candle['high']
        inside_low = curr_candle['low'] > prev_candle['low']
        
        # Calculate confidence
        confidence = 0
        if inside_high and inside_low:
            # Smaller inside bar is better
            prev_range = prev_candle['high'] - prev_candle['low']
            curr_range = curr_candle['high'] - curr_candle['low']
            size_ratio = curr_range / prev_range
            
            confidence = 0.7 + 0.25 * (1 - min(1, size_ratio))
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_morning_star(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect morning star pattern (bullish)"""
    try:
        # Need at least 3 candles
        if len(df) < 3:
            return {"detected": False, "confidence": 0}
        
        candle_1 = df.iloc[-3]  # First candle (bearish)
        candle_2 = df.iloc[-2]  # Second candle (small body)
        candle_3 = df.iloc[-1]  # Third candle (bullish)
        
        # Check for downtrend
        if len(df) >= 8:
            closes = df['close'].iloc[-8:-3]
            downtrend = sum(closes.iloc[i] > closes.iloc[i+1] for i in range(len(closes)-1)) >= 3
        else:
            downtrend = True
        
        # Check pattern criteria:
        # 1. First candle is bearish (long body)
        # 2. Second candle is small (gap down from first)
        # 3. Third candle is bullish (closes above midpoint of first candle)
        
        first_bearish = candle_1['close'] < candle_1['open']
        first_body_size = abs(candle_1['open'] - candle_1['close'])
        
        second_small_body = abs(candle_2['open'] - candle_2['close']) < first_body_size * 0.5
        gap_down = max(candle_2['open'], candle_2['close']) < candle_1['close']
        
        third_bullish = candle_3['close'] > candle_3['open']
        third_closes_high = candle_3['close'] > (candle_1['open'] + candle_1['close']) / 2
        
        # Calculate confidence
        confidence = 0
        if first_bearish and second_small_body and third_bullish and downtrend:
            confidence = 0.7  # Base confidence
            
            if gap_down:
                confidence += 0.1
            
            if third_closes_high:
                confidence += 0.15
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_evening_star(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect evening star pattern (bearish)"""
    try:
        # Need at least 3 candles
        if len(df) < 3:
            return {"detected": False, "confidence": 0}
        
        candle_1 = df.iloc[-3]  # First candle (bullish)
        candle_2 = df.iloc[-2]  # Second candle (small body)
        candle_3 = df.iloc[-1]  # Third candle (bearish)
        
        # Check for uptrend
        if len(df) >= 8:
            closes = df['close'].iloc[-8:-3]
            uptrend = sum(closes.iloc[i] < closes.iloc[i+1] for i in range(len(closes)-1)) >= 3
        else:
            uptrend = True
        
        # Check pattern criteria:
        # 1. First candle is bullish (long body)
        # 2. Second candle is small (gap up from first)
        # 3. Third candle is bearish (closes below midpoint of first candle)
        
        first_bullish = candle_1['close'] > candle_1['open']
        first_body_size = abs(candle_1['open'] - candle_1['close'])
        
        second_small_body = abs(candle_2['open'] - candle_2['close']) < first_body_size * 0.5
        gap_up = min(candle_2['open'], candle_2['close']) > candle_1['close']
        
        third_bearish = candle_3['close'] < candle_3['open']
        third_closes_low = candle_3['close'] < (candle_1['open'] + candle_1['close']) / 2
        
        # Calculate confidence
        confidence = 0
        if first_bullish and second_small_body and third_bearish and uptrend:
            confidence = 0.7  # Base confidence
            
            if gap_up:
                confidence += 0.1
            
            if third_closes_low:
                confidence += 0.15
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_piercing_line(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect piercing line pattern (bullish)"""
    try:
        # Need at least 2 candles
        if len(df) < 2:
            return {"detected": False, "confidence": 0}
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        # Check for downtrend
        if len(df) >= 7:
            closes = df['close'].iloc[-7:-2]
            downtrend = sum(closes.iloc[i] > closes.iloc[i+1] for i in range(len(closes)-1)) >= 3
        else:
            downtrend = True
        
        # Check pattern criteria:
        # 1. First candle is bearish
        # 2. Second candle opens below previous low
        # 3. Second candle closes above midpoint of first candle's body
        
        first_bearish = prev_candle['close'] < prev_candle['open']
        second_bullish = curr_candle['close'] > curr_candle['open']
        
        gap_down_open = curr_candle['open'] < prev_candle['low']
        closes_above_midpoint = curr_candle['close'] > (prev_candle['open'] + prev_candle['close']) / 2
        closes_below_open = curr_candle['close'] < prev_candle['open']
        
        # Calculate confidence
        confidence = 0
        if first_bearish and second_bullish and closes_above_midpoint and closes_below_open and downtrend:
            confidence = 0.7  # Base confidence
            
            if gap_down_open:
                confidence += 0.15
            
            # Higher confidence if closer to previous open
            penetration = (curr_candle['close'] - prev_candle['close']) / (prev_candle['open'] - prev_candle['close'])
            if penetration > 0.8:
                confidence += 0.1
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_dark_cloud_cover(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect dark cloud cover pattern (bearish)"""
    try:
        # Need at least 2 candles
        if len(df) < 2:
            return {"detected": False, "confidence": 0}
        
        prev_candle = df.iloc[-2]
        curr_candle = df.iloc[-1]
        
        # Check for uptrend
        if len(df) >= 7:
            closes = df['close'].iloc[-7:-2]
            uptrend = sum(closes.iloc[i] < closes.iloc[i+1] for i in range(len(closes)-1)) >= 3
        else:
            uptrend = True
        
        # Check pattern criteria:
        # 1. First candle is bullish
        # 2. Second candle opens above previous high
        # 3. Second candle closes below midpoint of first candle's body
        
        first_bullish = prev_candle['close'] > prev_candle['open']
        second_bearish = curr_candle['close'] < curr_candle['open']
        
        gap_up_open = curr_candle['open'] > prev_candle['high']
        closes_below_midpoint = curr_candle['close'] < (prev_candle['open'] + prev_candle['close']) / 2
        closes_above_open = curr_candle['close'] > prev_candle['open']
        
        # Calculate confidence
        confidence = 0
        if first_bullish and second_bearish and closes_below_midpoint and closes_above_open and uptrend:
            confidence = 0.7  # Base confidence
            
            if gap_up_open:
                confidence += 0.15
            
            # Higher confidence if closer to previous open
            penetration = (prev_candle['close'] - curr_candle['close']) / (prev_candle['close'] - prev_candle['open'])
            if penetration > 0.8:
                confidence += 0.1
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_three_white_soldiers(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect three white soldiers pattern (bullish)"""
    try:
        # Need at least 3 candles
        if len(df) < 3:
            return {"detected": False, "confidence": 0}
        
        # Get last three candles
        candle_1 = df.iloc[-3]
        candle_2 = df.iloc[-2]
        candle_3 = df.iloc[-1]
        
        # Check pattern criteria:
        # 1. All three candles are bullish (close > open)
        # 2. Each candle closes higher than the previous
        # 3. Each candle opens within the previous candle's body
        # 4. Each candle has relatively small upper shadows
        
        all_bullish = (
            candle_1['close'] > candle_1['open'] and
            candle_2['close'] > candle_2['open'] and
            candle_3['close'] > candle_3['open']
        )
        
        progressive_closes = (
            candle_2['close'] > candle_1['close'] and
            candle_3['close'] > candle_2['close']
        )
        
        opens_within_previous = (
            candle_2['open'] > candle_1['open'] and
            candle_2['open'] < candle_1['close'] and
            candle_3['open'] > candle_2['open'] and
            candle_3['open'] < candle_2['close']
        )
        
        small_upper_shadows = (
            (candle_1['high'] - candle_1['close']) < (candle_1['close'] - candle_1['open']) / 2 and
            (candle_2['high'] - candle_2['close']) < (candle_2['close'] - candle_2['open']) / 2 and
            (candle_3['high'] - candle_3['close']) < (candle_3['close'] - candle_3['open']) / 2
        )
        
        # Calculate confidence
        confidence = 0
        if all_bullish and progressive_closes:
            confidence = 0.6  # Base confidence
            
            if opens_within_previous:
                confidence += 0.2
            
            if small_upper_shadows:
                confidence += 0.15
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}

def detect_three_black_crows(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect three black crows pattern (bearish)"""
    try:
        # Need at least 3 candles
        if len(df) < 3:
            return {"detected": False, "confidence": 0}
        
        # Get last three candles
        candle_1 = df.iloc[-3]
        candle_2 = df.iloc[-2]
        candle_3 = df.iloc[-1]
        
        # Check pattern criteria:
        # 1. All three candles are bearish (close < open)
        # 2. Each candle closes lower than the previous
        # 3. Each candle opens within the previous candle's body
        # 4. Each candle has relatively small lower shadows
        
        all_bearish = (
            candle_1['close'] < candle_1['open'] and
            candle_2['close'] < candle_2['open'] and
            candle_3['close'] < candle_3['open']
        )
        
        progressive_closes = (
            candle_2['close'] < candle_1['close'] and
            candle_3['close'] < candle_2['close']
        )
        
        opens_within_previous = (
            candle_2['open'] < candle_1['open'] and
            candle_2['open'] > candle_1['close'] and
            candle_3['open'] < candle_2['open'] and
            candle_3['open'] > candle_2['close']
        )
        
        small_lower_shadows = (
            (candle_1['close'] - candle_1['low']) < (candle_1['open'] - candle_1['close']) / 2 and
            (candle_2['close'] - candle_2['low']) < (candle_2['open'] - candle_2['close']) / 2 and
            (candle_3['close'] - candle_3['low']) < (candle_3['open'] - candle_3['close']) / 2
        )
        
        # Calculate confidence
        confidence = 0
        if all_bearish and progressive_closes:
            confidence = 0.6  # Base confidence
            
            if opens_within_previous:
                confidence += 0.2
            
            if small_lower_shadows:
                confidence += 0.15
            
            return {"detected": True, "confidence": confidence}
        
        return {"detected": False, "confidence": 0}
    except:
        return {"detected": False, "confidence": 0}