-- depends_on: {{ ref('raw_invoice_items') }}

with source as (

    select * from {{ source('oakwell_app', 'invoice_items') }}

),

renamed as (

    select
        cast(invoice_item_id as integer) as invoice_item_id,
        cast(invoice_id as integer) as invoice_id,
        cast(customer_id as integer) as customer_id,
        {{ to_int('subscription_id') }} as subscription_id,
        {{ to_int('plan_id') }} as plan_id,
        description,
        item_type,
        cast(quantity as double) as quantity,
        cast(unit_price as double) as unit_price,
        cast(amount as double) as amount
    from source

)

select * from renamed
