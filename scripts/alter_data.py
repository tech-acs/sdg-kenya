import numpy as np
import pandas as pd

_DIGIT_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    # Trim all text cols (fixes COMMENT_OBS / SOURCE_DETAIL / Observation-level footnotes)
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = (df[c].astype(str)
                       .str.replace("\u00A0", " ", regex=False)  # NBSP
                       .str.strip())
    if "Value" in df.columns:
        t = (df["Value"].astype(str)
             .str.translate(_DIGIT_TRANS)
             .str.replace("\u00A0", " ", regex=False)
             .str.strip()
             .replace({"": np.nan, "nan": np.nan, "NaN": np.nan,
                       "N/A": np.nan, "n/a": np.nan, "..": np.nan,
                       "—": np.nan, "–": np.nan}))
        t = t.str.replace(r"^[<>]=?\s*", "", regex=True)  # remove <, >, <=, >=
        t = t.str.replace("−", "-", regex=False)          # unicode minus
        t = t.str.replace("%", "", regex=False)
        t = t.str.replace(",", "", regex=False)           # 1,234 -> 1234
        t = t.str.replace(r"^(-?\d+),(\d+)$", r"\1.\2", regex=True)  # 12,3 -> 12.3
        df["Value"] = pd.to_numeric(t, errors="coerce")
    return df

# Works across sdg-build versions (param order differs)
def alter_data(arg1, arg2=None, **kwargs):
    if hasattr(arg1, "columns"):   # (df, context)
        return _clean(arg1.copy())
    elif hasattr(arg2, "columns"): # (indicator_id, df)
        return _clean(arg2.copy())
    return arg1
