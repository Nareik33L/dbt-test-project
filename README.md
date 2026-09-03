# Oakwell analytics

dbt Core + MetricFlow project for **Oakwell**, a fictional B2B SaaS company.
The warehouse runs locally on DuckDB. No cloud credentials are required.

## 1. The company

Oakwell Labs sells **Oakwell**, a work-management platform used by professional-services firms, logistics operators, facilities teams, manufacturers, and similar organisations. Customers run standard operating procedures, work orders, and capacity planning across locations.

The company is commercially active from July 2022 through the warehouse as-of date of **31 August 2026**. Headquarters sells worldwide in USD.

## 2. Business model

Seat-based subscriptions on four packaged plans:

| Plan | List price | Typical buyer | Billing |
| --- | --- | --- | --- |
| Starter | $29 / seat / month | Small teams | Monthly only, cap 10 seats |
| Team | $59 / seat / month | Growing operations teams | Monthly or annual |
| Business | $99 / seat / month | Multi-site operators | Monthly or annual, SSO |
| Enterprise | $149 / seat / month | Large organisations | Annual only, SSO + premium support |

Annual terms collect ten months up front (two months free). **MRR** is the monthly equivalent of contracted recurring subscription value. Implementation fees, extra storage, and success packages appear on invoices as add-ons or one-time lines and count toward **collected revenue**, not MRR.

Customers are organisations (not individual users), segmented SMB / Mid-Market / Enterprise from employee count. Acquisition is credited to self-serve, inbound, outbound, partner, or event.

## 3. The dataset

Synthetic application, billing, usage, and support extracts generated with a fixed seed (`42`) so rebuilds are identical.

| Extract | Grain | Rows (approx.) |
| --- | --- | --- |
| Customers | organisation | 570 (480 paying + 90 expired trials) |
| Plans | plan | 4 |
| Subscriptions | subscription | 495 |
| Subscription history | type-2 state | 1,137 |
| Subscription events | commercial event | 1,290 |
| Invoices | invoice | 4,193 |
| Invoice items | line | 4,451 |
| Product usage | customer-day with activity | 89,857 |
| Support tickets | ticket | 5,349 |
| Trials | trial | 201 |

History covers **July 2022 – August 2026**. Geography includes the US (with census regions), Canada, UK, Germany, France, Netherlands, Sweden, and Australia. The book includes new logos, churn, reactivations, plan upgrades/downgrades, seat expansion/contraction, high- and low-usage accounts, and a long tail of support volume.

As of August 2026 there are **342** customers with positive ending MRR.

## 4. Warehouse / data model

Raw extracts load as dbt seeds (`raw_*`). Staging models clean types. Intermediate models reconstruct month-end subscription state from type-2 history and classify the customer-month MRR bridge. Marts are the tables MetricFlow reads.

**Ending MRR** is a month-end snapshot: a subscription contributes to month M if it was commercially active on the last day of M. That is semi-additive across time (use the latest month in a range). **New / expansion / contraction / churned / reactivation MRR** are additive flows.

Collected **revenue** is the sum of paid invoice totals. It is not the same as MRR: an annual invoice books a year of cash in the invoice month.

## 5. dbt project structure

```text
models/
  staging/          stg_* from seeds (source-documented)
  intermediate/     subscription-month, customer-month, MRR bridge
  marts/
    core/           dim_customers, dim_plans, fct_subscriptions, fct_trials
    finance/        fct_mrr_snapshot, fct_mrr_movements, invoices, invoice items
    product/        fct_product_usage_daily
    support/        fct_support_tickets
  utilities/        time_spine_daily, dim_dates
  metrics.yml       derived, ratio, cumulative, and conversion metrics
seeds/              raw extracts
macros/             date/int/bool casting helpers
scripts/            data generator, ground truth, validation
validation/         questions and expected answers
```

## 6. Semantic models

MetricFlow semantic models are declared on the mart YAML (dbt 1.12 spec): entities and dimensions on columns, simple metrics on the model, cross-model metrics in `models/metrics.yml`.

| Semantic model | Primary entity | Time dimension | Role |
| --- | --- | --- | --- |
| `customers` | customer | signup_date | Organisation attributes, signups |
| `plans` | plan | — | Plan catalogue |
| `subscriptions` | subscription | started_at | Subscription starts / cancels |
| `trials` | trial | trial_start_date | Trial cohort conversion |
| `mrr_snapshot` | customer_month | month_start (month) | Ending MRR and the MRR bridge |
| `mrr_movements` | mrr_movement | month_start (month) | Non-retained commercial movements |
| `invoices` | invoice | invoice_date | Billed and collected cash |
| `invoice_items` | invoice_item | invoice_date | Line-item mix |
| `product_usage` | usage_day | usage_date | Adoption and utilisation |
| `support_tickets` | ticket | opened_at | Support volume and SLAs |

Facts join to `customer` (and often `plan`) so geography, segment, and channel on `dim_customers` are available next to measures. Snapshot facts also carry historical plan and geo for time-correct slicing.

## 7. Important metrics

**Snapshots (semi-additive, last month in the window):** `ending_mrr`, `ending_arr`, `active_customers`, `active_subscriptions`, `ending_seats`, plus filtered variants (`enterprise_ending_mrr`, `smb_ending_mrr`, `self_serve_ending_mrr`).

**Additive MRR bridge:** `new_mrr`, `expansion_mrr`, `contraction_mrr`, `churned_mrr`, `reactivation_mrr`, `new_customers`, `churned_customers`. Derived: `net_new_mrr`, `arr`, `arpu`, `customer_churn_rate`, `gross_mrr_churn_rate`, `net_revenue_retention`, `mrr_mom_change`.

**Invoicing:** `revenue`, `billed_amount`, `invoice_count`, `average_invoice_value`, `median_invoice_value`, `large_invoice_revenue`, `open_invoice_amount`, `subscription_revenue`, `addon_revenue`, `one_time_revenue`.

**Product / support / trials:** `work_items_completed`, `seat_utilisation`, `support_tickets`, `tickets_per_active_customer`, `p90_first_response_hours`, `trial_conversion_rate`, `trial_to_paid_conversion` (30-day conversion), `trailing_90d_work_items`, `revenue_ytd`.

Offset and cumulative metrics must be queried with `metric_time` in the group-by list.

## 8. How synthetic data is generated

`scripts/generate_source_data.py` uses `random.Random(42)` and walks each customer month by month:

- Signup volume follows a growing, seasonal curve (stronger in 2024, slightly slower in 2026).
- Segment, country, channel, seats, and plan are correlated.
- Churn hazard is higher for SMB, low usage, and the first three months; lower for annual and Enterprise.
- Seat and plan changes create expansion, contraction, upgrades, and downgrades.
- A subset of churned customers reactivate on a new subscription.
- Invoices follow billing interval; some recent invoices stay open; a few are void or uncollectible.
- Daily usage is sparse and drops before churn. A minority of accounts are chronic high-ticket.
- About 3% of customers have a missing industry.

Re-running the script overwrites `seeds/*.csv`. Committed seeds already match seed 42; you only need to regenerate if you change the generator.

## 9. Install from a clean checkout

Python 3.10+ (3.12 used here). Git is required for `dbt deps`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DBT_PROFILES_DIR="$PWD"
dbt deps
```

`profiles.yml` in the repo root points DuckDB at `data/oakwell.duckdb`. Keep `DBT_PROFILES_DIR` set for every dbt and MetricFlow command, or pass `--profiles-dir .`.

## 10. Build the warehouse

Seeds plus models:

```bash
export DBT_PROFILES_DIR="$PWD"
dbt seed
dbt run
```

Or in one step with tests:

```bash
dbt build
```

## 11. Run dbt

```bash
dbt parse          # compile the semantic manifest
dbt run            # models only
dbt docs generate  # optional
```

## 12. Run tests

```bash
dbt test
# or
dbt build
```

This project’s intended tests are uniqueness, not-null, accepted values, relationships, a unique combination of columns on monthly grains, and two singular tests: active customers have positive MRR, and the MRR bridge reconciles to the month-on-month change.

## 13. Validate the semantic layer

```bash
dbt parse
mf validate-configs
```

That checks YAML, the semantic graph, and that metrics/dimensions/entities resolve against DuckDB.

## 14. Query metrics through MetricFlow

```bash
mf list metrics

mf query --metrics revenue --start-time 2026-07-01 --end-time 2026-07-31 --decimals 2

mf query --metrics ending_mrr,active_customers \
  --start-time 2026-08-01 --end-time 2026-08-31 --decimals 2

mf query --metrics ending_mrr \
  --group-by customer_month__customer_segment \
  --start-time 2026-08-01 --end-time 2026-08-31 --decimals 2

mf query --metrics revenue \
  --where "{{ Dimension('invoice__country') }} = 'US'" \
  --start-time 2026-07-01 --end-time 2026-07-31 --decimals 2

mf query --metrics ending_mrr,new_mrr,churned_mrr,expansion_mrr \
  --group-by metric_time \
  --start-time 2026-03-01 --end-time 2026-08-31 \
  --order metric_time --decimals 2
```

## 15. Reproduce the ground-truth answers

Independent SQL against DuckDB is the source of expected numbers:

```bash
python scripts/compute_ground_truth.py --write   # regenerate JSON + Markdown
python scripts/compute_ground_truth.py --check   # compare warehouse to stored JSON
```

Artifacts:

- `validation/ground_truth.json` — machine-readable cases (26)
- `validation/ground_truth.md` — the same cases for humans
- `validation/questions.md` — 33 business questions, including ones without stored answers

End-to-end harness (build, tests, MetricFlow validation, representative queries, ground-truth check):

```bash
python scripts/validate.py
```

## Known limitations

- Billing is USD only; there is no FX book.
- Revenue is invoice-based collections, not ASC-606 monthly recognition of annual contracts. MRR is the recurring-value metric; do not treat invoice cash as MRR.
- Product usage is stored only on days with activity, at customer grain (not named-user grain).
- Customer segment is based on employee count at signup and does not slowly change.
- Tax is not modelled.
- There is no sales-opportunity pipeline; acquisition is a customer attribute.

## License

Project content in this repository is provided as-is for analytics-engineering use.
