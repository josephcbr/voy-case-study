with source as (
    select * from {{ source('raw', 'acq_orders') }}
)
select
    customer_id::bigint as customer_id,
    taxonomy_business_category_group::varchar as taxonomy_business_category_group
from source
