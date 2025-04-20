from services.fetch_data import get_data
from services.signal_analyzer import analyze_signal
from utils.auto_execution_rules import check_auto_rules
from utils.fyers_client import place_order

async def process(auto_execute: bool):
    data = await get_data(index="NIFTY", mode="longterm")
    signal = analyze_signal(data, index="NIFTY", mode="longterm")

    executed, non_executed = [], []

    if signal:
        if auto_execute and check_auto_rules(signal):
            place_order(signal)
            executed.append(signal)
        else:
            non_executed.append(signal)

    return { "executed": executed, "non_executed": non_executed }
