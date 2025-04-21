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


cached_data = None
last_updated = 0
refresh_interval = 3 # seconds

# Load .env configs
load_dotenv()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
FYERS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")
FYERS_BASE_URL = os.getenv("FYERS_BASE_URL", "https://api.fyers.in/api/v2")
MOCK_MODE = os.getenv("MOCK_FYERS", "true").lower() == "true"

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
    tasks = []

    # 🧩 Add all selected processors
    for mode in req.nifty:
        key = f"nifty_{mode}"
        if key in strategy_map:
            tasks.append(asyncio.create_task(
                strategy_map[key](req.auto_execute, req.log_enabled)
            ))

    for mode in req.banknifty:
        key = f"banknifty_{mode}"
        if key in strategy_map:
            tasks.append(asyncio.create_task(
                strategy_map[key](req.auto_execute, req.log_enabled)
            ))

    # 🚀 Run all processors concurrently
    results = await asyncio.gather(*tasks)

    # 🔄 Merge results
    executed_signals = []
    non_executed_signals = []

    for res in results:
        executed_signals.extend(res.get("executed", []))
        non_executed_signals.extend(res.get("non_executed", []))

    return {
        "executed_signals": executed_signals,
        "non_executed_signals": non_executed_signals,
        "ai_enabled": AI_ENABLED
    }

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