# backend/utils/filternsestocks.py

import os
import pandas as pd
from typing import List, Dict, Any

def filter_stocks(preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter stocks based on user preferences (sector, market cap, etc.)
    
    Parameters:
    -----------
    preferences : Dict[str, Any]
        User preferences containing filtering criteria
        
    Returns:
    --------
    List[Dict[str, Any]]: Filtered list of stock data
    """
    try:
        print(f"[DEBUG] Filtering stocks with preferences: {preferences}")
        
        # Check if equity and swing trading are enabled
        equity_enabled = preferences.get("equity", {}).get("enabled", False)
        swing_enabled = preferences.get("equity", {}).get("swing", {}).get("enabled", False)
        
        if not equity_enabled or not swing_enabled:
            print("[INFO] Equity or swing trading not enabled, returning no stocks")
            return []
            
        # Default path for the CSV file
        csv_path = os.path.join(os.path.dirname(__file__), "../data/top500_nse_stocks.csv")
        
        # Check if the file exists
        if not os.path.exists(csv_path):
            print(f"[WARNING] NSE stocks CSV file not found at {csv_path}")
            # Try alternative paths
            alternative_paths = [
                "top500_nse_stocks.csv",                # Current directory
                "../data/top500_nse_stocks.csv",        # Parent directory
                "data/top500_nse_stocks.csv",           # Data subdirectory
                "backend/data/top500_nse_stocks.csv",   # Backend data directory
                "data/nse_stocks.csv"                   # Alternative filename
            ]
            
            for alt_path in alternative_paths:
                if os.path.exists(alt_path):
                    csv_path = alt_path
                    print(f"[INFO] Found CSV file at alternative path: {csv_path}")
                    break
            else:
                print(f"[WARNING] NSE stocks CSV file not found in any location")
                return []

        # Read the CSV file
        df = pd.read_csv(csv_path)
        original_count = len(df)
        print(f"[INFO] Loaded {original_count} stocks from CSV file")
        
        # Print csv file structure
        print(f"[DEBUG] CSV columns: {df.columns.tolist()}")
        print(f"[DEBUG] Sample data:\n{df.head(2)}")
        
        # Get equity swing preferences
        equity_prefs = preferences.get("equity", {}).get("swing", {})
        print(f"[DEBUG] Using swing equity preferences: {equity_prefs}")
        
        # Filter by sector if specified and sectors list is not empty
        selected_sectors = equity_prefs.get("sectors", [])
        if selected_sectors and len(selected_sectors) > 0:
            print(f"[INFO] Filtering by sectors: {selected_sectors}")
            
            # Create a mask for sector matching
            sector_mask = df['sector'].str.lower().isin([s.lower() for s in selected_sectors])
            
            # Also try partial matching if exact matching gives no results
            if not any(sector_mask):
                print(f"[INFO] No exact sector matches found, trying partial matching")
                sector_mask = pd.Series(False, index=df.index)
                for sector in selected_sectors:
                    sector_lower = sector.lower()
                    sector_mask = sector_mask | df['sector'].str.lower().str.contains(sector_lower, na=False)
            
            # Apply the sector filter
            df = df[sector_mask]
            print(f"[INFO] After sector filter: {len(df)} stocks remaining")
            
            # If no stocks match, print available sectors for debugging
            if len(df) == 0:
                available_sectors = df['sector'].unique().tolist()
                print(f"[DEBUG] Available sectors in CSV: {available_sectors}")
                return []
        
        # Filter by market cap if specified and market_caps list is not empty
        selected_caps = equity_prefs.get("market_caps", [])
        if selected_caps and len(selected_caps) > 0:
            print(f"[INFO] Filtering by market caps: {selected_caps}")
            
            # Create a mask for market cap matching - case insensitive
            market_cap_mask = df['market_cap_category'].str.lower().isin([c.lower() for c in selected_caps])
            
            # Apply the market cap filter
            df = df[market_cap_mask]
            print(f"[INFO] After market cap filter: {len(df)} stocks remaining")
            
            # If no stocks match, print available market caps for debugging
            if len(df) == 0:
                available_caps = df['market_cap_category'].unique().tolist()
                print(f"[DEBUG] Available market caps in CSV: {available_caps}")
                return []
        
        # Limit the number of stocks if specified
        max_stocks = equity_prefs.get("max_stocks", 5)
        if len(df) > max_stocks:
            df = df.sample(max_stocks, random_state=42)
            print(f"[INFO] Limited to {max_stocks} random stocks")
        
        # Convert DataFrame to list of dictionaries
        filtered_stocks = df.to_dict(orient="records")
        print(f"[INFO] Final filtered stocks count: {len(filtered_stocks)}")
        
        # Log the filtered stocks for debugging
        if filtered_stocks:
            print(f"[DEBUG] Filtered stock symbols: {[s.get('symbol', 'N/A') for s in filtered_stocks]}")
            print(f"[DEBUG] Filtered stock sectors: {[s.get('sector', 'N/A') for s in filtered_stocks]}")
            print(f"[DEBUG] Filtered stock market caps: {[s.get('market_cap_category', 'N/A') for s in filtered_stocks]}")
        
        return filtered_stocks
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Error filtering stocks: {str(e)}")
        return []