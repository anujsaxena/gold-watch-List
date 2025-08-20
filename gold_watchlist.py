import requests
import pandas as pd
from datetime import datetime
import os

# --- Settings ---
TARGET_LOW = 96000     # INR/10g landed wholesale
TARGET_HIGH = 98000
IMPORT_DUTY = 0.06
GRAMS_PER_OZ = 31.1034768
CSV_PATH = "gold_watchlist.csv"

# API Endpoints
GOLD_API_URL = "https://gold-api.com/api/XAU/USD"
USD_INR_API = "https://api.exchangerate.host/latest?base=USD&symbols=INR"

def get_gold_usd_oz():
    resp = requests.get(GOLD_API_URL)
    data = resp.json()
    return data["price"]  # Price in USD/oz

def get_usd_inr_rate():
    resp = requests.get(USD_INR_API)
    data = resp.json()
    return data["rates"]["INR"]

def compute_landed_price(usd_oz, usd_inr):
    usd_per_10g = (usd_oz / GRAMS_PER_OZ) * 10
    return usd_per_10g * usd_inr * (1 + IMPORT_DUTY)

def run_and_update():
    usd_oz = get_gold_usd_oz()
    usd_inr = get_usd_inr_rate()
    landed_price = compute_landed_price(usd_oz, usd_inr)
    status = "BUY" if TARGET_LOW <= landed_price <= TARGET_HIGH else "WAIT"

    row = {
        "Date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "Gold USD/oz": round(usd_oz, 2),
        "USD/INR": round(usd_inr, 2),
        "Landed INR/10g": round(landed_price, 2),
        "Status": status
    }

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(CSV_PATH, index=False)
    print("Watchlist updated:", row)

if _name_ == "_main_":
    run_and_update()