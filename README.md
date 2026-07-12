# 🏎️ Formula One World Championship Data Analytics Dashboard

A complete end-to-end data analytics project developed as part of the **Google Cloud Data Analytics Virtual Internship**. The project demonstrates data cleaning, preprocessing, relational data integration, feature engineering, and interactive dashboard creation using historical Formula One World Championship data.

---

## Key Features

- **End-to-End Data Analytics Pipeline**: Loads multiple relational Formula One datasets, performs cleaning, preprocessing, and merges them into a single analytics-ready dataset.
- **Data Cleaning & Preprocessing**:
  - Handles missing values (`\N` → `NaN`)
  - Removes duplicate records
  - Corrects data types
  - Standardizes dataset for analysis
- **Feature Engineering**:
  - Driver Full Name
  - Constructor Name
  - Winner Indicator
  - Podium Finish
  - Race Completion Status
  - Decade Classification
  - Position Category
  - Points Category
- **Interactive Dashboard** (Google Looker Studio):
  - Dashboard KPIs
    - Total Drivers
    - Total Constructors
    - Total Race Results
    - Total Seasons
    - Average Points
  - Interactive Filters
    - Season
    - Driver
    - Constructor
    - Country
    - Race Status
  - Visualizations
    - Top Drivers by Championship Points
    - Constructor Performance
    - Championship Points Trend
    - Race Finish Status Distribution
    - Countries Hosting Formula One Races
    - Grid Position vs Finish Position
    - Interactive Race Results Table

---

## Project Structure

```text
.
├── data/
│   ├── circuits.csv
│   ├── constructor_results.csv
│   ├── constructor_standings.csv
│   ├── constructors.csv
│   ├── driver_standings.csv
│   ├── drivers.csv
│   ├── lap_times.csv
│   ├── pit_stops.csv
│   ├── qualifying.csv
│   ├── races.csv
│   ├── results.csv
│   ├── seasons.csv
│   ├── sprint_results.csv
│   └── status.csv
│
├── Formula1_Data_Cleaning_Preprocessing.ipynb
├── cleaned_f1_dataset.csv
├── README.md
└── Dashboard/
    ├── dashboard.png
    └── dashboard.pdf
```

---

## Dataset

This project uses the **Formula One World Championship Dataset (1950–2020)** from Kaggle.

The dataset contains historical information including:

- Drivers
- Constructors
- Circuits
- Race Results
- Driver Standings
- Constructor Standings
- Qualifying Results
- Sprint Results
- Lap Times
- Pit Stops
- Seasons

---

## Data Analytics Workflow

### 1. Data Exploration

- Dataset inspection
- Data types analysis
- Missing value identification
- Duplicate detection
- Statistical summaries

### 2. Data Cleaning

- Handling missing values
- Removing duplicates
- Converting data types
- Standardizing data

### 3. Data Integration

Multiple relational datasets were merged using:

- Driver ID
- Constructor ID
- Race ID
- Circuit ID
- Status ID

to create a unified analytical dataset.

### 4. Feature Engineering

Additional analytical columns were generated:

- Driver
- Constructor
- Winner
- Podium
- Finished
- Decade
- Position Category
- Points Category

### 5. Dashboard Development

The cleaned dataset was imported into **Google Looker Studio** to build an interactive analytics dashboard.

---

## Dashboard Overview

The dashboard provides insights into Formula One performance through:

### KPIs

- Total Drivers
- Total Constructors
- Total Race Results
- Total Seasons
- Average Points

### Visualizations

- Top Drivers by Total Championship Points
- Constructor Performance
- Championship Points by Season
- Race Finish Status Distribution
- Number of Race Results by Country
- Grid Position vs Finishing Position
- Interactive Race Results Table

### Interactive Filters

- Season
- Driver
- Constructor
- Country
- Race Status

---

## Technologies Used

- Python
- Pandas
- NumPy
- Jupyter Notebook
- Google Looker Studio
- Google Sheets
- Git
- GitHub

---

## Installation

Clone the repository

```bash
git clone https://github.com/your-username/formula1-data-analytics.git

cd formula1-data-analytics
```

Install dependencies

```bash
pip install pandas numpy matplotlib
```

Launch Jupyter Notebook

```bash
jupyter notebook
```

Open

```text
Formula1_Data_Cleaning_Preprocessing.ipynb
```

Run all cells to generate

```text
cleaned_f1_dataset.csv
```

Upload the generated CSV to **Google Sheets** (or BigQuery) and connect it to **Google Looker Studio** to build the dashboard.

---

## Learning Outcomes

This project demonstrates practical experience in:

- Data Cleaning
- Data Preprocessing
- Data Integration
- Exploratory Data Analysis (EDA)
- Feature Engineering
- Dashboard Development
- Data Visualization
- Business Insight Generation

---

## Dashboard Preview

> Add your Looker Studio dashboard screenshot here.

Example:

```text
Dashboard/dashboard.png
```

---

## Future Enhancements

- Live Formula One API integration
- BigQuery data warehouse support
- Predictive analytics using Machine Learning
- Driver performance forecasting
- Interactive season comparisons
- Automated ETL pipeline
- Real-time dashboard updates

---
