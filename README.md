# Voy — Analytics Engineer case study

A dbt project modelling subscription retention, cohorts, churn, and
acquisition for Voy's take-home assessment, plus a Streamlit dashboard for
the outputs.

Built as a standalone project against its own free
[BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)

## Links

- **Live dashboard:** https://voy-case-study-pg22d3aqmurta8uj2muc9f.streamlit.app/
- **Public dataset (BigQuery console):** https://console.cloud.google.com/bigquery?project=voy-case-study&d=analytics&p=voy-case-study&page=dataset
  — the `analytics` dataset is readable by any signed-in Google account. Open
  a table and use the Preview tab to browse without running a query, or run
  your own query under your own GCP project.
- **Approach write-up** (the case-study questions, answered): [`docs/approach.md`](docs/approach.md)
- **Task brief and dataset notes:** [`docs/dataset_README.md`](docs/dataset_README.md)

## Status

Staging, core (customer/date dimensions, subscription-period fact), one
marts model (`fct_customer_monthly_activity`), and the dashboard are all
built and live.

## Stack

- **Database:** [BigQuery sandbox](https://cloud.google.com/bigquery/docs/sandbox)
- **Transformation:** dbt-core + `dbt-bigquery`, in its own Python virtualenv
- **Auth:** OAuth via `gcloud auth application-default login` — no key file
- **Dashboard:** Streamlit + Plotly, deployed on Streamlit Community Cloud,
  reading `analytics.fct_customer_monthly_activity` with a read-only service
  account
- **Linting:** `sqlfluff` (dbt templater, BigQuery dialect) — config in `.sqlfluff`

## Repo structure

```
docs/
  dataset_README.md   task brief + dataset schema notes
  approach.md          write-up: modelling approach, decisions, how it answers the brief
dashboard/
  app.py               Streamlit dashboard (reads the mart, not raw/staging/core)
  requirements.txt
scripts/
  load_raw_data.py     loads the 3 case-study CSVs into BigQuery's raw dataset
models/
  staging/             _sources.yml + one stg_ model/yml per raw source
  core/                dim_customer, dim_date, fct_customer_subscription_period
  marts/                fct_customer_monthly_activity
packages.yml           dbt-labs/codegen, used to draft yml column docs
dbt_project.yml         vars: current_date (frozen "as of" date for the whole build)
profiles.yml            dbt connection profile — no secrets, reads from env vars
env.example.sh          template for the env vars profiles.yml + the loader need
```

## Setup — run the models yourself

Write access to the `voy-case-study` GCP project is private. To rebuild or
modify the models, point this same code at your **own** free BigQuery
sandbox project instead:

1. Python 3.11–3.13 (dbt-core doesn't support 3.14 yet):
   ```
   python3.13 -m venv .venv
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install dbt-bigquery
   .venv/bin/dbt deps
   ```
2. Create your own sandbox project at
   [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
   (personal Google account, no billing needed), then note its project ID.
3. Install the gcloud CLI (`brew install --cask gcloud-cli`) and run
   `gcloud auth application-default login` once, in that same account.
4. Get the 3 raw case-study CSVs (`customers.csv`, `activity.csv`,
   `acq_orders.csv`) — they're Voy's own case-study material and aren't
   committed to this repo (see `docs/dataset_README.md`). Ask the project
   owner if you don't already have them.
5. `cp env.example.sh env.sh`, fill in your project ID and the path to the
   raw CSVs, then `source env.sh`.
6. Load the raw data: `.venv/bin/python scripts/load_raw_data.py`
7. `.venv/bin/dbt debug` to verify the connection, then `.venv/bin/dbt run`
   and `.venv/bin/dbt test`.

`env.sh` holds your project ID (not a secret, but still local-only) and is
gitignored — never commit it.

### Running the dashboard locally

```
cd dashboard
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
source ../env.sh
.venv/bin/streamlit run app.py
```

Locally it authenticates the same way as dbt (`gcloud` ADC). The deployed
version on Streamlit Cloud instead reads a read-only service account key
from Streamlit's own secrets manager — see `dashboard/app.py` for the
fallback logic.
