import numpy as np
import pandas as pd

# Map Arabic-Indic digits to ASCII (covers ٠١٢٣٤٥٦٧٨٩ and ۰۱۲۳۴۵۶۷۸۹)
_DIGIT_TRANS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def alter_data(df, context=None):
    # Trim all text cols (also fixes COMMENT_OBS / SOURCE_DETAIL / Observation-level footnotes)
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = (df[c].astype(str)
                           .str.replace("\u00A0", " ", regex=False)  # NBSP
                           .str.strip())

    # Normalise Value from UN SDG API
    if "Value" in df.columns:
        t = (df["Value"].astype(str)
             .str.translate(_DIGIT_TRANS)
             .str.replace("\u00A0", " ", regex=False)
             .str.strip()
             .replace({"": np.nan, "nan": np.nan, "NaN": np.nan,
                       "N/A": np.nan, "n/a": np.nan, "..": np.nan,
                       "—": np.nan, "–": np.nan}))
        # drop inequality signs like <5, >=10
        t = t.str.replace(r"^[<>]=?\s*", "", regex=True)
        # unicode minus to hyphen
        t = t.str.replace("−", "-", regex=False)
        # remove percent and thousands separators
        t = t.str.replace("%", "", regex=False).str.replace(",", "", regex=False)
        # convert comma decimals: 12,3 -> 12.3
        t = t.str.replace(r"^(-?\d+),(\d+)$", r"\1.\2", regex=True)
        df["Value"] = pd.to_numeric(t, errors="coerce")

    return df
