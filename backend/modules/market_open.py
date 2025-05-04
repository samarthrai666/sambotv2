from typing import Union, Dict, Any
import pandas as pd
from datetime import datetime, date


def run_market_open_analysis(data: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
    try:
        if isinstance(data, dict) and 'candles' in data:
            candles = data['candles']
            if not candles or len(candles) < 3:
                return {"error": "Insufficient candle data for analysis"}

            sorted_candles = sorted(candles, key=lambda x: x[0], reverse=True)

            day_boundaries = []
            for i in range(1, len(sorted_candles)):
                time_diff = sorted_candles[i - 1][0] - sorted_candles[i][0]
                if time_diff > 7200:
                    day_boundaries.append(i)
                    if len(day_boundaries) == 1:
                        break

            if day_boundaries:
                most_recent_day_candles = sorted_candles[:day_boundaries[0]]
            else:
                most_recent_day_candles = sorted_candles

            most_recent_day_candles = sorted(most_recent_day_candles, key=lambda x: x[0])

            if len(most_recent_day_candles) >= 3:
                opening_range_candles = most_recent_day_candles[:3]
            else:
                return {"error": "Not enough candles for the most recent day"}

            high = max(c[2] for c in opening_range_candles)
            low = min(c[3] for c in opening_range_candles)
            open_price = opening_range_candles[0][1]
            close_price = opening_range_candles[2][4]

            volatility = ((high - low) / low * 100) if low > 0 else 0

            if close_price > high * 0.9975:
                direction = "strongly_bullish"
            elif close_price > open_price:
                direction = "bullish"
            elif close_price < low * 1.0025:
                direction = "strongly_bearish"
            elif close_price < open_price:
                direction = "bearish"
            else:
                direction = "neutral"

            vwap = (opening_range_candles[2][2] + opening_range_candles[2][3] + opening_range_candles[2][4]) / 3
            vwap_relation = "above" if close_price > vwap else "below"
            vwap_distance = abs(close_price - vwap) / vwap * 100 if vwap > 0 else 0

            opening_volume = sum(c[5] for c in opening_range_candles)
            avg_volume = sum(c[5] for c in most_recent_day_candles) / len(most_recent_day_candles) * 3
            high_volume_opening = opening_volume > avg_volume

            today = date.today()

            result = {
                "market_open_date": today.isoformat(),
                "market_open_time": "09:15:00",
                "analysis_period": "09:15 - 09:30",
                "candles_used": 3,
                "opening_high": float(high),
                "opening_low": float(low),
                "opening_range_width": float(high - low),
                "volatility_pct": float(volatility),
                "opening_direction": direction,
                "open_close_change_pct": float((close_price - open_price) / open_price * 100) if open_price > 0 else 0,
                "high_volume_opening": bool(high_volume_opening),
                "vwap_relation": vwap_relation,
                "vwap_distance_pct": float(vwap_distance),
                "opening_range_time": "first_15_minutes"
            }

            return result
        else:
            return {"error": "Invalid data format, expected dict with 'candles' key"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Failed to analyze candles: {str(e)}"}
