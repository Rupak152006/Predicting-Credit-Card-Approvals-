import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, RocCurveDisplay, accuracy_score,
                             classification_report, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import (RandomizedSearchCV, RepeatedStratifiedKFold,
                                     StratifiedKFold, cross_val_predict, cross_validate,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from xgboost import XGBClassifier

from src.config import (CATEGORICAL_FEATURES, FIGURES_DIR, MODELS_DIR, NUMERIC_FEATURES,
                        RANDOM_STATE, REPORTS_DIR, TARGET, TEST_SIZE)
from src.features import build_preprocessor

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
METRICS = ["accuracy", "precision", "recall", "f1", "roc_auc"]
SEED = RANDOM_STATE

# model -> (estimator, search space for RandomizedSearchCV)
MODELS = {
    "LogisticRegression": (
        LogisticRegression(max_iter=5000),
        {"model__C": np.logspace(-3, 2, 30), "model__class_weight": [None, "balanced"]}),
    "RandomForest": (
        RandomForestClassifier(random_state=SEED, n_jobs=1),
        {"model__n_estimators": [200, 300, 500], "model__max_depth": [3, 5, 8, None],
         "model__min_samples_leaf": [1, 2, 4, 8], "model__max_features": ["sqrt", 0.3, 0.5]}),
    "GradientBoosting": (
        GradientBoostingClassifier(random_state=SEED),
        {"model__n_estimators": [50, 100, 200, 300], "model__learning_rate": [0.02, 0.05, 0.1],
         "model__max_depth": [1, 2, 3], "model__subsample": [0.7, 0.85, 1.0],
         "model__min_samples_leaf": [1, 5, 10]}),
    "XGBoost": (
        XGBClassifier(random_state=SEED, eval_metric="logloss", n_jobs=1),
        {"model__n_estimators": [100, 200, 400], "model__max_depth": [1, 2, 3, 4],
         "model__learning_rate": [0.02, 0.05, 0.1], "model__subsample": [0.7, 0.85, 1.0],
         "model__colsample_bytree": [0.6, 0.8, 1.0], "model__reg_lambda": [0.5, 1, 5, 10]}),
    "SVM": (
        CalibratedClassifierCV(SVC(random_state=SEED), ensemble=False),
        {"model__estimator__C": np.logspace(-2, 1.5, 15),
         "model__estimator__kernel": ["rbf", "linear"]}),
}


def make_pipe(est):
    return Pipeline([("prep", build_preprocessor()), ("model", est)])


def split(df):
    return train_test_split(df[FEATURES], df[TARGET], test_size=TEST_SIZE,
                            stratify=df[TARGET], random_state=SEED)


def compare_models(X, y):
    # 5x3 repeated CV: with only ~550 training rows a single 5-fold split is noisy
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=SEED)
    rows = []
    for name, (est, _) in MODELS.items():
        s = cross_validate(make_pipe(est), X, y, cv=cv, scoring=METRICS, n_jobs=-1)
        row = {"Model": name, **{m: s[f"test_{m}"].mean() for m in METRICS}}
        row["roc_auc_std"] = s["test_roc_auc"].std()
        rows.append(row)
    return pd.DataFrame(rows).sort_values("roc_auc", ascending=False, ignore_index=True)


def tune(names, X, y, n_iter=40):
    """Tune each shortlisted model and keep the one with the best CV AUC."""
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    results = {}
    for name in names:
        est, space = MODELS[name]
        search = RandomizedSearchCV(make_pipe(est), space, n_iter=n_iter, cv=cv,
                                    scoring="roc_auc", n_jobs=-1, random_state=SEED)
        search.fit(X, y)
        results[name] = search
        print(f"  {name:<18} CV AUC {search.best_score_:.4f}")
    best = max(results, key=lambda n: results[n].best_score_)
    return best, results[best]


def pick_threshold(model, X, y):
    """Choose the cut-off that maximises F1 on out-of-fold predictions (train set only)."""
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    oof = cross_val_predict(model, X, y, cv=cv, method="predict_proba", n_jobs=-1)[:, 1]
    grid = np.arange(0.30, 0.71, 0.01)
    scores = [f1_score(y, oof >= t) for t in grid]
    return round(float(grid[int(np.argmax(scores))]), 2)


def evaluate(model, X_test, y_test, threshold=0.5):
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred),
        "recall": recall_score(y_test, pred),
        "f1": f1_score(y_test, pred),
        "roc_auc": roc_auc_score(y_test, proba),
    }
    print(classification_report(y_test, pred, target_names=["Rejected", "Approved"]))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=["Rejected", "Approved"],
                                            cmap="Greens", ax=ax, colorbar=False)
    ax.set_title(f"Confusion matrix (test, threshold {threshold})")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "05_confusion_matrix.png", dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    RocCurveDisplay.from_predictions(y_test, proba, ax=ax, name="Final model")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_title("ROC curve (test)")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "06_roc_curve.png", dpi=120); plt.close(fig)
    return metrics


def feature_importance(model, X, y):
    """Permutation importance on the original columns, so every model type is comparable."""
    from sklearn.inspection import permutation_importance

    r = permutation_importance(model, X, y, scoring="roc_auc", n_repeats=20,
                               random_state=SEED, n_jobs=-1)
    imp = pd.Series(r.importances_mean, index=X.columns).clip(lower=0)
    out = (imp / imp.sum()).sort_values(ascending=False)
    out = out.rename("Importance").rename_axis("Feature").reset_index()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(out["Feature"][::-1], out["Importance"][::-1], color="#2a9d8f")
    ax.set(title="Permutation importance (drop in AUC, normalised)", xlabel="Share")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "07_feature_importance.png", dpi=120); plt.close(fig)
    return out


def save(model, name, params, threshold, cv_table, metrics):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "threshold": threshold}, MODELS_DIR / "credit_approval_model.joblib")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cv_table.to_csv(REPORTS_DIR / "model_comparison.csv", index=False)
    clean_params = {k.split("__")[-1]: (v.item() if hasattr(v, "item") else v) for k, v in params.items()}
    with open(REPORTS_DIR / "metrics.json", "w") as f:
        json.dump({"best_model": name, "best_params": clean_params, "threshold": threshold,
                   "test_metrics": {k: round(v, 4) for k, v in metrics.items()}}, f, indent=2)
