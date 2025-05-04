# backend/utils/filternsestocks.py
import csv
import os
import random
from typing import List, Dict, Any

# Path to the NSE stocks CSV file
NSE_STOCKS_CSV_PATH = "data/top500_nse_stocks.csv"

def get_stocks_by_filters(sectors: List[str] = None, market_caps: List[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Filter NSE stocks by sector and market capitalization

    Args:
        sectors (List[str], optional): List of sectors to filter by from trading preferences
        market_caps (List[str], optional): List of market cap categories to filter by
                                         (largecap, midcap, smallcap)
        limit (int, optional): Maximum number of stocks to return

    Returns:
        List[Dict[str, Any]]: List of filtered stocks
    """
    print(f"Starting filter with sectors: {sectors}")
    print(f"Market caps: {market_caps}")
    print(f"Limit: {limit}")
    print(f"Looking for CSV at: {os.path.abspath(NSE_STOCKS_CSV_PATH)}")

    stocks = load_stocks_from_csv()

    if stocks:
        print(f"Successfully loaded {len(stocks)} stocks")
        print(f"First few stocks: {stocks[:3]}")

        available_sectors = set(stock.get('sector', '').strip() for stock in stocks)
        print(f"Available sectors in CSV: {sorted(list(available_sectors))}")
    else:
        print("WARNING: No stocks were loaded from CSV")
        return []

    filtered_stocks = stocks

    if sectors is not None and len(sectors) > 0:
        lowercase_sectors = [s.strip().lower() for s in sectors]
        old_count = len(filtered_stocks)
        filtered_stocks = [
            s for s in filtered_stocks 
            if s.get("sector", "").strip().lower() in lowercase_sectors
        ]
        print(f"Sector filter: {old_count} → {len(filtered_stocks)} stocks")
        print(f"Requested sectors: {sectors}")
        matched_sectors = set(s.get("sector", "").strip() for s in filtered_stocks)
        print(f"Matched sectors: {matched_sectors}")

    if market_caps is not None and len(market_caps) > 0:
        lowercase_market_caps = [mc.strip().lower() for mc in market_caps]
        old_count = len(filtered_stocks)
        filtered_stocks = [
            s for s in filtered_stocks 
            if s.get("market_cap_category", "").strip().lower() in lowercase_market_caps
        ]
        print(f"Market cap filter: {old_count} → {len(filtered_stocks)} stocks")
        matched_caps = set(s.get("market_cap_category", "").strip() for s in filtered_stocks)
        print(f"Matched market caps: {matched_caps}")

    if len(filtered_stocks) < limit:
        print(f"Warning: Only {len(filtered_stocks)} stocks match the filters (requested {limit})")

    if filtered_stocks:
        random.shuffle(filtered_stocks)

    result = filtered_stocks[:limit]
    if result:
        print(f"Final filtered stocks ({len(result)}):")
        for s in result:
            print(f"  - {s.get('symbol')}: {s.get('sector')} ({s.get('market_cap_category')})")
    else:
        print("No stocks match the filters!")

    return result

def load_stocks_from_csv() -> List[Dict[str, Any]]:
    stocks = []

    try:
        if not os.path.exists(NSE_STOCKS_CSV_PATH):
            print(f"Error: CSV file not found at {NSE_STOCKS_CSV_PATH}")
            potential_locations = [
                "data/top500_nse_stocks.csv",
                "./data/top500_nse_stocks.csv",
                "../data/top500_nse_stocks.csv",
                "../../data/top500_nse_stocks.csv",
                "top500_nse_stocks.csv",
                "./top500_nse_stocks.csv"
            ]
            for location in potential_locations:
                if os.path.exists(location):
                    print(f"Found CSV at alternate location: {location}")
                    globals()["NSE_STOCKS_CSV_PATH"] = location
                    break
            if not os.path.exists(NSE_STOCKS_CSV_PATH):
                print(f"Could not find CSV in any common locations. Current directory: {os.getcwd()}")
                return []

        with open(NSE_STOCKS_CSV_PATH, 'r', encoding='utf-8') as csvfile:
            first_line = csvfile.readline().strip()
            print(f"CSV first line: {first_line}")
            csvfile.seek(0)
            delimiter = ',' if ',' in first_line else ';'
            print(f"Using delimiter: '{delimiter}'")

            reader = csv.DictReader(csvfile, delimiter=delimiter)
            print(f"CSV columns: {reader.fieldnames}")

            for row in reader:
                stock = {
                    "symbol": row.get("symbol", "").strip(),
                    "name": row.get("company", "").strip(),
                    "sector": row.get("sector", "").strip(),
                    "market_cap_category": row.get("market_cap_category", "").strip()
                }
                if len(stocks) == 0:
                    print(f"Sample CSV row: {row}")
                    print(f"Converted to stock object: {stock}")
                stocks.append(stock)

        print(f"Successfully loaded {len(stocks)} stocks from CSV")
        return stocks

    except Exception as e:
        print(f"Error loading stocks from CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("\n=== TESTING FILTER FUNCTION ===\n")
    test_filters = [
        {"sectors": ["Information Technology", "Financial Services"], "market_caps": ["Largecap"]},
        {"sectors": ["Power"], "market_caps": ["Midcap", "Smallcap"]},
        {"sectors": None, "market_caps": ["Largecap"]},
        {"sectors": ["Healthcare"], "market_caps": None},
        {"sectors": None, "market_caps": None}
    ]
    for i, filters in enumerate(test_filters):
        print(f"\n--- Test {i+1} ---")
        results = get_stocks_by_filters(
            sectors=filters["sectors"], 
            market_caps=filters["market_caps"],
            limit=5
        )
        print(f"\nTest {i+1} Results: Sectors={filters['sectors']}, Market Caps={filters['market_caps']}")
        print(f"Found {len(results)} stocks")
