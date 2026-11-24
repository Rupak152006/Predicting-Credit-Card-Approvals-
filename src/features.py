import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.config import CATEGORICAL_FEATURES, NUMERIC_FEATURES

# Income, CreditScore, YearsEmployed and Debt are heavily right-skewed
# (Income skew ~13), so they get a log1p before scaling. Age is left as is.
SKEWED = ["Debt", "YearsEmployed", "CreditScore", "Income"]
PLAIN = [c for c in NUMERIC_FEATURES if c not in SKEWED]


def build_preprocessor():
    log_num = make_pipeline(SimpleImputer(strategy="median"),
                            FunctionTransformer(np.log1p, feature_names_out="one-to-one"),
                            StandardScaler())
    num = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    cat = make_pipeline(SimpleImputer(strategy="most_frequent"),
                        OneHotEncoder(handle_unknown="ignore", min_frequency=10))
    return ColumnTransformer([
        ("log", log_num, SKEWED),
        ("num", num, PLAIN),
        ("cat", cat, CATEGORICAL_FEATURES),
    ])


def _band(s, bins, labels, **kw):
    return pd.cut(s, bins, labels=labels, **kw).astype(str).replace("nan", "Unknown")


def add_bands(df):
    df = df.copy()
    df["AgeBand"] = _band(df["Age"], [0, 25, 35, 45, 55, 120],
                          ["<25", "25-34", "35-44", "45-54", "55+"], right=False)
    df["IncomeBand"] = _band(df["Income"], [-1, 0, 500, 2000, 10000, np.inf],
                             ["0", "1-500", "501-2k", "2k-10k", "10k+"])
    df["CreditScoreBand"] = _band(df["CreditScore"], [-1, 0, 2, 5, 10, np.inf],
                                  ["0", "1-2", "3-5", "6-10", "11+"])
    df["DebtBand"] = _band(df["Debt"], [-1, 1, 3, 7, np.inf], ["<1", "1-3", "3-7", "7+"])
    return df
