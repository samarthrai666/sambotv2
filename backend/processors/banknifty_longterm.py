from services.fetch_data import get_data
from utils.signal_analyzer import analyze_signal
from utils.auto_execution_rules import check_auto_rules
from services.fyers_client import place_order
from utils.trade_journal import log_trade
from ml.predict_ml_signal import predict_signal_ml
async def process(auto_execute: bool):
    data = await get_data(index="BANKNIFTY", mode="longterm")
    signal = analyze_signal(data, index="BANKNIFTY", mode="longterm")

    executed, non_executed = [], []

    if signal:
        if auto_execute and check_auto_rules(signal):
            place_order(signal)
            executed.append(signal)
        else:
            non_executed.append(signal)

    return { "executed": executed, "non_executed": non_executed }
