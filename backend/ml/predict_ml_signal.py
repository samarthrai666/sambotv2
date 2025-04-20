import joblib
import pandas as pd
import ta

# Load trained model
model = joblib.load("ml/sambot_model.joblib")

def predict_signal_ml(data: dict):
    """
    Predicts a trade signal using the trained AI model.
    Expects OHLCV candle data in 'candles' list format.
    """
    candles = data.get("candles", [])
    if not candles or len(candles) < 5:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])

    # Add indicators
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
        high=df['high'], low=df['low'], close=df['close'], volume=df['volume']
    ).vwap

    # Dummy candlestick pattern flags — replace later with real detection
    df["bullish_engulfing"] = 0
    df["bearish_engulfing"] = 0
    df["doji"] = 0
    df["hammer"] = 0
    df["shooting_star"] = 0

    df = df.fillna(0)

    # Use the last candle as input for prediction
    row = df.iloc[-1]

    features = [
        "open", "high", "low", "close",
        "bullish_engulfing", "bearish_engulfing",
        "doji", "hammer", "shooting_star",
        "rsi", "macd", "macd_signal", "vwap", "volume"
    ]

    X_live = row[features].values.reshape(1, -1)

    prediction = model.predict(X_live)[0]
    confidence = max(model.predict_proba(X_live)[0])

    return {
        "ml_signal": "BUY CALL" if prediction == 1 else "SELL CALL" if prediction == -1 else "HOLD",
        "confidence": round(confidence, 3)
    }
