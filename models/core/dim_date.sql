with spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2015-01-01' as date)",
        end_date="cast('2030-01-01' as date)"
    ) }}
),

final as (
    select
        date_day::date as date_day,
        extract(isodow from date_day)::int as day_of_week,
        trim(to_char(date_day, 'Day')) as day_name,
        extract(isodow from date_day) in (6, 7) as is_weekend,
        date_trunc('month', date_day)::date as month_start_date,
        trim(to_char(date_day, 'Month')) as month_name,
        date_trunc('quarter', date_day)::date as quarter_start_date,
        extract(year from date_day)::int as year_number
    from spine
)

select * from final
