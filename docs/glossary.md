# Oakwell metric glossary

Short definitions for the metrics published in this project. Grain and
additivity notes matter: several SaaS measures are snapshots, not flows.

## Snapshot / semi-additive

| Metric | Meaning |
| --- | --- |
| Ending MRR | Monthly recurring revenue as of month-end. Take the last month in a range, then sum customers. |
| Ending ARR | Ending MRR × 12. |
| Active customers | Customers with ending MRR > 0 as of that month-end. |
| Active subscriptions | Subscriptions contributing MRR at month-end. |
| Ending seats | Licensed seats at month-end. |
| ARPU | Ending MRR / active customers. |

## Additive MRR bridge

| Metric | Meaning |
| --- | --- |
| New MRR | First paid month for a customer. |
| Expansion MRR | Increase in MRR from an already-paying customer. |
| Contraction MRR | Decrease in MRR from a still-paying customer. |
| Churned MRR | MRR lost when a customer goes to zero. |
| Reactivation MRR | MRR from a customer who had previously churned. |
| Net new MRR | New + expansion + reactivation − contraction − churn. |

## Revenue and invoicing

| Metric | Meaning |
| --- | --- |
| Revenue | Paid invoice totals (cash collected), including subscription, add-on, and one-time lines. |
| Billed amount | Invoice totals excluding voids. |
| Subscription / add-on / one-time revenue | Paid line items by type. |
| Average / median invoice value | On paid invoices. |

## Product and support

| Metric | Meaning |
| --- | --- |
| Work items completed | In-product work items finished. |
| Seat utilisation | Active seat-days / licensed seat-days on days with activity. |
| Support tickets | Tickets opened. |
| Tickets per active customer | Tickets / ending active customers. |

Revenue is **not** the same as MRR. Annual invoices recognise a year of cash in the invoice month; MRR spreads that value across the subscription term.
