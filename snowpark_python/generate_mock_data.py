import os
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
import sqlalchemy
from sqlalchemy import create_engine

fake = Faker()
NUM_USERS = 50
NUM_EVENTS = 500
REGIONS = ['US-EAST', 'EU-WEST', 'AP-SOUTH', 'LATAM']
EVENT_TYPES = ['page_view', 'product_view', 'add_to_cart', 'remove_from_cart', 'checkout_click', 'purchase_success']

def generate_ecom_events():
    """Generates realistic raw e-commerce clickstream payloads."""
    user_pool = [str(uuid.uuid4())[:8] for _ in range(NUM_USERS)]
    product_pool = [f"PROD-{random.randint(1000, 1050)}" for _ in range(50)]
    
    events = []
    base_time = datetime.utcnow() - timedelta(days=1)
    
    for _ in range(NUM_EVENTS):
        base_time += timedelta(seconds=random.randint(5, 300))
        user_id = random.choice(user_pool)
        
        event_payload = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": str(hash(user_id))[-6:],
            "event_timestamp": base_time.strftime('%Y-%m-%d %H:%M:%S'),
            "event_type": random.choice(EVENT_TYPES),
            "product_id": random.choice(product_pool),
            "region_id": random.choice(REGIONS),
            "ip_address": fake.ipv4(),
            "device_type": random.choice(['desktop', 'mobile', 'tablet'])
        }
        events.append(event_payload)
        
    return pd.DataFrame(events)

def upload_to_postgres(df):
    """Connects to local PostgreSQL and inserts the mock dataframe."""
    print(f"Connecting to local PostgreSQL to upload {len(df)} rows...")
    
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'YourActualPasswordHere') # <-- Ensure your real password is here
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'ecom_analytics_db')
    
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    # SQLAlchemy 2.0 native auto-committing connection block
    with engine.begin() as connection:
        connection.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS raw;"))

    # Stream data straight into the raw schema layer
    df.to_sql('raw_customer_behavior', engine, schema='raw', if_exists='replace', index=False)
    print("Successfully populated ecom_analytics_db.raw.raw_customer_behavior!")
