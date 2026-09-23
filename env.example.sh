# Copy this file to env.sh, fill in the real values, then run: source env.sh
# env.sh is gitignored — never commit real credentials.

export DBT_PROFILES_DIR="$(pwd)"

export PGHOST="ep-xxxxxxxx-pooler.c-2.us-east-2.aws.neon.tech"
export PGUSER="neondb_owner"
export PGPASSWORD="changeme"
export PGDATABASE="neondb"
export PGSCHEMA="analytics"

# Folder holding the raw case-study CSVs (customers.csv, activity.csv, acq_orders.csv),
# read by scripts/load_raw_data.py. Not part of this repo.
export RAW_DATA_DIR="$HOME/Downloads/Analytics Engineering/data"
