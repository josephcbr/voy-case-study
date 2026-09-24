# Approach

This document explains the modelling approach for the Voy case study.
See `docs/dataset_README.md` for the brief itself and the raw dataset schema.

## Architecture

The project follows three layers.

**Staging** (`stg_*`) cleans each raw source and casts field data types. It does not
join or apply business logic.

**Core** holds the reusable, source-of-truth entities: `dim_customer`,
`dim_date`, and `fct_customer_subscription_period`. These models answer "who
is this customer" and "when did they hold a subscription." They know
nothing about retention, cohorts, or churn. Any future question about this
data — an LTV model, a marketing-spend analysis, a support-triage
dashboard — should read from this layer, not from staging or raw.

**Marts** hold the retention-specific output: `fct_customer_monthly_activity`.
This is the model built to measure metrics around retention and acquisition
from the case study. It is built only from core models.

A stakeholder should use `fct_customer_monthly_activity` directly to answer
their use-case specific business questions, while the core layer underneath it is
generic to the business process and can feed other use cases as required.

## The mart

`fct_customer_monthly_activity` has one row per customer per calendar month,
from the customer's first active month through the current "as of" date
(`dbt_project.yml`'s `current_date` var — the whole build is frozen to a
fixed date, not wall-clock `today()`, since the source data is static).

That date is deliberately not the last date in the raw data. `activity.csv`
runs to 2024-08-16, but `current_date` is pinned to 2024-07-24 in order to 
simulate the use case of having subscriptions that run past the current
date. The data in the last 3 weeks of the dataset looks to behave differently
than the historic data, looking more like subscription snapshot data for 
active subscriptions. More detail is needed on how this data is generated
in order to decide if the method of combining the records for a subscription
ID with the same start date applies correctly to it.

Each row carries:

- `active_days` / `non_active_days` — days in the month the customer did or
  didn't hold an active subscription.
- `is_active` — `active_days > 0`.
- `is_acquisition` — true for the customer's first-ever active month.
- `is_reactivation` — true if this month is active, it is not the
  acquisition month, and the previous calendar month had zero active days.
  This is equivalent to "the customer's previous subscription ended at
  least 2 months before this one starts."
- `is_churn` — true if this month has zero active days and the previous
  month had active days. It fires exactly once per churn event, not on
  every subsequent dormant month.
- `cohort_month` / `first_active_date` / `months_since_acquisition` — cohort
  fields, described below.
- `customer_country` / `taxonomy_business_category_group` — denormalized
  from `dim_customer` to add customer details.

## Deduplicating concurrent subscriptions

In the raw data, 64% of customers hold two or more overlapping subscriptions 
at some point. The assumption the models make is that we focus on if a customer
has an active subscription on a particular day, and ignore how many active
subscriptions they have on that day.

The mart resolves this by joining each subscription period to `dim_date` (one
row per calendar day the period covers), then keeping exactly one row per
`(customer_id, day)` with `QUALIFY ROW_NUMBER() ... = 1`. Overlapping
subscriptions on the same day collapse to a single active day.

## Grain: monthly

A monthly grain was chosen to match common business and financial reporting
cadence. Subscription cycles are also monthly-shaped in the data (most renewal periods 
run 28–31 days), so this grain matches well with the subscription cycle.

Depending on the use case, it is also possible to create a day level grain (e.g. to 
track exact customer behaviour by day and to preserve a daily subscription history).
However, that should be weighed up against the storage and performance cost
in the database with the value the use case brings. In this simpler use case of
retention metrics, the trade-off isn't worth it.

## Cohorts

The brief asks for "retention from initial cohort" — the classic cohort
curve: of everyone acquired in month X, what fraction is still active N
months later.

To support slicing the population by cohort, we include three columns so no 
consumer has to re-derive them:

- `cohort_month` — the month bucket, for the standard monthly cohort curve.
- `months_since_acquisition` — the x-axis offset for that curve (0, 1, 2, ...).
- `first_active_date` — the actual acquisition date, at day precision, kept
  separate from `cohort_month`. If a weekly or daily cohort cut is ever
  needed, it can be built from this column without touching core or
  re-deriving anything upstream.

## Defining Churn and Retention

We define churn as being active (i.e. they have at least 1 day with an active
subscription in the month, but this definition can be created using a mix of
active vs non-active days) in the prevous month, but inactive in the
current month. Likewise, retention is defined as being active in the previous
month and also active in the current month. These are both measured as a 
percentage of the active base in the previous month.

## The dashboard

The Streamlit dashboard has 2 tabs and reads direcetly from the mart.
Trends shows the four rates (retention, churn, acquisition, reactivation) 
as a single-axis line chart over time, plus KPI tiles for the latest month. 
Monthly detail shows the same period as a table, for drill-down. The filter bar 
above both tabs filters by country, acquisition category, the month range 
shown, and the cohort month range. The cohort month range filter allows the
stakeholder to review the metrics of a particular cohort over their chosen
time period.

## Next Steps

The current setup is limited to the models and the dashboard for stakeholders
to use. While the .yml documentation gives descriptions of all the fields and
grain of the model, a semantic layer is a natural next step to create better
guardrails for models using the data. This can be built directly on top of 
the mart in order to define all the metrics, and also on the core models
directly, so that context is provided to the AI agent for use in other use
cases.
