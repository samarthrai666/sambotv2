# In backend/services/fyers_client.py
from fyers_apiv3 import fyersModel
import os

# Use your existing client setup from fii_dii.py
client_id = os.getenv("FYERS_CLIENT_ID")
access_token = os.getenv("FYERS_ACCESS_TOKEN")
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path="")

def place_order(signal: dict):
    """Place real order with Fyers API"""
    try:
        # Convert signal to Fyers order format
        order_data = {
            "symbol": f"NSE:{signal['index']}-INDEX",
            "qty": signal.get('quantity', 1),
            "type": 1,  # 1 for Market, 2 for Limit
            "side": 1 if "BUY" in signal['signal'] else -1,  # 1 for Buy, -1 for Sell
            "productType": "INTRADAY",  # Or "CNC" for delivery
            "limitPrice": 0,  # For Market orders
            "stopPrice": 0,   # For Market orders
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False
        }
        
        # Add stop loss if provided
        if 'stop_loss' in signal:
            order_data["stopLoss"] = signal['stop_loss']
            
        # Add target if provided
        if 'target' in signal:
            order_data["takeProfit"] = signal['target']
        
        # Place the order
        response = fyers.place_order(order_data)
        
        print(f"[ORDER PLACED] {signal['signal']} → {signal['index']} | Response: {response}")
        return response
        
    except Exception as e:
        print(f"[ORDER ERROR] Failed to place order: {str(e)}")
        raise e