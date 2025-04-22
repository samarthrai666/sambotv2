import json
from modules.pre_market import analyze_pdf_sentiment as run_pre_market_analysis
from modules.market_open import run_market_open_analysis
from modules.trend_analysis import get_trend_summary as detect_trend 
from modules.support_resistance import get_support_resistance
from modules.fib_analysis import get_fib_levels
from modules.indicator_engine import calculate_indicators
from modules.pattern_detector import detect_patterns
from modules.momentum import analyze_momentum
from modules.option_chain import analyze_option_chain
from modules.fii_dii import fetch_fii_dii_sentiment
from modules.sector_analysis import analyze_sectors
from modules.risk_management import evaluate_risk
from modules.psychology import check_psychology
from ml.predict_ml_signal import predict_signal_ml
from modules.openai_checker import validate_with_openai


def build_final_signal(data: dict, index: str, mode: str) -> dict:
    signal = {}

    # 1. Pre-market context
    try: signal["pre_market"] = json.load(open("data/pre_market_result.json"))
    except: signal["pre_market"] = {"error": "Pre-market data missing"}

    # 2. Opening range analysis
    signal["market_open"] = run_market_open_analysis(data)

    # 3. Trend detection
    signal["primary_trend"] = detect_trend(data)

    # 4. Support/resistance zones
    signal["zones"] = get_support_resistance(data)

    # 5. Fibonacci
    signal["fib"] = get_fib_levels(data)

    # 6. Indicators
    signal["indicators"] = calculate_indicators(data)

    # 7. Chart patterns
    signal["patterns"] = detect_patterns(data)

    # 8. Momentum check
    signal["momentum"] = analyze_momentum(data)

    # 9. Option chain + OI
    signal["option_chain"] = analyze_option_chain(index, mode)

    # 10. FII/DII sentiment
    signal["fii_dii"] = fetch_fii_dii_sentiment()

    # 11. Sector rotation
    signal["sectors"] = analyze_sectors(index)

    # 12. Risk profile
    signal["risk"] = evaluate_risk(data, index, mode)

    # 13. Psychology guardrails
    signal["psychology"] = check_psychology()

    # 14. ML model prediction
    ml_signal = predict_signal_ml(data)
    signal["ml_prediction"] = ml_signal

    # 15. AI review via GPT/OpenAI
    gpt_opinion = validate_with_openai(signal)
    signal["ai_opinion"] = gpt_opinion

    # 16. Final metadata
    signal["final_decision"] = (
        ml_signal["ml_signal"] if gpt_opinion["decision"] == "AGREE" and gpt_opinion["confidence"] >= 0.75 else "SKIP"
    )
    signal["confidence_score"] = (
        round((ml_signal["confidence"] * 0.6) + (gpt_opinion["confidence"] * 0.4), 3)
    )

    return signal
