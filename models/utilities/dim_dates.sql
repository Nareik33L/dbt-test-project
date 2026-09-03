with days as (

    select date_day
    from {{ ref('time_spine_daily') }}

)

select
    date_day,
    date_trunc('week', date_day)::date as date_week,
    date_trunc('month', date_day)::date as date_month,
    date_trunc('quarter', date_day)::date as date_quarter,
    date_trunc('year', date_day)::date as date_year,
    extract(year from date_day)::integer as year_number,
    extract(quarter from date_day)::integer as quarter_number,
    extract(month from date_day)::integer as month_number,
    extract(dow from date_day)::integer as day_of_week,
    strftime(date_day, '%Y-%m') as year_month,
    last_day(date_day) as month_end_date,
    date_day = last_day(date_day) as is_month_end,
    date_day <= '{{ var("as_of_date") }}'::date as is_as_of_or_before
from days
