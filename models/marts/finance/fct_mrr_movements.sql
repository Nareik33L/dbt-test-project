-- Additive MRR bridge at customer-month grain. Each row is a classified
-- commercial movement (or a retained month with zero change). Snapshot-style
-- ending MRR lives in fct_mrr_snapshot; this model is the change log.

select
    mrr_movement_id,
    customer_id,
    month_start,
    month_end,
    movement_type,
    beginning_mrr,
    ending_mrr,
    net_mrr_change,
    new_mrr,
    reactivation_mrr,
    expansion_mrr,
    contraction_mrr,
    churned_mrr,
    plan_id,
    plan_code,
    plan_name,
    billing_interval,
    seats
from {{ ref('int_mrr_movements') }}
where movement_type <> 'retained'
