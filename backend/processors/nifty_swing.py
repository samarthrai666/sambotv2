from services.fetch_data import get_data
from utils.signal_analyzer import analyze_signal
from utils.auto_execution_rules import check_auto_rules
from services.fyers_client import place_order
from utils.trade_journal import log_trade
from ml.predict_ml_signal import predict_signal_ml
import os
from dotenv import load_dotenv

load_dotenv()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"

async def process(auto_execute: bool, log_enabled: bool = True):
    data = await get_data(index="NIFTY", mode="swing")

    # 🔍 Technical signal
    signal = analyze_signal(data, index="NIFTY", mode="swing")

    # 🧠 Inject AI signal (always enabled via .env)
    if AI_ENABLED:
        ml_signal = predict_signal_ml(data)
        if ml_signal:
            signal["ml_prediction"] = ml_signal

    executed, non_executed = [], []
    is_executed = False

    if signal:
        if auto_execute and check_auto_rules(signal):
            place_order(signal)
            executed.append(signal)
            is_executed = True
        else:
            non_executed.append(signal)

        # 🧾 Log to journal
        if log_enabled:
            log_trade(signal, executed=is_executed)

    return { "executed": executed, "non_executed": non_executed }
