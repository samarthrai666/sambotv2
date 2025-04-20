from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict
import asyncio

from processors import (
    nifty_scalp, nifty_swing, nifty_longterm,
    banknifty_scalp, banknifty_swing, banknifty_longterm
)

app = FastAPI()

# 📦 Define request model
class TradeModeRequest(BaseModel):
    nifty: List[str] = []
    banknifty: List[str] = []
    auto_execute: bool

# 🧠 Processor map
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

    # 🧩 Check and queue up all processors from request
    for mode in req.nifty:
        key = f"nifty_{mode}"
        if key in strategy_map:
            tasks.append(asyncio.create_task(strategy_map[key](req.auto_execute)))

    for mode in req.banknifty:
        key = f"banknifty_{mode}"
        if key in strategy_map:
            tasks.append(asyncio.create_task(strategy_map[key](req.auto_execute)))

    # 🚀 Run all selected processors in parallel
    results = await asyncio.gather(*tasks)

    # 🔄 Merge results
    executed_signals = []
    non_executed_signals = []

    for res in results:
        executed_signals.extend(res.get("executed", []))
        non_executed_signals.extend(res.get("non_executed", []))

    return {
        "executed_signals": executed_signals,
        "non_executed_signals": non_executed_signals
    }

