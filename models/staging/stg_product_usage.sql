-- depends_on: {{ ref('raw_product_usage') }}

with source as (

    select * from {{ source('oakwell_app', 'product_usage') }}

),

renamed as (

    select
        cast(usage_id as integer) as usage_id,
        cast(customer_id as integer) as customer_id,
        {{ to_int('subscription_id') }} as subscription_id,
        {{ to_date('usage_date') }} as usage_date,
        cast(active_seats as integer) as active_seats,
        cast(licensed_seats as integer) as licensed_seats,
        cast(work_items_completed as integer) as work_items_completed,
        cast(api_calls as integer) as api_calls,
        cast(session_minutes as integer) as session_minutes
    from source

)

select * from renamed
