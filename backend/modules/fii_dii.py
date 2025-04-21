# backend/modules/fii_dii.py

def fetch_fii_dii_sentiment():
    """Fetch FII/DII activity data or return fallback data if unavailable"""
    try:
        # In a real implementation, you would fetch FII/DII data from an API
        # For now, return fallback data
        
        # Sample data structure
        return {
            "fii": {
                "buy_value": 15423.68,
                "sell_value": 14567.45,
                "net_value": 856.23,
                "trend": "buying"
            },
            "dii": {
                "buy_value": 12654.32,
                "sell_value": 13109.67,
                "net_value": -455.35,
                "trend": "selling"
            },
            "sentiment": "bullish",
            "market_impact": "Positive - FII buying outweighs DII selling",
            "date": "2023-04-21"  # Would be current date in real implementation
        }
    except Exception as e:
        print(f"[FII/DII ERROR] {str(e)}")
        # Return fallback data
        return {
            "fii": {"net_value": 0, "trend": "neutral"},
            "dii": {"net_value": 0, "trend": "neutral"},
            "sentiment": "neutral",
            "error": str(e)
        }