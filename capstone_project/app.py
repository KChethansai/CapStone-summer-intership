import os
import sys
import subprocess
import threading
import pandas as pd
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Thread safety variables for tracking the data pipeline running status
pipeline_status = {
    "status": "idle",  # "idle", "running", "success", "error"
    "logs": []
}
pipeline_lock = threading.Lock()

CHARTS = [
    {
        "id": 1,
        "filename": "01_credit_score_distribution.png",
        "title": "Credit Score Distribution",
        "category": "Customer Credit",
        "description": "KDE and Histogram showing the distribution of customer credit scores segmented by rating tiers (Poor, Fair, Good, Excellent)."
    },
    {
        "id": 2,
        "filename": "02_income_by_education.png",
        "title": "Annual Income by Education Level",
        "category": "Customer Credit",
        "description": "Box plot demonstrating annual income distributions across different educational attainment levels."
    },
    {
        "id": 3,
        "filename": "03_loan_amount_by_purpose.png",
        "title": "Loan Amount by Purpose",
        "category": "Loan Portfolio",
        "description": "Violin plot highlighting loan amount distributions grouped by the intended purpose of the loan."
    },
    {
        "id": 4,
        "filename": "04_loan_status_donut.png",
        "title": "Loan Status Breakdown",
        "category": "Loan Portfolio",
        "description": "Donut chart detailing the proportion of active, closed, defaulted, and under-review loans."
    },
    {
        "id": 5,
        "filename": "05_default_rate_by_purpose.png",
        "title": "Default Rate by Loan Purpose",
        "category": "Loan Portfolio",
        "description": "Grouped bar chart showing default percentage ratios across different loan purposes."
    },
    {
        "id": 6,
        "filename": "06_credit_score_vs_loan_amount.png",
        "title": "Credit Score vs Loan Amount",
        "category": "Customer Credit",
        "description": "Scatter plot showing relationship between credit score and loan amount, colored by risk category, with a trend regression line."
    },
    {
        "id": 7,
        "filename": "07_correlation_heatmap.png",
        "title": "Feature Correlation Heatmap",
        "category": "Loan Portfolio",
        "description": "Correlation matrix heatmap displaying relationships between customer characteristics and loan attributes."
    },
    {
        "id": 8,
        "filename": "08_emi_to_income_by_risk.png",
        "title": "EMI-to-Income Ratio by Risk",
        "category": "Loan Portfolio",
        "description": "Bar chart with standard error bars displaying the average monthly debt-to-income ratio across credit risk tiers."
    },
    {
        "id": 9,
        "filename": "09_monthly_disbursements.png",
        "title": "Monthly Disbursements Over Time",
        "category": "Time Trends",
        "description": "Line chart showing the monthly progression of loans disbursed (volume) and aggregate loan amounts (value)."
    },
    {
        "id": 10,
        "filename": "10_income_tier_bubble.png",
        "title": "Income Tier vs Loan Amount",
        "category": "Time Trends",
        "description": "Bubble chart plotting average annual income against average loan amount by income tier. Bubble size represents loan count; color maps to default rate."
    }
]

# Root route serves index.html
@app.route('/')
def index():
    # If static/index.html doesn't exist, return a simple welcome string or error
    if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return "Frontend files are currently building. Please refresh in a moment."
    return send_from_directory(app.static_folder, 'index.html')

# Endpoint to serve generated visualizations
@app.route('/reports/visualizations/<path:filename>')
def serve_visualization(filename):
    vis_dir = os.path.join(os.getcwd(), 'reports', 'visualizations')
    return send_from_directory(vis_dir, filename)

# Endpoint to fetch high-level portfolio statistics
@app.route('/api/stats')
def get_stats():
    master_path = 'data/transformed/master_merged.csv'
    loans_path = 'data/cleaned/loans_clean.csv'
    cust_path = 'data/cleaned/customers_clean.csv'
    
    if not os.path.exists(master_path) or not os.path.exists(loans_path) or not os.path.exists(cust_path):
        return jsonify({
            "initialized": False,
            "message": "Data pipeline has not been run yet, or files are missing. Please run the pipeline to generate statistics."
        })
        
    try:
        master = pd.read_csv(master_path)
        loans = pd.read_csv(loans_path)
        cust = pd.read_csv(cust_path)
        
        # Calculate key metrics
        total_customers = int(cust['customer_id'].nunique())
        total_loans = int(loans['loan_id'].nunique())
        total_disbursed = float(loans['loan_amount'].sum())
        avg_interest_rate = float(loans['interest_rate'].mean())
        avg_credit_score = float(cust['credit_score'].mean())
        
        # Default rate calculations
        defaulted_count = int((loans['loan_status'].str.lower() == 'defaulted').sum())
        default_rate = (defaulted_count / total_loans) * 100 if total_loans > 0 else 0.0
        
        # Categorical distribution breakdowns
        risk_counts = loans['risk_category'].value_counts().to_dict()
        status_counts = loans['loan_status'].value_counts().to_dict()
        purpose_counts = loans['loan_purpose'].value_counts().to_dict()
        
        return jsonify({
            "initialized": True,
            "total_customers": total_customers,
            "total_loans": total_loans,
            "total_disbursed": total_disbursed,
            "avg_interest_rate": round(avg_interest_rate, 2),
            "avg_credit_score": round(avg_credit_score, 1),
            "default_rate": round(default_rate, 2),
            "risk_counts": risk_counts,
            "status_counts": status_counts,
            "purpose_counts": purpose_counts
        })
    except Exception as e:
        return jsonify({
            "initialized": False,
            "message": f"Error loading statistics: {str(e)}"
        }), 500

# Endpoint to fetch metadata about the charts
@app.route('/api/charts')
def get_charts():
    # Check if visualizations exist on disk
    vis_dir = os.path.join(os.getcwd(), 'reports', 'visualizations')
    available_charts = []
    
    for chart in CHARTS:
        full_path = os.path.join(vis_dir, chart['filename'])
        chart_info = chart.copy()
        chart_info['exists'] = os.path.exists(full_path)
        # Add cache buster timestamp if it exists to prevent browser image caching issues
        if chart_info['exists']:
            mtime = int(os.path.getmtime(full_path))
            chart_info['url'] = f"/reports/visualizations/{chart['filename']}?v={mtime}"
        else:
            chart_info['url'] = ""
        available_charts.append(chart_info)
        
    return jsonify(available_charts)

# Endpoint to fetch a data sample (first 100 rows)
@app.route('/api/data-preview')
def get_data_preview():
    master_path = 'data/transformed/master_merged.csv'
    if not os.path.exists(master_path):
        return jsonify({"initialized": False, "data": []})
        
    try:
        # Read first 100 rows
        df = pd.read_csv(master_path, nrows=100)
        # Handle nan values for JSON compliance
        df = df.fillna("")
        data_list = df.to_dict(orient='records')
        columns = [{"field": col, "title": col.replace('_', ' ').title()} for col in df.columns]
        return jsonify({
            "initialized": True,
            "columns": columns,
            "data": data_list
        })
    except Exception as e:
        return jsonify({"initialized": False, "error": str(e)}), 500

# Endpoint to download the full merged dataset as CSV
@app.route('/api/download-master')
def download_master():
    master_path = 'data/transformed/master_merged.csv'
    if not os.path.exists(master_path):
        return "File not found. Please run the pipeline first.", 404
    return send_from_directory('data/transformed', 'master_merged.csv', as_attachment=True)

# Asynchronous pipeline runner helper
def run_pipeline_async():
    global pipeline_status
    
    with pipeline_lock:
        pipeline_status["status"] = "running"
        pipeline_status["logs"] = ["[START] Triggering pipeline execution...\n"]
        
    try:
        # Run run_pipeline.py using Python interpreter
        # stdout and stderr are redirected to the same stream
        process = subprocess.Popen(
            [sys.executable, "run_pipeline.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1, # Line buffering
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Read process output line by line in real time
        for line in iter(process.stdout.readline, ''):
            with pipeline_lock:
                pipeline_status["logs"].append(line)
                
        process.stdout.close()
        return_code = process.wait()
        
        with pipeline_lock:
            if return_code == 0:
                pipeline_status["status"] = "success"
                pipeline_status["logs"].append("\n[SUCCESS] Data pipeline execution finished successfully!\n")
            else:
                pipeline_status["status"] = "error"
                pipeline_status["logs"].append(f"\n[ERROR] Data pipeline exited with code {return_code}\n")
                
    except Exception as e:
        with pipeline_lock:
            pipeline_status["status"] = "error"
            pipeline_status["logs"].append(f"\n[EXCEPTION] Failed running pipeline: {str(e)}\n")

# Endpoint to trigger data pipeline execution
@app.route('/api/run-pipeline', methods=['POST'])
def trigger_pipeline():
    global pipeline_status
    
    with pipeline_lock:
        if pipeline_status["status"] == "running":
            return jsonify({"status": "already_running", "message": "Pipeline is already running."}), 409
            
    # Run the pipeline in a separate daemon thread
    thread = threading.Thread(target=run_pipeline_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "message": "Pipeline started in background."})

# Endpoint to poll status of the pipeline
@app.route('/api/pipeline-status')
def get_pipeline_status():
    with pipeline_lock:
        return jsonify({
            "status": pipeline_status["status"],
            "log_count": len(pipeline_status["logs"])
        })

# Endpoint to retrieve pipeline logs
@app.route('/api/pipeline-logs')
def get_pipeline_logs():
    with pipeline_lock:
        return jsonify({
            "status": pipeline_status["status"],
            "logs": "".join(pipeline_status["logs"])
        })

if __name__ == '__main__':
    # Running on local host 0.0.0.0, port 8000
    app.run(host='0.0.0.0', port=8000, debug=True)
