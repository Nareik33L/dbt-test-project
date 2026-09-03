with items as (

    select * from {{ ref('stg_invoice_items') }}

),

invoices as (

    select
        invoice_id,
        invoice_date,
        status as invoice_status,
        currency
    from {{ ref('stg_invoices') }}

),

plans as (

    select plan_id, plan_code, plan_name
    from {{ ref('stg_plans') }}

)

select
    items.invoice_item_id,
    items.invoice_id,
    items.customer_id,
    items.subscription_id,
    items.plan_id,
    plans.plan_code,
    plans.plan_name,
    items.description,
    items.item_type,
    items.quantity,
    items.unit_price,
    items.amount,
    invoices.invoice_date,
    invoices.invoice_status,
    invoices.currency,
    case when invoices.invoice_status = 'paid' then items.amount else 0 end as paid_amount,
    case when items.amount >= 1000 then 'gte_1000' else 'lt_1000' end as amount_band
from items
left join invoices
    on items.invoice_id = invoices.invoice_id
left join plans
    on items.plan_id = plans.plan_id
