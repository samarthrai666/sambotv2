from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel
import time
import random
from modules.pre_market import analyze_pdf_sentiment
import shutil
import json

# ==========================================
# 🔧 CONFIGURATION AND SETUP
# ==========================================

cached_data = None
last_updated = 0
refresh_interval = 30  # seconds

# Load .env configs
load_dotenv()
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
FYERS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")
FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
FYERS_BASE_URL = os.getenv("FYERS_BASE_URL", "https://api.fyers.in/api/v2")
MOCK_MODE = os.getenv("MOCK_FYERS", "false").lower() == "true"

print("===== DEBUG ENVIRONMENT SETTINGS =====")
print(f"MOCK_FYERS env var value: '{os.getenv('MOCK_FYERS')}'")
print(f"MOCK_MODE in main.py: {MOCK_MODE}")
print(f"AI_ENABLED: {AI_ENABLED}")
print("=====================================")

fyers = fyersModel.FyersModel(
    client_id=FYERS_CLIENT_ID,
    token=FYERS_TOKEN,
    is_async=False,
    log_path=""
)

# Import processors
from processors import (
    # Options trading processors
    nifty_scalp, nifty_swing, nifty_longterm,
    banknifty_scalp, banknifty_swing, banknifty_longterm,
    # Intraday trading processor
    intraday,
    # Equity swing trading processor
    equity_swing
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 📦 DATA MODELS
# ==========================================

class TradeModeRequest(BaseModel):
    # Options trading
    nifty: List[str] = []
    banknifty: List[str] = []
    # Intraday trading
    intraday: bool = False
    # Equity swing trading
    equity_swing: bool = False
    # General settings
    auto_execute: bool
    log_enabled: bool = True

class SignalRequest(BaseModel):
    signal_id: str
    quantity: int
    price: float
    user_id: Optional[str] = None

# ==========================================
# 🧠 PROCESSOR MAPPING
# ==========================================

# Each strategy maps to a specific processor function
strategy_map = {
    # Options trading processors
    "nifty_scalp": nifty_scalp.process,
    "nifty_swing": nifty_swing.process,
    "nifty_longterm": nifty_longterm.process,
    "banknifty_scalp": banknifty_scalp.process,
    "banknifty_swing": banknifty_swing.process,
    "banknifty_longterm": banknifty_longterm.process,
    # Intraday trading processor
    "intraday": intraday.process,
    # Equity swing trading processor
    "equity_swing": equity_swing.process
}

# ==========================================
# 🔄 SIGNAL PROCESSING ENDPOINTS
# ==========================================

@app.get("/signals/options")
async def get_options_signals(nifty: str = "", banknifty: str = ""):
    """Get available options trading signals for NIFTY and BANKNIFTY"""
    try:
        print("\n===== PROCESSING OPTIONS SIGNALS =====")
        print(f"Options signal request with: nifty={nifty}, banknifty={banknifty}")
        
        # Parse the selections
        nifty_modes = nifty.split(",") if nifty else []
        banknifty_modes = banknifty.split(",") if banknifty else []
        
        print(f"Parsed modes: nifty_modes={nifty_modes}, banknifty_modes={banknifty_modes}")
        
        all_signals = []
        
        # Process NIFTY options signals
        for mode in nifty_modes:
            if mode in ['scalp', 'swing', 'longterm']:
                print(f"Processing NIFTY {mode} signals...")
                processor_key = f"nifty_{mode}"
                if processor_key in strategy_map:
                    result = await strategy_map[processor_key](auto_execute=False)
                    if result and "non_executed" in result and result["non_executed"]:
                        for signal in result["non_executed"]:
                            formatted_signal = format_signal_for_frontend(signal, "NIFTY", mode)
                            all_signals.append(formatted_signal)
        
        # Process BANKNIFTY options signals
        for mode in banknifty_modes:
            if mode in ['scalp', 'swing', 'longterm']:
                print(f"Processing BANKNIFTY {mode} signals...")
                processor_key = f"banknifty_{mode}"
                if processor_key in strategy_map:
                    result = await strategy_map[processor_key](auto_execute=False)
                    if result and "non_executed" in result and result["non_executed"]:
                        for signal in result["non_executed"]:
                            formatted_signal = format_signal_for_frontend(signal, "BANKNIFTY", mode)
                            all_signals.append(formatted_signal)
        
        print(f"Found {len(all_signals)} options signals")
        return all_signals
    except Exception as e:
        print(f"[ERROR] Failed to get options signals: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/signals/intraday")
async def get_intraday_signals():
    """Get available intraday trading signals"""
    try:
        print("\n===== PROCESSING INTRADAY SIGNALS =====")
        all_signals = []
        
        print("Fetching intraday signals...")
        result = await strategy_map["intraday"](auto_execute=False)
        if result and "non_executed" in result and result["non_executed"]:
            for signal in result["non_executed"]:
                # Determine which index the signal is for
                index_type = "NIFTY" if "NIFTY-" in signal.get("symbol", "") else "BANKNIFTY"
                formatted_signal = format_signal_for_frontend(signal, index_type, "intraday")
                all_signals.append(formatted_signal)
        
        print(f"Found {len(all_signals)} intraday signals")
        return all_signals
    except Exception as e:
        print(f"[ERROR] Failed to get intraday signals: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/signals/equity")
async def get_equity_signals():
    """Get available equity swing trading signals"""
    try:
        print("\n===== PROCESSING EQUITY SIGNALS =====")
        all_signals = []
        
        print("Fetching equity swing signals...")
        result = await strategy_map["equity_swing"](auto_execute=False)
        if result and "non_executed" in result and result["non_executed"]:
            for signal in result["non_executed"]:
                # Extract stock symbol from the signal
                symbol_parts = signal.get("symbol", "").split("-")
                stock_symbol = symbol_parts[1] if len(symbol_parts) > 1 else "EQUITY"
                formatted_signal = format_equity_signal_for_frontend(signal, stock_symbol, "swing")
                all_signals.append(formatted_signal)
        
        print(f"Found {len(all_signals)} equity signals")
        return all_signals
    except Exception as e:
        print(f"[ERROR] Failed to get equity signals: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/signals/available")
async def get_available_signals(
    nifty: str = "", 
    banknifty: str = "",
    intraday: bool = False,
    equity_swing: bool = False
):
    """Get all available trading signals based on user preferences"""
    try:
        print("\n===== PROCESSING ALL SIGNALS =====")
        print(f"Signal request with: nifty={nifty}, banknifty={banknifty}, intraday={intraday}, equity_swing={equity_swing}")
        
        all_signals = []
        
        # Get options signals if requested
        if nifty or banknifty:
            options_signals = await get_options_signals(nifty, banknifty)
            all_signals.extend(options_signals)
        
        # Get intraday signals if requested
        if intraday:
            intraday_signals = await get_intraday_signals()
            all_signals.extend(intraday_signals)
        
        # Get equity signals if requested
        if equity_swing:
            equity_signals = await get_equity_signals()
            all_signals.extend(equity_signals)
        
        print(f"Found {len(all_signals)} total signals")
        return all_signals
    except Exception as e:
        print(f"[ERROR] Failed to get available signals: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@app.post("/signal/execute/{signal_id}")
async def execute_signal(signal_id: str, request: SignalRequest):
    """Execute a trading signal"""
    try:
        print(f"\n===== EXECUTING SIGNAL {signal_id} =====")
        # In a real implementation, this would connect to the broker API to place the order
        
        # For now, return a mock successful execution
        return {
            "status": "success",
            "message": f"Signal {signal_id} executed successfully",
            "order_id": f"ORD-{int(time.time())}-{random.randint(1000, 9999)}",
            "execution_time": datetime.now().isoformat(),
            "execution_price": request.price,
            "quantity": request.quantity
        }
    except Exception as e:
        print(f"[ERROR] Failed to execute signal {signal_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing signal: {str(e)}")

@app.post("/signals/refresh-analysis")
async def refresh_signal_analysis(signals: List[dict]):
    """Refresh the analysis for a list of signals with current market data"""
    try:
        updated_signals = []
        
        for signal in signals:
            # Get fresh market data for the symbol
            symbol_data = await get_symbol_data(signal["symbol"])
            
            # Recalculate technical indicators
            indicators = calculate_indicators(symbol_data)
            
            # Re-detect patterns
            patterns = detect_patterns(symbol_data)
            
            # Recalculate confidence score based on current conditions
            confidence_score = calculate_confidence_score(signal, symbol_data, indicators, patterns)
            
            # Check if the signal is still valid
            still_valid = is_signal_still_valid(signal, symbol_data)
            
            # Update the signal with fresh analysis
            updated_signal = {
                **signal,
                "current_price": symbol_data["lp"],
                "indicators": indicators,
                "patterns": patterns,
                "confidence_score": confidence_score,
                "is_valid": still_valid,
                "time_to_expiry": calculate_time_to_expiry(signal),
                "last_updated": datetime.now().isoformat()
            }
            
            # Add a field to show if anything has changed
            if updated_signal["confidence_score"] > signal.get("confidence_score", 0) + 5:
                updated_signal["confidence_change"] = "increased"
            elif updated_signal["confidence_score"] < signal.get("confidence_score", 0) - 5:
                updated_signal["confidence_change"] = "decreased"
            else:
                updated_signal["confidence_change"] = "stable"
                
            updated_signals.append(updated_signal)
        
        return updated_signals
        
    except Exception as e:
        print(f"Error refreshing signal analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 📈 MARKET DATA ENDPOINTS
# ==========================================

@app.get("/market/data")
def get_market_data():
    """Get current market data for indices"""
    try:
        response = fyers.quotes(data={
            "symbols": "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX"
        })

        if response.get("s") != "ok" or not response.get("d"):
            raise ValueError(f"Fyers error: {response.get('message', 'Unknown error')}")

        quotes = response["d"]
        nifty = next((item for item in quotes if "NIFTY50" in item.get("n", "")), None)
        banknifty = next((item for item in quotes if "NIFTYBANK" in item.get("n", "")), None)

        if not nifty or not banknifty:
            raise ValueError("Missing quote data for NIFTY or BANKNIFTY")

        return {
            "nifty": {
                "price": nifty["v"].get("lp", 0),
                "change": nifty["v"].get("ch", 0),
                "changePercent": nifty["v"].get("chp", 0)
            },
            "banknifty": {
                "price": banknifty["v"].get("lp", 0),
                "change": banknifty["v"].get("ch", 0),
                "changePercent": banknifty["v"].get("chp", 0)
            },
            "marketStatus": "open",
            "marketOpenTime": "09:15:00",
            "marketCloseTime": "15:30:00",
            "serverTime": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market data: {str(e)}")

# ==========================================
# 📝 PRE-MARKET ANALYSIS ENDPOINTS
# ==========================================

@app.post("/upload-pdf")
async def upload_pre_market_pdf(file: UploadFile = File(...)):
    """Upload and analyze pre-market PDF report"""
    try:
        # Define upload directories and files
        UPLOAD_DIR = "data"
        PDF_NAME = "pre_market.pdf"
        PDF_PATH = os.path.join(UPLOAD_DIR, PDF_NAME)
        RESULT_PATH = os.path.join(UPLOAD_DIR, "pre_market_result.json")
        
        # Check file type
        if not file.filename.endswith(".pdf"):
            print("❌ Not a PDF file")
            return {"error": "Only PDF files are allowed."}

        # Create directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save the uploaded file
        with open(PDF_PATH, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print(f"✅ PDF saved to {PDF_PATH}")

        # Analyze the PDF
        analysis = analyze_pdf_sentiment()
        print("🧠 GPT Analysis complete")

        # Save the analysis to JSON
        with open(RESULT_PATH, "w") as f:
            json.dump(analysis, f, indent=2)
        print(f"💾 Analysis saved to {RESULT_PATH}")

        # Clean up by removing the uploaded PDF
        os.remove(PDF_PATH)
        print("🧹 PDF deleted after analysis")

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Upload or GPT processing failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Exception occurred: {str(e)}"
        }

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def format_signal_for_frontend(signal, symbol, strategy):
    """Format a signal from the backend format to the frontend expected format"""
    # Get current timestamp if not available
    timestamp = signal.get("trade_time", datetime.now().isoformat())
    
    # Generate a unique ID
    signal_id = f"{symbol.lower()}-{strategy}-{int(time.time())}-{random.randint(1000, 9999)}"
    
    # Map signal type to action
    action = "BUY" if any(s in signal.get("signal", "HOLD") for s in ["BUY", "CALL", "UP"]) else "SELL"
    
    # Determine option type based on signal
    option_type = "CE" if "CALL" in signal.get("signal", "") else "PE"
    
    # Format expiry date (would be dynamic in real implementation)
    expiry_date = "Apr 24th"  # Example static date
    
    # Map confidence to a percentage
    confidence = int(signal.get("confidence", 0.7) * 100)
    
    # Extract indicators from the signal
    indicators = []
    if "indicator_snapshot" in signal:
        for key, value in signal["indicator_snapshot"].items():
            if isinstance(value, bool) and value:
                indicators.append(key.upper())
            elif isinstance(value, str) and "bullish" in value:
                indicators.append(f"{key.upper()} (Bullish)")
            elif isinstance(value, str) and "bearish" in value:
                indicators.append(f"{key.upper()} (Bearish)")
    
    # Extract patterns
    patterns = []
    if "pattern_analysis" in signal and "patterns_detected" in signal["pattern_analysis"]:
        patterns = signal["pattern_analysis"]["patterns_detected"]
    
    # Create frontend-compatible signal
    return {
        "id": signal_id,
        "symbol": symbol,
        "instrumentType": "Option",
        "strike": signal.get("strike", 0),
        "optionType": option_type,
        "action": action,
        "price": signal.get("entry", 0),
        "target_price": signal.get("target", 0),
        "stop_loss": signal.get("stop_loss", 0),
        "quantity": 50 if symbol == "NIFTY" else 25,  # Default quantities
        "potential_return": abs((signal.get("target", 0) - signal.get("entry", 0)) / signal.get("entry", 1)),
        "risk_reward_ratio": signal.get("rrr", 1.5),
        "timeframe": "1hour" if strategy == "swing" else "5min",
        "confidence_score": confidence,
        "indicators": indicators[:4],  # Limit to top 4 indicators
        "patterns": patterns[:2],     # Limit to top 2 patterns
        "strategy": strategy,
        "aiAnalysis": signal.get("ai_opinion", {}).get("reasoning", ""),
        "notes": f"{symbol} {strategy} signal with {signal.get('trend', 'neutral')} trend",
        "timestamp": timestamp,
        "executed": False,
        "expiryDate": expiry_date
    }

def format_equity_signal_for_frontend(signal, symbol, strategy):
    """Format an equity signal from the backend format to the frontend expected format"""
    # Get current timestamp if not available
    timestamp = signal.get("trade_time", datetime.now().isoformat())
    
    # Generate a unique ID
    signal_id = f"equity-{symbol.lower()}-{strategy}-{int(time.time())}-{random.randint(1000, 9999)}"
    
    # Map signal type to action
    action = signal.get("signal", "HOLD")
    
    # Format expiry date (for equity swing, use expected exit date)
    expiry_date = signal.get("expected_exit_date", "N/A")
    
    # Map confidence to a percentage
    confidence = int(signal.get("confidence", 0.7) * 100)
    
    # Extract indicators from the signal
    indicators = []
    if "indicator_snapshot" in signal:
        for key, value in signal["indicator_snapshot"].items():
            if isinstance(value, bool) and value:
                indicators.append(key.upper())
            elif isinstance(value, str):
                indicators.append(f"{key.upper()} ({value})")
    
    # Extract patterns
    patterns = []
    if "pattern_analysis" in signal and "patterns_detected" in signal["pattern_analysis"]:
        patterns = signal["pattern_analysis"]["patterns_detected"]
    
    # Create frontend-compatible signal
    return {
        "id": signal_id,
        "symbol": symbol,
        "instrumentType": "Equity",
        "action": action,
        "price": signal.get("entry", 0),
        "target_price": signal.get("target", 0),
        "stop_loss": signal.get("stop_loss", 0),
        "quantity": 10,  # Default quantity for equity
        "potential_return": abs((signal.get("target", 0) - signal.get("entry", 0)) / signal.get("entry", 1)),
        "risk_reward_ratio": signal.get("rrr", 1.5),
        "timeframe": signal.get("timeframe", "daily"),
        "confidence_score": confidence,
        "indicators": indicators[:4],  # Limit to top 4 indicators
        "patterns": patterns[:2],     # Limit to top 2 patterns
        "strategy": strategy,
        "aiAnalysis": signal.get("ai_opinion", {}).get("reasoning", ""),
        "notes": f"{symbol} {strategy} signal with {signal.get('trend', 'neutral')} trend",
        "timestamp": timestamp,
        "executed": False,
        "expiryDate": expiry_date,
        "holdingPeriod": signal.get("expected_holding_period", "N/A")
    }

# Placeholder implementations for the missing functions
async def get_symbol_data(symbol):
    """Get latest market data for a symbol"""
    try:
        # In a real implementation, you would fetch from Fyers API
        if isinstance(symbol, str) and "EQ-" in symbol:
            # It's an equity symbol
            symbol_parts = symbol.split("-")
            stock_name = symbol_parts[1] if len(symbol_parts) > 1 else "UNKNOWN"
            return {
                "lp": random.randint(500, 5000),  # Random stock price
                "ch": random.randint(-50, 50),
                "chp": round(random.uniform(-2.0, 2.0), 2)
            }
        else:
            # It's an index
            return {
                "lp": 22500 if "NIFTY" in str(symbol) else 48750,
                "ch": 50,
                "chp": 0.2
            }
    except Exception as e:
        print(f"Error getting symbol data: {str(e)}")
        return {"lp": 0, "ch": 0, "chp": 0}

def calculate_indicators(data):
    """Calculate technical indicators from market data"""
    # Placeholder implementation
    return ["RSI", "MACD", "EMA Cross", "VWAP"]

def detect_patterns(data):
    """Detect chart patterns from market data"""
    # Placeholder implementation
    return ["Support Bounce", "Bullish Engulfing"]

def calculate_confidence_score(signal, data, indicators, patterns):
    """Calculate confidence score based on current market conditions"""
    # Placeholder implementation - keep existing score or slightly adjust
    base_score = signal.get("confidence_score", 75)
    return base_score + random.randint(-5, 5)

def is_signal_still_valid(signal, data):
    """Check if a signal is still valid based on current price"""
    # Placeholder implementation - most signals remain valid
    return True

def calculate_time_to_expiry(signal):
    """Calculate time to expiry for an option signal"""
    # Placeholder implementation
    return "3 days"