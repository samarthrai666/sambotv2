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
    file_path = f"mock_data/{index.lower()}_{mode.lower()}.json"
    try:
        print(f"[MOCK] Loading mock data from {file_path}")
        with open(file_path, "r") as f:
            data = json.load(f)
            print(f"[MOCK] Loaded {len(data.get('candles', []))} candles")
            return data
    except FileNotFoundError:
        print(f"[MOCK WARNING] File not found: {file_path}")
        # Create a minimal mock structure to avoid null pointer exceptions
        return { "candles": [] }
    except Exception as e:
        print(f"[MOCK ERROR] Failed to load mock data: {str(e)}")
        traceback.print_exc()
        return { "candles": [] }

async def get_data(index: str, mode: str):
    print(f"[INFO] Fetching data for {index} - {mode} (MOCK_MODE={MOCK_MODE})")
    
    if MOCK_MODE:
        print(f"[MOCK MODE] Loading mock data for {index} - {mode}")
        return load_mock_data(index, mode)

    # Check if API token is set
    if not FYERS_TOKEN:
        print("[ERROR] FYERS_ACCESS_TOKEN is not set in environment variables")
        return load_mock_data(index, mode)  # Fall back to mock data
    
    try:
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:BANKNIFTY-INDEX"
        }

        if index not in symbol_map:
            print(f"[ERROR] Unknown index: {index}")
            return { "candles": [] }

        resolution = get_resolution(mode)
        from_date, to_date = get_date_range(mode)

        print(f"[API] Fetching {index} {mode} data from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')} with resolution {resolution}")

        payload = {
            "symbol": symbol_map[index],
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

        print(f"[API] Sending request to {FYERS_BASE_URL}/history")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FYERS_BASE_URL}/history", json=payload, headers=headers)
            
            print(f"[API] Received response with status code {response.status_code}")
            
            if response.status_code != 200:
                print(f"[API ERROR] Non-200 status code: {response.status_code}")
                print(f"[API ERROR] Response body: {response.text}")
                # Fall back to mock data on API error
                return load_mock_data(index, mode)
                
            response.raise_for_status()
            data = response.json()
            
            # Validate response structure
            if "candles" not in data or not data["candles"]:
                print(f"[API WARNING] Missing or empty candles in response: {data}")
                # If API returns invalid structure, fall back to mock
                return load_mock_data(index, mode)
                
            print(f"[API] Successfully fetched {len(data['candles'])} candles")
            return data
            
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {index} - {mode}: {str(e)}")
        traceback.print_exc()
        # Fall back to mock data on any exception
        return load_mock_data(index, mode)