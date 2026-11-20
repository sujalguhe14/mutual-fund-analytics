import glob
import os
import pandas as pd

raw_folder = "data/raw"
csv_files = sorted(glob.glob(os.path.join(raw_folder, "*.csv")))

# Filter out generated live_nav files so we inspect the 10 provided CSVs
provided_csvs = [f for f in csv_files if not os.path.basename(f).startswith("live_nav_")]

print(f"Found {len(provided_csvs)} provided CSV datasets.\n" + "=" * 60)

datasets = {}

for file_path in provided_csvs:
    file_name = os.path.basename(file_path)
    df = pd.read_csv(file_path)
    datasets[file_name] = df
    
    print(f"\nDATASET: {file_name}")
    print(f"Shape: {df.shape}")
    print("Data Types:\n", df.dtypes)
    print("\nFirst 5 Rows:\n", df.head())
    
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0].to_dict()
    dup_count = df.duplicated().sum()
    print(f"Anomalies -> Missing values: {null_cols if null_cols else 'None'} | Exact Duplicates: {dup_count}")
    print("-" * 60)

# Match your exact filenames: fund_master01.csv and nav_hist02.csv
fund_master_key = next((k for k in datasets if "fund_master" in k.lower()), None)
nav_history_key = next((k for k in datasets if "nav_hist" in k.lower()), None)

if fund_master_key:
    fm = datasets[fund_master_key]
    print("\n=== FUND MASTER EXPLORATION ===")
    for col in ["fund_house", "category", "sub_category", "risk_grade", "scheme_category"]:
        if col in fm.columns:
            print(f"Unique {col} ({fm[col].nunique()}): {fm[col].dropna().unique()[:10]}")

if fund_master_key and nav_history_key:
    fm = datasets[fund_master_key]
    nh = datasets[nav_history_key]
    
    fm_code_col = next((c for c in fm.columns if "code" in c.lower() or "amfi" in c.lower()), fm.columns[0])
    nh_code_col = next((c for c in nh.columns if "code" in c.lower() or "amfi" in c.lower()), nh.columns[0])
    
    fm_codes = set(fm[fm_code_col].dropna().astype(str))
    nh_codes = set(nh[nh_code_col].dropna().astype(str))
    
    missing_in_nav = fm_codes - nh_codes
    print("\n=== AMFI CODE VALIDATION ===")
    print(f"Total unique AMFI codes in {fund_master_key}: {len(fm_codes)}")
    print(f"Total unique AMFI codes in {nav_history_key}: {len(nh_codes)}")
    print(f"Codes in fund_master missing from nav_history: {len(missing_in_nav)}")
    if missing_in_nav:
        print("Missing codes sample:", list(missing_in_nav)[:10])

os.makedirs("reports", exist_ok=True)
with open("reports/day1_data_quality_summary.txt", "w") as f:
    f.write("DAY 1 DATA QUALITY & INGESTION SUMMARY\n")
    f.write("=" * 40 + "\n")
    for name, df in datasets.items():
        f.write(f"{name}: {df.shape[0]} rows, {df.shape[1]} cols, {df.isnull().sum().sum()} nulls, {df.duplicated().sum()} duplicates\n")
    if fund_master_key and nav_history_key:
        f.write(f"\nAMFI Validation: {len(fm_codes - nh_codes)} fund_master codes missing in nav_history.\n")

print("\nSaved data quality summary to reports/day1_data_quality_summary.txt")