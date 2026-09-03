with customers as (

    select * from {{ ref('stg_customers') }}

),

subscriptions as (

    select * from {{ ref('stg_subscriptions') }}

),

plans as (

    select * from {{ ref('stg_plans') }}

),

invoices as (

    select
        customer_id,
        sum(case when status = 'paid' then total_amount else 0 end) as lifetime_paid_revenue,
        count(*) as invoice_count
    from {{ ref('stg_invoices') }}
    group by 1

),

current_sub as (

    select
        subscriptions.*,
        plans.plan_name as current_plan_name,
        plans.plan_code as current_plan_code,
        row_number() over (
            partition by subscriptions.customer_id
            order by
                case when subscriptions.status = 'active' then 0 else 1 end,
                subscriptions.started_at desc,
                subscriptions.subscription_id desc
        ) as rn
    from subscriptions
    left join plans
        on subscriptions.plan_id = plans.plan_id

),

first_sub as (

    select
        customer_id,
        min(started_at) as first_subscription_date
    from subscriptions
    group by 1

)

select
    customers.customer_id,
    customers.customer_code,
    customers.organisation_name,
    customers.country_code,
    customers.country_name,
    customers.region,
    customers.subregion,
    coalesce(customers.industry, 'unknown') as industry,
    customers.industry is null as is_industry_missing,
    customers.employee_count,
    customers.segment,
    customers.acquisition_channel,
    customers.signup_date,
    customers.trial_start_date,
    customers.status as customer_status,
    customers.trial_start_date is not null as had_trial,
    current_sub.subscription_id as current_subscription_id,
    current_sub.current_plan_code,
    current_sub.current_plan_name,
    current_sub.billing_interval as current_billing_interval,
    current_sub.seats as current_seats,
    case
        when current_sub.status = 'active' then current_sub.mrr
        else 0
    end as current_mrr,
    current_sub.status as current_subscription_status,
    first_sub.first_subscription_date,
    coalesce(invoices.lifetime_paid_revenue, 0) as lifetime_paid_revenue,
    coalesce(invoices.invoice_count, 0) as invoice_count,
    customers.segment = 'Enterprise' as is_enterprise,
    customers.employee_count >= 500 as is_large_organisation
from customers
left join current_sub
    on customers.customer_id = current_sub.customer_id
   and current_sub.rn = 1
left join first_sub
    on customers.customer_id = first_sub.customer_id
left join invoices
    on customers.customer_id = invoices.customer_id
