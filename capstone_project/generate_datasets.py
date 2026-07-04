"""
Dataset Generator
=================
Generates synthetic Customer (1500 rows) and Loan (1500 rows) datasets
and saves them to the 'data/raw/' directory.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

os.makedirs("data/raw", exist_ok=True)

# ─────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────

def random_dates(start, end, n):
    delta = (end - start).days
    return [start + timedelta(days=random.randint(0, delta)) for _ in range(n)]

N = 1500

# ─────────────────────────────────────────────
# 1. CUSTOMERS DATASET  (1 500 rows × 20 columns)
# ─────────────────────────────────────────────

first_names = [
    "Aditya","Rahul","Priya","Sneha","Rohan","Ananya","Vikram","Kavya",
    "Arjun","Nisha","Suresh","Pooja","Kiran","Meera","Deepak","Lakshmi",
    "Ravi","Sunita","Amit","Divya","Naveen","Swati","Harish","Rekha","Sachin",
]
last_names = [
    "Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Nair",
    "Iyer","Pillai","Rao","Reddy","Mehta","Shah","Mishra","Dubey",
    "Tiwari","Pandey","Malhotra","Bhat",
]
cities       = ["Bengaluru","Mumbai","Delhi","Hyderabad","Chennai","Pune","Kolkata","Ahmedabad","Jaipur","Lucknow"]
states       = ["Karnataka","Maharashtra","Delhi","Telangana","Tamil Nadu","Maharashtra","West Bengal","Gujarat","Rajasthan","Uttar Pradesh"]
occupations  = ["Engineer","Doctor","Teacher","Businessman","Lawyer","Accountant","Manager","Consultant","Professor","Analyst","Designer","Nurse"]
education    = ["High School","Bachelor's","Master's","PhD","Diploma"]
marital_stat = ["Single","Married","Divorced","Widowed"]

# Inject ~5% missing values helper
def inject_nulls(series, frac=0.05):
    s = series.copy().astype(object)
    idx = s.sample(frac=frac, random_state=99).index
    s[idx] = np.nan
    return s

customer_ids = [f"CUST{str(i).zfill(5)}" for i in range(1, N + 1)]
ages         = np.random.randint(21, 70, N)
incomes      = np.round(np.random.lognormal(mean=11.5, sigma=0.6, size=N), 2)  # ₹ annual
credit_scores = np.random.randint(300, 900, N)

city_col  = [random.choice(cities) for _ in range(N)]
state_col = [states[cities.index(c)] for c in city_col]

customers_raw = pd.DataFrame({
    "customer_id"         : customer_ids,
    "first_name"          : [random.choice(first_names) for _ in range(N)],
    "last_name"           : [random.choice(last_names)  for _ in range(N)],
    "age"                 : ages,
    "gender"              : np.random.choice(["Male","Female","Other"], N, p=[0.50,0.48,0.02]),
    "marital_status"      : np.random.choice(marital_stat, N, p=[0.35,0.50,0.10,0.05]),
    "education_level"     : np.random.choice(education, N, p=[0.15,0.40,0.30,0.10,0.05]),
    "occupation"          : [random.choice(occupations) for _ in range(N)],
    "annual_income"       : incomes,
    "monthly_expenses"    : np.round(incomes / np.random.uniform(4, 8, N), 2),
    "credit_score"        : credit_scores,
    "num_dependents"      : np.random.randint(0, 6, N),
    "years_employed"      : np.random.randint(0, 40, N),
    "city"                : city_col,
    "state"               : state_col,
    "phone_number"        : [f"9{random.randint(100000000,999999999)}" for _ in range(N)],
    "email"               : [f"{fn.lower()}.{ln.lower()}{random.randint(1,999)}@example.com"
                              for fn,ln in zip([random.choice(first_names) for _ in range(N)],
                                               [random.choice(last_names)  for _ in range(N)])],
    "has_existing_loan"   : np.random.choice([True, False], N, p=[0.35,0.65]),
    "num_credit_cards"    : np.random.randint(0, 8, N),
    "registration_date"   : random_dates(datetime(2015,1,1), datetime(2024,12,31), N),
})

# Introduce realistic noise
customers_raw["annual_income"]  = inject_nulls(customers_raw["annual_income"])
customers_raw["credit_score"]   = inject_nulls(customers_raw["credit_score"])
customers_raw["occupation"]     = inject_nulls(customers_raw["occupation"])
customers_raw["years_employed"] = inject_nulls(customers_raw["years_employed"])

# Duplicate ~2% rows
dup_idx = customers_raw.sample(frac=0.02, random_state=7).index
customers_raw = pd.concat([customers_raw, customers_raw.loc[dup_idx]], ignore_index=True)

customers_raw.to_csv("data/raw/customers_raw.csv", index=False)


# ─────────────────────────────────────────────
# 2. LOANS DATASET  (1 500 rows × 20 columns)
# ─────────────────────────────────────────────

loan_purposes = ["Home","Education","Personal","Vehicle","Business","Medical","Travel","Wedding"]
loan_types    = ["Secured","Unsecured"]
repay_freq    = ["Monthly","Quarterly","Bi-Annual"]
loan_status   = ["Active","Closed","Defaulted","Under Review"]

loan_ids  = [f"LOAN{str(i).zfill(6)}" for i in range(1, N + 1)]
cust_refs = np.random.choice(customer_ids, N, replace=True)   # FK → customers

loan_amounts   = np.round(np.random.lognormal(mean=12.5, sigma=0.8, size=N), 2)
interest_rates = np.round(np.random.uniform(6.5, 22.0, N), 2)
tenure_months  = np.random.choice([12, 24, 36, 48, 60, 84, 120, 180, 240], N)
disbursement   = random_dates(datetime(2018,1,1), datetime(2024,6,30), N)
maturity       = [d + timedelta(days=int(t)*30) for d,t in zip(disbursement, tenure_months)]

# EMI = P * r*(1+r)^n / ((1+r)^n - 1)
monthly_rate = interest_rates / (12 * 100)
emi          = np.where(
    monthly_rate == 0,
    loan_amounts / tenure_months,
    loan_amounts * monthly_rate * (1 + monthly_rate)**tenure_months /
    ((1 + monthly_rate)**tenure_months - 1)
)

loans_raw = pd.DataFrame({
    "loan_id"             : loan_ids,
    "customer_id"         : cust_refs,
    "loan_purpose"        : np.random.choice(loan_purposes, N, p=[0.20,0.15,0.25,0.10,0.12,0.08,0.05,0.05]),
    "loan_type"           : np.random.choice(loan_types, N, p=[0.45,0.55]),
    "loan_amount"         : loan_amounts,
    "interest_rate"       : interest_rates,
    "tenure_months"       : tenure_months,
    "emi_amount"          : np.round(emi, 2),
    "disbursement_date"   : disbursement,
    "maturity_date"       : maturity,
    "repayment_frequency" : np.random.choice(repay_freq, N, p=[0.75,0.15,0.10]),
    "loan_status"         : np.random.choice(loan_status, N, p=[0.55,0.30,0.10,0.05]),
    "num_payments_made"   : np.random.randint(0, 240, N),
    "outstanding_balance" : np.round(loan_amounts * np.random.uniform(0, 1, N), 2),
    "collateral_value"    : np.round(loan_amounts * np.random.uniform(0, 2, N), 2),
    "num_late_payments"   : np.random.randint(0, 20, N),
    "penalty_charges"     : np.round(np.random.uniform(0, 50000, N), 2),
    "loan_officer_id"     : [f"LO{random.randint(100,199)}" for _ in range(N)],
    "branch_code"         : [f"BR{random.randint(10,50)}" for _ in range(N)],
    "insurance_taken"     : np.random.choice([True, False], N, p=[0.40,0.60]),
})

# Inject nulls
loans_raw["collateral_value"]   = inject_nulls(loans_raw["collateral_value"])
loans_raw["penalty_charges"]    = inject_nulls(loans_raw["penalty_charges"])
loans_raw["num_late_payments"]  = inject_nulls(loans_raw["num_late_payments"])
loans_raw["interest_rate"]      = inject_nulls(loans_raw["interest_rate"])

# Add some outliers
loans_raw.loc[loans_raw.sample(5, random_state=1).index, "loan_amount"] = 9_999_999_999.0

# Duplicate ~2%
dup_idx2 = loans_raw.sample(frac=0.02, random_state=11).index
loans_raw = pd.concat([loans_raw, loans_raw.loc[dup_idx2]], ignore_index=True)

loans_raw.to_csv("data/raw/loans_raw.csv", index=False)
