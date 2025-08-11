# scripts/alter_data.py
import pandas as pd

# Open SDG will import this function and call it for every indicator.
def alter_data(df, indicator_id, meta=None, **kwargs):
    # 1) Trim leading/trailing spaces across all text columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()

    # 2) Make Value truly numeric (drop common placeholders)
    if 'Value' in df.columns:
        placeholders = ['..', '.', ':', '—', '–', '-', '…', 'NA', 'N/A', 'n/a', '']
        df['Value'] = df['Value'].replace(placeholders, None)
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df[df['Value'].notna()].copy()
        # keep as float
        df['Value'] = df['Value'].astype(float)

    return df
