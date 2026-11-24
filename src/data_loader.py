"""Loads the UCI Credit Approval data (crx.data), downloading it first if needed."""
import urllib.request

import numpy as np
import pandas as pd

from src.config import COLUMNS, DATA_URLS, RAW_DIR, RAW_FILE


def download_data(force: bool = False) -> None:
    """Fetch crx.data into data/raw, trying each mirror in turn."""
    if RAW_FILE.exists() and not force:
        return
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    last_err = None
    for url in DATA_URLS:
        try:
            urllib.request.urlretrieve(url, RAW_FILE)
            print(f"Downloaded dataset from {url}")
            return
        except Exception as err:  # noqa: BLE001
            last_err = err
    raise RuntimeError(f"Could not download dataset: {last_err}")


def load_raw() -> pd.DataFrame:
    """Return the raw dataset with named columns; '?' becomes NaN."""
    download_data()
    df = pd.read_csv(RAW_FILE, header=None, names=COLUMNS, na_values="?")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtypes and encode the target (1 = approved, 0 = rejected)."""
    df = df.copy()
    for col in ["Age", "Debt", "YearsEmployed", "CreditScore", "Income"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Approved"] = (df["Approved"] == "+").astype(int)
    df.insert(0, "ApplicantID", np.arange(1, len(df) + 1))
    return df


if __name__ == "__main__":
    data = clean(load_raw())
    print(data.head())
    print(data.isna().sum())
