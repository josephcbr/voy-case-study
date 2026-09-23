# Dataset notes

Source data for this case study lives outside the repo (see `RAW_DATA_DIR`
in `env.sh`) and is loaded into Neon by `scripts/load_raw_data.py`. It is not
committed here — the files are large (~95 MB combined) and are the
company's own case-study material, not this repo's content to publish.

## Files

- **customers.csv** (~533k rows) — `customer_id`, `customer_country`
- **activity.csv** (~2.18M rows) — `customer_id`, `subscription_id`,
  `from_date`, `to_date`. One row per subscription period; a customer can
  have multiple, possibly overlapping or gapped, periods.
- **acq_orders.csv** (~509k rows) — `customer_id`,
  `taxonomy_business_category_group`. Acquisition-channel taxonomy per
  customer.

## Brief (paraphrased)

Subscription business, retention-focused. The models should support:
retention over time, retention from a customer's initial cohort, churn and
acquisition metrics, drill-down by country/acquisition taxonomy/other
relational dimensions, and customer activity over a period. Output should be
analysis-ready (not necessarily a final reporting table). A customer's
"active" status doesn't depend on how many subscriptions they hold.
Submission = a GitHub repo of model logic + a visual representation of the
key outputs, aimed at a business-stakeholder audience.
