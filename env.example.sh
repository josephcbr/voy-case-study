# Copy this file to env.sh, fill in the real values, then run: source env.sh
# env.sh is gitignored — never commit real credentials.
# No password/key lives here - auth is via `gcloud auth application-default login`.

export DBT_PROFILES_DIR="$(pwd)"

export GCP_PROJECT_ID="your-sandbox-project-id"
export BQ_DATASET="analytics"
export BQ_LOCATION="US"

# Folder holding the raw case-study CSVs (customers.csv, activity.csv, acq_orders.csv),
# read by scripts/load_raw_data.py. Not part of this repo.
export RAW_DATA_DIR="$HOME/Downloads/Analytics Engineering/data"
