"""
Data Cleaning Pipeline
======================
Reads raw CSVs, applies cleaning steps, and saves cleaned files to data/cleaned/.

Cleaning steps performed:
  1. Remove exact duplicate rows
  2. Fix data types
  3. Handle missing values (median / mode imputation)
  4. Detect & cap outliers (IQR method)
  5. Standardise text columns (strip, title-case)
  6. Validate referential integrity (loan → customer)
  7. Save cleaned datasets + generate a cleaning report
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime

os.makedirs("data/cleaned", exist_ok=True)

# ──────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────

def cap_outliers_iqr(df, cols, factor=3.0):
    """Winsorise numeric columns at [Q1 - factor*IQR, Q3 + factor*IQR]."""
    report = {}
    for col in cols:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        before = ((df[col] < lower) | (df[col] > upper)).sum()
        df[col] = df[col].clip(lower=lower, upper=upper)
        report[col] = {"outliers_capped": int(before), "lower_bound": round(lower, 2), "upper_bound": round(upper, 2)}
    return df, report

def impute_missing(df, strategy="median"):
    """Impute numeric cols with median/mean; categorical with mode."""
    impute_report = {}
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median() if strategy == "median" else df[col].mean()
            df[col] = df[col].fillna(fill_val)
            impute_report[col] = {"missing": int(missing), "strategy": strategy, "fill_value": round(fill_val, 4)}
        else:
            fill_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(fill_val)
            impute_report[col] = {"missing": int(missing), "strategy": "mode", "fill_value": fill_val}
    return df, impute_report

# ──────────────────────────────────────────────────────────
# 1. CLEAN CUSTOMERS
# ──────────────────────────────────────────────────────────

cust = pd.read_csv("data/raw/customers_raw.csv", parse_dates=["registration_date"])
raw_shape = cust.shape

# --- 1a. Remove duplicates ---
cust.drop_duplicates(subset="customer_id", keep="first", inplace=True)
cust.reset_index(drop=True, inplace=True)

# --- 1b. Fix data types ---
cust["age"]            = pd.to_numeric(cust["age"],            errors="coerce")
cust["annual_income"]  = pd.to_numeric(cust["annual_income"],  errors="coerce")
cust["credit_score"]   = pd.to_numeric(cust["credit_score"],   errors="coerce")
cust["years_employed"] = pd.to_numeric(cust["years_employed"], errors="coerce")
cust["num_dependents"] = pd.to_numeric(cust["num_dependents"], errors="coerce")
cust["num_credit_cards"]= pd.to_numeric(cust["num_credit_cards"],errors="coerce")

# --- 1c. Standardise text ---
for col in ["first_name","last_name","city","state","occupation","education_level","marital_status","gender"]:
    cust[col] = cust[col].astype(str).str.strip().str.title()

# --- 1d. Validate age & credit_score ranges ---
cust = cust[(cust["age"].between(18, 100)) | cust["age"].isna()]
cust.loc[~cust["credit_score"].between(300, 900), "credit_score"] = np.nan

# --- 1e. Handle missing values ---
cust, impute_rep_c = impute_missing(cust)

# --- 1f. Cap outliers ---
num_cols_c = ["annual_income","monthly_expenses","credit_score","num_dependents","years_employed"]
cust, out_rep_c = cap_outliers_iqr(cust, num_cols_c)

# --- 1g. Derived columns ---
cust["income_tier"] = pd.cut(
    cust["annual_income"],
    bins=[0, 300_000, 600_000, 1_000_000, 2_000_000, np.inf],
    labels=["Low","Lower-Mid","Mid","Upper-Mid","High"]
)
cust["savings_ratio"] = ((cust["annual_income"] - cust["monthly_expenses"]*12) /
                          cust["annual_income"]).round(4)
cust["age_group"] = pd.cut(
    cust["age"],
    bins=[17, 30, 40, 50, 60, 100],
    labels=["21-30","31-40","41-50","51-60","60+"]
)

cust.to_csv("data/cleaned/customers_clean.csv", index=False)

# ──────────────────────────────────────────────────────────
# 2. CLEAN LOANS
# ──────────────────────────────────────────────────────────

loans = pd.read_csv(
    "data/raw/loans_raw.csv",
    parse_dates=["disbursement_date","maturity_date"]
)

# --- 2a. Remove duplicates ---
loans.drop_duplicates(subset="loan_id", keep="first", inplace=True)
loans.reset_index(drop=True, inplace=True)

# --- 2b. Fix data types ---
for col in ["loan_amount","interest_rate","emi_amount","outstanding_balance",
            "collateral_value","penalty_charges"]:
    loans[col] = pd.to_numeric(loans[col], errors="coerce")

for col in ["num_payments_made","num_late_payments","tenure_months"]:
    loans[col] = pd.to_numeric(loans[col], errors="coerce")

# --- 2c. Standardise text ---
for col in ["loan_purpose","loan_type","repayment_frequency","loan_status"]:
    loans[col] = loans[col].astype(str).str.strip().str.title()

# --- 2d. Cap outliers (loan_amount extreme values) ---
num_cols_l = ["loan_amount","interest_rate","emi_amount","outstanding_balance",
              "collateral_value","penalty_charges","num_late_payments"]
loans, out_rep_l = cap_outliers_iqr(loans, num_cols_l)

# --- 2e. Handle missing values ---
loans, impute_rep_l = impute_missing(loans)

# --- 2f. Validate referential integrity ---
valid_cust_ids   = set(cust["customer_id"])
invalid_refs     = ~loans["customer_id"].isin(valid_cust_ids)
loans.loc[invalid_refs, "customer_id"] = np.nan

# --- 2g. Derived columns ---
loans["loan_duration_years"] = loans["tenure_months"] / 12
loans["total_repayment"]     = (loans["emi_amount"] * loans["tenure_months"]).round(2)
loans["total_interest_paid"] = (loans["total_repayment"] - loans["loan_amount"]).round(2)
loans["default_flag"]        = loans["loan_status"].str.lower() == "defaulted"
loans["ltv_ratio"]           = (loans["loan_amount"] /
                                 loans["collateral_value"].replace(0, np.nan)).round(4)

# Loan risk bucket
def risk_bucket(row):
    if row["default_flag"]:
        return "High"
    if row["num_late_payments"] > 5:
        return "Medium"
    return "Low"

loans["risk_category"] = loans.apply(risk_bucket, axis=1)

loans.to_csv("data/cleaned/loans_clean.csv", index=False)

# ──────────────────────────────────────────────────────────
# 3. Cleaning Summary Report
# ──────────────────────────────────────────────────────────

os.makedirs("reports", exist_ok=True)
with open("reports/cleaning_report.txt", "w") as f:
    f.write(f"DATA CLEANING REPORT\nGenerated : {datetime.now()}\n")
    f.write("="*60 + "\n\n")

    f.write("CUSTOMERS\n")
    f.write(f"  Raw rows         : {raw_shape[0]}\n")
    f.write(f"  Cleaned rows     : {len(cust)}\n")
    f.write(f"  Columns          : {len(cust.columns)}\n")
    f.write(f"  Nulls remaining  : {cust.isna().sum().sum()}\n")
    f.write("  Imputed:\n")
    for k,v in impute_rep_c.items():
        f.write(f"    {k}: {v}\n")
    f.write("  Outliers capped:\n")
    for k,v in out_rep_c.items():
        f.write(f"    {k}: {v}\n")
    f.write("\nLOANS\n")
    f.write(f"  Cleaned rows     : {len(loans)}\n")
    f.write(f"  Columns          : {len(loans.columns)}\n")
    f.write(f"  Nulls remaining  : {loans.isna().sum().sum()}\n")
    f.write("  Imputed:\n")
    for k,v in impute_rep_l.items():
        f.write(f"    {k}: {v}\n")
    f.write("  Outliers capped:\n")
    for k,v in out_rep_l.items():
        f.write(f"    {k}: {v}\n")


