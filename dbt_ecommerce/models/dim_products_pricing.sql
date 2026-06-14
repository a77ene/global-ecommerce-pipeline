{{ config(materialized='table') }}

with inventory as (
    select * from {{ ref('int_regional_inventory_balances') }}
),

behavior as (
    select * from {{ ref('fct_customer_behavior') }}
),

pricing_logic as (
    select
        inv.region_id,
        inv.product_id,
        inv.current_stock_level,
        inv.rolling_avg_stock,
        beh.conversion_rate,
        -- Establish a base retail price floor dynamically for the item
        100.00 as base_retail_price,
        -- Isolate an inventory anomaly condition (stock dropping drastically vs history)
        case 
            when inv.current_stock_level < (inv.rolling_avg_stock * 0.7) then 1 
            else 0 
        end as is_inventory_anomaly
    from inventory inv
    left join behavior beh 
        on inv.region_id = beh.region_id 
        and inv.product_id = beh.product_id
)

select
    region_id,
    product_id,
    current_stock_level,
    rolling_avg_stock,
    conversion_rate,
    is_inventory_anomaly,
    base_retail_price,
    -- Execute the optimization algorithm directly via SQL window mechanics
    case 
        when is_inventory_anomaly = 1 and conversion_rate > 0.10 then round(base_retail_price * 1.15, 2)
        when current_stock_level > (rolling_avg_stock * 1.3) then round(base_retail_price * 0.90, 2) -- Markdown slow items
        else base_retail_price
    end as dynamic_optimized_price
from pricing_logic

