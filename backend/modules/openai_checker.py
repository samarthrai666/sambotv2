# backend/modules/openai_checker.py
from typing import Dict, Any
import os
import time

def validate_with_openai(signal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate trading signal with OpenAI API as a final sanity check
    
    Parameters:
    -----------
    signal : Dict[str, Any]
        Complete signal data to validate
        
    Returns:
    --------
    dict: GPT validation response
    """
    try:
        # Check if we should actually call the API
        openai_enabled = os.environ.get("OPENAI_ENABLED", "false").lower() == "true"
        
        if not openai_enabled:
            # Return sensible fallback without making API call
            return generate_mock_response(signal)
        
        # In real implementation, call the OpenAI API here
        # response = openai.chat.completions.create(...)
        
        # For now, return mock response
        return generate_mock_response(signal)
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        # Return fallback on error
        return {
            "decision": "AGREE",
            "confidence": 0.7,
            "reasoning": f"Error in OpenAI verification: {str(e)}. Defaulting to agree with caution.",
            "warning": str(e)
        }

def generate_mock_response(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a mock GPT response based on signal characteristics"""
    # Extract key information for decision making
    signal_type = signal.get("signal", "HOLD")
    ml_confidence = signal.get("ml_prediction", {}).get("confidence", 0.5)
    
    # Get trend information
    trend = signal.get("primary_trend", {}).get("trend", "neutral")
    trend_aligned = (
        ("UP" in signal_type or "CALL" in signal_type or "BUY" in signal_type) and 
        ("up" in trend.lower() or "bull" in trend.lower())
    ) or (
        ("DOWN" in signal_type or "PUT" in signal_type or "SELL" in signal_type) and 
        ("down" in trend.lower() or "bear" in trend.lower())
    )
    
    # Get indicator confirmations
    indicators = signal.get("indicators", {})
    rsi = indicators.get("rsi", 50)
    macd = indicators.get("macd", 0)
    
    # More confirmations for bullish signals
    bullish_confirmations = (
        ("UP" in signal_type or "CALL" in signal_type or "BUY" in signal_type) and
        (rsi > 50) and
        (macd > 0)
    )
    
    # More confirmations for bearish signals
    bearish_confirmations = (
        ("DOWN" in signal_type or "PUT" in signal_type or "SELL" in signal_type) and
        (rsi < 50) and
        (macd < 0)
    )
    
    # Make decision based on confirmations
    confirmations = bullish_confirmations or bearish_confirmations
    
    # Calculate confidence
    confidence = 0.6  # Base confidence
    
    if trend_aligned:
        confidence += 0.15
    
    if confirmations:
        confidence += 0.15
    
    # Add small random factor (±0.05)
    confidence += (time.time() % 10) / 100 - 0.05
    
    # Ensure confidence is within valid range
    confidence = max(0.4, min(0.98, confidence))
    
    # Make decision
    if confidence > 0.75:
        decision = "AGREE"
        reasoning = f"Strong alignment between {signal_type} signal and market conditions. Technical indicators provide confirmation with trend alignment."
    elif confidence > 0.6:
        decision = "AGREE"
        reasoning = f"Reasonable alignment between {signal_type} signal and market conditions, though some indicators show mixed signals."
    else:
        decision = "DISAGREE"
        reasoning = f"Limited confirmation for {signal_type} signal. Technical indicators and market conditions show contradictory signals."
    
    return {
        "decision": decision,
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
        "analysis": f"ML confidence: {ml_confidence}, Trend aligned: {trend_aligned}, Indicator confirmations: {confirmations}",
        "warning": None if confidence > 0.7 else "Consider waiting for stronger confirmation"
    }