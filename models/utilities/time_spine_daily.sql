{{
    config(
        materialized='table'
    )
}}

-- Daily time spine used by MetricFlow for cumulative metrics, offsets,
-- conversion windows, and join_to_timespine behaviour.

select
    cast(date_day as date) as date_day
from generate_series(
    cast('{{ var("time_spine_start_date") }}' as date),
    cast('{{ var("time_spine_end_date") }}' as date),
    interval 1 day
) as t(date_day)
