with subscriptions as (

    select * from {{ ref('stg_subscriptions') }}

),

plans as (

    select * from {{ ref('stg_plans') }}

),

customers as (

    select customer_id, country_code, region, segment, acquisition_channel
    from {{ ref('stg_customers') }}

)

select
    {{ dbt_utils.generate_surrogate_key(['subscriptions.subscription_id']) }} as subscription_key,
    subscriptions.subscription_id,
    subscriptions.customer_id,
    subscriptions.plan_id,
    plans.plan_code,
    plans.plan_name,
    plans.plan_tier,
    subscriptions.seats,
    subscriptions.billing_interval,
    subscriptions.mrr,
    subscriptions.mrr * 12 as arr,
    subscriptions.started_at,
    subscriptions.ended_at,
    subscriptions.status as subscription_status,
    subscriptions.cancellation_reason,
    customers.country_code,
    customers.region,
    customers.segment,
    customers.acquisition_channel,
    datediff('day', subscriptions.started_at, coalesce(subscriptions.ended_at, '{{ var("as_of_date") }}'::date)) as duration_days
from subscriptions
left join plans
    on subscriptions.plan_id = plans.plan_id
left join customers
    on subscriptions.customer_id = customers.customer_id
