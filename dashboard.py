import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# Set up page configurations
st.set_page_config(page_title="Global E-Commerce Pricing Control Center", layout="wide")

st.title("📊 Global E-Commerce Dynamic Pricing Control Center")
st.markdown("Real-time telemetry tracking regional inventory anomalies and price optimization thresholds.")

# Establish connection to local database
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '544ko') # <-- Replace with your real password
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'ecom_analytics_db')

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Fetch latest calculation parameters from dbt Mart Layer
try:
    df = pd.read_sql("SELECT * FROM dim_products_pricing", engine)
    
    # ─── METRIC BLOCKS ───
    total_anomalies = int(df['is_inventory_anomaly'].sum())
    avg_conversion = float(df['conversion_rate'].mean() * 100)
    max_price = float(df['dynamic_optimized_price'].max())
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="🚨 Active Regional Stock Anomalies", value=total_anomalies, delta="-2% vs last hour")
    col2.metric(label="📈 Average Platform Conversion Rate", value=f"{avg_conversion:.2f}%")
    col3.metric(label="💰 Highest Surge Optimized Price", value=f"${max_price:.2f}", delta="+$15.00 Scarcity Premium")
    
    # ─── COMPONENT CHART ───
    st.subheader("📊 Price Spikes vs Baseline by Region")
    chart_data = df.groupby('region_id')[['base_retail_price', 'dynamic_optimized_price']].mean()
    st.bar_chart(chart_data)
    
    # ─── PIE CHART SECTION ───
    st.subheader("📈 Composition Analysis")
    
    pie_col1, pie_col2 = st.columns(2)
    
    with pie_col1:
        st.write("**Products by Region**")
        regional_distribution = df.groupby('region_id').size()
        st.pie_chart(regional_distribution)
    
    with pie_col2:
        st.write("**Inventory Anomaly Status**")
        anomaly_counts = df['is_inventory_anomaly'].value_counts()
        anomaly_labels = {1: 'With Anomalies', 0: 'Normal Stock'}
        anomaly_counts.index = anomaly_counts.index.map(anomaly_labels)
        st.pie_chart(anomaly_counts)
    
    # ─── ADDITIONAL PIE CHARTS ───
    pie_col3, pie_col4 = st.columns(2)
    
    with pie_col3:
        st.write("**Price Tier Distribution**")
        # Categorize products by price range
        price_bins = [0, df['dynamic_optimized_price'].quantile(0.33), 
                      df['dynamic_optimized_price'].quantile(0.66), 
                      df['dynamic_optimized_price'].max()]
        price_labels = ['Budget', 'Mid-Range', 'Premium']
        df['price_tier'] = pd.cut(df['dynamic_optimized_price'], bins=price_bins, labels=price_labels, include_lowest=True)
        price_tier_dist = df['price_tier'].value_counts()
        st.pie_chart(price_tier_dist)
    
    with pie_col4:
        st.write("**Conversion Rate Performance**")
        # Categorize by conversion rate quartiles
        conv_bins = [0, df['conversion_rate'].quantile(0.25),
                     df['conversion_rate'].quantile(0.75), 1.0]
        conv_labels = ['Low', 'Medium', 'High']
        df['conversion_tier'] = pd.cut(df['conversion_rate'], bins=conv_bins, labels=conv_labels, include_lowest=True)
        conv_dist = df['conversion_tier'].value_counts()
        st.pie_chart(conv_dist)
    
    # ─── DATA SECTIONS ───
    st.subheader("🌐 Global Price Matrix Grid")
    
    # Highlight items experiencing scarcity pricing adjustments
    def highlight_surges(row):
        return ['background-color: #ffcccc' if row.is_inventory_anomaly == 1 else '' for _ in row]
        
    st.dataframe(df.style.apply(highlight_surges, axis=1), use_container_width=True)

except Exception as e:
    st.error(f"Could not connect to database. Ensure your orchestrator loop is running. Error: {e}")
