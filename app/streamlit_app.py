# streamlit run app/streamlit_app.py
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.predict import load_model, predict  # noqa: E402

st.set_page_config(page_title="Credit approval check")
st.title("Credit card approval check")

bundle = load_model()
st.caption(f"Model: gradient boosting, approve if probability >= {bundle['threshold']:.2f}")
yn = {"Yes": "t", "No": "f"}

c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age", 13.0, 90.0, 30.0)
    debt = st.number_input("Debt", 0.0, 30.0, 2.0)
    years = st.number_input("Years employed", 0.0, 30.0, 2.0)
    credit = st.number_input("Credit score (A11)", 0, 70, 1)
    income = st.number_input("Income", 0, 100000, 500)
with c2:
    prior = st.selectbox("Prior default flag (A9)", ["Yes", "No"])
    employed = st.selectbox("Employed", ["Yes", "No"])
    license_ = st.selectbox("Driver's license", ["No", "Yes"])
    citizen = st.selectbox("Citizen", ["g", "s", "p"])
    gender = st.selectbox("Gender (A1)", ["b", "a"])

with st.expander("Other attributes"):
    married = st.selectbox("Married (A4)", ["u", "y", "l"])
    bank = st.selectbox("Bank customer (A5)", ["g", "p", "gg"])
    edu = st.selectbox("Education level (A6)", ["c", "q", "w", "i", "aa", "ff", "k", "cc", "m", "x", "d", "e", "j", "r"])
    eth = st.selectbox("Ethnicity (A7)", ["v", "h", "bb", "ff", "j", "z", "dd", "n", "o"])

if st.button("Predict", type="primary"):
    row = pd.DataFrame([{
        "Age": age, "Debt": debt, "YearsEmployed": years, "CreditScore": credit, "Income": income,
        "Gender": gender, "Married": married, "BankCustomer": bank, "EducationLevel": edu,
        "Ethnicity": eth, "PriorDefault": yn[prior], "Employed": yn[employed],
        "DriversLicense": yn[license_], "Citizen": citizen,
    }])
    res = predict(row, bundle).iloc[0]
    p = res["ApprovalProbability"]
    show = st.success if res["Decision"] == "Approve" else st.error
    show(f"{res['Decision']} (probability {p:.1%})")
    st.progress(float(p))
