"""
run_pipeline.py  —  Master Runner
===================================
Runs all four stages of the capstone pipeline in order:
  1. generate_datasets.py     → create raw CSVs (1500 rows each)
  2. data_cleaning.py         → clean and validate
  3. data_transformation.py   → encode, scale, merge
  4. data_visualization.py    → 10 publication-quality graphs
"""

import subprocess
import sys
import time
import os

os.environ["PYTHONWARNINGS"] = "ignore"

steps = [
    ("Dataset Generation",      "generate_datasets.py"),
    ("Data Cleaning",           "data_cleaning.py"),
    ("Data Transformation",     "data_transformation.py"),
    ("Data Visualization",      "data_visualization.py"),
]

for title, script in steps:
    print(f"\n{'='*50}")
    print(f"  Running: {title}")
    print(f"{'='*50}")
    sys.stdout.flush()

    result = subprocess.run(
        [sys.executable, "-W", "ignore", script],
        capture_output=True, text=True
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        print(f"\n[ERROR] '{script}' failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)
    else:
        print(f"  [OK] {title} completed successfully.")

print(f"\n{'='*50}")
print("  All pipeline stages completed successfully!")
print(f"{'='*50}\n")
