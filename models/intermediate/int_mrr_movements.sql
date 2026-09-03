with monthly as (

    select *
    from {{ ref('int_customer_monthly') }}

),

cancelled as (

    select distinct
        customer_id,
        date_trunc('month', ended_at)::date as month_start
    from {{ ref('stg_subscriptions') }}
    where ended_at is not null

),

-- Customer-level churn month: the month a subscription ended, if the customer
-- had no remaining MRR at that month-end (already excluded from monthly).
churn_months as (

    select
        cancelled.customer_id,
        cancelled.month_start,
        last_day(cancelled.month_start) as month_end,
        0.0 as mrr,
        0 as seats,
        0 as active_subscriptions,
        cast(null as integer) as plan_id,
        cast(null as varchar) as plan_code,
        cast(null as varchar) as plan_name,
        cast(null as integer) as plan_tier,
        cast(null as varchar) as billing_interval
    from cancelled
    left join monthly
        on cancelled.customer_id = monthly.customer_id
       and cancelled.month_start = monthly.month_start
    where monthly.customer_id is null

),

combined as (

    select
        customer_id,
        month_start,
        month_end,
        mrr,
        seats,
        active_subscriptions,
        plan_id,
        plan_code,
        plan_name,
        plan_tier,
        billing_interval
    from monthly

    union all

    select
        customer_id,
        month_start,
        month_end,
        mrr,
        seats,
        active_subscriptions,
        plan_id,
        plan_code,
        plan_name,
        plan_tier,
        billing_interval
    from churn_months

),

with_lag as (

    select
        combined.*,
        lag(mrr) over (
            partition by customer_id
            order by month_start
        ) as previous_mrr,
        lag(month_start) over (
            partition by customer_id
            order by month_start
        ) as previous_month_start
    from combined

),

classified as (

    select
        {{ dbt_utils.generate_surrogate_key(['customer_id', 'month_start']) }} as mrr_movement_id,
        customer_id,
        month_start,
        month_end,
        mrr as ending_mrr,
        coalesce(previous_mrr, 0) as beginning_mrr,
        previous_month_start,
        mrr - coalesce(previous_mrr, 0) as net_mrr_change,
        case
            when previous_mrr is null and mrr > 0 then 'new'
            when coalesce(previous_mrr, 0) > 0 and mrr = 0 then 'churn'
            when coalesce(previous_mrr, 0) = 0 and mrr > 0 then 'reactivation'
            when mrr > previous_mrr then 'expansion'
            when mrr < previous_mrr then 'contraction'
            else 'retained'
        end as movement_type,
        case when previous_mrr is null and mrr > 0 then mrr else 0 end as new_mrr,
        case
            when previous_mrr is not null and previous_mrr = 0 and mrr > 0 then mrr
            else 0
        end as reactivation_mrr,
        case
            when previous_mrr is not null and previous_mrr > 0 and mrr > previous_mrr then mrr - previous_mrr
            else 0
        end as expansion_mrr,
        case
            when previous_mrr is not null and mrr < previous_mrr and mrr > 0 then previous_mrr - mrr
            else 0
        end as contraction_mrr,
        case when coalesce(previous_mrr, 0) > 0 and mrr = 0 then previous_mrr else 0 end as churned_mrr,
        plan_id,
        plan_code,
        plan_name,
        plan_tier,
        billing_interval,
        seats,
        active_subscriptions
    from with_lag

)

select * from classified
