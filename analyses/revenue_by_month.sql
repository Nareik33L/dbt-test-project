-- Example analysis: collected revenue by month.
select
    date_trunc('month', invoice_date)::date as month_start,
    sum(paid_amount) as revenue,
    count(*) as invoices,
    sum(is_paid) as paid_invoices
from {{ ref('fct_invoices') }}
group by 1
order by 1
