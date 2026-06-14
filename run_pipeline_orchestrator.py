import os
import subprocess
import time
from datetime import datetime
import schedule

# Setup absolute pipeline paths
PROJECT_ROOT = r"C:\Users\allen\global-ecommerce-pipeline"
MOCK_DATA_SCRIPT = os.path.join(PROJECT_ROOT, "snowpark_python", "generate_mock_data.py")
DBT_PROJECT_DIR = os.path.join(PROJECT_ROOT, "dbt_ecommerce")

# Pin down virtual environment engines explicitly
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "Scripts", "python.exe")
VENV_DBT = os.path.join(PROJECT_ROOT, "venv", "Scripts", "dbt.exe")

def execute_ecommerce_pipeline():
    """Master orchestration job executing step-by-step processing tasks."""
    print(f"\n=======================================================")
    print(f"🔄 PIPELINE INITIALIZED AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=======================================================")
    
    # ─── TASK 1: RUN PYTHON MOCK INGESTION STREAM ───
    print("▶️ Task 1/2: Generating user clickstreams and pushing to PostgreSQL...")
    ingest_proc = subprocess.run([VENV_PYTHON, MOCK_DATA_SCRIPT], capture_output=True, text=True)
    
    if ingest_proc.returncode != 0:
        print(f"❌ CRITICAL TASK 1 FAILURE:\n{ingest_proc.stderr}")
        return
    print(ingest_proc.stdout.strip())
    
    # ─── TASK 2: RUN DBT TRANSFORMATION ENGINE ───
    print("\n▶️ Task 2/2: Launching dbt modeling compilation and structural pricing calculations...")
    dbt_proc = subprocess.run([VENV_DBT, "run"], cwd=DBT_PROJECT_DIR, capture_output=True, text=True)
    
    if dbt_proc.returncode != 0:
        print(f"❌ CRITICAL TASK 2 FAILURE:\n{dbt_proc.stderr}")
        return
    print("✅ dbt compilation layer completed successfully!")
    print(f"🏁 PIPELINE RUN CYCLE COMPLETE WITH ZERO ERRORS.")

# Force an immediate manual test run on startup so you can see it work!
execute_ecommerce_pipeline()

# Configure the clock schedule loop (Triggers exactly every hour)
schedule.every().hour.do(execute_ecommerce_pipeline)

print("\n🚀 Platform controller is running in the background. Keeping loop alive...")
while True:
    schedule.run_pending()
    time.sleep(1)
