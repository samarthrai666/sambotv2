import os
import json
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

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
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[MOCK WARNING] File not found: {file_path}")
        return { "candles": [] }

async def get_data(index: str, mode: str):
    if MOCK_MODE:
        print(f"[MOCK MODE] Loading mock data for {index} - {mode}")
        return load_mock_data(index, mode)

    symbol_map = {
        "NIFTY": "NSE:NIFTY50-INDEX",
        "BANKNIFTY": "NSE:BANKNIFTY-INDEX"
    }

    resolution = get_resolution(mode)
    from_date, to_date = get_date_range(mode)

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

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FYERS_BASE_URL}/history", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
