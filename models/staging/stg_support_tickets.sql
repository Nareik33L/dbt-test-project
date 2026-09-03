-- depends_on: {{ ref('raw_support_tickets') }}

with source as (

    select * from {{ source('oakwell_app', 'support_tickets') }}

),

renamed as (

    select
        cast(ticket_id as integer) as ticket_id,
        ticket_number,
        cast(customer_id as integer) as customer_id,
        {{ to_int('subscription_id') }} as subscription_id,
        {{ to_date('opened_at') }} as opened_at,
        {{ to_date('resolved_at') }} as resolved_at,
        status,
        category,
        priority,
        channel,
        nullif(assignee, '') as assignee,
        {{ to_int('first_response_hours') }} as first_response_hours,
        {{ to_int('csat_score') }} as csat_score
    from source

)

select * from renamed
