with source as (
    select * from {{ source('raw', 'customers') }}
)
    
select
    customer_id::bigint as customer_id,
    customer_country::varchar as customer_country
from source
