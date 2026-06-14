import os
import subprocess
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Define base paths for local execution paths
PROJECT_ROOT = "C:\\Users\\allen\\global-ecommerce-pipeline"
DBT_DIR = os.path.join(PROJECT_ROOT, "dbt_ecommerce")
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "Scripts", "python.exe")
VENV_DBT = os.path.join(PROJECT_ROOT, "venv", "Scripts", "dbt.exe")

def run_mock_data_script():
    """Triggers the mock data generator script using the virtual environment python engine."""
    script_path = os.path.join(PROJECT_ROOT, "snowpark_python", "generate_mock_data.py")
    result = subprocess.run([VENV_PYTHON, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Mock Data Script Failed: {result.stderr}")
    print(result.stdout)

# Establish default workflow retry rules
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Define the scheduling loop properties
with DAG(
    dag_id='global_ecommerce_data_platform',
    default_args=default_args,
    description='Automated batch clickstream streaming and dbt transformation loop',
    schedule_interval='@hourly',  # Dynamically recalculate prices and inventory boundaries every hour
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['production', 'elt'],
) as dag:

    # Task 1: Generate fresh user events and stream them into PostgreSQL
    generate_raw_stream = PythonOperator(
        task_id='generate_mock_clickstream_events',
        python_callable=run_mock_data_script
    )

    # Task 2: Fire dbt Core engine to transform data layers and update prices
    execute_dbt_transformations = BashOperator(
        task_id='run_dbt_transformation_layers',
        bash_command=f'cd {DBT_DIR} && {VENV_DBT} run',
    )

    # Establish the sequential dependency chain logic
    generate_raw_stream >> execute_dbt_transformations
