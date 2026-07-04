# LoanVision — Capstone Data Dashboard & Pipeline

A self-contained data engineering and analytics pipeline that generates, cleans, transforms, and visualizes synthetic loan portfolio datasets. The project features a headless python execution flow integrated with a clean, functional web-based monitoring dashboard.

---

## Key Features

- **Scalable Data Pipeline**: Generates 10,000 synthetic customers and loans, cleanses missing entries, merges the relationships into a single master analytical dataset, and generates 10 distinct portfolio and risk charts.
- **Headless Plotting**: Matplotlib and Seaborn visualization outputs execute silently in the background using the non-interactive `Agg` backend to avoid disruptive graphical popups.
- **Web Dashboard**: A single-page, tabbed dashboard application:
  - **Overview & Stats**: High-level financial KPIs (Total Customers, Loans, Disbursed Volume, Interest Rates, Default Rates) and progress-bar breakdowns of credit risk and loan statuses.
  - **Visualizations**: A category-filterable grid showing all 10 generated charts with overlay modal zoom windows.
  - **Data Explorer**: An interactive table that previews the first 100 rows of the transformed master dataset, with custom client-side search text filtering and a CSV export downloader.
  - **Pipeline Logs**: Real-time streaming console that displays the stdout/stderr lines of the running pipeline subprocess directly on the web page.

---

## Directory Structure

```text
capstone_project/
├── app.py                  # Flask backend server & REST API
├── run_pipeline.py         # Subprocess runner orchestrating stages
├── generate_datasets.py    # Synthetic customer/loan generator (N=10,000)
├── data_cleaning.py        # Cleans nulls, outliers, and duplicates
├── data_transformation.py  # Joins datasets into master_merged.csv
├── data_visualization.py   # Renders headless matplotlib/seaborn charts
├── data/
│   ├── raw/                # Output destination for raw generation
│   ├── cleaned/            # Sanitized customer/loan tables
│   └── transformed/        # Contains joined 'master_merged.csv'
├── reports/
│   └── visualizations/     # Output destination for the 10 chart images
└── static/
    ├── index.html          # Dashboard single-page structural layout
    ├── app.css             # Simplified, professional dark dashboard theme
    └── app.js              # Client controller for API fetches and logging
```

---

## Quick Start & Setup

### 1. Install Dependencies
Ensure you have Python 3 installed. Install the necessary data science and web libraries:
```bash
pip install flask pandas matplotlib seaborn numpy
```

### 2. Start the Web Dashboard
Navigate to the directory and start the Flask web server:
```bash
python3 capstone_project/app.py
```
*Note: The server runs locally on **`http://localhost:8000`**.*

### 3. Open in Browser
Open **`http://localhost:8000`** in your browser.
- If you are running the dashboard for the first time, you will see a warning indicating that the datasets do not exist.
- Click the **"Run Pipeline"** button in the sidebar or run the pipeline manually in your terminal:
  ```bash
  python3 capstone_project/run_pipeline.py
  ```
- The dashboard will display progress bars, statistics, charts, and table rows once the execution finishes successfully.
