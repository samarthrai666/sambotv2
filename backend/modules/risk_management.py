# backend/modules/risk_management.py
from typing import Dict, Union, Any
import pandas as pd

def evaluate_risk(data: Union[pd.DataFrame, Dict[str, Any]], index: str, mode: str) -> Dict[str, Any]:
    """
    Evaluate trading risk for the given market conditions
    
    Parameters:
    -----------
    data : pd.DataFrame or dict
        Market data for risk assessment
    index : str
        Index being traded (NIFTY or BANKNIFTY)
    mode : str
        Trading mode (scalp, swing, longterm)
        
    Returns:
    --------
    dict: Risk assessment and position sizing recommendations
    """
    try:
        # Get current price
        if isinstance(data, dict) and 'candles' in data and data['candles']:
            # Extract close price from last candle
            current_price = data['candles'][-1][4]  # Assuming [timestamp, open, high, low, close, volume]
        elif isinstance(data, pd.DataFrame) and not data.empty:
            current_price = data['close'].iloc[-1]
        else:
            current_price = 22000 if index == "NIFTY" else 48000
        
        # Default ATR values based on index and mode
        default_atr = {
            "NIFTY": {"scalp": 30, "swing": 120, "longterm": 300},
            "BANKNIFTY": {"scalp": 80, "swing": 300, "longterm": 700}
        }
        
        # Base risk parameters
        atr_value = default_atr.get(index, default_atr["NIFTY"]).get(mode, default_atr["NIFTY"]["swing"])
        
        # Risk per trade (as percentage of capital)
        risk_per_trade = {
            "scalp": 1.0,    # 1% risk for scalp
            "swing": 1.5,    # 1.5% risk for swing
            "longterm": 2.0  # 2% risk for long-term
        }.get(mode, 1.0)
        
        # Position sizing based on ATR
        # Assuming a 100,000 capital for calculation
        capital = 100000
        risk_amount = capital * (risk_per_trade / 100)
        
        # Lot sizes
        lot_size = 50 if index == "NIFTY" else 25
        
        # Stop loss calculation
        stop_loss_multiplier = {
            "scalp": 1.5,
            "swing": 2.0,
            "longterm": 3.0
        }.get(mode, 1.5)
        
        stop_loss_points = atr_value * stop_loss_multiplier
        
        # Position size calculation
        max_quantity = int(risk_amount / stop_loss_points)
        suggested_lots = max(1, max_quantity // lot_size)
        
        # Volatility risk assessment
        volatility_rank = "moderate"
        if atr_value > default_atr[index][mode] * 1.5:
            volatility_rank = "high"
        elif atr_value < default_atr[index][mode] * 0.7:
            volatility_rank = "low"
        
        # Market phase risk
        market_phase_risk = {
            "scalp": "moderate",
            "swing": "moderate" if volatility_rank != "high" else "high",
            "longterm": "moderate"
        }.get(mode, "moderate")
        
        # VIX assessment (simulated)
        vix_value = 15.5
        vix_risk = "normal"
        if vix_value > 22:
            vix_risk = "elevated"
        elif vix_value > 28:
            vix_risk = "high"
        
        return {
            "overall_risk": market_phase_risk,
            "position_sizing": {
                "capital": capital,
                "risk_per_trade_pct": risk_per_trade,
                "risk_amount": risk_amount,
                "stop_loss_points": stop_loss_points,
                "max_quantity": max_quantity,
                "suggested_lots": suggested_lots,
                "lot_size": lot_size
            },
            "volatility": {
                "atr": atr_value,
                "rank": volatility_rank,
                "vix": vix_value,
                "vix_status": vix_risk
            },
            "overnight_risk": "high" if mode == "scalp" else "moderate",
            "gap_risk": "low" if mode == "scalp" else "moderate",
            "max_drawdown_expected": f"{risk_per_trade * 3:.1f}%",
            "market_phase": "trending" if vix_value < 18 else "volatile",
            "liquidity_risk": "low" if index in ["NIFTY", "BANKNIFTY"] else "moderate"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return fallback on error
        return {
            "overall_risk": "moderate",
            "position_sizing": {
                "suggested_lots": 1
            },
            "volatility": {
                "rank": "moderate"
            },
            "error": str(e)
        }