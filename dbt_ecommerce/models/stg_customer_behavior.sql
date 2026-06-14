{{ config(materialized='view') }}

with raw_events as (
    select * from {{ source('raw_source', 'raw_customer_behavior') }}
)

select
    event_id,
    user_id,
    session_id,
    -- Cast text timestamps into proper database datetime objects
    cast(event_timestamp as timestamp) as event_at,
    event_type,
    product_id,
    region_id,
    ip_address,
    device_type
from raw_events
