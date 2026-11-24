"""Score new applicants.

    python -m src.predict --input data/sample_new_applicants.csv --output scored.csv
"""
import argparse

import joblib
import pandas as pd

from src.config import CATEGORICAL_FEATURES, MODELS_DIR, NUMERIC_FEATURES

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_model():
    return joblib.load(MODELS_DIR / "credit_approval_model.joblib")


def predict(df, bundle=None, threshold=None):
    bundle = bundle or load_model()
    threshold = bundle["threshold"] if threshold is None else threshold
    out = df.copy()
    out["ApprovalProbability"] = bundle["model"].predict_proba(df[FEATURES])[:, 1].round(4)
    out["Decision"] = (out["ApprovalProbability"] >= threshold).map({True: "Approve", False: "Reject"})
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default="scored_applicants.csv")
    p.add_argument("--threshold", type=float, help="defaults to the threshold saved with the model")
    a = p.parse_args()
    res = predict(pd.read_csv(a.input), threshold=a.threshold)
    res.to_csv(a.output, index=False)
    print(res[["ApprovalProbability", "Decision"]].to_string())
