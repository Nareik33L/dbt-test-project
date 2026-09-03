{% macro to_date(expr) %}
try_cast(nullif(trim(cast({{ expr }} as varchar)), '') as date)
{% endmacro %}

{% macro to_int(expr) %}
try_cast(nullif(trim(cast({{ expr }} as varchar)), '') as integer)
{% endmacro %}

{% macro to_bool(expr) %}
lower(trim(cast({{ expr }} as varchar))) in ('true', 't', '1')
{% endmacro %}
