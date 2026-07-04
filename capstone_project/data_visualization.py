"""
Data Visualization  —  10 Professional Graphs
===============================================
Reads transformed/merged datasets and produces 10 publication-ready plots
saved to reports/visualizations/.

Graphs:
  1.  Credit Score Distribution (KDE + Histogram)
  2.  Annual Income by Education Level (Box Plot)
  3.  Loan Amount Distribution by Purpose (Violin Plot)
  4.  Loan Status Breakdown (Donut Chart)
  5.  Default Rate by Loan Purpose (Grouped Bar)
  6.  Credit Score vs Loan Amount (Scatter + Regression)
  7.  Heatmap — Feature Correlation Matrix
  8.  EMI-to-Income Ratio by Risk Category (Stacked Bar)
  9.  Monthly Loan Disbursements Over Time (Line Chart)
  10. Customer Income Tier vs Loan Amount (Bubble Chart)
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")
os.makedirs("reports/visualizations", exist_ok=True)

# ──────────────────────────────────────────────────────────
# Theme / Palette
# ──────────────────────────────────────────────────────────

PALETTE    = ["#6C63FF","#FF6584","#43B89C","#FFC107","#E74C3C","#3498DB","#9B59B6","#1ABC9C"]
BG_COLOR   = "#0F0F1A"
PANEL_COLOR= "#1A1A2E"
TEXT_COLOR = "#E0E0E0"
GRID_COLOR = "#2A2A40"

plt.rcParams.update({
    "figure.facecolor"  : BG_COLOR,
    "axes.facecolor"    : PANEL_COLOR,
    "axes.edgecolor"    : GRID_COLOR,
    "axes.labelcolor"   : TEXT_COLOR,
    "xtick.color"       : TEXT_COLOR,
    "ytick.color"       : TEXT_COLOR,
    "text.color"        : TEXT_COLOR,
    "grid.color"        : GRID_COLOR,
    "grid.linestyle"    : "--",
    "grid.alpha"        : 0.5,
    "legend.facecolor"  : PANEL_COLOR,
    "legend.edgecolor"  : GRID_COLOR,
    "font.family"       : "DejaVu Sans",
    "font.size"         : 11,
    "axes.titlesize"    : 14,
    "axes.titleweight"  : "bold",
    "axes.titlepad"     : 12,
})

def save_fig(fig, name):
    path = f"reports/visualizations/{name}"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    # plt.show()
    plt.close(fig)
    print(f"  Saved: {path}")

# ──────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────

cust   = pd.read_csv("data/cleaned/customers_clean.csv")
loans  = pd.read_csv("data/cleaned/loans_clean.csv",
                     parse_dates=["disbursement_date","maturity_date"])
master = pd.read_csv("data/transformed/master_merged.csv")



# ══════════════════════════════════════════════════════════
# Graph 1: Credit Score Distribution (KDE + Histogram)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 5))
data = cust["credit_score"].dropna()

ax.hist(data, bins=40, color=PALETTE[0], alpha=0.4, density=True, label="Histogram")
kde_x = np.linspace(data.min(), data.max(), 500)
kde   = stats.gaussian_kde(data)
ax.plot(kde_x, kde(kde_x), color=PALETTE[1], lw=2.5, label="KDE")

# Shade credit tiers
for lo, hi, color, label in [
    (300, 500, "#E74C3C","Poor"),
    (500, 650, "#FFC107","Fair"),
    (650, 750, "#3498DB","Good"),
    (750, 900, "#1ABC9C","Excellent"),
]:
    ax.axvspan(lo, hi, alpha=0.08, color=color, label=label)

ax.set_title("Credit Score Distribution of Customers")
ax.set_xlabel("Credit Score")
ax.set_ylabel("Density")
ax.legend(fontsize=9)
ax.grid(True, axis="y")

fig.text(0.5, -0.02, f"n = {len(data):,}  |  Mean = {data.mean():.0f}  |  Median = {data.median():.0f}",
         ha="center", color=TEXT_COLOR, fontsize=9)
save_fig(fig, "01_credit_score_distribution.png")

# ══════════════════════════════════════════════════════════
# Graph 2: Annual Income by Education Level (Box Plot)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(11, 6))
order = ["High School","Diploma","Bachelor'S","Master'S","Phd"]
order = [o for o in order if o in cust["education_level"].unique()]

bp = sns.boxplot(
    data=cust, x="education_level", y="annual_income",
    order=order, palette=PALETTE[:len(order)], ax=ax,
    flierprops=dict(marker="o", color=PALETTE[1], alpha=0.5, markersize=4),
    medianprops=dict(color="white", lw=2),
)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
ax.set_title("Annual Income Distribution by Education Level")
ax.set_xlabel("Education Level")
ax.set_ylabel("Annual Income (₹ Lakhs)")
ax.grid(True, axis="y")
save_fig(fig, "02_income_by_education.png")

# ══════════════════════════════════════════════════════════
# Graph 3: Loan Amount Distribution by Purpose (Violin)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(13, 6))
order3 = loans.groupby("loan_purpose")["loan_amount"].median().sort_values(ascending=False).index.tolist()

sns.violinplot(
    data=loans, x="loan_purpose", y="loan_amount",
    order=order3, palette=PALETTE, ax=ax,
    inner="quartile", cut=0,
)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))
ax.set_title("Loan Amount Distribution by Loan Purpose")
ax.set_xlabel("Loan Purpose")
ax.set_ylabel("Loan Amount (₹ Lakhs)")
ax.grid(True, axis="y")
save_fig(fig, "03_loan_amount_by_purpose.png")

# ══════════════════════════════════════════════════════════
# Graph 4: Loan Status Breakdown (Donut Chart)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(8, 7))
status_counts = loans["loan_status"].value_counts()
colors = [PALETTE[i] for i in range(len(status_counts))]

wedges, texts, autotexts = ax.pie(
    status_counts,
    labels=status_counts.index,
    colors=colors,
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.80,
    wedgeprops=dict(width=0.55, edgecolor=BG_COLOR, linewidth=2),
)
for t in texts:
    t.set_color(TEXT_COLOR); t.set_fontsize(11)
for at in autotexts:
    at.set_color("white"); at.set_fontweight("bold"); at.set_fontsize(10)

ax.text(0, 0, f"Total\n{len(loans):,}", ha="center", va="center",
        fontsize=13, color=TEXT_COLOR, fontweight="bold")
ax.set_title("Loan Status Breakdown")
save_fig(fig, "04_loan_status_donut.png")

# ══════════════════════════════════════════════════════════
# Graph 5: Default Rate by Loan Purpose (Grouped Bar)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 6))
def_rate = (
    loans.groupby("loan_purpose")["loan_status"]
    .apply(lambda s: (s.str.lower() == "defaulted").mean() * 100)
    .reset_index(name="default_rate")
    .sort_values("default_rate", ascending=False)
)

bars = ax.bar(def_rate["loan_purpose"], def_rate["default_rate"],
              color=PALETTE[:len(def_rate)], edgecolor=BG_COLOR, linewidth=1.5, width=0.6)
ax.bar_label(bars, fmt="%.1f%%", padding=4, color=TEXT_COLOR, fontsize=10)
ax.set_ylim(0, def_rate["default_rate"].max() * 1.3)
ax.set_title("Default Rate by Loan Purpose")
ax.set_xlabel("Loan Purpose")
ax.set_ylabel("Default Rate (%)")
ax.grid(True, axis="y")
save_fig(fig, "05_default_rate_by_purpose.png")

# ══════════════════════════════════════════════════════════
# Graph 6: Credit Score vs Loan Amount (Scatter + Regression)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 6))
sample = master.dropna(subset=["credit_score","loan_amount"]).sample(
    min(800, len(master)), random_state=42
)
risk_colors = {"Low": PALETTE[2], "Medium": PALETTE[3], "High": PALETTE[4]}
for risk, grp in sample.groupby("risk_category"):
    ax.scatter(grp["credit_score"], grp["loan_amount"] / 1e5,
               color=risk_colors.get(str(risk), PALETTE[0]), alpha=0.6,
               s=35, label=str(risk), edgecolors="none")

# Regression line
m, b, *_ = stats.linregress(sample["credit_score"].fillna(0), sample["loan_amount"].fillna(0) / 1e5)
xs = np.linspace(sample["credit_score"].min(), sample["credit_score"].max(), 300)
ax.plot(xs, m * xs + b, color="white", lw=2, linestyle="--", label="Trend")

ax.set_title("Credit Score vs Loan Amount by Risk Category")
ax.set_xlabel("Credit Score")
ax.set_ylabel("Loan Amount (₹ Lakhs)")
ax.legend(title="Risk", framealpha=0.3)
ax.grid(True)
save_fig(fig, "06_credit_score_vs_loan_amount.png")

# ══════════════════════════════════════════════════════════
# Graph 7: Heatmap — Feature Correlation Matrix
# ══════════════════════════════════════════════════════════

corr_cols = [
    "loan_amount","interest_rate","tenure_months","emi_amount",
    "outstanding_balance","num_late_payments","credit_score",
    "annual_income","num_dependents","years_employed",
]
corr_data = master[corr_cols].dropna()
corr_matrix = corr_data.corr()

fig, ax = plt.subplots(figsize=(12, 9))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt=".2f",
    cmap="coolwarm", center=0, vmin=-1, vmax=1,
    linewidths=0.5, linecolor=BG_COLOR,
    ax=ax, cbar_kws={"shrink": 0.8},
    annot_kws={"size": 9},
)
ax.set_title("Feature Correlation Heatmap (Loan × Customer)", pad=15)
ax.tick_params(axis="x", rotation=35)
save_fig(fig, "07_correlation_heatmap.png")

# ══════════════════════════════════════════════════════════
# Graph 8: EMI-to-Income Ratio by Risk Category (Bar + Error)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(9, 5))
master["emi_to_income_ratio"] = (
    master["emi_amount"] / (master["annual_income"] / 12)
).replace([np.inf, -np.inf], np.nan)

eti = (
    master.groupby("risk_category")["emi_to_income_ratio"]
    .agg(["mean","std","count"]).reset_index()
)
eti["se"] = eti["std"] / np.sqrt(eti["count"])
eti = eti.sort_values("mean", ascending=False)

colors8 = {"High": PALETTE[4], "Medium": PALETTE[3], "Low": PALETTE[2]}
bars8 = ax.bar(eti["risk_category"], eti["mean"],
               color=[colors8.get(r, PALETTE[0]) for r in eti["risk_category"]],
               yerr=eti["se"], capsize=6, error_kw=dict(ecolor="white", lw=1.5),
               edgecolor=BG_COLOR, width=0.5)
ax.bar_label(bars8, fmt="%.3f", padding=8, color=TEXT_COLOR, fontsize=10)
ax.set_title("Average EMI-to-Income Ratio by Risk Category")
ax.set_xlabel("Risk Category")
ax.set_ylabel("EMI / Monthly Income")
ax.grid(True, axis="y")
save_fig(fig, "08_emi_to_income_by_risk.png")

# ══════════════════════════════════════════════════════════
# Graph 9: Monthly Loan Disbursements Over Time (Line Chart)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(13, 5))
loans["ym"] = loans["disbursement_date"].dt.to_period("M")
monthly = loans.groupby("ym").agg(
    count=("loan_id","count"),
    total_amt=("loan_amount","sum")
).reset_index()
monthly["ym_dt"] = monthly["ym"].dt.to_timestamp()
monthly = monthly.sort_values("ym_dt")

ax.fill_between(monthly["ym_dt"], monthly["count"], alpha=0.25, color=PALETTE[0])
ax.plot(monthly["ym_dt"], monthly["count"], color=PALETTE[0], lw=2, marker="o",
        markersize=4, label="# Loans Disbursed")

ax2 = ax.twinx()
ax2.plot(monthly["ym_dt"], monthly["total_amt"] / 1e7, color=PALETTE[1],
         lw=2, linestyle="--", marker="s", markersize=3, label="Total Amt (₹ Cr)")
ax2.set_ylabel("Total Amount (₹ Crores)", color=PALETTE[1])
ax2.tick_params(axis="y", colors=PALETTE[1])
ax2.spines["right"].set_color(PALETTE[1])

ax.set_title("Monthly Loan Disbursements Over Time")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Loans", color=PALETTE[0])
ax.tick_params(axis="y", colors=PALETTE[0])

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
ax.grid(True, axis="y")
fig.autofmt_xdate(rotation=30)
save_fig(fig, "09_monthly_disbursements.png")

# ══════════════════════════════════════════════════════════
# Graph 10: Income Tier vs Loan Amount (Bubble Chart)
# ══════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 7))
bubble = (
    master.groupby("income_tier", observed=True)
    .agg(
        avg_loan   =("loan_amount","mean"),
        avg_income =("annual_income","mean"),
        count      =("loan_id","count"),
        default_rate=("default_flag","mean"),
    ).reset_index()
)
bubble = bubble.dropna(subset=["avg_loan","avg_income"])

sc = ax.scatter(
    bubble["avg_income"] / 1e5,
    bubble["avg_loan"] / 1e5,
    s=bubble["count"] * 2,
    c=bubble["default_rate"] * 100,
    cmap="RdYlGn_r",
    alpha=0.85,
    edgecolors="white",
    linewidths=1.5,
)
cbar = fig.colorbar(sc, ax=ax, pad=0.01)
cbar.set_label("Default Rate (%)", color=TEXT_COLOR)
cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

for _, row in bubble.iterrows():
    ax.annotate(
        str(row["income_tier"]),
        (row["avg_income"] / 1e5, row["avg_loan"] / 1e5),
        textcoords="offset points", xytext=(8, 4),
        color=TEXT_COLOR, fontsize=10, fontweight="bold",
    )

ax.set_title("Income Tier vs Average Loan Amount\n(Bubble size = # loans | Color = Default Rate)")
ax.set_xlabel("Average Annual Income (₹ Lakhs)")
ax.set_ylabel("Average Loan Amount (₹ Lakhs)")
ax.grid(True)
save_fig(fig, "10_income_tier_bubble.png")

print("\nAll 10 charts saved to: reports/visualizations/")
