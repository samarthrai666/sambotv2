import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump
import ta
import os

# Load labeled candle data
df = pd.read_csv('data/nifty_labeled.csv')

# === Feature Engineering ===
df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
macd = ta.trend.MACD(df['close'])
df['macd'] = macd.macd()
df['macd_signal'] = macd.macd_signal()
df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
    high=df['high'], low=df['low'], close=df['close'], volume=df['volume']
).vwap

df = df.fillna(0)  # handle NaNs after indicators

# === Features & Label ===
features = [
    "open", "high", "low", "close",
    "bullish_engulfing", "bearish_engulfing",
    "doji", "hammer", "shooting_star",
    "rsi", "macd", "macd_signal", "vwap", "volume"
]
X = df[features]
y = df["label"]  # target: 1=BUY, 0=HOLD, -1=SELL

# === Train-Test Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# === Train Model ===
model = RandomForestClassifier()
model.fit(X_train, y_train)

# === Evaluate ===
print("\n📊 Model Performance:\n")
print(classification_report(y_test, model.predict(X_test)))

# === Save model ===
os.makedirs("ml", exist_ok=True)
dump(model, 'ml/sambot_model.joblib')
print("✅ Model trained and saved to ml/sambot_model.joblib")
