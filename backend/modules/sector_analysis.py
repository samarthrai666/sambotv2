# backend/modules/sector_analysis.py
from typing import Dict, List, Any

def analyze_sectors(index: str) -> Dict[str, Any]:
    """
    Analyze sector performance relative to the main index
    
    Parameters:
    -----------
    index : str
        The index to analyze sectors for (NIFTY or BANKNIFTY)
        
    Returns:
    --------
    dict: Sector performance analysis
    """
    try:
        # In a real implementation, you would fetch sector data from an API
        # For now, return fallback data
        
        # Simulated sector performance data
        sectors = {
            "IT": {
                "performance_today": 1.2,
                "performance_week": -0.8,
                "relative_strength": 0.95,
                "trend": "bullish_intraday"
            },
            "Banking": {
                "performance_today": 0.7,
                "performance_week": 1.5,
                "relative_strength": 1.15,
                "trend": "bullish"
            },
            "Pharma": {
                "performance_today": -0.3,
                "performance_week": 2.1,
                "relative_strength": 1.05,
                "trend": "neutral"
            },
            "Auto": {
                "performance_today": 1.5,
                "performance_week": 2.3,
                "relative_strength": 1.25,
                "trend": "strongly_bullish"
            },
            "Metal": {
                "performance_today": -1.2,
                "performance_week": -3.5,
                "relative_strength": 0.75,
                "trend": "bearish"
            },
            "Energy": {
                "performance_today": 0.5,
                "performance_week": 0.8,
                "relative_strength": 1.02,
                "trend": "neutral"
            }
        }
        
        # Determine top and bottom performers
        sorted_today = sorted(
            sectors.items(), 
            key=lambda x: x[1]["performance_today"], 
            reverse=True
        )
        
        top_sectors = [{k: v["performance_today"]} for k, v in sorted_today[:3]]
        bottom_sectors = [{k: v["performance_today"]} for k, v in sorted_today[-3:]]
        
        # Determine if the index's key sectors are strong
        # (Banking is key for BankNifty, IT/Banking are key for Nifty)
        key_sectors_strong = False
        
        if index == "BANKNIFTY":
            key_sectors_strong = sectors["Banking"]["trend"] in ["bullish", "strongly_bullish"]
        else:  # NIFTY
            banking_strong = sectors["Banking"]["trend"] in ["bullish", "strongly_bullish"]
            it_strong = sectors["IT"]["trend"] in ["bullish", "strongly_bullish"]
            key_sectors_strong = banking_strong or it_strong
        
        # Create overall market breadth score (percentage of sectors trending positive)
        bullish_count = sum(1 for s in sectors.values() if s["trend"] in ["bullish", "strongly_bullish"])
        bearish_count = sum(1 for s in sectors.values() if s["trend"] in ["bearish", "strongly_bearish"])
        
        breadth_score = bullish_count / (bullish_count + bearish_count) if (bullish_count + bearish_count) > 0 else 0.5
        
        return {
            "top_sectors": top_sectors,
            "bottom_sectors": bottom_sectors,
            "key_sectors_strong": key_sectors_strong,
            "market_breadth": breadth_score,
            "breadth_interpretation": "Positive" if breadth_score > 0.6 else "Negative" if breadth_score < 0.4 else "Neutral",
            "sector_rotation": "Defensive" if sectors["Pharma"]["performance_today"] > sectors["Metal"]["performance_today"] else "Cyclical",
            "relative_to_index": "Outperforming" if breadth_score > 0.5 else "Underperforming"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return fallback on error
        return {
            "top_sectors": [],
            "bottom_sectors": [],
            "key_sectors_strong": False,
            "error": str(e)
        }