{{ config(materialized='table') }}

with sessions as (
    select * from {{ ref('int_customer_sessions') }}
)

select
    region_id,
    product_id,
    count(distinct unique_session_id) as total_sessions,
    count(case when event_type = 'product_view' then 1 end) as total_views,
    count(case when event_type = 'add_to_cart' then 1 end) as total_carts,
    count(case when event_type = 'purchase_success' then 1 end) as total_purchases,
    -- Calculate conversion rate; handle division-by-zero safely
    case 
        when count(case when event_type = 'product_view' then 1 end) > 0 
        then round(count(case when event_type = 'purchase_success' then 1 end)::numeric / count(case when event_type = 'product_view' then 1 end)::numeric, 4)
        else 0 
    end as conversion_rate
from sessions
group by 1, 2
