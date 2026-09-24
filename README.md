# Voy — Analytics Engineer case study

A dbt project modelling subscription retention/cohort/churn for Voy's
take-home assessment.

Built as a standalone sandbox against its own free
[BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox) project —
not tied to any company's Snowflake/BigQuery account, dbt Cloud project, or
GitHub org.

For the task brief, see `docs/dataset_README.md`.

## Status

Repo structure, BigQuery connection, raw sources, staging, core (customer/date
dimensions, subscription-period and active-span facts) and a first marts model
(`fct_customer_monthly_activity`) are in place. The stakeholder-facing visual
is still to come.

## Stack

- **Database:** [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
  (no billing account, no credit card — 10 GiB storage lifetime cap, 1 TiB
  query processing/month, tables auto-expire after 60 days of inactivity, DML
  blocked but `CREATE OR REPLACE TABLE ... AS SELECT` is fine)
- **Transformation:** dbt-core + `dbt-bigquery`, in its own Python virtualenv
- **Auth:** OAuth via `gcloud auth application-default login` — no key file
- **Linting:** `sqlfluff` (dbt templater, BigQuery dialect) — config in `.sqlfluff`

## Repo structure

```
docs/             task brief notes + dataset schema
scripts/
  load_raw_data.py  loads the 3 case-study CSVs into BigQuery's raw dataset
models/
  staging/        _sources.yml + one stg_ model/yml per raw source
  core/           dim_customer, dim_date, fct_customer_subscription_period,
                  fct_customer_active_span
  marts/          fct_customer_monthly_activity
packages.yml      dbt-labs/codegen, used to draft staging yml column docs
dbt_project.yml
profiles.yml      dbt connection profile — no secrets, reads from env vars
env.example.sh    template for the env vars profiles.yml + the loader need
```

## Setup

1. Python 3.11–3.13 (dbt-core doesn't support 3.14 yet):
   ```
   python3.13 -m venv .venv
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install dbt-bigquery
   .venv/bin/dbt deps
   ```
2. Install the gcloud CLI (`brew install --cask gcloud-cli`) and run
   `gcloud auth application-default login` once, in your own Google account.
3. `cp env.example.sh env.sh`, fill in your BigQuery sandbox project ID and
   the path to the raw CSVs, then `source env.sh`.
4. Load the raw data: `.venv/bin/python scripts/load_raw_data.py`
5. `.venv/bin/dbt debug` to verify the connection, then `.venv/bin/dbt run`.

`env.sh` holds your project ID (not a secret, but still local-only) and is
gitignored — never commit it.
