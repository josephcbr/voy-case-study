with source as (
    select * from {{ source('raw', 'acq_orders') }}
)
select
    cast(customer_id as int64) as customer_id,
    cast(taxonomy_business_category_group as string) as taxonomy_business_category_group
from source
