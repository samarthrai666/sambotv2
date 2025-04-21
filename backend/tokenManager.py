import hashlib
import requests
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Your FYERS credentials
APP_ID = os.getenv("FYERS_CLIENT_ID")  # e.g. E2BTVTH9ZR-100
APP_SECRET = os.getenv("FYERS_SECRET_ID")  # e.g. 5ST7ARI9ZH
REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI")  # e.g. https://yourdomain.com/callback
ENV_FILE = ".env"

# 1️⃣ Step: Generate login URL
def generate_login_url():
    state = "sambot-login"
    url = (
        f"https://api-t1.fyers.in/api/v3/generate-authcode?"
        f"client_id={APP_ID}&redirect_uri={REDIRECT_URI}&response_type=code&state={state}"
    )
    print("🔗 Open this URL in your browser & login to FYERS:")
    print(url)
    print("\n➡️ After login, you'll be redirected to your redirect_uri.")
    print("🔁 Copy the 'auth_code' from the URL and paste below.\n")

# 2️⃣ Step: Ask user for auth code
def get_auth_code_from_user():
    return input("Paste the auth_code here: ").strip()

# 3️⃣ Step: Generate SHA256 hash of appId:secret
def get_app_id_hash():
    raw = f"{APP_ID}:{APP_SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()

# 4️⃣ Step: Exchange auth_code for token
def get_access_token(auth_code, app_id_hash):
    url = "https://api-t1.fyers.in/api/v3/validate-authcode"
    payload = {
        "grant_type": "authorization_code",
        "appIdHash": app_id_hash,
        "code": auth_code
    }
    headers = {"Content-Type": "application/json"}

    res = requests.post(url, json=payload, headers=headers)
    return res.json()

# 5️⃣ Step: Update .env
def update_env_file(key, value):
    updated = False
    lines = []

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    lines.append(line)
    
    if not updated:
        lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)

def main():
    generate_login_url()
    auth_code = get_auth_code_from_user()
    app_id_hash = get_app_id_hash()
    print("\n🔐 Generating access token...")

    token_response = get_access_token(auth_code, app_id_hash)
    if token_response.get("s") != "ok":
        print("❌ Token generation failed:", token_response)
        return

    access_token = token_response.get("access_token")
    refresh_token = token_response.get("refresh_token")

    update_env_file("FYERS_ACCESS_TOKEN", access_token)
    update_env_file("FYERS_REFRESH_TOKEN", refresh_token)

    print("\n✅ Token generated successfully!")
    print("🔐 Access Token and Refresh Token saved to .env 🔒")

if __name__ == "__main__":
    main()
