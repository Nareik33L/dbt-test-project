-- depends_on: {{ ref('raw_customers') }}

with source as (

    select * from {{ source('oakwell_app', 'customers') }}

),

renamed as (

    select
        cast(customer_id as integer) as customer_id,
        customer_code,
        organisation_name,
        country_code,
        country_name,
        region,
        subregion,
        nullif(industry, '') as industry,
        cast(employee_count as integer) as employee_count,
        segment,
        acquisition_channel,
        {{ to_date('signup_date') }} as signup_date,
        {{ to_date('trial_start_date') }} as trial_start_date,
        status
    from source

)

select * from renamed
