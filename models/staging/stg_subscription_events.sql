-- depends_on: {{ ref('raw_subscription_events') }}

with source as (

    select * from {{ source('oakwell_app', 'subscription_events') }}

),

renamed as (

    select
        cast(event_id as integer) as event_id,
        cast(subscription_id as integer) as subscription_id,
        cast(customer_id as integer) as customer_id,
        {{ to_date('event_at') }} as event_at,
        event_type,
        cast(plan_id as integer) as plan_id,
        cast(seats as integer) as seats,
        cast(mrr as double) as mrr,
        billing_interval,
        nullif(notes, '') as notes
    from source

)

select * from renamed
