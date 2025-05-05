"""
Equity swing trading processor module for trading signals

This module handles the generation of swing trading signals for equity stocks.
"""
from datetime import datetime, timedelta
import random
import time
import os
from typing import Dict, Any, List, Optional
from utils.filternsestocks import filter_stocks
import pandas as pd
import numpy as np

async def process(auto_execute: bool = False, log_enabled: bool = True) -> Dict[str, Any]:
    """
    Process equity swing trading signals
    
    Args:
        auto_execute (bool): Whether to automatically execute the generated signals
        log_enabled (bool): Whether to enable logging
        
    Returns:
        Dict[str, Any]: Dictionary containing executed and non-executed signals
    """
    if log_enabled:
        print(f"🔎 Running equity swing processor at {datetime.now().isoformat()}")
    
    # Get user preferences from stored configuration
    prefs_path = os.path.join(os.path.dirname(__file__), "../data/preferences.json")
    preferences = {}
    try:
        if os.path.exists(prefs_path):
            import json
            with open(prefs_path, 'r') as f:
                preferences = json.load(f)
        else:
            # If no stored preferences, use default
            preferences = {
                "equity": {
                    "enabled": True,
                    "swing": {
                        "enabled": True,
                        "modes": ["momentum", "breakout"],
                        "max_stocks": 5,
                        "sectors": [],
                        "scan_frequency": "weekly",
                        "market_caps": []
                    }
                }
            }
    except Exception as e:
        print(f"[WARNING] Error loading preferences: {str(e)}")
    
    # Filter stocks based on user preferences
    filtered_stocks = filter_stocks(preferences)
    
    if log_enabled:
        print(f"📊 Found {len(filtered_stocks)} stocks matching user preferences")
    
    # If no stocks match the criteria, return empty signals
    if not filtered_stocks:
        return {
            "executed": [],
            "non_executed": [],
            "timestamp": datetime.now().isoformat(),
            "processor": "equity_swing"
        }
    
    # Generate equity swing signals based on filtered stocks
    signals = []
    
    for stock in filtered_stocks:
        # Skip if stock data is incomplete
        if not all(k in stock for k in ["symbol", "company", "sector", "market_cap_category"]):
            continue
            
        symbol = stock["symbol"]
        company = stock["company"]
        sector = stock["sector"]
        market_cap = stock["market_cap_category"]
        
        # Determine random price points based on stock
        # In a real implementation, this would fetch actual market data
        base_price = get_simulated_price(symbol)
        
        # Run technical analysis to determine signal type
        signal_type, confidence = analyze_stock_technicals(symbol, company, sector)
        
        # Skip if no actionable signal
        if signal_type == "NEUTRAL":
            continue
            
        # Calculate entry, target and stop loss based on signal type
        is_buy = signal_type == "BUY"
        
        if is_buy:
            entry = base_price
            target = round(entry * (1 + random.uniform(0.05, 0.15)), 2)  # 5-15% upside
            stop_loss = round(entry * (1 - random.uniform(0.03, 0.08)), 2)  # 3-8% downside
        else:
            entry = base_price
            target = round(entry * (1 - random.uniform(0.05, 0.15)), 2)  # 5-15% downside
            stop_loss = round(entry * (1 + random.uniform(0.03, 0.08)), 2)  # 3-8% upside
        
        # Calculate risk-reward ratio
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        rrr = round(reward / risk, 2) if risk > 0 else 0
        
        # Generate a set of indicators based on the signal type
        indicators = generate_technical_indicators(is_buy)
        
        # Generate pattern analysis
        pattern_analysis = generate_pattern_analysis(is_buy)
        
        # Calculate expected holding period (3-15 days for swing)
        days_to_hold = random.randint(3, 15)
        expected_exit_date = (datetime.now() + timedelta(days=days_to_hold)).strftime("%d %b %Y")
        
        # AI opinion simulation
        ai_opinion = generate_ai_opinion(symbol, company, signal_type, confidence)
        
        # Create the signal
        signal = {
            "id": f"equity-swing-{symbol.lower()}-{int(time.time())}-{random.randint(1000, 9999)}",
            "trade_time": datetime.now().isoformat(),
            "symbol": symbol,
            "company": company,
            "sector": sector,
            "market_cap_category": market_cap,
            "signal": signal_type,
            "entry": entry,
            "target": target,
            "stop_loss": stop_loss,
            "rrr": rrr,
            "trend": "bullish" if is_buy else "bearish",
            "timeframe": "daily",
            "confidence": confidence,
            "indicator_snapshot": indicators,
            "pattern_analysis": pattern_analysis,
            "ai_opinion": ai_opinion,
            "expected_holding_period": f"{days_to_hold} days",
            "expected_exit_date": expected_exit_date,
            "potential_gain": round(abs((target - entry) / entry) * 100, 2),
            # Format for SwingEquitySignals.tsx component
            "entry_price": entry,
            "target_price": target,
            "setup_type": pattern_analysis["patterns_detected"][0] if pattern_analysis["patterns_detected"] else "Technical Setup",
            "action": "BUY" if is_buy else "SELL",
            "risk_reward": rrr,
            "analysis": ai_opinion["reasoning"]
        }
        
        signals.append(signal)
    
    # If auto-execute is enabled, simulate execution for some signals
    executed = []
    non_executed = signals
    
    if auto_execute and signals:
        # Randomly select signals to execute
        num_to_execute = random.randint(0, min(len(signals), 2))
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
        "processor": "equity_swing"
    }

def get_simulated_price(symbol: str) -> float:
    """Get a simulated price for a stock based on its symbol"""
    # Use the symbol's string hash to generate a consistent but random-looking price
    # This ensures the same stock always gets the same base price
    h = 0
    for char in symbol:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    
    # Generate a price between 500 and 5000
    base = (h % 4500) + 500
    
    # Add some cents
    cents = round((h % 99) / 100, 2)
    
    return base + cents

def analyze_stock_technicals(symbol: str, company: str, sector: str) -> tuple:
    """
    Analyze stock technicals to determine signal type and confidence
    In a real implementation, this would use actual market data
    """
    # Determine signal based on symbol hash to ensure consistent results
    h = sum(ord(c) for c in symbol)
    
    # 70% of stocks should have a BUY signal, 20% SELL, 10% NEUTRAL
    if h % 10 < 7:
        signal_type = "BUY"
        # Confidence between 70-95%
        confidence = 70 + (h % 25)
    elif h % 10 < 9:
        signal_type = "SELL"
        # Confidence between 70-90%
        confidence = 70 + (h % 20)
    else:
        signal_type = "NEUTRAL"
        confidence = 50
        
    return signal_type, confidence / 100  # Return confidence as a decimal

def generate_technical_indicators(is_bullish: bool) -> Dict[str, Any]:
    """Generate a set of technical indicators based on the signal type"""
    if is_bullish:
        return {
            "rsi": random.randint(40, 65),
            "macd": random.choice(["bullish", "neutral"]),
            "sma_50_200": random.choice(["golden_cross", "neutral"]),
            "bollinger": random.choice(["lower_touch", "middle_band"]),
            "volume_trend": random.choice(["increasing", "neutral"])
        }
    else:
        return {
            "rsi": random.randint(35, 60),
            "macd": random.choice(["bearish", "neutral"]),
            "sma_50_200": random.choice(["death_cross", "neutral"]),
            "bollinger": random.choice(["upper_touch", "middle_band"]),
            "volume_trend": random.choice(["decreasing", "neutral"])
        }

def generate_pattern_analysis(is_bullish: bool) -> Dict[str, Any]:
    """Generate pattern analysis based on the signal type"""
    bullish_patterns = [
        "Double Bottom", "Inverse Head and Shoulders", "Cup and Handle", 
        "Bullish Engulfing", "Morning Star", "Flag Pattern", "Rounding Bottom"
    ]
    
    bearish_patterns = [
        "Double Top", "Head and Shoulders", "Bearish Engulfing", 
        "Evening Star", "Descending Triangle", "Rising Wedge"
    ]
    
    patterns = random.sample(bullish_patterns if is_bullish else bearish_patterns, k=random.randint(1, 3))
    
    return {
        "patterns_detected": patterns,
        "strength": random.choice(["strong", "moderate", "weak"])
    }

def generate_ai_opinion(symbol: str, company: str, signal_type: str, confidence: float) -> Dict[str, Any]:
    """Generate AI opinion for a stock"""
    buy_templates = [
        f"{company} ({symbol}) shows promising bullish momentum with key support levels being respected. Recent volume patterns confirm buying interest.",
        f"{symbol} has formed a strong technical setup with multiple indicators confirming a potential upward move. The risk-reward ratio is favorable.",
        f"Technical analysis for {company} reveals a potential breakout pattern forming. Price action and momentum indicators are aligned for an upward move."
    ]
    
    sell_templates = [
        f"{company} ({symbol}) is showing bearish divergence patterns with declining volume on recent rallies, suggesting potential downside.",
        f"{symbol} has broken below key support levels with increasing volume, indicating potential continuation of the downtrend.",
        f"Technical analysis for {company} suggests overhead resistance remains strong with bearish momentum building."
    ]
    
    reasoning = random.choice(buy_templates if signal_type == "BUY" else sell_templates)
    
    return {
        "sentiment": "bullish" if signal_type == "BUY" else "bearish",
        "confidence": confidence,
        "reasoning": reasoning
    }