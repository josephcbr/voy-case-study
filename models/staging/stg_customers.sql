with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    cast(customer_id as int64) as customer_id,
    cast(customer_country as string) as customer_country
from source
