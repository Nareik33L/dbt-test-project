# Oakwell ground truth

Expected answers calculated from the DuckDB warehouse after `dbt build`.
Do not edit numbers by hand — regenerate with `python scripts/compute_ground_truth.py --write`.

Cases: **26**. As-of date: **2026-08-31**.

## GT-001 — What was collected revenue in July 2026?

- Concept: `revenue`
- Time period: 2026-07-01 to 2026-07-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `2183549.37`

## GT-002 — What was ending MRR as of August 2026?

- Concept: `ending_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `2309714.33`

## GT-003 — How many customers had positive ending MRR in August 2026?

- Concept: `active_customers`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `342`

## GT-004 — What was ending ARR as of August 2026?

- Concept: `ending_arr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `27716571.96`

## GT-005 — Which customer segments generated the most ending MRR in August 2026?

- Concept: `ending_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Dimensions: `customer_segment`
- Method: Independent DuckDB SQL against the built marts.
- Expected result:

| customer_segment | ending_mrr |
| --- | --- |
| Enterprise | 1912046.67 |
| Mid-Market | 330153.5 |
| SMB | 67514.16 |


## GT-006 — How much collected revenue came from United States customers in July 2026?

- Concept: `revenue`
- Time period: 2026-07-01 to 2026-07-31 (month)
- Filters: country = US
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `901475.37`

## GT-007 — How much new MRR was added in August 2026?

- Concept: `new_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `26278.67`

## GT-008 — How much expansion MRR was recognised in August 2026?

- Concept: `expansion_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `21312.0`

## GT-009 — How much MRR did we lose to contraction in August 2026?

- Concept: `contraction_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `8279.5`

## GT-010 — How much MRR was lost to churn in August 2026?

- Concept: `churned_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `2771.5`

## GT-011 — How many customers churned in August 2026?

- Concept: `churned_customers`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `6`

## GT-012 — How many new paying customers were added in August 2026?

- Concept: `new_customers`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `12`

## GT-013 — What was net new MRR in August 2026?

- Concept: `net_new_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `36829.67`

## GT-014 — What was ARPU in August 2026?

- Concept: `arpu`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `6753.55`

## GT-015 — How many support tickets were opened in Q2 2026?

- Concept: `support_tickets`
- Time period: 2026-04-01 to 2026-06-30 (quarter)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `671`

## GT-016 — How did Q2 2026 support tickets break down by category?

- Concept: `support_tickets`
- Time period: 2026-04-01 to 2026-06-30 (quarter)
- Dimensions: `ticket_category`
- Method: Independent DuckDB SQL against the built marts.
- Expected result:

| ticket_category | support_tickets |
| --- | --- |
| billing | 89 |
| bug | 147 |
| feature_request | 112 |
| how_to | 237 |
| onboarding | 62 |
| outage | 24 |


## GT-017 — What share of trials started in 2025 converted to paid?

- Concept: `trial_conversion_rate`
- Time period: 2025-01-01 to 2025-12-31 (year)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `0.5143`

## GT-018 — How many invoices were paid in the first half of 2026?

- Concept: `paid_invoice_count`
- Time period: 2026-01-01 to 2026-06-30 (half)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `921`

## GT-019 — What was the average paid invoice value in July 2026?

- Concept: `average_invoice_value`
- Time period: 2026-07-01 to 2026-07-31 (month)
- Filters: invoice_status = paid
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `12198.6`

## GT-020 — How many work items were completed in August 2026?

- Concept: `work_items_completed`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `915126`

## GT-021 — What was Enterprise ending MRR in August 2026?

- Concept: `enterprise_ending_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Filters: customer_segment = Enterprise
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `1912046.67`

## GT-022 — How much collected revenue in 2026 came from invoices of $2,000 or more?

- Concept: `large_invoice_revenue`
- Time period: 2026-01-01 to 2026-08-31 (ytd)
- Filters: invoice_size_tier = large
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `16141039.17`

## GT-023 — What is the outstanding amount on open invoices?

- Concept: `open_invoice_amount`
- Time period: 2022-07-01 to 2026-08-31 (all_time)
- Filters: invoice_status = open
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `22809.0`

## GT-024 — How much paid subscription line-item revenue was recognised in July 2026?

- Concept: `subscription_revenue`
- Time period: 2026-07-01 to 2026-07-31 (month)
- Filters: item_type = subscription
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `2178681.37`

## GT-025 — What was ending MRR from self-serve acquired customers in August 2026?

- Concept: `self_serve_ending_mrr`
- Time period: 2026-08-01 to 2026-08-31 (month)
- Filters: acquisition_channel = self_serve
- Method: Independent DuckDB SQL against the built marts.
- Expected result: `127045.47`

## GT-026 — How has ending MRR changed month by month from March to August 2026?

- Concept: `ending_mrr`
- Time period: 2026-03-01 to 2026-08-31 (month)
- Dimensions: `month_start`
- Method: Independent DuckDB SQL against the built marts.
- Expected result:

| month_start | ending_mrr |
| --- | --- |
| 2026-03-01 | 2122574.49 |
| 2026-04-01 | 2180896.82 |
| 2026-05-01 | 2188524.31 |
| 2026-06-01 | 2243301.65 |
| 2026-07-01 | 2272884.66 |
| 2026-08-01 | 2309714.33 |

