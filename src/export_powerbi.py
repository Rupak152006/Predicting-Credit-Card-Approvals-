"""CSV exports for the Power BI report."""
import pandas as pd

from src.config import POWERBI_DIR
from src.features import add_bands


def export(df, model, features, test_ids, cv_table, metrics, importance, threshold=0.5):
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    # Fact table: one row per application with model output
    fact = add_bands(df)
    yes_no = {"t": "Yes", "f": "No"}
    # A9 is anonymised; "t" goes with ~79% approval, so it is shown as a neutral True/False flag
    fact["PriorDefaultFlag"] = fact["PriorDefault"].map({"t": "True", "f": "False"})
    fact["EmployedLabel"] = fact["Employed"].map(yes_no)
    fact["DriversLicenseLabel"] = fact["DriversLicense"].map(yes_no)
    fact["CitizenLabel"] = fact["Citizen"].map({"g": "By birth", "p": "Other", "s": "By naturalisation"})
    proba = model.predict_proba(df[features])[:, 1]
    fact["ApprovalProbability"] = proba.round(4)
    fact["PredictedApproved"] = (proba >= threshold).astype(int)
    fact["ActualStatus"] = fact["Approved"].map({1: "Approved", 0: "Rejected"})
    fact["PredictedStatus"] = fact["PredictedApproved"].map({1: "Approved", 0: "Rejected"})
    fact["Dataset"] = fact["ApplicantID"].isin(test_ids).map({True: "Test", False: "Train"})
    fact["PredictionOutcome"] = [
        ("True Positive" if a and p else "True Negative" if not a and not p
         else "False Positive" if p else "False Negative")
        for a, p in zip(fact["Approved"], fact["PredictedApproved"])
    ]
    fact["RiskSegment"] = pd.cut(proba, [-0.01, 0.3, 0.7, 1.0],
                                 labels=["High Risk", "Review", "Low Risk"]).astype(str)
    # Sort-order helpers for Power BI "Sort by column"
    orders = {
        "AgeBand": ["<25", "25-34", "35-44", "45-54", "55+", "Unknown"],
        "IncomeBand": ["0", "1-500", "501-2k", "2k-10k", "10k+"],
        "CreditScoreBand": ["0", "1-2", "3-5", "6-10", "11+"],
        "DebtBand": ["<1", "1-3", "3-7", "7+"],
        "RiskSegment": ["High Risk", "Review", "Low Risk"],
    }
    for col, order in orders.items():
        fact[col + "Order"] = fact[col].map({v: i for i, v in enumerate(order, 1)})
    fact.drop(columns=["ZipCode"]).to_csv(POWERBI_DIR / "applications_scored.csv", index=False)

    cv_table.drop(columns="roc_auc_std", errors="ignore").round(4).to_csv(POWERBI_DIR / "model_comparison.csv", index=False)
    importance.round(4).to_csv(POWERBI_DIR / "feature_importance.csv", index=False)
    pd.DataFrame([{"Metric": k.replace("_", " ").upper() if k == "roc_auc" else k.title(),
                   "Value": round(v, 4)} for k, v in metrics.items()]) \
        .to_csv(POWERBI_DIR / "test_metrics.csv", index=False)
    print(f"Power BI datasets written to {POWERBI_DIR}")
