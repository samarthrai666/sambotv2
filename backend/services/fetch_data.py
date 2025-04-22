import os
import json
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv
import traceback

load_dotenv()

FYERS_BASE_URL = os.getenv("FYERS_BASE_URL", "https://api.fyers.in/api/v2")
FYERS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")
MOCK_MODE = os.getenv("MOCK_FYERS", "false").lower() == "true"

def get_resolution(mode: str):
    return {
        "scalp": "1",
        "swing": "15",
        "longterm": "D"
    }.get(mode, "1")

def get_date_range(mode: str):
    today = datetime.now()
    if mode == "scalp":
        return (today - timedelta(days=1), today)
    elif mode == "swing":
        return (today - timedelta(days=7), today)
    else:
        return (today - timedelta(days=90), today)

def load_mock_data(index: str, mode: str):
    file_path = f"mockdata/{index.lower()}_{mode.lower()}.json"
    try:
        print(f"[MOCK] Loading mock data from {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)
            print(f"[MOCK] Loaded {len(data.get('candles', []))} candles")
            return data
    except FileNotFoundError:
        print(f"[MOCK WARNING] File not found: {file_path}")
        return { "candles": [] }
    except Exception as e:
        print(f"[MOCK ERROR] Failed to load mock data: {str(e)}")
        traceback.print_exc()
        return { "candles": [] }

async def get_data(index: str, mode: str):
    print(f"\n===== DEBUGGING FETCH_DATA =====")
    print(f"[INFO] Fetching data for {index} - {mode}")
    print(f"MOCK_MODE value: {MOCK_MODE}")
    print(f"MOCK_MODE source: {'Environment var' if os.getenv('MOCK_FYERS') else 'Default'}")
    print(f"FYERS_TOKEN exists: {bool(FYERS_TOKEN)}")
    print(f"FYERS_TOKEN length: {len(FYERS_TOKEN) if FYERS_TOKEN else 0}")

    if MOCK_MODE:
        return load_mock_data(index, mode)

    if not FYERS_TOKEN:
        print("[ERROR] FYERS_ACCESS_TOKEN is not set.")
        return load_mock_data(index, mode)

    try:
        # Import and initialize Fyers SDK
        from fyers_apiv3 import fyersModel
        
        client_id = os.getenv("FYERS_CLIENT_ID")
        if not client_id:
            print("[ERROR] FYERS_CLIENT_ID is not set.")
            return load_mock_data(index, mode)
            
        fyers = fyersModel.FyersModel(client_id=client_id, token=FYERS_TOKEN, is_async=False, log_path="")
        
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }

        if index.upper() not in symbol_map:
            print(f"[ERROR] Unknown index: {index}")
            return { "candles": [] }

        # Map mode to resolution according to documentation
        resolution_map = {
            "scalp": "1",  # 1-minute for scalping
            "swing": "60",  # 1-hour for swing
            "longterm": "D"  # Daily for long-term
        }
        resolution = resolution_map.get(mode, "1")
        
        from_date, to_date = get_date_range(mode)
        
        # Format dates according to documentation (use date_format=1 for YYYY-MM-DD)
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')
        
        print(f"[API] Using Fyers SDK to get history data for {symbol_map[index.upper()]}")
        print(f"[API] Dates: {from_date_str} to {to_date_str}, Resolution: {resolution}")
        
        # Prepare request using the exact format from documentation
        history_params = {
            "symbol": symbol_map[index.upper()],
            "resolution": resolution,
            "date_format": 1,  # Use YYYY-MM-DD format
            "range_from": from_date_str,
            "range_to": to_date_str,
            "cont_flag": 1  # Documentation shows this as an int
        }
        
        print(f"[API] Request params: {history_params}")
        
        history_data = fyers.history(data=history_params)
        
        print(f"[API] Response type: {type(history_data)}")
        if isinstance(history_data, dict):
            print(f"[API] Response keys: {list(history_data.keys())}")
            print(f"[API] Status: {history_data.get('s', 'unknown')}")
        else:
            print(f"[API] Non-dict response: {history_data}")
        
        # Check if the response was successful
        if not isinstance(history_data, dict) or history_data.get("s") != "ok":
            error_msg = history_data.get("message", str(history_data)) if isinstance(history_data, dict) else str(history_data)
            print(f"[API ERROR] Failed to get history data: {error_msg}")
            return load_mock_data(index, mode)
        
        # Extract candles from the response
        candles = history_data.get("candles", [])
        if not candles:
            print(f"[API WARNING] No candles returned")
            return load_mock_data(index, mode)
        
        print(f"[API] ✅ {len(candles)} candles fetched successfully.")
        
        # Return in the expected format
        return {"candles": candles}

    except Exception as e:
        print(f"[ERROR] Exception occurred while fetching data: {str(e)}")
        traceback.print_exc()
        return load_mock_data(index, mode)
