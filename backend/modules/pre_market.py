import os
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PDF_PATH = "data/pre_market.pdf"

def extract_text_from_pdf(filepath=PDF_PATH):
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text

def analyze_pdf_sentiment():
    if not os.path.exists(PDF_PATH):
        return {"error": "PDF not found. Upload it first."}

    text = extract_text_from_pdf()

    prompt = f"""
You're a professional Indian stock market analyst.

Analyze the following pre-market report and provide:

1. **Overall Market Sentiment** (bullish / bearish / neutral)
2. **One-line Summary** of global and local cues
3. **Nifty Outlook**: key support/resistance levels, momentum
4. **Bank Nifty Outlook**: structure, trend, risk zones
5. **Top 3 Bullish Sectors**
6. **Top 3 Bearish Sectors**
7. **FII/DII Activity Summary**
8. **Key Risks to watch for today**
9. Final sentiment verdict (Short-Term Bias): Bullish / Neutral / Bearish

Here is the full pre-market report:

{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return {"gpt_response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = analyze_pdf_sentiment()
    print(result)
