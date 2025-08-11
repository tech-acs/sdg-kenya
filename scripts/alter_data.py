# scripts/alter_data.py
import numpy as np
import pandas as pd

_DIGIT_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def _clean_df(df: pd.DataFrame, indicator_id=None) -> pd.DataFrame:
    # Trim all text columns (fixes COMMENT_OBS/SOURCE_DETAIL etc.)
    obj_cols = df.select_dtypes(include=["object"]).columns
    for c in obj_cols:
        df[c] = (df[c].astype(str)
                        .str.replace("\u00A0", " ", regex=False)  # NBSP
                        .str.strip())

    # Normalise UN tokens -> NaN
    na_tokens = {"", "nan", "NaN", "N/A", "n/a", "..", "—", "–", "…"}
    for tok in list(na_tokens):
        df.replace(tok, np.nan, inplace=True)

    # Map common yes/no text to numeric (seen in policy/legal indicators)
    if "Value" in df.columns:
        t = (df["Value"].astype(str)
             .str.translate(_DIGIT_TRANS)
             .str.replace("\u00A0", " ", regex=False)
             .str.strip())
        t = (t.replace({"Yes": "1", "No": "0", "yes": "1", "no": "0",
                        "TRUE": "1", "FALSE": "0", "True": "1", "False": "0"}))
        t = t.str.replace(r"^[<>]=?\s*", "", regex=True)   # <5, >=10
        t = t.str.replace("−", "-", regex=False)           # unicode minus
        t = t.str.replace("%", "", regex=False)
        t = t.str.replace(",", "", regex=False)            # 1,234 -> 1234
        t = t.str.replace(r"^(-?\d+),(\d+)$", r"\1.\2", regex=True)  # 12,3 -> 12.3
        df["Value"] = pd.to_numeric(t, errors="coerce")
        # Drop rows with no numeric value
        df = df[df["Value"].notna()].copy()

    print(f"[alter_data] cleaned {indicator_id or ''} rows={len(df)}", flush=True)
    return df

# Compatible with multiple sdg-build versions
def alter_data(arg1, arg2=None, **kwargs):
    if hasattr(arg1, "columns"):   # (df, context)
        ind = (arg2 or {}).get("indicator_id") if isinstance(arg2, dict) else None
        return _clean_df(arg1.copy(), ind)
    elif hasattr(arg2, "columns"): # (indicator_id, df)
        return _clean_df(arg2.copy(), arg1)
    return arg1
