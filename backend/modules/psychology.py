# backend/modules/psychology.py
from typing import Dict, Any
import datetime

def check_psychology() -> Dict[str, Any]:
    """
    Apply psychological guardrails to trading decisions
    
    Returns:
    --------
    dict: Trading psychology assessment and recommendations
    """
    try:
        # Get current time
        now = datetime.datetime.now()
        
        # Get current day of week
        day_of_week = now.weekday()  # 0-6 (Monday-Sunday)
        
        # Time-based risk assessment
        first_hour = 9 <= now.hour < 10
        last_hour = 14 <= now.hour < 15
        midday = 11 <= now.hour < 13
        
        # Day-based risk assessment
        monday = day_of_week == 0
        friday = day_of_week == 4
        midweek = 1 <= day_of_week <= 3
        
        # Determine trading session context
        if first_hour:
            session_context = "opening_hour"
            session_risk = "moderate"
            caution_note = "High volatility during market open, confirm signals before trading"
        elif last_hour:
            session_context = "closing_hour"
            session_risk = "moderate"
            caution_note = "Position squaring may create volatility, be cautious with new entries"
        elif midday:
            session_context = "midday_lull"
            session_risk = "low"
            caution_note = "Typically lower volume and momentum, scalp trades may underperform"
        else:
            session_context = "regular_session"
            session_risk = "normal"
            caution_note = "Standard trading conditions"
        
        # Day context assessment
        if monday:
            day_context = "monday"
            day_risk = "moderate"
            day_note = "Weekly positioning often occurs, may see directional bias"
        elif friday:
            day_context = "friday"
            day_risk = "moderate"
            day_note = "Risk of weekend gap, consider reducing position sizes for swing trades"
        else:
            day_context = "midweek"
            day_risk = "normal"
            day_note = "Typical trading conditions, follow standard risk management"
        
        # Emotionality checks (these would ideally be personalized)
        emotionality_checks = [
            "Validate trade with multiple timeframes before entry",
            "Stick to predefined stop loss - no adjustments after entry",
            "Clear profit targets set before trade execution",
            "Are you trading out of FOMO or solid analysis?"
        ]
        
        # Behavioral nudges
        behavioral_nudges = [
            "Follow your trading plan, not your emotions",
            "Consistency matters more than occasional big wins",
            f"Maximum {3} trades per day to avoid overtrading",
            "Take a break after 2 consecutive losses"
        ]
        
        return {
            "session": {
                "context": session_context,
                "risk_level": session_risk,
                "guidance": caution_note
            },
            "day": {
                "context": day_context,
                "risk_level": day_risk,
                "guidance": day_note
            },
            "psychological_checks": emotionality_checks,
            "behavioral_nudges": behavioral_nudges,
            "trade_readiness": "ready" if session_risk != "high" and day_risk != "high" else "caution",
            "max_trades_today": 5 if midweek else 3,
            "risk_adjustment": 1.0 if midweek else 0.8
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return fallback on error
        return {
            "session": {"context": "unknown", "risk_level": "normal"},
            "day": {"context": "unknown", "risk_level": "normal"},
            "psychological_checks": ["Validate signals before trading"],
            "trade_readiness": "ready",
            "error": str(e)
        }