"""
app.py — BankLens: Banking Operations Analytics Platform
Run with: streamlit run src/app.py
"""

import streamlit as st

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

# ══════════════════════════════════════════════════════════════════════════════
# Global CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── App shell ──────────────────────────────────────────────────────────── */
.stApp {
    background-color: #0F172A;
    color: #CBD5E1;
}
.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 1440px;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0B1120;
    border-right: 1px solid #1E293B;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label {
    color: #94A3B8 !important;
    font-size: 0.82rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}
/* Sidebar multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #0EA5E9 !important;
    border-color: #0EA5E9 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #1E293B !important;
    border-color: #334155 !important;
    border-radius: 8px !important;
    color: #CBD5E1 !important;
}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1E293B;
    border-radius: 12px;
    padding: 5px 6px;
    gap: 4px;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #64748B !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 8px 18px !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #CBD5E1 !important;
    background: rgba(255,255,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0284C7, #0EA5E9) !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 12px rgba(14,165,233,0.35) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── KPI metric cards ────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1E293B 0%, #162032 100%);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
}
[data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
    letter-spacing: -0.5px;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: #64748B !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 500;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ── Plotly chart card containers ────────────────────────────────────────── */
[data-testid="stPlotlyChart"],
.stPlotlyChart {
    background: #1E293B;
    border: 1px solid #2D3F55;
    border-radius: 16px;
    padding: 0.75rem;
    box-shadow: 0 4px 28px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03);
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr {
    border-color: #1E293B !important;
    margin: 1.5rem 0 !important;
}

/* ── Slider ──────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] > div > div > div > div {
    background: #0EA5E9 !important;
}

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #1E293B;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
    color: #94A3B8 !important;
    font-size: 0.85rem;
}

/* ── Dataframe ────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Warning / info banners ──────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #1E293B;
    border-color: #0EA5E9;
    border-radius: 10px;
    color: #CBD5E1;
}

/* ── General text ────────────────────────────────────────────────────────── */
p, li, span { color: #CBD5E1; }
h1, h2, h3, h4 { color: #F1F5F9 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helper: section header with accent bar ─────────────────────────────────────
def section_header(title: str, subtitle: str = "") -> None:
    sub_html = (
        f'<p style="color:#64748B;font-size:0.82rem;margin:5px 0 0 15px;'
        f'font-family:Inter,sans-serif;">{subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;margin:1.75rem 0 1rem 0;gap:12px;">
        <div style="width:3px;min-height:28px;background:linear-gradient(180deg,#0EA5E9,#0284C7);
                    border-radius:2px;margin-top:2px;flex-shrink:0;"></div>
        <div>
            <span style="font-size:1rem;font-weight:600;color:#F1F5F9;
                         font-family:Inter,sans-serif;">{title}</span>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def tab_header(title: str, icon: str = "") -> None:
    st.markdown(f"""
    <div style="padding:0.25rem 0 1.75rem 0;">
        <h2 style="font-size:1.55rem;font-weight:700;color:#F1F5F9;margin:0;padding:0;
                   font-family:Inter,sans-serif;letter-spacing:-0.3px;">
            {(icon + "&nbsp;&nbsp;") if icon else ""}{title}
        </h2>
        <div style="height:3px;width:56px;
                    background:linear-gradient(90deg,#0EA5E9,#38BDF8,rgba(56,189,248,0));
                    margin-top:10px;border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:0.5rem 0 1.5rem 0;display:flex;align-items:center;gap:12px;">
        <div style="font-size:1.8rem;line-height:1;">🏦</div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#F1F5F9;
                        font-family:Inter,sans-serif;letter-spacing:-0.3px;">BankLens</div>
            <div style="font-size:0.72rem;color:#0EA5E9;font-weight:500;
                        letter-spacing:0.06em;text-transform:uppercase;">Analytics Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,#334155,transparent);
                margin-bottom:1.5rem;"></div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="font-size:0.7rem;color:#475569;text-transform:uppercase;'
        'letter-spacing:0.1em;font-weight:600;margin-bottom:0.75rem;">Filters</p>',
        unsafe_allow_html=True,
    )

    df_full = load_enriched()

    year_options = sorted(df_full["year"].unique().tolist())
    selected_years = st.multiselect("Year", year_options, default=year_options)

    region_options = sorted(df_full["region"].unique().tolist())
    selected_regions = st.multiselect("Region", region_options, default=region_options)

    segment_options = sorted(df_full["customer_segment"].unique().tolist())
    selected_segments = st.multiselect("Customer Segment", segment_options, default=segment_options)

    channel_options = sorted(df_full["channel"].unique().tolist())
    selected_channels = st.multiselect("Channel", channel_options, default=channel_options)

    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,#334155,transparent);
                margin:1.5rem 0 1rem 0;"></div>
    <p style="font-size:0.72rem;color:#334155;text-align:center;">
        2022 – 2024 &nbsp;·&nbsp; 100K synthetic transactions
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Filter
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def filter_df(years: tuple, regions: tuple, segments: tuple, channels: tuple) -> pd.DataFrame:
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
    st.warning("No data matches the current filters — adjust the sidebar selections.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# App header
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;">
        <h1 style="font-size:2rem;font-weight:800;color:#F1F5F9;margin:0;
                   font-family:Inter,sans-serif;letter-spacing:-0.5px;">
            Banking Operations Analytics
        </h1>
        <span style="font-size:0.78rem;background:rgba(14,165,233,0.12);color:#38BDF8;
                     border:1px solid rgba(14,165,233,0.25);border-radius:20px;
                     padding:3px 12px;font-weight:500;letter-spacing:0.03em;">
            LIVE DASHBOARD
        </span>
    </div>
    <p style="color:#475569;font-size:0.88rem;margin:6px 0 0 0;font-family:Inter,sans-serif;">
        Star-schema · 100K transactions · 2022–2024
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Tabs
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  Executive Summary  ",
    "  Transaction Trends  ",
    "  Customer Segmentation  ",
    "  Branch Performance  ",
    "  Digital vs Physical  ",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — EXECUTIVE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    tab_header("Executive Summary", "📊")

    kpis = kpi_summary(df)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Transactions",  f"{kpis['total_transactions']:,}")
    c2.metric("Total Revenue",       f"£{kpis['total_revenue']:,.0f}")
    c3.metric("Avg Transaction",     f"£{kpis['avg_transaction_value']:,.0f}")
    c4.metric("Digital Adoption",    f"{kpis['digital_adoption_rate']:.1%}")
    c5.metric("Unique Customers",    f"{kpis['unique_customers']:,}")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    section_header("Volume & Revenue", "Transaction count and product revenue over time")
    col_a, col_b = st.columns([3, 2], gap="medium")
    with col_a:
        st.plotly_chart(ch.monthly_volume_line(monthly_volume(df)), use_container_width=True)
    with col_b:
        st.plotly_chart(ch.revenue_by_product_bar(revenue_by_product(df)), use_container_width=True)

    section_header("Customer Mix", "Segment distribution and transaction type breakdown")
    col_c, col_d = st.columns([2, 3], gap="medium")
    with col_c:
        st.plotly_chart(ch.segment_pie(load_dim_customer()), use_container_width=True)
    with col_d:
        st.plotly_chart(ch.txn_type_bar(txn_type_distribution(df)), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — TRANSACTION TRENDS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    tab_header("Transaction Trends", "📈")

    section_header("Volume Over Time", "Monthly breakdown by transaction type")
    monthly_by_type = (
        df.groupby(["year_month", "transaction_type"])["transaction_id"]
        .count()
        .reset_index(name="transaction_count")
        .sort_values("year_month")
    )
    st.plotly_chart(ch.monthly_txn_type_area(monthly_by_type), use_container_width=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_header("Channel & Timing", "Average value per channel and weekly activity patterns")
    col_e, col_f = st.columns(2, gap="medium")
    with col_e:
        st.plotly_chart(ch.avg_value_by_channel_bar(avg_value_by_channel(df)), use_container_width=True)
    with col_f:
        st.plotly_chart(ch.heatmap_dow_month(heatmap_data(df)), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — CUSTOMER SEGMENTATION
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    tab_header("Customer Segmentation", "👥")

    dim_cust = load_dim_customer()

    section_header("Value & Balance", "CLV proxy distribution and average balances by segment")
    col_g, col_h = st.columns(2, gap="medium")
    with col_g:
        st.plotly_chart(ch.clv_box(dim_cust), use_container_width=True)
    with col_h:
        st.plotly_chart(ch.avg_balance_bar(dim_cust), use_container_width=True)

    section_header("Demographics", "Tenure spread and age-group composition")
    col_i, col_j = st.columns(2, gap="medium")
    with col_i:
        st.plotly_chart(ch.tenure_histogram(dim_cust), use_container_width=True)
    with col_j:
        st.plotly_chart(ch.age_group_bar(dim_cust), use_container_width=True)

    with st.expander("Customer Data Sample (top 100 by CLV)"):
        st.dataframe(
            dim_cust.sort_values("clv_proxy", ascending=False).head(100),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — BRANCH PERFORMANCE
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    tab_header("Branch Performance", "🏢")

    bp = branch_performance(df)
    rr = region_revenue(df)

    section_header("Efficiency Ranking", "Revenue generated per staff member")
    top_n = st.slider("Top N branches", min_value=5, max_value=60, value=20, step=5)

    col_k, col_l = st.columns([3, 2], gap="medium")
    with col_k:
        st.plotly_chart(ch.branch_efficiency_bar(bp, top_n=top_n), use_container_width=True)
    with col_l:
        st.plotly_chart(ch.region_revenue_bar(rr), use_container_width=True)

    section_header("Headcount vs Revenue", "Bubble size = efficiency score")
    st.plotly_chart(ch.branch_scatter(bp), use_container_width=True)

    with st.expander("Full Branch Data Table"):
        st.dataframe(
            bp[["branch_name", "region", "headcount", "total_revenue", "branch_efficiency_score"]]
            .sort_values("branch_efficiency_score", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — DIGITAL vs PHYSICAL
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    tab_header("Digital vs Physical Channel", "📱")

    dat = digital_adoption_trend(df)
    overall_rate  = dat["digital"].sum() / dat["total"].sum()
    digital_txns  = int(dat["digital"].sum())
    physical_txns = int((dat["total"] - dat["digital"]).sum())

    d1, d2, d3 = st.columns(3)
    d1.metric("Overall Digital Adoption", f"{overall_rate:.1%}")
    d2.metric("Digital Transactions",     f"{digital_txns:,}")
    d3.metric("Physical Transactions",    f"{physical_txns:,}")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    section_header("Adoption Trend", "Monthly digital adoption rate (50% reference line shown)")
    st.plotly_chart(ch.digital_adoption_line(dat), use_container_width=True)

    section_header("Channel Split", "Volume distribution and year-over-year channel comparison")
    col_m, col_n = st.columns(2, gap="medium")
    with col_m:
        st.plotly_chart(ch.digital_vs_physical_area(dat), use_container_width=True)
    with col_n:
        st.plotly_chart(ch.channel_volume_bar(df), use_container_width=True)

    section_header("Average Value", "Transaction size comparison across all four channels")
    st.plotly_chart(ch.avg_value_digital_bar(df), use_container_width=True)
