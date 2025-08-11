# scripts/alter_data.py
import pandas as pd, numpy as np

def alter_data(df, context=None):
    # trim all text cols (fixes COMMENT_OBS / SOURCE_DETAIL)
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = (df[c].astype(str)
                           .str.replace("\u00A0"," ",regex=False)
                           .str.strip())
    if "Value" in df.columns:
        t = (df["Value"].astype(str).str.replace("\u00A0"," ",regex=False).str.strip()
             .replace({"":np.nan,"nan":np.nan,"NaN":np.nan,"N/A":np.nan,"n/a":np.nan,"—":np.nan,"–":np.nan}))
        t = t.str.replace(r"^[<>]=?\s*", "", regex=True)  # drop <, >, <=, >=
        t = t.str.replace("−","-",regex=False).str.replace("%","",regex=False).str.replace(",","",regex=False)
        t = t.str.replace(r"^(-?\d+),(\d+)$", r"\1.\2", regex=True)  # 12,3 -> 12.3
        df["Value"] = pd.to_numeric(t, errors="coerce")
    return df
