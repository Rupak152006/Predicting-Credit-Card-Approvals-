"""Run the whole project: load, clean, EDA, train, evaluate, export for Power BI."""
import time

from src.config import PROCESSED_DIR
from src.dashboard_preview import render
from src.data_loader import clean, load_raw
from src.eda import run_eda
from src.export_powerbi import export
from src.train import (compare_models, evaluate, feature_importance, pick_threshold, save,
                       split, tune, FEATURES)


def main():
    t0 = time.time()
    df = clean(load_raw())
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "credit_approval_clean.csv", index=False)
    run_eda(df)

    X_train, X_test, y_train, y_test = split(df.set_index("ApplicantID", drop=False))

    print("Baseline comparison (5x3 repeated CV):")
    cv_table = compare_models(X_train, y_train)
    print(cv_table.round(3).to_string(index=False))

    print("Tuning the top 3:")
    name, search = tune(cv_table["Model"].head(3).tolist(), X_train, y_train)
    model = search.best_estimator_
    threshold = pick_threshold(model, X_train, y_train)
    print(f"Picked {name}, threshold {threshold}")

    metrics = evaluate(model, X_test, y_test, threshold)
    # permutation importance on all 690 rows; the 138-row test set alone is too noisy
    importance = feature_importance(model, df[FEATURES], df["Approved"])
    save(model, name, search.best_params_, threshold, cv_table, metrics)

    export(df, model, FEATURES, set(X_test.index), cv_table, metrics, importance, threshold)
    render()
    print({k: round(v, 3) for k, v in metrics.items()}, f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
