with tickets as (

    select * from {{ ref('stg_support_tickets') }}

),

customers as (

    select
        customer_id,
        country_code,
        region,
        segment,
        acquisition_channel,
        customer_status
    from {{ ref('dim_customers') }}

)

select
    tickets.ticket_id,
    tickets.ticket_number,
    tickets.customer_id,
    tickets.subscription_id,
    tickets.opened_at,
    tickets.resolved_at,
    tickets.status as ticket_status,
    tickets.category,
    tickets.priority,
    tickets.channel as ticket_channel,
    tickets.assignee,
    tickets.first_response_hours,
    tickets.csat_score,
    case when tickets.status in ('solved', 'closed') then 1 else 0 end as is_resolved,
    case when tickets.resolved_at is not null
        then datediff('day', tickets.opened_at, tickets.resolved_at)
    end as resolution_days,
    case when tickets.priority in ('high', 'urgent') then 1 else 0 end as is_high_priority,
    customers.country_code,
    customers.region,
    customers.segment,
    customers.acquisition_channel,
    customers.customer_status
from tickets
left join customers
    on tickets.customer_id = customers.customer_id
