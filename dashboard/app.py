"""Voy subscription analytics dashboard.

Reads analytics.fct_customer_monthly_activity from BigQuery and charts
acquisition/retention/churn/reactivation rates over time.

Local dev: uses gcloud application-default credentials (no secrets needed).
Streamlit Cloud: reads a service account key from st.secrets["gcp_service_account"].
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT_ID = "voy-case-study"
TABLE = f"{PROJECT_ID}.analytics.fct_customer_monthly_activity"

# fixed hue order from the dataviz palette - never cycled, assigned by metric identity
METRIC_SPECS = [
    ("retention_rate", "Retention rate", "#2a78d6"),
    ("churn_rate", "Churn rate", "#eb6834"),
    ("acquisition_rate", "Acquisition rate", "#1baf7a"),
    ("reactivation_rate", "Reactivation rate", "#eda100"),
]

st.set_page_config(page_title="Voy Subscription Analytics", layout="wide")


@st.cache_resource
def get_client():
    try:
        has_service_account = "gcp_service_account" in st.secrets
    except Exception:
        # no secrets.toml at all - expected for local dev, which uses gcloud ADC instead
        has_service_account = False
    if has_service_account:
        credentials = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        return bigquery.Client(credentials=credentials, project=credentials.project_id, location="US")
    return bigquery.Client(project=PROJECT_ID, location="US")


@st.cache_data(ttl=3600)
def load_filter_options():
    client = get_client()
    df = client.query(f"""
        select distinct customer_country, taxonomy_business_category_group
        from `{TABLE}`
    """).to_dataframe()
    countries = sorted(df["customer_country"].dropna().unique().tolist())
    categories = sorted(df["taxonomy_business_category_group"].dropna().unique().tolist())
    min_month, max_month = client.query(f"""
        select min(month_start_date) as mn, max(month_start_date) as mx
        from `{TABLE}`
    """).to_dataframe().iloc[0][["mn", "mx"]]
    return countries, categories, min_month, max_month


@st.cache_data(ttl=3600)
def load_monthly(countries, categories, month_start, month_end):
    client = get_client()
    clauses = ["month_start_date between @month_start and @month_end"]
    params = [
        bigquery.ScalarQueryParameter("month_start", "DATE", month_start),
        bigquery.ScalarQueryParameter("month_end", "DATE", month_end),
    ]
    if countries:
        clauses.append("customer_country in unnest(@countries)")
        params.append(bigquery.ArrayQueryParameter("countries", "STRING", list(countries)))
    if categories:
        clauses.append("taxonomy_business_category_group in unnest(@categories)")
        params.append(bigquery.ArrayQueryParameter("categories", "STRING", list(categories)))

    query = f"""
        select
            month_start_date,
            countif(is_active) as active_customers,
            countif(is_acquisition) as new_customers,
            countif(is_reactivation) as reactivated_customers,
            countif(is_churn) as churned_customers
        from `{TABLE}`
        where {" and ".join(clauses)}
        group by 1
        order by 1
    """
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    df = client.query(query, job_config=job_config).to_dataframe()
    df["month_start_date"] = pd.to_datetime(df["month_start_date"])

    prior_active = df["active_customers"].shift(1)
    continuing = df["active_customers"] - df["new_customers"] - df["reactivated_customers"]
    df["retention_rate"] = continuing / prior_active
    df["churn_rate"] = df["churned_customers"] / prior_active
    df["acquisition_rate"] = df["new_customers"] / df["active_customers"]
    df["reactivation_rate"] = df["reactivated_customers"] / df["active_customers"]
    return df


st.title("Voy Subscription Analytics")

countries_all, categories_all, min_month, max_month = load_filter_options()

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
with filter_col1:
    selected_countries = st.multiselect("Country", countries_all)
with filter_col2:
    selected_categories = st.multiselect("Acquisition category", categories_all)
with filter_col3:
    min_month_dt = pd.Timestamp(min_month).to_pydatetime()
    max_month_dt = pd.Timestamp(max_month).to_pydatetime()
    month_range = st.slider(
        "Month range",
        min_value=min_month_dt,
        max_value=max_month_dt,
        value=(min_month_dt, max_month_dt),
        format="YYYY-MM",
    )

df = load_monthly(
    tuple(selected_countries),
    tuple(selected_categories),
    month_range[0].date(),
    month_range[1].date(),
)

tab_trends, tab_detail = st.tabs(["Trends", "Monthly detail"])

with tab_trends:
    if df.empty:
        st.info("No data for the selected filters.")
    else:
        latest = df.iloc[-1]
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Active customers", f"{int(latest['active_customers']):,}")
        for col, (key, label, _) in zip((k2, k3, k4), METRIC_SPECS[:3]):
            value = latest[key]
            col.metric(label, f"{value * 100:.1f}%" if pd.notna(value) else "—")

        fig = go.Figure()
        for col, label, color in METRIC_SPECS:
            fig.add_trace(go.Scatter(
                x=df["month_start_date"],
                y=df[col] * 100,
                mode="lines",
                name=label,
                line=dict(width=2, color=color),
            ))
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Rate (%)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            margin=dict(t=60),
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("How these rates are defined"):
            st.markdown(
                "- **Retention rate** = customers active last month who are still "
                "active this month, as a % of last month's active customers.\n"
                "- **Churn rate** = customers active last month who are not active "
                "this month, as a % of last month's active customers "
                "(retention + churn = 100%).\n"
                "- **Acquisition rate** = customers active for the first time ever "
                "this month, as a % of this month's active customers.\n"
                "- **Reactivation rate** = customers returning after a gap of at "
                "least one full month, as a % of this month's active customers."
            )

with tab_detail:
    if df.empty:
        st.info("No data for the selected filters.")
    else:
        display_df = df.copy()
        display_df["month_start_date"] = display_df["month_start_date"].dt.strftime("%Y-%m")
        for key, _, _ in METRIC_SPECS:
            display_df[key] = (display_df[key] * 100).round(1)
        display_df = display_df.rename(columns={
            "month_start_date": "Month",
            "active_customers": "Active customers",
            "new_customers": "New customers",
            "reactivated_customers": "Reactivated customers",
            "churned_customers": "Churned customers",
            "retention_rate": "Retention rate (%)",
            "churn_rate": "Churn rate (%)",
            "acquisition_rate": "Acquisition rate (%)",
            "reactivation_rate": "Reactivation rate (%)",
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)
