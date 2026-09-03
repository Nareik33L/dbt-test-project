{{
    config(severity='warn')
}}

-- Every active customer-month should have positive ending MRR.
select
    customer_id,
    month_start,
    ending_mrr
from {{ ref('fct_mrr_snapshot') }}
where is_active = 1
  and ending_mrr <= 0
