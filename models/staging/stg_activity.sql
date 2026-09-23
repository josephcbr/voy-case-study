with source as (
    select * from {{ source('raw', 'activity') }}
)

select
    customer_id::bigint as customer_id,
    subscription_id::bigint as subscription_id,
    from_date::date as from_date,
    to_date::date as to_date
from source
