{{ config(materialized='table') }}

with staging_events as (
    select * from {{ ref('stg_customer_behavior') }}
),

-- 1. Calculate time difference between consecutive clicks for each user
calculated_intervals as (
    select
        *,
        lag(event_at) over (partition by user_id order by event_at) as previous_event_at
    from staging_events
),

-- 2. Flag a new session (1) if idle time > 30 minutes or it's the user's first click
session_flags as (
    select
        *,
        case 
            when extract(epoch from (event_at - previous_event_at)) / 60 > 30 then 1
            when previous_event_at is null then 1
            else 0
        end as is_new_session
    from calculated_intervals
),

-- 3. Create a unique running session identifier per user
session_groups as (
    select
        *,
        sum(is_new_session) over (partition by user_id order by event_at rows unbounded preceding) as user_session_index
    from session_flags
)

select
    event_id,
    user_id,
    -- Construct a clean, deterministic unique session token
    concat(user_id, '_', user_session_index) as unique_session_id,
    event_at,
    event_type,
    product_id,
    region_id,
    device_type
from session_groups
