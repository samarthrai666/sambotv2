from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel
from datetime import datetime
import time
import random


cached_data = None
last_updated = 0
refresh_interval = 30 # seconds

# Load .env configs
load_dotenv()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
FYERS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")
FYERS_BASE_URL = os.getenv("FYERS_BASE_URL", "https://api.fyers.in/api/v2")
MOCK_MODE = True  # Force mock mode for testing

print("=== ENVIRONMENT VARIABLES ===")
print(f"MOCK_FYERS env var: {os.getenv('MOCK_FYERS', 'NOT SET')}")
print(f"Calculated MOCK_MODE: {os.getenv('MOCK_FYERS', 'true').lower() == 'true'}")
print("============================")

# Import processors
from processors import (
    nifty_scalp, nifty_swing, nifty_longterm,
    banknifty_scalp, banknifty_swing, banknifty_longterm
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Request schema
class TradeModeRequest(BaseModel):
    nifty: List[str] = []
    banknifty: List[str] = []
    auto_execute: bool
    log_enabled: bool = True


# 🧠 Processor Map
strategy_map = {
    "nifty_scalp": nifty_scalp.process,
    "nifty_swing": nifty_swing.process,
    "nifty_longterm": nifty_longterm.process,
    "banknifty_scalp": banknifty_scalp.process,
    "banknifty_swing": banknifty_swing.process,
    "banknifty_longterm": banknifty_longterm.process,
}

@app.post("/signal/process")
async def process_trade_modes(req: TradeModeRequest):
    try:
        print(f"[INFO] Processing trade modes: NIFTY={req.nifty}, BANKNIFTY={req.banknifty}, auto_execute={req.auto_execute}")
        tasks = []

        # 🧩 Add all selected processors
        for mode in req.nifty:
            key = f"nifty_{mode}"
            if key in strategy_map:
                print(f"[INFO] Adding task for {key}")
                tasks.append(asyncio.create_task(
                    strategy_map[key](req.auto_execute, req.log_enabled)
                ))
            else:
                print(f"[WARNING] Strategy {key} not found in strategy_map")

        for mode in req.banknifty:
            key = f"banknifty_{mode}"
            if key in strategy_map:
                print(f"[INFO] Adding task for {key}")
                tasks.append(asyncio.create_task(
                    strategy_map[key](req.auto_execute, req.log_enabled)
                ))
            else:
                print(f"[WARNING] Strategy {key} not found in strategy_map")

        # 🚀 Run all processors concurrently
        print(f"[INFO] Running {len(tasks)} tasks concurrently")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for exceptions
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            for e in exceptions:
                print(f"[ERROR] Task exception: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Filter out exceptions
            results = [r for r in results if not isinstance(r, Exception)]

        # 🔄 Merge results
        executed_signals = []
        non_executed_signals = []

        for res in results:
            if isinstance(res, dict):
                executed_signals.extend(res.get("executed", []))
                non_executed_signals.extend(res.get("non_executed", []))
            else:
                print(f"[WARNING] Unexpected result type: {type(res)}")

        print(f"[INFO] Processed {len(executed_signals)} executed and {len(non_executed_signals)} non-executed signals")
        
        return {
            "executed_signals": executed_signals,
            "non_executed_signals": non_executed_signals,
            "ai_enabled": AI_ENABLED
        }
    except Exception as e:
        print(f"[ERROR] Exception in process_trade_modes: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signal processing failed: {str(e)}")

# Cache for storing signals (temporary solution until you have a database)
signals_cache = []

@app.post("/signal/execute/{signal_id}")
async def execute_signal(signal_id: str):
    try:
        # In real scenario, fetch signal from database using signal_id
        # For now, we'll recreate it based on what we know
        from utils.fyers_client import place_order
        from utils.trade_journal import log_trade
        
        # Get signal details (in production you'd fetch this from DB)
        signal = next((s for s in signals_cache if s["id"] == signal_id), None)
        
        if not signal:
            # If not found in cache, return mock response for now
            mock_signal = {
                "id": signal_id,
                "signal": "BUY CALL",
                "index": "NIFTY",
                "entry": 17865.50,
                "target": 17985.88,
                "stop_loss": 17785.25,
                "confidence": 0.91
            }
            
            # Place order with Fyers API
            order_response = place_order(mock_signal)
            
            # Log the trade
            log_trade(mock_signal, executed=True)
            
            return {
                "order_id": f"ORD-{signal_id[:8]}",
                "status": "success",
                "message": "Trade executed successfully",
                "executed_at": datetime.now().isoformat()
            }
        
        # If signal found, execute it
        order_response = place_order(signal)
        log_trade(signal, executed=True)
        
        return {
            "order_id": order_response.get("id", f"ORD-{signal_id[:8]}"),
            "status": "success",
            "message": "Trade executed successfully",
            "executed_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Set this globally
fyers = fyersModel.FyersModel(
    client_id=os.getenv("FYERS_CLIENT_ID"),
    token=os.getenv("FYERS_ACCESS_TOKEN"),
    is_async=False,
    log_path=""
)

@app.get("/market/data")
async def get_market_data():
    global cached_data, last_updated

    try:
        if time.time() - last_updated > refresh_interval:
            response = fyers.quotes(data={
                "symbols": "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX"
            })


            if response["s"] != "ok":
                raise ValueError(response.get("message", "Invalid Fyers response"))

            quotes = response["d"]

            nifty = next((item for item in quotes if "NIFTY50" in item.get("n", "")), None)
            banknifty = next((item for item in quotes if "NIFTYBANK" in item.get("n", "")), None)

            if not nifty or not banknifty:
                raise ValueError("Missing quote data for NIFTY or BANKNIFTY")


            # Extract values from nested "v" dict
            nifty_values = nifty.get("v", {})
            banknifty_values = banknifty.get("v", {})

            cached_data = {
                "nifty": {
                    "price": nifty_values.get("lp", 0),
                    "change": nifty_values.get("ch", 0),
                    "changePercent": nifty_values.get("chp", 0)
                },
                "banknifty": {
                    "price": banknifty_values.get("lp", 0),
                    "change": banknifty_values.get("ch", 0),
                    "changePercent": banknifty_values.get("chp", 0)
                },
                "marketStatus": "open",
                "marketOpenTime": "09:15:00",
                "marketCloseTime": "15:30:00",
                "serverTime": datetime.now().isoformat()
            }

            last_updated = time.time()

        return cached_data

    except Exception as e:
        print(f"🔥 Using mock due to error: {e}")
        return {
            "nifty": {"price": 23412.65, "change": 142.50, "changePercent": 0.61},
            "banknifty": {"price": 48723.90, "change": -104.80, "changePercent": -0.21},
            "marketStatus": "closed",
            "marketOpenTime": "09:15:00",
            "marketCloseTime": "15:30:00",
            "serverTime": datetime.now().isoformat()
        }

# Helper functions for fetching market data
async def fetch_quote(symbol):
    """Fetch real-time quote from Fyers"""
    try:
        headers = {"Authorization": f"Bearer {FYERS_TOKEN}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FYERS_BASE_URL}/quotes",
                params={"symbols": symbol},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            print("FYERS QUOTES RESPONSE:", data)  # Debugging output
            return data["d"][0] if data.get("s") == "ok" and data.get("d") else {}
    except Exception as e:
        print(f"Error fetching quote for {symbol}: {str(e)}")
        return {
            "lp": 23000.00 if "NIFTY" in symbol else 48000.00,
            "ch": 100.00,
            "chp": 0.5
        }


async def get_market_status():
    """Get market status from Fyers"""
    try:
        headers = {"Authorization": f"Bearer {FYERS_TOKEN}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FYERS_BASE_URL}/market-status", headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching market status: {str(e)}")
        # Return mock status on error
        now = datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        is_market_open = market_open <= now <= market_close
        
        return {"market_status": is_market_open}
    

@app.post("/signals/refresh-analysis")
async def refresh_signal_analysis(signals: List[dict]):
    """Refresh the analysis for a list of signals with current market data"""
    try:
        updated_signals = []
        
        for signal in signals:
            # Get fresh market data for the symbol
            symbol_data = await get_symbol_data(signal["symbol"])
            
            # Recalculate technical indicators
            indicators = calculate_indicators(symbol_data)
            
            # Re-detect patterns
            patterns = detect_patterns(symbol_data)
            
            # Recalculate confidence score based on current conditions
            confidence_score = calculate_confidence_score(signal, symbol_data, indicators, patterns)
            
            # Check if the signal is still valid
            still_valid = is_signal_still_valid(signal, symbol_data)
            
            # Update the signal with fresh analysis
            updated_signal = {
                **signal,
                "current_price": symbol_data["lp"],
                "indicators": indicators,
                "patterns": patterns,
                "confidence_score": confidence_score,
                "is_valid": still_valid,
                "time_to_expiry": calculate_time_to_expiry(signal),
                "last_updated": datetime.now().isoformat()
            }
            
            # Add a field to show if anything has changed
            if updated_signal["confidence_score"] > signal.get("confidence_score", 0) + 5:
                updated_signal["confidence_change"] = "increased"
            elif updated_signal["confidence_score"] < signal.get("confidence_score", 0) - 5:
                updated_signal["confidence_change"] = "decreased"
            else:
                updated_signal["confidence_change"] = "stable"
                
            updated_signals.append(updated_signal)
        
        return updated_signals
        
    except Exception as e:
        print(f"Error refreshing signal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/signals/available")
async def get_available_signals():
    """Get available trading signals based on current market data"""
    try:
        # Process signals for key indices/timeframes
        nifty_swing_result = await nifty_swing.process(auto_execute=False, log_enabled=True)
        banknifty_scalp_result = await banknifty_scalp.process(auto_execute=False, log_enabled=True)
        
        # Combine signals from different processors
        all_signals = []
        
        # Add non-executed signals from each processor
        if nifty_swing_result and "non_executed" in nifty_swing_result:
            # Format signals for frontend compatibility
            for signal in nifty_swing_result["non_executed"]:
                formatted_signal = format_signal_for_frontend(signal, "NIFTY", "swing")
                all_signals.append(formatted_signal)
        
        if banknifty_scalp_result and "non_executed" in banknifty_scalp_result:
            for signal in banknifty_scalp_result["non_executed"]:
                formatted_signal = format_signal_for_frontend(signal, "BANKNIFTY", "scalp")
                all_signals.append(formatted_signal)
        
        # If no signals were found, return sample signals
        if not all_signals:
            print("[WARNING] No signals detected, returning sample signals")
            return get_sample_signals()
            
        return all_signals
    except Exception as e:
        print(f"[ERROR] Failed to get available signals: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return sample signals on error
        return get_sample_signals()

def format_signal_for_frontend(signal, symbol, strategy):
    """Format a signal from the backend format to the frontend expected format"""
    # Get current timestamp if not available
    timestamp = signal.get("trade_time", datetime.now().isoformat())
    
    # Generate a unique ID
    signal_id = f"{symbol.lower()}-{strategy}-{int(time.time())}-{random.randint(1000, 9999)}"
    
    # Map signal type to action
    action = "BUY" if any(s in signal.get("signal", "HOLD") for s in ["BUY", "CALL", "UP"]) else "SELL"
    
    # Determine option type based on signal
    option_type = "CE" if "CALL" in signal.get("signal", "") else "PE"
    
    # Format expiry date (would be dynamic in real implementation)
    expiry_date = "Apr 24th"  # Example static date
    
    # Map confidence to a percentage
    confidence = int(signal.get("confidence", 0.7) * 100)
    
    # Extract indicators from the signal
    indicators = []
    if "indicator_snapshot" in signal:
        for key, value in signal["indicator_snapshot"].items():
            if isinstance(value, bool) and value:
                indicators.append(key.upper())
            elif isinstance(value, str) and "bullish" in value:
                indicators.append(f"{key.upper()} (Bullish)")
            elif isinstance(value, str) and "bearish" in value:
                indicators.append(f"{key.upper()} (Bearish)")
    
    # Extract patterns
    patterns = []
    if "pattern_analysis" in signal and "patterns_detected" in signal["pattern_analysis"]:
        patterns = signal["pattern_analysis"]["patterns_detected"]
    
    # Create frontend-compatible signal
    return {
        "id": signal_id,
        "symbol": symbol,
        "instrumentType": "Option",
        "strike": signal.get("strike", 0),
        "optionType": option_type,
        "action": action,
        "price": signal.get("entry", 0),
        "target_price": signal.get("target", 0),
        "stop_loss": signal.get("stop_loss", 0),
        "quantity": 50 if symbol == "NIFTY" else 25,  # Default quantities
        "potential_return": abs((signal.get("target", 0) - signal.get("entry", 0)) / signal.get("entry", 1)),
        "risk_reward_ratio": signal.get("rrr", 1.5),
        "timeframe": "1hour" if strategy == "swing" else "5min",
        "confidence_score": confidence,
        "indicators": indicators[:4],  # Limit to top 4 indicators
        "patterns": patterns[:2],     # Limit to top 2 patterns
        "strategy": strategy,
        "aiAnalysis": signal.get("ai_opinion", {}).get("reasoning", ""),
        "notes": f"{symbol} {strategy} signal with {signal.get('trend', 'neutral')} trend",
        "timestamp": timestamp,
        "executed": False,
        "expiryDate": expiry_date
    }

def get_sample_signals():
    """Return sample signals when real signals are not available"""
    nifty_signal = {
        "id": f"nifty-swing-{int(time.time())}",
        "symbol": "NIFTY",
        "instrumentType": "Option",
        "strike": 22500,
        "optionType": "CE",
        "action": "BUY",
        "price": 22450.75,
        "target_price": 22500.00,
        "stop_loss": 22400.00,
        "quantity": 50,
        "potential_return": 0.0022,
        "risk_reward_ratio": 1.8,
        "timeframe": "1hour",
        "confidence_score": 85,
        "indicators": ["RSI", "MACD", "VWAP", "Bollinger Bands"],
        "patterns": ["Support Bounce", "Bullish Engulfing"],
        "strategy": "swing",
        "aiAnalysis": "Strong buy signal with multiple indicator confluence and trend support",
        "notes": "NIFTY swing opportunity with strong confirmation",
        "timestamp": datetime.now().isoformat(),
        "executed": False,
        "expiryDate": "Apr 24th"
    }
    
    bank_signal = {
        "id": f"banknifty-scalp-{int(time.time())}",
        "symbol": "BANKNIFTY",
        "instrumentType": "Option",
        "strike": 48500,
        "optionType": "PE",
        "action": "SELL",
        "price": 48750.25,
        "target_price": 48650.00,
        "stop_loss": 48850.00,
        "quantity": 25,
        "potential_return": 0.0020,
        "risk_reward_ratio": 1.5,
        "timeframe": "5min",
        "confidence_score": 78,
        "indicators": ["RSI", "MACD", "EMA Cross"],
        "patterns": ["Resistance Rejection"],
        "strategy": "scalp",
        "notes": "Short-term resistance hit with overbought indicators",
        "timestamp": datetime.now().isoformat(),
        "executed": False,
        "expiryDate": "Apr 24th"
    }
    
    return [nifty_signal, bank_signal]

# Placeholder implementations for the missing functions
async def get_symbol_data(symbol):
    """Get latest market data for a symbol"""
    try:
        # In a real implementation, you would fetch from Fyers API
        return {
            "lp": 22500 if symbol == "NIFTY" else 48750,
            "ch": 50,
            "chp": 0.2
        }
    except Exception as e:
        print(f"Error getting symbol data: {str(e)}")
        return {"lp": 0, "ch": 0, "chp": 0}

def calculate_indicators(data):
    """Calculate technical indicators from market data"""
    # Placeholder implementation
    return ["RSI", "MACD", "EMA Cross", "VWAP"]

def detect_patterns(data):
    """Detect chart patterns from market data"""
    # Placeholder implementation
    return ["Support Bounce", "Bullish Engulfing"]

def calculate_confidence_score(signal, data, indicators, patterns):
    """Calculate confidence score based on current market conditions"""
    # Placeholder implementation - keep existing score or slightly adjust
    base_score = signal.get("confidence_score", 75)
    return base_score + random.randint(-5, 5)

def is_signal_still_valid(signal, data):
    """Check if a signal is still valid based on current price"""
    # Placeholder implementation - most signals remain valid
    return True

def calculate_time_to_expiry(signal):
    """Calculate time to expiry for an option signal"""
    # Placeholder implementation
    return "3 days"

@app.get("/debug/market-data/{index}/{mode}")
async def debug_market_data(index: str, mode: str):
    """Debug endpoint to check real market data"""
    from services.fetch_data import get_data, MOCK_MODE
    import traceback
    
    try:
        print(f"[DEBUG] Fetching {index} {mode} data (MOCK_MODE={MOCK_MODE})")
        data = await get_data(index=index, mode=mode)
        
        # Check if we got candles
        candle_count = len(data.get('candles', []))
        
        # Return useful debug information
        return {
            "status": "success",
            "using_mock_data": MOCK_MODE,
            "candle_count": candle_count,
            "first_candle": data['candles'][0] if candle_count > 0 else None,
            "last_candle": data['candles'][-1] if candle_count > 0 else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }