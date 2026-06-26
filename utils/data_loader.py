import pandas as pd
from typing import Tuple, Optional


def load_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load a CSV or Excel file uploaded via Streamlit into a pandas DataFrame.

    Returns:
        (df, None)        on success
        (None, error_msg) on failure
    """
    try:
        filename = uploaded_file.name.lower()

        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file type. Please upload a CSV or Excel file."

        if df.empty:
            return None, "The uploaded file is empty."

        # Clean column names: strip whitespace
        df.columns = df.columns.str.strip()

        # Try to auto-parse date columns
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                except Exception:
                    pass  # leave as-is if parsing fails

        return df, None

    except Exception as e:
        return None, str(e)


def describe_dataframe(df: pd.DataFrame) -> str:
    """
    Build a compact text description of the dataframe to inject into the LLM prompt.
    Includes column names, dtypes, and a few sample values per column.
    """
    lines = [
        f"The dataframe has {len(df):,} rows and {len(df.columns)} columns.",
        "Columns and sample values:",
    ]
    for col in df.columns:
        sample = df[col].dropna().head(3).tolist()
        dtype = str(df[col].dtype)
        lines.append(f"  - '{col}' ({dtype}): {sample}")
    return "\n".join(lines)
