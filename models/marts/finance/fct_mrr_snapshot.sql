with movements as (

    select * from {{ ref('int_mrr_movements') }}

),

customers as (

    select
        customer_id,
        country_code,
        country_name,
        region,
        subregion,
        industry,
        segment,
        acquisition_channel,
        customer_status
    from {{ ref('dim_customers') }}

)

select
    movements.mrr_movement_id as customer_month_id,
    movements.customer_id,
    movements.month_start,
    movements.month_end,
    movements.beginning_mrr,
    movements.ending_mrr,
    movements.ending_mrr * 12 as ending_arr,
    movements.net_mrr_change,
    movements.movement_type,
    movements.new_mrr,
    movements.reactivation_mrr,
    movements.expansion_mrr,
    movements.contraction_mrr,
    movements.churned_mrr,
    movements.plan_id,
    movements.plan_code,
    movements.plan_name,
    movements.plan_tier,
    movements.billing_interval,
    movements.seats,
    movements.active_subscriptions,
    case when movements.ending_mrr > 0 then 1 else 0 end as is_active,
    case when movements.movement_type = 'new' then 1 else 0 end as is_new_customer,
    case when movements.movement_type = 'churn' then 1 else 0 end as is_churned_customer,
    case when movements.movement_type = 'reactivation' then 1 else 0 end as is_reactivated_customer,
    customers.country_code,
    customers.country_name,
    customers.region,
    customers.subregion,
    coalesce(customers.industry, 'unknown') as industry,
    customers.segment,
    customers.acquisition_channel
from movements
left join customers
    on movements.customer_id = customers.customer_id
