with trials as (

    select * from {{ ref('stg_trials') }}

),

customers as (

    select
        customer_id,
        country_code,
        region,
        segment,
        acquisition_channel as customer_acquisition_channel
    from {{ ref('stg_customers') }}

)

select
    trials.trial_id,
    trials.customer_id,
    trials.trial_start_date,
    trials.trial_end_date,
    trials.is_converted,
    trials.converted_at,
    trials.acquisition_channel,
    case when trials.is_converted then 1 else 0 end as converted_count,
    case when trials.is_converted then 'converted' else 'not_converted' end as conversion_status,
    datediff('day', trials.trial_start_date, coalesce(trials.converted_at, trials.trial_end_date)) as trial_duration_days,
    customers.country_code,
    customers.region,
    customers.segment
from trials
left join customers
    on trials.customer_id = customers.customer_id
