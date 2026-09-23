"""Load the case-study CSVs into Neon as raw tables.

Reads connection details from PGHOST/PGUSER/PGPASSWORD/PGDATABASE/PGSCHEMA
and the CSV folder from RAW_DATA_DIR (see env.example.sh). Run with:

    source env.sh && .venv/bin/python scripts/load_raw_data.py
"""

import os
import pathlib

import psycopg2

TABLES = {
    "customers": {
        "file": "customers.csv",
        "columns": "customer_id bigint, customer_country text",
    },
    "activity": {
        "file": "activity.csv",
        "columns": (
            "customer_id bigint, subscription_id bigint, "
            "from_date date, to_date date"
        ),
    },
    "acq_orders": {
        "file": "acq_orders.csv",
        "columns": "customer_id bigint, taxonomy_business_category_group text",
    },
}


def main():
    raw_dir = pathlib.Path(os.environ["RAW_DATA_DIR"])
    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        dbname=os.environ["PGDATABASE"],
        port=os.environ.get("PGPORT", "5432"),
        sslmode="require",
    )
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            for table, spec in TABLES.items():
                csv_path = raw_dir / spec["file"]
                cur.execute(f"DROP TABLE IF EXISTS raw.{table};")
                cur.execute(f"CREATE TABLE raw.{table} ({spec['columns']});")
                with open(csv_path, encoding="utf-8") as f:
                    cur.copy_expert(
                        f"COPY raw.{table} FROM STDIN WITH (FORMAT csv, HEADER true)",
                        f,
                    )
                cur.execute(f"SELECT count(*) FROM raw.{table};")
                print(f"raw.{table}: loaded {cur.fetchone()[0]} rows from {csv_path.name}")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
