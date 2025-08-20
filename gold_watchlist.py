import requests
import pandas as pd
from datetime import datetime

# Your gold API endpoint (replace with actual API or web scraping)
# For demo, we'll use a placeholder value
gold_price = 5850  # per gram in INR

# File path
file_path = "gold_watchlist.csv"

# Load existing data if file exists
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Date", "Price_per_gram_INR"])

# Append new data
df = pd.concat([df, pd.DataFrame({"Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                                  "Price_per_gram_INR": [gold_price]})])

# Save updated CSV
df.to_csv(file_path, index=False)
print(f"Updated gold price to {gold_price} INR/g at {datetime.now()}")
