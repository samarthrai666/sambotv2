def run_market_open_analysis(data: pd.DataFrame):
    if data.empty or len(data) < 3:
        return {
            "error": "Insufficient data for opening range analysis"
        }
    
    # First 15 minutes (assuming 5-min candles)
    opening_range = data.iloc[:3]  
    
    high = opening_range["high"].max()
    low = opening_range["low"].min()
    open_price = opening_range["open"].iloc[0]
    close_price = opening_range["close"].iloc[2]
    
    # Calculate volatility
    volatility = (high - low) / low * 100
    
    # Volume analysis
    opening_volume = opening_range["volume"].sum()
    avg_daily_volume = data["volume"].mean() * 3  # Comparable 15-min volume
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
    
    # VWAP relationship
    vwap_current = data["vwap"].iloc[2]
    vwap_relation = "above" if close_price > vwap_current else "below"
    vwap_distance = abs(close_price - vwap_current) / vwap_current * 100
    
    return {
        "opening_high": high,
        "opening_low": low,
        "opening_range_width": high - low,
        "volatility_pct": volatility,
        "opening_direction": direction,
        "open_close_change_pct": (close_price - open_price) / open_price * 100,
        "high_volume_opening": high_volume_open,
        "vwap_relation": vwap_relation,
        "vwap_distance_pct": vwap_distance,
        "opening_range_time": "first_15min"
    }