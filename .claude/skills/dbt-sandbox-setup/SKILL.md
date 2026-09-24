---
name: dbt-sandbox-setup
description: Set up and run this dbt + BigQuery sandbox from a fresh clone - create the Python venv, install dbt-bigquery, authenticate gcloud, and load the raw data. Use whenever someone has just cloned this repo and wants dbt working locally against the sandbox project, or asks to "set up" or "run" this project.
---

# dbt sandbox setup

This repo is a standalone dbt project connected to its own BigQuery sandbox
project (see the root `README.md` for background). Follow these steps in
order from the repo root. Stop and report back if a step fails - don't guess
past an error.

Always call the venv's `dbt` binary directly (`.venv/bin/dbt ...`) rather than
a bare `dbt`, in case the machine has some other `dbt` shell alias or function
defined elsewhere.

1. **Check Python version.** dbt-core does not yet support Python 3.14. Look
   for 3.11, 3.12, or 3.13, e.g. `python3.13 --version`. If none of those
   exist, tell the user to install one (e.g. `brew install python@3.13`)
   rather than falling back to an unsupported version.

2. **Create and activate a project-local venv, install dbt:**
   ```
   python3.13 -m venv .venv
   .venv/bin/pip install --upgrade pip
   .venv/bin/pip install dbt-bigquery
   .venv/bin/dbt deps
   ```
   Skip this if `.venv/bin/dbt` already exists and works.

3. **Check gcloud auth.**
   - Check `gcloud auth application-default print-access-token` works. If not,
     ask the user to run `gcloud auth application-default login` themselves
     (opens a browser to their Google account) - never do this on their behalf.
   - Auth is OAuth-based; there is no key file to manage or gitignore.

4. **Set up project config.**
   - If `env.sh` already exists in the repo root, just read it and move on.
   - If it doesn't exist, copy `env.example.sh` to `env.sh`, then ask the user
     for their GCP sandbox project ID and the path to the raw CSVs
     (`RAW_DATA_DIR`). Never invent a placeholder project ID - ask if you
     don't have it. Fill the real values into `env.sh`.
   - `env.sh` is gitignored. Never commit it.

5. **Verify the connection:**
   ```
   source env.sh && .venv/bin/dbt debug
   ```
   If this fails, check that the project ID is correct and that
   `gcloud auth application-default login` has been run.

6. **Load the raw data:**
   ```
   source env.sh && .venv/bin/python scripts/load_raw_data.py
   ```
   Loads ~3.2M rows across 3 CSVs (customers, activity, acq_orders) into the
   `raw` dataset. The CSVs are large (~95 MB) - this can take a minute or two.

7. **Build the models:**
   ```
   source env.sh && .venv/bin/dbt run
   ```

8. **Run the tests:**
   ```
   source env.sh && .venv/bin/dbt test
   ```

9. **Report back** what got built, raw row counts, and the test pass/fail
   summary. Remind the user the sandbox has a lifetime 10 GiB storage cap and
   tables auto-expire after 60 days of inactivity.
