import os
import requests
import pandas as pd

os.makedirs("data/raw", exist_ok=True)

schemes = {
    "HDFC_Top_100_Direct": "125497",
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_Large_Cap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

all_schemes_data = []

for name, code in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"Fetching {name} (Code: {code})...")
    
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        payload = response.json()
        meta = payload.get("meta", {})
        nav_records = payload.get("data", [])
        
        df = pd.DataFrame(nav_records)
        df["scheme_code"] = code
        df["scheme_name"] = meta.get("scheme_name", name)
        df["fund_house"] = meta.get("fund_house", "")
        df["scheme_category"] = meta.get("scheme_category", "")
        
        file_path = f"data/raw/live_nav_{code}_{name}.csv"
        df.to_csv(file_path, index=False)
        print(f" -> Saved {len(df)} rows to {file_path}")
        all_schemes_data.append(df)
    else:
        print(f" -> Failed to fetch {code}: HTTP {response.status_code}")

if all_schemes_data:
    combined_df = pd.concat(all_schemes_data, ignore_index=True)
    combined_df.to_csv("data/raw/live_nav_key_schemes_combined.csv", index=False)
    print("\nSaved combined live NAV dataset to data/raw/live_nav_key_schemes_combined.csv")