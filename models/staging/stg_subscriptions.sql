-- depends_on: {{ ref('raw_subscriptions') }}

with source as (

    select * from {{ source('oakwell_app', 'subscriptions') }}

),

renamed as (

    select
        cast(subscription_id as integer) as subscription_id,
        cast(customer_id as integer) as customer_id,
        cast(plan_id as integer) as plan_id,
        cast(seats as integer) as seats,
        billing_interval,
        cast(mrr as double) as mrr,
        {{ to_date('started_at') }} as started_at,
        {{ to_date('ended_at') }} as ended_at,
        status,
        nullif(cancellation_reason, '') as cancellation_reason
    from source

)

select * from renamed
