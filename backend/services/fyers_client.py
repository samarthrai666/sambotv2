def place_order(signal: dict):
    """
    Dummy Fyers order executor.
    Replace with real Fyers API integration later.
    """
    print(f"[ORDER PLACED] {signal['signal_type']} → {signal['index']} | Entry: {signal['entry']} | Target: {signal['target']} | SL: {signal['stop_loss']} | Confidence: {signal['confidence']}")
