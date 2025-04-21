from fastapi import FastAPI, UploadFile, File
import shutil
import os
import json
from modules.pre_market import analyze_pdf_sentiment
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

UPLOAD_DIR = "data"
PDF_NAME = "pre_market.pdf"
PDF_PATH = os.path.join(UPLOAD_DIR, PDF_NAME)
RESULT_PATH = os.path.join(UPLOAD_DIR, "pre_market_result.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-pdf")
async def upload_pre_market_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            print("❌ Not a PDF file")
            return {"error": "Only PDF files are allowed."}

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(PDF_PATH, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print("✅ PDF uploaded successfully")

        analysis = analyze_pdf_sentiment()
        print("🧠 GPT Analysis complete")

        with open(RESULT_PATH, "w") as f:
            json.dump(analysis, f, indent=2)
        print("💾 Analysis saved to JSON")

        os.remove(PDF_PATH)
        print("🧹 PDF deleted after analysis")

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:
        print("❌ Upload or GPT processing failed:", str(e))
        return {
            "status": "error",
            "message": f"Exception occurred: {str(e)}"
        }
