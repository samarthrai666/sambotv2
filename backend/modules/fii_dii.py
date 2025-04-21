# In backend/modules/fii_dii.py
def fetch_fii_dii_sentiment():
    """Fetch FII/DII activity data from Fyers API"""
    try:
        # This endpoint may vary depending on Fyers API availability
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Make API call to get FII/DII data
        response = fyers.get_market_depth() # replace with actual endpoint
        
        # Process and return data
        return {
            "fii": {
                "buy_value": response["fii_buy_value"],
                "sell_value": response["fii_sell_value"],
                "net_value": response["fii_net_value"]
            },
            "dii": {
                "buy_value": response["dii_buy_value"],
                "sell_value": response["dii_sell_value"],
                "net_value": response["dii_net_value"]
            },
            "sentiment": "bullish" if response["fii_net_value"] > 0 else "bearish"
        }
    except Exception as e:
        print(f"[FII/DII ERROR] {str(e)}")
        # Return fallback data
        return {
            "fii": {"net_value": 0},
            "dii": {"net_value": 0},
            "sentiment": "neutral",
            "error": str(e)
        }