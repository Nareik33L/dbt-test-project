with invoices as (

    select * from {{ ref('stg_invoices') }}

),

customers as (

    select
        customer_id,
        country_code,
        region,
        segment,
        acquisition_channel
    from {{ ref('stg_customers') }}

),

items as (

    select
        invoice_id,
        count(*) as line_item_count,
        sum(case when item_type = 'subscription' then amount else 0 end) as subscription_amount,
        sum(case when item_type = 'addon' then amount else 0 end) as addon_amount,
        sum(case when item_type = 'one_time' then amount else 0 end) as one_time_amount
    from {{ ref('stg_invoice_items') }}
    group by 1

)

select
    invoices.invoice_id,
    invoices.invoice_number,
    invoices.customer_id,
    invoices.subscription_id,
    invoices.invoice_date,
    invoices.due_date,
    invoices.status as invoice_status,
    invoices.currency,
    invoices.subtotal_amount,
    invoices.tax_amount,
    invoices.total_amount,
    invoices.paid_at,
    case when invoices.status = 'paid' then invoices.total_amount else 0 end as paid_amount,
    case when invoices.status = 'paid' then 1 else 0 end as is_paid,
    case
        when invoices.total_amount >= 2000 then 'large'
        when invoices.total_amount >= 500 then 'medium'
        else 'small'
    end as invoice_size_tier,
    coalesce(items.line_item_count, 0) as line_item_count,
    coalesce(items.subscription_amount, 0) as subscription_amount,
    coalesce(items.addon_amount, 0) as addon_amount,
    coalesce(items.one_time_amount, 0) as one_time_amount,
    customers.country_code,
    customers.region,
    customers.segment,
    customers.acquisition_channel
from invoices
left join items
    on invoices.invoice_id = items.invoice_id
left join customers
    on invoices.customer_id = customers.customer_id
