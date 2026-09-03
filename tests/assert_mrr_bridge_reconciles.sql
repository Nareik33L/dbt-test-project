-- Bridge components should reconcile to the month-on-month change.
-- new + reactivation + expansion - contraction - churned = ending - beginning
-- for every customer-month.

select
    customer_id,
    month_start,
    ending_mrr,
    beginning_mrr,
    new_mrr + reactivation_mrr + expansion_mrr - contraction_mrr - churned_mrr as reconstructed_change,
    ending_mrr - beginning_mrr as actual_change
from {{ ref('int_mrr_movements') }}
where abs(
        (new_mrr + reactivation_mrr + expansion_mrr - contraction_mrr - churned_mrr)
        - (ending_mrr - beginning_mrr)
    ) > 0.02
