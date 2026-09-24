"""Load the case-study CSVs into BigQuery as raw tables.

Reads GCP_PROJECT_ID/BQ_LOCATION and the CSV folder from RAW_DATA_DIR (see
env.example.sh). Auth is via gcloud application-default credentials - run
`gcloud auth application-default login` once before this. Run with:

    source env.sh && .venv/bin/python scripts/load_raw_data.py
"""

import os
import pathlib

from google.cloud import bigquery

TABLES = {
    "customers": {
        "file": "customers.csv",
        "schema": [
            bigquery.SchemaField("customer_id", "INT64"),
            bigquery.SchemaField("customer_country", "STRING"),
        ],
    },
    "activity": {
        "file": "activity.csv",
        "schema": [
            bigquery.SchemaField("customer_id", "INT64"),
            bigquery.SchemaField("subscription_id", "INT64"),
            bigquery.SchemaField("from_date", "DATE"),
            bigquery.SchemaField("to_date", "DATE"),
        ],
    },
    "acq_orders": {
        "file": "acq_orders.csv",
        "schema": [
            bigquery.SchemaField("customer_id", "INT64"),
            bigquery.SchemaField("taxonomy_business_category_group", "STRING"),
        ],
    },
}


def main():
    raw_dir = pathlib.Path(os.environ["RAW_DATA_DIR"])
    project = os.environ["GCP_PROJECT_ID"]
    location = os.environ.get("BQ_LOCATION", "US")
    client = bigquery.Client(project=project, location=location)

    dataset_id = f"{project}.raw"
    client.create_dataset(bigquery.Dataset(dataset_id), exists_ok=True)

    for table, spec in TABLES.items():
        csv_path = raw_dir / spec["file"]
        table_id = f"{dataset_id}.{table}"
        job_config = bigquery.LoadJobConfig(
            schema=spec["schema"],
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        with open(csv_path, "rb") as f:
            job = client.load_table_from_file(f, table_id, job_config=job_config)
        job.result()
        table_ref = client.get_table(table_id)
        print(f"raw.{table}: loaded {table_ref.num_rows} rows from {csv_path.name}")


if __name__ == "__main__":
    main()
