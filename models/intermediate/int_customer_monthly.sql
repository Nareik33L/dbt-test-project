with subscription_months as (

    select *
    from {{ ref('int_subscription_monthly') }}

),

plans as (

    select plan_id, plan_code, plan_name, plan_tier
    from {{ ref('stg_plans') }}

),

rolled_up as (

    select
        customer_id,
        month_start,
        max(month_end) as month_end,
        sum(mrr) as mrr,
        sum(seats) as seats,
        count(distinct subscription_id) as active_subscriptions,
        arg_max(plan_id, mrr) as plan_id,
        arg_max(billing_interval, mrr) as billing_interval
    from subscription_months
    group by 1, 2

),

with_plan as (

    select
        rolled_up.customer_id,
        rolled_up.month_start,
        rolled_up.month_end,
        rolled_up.mrr,
        rolled_up.seats,
        rolled_up.active_subscriptions,
        rolled_up.plan_id,
        plans.plan_code,
        plans.plan_name,
        plans.plan_tier,
        rolled_up.billing_interval
    from rolled_up
    left join plans
        on rolled_up.plan_id = plans.plan_id

)

select * from with_plan
