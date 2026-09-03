-- depends_on: {{ ref('raw_subscription_history') }}

with source as (

    select * from {{ source('oakwell_app', 'subscription_history') }}

),

renamed as (

    select
        cast(subscription_history_id as integer) as subscription_history_id,
        cast(subscription_id as integer) as subscription_id,
        cast(customer_id as integer) as customer_id,
        cast(plan_id as integer) as plan_id,
        cast(seats as integer) as seats,
        billing_interval,
        cast(mrr as double) as mrr,
        status,
        {{ to_date('valid_from') }} as valid_from,
        {{ to_date('valid_to') }} as valid_to,
        {{ to_bool('is_current') }} as is_current
    from source

)

select * from renamed
