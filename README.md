# Global E-Commerce Real-Time Pricing & Inventory Pipeline

An end-to-end, production-grade ELT data platform that ingests streaming global clickstream events, monitors regional inventory balances for supply chain stock anomalies, and dynamically recalculates real-time optimal consumer pricing structures.

## 🏗️ Architecture Blueprint
1. **Extraction/Ingest Layer**: A custom Python generator engine leverages `Faker` to continuously stream mock geographic clickstream telemetry data into a local raw PostgreSQL schema layout database environment.
2. **Orchestration Layer (Local / Windows)**: A native Python `schedule` background daemon executes a lightweight, zero-dependency processing loop on an automated clock cycle.
3. **Data Transformation & Testing Platform (dbt Core)**:
   - **Staging**: Casts event models, sanitizes nested timestamp targets, and structures data types.
   - **Intermediate**: Applies advanced analytical SQL window analytics (`LEAD`/`LAG`) to group customer logs into clean sessions and calculates a 7-period historical rolling inventory average baseline.
   - **Marts**: Couples conversion velocities with supply chain warning constraints to dynamically apply demand-elasticity price adjustments.
4. **Analytics Layer**: An interactive **Streamlit** control panel reads downstream pricing structures directly from data mart layers to render real-time optimization insights.

## 🛠️ Repository Directory Blueprint
```text
global-ecommerce-pipeline/
├── airflow/                 # Planned architectural DAG skeletons
├── dbt_ecommerce/           # Core data transformation models
│   ├── models/
│   │   ├── src_ecommerce.yml
│   │   ├── stg_customer_behavior.sql
│   │   ├── int_customer_sessions.sql
│   │   ├── int_regional_inventory_balances.sql
│   │   ├── fct_customer_behavior.sql
│   │   └── dim_products_pricing.sql
│   └── dbt_project.yml
├── snowpark_python/         # Automated database load scripts
│   └── generate_mock_data.py
├── dashboard.py             # Streamlit visual dashboard interface
├── run_pipeline_orchestrator.py # Master loop controller daemon
└── .gitignore
```

## 🚀 Deployment Instructions
1. Ensure a local instance of PostgreSQL is listening on port `5432`.
2. Spin up a virtual environment and load required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install dbt-postgres pandas faker sqlalchemy psycopg2-binary streamlit schedule
   ```
3. Update database authentication configurations inside `profiles.yml`, `generate_mock_data.py`, and `dashboard.py`.
4. Fire up the platform loop controller daemon:
   ```bash
   python run_pipeline_orchestrator.py
   ```
5. View real-time pricing multipliers by launching the analytical control hub:
   ```bash
   streamlit run dashboard.py
   ```---

## 🚀 Future Roadmap: Scaling to Production (Apache Airflow)
While the current architecture utilizes a lightweight local Python scheduler to bypass Windows OS limitations (specifically the UNIX-only `pwd` dependency), the repository includes an **`airflow/`** directory skeleton. 

When deploying this platform to production cloud environments (AWS/GCP/Azure) inside isolated Linux containers, the infrastructure is pre-configured to easily replace the local scheduler with **Apache Airflow**. The `airflow/dags/ecommerce_master_pipeline.py` template is ready to manage heavy upstream/downstream retries, failure notifications, and distributed DAG task execution.
