"""
Data Transformation Pipeline
=============================
Reads cleaned CSVs and produces a transformed/merged dataset ready for ML/analysis.

Transformations:
  1. Label encoding for binary categoricals
  2. One-hot encoding for multi-class categoricals
  3. StandardScaler on numerical features
  4. Log-transform on skewed financial columns
  5. Date feature extraction
  6. Merge customers + loans into a master analytical table
  7. Save transformed datasets & merged master table
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

os.makedirs("data/transformed", exist_ok=True)

# ──────────────────────────────────────────────────────────
# Load cleaned data
# ──────────────────────────────────────────────────────────

cust  = pd.read_csv("data/cleaned/customers_clean.csv",  parse_dates=["registration_date"])
loans = pd.read_csv("data/cleaned/loans_clean.csv",
                    parse_dates=["disbursement_date","maturity_date"])



# ──────────────────────────────────────────────────────────
# CUSTOMER TRANSFORMATIONS
# ──────────────────────────────────────────────────────────

cust_t = cust.copy()

# 1. Date features
cust_t["reg_year"]  = cust_t["registration_date"].dt.year
cust_t["reg_month"] = cust_t["registration_date"].dt.month

# 2. Log-transform skewed numerics
for col in ["annual_income","monthly_expenses"]:
    cust_t[f"log_{col}"] = np.log1p(cust_t[col])

# 3. Label encode binary & ordinal columns
le = LabelEncoder()
for col in ["gender","has_existing_loan"]:
    cust_t[f"{col}_enc"] = le.fit_transform(cust_t[col].astype(str))

edu_order = {"High School": 0, "Diploma": 1, "Bachelor'S": 2, "Master'S": 3, "Phd": 4}
cust_t["education_ord"] = cust_t["education_level"].map(edu_order).fillna(0).astype(int)

# 4. One-hot encode nominal categoricals
ohe_cols_c = ["marital_status","occupation","city"]
cust_ohe   = pd.get_dummies(cust_t[ohe_cols_c], drop_first=True, dtype=int)
cust_t     = pd.concat([cust_t, cust_ohe], axis=1)

# 5. StandardScaler on selected numerics
scale_cols_c = ["age","annual_income","monthly_expenses","credit_score",
                "years_employed","num_dependents","num_credit_cards","savings_ratio"]
scaler_c = StandardScaler()
cust_t[[f"{c}_scaled" for c in scale_cols_c]] = scaler_c.fit_transform(cust_t[scale_cols_c])

# 6. Credit risk tier
cust_t["credit_risk_tier"] = pd.cut(
    cust_t["credit_score"],
    bins=[299, 500, 650, 750, 900],
    labels=["Poor","Fair","Good","Excellent"]
)

cust_t.to_csv("data/transformed/customers_transformed.csv", index=False)

# ──────────────────────────────────────────────────────────
# LOAN TRANSFORMATIONS
# ──────────────────────────────────────────────────────────

loans_t = loans.copy()

# 1. Date features
loans_t["disbursement_year"]  = loans_t["disbursement_date"].dt.year
loans_t["disbursement_month"] = loans_t["disbursement_date"].dt.month
loans_t["days_to_maturity"]   = (loans_t["maturity_date"] - loans_t["disbursement_date"]).dt.days

# 2. Log-transform skewed numerics
for col in ["loan_amount","emi_amount","outstanding_balance","total_repayment","total_interest_paid"]:
    if col in loans_t.columns:
        loans_t[f"log_{col}"] = np.log1p(loans_t[col].clip(lower=0))

# 3. Label encode binary
for col in ["insurance_taken","default_flag"]:
    loans_t[f"{col}_enc"] = loans_t[col].astype(int)

# 4. One-hot encode
ohe_cols_l = ["loan_purpose","loan_type","repayment_frequency","risk_category"]
loans_ohe  = pd.get_dummies(loans_t[ohe_cols_l], drop_first=True, dtype=int)
loans_t    = pd.concat([loans_t, loans_ohe], axis=1)

# 5. StandardScaler
scale_cols_l = ["loan_amount","interest_rate","tenure_months","emi_amount",
                "num_payments_made","outstanding_balance","num_late_payments"]
scaler_l = StandardScaler()
loans_t[[f"{c}_scaled" for c in scale_cols_l]] = scaler_l.fit_transform(
    loans_t[scale_cols_l].fillna(0)
)

loans_t.to_csv("data/transformed/loans_transformed.csv", index=False)

# ──────────────────────────────────────────────────────────
# MASTER MERGED TABLE
# ──────────────────────────────────────────────────────────

master = loans.merge(cust, on="customer_id", how="left", suffixes=("_loan","_cust"))

# Derived cross-dataset features
master["emi_to_income_ratio"]     = (master["emi_amount"] / (master["annual_income"] / 12)).round(4)
master["loan_to_income_ratio"]    = (master["loan_amount"] / master["annual_income"]).round(4)
master["repayment_progress_pct"]  = ((master["num_payments_made"] / master["tenure_months"]) * 100).round(2)
master["remaining_balance_pct"]   = (master["outstanding_balance"] / master["loan_amount"]).round(4)

master.to_csv("data/transformed/master_merged.csv", index=False)
