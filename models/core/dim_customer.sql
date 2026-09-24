with
customers as (
    select
        customer_id,
        customer_country
    from {{ ref('stg_customers') }}
),

acq as (
    select
        customer_id,
        taxonomy_business_category_group
    from {{ ref('stg_acq_orders') }}
),

subscriptions as (
    select
        customer_id,
        min(subscription_period_start_date) as customer_join_date,
        max(subscription_period_end_date) as latest_subscription_end_date
    from {{ ref('fct_customer_subscription_period') }}
    group by 1
)

select
    customers.customer_id,
    customers.customer_country,
    acq.taxonomy_business_category_group,
    subscriptions.customer_join_date,
    case
        when subscriptions.customer_join_date is null
            then 'Inactive'
        when {{ var('current_date') }} <= subscriptions.latest_subscription_end_date
            then 'Active'
        else 'Expired'
    end as customer_status
from customers
left join acq
    on customers.customer_id = acq.customer_id
left join subscriptions
    on customers.customer_id = subscriptions.customer_id
