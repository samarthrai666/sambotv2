import os
import fitz  # PyMuPDF
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PDF_PATH = "data/pre_market.pdf"

def extract_text_from_pdf(filepath=PDF_PATH):
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            return None, f"Error: File not found at path: {filepath}"
            
        # Check if directory exists
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            return None, f"Error: Directory {directory} does not exist"
            
        # Try to open the file
        with fitz.open(filepath) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            
            if not text.strip():
                return None, "Warning: Extracted text is empty. PDF might be empty or contain only images."
                
            return text.strip(), None
    except fitz.FileDataError:
        return None, "Error: Invalid or corrupted PDF file"
    except Exception as e:
        return None, f"Error extracting text from PDF: {str(e)}"

def analyze_pdf_sentiment():
    # Verify if PDF exists and extract text
    text, error = extract_text_from_pdf()
    
    if error:
        return {"error": error}
    
    if not text:
        return {"error": "Failed to extract text from PDF"}

    prompt = f"""
        You are an elite Indian stock market AI built for precision intraday and options trading in NIFTY and BANKNIFTY.

        You will receive a **pre-market report** below.

        Analyze it thoroughly and extract only **key actionable insights** relevant for today's market setup. Include sentiment, macro, technical cues, and risk warnings — everything needed to prepare for trading decisions.

        Respond ONLY with a clean and valid JSON in the following format (NO explanation text):

        {{
        "market_sentiment": "",                # Overall tone - bullish, bearish, cautious, neutral
        "global_summary": "",                  # Summary of global markets (US, Asia, Europe)
        "local_cues": "",                      # Indian-specific news and cues (RBI, earnings, politics, etc.)
        "nifty_outlook": "",                   # Technical + sentiment view on NIFTY
        "banknifty_outlook": "",              # Technical + sentiment view on BANKNIFTY
        "bullish_sectors": ["", "", ""],       # Max 3 sectors showing strength
        "bearish_sectors": ["", "", ""],       # Max 3 sectors showing weakness
        "fii_dii_activity": "",                # FII/DII cash activity summary
        "currency_view": "",                   # INR movement and impact
        "commodities_outlook": "",            # Key levels or tone on gold/oil
        "interest_rate_bias": "",             # RBI stance or bond yield trend
        "stocks_to_watch": ["", "", ""],       # 3 stocks from news, results, volume spike, etc.
        "risk_factors": "",                   # Any global or domestic risks to consider
        "option_chain_bias": "",             // Call-heavy / Put-heavy / Mixed / Neutral sentiment from OI data
        "pcr": 0.00,                         // Put-Call Ratio (total or index-wise)
        "vix_view": "",                      // India VIX reading and its implication
        "support_resistance_zones": {{     // Clean levels for quick decision making
            "nifty": {{
                "support": 0,
                "resistance": 0
            }},
            "banknifty": {{
                "support": 0,
                "resistance": 0
            }}
        }},
        "gap_up_down_view": "",             // Will it open gap up / down / flat? and how to trade it
        "top_fno_buildup": {{             // For future trades
            "long": ["", "", ""],
            "short": ["", "", ""]
        }},
        "stocks_in_ban": ["", "", ""],      // For avoiding trap trades
        "final_verdict": ""                   # Summary call: Trade Aggressive / Cautious / Avoid / Wait for Dip / Buy on Rally
        }}

        Pre-market report:
        {text}
        """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt.strip()}],
            temperature=0.4,
        )

        response_json = response.choices[0].message.content
        return json.loads(response_json)

    except Exception as e:
        return {
            "error": str(e),
            "hint": "Check OpenAI key, PDF format, or GPT model issues"
        }

def verify_environment():
    """Check if all the necessary components are in place"""
    results = {}
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        results["api_key"] = "Missing OpenAI API key in environment variables"
    else:
        results["api_key"] = "API key is set"
    
    # Check if data directory exists
    data_dir = os.path.dirname(PDF_PATH)
    if not os.path.exists(data_dir):
        results["data_directory"] = f"Directory {data_dir} does not exist. Creating it now."
        try:
            os.makedirs(data_dir, exist_ok=True)
            results["data_directory"] += " Directory created successfully."
        except Exception as e:
            results["data_directory"] += f" Failed to create directory: {str(e)}"
    else:
        results["data_directory"] = f"Directory {data_dir} exists"
    
    # Check if PDF file exists
    if os.path.exists(PDF_PATH):
        file_size = os.path.getsize(PDF_PATH)
        results["pdf_file"] = f"File exists at {PDF_PATH} (Size: {file_size} bytes)"
    else:
        results["pdf_file"] = f"File does not exist at {PDF_PATH}"
    
    return results

if __name__ == "__main__":
    # First, verify the environment
    env_check = verify_environment()
    
    if "File does not exist" in env_check.get("pdf_file", ""):
        pass
    else:
        print("Analyzing PDF...")
        result = analyze_pdf_sentiment()