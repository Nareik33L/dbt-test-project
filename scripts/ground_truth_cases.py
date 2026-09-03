"""Ground-truth analytical cases for the Oakwell warehouse.

Each case has independent DuckDB SQL. Optional MetricFlow query parameters are
recorded so the same question can be asked through the semantic layer. Run:

    python scripts/compute_ground_truth.py --write
    python scripts/compute_ground_truth.py --check
"""

from __future__ import annotations

CASES = [
    {
        "id": "GT-001",
        "question": "What was collected revenue in July 2026?",
        "concept": "revenue",
        "time_period": {"start": "2026-07-01", "end": "2026-07-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(paid_amount), 2) as value
            from fct_invoices
            where invoice_date between date '2026-07-01' and date '2026-07-31'
        """,
        "mf": {
            "metrics": ["revenue"],
            "start_time": "2026-07-01",
            "end_time": "2026-07-31",
        },
    },
    {
        "id": "GT-002",
        "question": "What was ending MRR as of August 2026?",
        "concept": "ending_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(ending_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["ending_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-003",
        "question": "How many customers had positive ending MRR in August 2026?",
        "concept": "active_customers",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select sum(is_active) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["active_customers"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-004",
        "question": "What was ending ARR as of August 2026?",
        "concept": "ending_arr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(ending_arr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["ending_arr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-005",
        "question": "Which customer segments generated the most ending MRR in August 2026?",
        "concept": "ending_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": ["customer_segment"],
        "filters": [],
        "result_type": "table",
        "tolerance": 0.01,
        "sql": """
            select
                segment as customer_segment,
                round(sum(ending_mrr), 2) as ending_mrr
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
            group by 1
            order by 2 desc
        """,
        "mf": {
            "metrics": ["ending_mrr"],
            "group_by": ["customer_month__customer_segment"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-006",
        "question": "How much collected revenue came from United States customers in July 2026?",
        "concept": "revenue",
        "time_period": {"start": "2026-07-01", "end": "2026-07-31", "grain": "month"},
        "dimensions": [],
        "filters": [{"dimension": "country", "op": "=", "value": "US"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(paid_amount), 2) as value
            from fct_invoices
            where invoice_date between date '2026-07-01' and date '2026-07-31'
              and country_code = 'US'
        """,
        "mf": {
            "metrics": ["revenue"],
            "start_time": "2026-07-01",
            "end_time": "2026-07-31",
            "where": "{{ Dimension('invoice__country') }} = 'US'",
        },
    },
    {
        "id": "GT-007",
        "question": "How much new MRR was added in August 2026?",
        "concept": "new_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(new_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["new_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-008",
        "question": "How much expansion MRR was recognised in August 2026?",
        "concept": "expansion_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(expansion_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["expansion_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-009",
        "question": "How much MRR did we lose to contraction in August 2026?",
        "concept": "contraction_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(contraction_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["contraction_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-010",
        "question": "How much MRR was lost to churn in August 2026?",
        "concept": "churned_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(churned_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["churned_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-011",
        "question": "How many customers churned in August 2026?",
        "concept": "churned_customers",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select sum(is_churned_customer) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["churned_customers"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-012",
        "question": "How many new paying customers were added in August 2026?",
        "concept": "new_customers",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select sum(is_new_customer) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["new_customers"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-013",
        "question": "What was net new MRR in August 2026?",
        "concept": "net_new_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(
                sum(new_mrr + expansion_mrr + reactivation_mrr - contraction_mrr - churned_mrr),
                2
            ) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["net_new_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-014",
        "question": "What was ARPU in August 2026?",
        "concept": "arpu",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(ending_mrr) / nullif(sum(is_active), 0), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
        """,
        "mf": {
            "metrics": ["arpu"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-015",
        "question": "How many support tickets were opened in Q2 2026?",
        "concept": "support_tickets",
        "time_period": {"start": "2026-04-01", "end": "2026-06-30", "grain": "quarter"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select count(*) as value
            from fct_support_tickets
            where opened_at between date '2026-04-01' and date '2026-06-30'
        """,
        "mf": {
            "metrics": ["support_tickets"],
            "start_time": "2026-04-01",
            "end_time": "2026-06-30",
        },
    },
    {
        "id": "GT-016",
        "question": "How did Q2 2026 support tickets break down by category?",
        "concept": "support_tickets",
        "time_period": {"start": "2026-04-01", "end": "2026-06-30", "grain": "quarter"},
        "dimensions": ["ticket_category"],
        "filters": [],
        "result_type": "table",
        "tolerance": 0.0,
        "sql": """
            select
                category as ticket_category,
                count(*) as support_tickets
            from fct_support_tickets
            where opened_at between date '2026-04-01' and date '2026-06-30'
            group by 1
            order by 1
        """,
        "mf": {
            "metrics": ["support_tickets"],
            "group_by": ["ticket__ticket_category"],
            "start_time": "2026-04-01",
            "end_time": "2026-06-30",
        },
    },
    {
        "id": "GT-017",
        "question": "What share of trials started in 2025 converted to paid?",
        "concept": "trial_conversion_rate",
        "time_period": {"start": "2025-01-01", "end": "2025-12-31", "grain": "year"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0001,
        "sql": """
            select round(sum(converted_count)::double / nullif(count(*), 0), 4) as value
            from fct_trials
            where trial_start_date between date '2025-01-01' and date '2025-12-31'
        """,
        "mf": {
            "metrics": ["trial_conversion_rate"],
            "start_time": "2025-01-01",
            "end_time": "2025-12-31",
        },
    },
    {
        "id": "GT-018",
        "question": "How many invoices were paid in the first half of 2026?",
        "concept": "paid_invoice_count",
        "time_period": {"start": "2026-01-01", "end": "2026-06-30", "grain": "half"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select sum(is_paid) as value
            from fct_invoices
            where invoice_date between date '2026-01-01' and date '2026-06-30'
        """,
        "mf": {
            "metrics": ["paid_invoice_count"],
            "start_time": "2026-01-01",
            "end_time": "2026-06-30",
        },
    },
    {
        "id": "GT-019",
        "question": "What was the average paid invoice value in July 2026?",
        "concept": "average_invoice_value",
        "time_period": {"start": "2026-07-01", "end": "2026-07-31", "grain": "month"},
        "dimensions": [],
        "filters": [{"dimension": "invoice_status", "op": "=", "value": "paid"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(avg(total_amount), 2) as value
            from fct_invoices
            where invoice_date between date '2026-07-01' and date '2026-07-31'
              and invoice_status = 'paid'
        """,
        "mf": {
            "metrics": ["average_invoice_value"],
            "start_time": "2026-07-01",
            "end_time": "2026-07-31",
        },
    },
    {
        "id": "GT-020",
        "question": "How many work items were completed in August 2026?",
        "concept": "work_items_completed",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [],
        "result_type": "scalar",
        "tolerance": 0.0,
        "sql": """
            select sum(work_items_completed) as value
            from fct_product_usage_daily
            where usage_date between date '2026-08-01' and date '2026-08-31'
        """,
        "mf": {
            "metrics": ["work_items_completed"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-021",
        "question": "What was Enterprise ending MRR in August 2026?",
        "concept": "enterprise_ending_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [{"dimension": "customer_segment", "op": "=", "value": "Enterprise"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(ending_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
              and segment = 'Enterprise'
        """,
        "mf": {
            "metrics": ["enterprise_ending_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-022",
        "question": "How much collected revenue in 2026 came from invoices of $2,000 or more?",
        "concept": "large_invoice_revenue",
        "time_period": {"start": "2026-01-01", "end": "2026-08-31", "grain": "ytd"},
        "dimensions": [],
        "filters": [{"dimension": "invoice_size_tier", "op": "=", "value": "large"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(paid_amount), 2) as value
            from fct_invoices
            where invoice_date between date '2026-01-01' and date '2026-08-31'
              and invoice_size_tier = 'large'
        """,
        "mf": {
            "metrics": ["large_invoice_revenue"],
            "start_time": "2026-01-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-023",
        "question": "What is the outstanding amount on open invoices?",
        "concept": "open_invoice_amount",
        "time_period": {"start": "2022-07-01", "end": "2026-08-31", "grain": "all_time"},
        "dimensions": [],
        "filters": [{"dimension": "invoice_status", "op": "=", "value": "open"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(total_amount), 2) as value
            from fct_invoices
            where invoice_status = 'open'
        """,
        "mf": {
            "metrics": ["open_invoice_amount"],
            "start_time": "2022-07-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-024",
        "question": "How much paid subscription line-item revenue was recognised in July 2026?",
        "concept": "subscription_revenue",
        "time_period": {"start": "2026-07-01", "end": "2026-07-31", "grain": "month"},
        "dimensions": [],
        "filters": [{"dimension": "item_type", "op": "=", "value": "subscription"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(paid_amount), 2) as value
            from fct_invoice_items
            where invoice_date between date '2026-07-01' and date '2026-07-31'
              and item_type = 'subscription'
        """,
        "mf": {
            "metrics": ["subscription_revenue"],
            "start_time": "2026-07-01",
            "end_time": "2026-07-31",
        },
    },
    {
        "id": "GT-025",
        "question": "What was ending MRR from self-serve acquired customers in August 2026?",
        "concept": "self_serve_ending_mrr",
        "time_period": {"start": "2026-08-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": [],
        "filters": [{"dimension": "acquisition_channel", "op": "=", "value": "self_serve"}],
        "result_type": "scalar",
        "tolerance": 0.01,
        "sql": """
            select round(sum(ending_mrr), 2) as value
            from fct_mrr_snapshot
            where month_start = date '2026-08-01'
              and acquisition_channel = 'self_serve'
        """,
        "mf": {
            "metrics": ["self_serve_ending_mrr"],
            "start_time": "2026-08-01",
            "end_time": "2026-08-31",
        },
    },
    {
        "id": "GT-026",
        "question": "How has ending MRR changed month by month from March to August 2026?",
        "concept": "ending_mrr",
        "time_period": {"start": "2026-03-01", "end": "2026-08-31", "grain": "month"},
        "dimensions": ["month_start"],
        "filters": [],
        "result_type": "table",
        "tolerance": 0.01,
        "sql": """
            select
                month_start,
                round(sum(ending_mrr), 2) as ending_mrr
            from fct_mrr_snapshot
            where month_start between date '2026-03-01' and date '2026-08-01'
            group by 1
            order by 1
        """,
        "mf": {
            "metrics": ["ending_mrr"],
            "group_by": ["metric_time"],
            "start_time": "2026-03-01",
            "end_time": "2026-08-31",
        },
    },
]
