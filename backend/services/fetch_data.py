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
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }

        if index.upper() not in symbol_map:
            print(f"[ERROR] Unknown index: {index}")
            return { "candles": [] }

        resolution = get_resolution(mode)
        from_date, to_date = get_date_range(mode)

        payload = {
            "symbol": symbol_map[index.upper()],
            "resolution": resolution,
            "date_format": 1,
            "range_from": from_date.strftime('%Y-%m-%d'),
            "range_to": to_date.strftime('%Y-%m-%d'),
            "cont_flag": "1"
        }

        headers = {
            "Authorization": f"Bearer {FYERS_TOKEN}",
            "Content-Type": "application/json"
        }

        print(f"[API] Sending POST to {FYERS_BASE_URL}/history with payload:")
        print(json.dumps(payload, indent=2))

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FYERS_BASE_URL}/history", json=payload, headers=headers)
            print(f"[API] Status code: {response.status_code}")

            if response.status_code != 200:
                print(f"[API ERROR] {response.status_code}: {response.text}")
                return load_mock_data(index, mode)

            data = response.json()
            candles = data.get("candles", [])
            if not candles:
                print(f"[API WARNING] No candles returned")
                return load_mock_data(index, mode)

            print(f"[API] ✅ {len(candles)} candles fetched successfully.")
            return data

    except Exception as e:
        print(f"[ERROR] Exception occurred while fetching data: {str(e)}")
        traceback.print_exc()
        return load_mock_data(index, mode)
