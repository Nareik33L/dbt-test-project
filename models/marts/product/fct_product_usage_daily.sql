with usage as (

    select * from {{ ref('stg_product_usage') }}

),

customers as (

    select
        customer_id,
        country_code,
        region,
        segment,
        acquisition_channel,
        customer_status
    from {{ ref('dim_customers') }}

)

select
    usage.usage_id,
    usage.customer_id,
    usage.subscription_id,
    usage.usage_date,
    usage.active_seats,
    usage.licensed_seats,
    usage.work_items_completed,
    usage.api_calls,
    usage.session_minutes,
    case
        when usage.licensed_seats = 0 then 0
        else usage.active_seats::double / usage.licensed_seats
    end as seat_utilisation,
    customers.country_code,
    customers.region,
    customers.segment,
    customers.acquisition_channel,
    customers.customer_status
from usage
left join customers
    on usage.customer_id = customers.customer_id
