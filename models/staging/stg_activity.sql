with source as (
    select * from {{ source('raw', 'activity') }}
)

select
    cast(customer_id as int64) as customer_id,
    cast(subscription_id as int64) as subscription_id,
    cast(from_date as date) as from_date,
    cast(to_date as date) as to_date
from source
