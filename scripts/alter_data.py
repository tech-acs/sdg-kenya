# scripts/alter_data.py
import pandas as pd
import numpy as np
import re

def alter_data(df, indicator_id=None, config=None):
    # Trim whitespace on all string columns (handles COMMENT_OBS/SOURCE_DETAIL too)
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object:
            df[c] = df[c].astype(str).str.replace("\u00A0", " ", regex=False).str.strip()

    if "Value" in df.columns:
        # Work on a string view
        t = df["Value"].astype(str).str.replace("\u00A0", " ", regex=False).str.strip()

        # Normalize variance seen in UNSD payloads
        t = t.replace(
            {"": np.nan, "nan": np.nan, "NaN": np.nan, "N/A": np.nan, "n/a": np.nan, "—": np.nan, "–": np.nan}
        )

        # If an inequality is present, move it to COMMENT_OBS and strip from Value
        ineq_mask = t.str.match(r"^[<>]=?\s*")
        if "COMMENT_OBS" in df.columns:
            df.loc[ineq_mask, "COMMENT_OBS"] = (
                df.loc[ineq_mask, "COMMENT_OBS"].fillna("").str.strip() + " (original value had inequality)"
            ).str.strip()
        # Remove the inequality symbols from Value
        t = t.str.replace(r"^[<>]=?\s*", "", regex=True)

        # Normalize minus and percentages; drop thousands separators
        t = t.str.replace("−", "-", regex=False)      # Unicode minus -> hyphen
        t = t.str.replace("%", "", regex=False)
        t = t.str.replace(",", "", regex=False)       # 1,234 -> 1234

        # Handle comma decimals like 12,3 -> 12.3 (only when that pattern remains)
        t = t.str.replace(r"^(-?\d+),(\d+)$", r"\1.\2", regex=True)

        # Final strip and coerce
        t = t.str.strip()
        df["Value"] = pd.to_numeric(t, errors="coerce")

    # Re-trim specific text columns (idempotent)
    for col in ("COMMENT_OBS", "SOURCE_DETAIL"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df
