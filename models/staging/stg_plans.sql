-- depends_on: {{ ref('raw_plans') }}

with source as (

    select * from {{ source('oakwell_app', 'plans') }}

),

renamed as (

    select
        cast(plan_id as integer) as plan_id,
        plan_code,
        plan_name,
        cast(plan_tier as integer) as plan_tier,
        cast(list_price_monthly as double) as list_price_monthly,
        billing_intervals,
        {{ to_int('max_seats') }} as max_seats,
        {{ to_bool('includes_sso') }} as includes_sso,
        {{ to_bool('includes_premium_support') }} as includes_premium_support,
        {{ to_bool('includes_api_access') }} as includes_api_access
    from source

)

select * from renamed
