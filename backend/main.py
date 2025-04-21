from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
import os
from dotenv import load_dotenv


# Load .env configs
load_dotenv()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"

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

@app.post("/signal/execute/{signal_id}")
async def execute_signal(signal_id: str):
    try:
        # This is a placeholder. You would typically:
        # 1. Retrieve the signal from a database
        # 2. Check if the signal is valid
        # 3. Place the order
        # 4. Return the order details
        
        # Dummy implementation
        from utils.fyers_client import place_order
        
        # Create a dummy signal for now
        signal = {
            "id": signal_id,
            "signal_type": "BUY CALL",
            "index": "NIFTY",
            "entry": 17865.50,
            "target": 17985.88,
            "stop_loss": 17785.25,
            "confidence": 0.91
        }
        
        place_order(signal)
        
        return {
            "order_id": f"ORD-{signal_id[:8]}",
            "status": "success",
            "message": "Trade executed successfully",
            "executed_at": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/data")
async def get_market_data():
    try:
        # This is a placeholder. You would typically:
        # 1. Fetch current market data from your data provider
        # 2. Format it according to your frontend's expectations
        
        # Dummy implementation
        from services.fetch_data import get_data
        
        # For a real implementation, you'd get actual market data
        # Placeholder values for now
        now = datetime.datetime.now()
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        is_market_open = market_open <= now <= market_close
        
        return {
            "nifty": {
                "price": 23412.65,
                "change": 142.50,
                "changePercent": 0.61
            },
            "banknifty": {
                "price": 48723.90,
                "change": -104.80,
                "changePercent": -0.21
            },
            "marketStatus": "open" if is_market_open else "closed",
            "marketOpenTime": "09:15:00",
            "marketCloseTime": "15:30:00",
            "serverTime": now.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))