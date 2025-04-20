import csv
import os
from datetime import datetime

JOURNAL_FILE = "data/trade_journal.csv"

def log_trade(signal: dict, executed: bool, result: str = "PENDING"):
    """
    Appends trade signal to journal for feedback loop training.
    """
    os.makedirs("data", exist_ok=True)

    fields = [
        "timestamp", "index", "mode", "signal", "entry", "target", "stop_loss", "executed",
        "ml_signal", "ml_confidence", "exit_price", "result"
    ]

    data = {
        "timestamp": datetime.now().isoformat(),
        "index": signal.get("index", "NIFTY"),
        "mode": signal.get("mode", "swing"),
        "signal": signal.get("signal", ""),
        "entry": signal.get("entry", 0),
        "target": signal.get("target", 0),
        "stop_loss": signal.get("stop_loss", 0),
        "executed": executed,
        "ml_signal": signal.get("ml_prediction", {}).get("ml_signal", ""),
        "ml_confidence": signal.get("ml_prediction", {}).get("confidence", 0),
        "exit_price": signal.get("exit_price", 0),  # can be updated later
        "result": result  # WIN, LOSS, or HOLD
    }

    # Write header if file doesn't exist
    write_header = not os.path.exists(JOURNAL_FILE)

    with open(JOURNAL_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(data)

    print(f"[📝] Logged trade signal for {data['index']} ({data['mode']})")
