# backend/processors/equity_swing.py
from datetime import datetime
import random
import time
from typing import Dict, Any, List
import os
import json

# Import stock list utility
from utils.filternsestocks import get_stocks_by_filters

async def process(auto_execute: bool = False, log_enabled: bool = True, trading_preferences: Dict = None) -> Dict[str, Any]:
    """
    Process equity swing trading signals based on user preferences
    
    Args:
        auto_execute (bool): Whether to automatically execute the generated signals
        log_enabled (bool): Whether to enable logging
        trading_preferences (Dict, optional): The user's trading preferences
        
    Returns:
        Dict[str, Any]: Dictionary containing executed and non-executed signals
    """
    print(f"🔎 Running equity swing processor at {datetime.now().isoformat()}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Load trading preferences from parameter or file
    if not trading_preferences:
        try:
            # Try to load from a preferences file
            prefs_path = "data/trading_preferences.json"
            if os.path.exists(prefs_path):
                with open(prefs_path, "r") as f:
                    trading_preferences = json.load(f)
                    print("Loaded trading preferences from file")
            else:
                print(f"Trading preferences file not found at {prefs_path}")
                prefs_paths_to_try = [
                    "./data/trading_preferences.json",
                    "../data/trading_preferences.json",
                    "trading_preferences.json",
                    "./trading_preferences.json"
                ]
                
                for path in prefs_paths_to_try:
                    if os.path.exists(path):
                        print(f"Found preferences at alternate location: {path}")
                        with open(path, "r") as f:
                            trading_preferences = json.load(f)
                            print("Loaded trading preferences from alternate location")
                            break
                
                if not trading_preferences:
                    print("No trading preferences found")
                    return {
                        "executed": [],
                        "non_executed": [],
                        "timestamp": datetime.now().isoformat(),
                        "processor": "equity_swing",
                        "error": "Trading preferences file not found"
                    }
        except Exception as e:
            print(f"Error loading trading preferences: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "executed": [],
                "non_executed": [],
                "timestamp": datetime.now().isoformat(),
                "processor": "equity_swing",
                "error": str(e)
            }
    
    # Log the trading preferences
    print("Trading preferences:")
    print(json.dumps(trading_preferences, indent=2))
    
    # Extract specific preferences
    equity_prefs = trading_preferences.get("equity", {})
    swing_prefs = equity_prefs.get("swing", {})
    
    # If swing trading is not enabled, return empty results
    if not equity_prefs.get("enabled", False) or not swing_prefs.get("enabled", False):
        print("Equity swing trading is disabled in preferences")
        return {
            "executed": [],
            "non_executed": [],
            "timestamp": datetime.now().isoformat(),
            "processor": "equity_swing"
        }
    
    # Extract swing trading settings from preferences
    modes = swing_prefs.get("modes", [])
    max_stocks = swing_prefs.get("max_stocks", 0)  # Use value from trading preferences
    selected_sectors = swing_prefs.get("sectors", [])
    market_caps = swing_prefs.get("market_caps", [])
    
    # Print detailed debug info
    print("\n=== Swing Trading Configuration ===")
    print(f"Modes: {modes}")
    print(f"Max stocks: {max_stocks}")
    print(f"Selected sectors: {selected_sectors}")
    print(f"Market caps: {market_caps}")
    print("====================================\n")
    
    # Validate required settings
    if not modes or max_stocks <= 0 or not selected_sectors or not market_caps:
        print("Incomplete swing trading preferences")
        print(f"Modes: {modes}, Max stocks: {max_stocks}, Sectors: {selected_sectors}, Market caps: {market_caps}")
        return {
            "executed": [],
            "non_executed": [],
            "timestamp": datetime.now().isoformat(),
            "processor": "equity_swing",
            "error": "Incomplete swing trading preferences"
        }
    
    # Get filtered stock list based on sectors and market caps from CSV
    try:
        print("\n=== Filtering Stocks ===")
        print(f"Calling get_stocks_by_filters with:")
        print(f"  Sectors: {selected_sectors}")
        print(f"  Market caps: {market_caps}")
        print(f"  Limit: {max_stocks * 3}")
        
        # Request max_stocks * 3 to allow for filtering/randomization
        filter_limit = max_stocks * 3
        filtered_stocks = get_stocks_by_filters(
            sectors=selected_sectors,
            market_caps=market_caps,
            limit=filter_limit
        )
        
        print(f"\nFiltered stocks result: {len(filtered_stocks)} stocks")
        if filtered_stocks:
            print("Sample of filtered stocks:")
            for i, stock in enumerate(filtered_stocks[:min(5, len(filtered_stocks))]):
                print(f"  {i+1}. {stock.get('symbol')} - {stock.get('sector')} ({stock.get('market_cap_category')})")
        else:
            print("No stocks found matching criteria")
            return {
                "executed": [],
                "non_executed": [],
                "timestamp": datetime.now().isoformat(),
                "processor": "equity_swing",
                "error": "No stocks found matching criteria"
            }
    except Exception as e:
        print(f"Error getting filtered stocks: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "executed": [],
            "non_executed": [],
            "timestamp": datetime.now().isoformat(),
            "processor": "equity_swing",
            "error": f"Error getting filtered stocks: {str(e)}"
        }
    
    signals = []
    
    # Generate signals based on the selected modes and stocks
    print("\n=== Generating Signals ===")
    for i, stock in enumerate(filtered_stocks):
        try:
            symbol = stock['symbol']
            sector = stock.get('sector', "Unknown")
            market_cap = stock.get('market_cap_category', "Unknown")
            
            print(f"Processing signal for {symbol} (Sector: {sector}, Market Cap: {market_cap})")
            
            # Current price (mock)
            base_price = 500 + (i * 100)  # Just to create variety
            current_price = base_price + random.randint(-50, 50)
            
            # Generate signals based on selected modes
            for mode in modes:
                if mode == "reversal" and random.random() < 0.6:  # 60% chance of generating a reversal signal
                    signal = generate_reversal_signal(symbol, current_price, sector, market_cap)
                    if signal:
                        signals.append(signal)
                        print(f"  - Generated reversal signal for {symbol}")
                        
                elif mode == "momentum" and random.random() < 0.6:
                    signal = generate_momentum_signal(symbol, current_price, sector, market_cap)
                    if signal:
                        signals.append(signal)
                        print(f"  - Generated momentum signal for {symbol}")
                        
                elif mode == "breakout" and random.random() < 0.6:
                    signal = generate_breakout_signal(symbol, current_price, sector, market_cap)
                    if signal:
                        signals.append(signal)
                        print(f"  - Generated breakout signal for {symbol}")
        
        except Exception as e:
            print(f"Error processing signal for {stock.get('symbol', 'unknown')}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Sort signals by confidence score
    signals = sorted(signals, key=lambda x: x.get("confidence", 0), reverse=True)
    
    # Print generated signals
    print(f"\nGenerated {len(signals)} signals before limiting")
    
    # Limit to max_stocks from trading preferences
    signals = signals[:max_stocks]
    
    print(f"Final signals after limiting to {max_stocks}: {len(signals)}")
    for i, signal in enumerate(signals):
        print(f"  {i+1}. {signal.get('symbol')} - {signal.get('signal')} ({signal.get('confidence_score')}%)")
    
    # If auto-execute is enabled, simulate execution for some signals
    executed = []
    non_executed = signals
    
    if auto_execute and signals:
        # Randomly select signals to execute
        num_to_execute = random.randint(0, len(signals))
        if num_to_execute > 0:
            to_execute = random.sample(signals, num_to_execute)
            executed = to_execute
            non_executed = [s for s in signals if s not in to_execute]
            
            print(f"✅ Auto-executed {len(executed)} equity swing signals")
    
    return {
        "executed": executed,
        "non_executed": non_executed,
        "timestamp": datetime.now().isoformat(),
        "processor": "equity_swing"
    }

def generate_reversal_signal(symbol, current_price, sector, market_cap):
    """Generate a reversal pattern signal"""
    # Simulate a reversal pattern
    is_bullish_reversal = random.choice([True, False])
    
    # Calculate targets and stop loss
    if is_bullish_reversal:
        target = current_price * 1.15  # 15% target for reversal
        stop_loss = current_price * 0.92  # 8% stop loss
        signal_type = "BUY"
        pattern = "Bullish Reversal"
    else:
        target = current_price * 0.85  # 15% target
        stop_loss = current_price * 1.08  # 8% stop loss
        signal_type = "SELL"
        pattern = "Bearish Reversal"
    
    # Calculate risk-reward ratio
    rrr = abs((target - current_price) / (current_price - stop_loss)) if stop_loss != current_price else 2.0
    
    # Potential gain percentage
    potential_gain = abs((target - current_price) / current_price) * 100
    
    # Create the signal with proper structure for frontend compatibility
    return {
        "id": f"equity-nse:eq-{symbol.lower()}-swing-{int(time.time())}-{random.randint(1000, 9999)}",
        "trade_time": datetime.now().isoformat(),
        "symbol": symbol,
        "signal": signal_type,
        "action": signal_type,  # Frontend compatibility
        "entry": current_price,
        "entry_price": current_price,  # Frontend compatibility
        "target": target,
        "target_price": target,  # Frontend compatibility
        "stop_loss": stop_loss,
        "rrr": rrr,
        "risk_reward": rrr,  # Frontend compatibility
        "risk_reward_ratio": rrr,  # Frontend compatibility
        "potential_gain": potential_gain,  # Frontend compatibility
        "trend": "bullish" if is_bullish_reversal else "bearish",
        "timeframe": "daily",
        "confidence": 0.75 + (random.random() * 0.2),  # 75-95% confidence
        "confidence_score": int((0.75 + (random.random() * 0.2)) * 100),  # Frontend compatibility
        "indicator_snapshot": {
            "rsi": 30 if is_bullish_reversal else 70,  # Oversold for bullish reversal, overbought for bearish
            "macd": 0.5 if is_bullish_reversal else -0.5,
            "price_action": "positive" if is_bullish_reversal else "negative"
        },
        "pattern_analysis": {
            "patterns_detected": [pattern]
        },
        "patterns": [pattern],  # Frontend compatibility
        "setup_type": pattern,  # Frontend compatibility
        "ai_opinion": {
            "sentiment": "bullish" if is_bullish_reversal else "bearish",
            "confidence": 0.8,
            "reasoning": f"Potential {pattern.lower()} pattern detected on {symbol}. Price action suggests reversal from current trend."
        },
        "aiAnalysis": f"Potential {pattern.lower()} pattern detected on {symbol}. Price action suggests reversal from current trend.",  # Frontend compatibility
        "sector": sector,
        "market_cap": market_cap,
        "expected_holding_period": "2-4 weeks",
        "executed": False
    }

def generate_momentum_signal(symbol, current_price, sector, market_cap):
    """Generate a momentum-based signal"""
    # Simulate momentum conditions
    is_bullish = random.choice([True, False])
    
    # Calculate targets and stop loss
    if is_bullish:
        target = current_price * 1.12  # 12% target for momentum
        stop_loss = current_price * 0.94  # 6% stop loss
        signal_type = "BUY"
        pattern = "Bullish Momentum"
    else:
        target = current_price * 0.88  # 12% target
        stop_loss = current_price * 1.06  # 6% stop loss
        signal_type = "SELL"
        pattern = "Bearish Momentum"
    
    # Calculate risk-reward ratio
    rrr = abs((target - current_price) / (current_price - stop_loss)) if stop_loss != current_price else 2.0
    
    # Potential gain percentage
    potential_gain = abs((target - current_price) / current_price) * 100
    
    # Create the signal with proper structure for frontend compatibility
    return {
        "id": f"equity-nse:eq-{symbol.lower()}-swing-{int(time.time())}-{random.randint(1000, 9999)}",
        "trade_time": datetime.now().isoformat(),
        "symbol": symbol,
        "signal": signal_type,
        "action": signal_type,  # Frontend compatibility
        "entry": current_price,
        "entry_price": current_price,  # Frontend compatibility
        "target": target,
        "target_price": target,  # Frontend compatibility
        "stop_loss": stop_loss,
        "rrr": rrr,
        "risk_reward": rrr,  # Frontend compatibility
        "risk_reward_ratio": rrr,  # Frontend compatibility
        "potential_gain": potential_gain,  # Frontend compatibility
        "trend": "bullish" if is_bullish else "bearish",
        "timeframe": "daily",
        "confidence": 0.75 + (random.random() * 0.2),  # 75-95% confidence
        "confidence_score": int((0.75 + (random.random() * 0.2)) * 100),  # Frontend compatibility
        "indicator_snapshot": {
            "rsi": 60 if is_bullish else 40,
            "macd": 0.7 if is_bullish else -0.7,
            "price_action": "positive" if is_bullish else "negative"
        },
        "pattern_analysis": {
            "patterns_detected": [pattern]
        },
        "patterns": [pattern],  # Frontend compatibility
        "setup_type": pattern,  # Frontend compatibility
        "ai_opinion": {
            "sentiment": "bullish" if is_bullish else "bearish",
            "confidence": 0.85,
            "reasoning": f"Strong {pattern.lower()} on {symbol} with favorable technical alignment."
        },
        "aiAnalysis": f"Strong {pattern.lower()} on {symbol} with favorable technical alignment.",  # Frontend compatibility
        "sector": sector,
        "market_cap": market_cap,
        "expected_holding_period": "2-3 weeks",
        "executed": False
    }

def generate_breakout_signal(symbol, current_price, sector, market_cap):
    """Generate a breakout-based signal"""
    # Simulate breakout conditions
    is_bullish = random.choice([True, False])
    
    # Calculate targets and stop loss
    if is_bullish:
        target = current_price * 1.10  # 10% target for breakout
        stop_loss = current_price * 0.95  # 5% stop loss
        signal_type = "BUY"
        pattern = "Bullish Breakout"
    else:
        target = current_price * 0.90  # 10% target
        stop_loss = current_price * 1.05  # 5% stop loss
        signal_type = "SELL"
        pattern = "Bearish Breakdown"
    
    # Calculate risk-reward ratio
    rrr = abs((target - current_price) / (current_price - stop_loss)) if stop_loss != current_price else 2.0
    
    # Potential gain percentage
    potential_gain = abs((target - current_price) / current_price) * 100
    
    # Create the signal with proper structure for frontend compatibility
    return {
        "id": f"equity-nse:eq-{symbol.lower()}-swing-{int(time.time())}-{random.randint(1000, 9999)}",
        "trade_time": datetime.now().isoformat(),
        "symbol": symbol,
        "signal": signal_type,
        "action": signal_type,  # Frontend compatibility
        "entry": current_price,
        "entry_price": current_price,  # Frontend compatibility
        "target": target,
        "target_price": target,  # Frontend compatibility
        "stop_loss": stop_loss,
        "rrr": rrr,
        "risk_reward": rrr,  # Frontend compatibility
        "risk_reward_ratio": rrr,  # Frontend compatibility
        "potential_gain": potential_gain,  # Frontend compatibility
        "trend": "bullish" if is_bullish else "bearish",
        "timeframe": "daily",
        "confidence": 0.75 + (random.random() * 0.2),  # 75-95% confidence
        "confidence_score": int((0.75 + (random.random() * 0.2)) * 100),  # Frontend compatibility
        "indicator_snapshot": {
            "rsi": 65 if is_bullish else 35,
            "macd": 0.6 if is_bullish else -0.6,
            "price_action": "positive" if is_bullish else "negative"
        },
        "pattern_analysis": {
            "patterns_detected": [pattern]
        },
        "patterns": [pattern],  # Frontend compatibility
        "setup_type": pattern,  # Frontend compatibility
        "ai_opinion": {
            "sentiment": "bullish" if is_bullish else "bearish",
            "confidence": 0.85,
            "reasoning": f"Clear {pattern.lower()} detected on {symbol} with volume confirmation."
        },
        "aiAnalysis": f"Clear {pattern.lower()} detected on {symbol} with volume confirmation.",  # Frontend compatibility
        "sector": sector,
        "market_cap": market_cap,
        "expected_holding_period": "1-3 weeks",
        "executed": False
    }