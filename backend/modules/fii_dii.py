import os
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# 🔐 Load environment variables
load_dotenv()

client_id = os.getenv("FYERS_CLIENT_ID")
access_token = os.getenv("FYERS_ACCESS_TOKEN")

if not client_id or not access_token:
    raise Exception("⚠️ FYERS_CLIENT_ID or FYERS_ACCESS_TOKEN not found in .env")

# 🔗 Connect to Fyers API
fyers = fyersModel.FyersModel(
    client_id=client_id,
    token=access_token,
    log_path=""
)

# 🧪 Test your API by fetching profile info
response = fyers.get_profile()

print("✅ Fyers API Test Result:")
print(response)
