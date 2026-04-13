"""
app.py — BankLens: Banking Operations Analytics Platform
Run with: streamlit run src/app.py
"""

import streamlit as st

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="BankLens",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import (  # noqa: E402
    load_enriched,
    load_dim_customer,
    kpi_summary,
    monthly_volume,
    revenue_by_product,
    avg_value_by_channel,
    digital_adoption_trend,
    txn_type_distribution,
    branch_performance,
    region_revenue,
    heatmap_data,
)
import charts as ch  # noqa: E402

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 0.78rem; color: #64748B; }
    .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/64/bank.png", width=48)
    st.title("BankLens")
    st.caption("Banking Operations Analytics")

    st.divider()
    st.subheader("Filters")

    df_full = load_enriched()

    year_options = sorted(df_full["year"].unique().tolist())
    selected_years = st.multiselect("Year", year_options, default=year_options)

    region_options = sorted(df_full["region"].unique().tolist())
    selected_regions = st.multiselect("Region", region_options, default=region_options)

    segment_options = sorted(df_full["customer_segment"].unique().tolist())
    selected_segments = st.multiselect("Customer Segment", segment_options, default=segment_options)

    channel_options = sorted(df_full["channel"].unique().tolist())
    selected_channels = st.multiselect("Channel", channel_options, default=channel_options)

    st.divider()
    st.caption("Data: 2022 – 2024 | 100 K synthetic transactions")


# ── filter dataframe ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def filter_df(
    years: tuple,
    regions: tuple,
    segments: tuple,
    channels: tuple,
) -> pd.DataFrame:
    df = load_enriched()
    mask = (
        df["year"].isin(years)
        & df["region"].isin(regions)
        & df["customer_segment"].isin(segments)
        & df["channel"].isin(channels)
    )
    return df[mask].copy()


df = filter_df(
    tuple(selected_years),
    tuple(selected_regions),
    tuple(selected_segments),
    tuple(selected_channels),
)

if df.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar selections.")
    st.stop()

# ── tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Summary",
    "Transaction Trends",
    "Customer Segmentation",
    "Branch Performance",
    "Digital vs Physical",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Executive Summary")

    kpis = kpi_summary(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Transactions", f"{kpis['total_transactions']:,}")
    c2.metric("Total Revenue", f"£{kpis['total_revenue']:,.0f}")
    c3.metric("Avg Transaction", f"£{kpis['avg_transaction_value']:,.0f}")
    c4.metric("Digital Adoption", f"{kpis['digital_adoption_rate']:.1%}")
    c5.metric("Unique Customers", f"{kpis['unique_customers']:,}")

    st.divider()

    col_a, col_b = st.columns([3, 2])
    with col_a:
        mv = monthly_volume(df)
        st.plotly_chart(ch.monthly_volume_line(mv), use_container_width=True)
    with col_b:
        rp = revenue_by_product(df)
        st.plotly_chart(ch.revenue_by_product_bar(rp), use_container_width=True)

    col_c, col_d = st.columns([2, 3])
    with col_c:
        dim_cust = load_dim_customer()
        st.plotly_chart(ch.segment_pie(dim_cust), use_container_width=True)
    with col_d:
        td = txn_type_distribution(df)
        st.plotly_chart(ch.txn_type_bar(td), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRANSACTION TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Transaction Trends")

    # monthly breakdown by transaction type
    monthly_by_type = (
        df.groupby(["year_month", "transaction_type"])["transaction_id"]
        .count()
        .reset_index(name="transaction_count")
        .sort_values("year_month")
    )
    st.plotly_chart(ch.monthly_txn_type_area(monthly_by_type), use_container_width=True)

    col_e, col_f = st.columns(2)
    with col_e:
        avc = avg_value_by_channel(df)
        st.plotly_chart(ch.avg_value_by_channel_bar(avc), use_container_width=True)
    with col_f:
        hm = heatmap_data(df)
        st.plotly_chart(ch.heatmap_dow_month(hm), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CUSTOMER SEGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Customer Segmentation")

    dim_cust = load_dim_customer()

    col_g, col_h = st.columns(2)
    with col_g:
        st.plotly_chart(ch.clv_box(dim_cust), use_container_width=True)
    with col_h:
        st.plotly_chart(ch.avg_balance_bar(dim_cust), use_container_width=True)

    col_i, col_j = st.columns(2)
    with col_i:
        st.plotly_chart(ch.tenure_histogram(dim_cust), use_container_width=True)
    with col_j:
        st.plotly_chart(ch.age_group_bar(dim_cust), use_container_width=True)

    with st.expander("Customer Data Sample"):
        st.dataframe(
            dim_cust.sort_values("clv_proxy", ascending=False).head(100),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — BRANCH PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("Branch Performance")

    bp = branch_performance(df)
    rr = region_revenue(df)

    top_n = st.slider("Top N branches to display", min_value=5, max_value=60, value=20, step=5)

    col_k, col_l = st.columns([3, 2])
    with col_k:
        st.plotly_chart(ch.branch_efficiency_bar(bp, top_n=top_n), use_container_width=True)
    with col_l:
        st.plotly_chart(ch.region_revenue_bar(rr), use_container_width=True)

    st.plotly_chart(ch.branch_scatter(bp), use_container_width=True)

    with st.expander("Branch Data Table"):
        st.dataframe(
            bp[["branch_name", "region", "headcount", "total_revenue", "branch_efficiency_score"]]
            .sort_values("branch_efficiency_score", ascending=False),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DIGITAL vs PHYSICAL
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("Digital vs Physical Channel")

    dat = digital_adoption_trend(df)

    overall_rate = dat["digital"].sum() / dat["total"].sum()
    digital_txns = dat["digital"].sum()
    physical_txns = (dat["total"] - dat["digital"]).sum()

    d1, d2, d3 = st.columns(3)
    d1.metric("Overall Digital Adoption", f"{overall_rate:.1%}")
    d2.metric("Digital Transactions", f"{int(digital_txns):,}")
    d3.metric("Physical Transactions", f"{int(physical_txns):,}")

    st.plotly_chart(ch.digital_adoption_line(dat), use_container_width=True)

    col_m, col_n = st.columns(2)
    with col_m:
        st.plotly_chart(ch.digital_vs_physical_area(dat), use_container_width=True)
    with col_n:
        st.plotly_chart(ch.channel_volume_bar(df), use_container_width=True)

    st.plotly_chart(ch.avg_value_digital_bar(df), use_container_width=True)
