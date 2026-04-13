"""
data_loader.py
Loads the star-schema CSVs and exposes cached, joined DataFrames
for use across all Streamlit tabs.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

# ── paths ─────────────────────────────────────────────────────────────────────
_CSV_DIR = Path(__file__).parent.parent / "data" / "csv"


def _csv(name: str) -> Path:
    return _CSV_DIR / name


# ── raw dimension / fact loaders ──────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_fact() -> pd.DataFrame:
    df = pd.read_csv(_csv("Fact_Transactions.csv"), parse_dates=["transaction_date"])
    return df


@st.cache_data(show_spinner=False)
def load_dim_customer() -> pd.DataFrame:
    return pd.read_csv(_csv("Dim_Customer.csv"))


@st.cache_data(show_spinner=False)
def load_dim_branch() -> pd.DataFrame:
    return pd.read_csv(_csv("Dim_Branch.csv"))


@st.cache_data(show_spinner=False)
def load_dim_date() -> pd.DataFrame:
    df = pd.read_csv(_csv("Dim_Date.csv"), parse_dates=["full_date"])
    return df


@st.cache_data(show_spinner=False)
def load_dim_product() -> pd.DataFrame:
    return pd.read_csv(_csv("Dim_Product.csv"))


@st.cache_data(show_spinner=False)
def load_dim_channel() -> pd.DataFrame:
    return pd.read_csv(_csv("Dim_Channel.csv"))


# ── enriched / joined views ───────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_enriched() -> pd.DataFrame:
    """Fact joined with date dimension for time-series analysis."""
    fact = load_fact()
    dim_date = load_dim_date()
    enriched = fact.merge(
        dim_date[["date_id", "year", "quarter", "month", "month_name", "day_of_week", "is_weekend"]],
        on="date_id",
        how="left",
    )
    enriched["year_month"] = enriched["transaction_date"].dt.to_period("M").astype(str)
    return enriched


# ── pre-aggregated metrics ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def kpi_summary(df: pd.DataFrame) -> dict:
    """Top-level KPIs for the Executive Summary tab."""
    total_txns = len(df)
    total_revenue = df["revenue"].sum()
    avg_txn_value = df["amount"].mean()
    digital_rate = df["channel"].isin(["mobile_app", "online_banking"]).mean()
    unique_customers = df["customer_id"].nunique()
    return {
        "total_transactions": total_txns,
        "total_revenue": total_revenue,
        "avg_transaction_value": avg_txn_value,
        "digital_adoption_rate": digital_rate,
        "unique_customers": unique_customers,
    }


@st.cache_data(show_spinner=False)
def monthly_volume(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("year_month")
        .agg(transaction_count=("transaction_id", "count"), total_amount=("amount", "sum"))
        .reset_index()
        .sort_values("year_month")
    )


@st.cache_data(show_spinner=False)
def revenue_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("product_line")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


@st.cache_data(show_spinner=False)
def avg_value_by_channel(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("channel")["amount"]
        .mean()
        .reset_index()
        .rename(columns={"amount": "avg_amount"})
        .sort_values("avg_amount", ascending=False)
    )


@st.cache_data(show_spinner=False)
def digital_adoption_trend(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    df2["is_digital"] = df2["channel"].isin(["mobile_app", "online_banking"])
    return (
        df2.groupby("year_month")
        .agg(
            total=("transaction_id", "count"),
            digital=("is_digital", "sum"),
        )
        .reset_index()
        .assign(digital_rate=lambda x: x["digital"] / x["total"])
        .sort_values("year_month")
    )


@st.cache_data(show_spinner=False)
def txn_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("transaction_type")
        .agg(count=("transaction_id", "count"), total_amount=("amount", "sum"))
        .reset_index()
    )


@st.cache_data(show_spinner=False)
def segment_clv(df: pd.DataFrame) -> pd.DataFrame:
    """CLV proxy and avg balance per customer, joined to segment."""
    dim_customer = load_dim_customer()
    return dim_customer[["customer_id", "customer_segment", "avg_balance", "clv_proxy", "tenure_months"]]


@st.cache_data(show_spinner=False)
def branch_performance(df: pd.DataFrame) -> pd.DataFrame:
    return load_dim_branch().sort_values("branch_efficiency_score", ascending=False)


@st.cache_data(show_spinner=False)
def region_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region")
        .agg(total_revenue=("revenue", "sum"), transaction_count=("transaction_id", "count"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )


@st.cache_data(show_spinner=False)
def heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transaction count by day-of-week × month (for heatmap)."""
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = (
        df.groupby(["day_of_week", "month_name"])["transaction_id"]
        .count()
        .reset_index(name="count")
    )
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    pivot["day_of_week"] = pd.Categorical(pivot["day_of_week"], categories=dow_order, ordered=True)
    pivot["month_name"] = pd.Categorical(pivot["month_name"], categories=month_order, ordered=True)
    return pivot.sort_values(["day_of_week", "month_name"])
