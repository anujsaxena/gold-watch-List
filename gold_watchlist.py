import requests
import pandas as pd
from datetime import datetime, timezone
import os
import sys

# --- Settings ---
TARGET_LOW = 96000     # INR/10g landed wholesale
TARGET_HIGH = 98000
IMPORT_DUTY = 0.06
GRAMS_PER_OZ = 31.1034768
CSV_PATH = "gold_watchlist.csv"

# API Endpoints
# Note: These API URLs require an API key to work correctly.
GOLD_API_URL = "https://api.metalpriceapi.com/v1/latest"
USD_INR_API = "https://api.exchangerate.host/latest"

def get_gold_usd_oz(api_key):
    """Fetches the real-time gold price from an API."""
    # The 'base' currency is USD, and the 'currency' requested is XAU (gold)
    params = {'api_key': api_key, 'base': 'USD', 'currencies': 'XAU'}
    try:
        resp = requests.get(GOLD_API_URL, params=params)
        resp.raise_for_status()  # Raise an exception for bad status codes
        data = resp.json()
        
        # The key for gold price in the response is 'XAU', not 'USD'
        return data['rates']['XAU']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching gold price: {e}")
        return None
    except KeyError:
        print("API response does not contain the expected 'rates' or 'XAU' key.")
        print("API response:", data) # Print the full response to debug
        return None

def get_usd_inr_rate():
    """Fetches the real-time USD to INR exchange rate."""
    try:
        resp = requests.get(USD_INR_API, params={'base': 'USD'})
        resp.raise_for_status()
        data = resp.json()
        return data["rates"]["INR"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching USD/INR rate: {e}")
        return None
    except KeyError:
        print("API response does not contain the expected 'rates' or 'INR' key.")
        return None

def compute_landed_price(usd_oz, usd_inr):
    """Calculates the landed price of gold in INR per 10 grams."""
    usd_per_10g = (usd_oz / GRAMS_PER_OZ) * 10
    return usd_per_10g * usd_inr * (1 + IMPORT_DUTY)

def run_and_update(gold_api_key):
    """Runs the main logic to fetch data, compute the price, and update the CSV."""
    usd_oz = get_gold_usd_oz(gold_api_key)
    usd_inr = get_usd_inr_rate()

    if usd_oz is None or usd_inr is None:
        print("Skipping CSV update due to failed API calls.")
        return

    landed_price = compute_landed_price(usd_oz, usd_inr)
    status = "BUY" if TARGET_LOW <= landed_price <= TARGET_HIGH else "WAIT"

    current_time_utc = datetime.now(timezone.utc)
    
    row = {
        "Date": current_time_utc.strftime("%Y-%m-%d %H:%M:%S"),
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: The gold API key is required as a command-line argument.")
        sys.exit(1)
        
    api_key = sys.argv[1]
    run_and_update(api_key)