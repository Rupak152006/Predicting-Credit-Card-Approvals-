import pandas as pd

from src.data_loader import clean, load_raw
from src.features import add_bands
from src.predict import FEATURES, load_model, predict


def test_raw_shape():
    df = load_raw()
    assert df.shape == (690, 16)


def test_clean_target_binary():
    df = clean(load_raw())
    assert set(df["Approved"].unique()) == {0, 1}
    assert df["Age"].dtype.kind == "f"


def test_bands_no_missing_labels():
    df = add_bands(clean(load_raw()).dropna(subset=["Age"]))
    assert "nan" not in set(df["AgeBand"])


def test_predict_outputs_probabilities():
    df = clean(load_raw()).head(20)
    out = predict(df[FEATURES], load_model())
    assert out["ApprovalProbability"].between(0, 1).all()
    assert set(out["Decision"]) <= {"Approve", "Reject"}
