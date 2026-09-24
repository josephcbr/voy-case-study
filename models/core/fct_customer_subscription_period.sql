with
subscriptions as (
    select
        customer_id,
        subscription_id,
        from_date as subscription_start_date,
        to_date as subscription_end_date
    from {{ ref('stg_activity') }}
),

--collapse repeated rows for subscription IDs with same start date to get subscription period
subscription_periods as (
    select
        customer_id,
        subscription_id,
        subscription_start_date,
        max(subscription_end_date) as subscription_end_date
    from subscriptions
    group by 1, 2, 3
)

select
    customer_id,
    subscription_id,
    subscription_start_date as subscription_period_start_date,
    subscription_end_date as subscription_period_end_date,
    min(subscription_start_date) over (
        partition by customer_id, subscription_id
    ) as subscription_start_date,
    row_number() over (
        partition by customer_id, subscription_id
        order by subscription_start_date
    ) as subscription_period
from subscription_periods
