# Voy — Analytics Engineer case study

A dbt project modelling subscription retention/cohort/churn for Voy's
take-home assessment.

Built as a standalone sandbox against its own free [Neon](https://neon.tech)
Postgres database — not tied to any company's Snowflake account, dbt Cloud
project, or GitHub org.

For the task brief, see `docs/dataset_README.md`.

## Status

Scaffold only, no models yet: repo structure, Neon connection, and raw
sources are wired up. Staging/core/marts modelling and the stakeholder-facing
visual are still to come.

## Stack

- **Database:** Neon (serverless Postgres, free tier)
- **Transformation:** dbt-core + `dbt-postgres`, in its own Python virtualenv
- **Linting:** `sqlfluff` (dbt templater, Postgres dialect) — config in `.sqlfluff`

## Repo structure

```
docs/             task brief notes + dataset schema
scripts/
  load_raw_data.py  loads the 3 case-study CSVs into Neon's raw schema
models/
  staging/        _sources.yml declaring the raw.* tables; staging models TBD
  core/           fct/dim tables (TBD)
  marts/          stakeholder-facing marts (TBD)
dbt_project.yml
profiles.yml      dbt connection profile — no secrets, reads from env vars
env.example.sh    template for the env vars profiles.yml + the loader need
```

## Setup

1. Python 3.11–3.13 (dbt-core doesn't support 3.14 yet):
   ```
   python3.13 -m venv .venv
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install dbt-postgres
   ```
2. `cp env.example.sh env.sh`, fill in the real Neon connection details and
   the path to the raw CSVs, then `source env.sh`.
3. Load the raw data: `.venv/bin/python scripts/load_raw_data.py`
4. `.venv/bin/dbt debug` to verify the connection, then `.venv/bin/dbt run`.

`env.sh` holds real credentials and is gitignored — never commit it.
