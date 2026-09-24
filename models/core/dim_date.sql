with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2015-01-01' as date)",
        end_date="cast('2030-01-01' as date)"
    ) }}
),

-- dbt_utils.date_spine builds date_day via dbt's cross-adapter dateadd macro,
-- which on BigQuery always returns DATETIME - cast to DATE immediately so
-- every expression below (date_trunc especially) operates on a real DATE
days as (
    select cast(date_day as date) as date_day
    from spine
),

final as (
    select
        date_day,
        cast(format_date('%u', date_day) as int64) as day_of_week,
        format_date('%A', date_day) as day_name,
        format_date('%u', date_day) in ('6', '7') as is_weekend,
        date_trunc(date_day, month) as month_start_date,
        date_sub(date_add(date_trunc(date_day, month), interval 1 month), interval 1 day) as month_end_date,
        format_date('%B', date_day) as month_name,
        date_trunc(date_day, quarter) as quarter_start_date,
        extract(year from date_day) as year_number
    from days
)

select * from final
