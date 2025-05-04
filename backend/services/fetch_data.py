import os
import traceback
from datetime import datetime, timedelta

FYERS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")


def get_date_range(mode):
    today = datetime.now()
    if mode == "scalp":
        return today - timedelta(days=15), today
    elif mode == "swing":
        return today - timedelta(days=45), today
    elif mode == "longterm":
        return today - timedelta(days=120), today
    else:
        return today - timedelta(days=15), today


async def get_data(index: str, mode: str):
    """
    Fetch historical price data from Fyers API

    Parameters:
    -----------
    index: str
        The index to fetch data for (NIFTY or BANKNIFTY)
    mode: str
        Trading mode (scalp, swing, longterm)

    Returns:
    --------
    dict: Dictionary containing candles data
    """
    print(f"\n===== FETCHING MARKET DATA =====")
    print(f"[INFO] Fetching data for {index} - {mode}")

    # Validate credentials
    if not FYERS_TOKEN:
        raise ValueError("FYERS_ACCESS_TOKEN is not set. Please set this environment variable.")

    client_id = os.getenv("FYERS_CLIENT_ID")
    if not client_id:
        raise ValueError("FYERS_CLIENT_ID is not set. Please set this environment variable.")

    try:
        # Import and initialize Fyers SDK
        from fyers_apiv3 import fyersModel

        fyers = fyersModel.FyersModel(client_id=client_id, token=FYERS_TOKEN, is_async=False, log_path="")

        # Map index to symbol
        symbol_map = {
            "NIFTY": "NSE:NIFTY50-INDEX",
            "BANKNIFTY": "NSE:NIFTYBANK-INDEX"
        }

        if index.upper() not in symbol_map:
            raise ValueError(f"Unknown index: {index}. Supported indices are NIFTY and BANKNIFTY.")

        # Map mode to resolution
        resolution_map = {
            "scalp": "1",   # 1-minute for scalping
            "swing": "5",   # 5-minute for swing
            "longterm": "15" # 15-minute for long-term analysis (or use "D" if needed)
        }
        resolution = resolution_map.get(mode, "1")

        from_date, to_date = get_date_range(mode)

        # Format dates according to documentation (use date_format=1 for YYYY-MM-DD)
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')

        print(f"[API] Fetching {symbol_map[index.upper()]} data from {from_date_str} to {to_date_str} (Resolution: {resolution})")

        # Prepare request
        history_params = {
            "symbol": symbol_map[index.upper()],
            "resolution": resolution,
            "date_format": 1,  # Use YYYY-MM-DD format
            "range_from": from_date_str,
            "range_to": to_date_str,
            "cont_flag": 1
        }

        # Make the API call
        history_data = fyers.history(data=history_params)

        # Validate response
        if not isinstance(history_data, dict) or history_data.get("s") != "ok":
            error_msg = history_data.get("message", str(history_data)) if isinstance(history_data, dict) else str(history_data)
            raise ValueError(f"Failed to get history data: {error_msg}")

        # Extract candles
        candles = history_data.get("candles", [])
        if not candles:
            raise ValueError("No candles returned from API")

        print(f"[SUCCESS] {len(candles)} candles fetched successfully")

        return {"candles": candles}

    except Exception as e:
        print(f"[ERROR] Exception occurred while fetching data: {str(e)}")
        traceback.print_exc()
        raise
