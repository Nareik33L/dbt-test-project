-- depends_on: {{ ref('raw_invoices') }}

with source as (

    select * from {{ source('oakwell_app', 'invoices') }}

),

renamed as (

    select
        cast(invoice_id as integer) as invoice_id,
        invoice_number,
        cast(customer_id as integer) as customer_id,
        {{ to_int('subscription_id') }} as subscription_id,
        {{ to_date('invoice_date') }} as invoice_date,
        {{ to_date('due_date') }} as due_date,
        status,
        currency,
        cast(subtotal_amount as double) as subtotal_amount,
        cast(tax_amount as double) as tax_amount,
        cast(total_amount as double) as total_amount,
        {{ to_date('paid_at') }} as paid_at
    from source

)

select * from renamed
