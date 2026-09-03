with history as (

    select *
    from {{ ref('stg_subscription_history') }}
    where status = 'active'
      and mrr > 0

),

months as (

    select distinct date_month as month_start
    from {{ ref('dim_dates') }}
    where date_month >= date_trunc('month', '{{ var("time_spine_start_date") }}'::date)
      and date_month <= date_trunc('month', '{{ var("as_of_date") }}'::date)

),

subscription_months as (

    select
        {{ dbt_utils.generate_surrogate_key(['history.subscription_id', 'months.month_start']) }} as subscription_month_id,
        history.subscription_id,
        history.customer_id,
        months.month_start,
        last_day(months.month_start) as month_end,
        history.plan_id,
        history.seats,
        history.billing_interval,
        history.mrr,
        history.valid_from,
        history.valid_to
    from history
    inner join months
        on history.valid_from <= last_day(months.month_start)
       and history.valid_to > last_day(months.month_start)
       -- A subscription that starts after the as-of date is excluded by the month spine.
       and last_day(months.month_start) <= '{{ var("as_of_date") }}'::date

)

select * from subscription_months
