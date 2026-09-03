-- depends_on: {{ ref('raw_trials') }}

with source as (

    select * from {{ source('oakwell_app', 'trials') }}

),

renamed as (

    select
        cast(trial_id as integer) as trial_id,
        cast(customer_id as integer) as customer_id,
        {{ to_date('trial_start_date') }} as trial_start_date,
        {{ to_date('trial_end_date') }} as trial_end_date,
        {{ to_bool('converted') }} as is_converted,
        {{ to_date('converted_at') }} as converted_at,
        acquisition_channel
    from source

)

select * from renamed
