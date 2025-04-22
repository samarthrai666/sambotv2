# For /Users/samarthrai/SamBotv2/backend/modules/option_chain.py

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

def analyze_option_chain(symbol="NIFTY", expiry_date=None, num_grid_levels=5):
    """
    Analyze option chain data and return grid levels and insights
    
    Parameters:
    -----------
    symbol : str
        Symbol name (NIFTY, BANKNIFTY, etc.)
    expiry_date : str, optional
        Expiry date in format 'DD-MMM-YYYY', defaults to nearest expiry
    num_grid_levels : int
        Number of grid levels to generate
    
    Returns:
    --------
    dict: Analysis results with grid levels and key insights
    """
    try:
        # For now, return some placeholder data
        # You can enhance this with real option chain analysis later
        
        # Mock spot price
        if symbol == "NIFTY":
            spot_price = 22450.75
        elif symbol == "BANKNIFTY":
            spot_price = 48325.60
        else:
            spot_price = 2000.00
            
        # Mock expiry date
        if not expiry_date:
            expiry_date = "25-Apr-2025"
            
        # Generate mock grid levels
        grid_levels = []
        spread = spot_price * 0.05  # 5% range
        
        for i in range(num_grid_levels):
            level_price = spot_price - spread + (2 * spread * i / (num_grid_levels - 1))
            
            # Determine action based on price
            if level_price < spot_price:
                action = "BUY"
                conviction = 80 + (spot_price - level_price) / spread * 15
            elif level_price > spot_price:
                action = "SELL"
                conviction = 80 + (level_price - spot_price) / spread * 15
            else:
                action = "NEUTRAL"
                conviction = 50
                
            deviation = (level_price - spot_price) / spot_price * 100
                
            grid_levels.append({
                "level": i + 1,
                "price": f"{level_price:.2f}",
                "action": action,
                "deviation": f"{deviation:.2f}%",
                "conviction": f"{min(conviction, 95):.0f}%",
                "allocation": f"{100/num_grid_levels:.1f}%",
                "source": "Mock Data"
            })
        
        # Create summary data
        result = {
            "symbol": symbol,
            "spot_price": spot_price,
            "expiry_date": expiry_date,
            "expiry_days": 30,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "key_insights": {
                "max_pain": {
                    "level": spot_price * 1.01,
                    "impact": "Slightly Bullish - Max pain slightly above spot"
                },
                "iv_skew": {
                    "skew_ratio": 1.05,
                    "interpretation": "Slightly Bearish - Moderately higher put premiums"
                },
                "market_sentiment": {
                    "score": "55.0/100",
                    "sentiment": "Slightly Bullish"
                }
            },
            "grid_levels": grid_levels
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        # Return error information
        return {
            "status": "error",
            "message": str(e)
        }