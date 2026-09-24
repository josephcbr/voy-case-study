with subscription_periods as (
    select
        customer_id,
        subscription_id,
        subscription_period_start_date as start_date,
        subscription_period_end_date as end_date
    from {{ ref('fct_customer_subscription_period') }}
),

customer_bounds as (
    select
        customer_id,
        min(start_date) as first_active_date
    from subscription_periods
    group by 1
),

-- a customer's month range runs from their first active month through
-- current_date's month, however long that is
customer_month_bounds as (
    select
        customer_id,
        first_active_date,
        date_trunc(first_active_date, month) as first_month,
        date_trunc({{ var('current_date') }}, month) as last_month
    from customer_bounds
),

months as (
    select distinct month_start_date, month_end_date
    from {{ ref('dim_date') }}
    where month_start_date <= date_trunc({{ var('current_date') }}, month)
),

customer_months as (
    select
        customer_month_bounds.customer_id,
        customer_month_bounds.first_active_date,
        customer_month_bounds.first_month,
        months.month_start_date,
        date_diff(months.month_end_date, months.month_start_date, day) + 1 as days_in_month
    from customer_month_bounds
    inner join months
        on months.month_start_date >= customer_month_bounds.first_month
       and months.month_start_date <= customer_month_bounds.last_month
),

-- explode each period to one row per active day via dim_date, then keep
-- only one row per (customer_id, day) so overlapping subscriptions on the
-- same day don't get double counted
exploded_days as (
    select
        subscription_periods.customer_id,
        dim_date.month_start_date
    from subscription_periods
    inner join {{ ref('dim_date') }} as dim_date
        on dim_date.date_day between subscription_periods.start_date and subscription_periods.end_date
    qualify row_number() over (
        partition by subscription_periods.customer_id, dim_date.date_day
        order by subscription_periods.subscription_id
    ) = 1
),

active_days_by_month as (
    select
        customer_id,
        month_start_date,
        count(*) as active_days
    from exploded_days
    group by 1, 2
),

final as (
    select
        customer_months.customer_id,
        customer_months.month_start_date,
        customer_months.first_active_date,
        customer_months.first_month as cohort_month,
        date_diff(customer_months.month_start_date, customer_months.first_month, month) as months_since_acquisition,
        coalesce(active_days_by_month.active_days, 0) as active_days,
        customer_months.days_in_month - coalesce(active_days_by_month.active_days, 0) as non_active_days,
        coalesce(active_days_by_month.active_days, 0) > 0 as is_active,
        customer_months.month_start_date = customer_months.first_month as is_acquisition,
        lag(coalesce(active_days_by_month.active_days, 0)) over (
            partition by customer_months.customer_id
            order by customer_months.month_start_date
        ) as prev_month_active_days
    from customer_months
    left join active_days_by_month
        on active_days_by_month.customer_id = customer_months.customer_id
       and active_days_by_month.month_start_date = customer_months.month_start_date
)

select
    final.customer_id,
    final.month_start_date,
    final.first_active_date,
    final.cohort_month,
    final.months_since_acquisition,
    dim_customer.customer_country,
    dim_customer.taxonomy_business_category_group,
    final.active_days,
    final.non_active_days,
    final.is_active,
    final.is_acquisition,
    (final.is_active and not final.is_acquisition and final.prev_month_active_days = 0) as is_reactivation,
    (not final.is_active and final.prev_month_active_days > 0) as is_churn
from final
left join {{ ref('dim_customer') }} as dim_customer
    on dim_customer.customer_id = final.customer_id
