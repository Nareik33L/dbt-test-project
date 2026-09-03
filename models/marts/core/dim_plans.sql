select
    plan_id,
    plan_code,
    plan_name,
    plan_tier,
    list_price_monthly,
    billing_intervals,
    max_seats,
    includes_sso,
    includes_premium_support,
    includes_api_access
from {{ ref('stg_plans') }}
