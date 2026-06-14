{{ config(materialized='table') }}

with session_events as (
    select * from {{ ref('int_customer_sessions') }}
),

-- Aggregate purchase actions per product, per region, per hour
regional_demand as (
    select
        date_trunc('hour', event_at) as evaluation_hour,
        region_id,
        product_id,
        count(case when event_type = 'purchase_success' then 1 end) as total_purchases,
        count(case when event_type = 'add_to_cart' then 1 end) as cart_additions
    from session_events
    group by 1, 2, 3
)

select
    evaluation_hour,
    region_id,
    product_id,
    total_purchases,
    cart_additions,
    -- Simulate current stock levels on hand locally for processing
    -- If demand spikes high, the simulated stock drops significantly
    greatest(100 - (total_purchases * 5) - (cart_additions * 2), 0) as current_stock_level,
    -- Build a 7-period historical rolling average baseline directly in Postgres
    avg(greatest(100 - (total_purchases * 5) - (cart_additions * 2), 0)) over (
        partition by region_id, product_id 
        order by evaluation_hour 
        rows between 6 preceding and current row
    ) as rolling_avg_stock
from regional_demand

