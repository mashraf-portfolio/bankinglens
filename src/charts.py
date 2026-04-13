"""
charts.py
All Plotly figure factories for BankLens.
Each function receives a pre-aggregated DataFrame and returns a go.Figure.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── palette ───────────────────────────────────────────────────────────────────
BLUE = "#1E3A5F"
TEAL = "#0D9488"
AMBER = "#F59E0B"
ROSE = "#E11D48"
SLATE = "#64748B"
COLORS = [BLUE, TEAL, AMBER, ROSE, SLATE, "#7C3AED", "#059669"]

_LAYOUT = dict(
    font_family="Inter, sans-serif",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=16, t=40, b=16),
)


def _apply(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=dict(text=title, font_size=14), **_LAYOUT)
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#E2E8F0", linecolor="#E2E8F0")
    return fig


# ── Executive Summary ─────────────────────────────────────────────────────────

def revenue_by_product_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — revenue by product line."""
    fig = px.bar(
        df.sort_values("revenue"),
        x="revenue",
        y="product_line",
        orientation="h",
        color="product_line",
        color_discrete_sequence=COLORS,
        labels={"revenue": "Revenue (£)", "product_line": "Product Line"},
    )
    fig.update_traces(showlegend=False)
    return _apply(fig, "Revenue by Product Line")


def segment_pie(df: pd.DataFrame) -> go.Figure:
    """Donut — customer count by segment."""
    counts = df["customer_segment"].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    fig = px.pie(
        counts,
        names="segment",
        values="count",
        hole=0.45,
        color_discrete_sequence=COLORS,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return _apply(fig, "Customers by Segment")


def monthly_volume_line(df: pd.DataFrame) -> go.Figure:
    """Dual-axis line — transaction count + total amount."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year_month"],
            y=df["transaction_count"],
            name="Transaction Count",
            line=dict(color=BLUE, width=2),
            mode="lines",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year_month"],
            y=df["total_amount"],
            name="Total Amount (£)",
            line=dict(color=TEAL, width=2, dash="dot"),
            mode="lines",
            yaxis="y2",
        )
    )
    fig.update_layout(
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            title="Total Amount (£)",
            tickformat=",.0f",
        ),
        yaxis=dict(title="Transaction Count"),
        legend=dict(orientation="h", y=1.08),
    )
    return _apply(fig, "Monthly Transaction Volume")


# ── Transaction Trends ────────────────────────────────────────────────────────

def txn_type_bar(df: pd.DataFrame) -> go.Figure:
    """Grouped bar — count and amount by transaction type."""
    fig = px.bar(
        df,
        x="transaction_type",
        y="count",
        color="transaction_type",
        color_discrete_sequence=COLORS,
        labels={"count": "Transaction Count", "transaction_type": "Type"},
    )
    fig.update_traces(showlegend=False)
    return _apply(fig, "Transactions by Type")


def avg_value_by_channel_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — average transaction value per channel."""
    fig = px.bar(
        df,
        x="channel",
        y="avg_amount",
        color="channel",
        color_discrete_sequence=COLORS,
        text=df["avg_amount"].map("£{:,.0f}".format),
        labels={"avg_amount": "Avg Transaction Value (£)", "channel": "Channel"},
    )
    fig.update_traces(showlegend=False, textposition="outside")
    return _apply(fig, "Avg Transaction Value by Channel")


def heatmap_dow_month(df: pd.DataFrame) -> go.Figure:
    """Heatmap — transaction volume by day-of-week × month."""
    pivot = df.pivot_table(
        index="day_of_week", columns="month_name", values="count", aggfunc="sum"
    )
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(index=dow_order, columns=[m for m in month_order if m in pivot.columns])

    fig = px.imshow(
        pivot,
        color_continuous_scale=[[0, "#EFF6FF"], [1, BLUE]],
        labels=dict(color="Count"),
        aspect="auto",
    )
    return _apply(fig, "Transaction Heatmap: Day of Week x Month")


def monthly_txn_type_area(df: pd.DataFrame) -> go.Figure:
    """Stacked area — monthly volume broken out by transaction type."""
    fig = px.area(
        df,
        x="year_month",
        y="transaction_count",
        color="transaction_type",
        color_discrete_sequence=COLORS,
        labels={"transaction_count": "Count", "year_month": "Month", "transaction_type": "Type"},
    )
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Monthly Volume by Transaction Type")


# ── Customer Segmentation ─────────────────────────────────────────────────────

def clv_box(df: pd.DataFrame) -> go.Figure:
    """Box plot — CLV proxy distribution by segment."""
    fig = px.box(
        df,
        x="customer_segment",
        y="clv_proxy",
        color="customer_segment",
        color_discrete_sequence=COLORS,
        points=False,
        labels={"clv_proxy": "CLV Proxy (£)", "customer_segment": "Segment"},
    )
    fig.update_traces(showlegend=False)
    return _apply(fig, "CLV Proxy Distribution by Segment")


def avg_balance_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — mean avg_balance by segment."""
    agg = (
        df.groupby("customer_segment")["avg_balance"]
        .mean()
        .reset_index()
        .sort_values("avg_balance", ascending=False)
    )
    fig = px.bar(
        agg,
        x="customer_segment",
        y="avg_balance",
        color="customer_segment",
        color_discrete_sequence=COLORS,
        text=agg["avg_balance"].map("£{:,.0f}".format),
        labels={"avg_balance": "Avg Balance (£)", "customer_segment": "Segment"},
    )
    fig.update_traces(showlegend=False, textposition="outside")
    return _apply(fig, "Average Balance by Customer Segment")


def tenure_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram — tenure distribution by segment."""
    fig = px.histogram(
        df,
        x="tenure_months",
        color="customer_segment",
        nbins=40,
        barmode="overlay",
        opacity=0.75,
        color_discrete_sequence=COLORS,
        labels={"tenure_months": "Tenure (months)", "customer_segment": "Segment"},
    )
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Customer Tenure Distribution")


def age_group_bar(df: pd.DataFrame) -> go.Figure:
    """Stacked bar — age group × segment."""
    agg = df.groupby(["age_group", "customer_segment"]).size().reset_index(name="count")
    age_order = ["18-25", "26-35", "36-50", "51-65", "65+"]
    agg["age_group"] = pd.Categorical(agg["age_group"], categories=age_order, ordered=True)
    agg = agg.sort_values("age_group")
    fig = px.bar(
        agg,
        x="age_group",
        y="count",
        color="customer_segment",
        barmode="stack",
        color_discrete_sequence=COLORS,
        labels={"count": "Customers", "age_group": "Age Group", "customer_segment": "Segment"},
    )
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Customers by Age Group and Segment")


# ── Branch Performance ────────────────────────────────────────────────────────

def branch_efficiency_bar(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Horizontal bar — top N branches by efficiency score."""
    top = df.nlargest(top_n, "branch_efficiency_score")
    fig = px.bar(
        top.sort_values("branch_efficiency_score"),
        x="branch_efficiency_score",
        y="branch_name",
        orientation="h",
        color="region",
        color_discrete_sequence=COLORS,
        labels={"branch_efficiency_score": "Efficiency Score (£ revenue / headcount)", "branch_name": "Branch"},
    )
    return _apply(fig, f"Top {top_n} Branches by Efficiency Score")


def region_revenue_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — total revenue by region."""
    fig = px.bar(
        df,
        x="region",
        y="total_revenue",
        color="region",
        color_discrete_sequence=COLORS,
        text=df["total_revenue"].map("£{:,.0f}".format),
        labels={"total_revenue": "Total Revenue (£)", "region": "Region"},
    )
    fig.update_traces(showlegend=False, textposition="outside")
    return _apply(fig, "Total Revenue by Region")


def branch_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter — headcount vs total revenue, coloured by region."""
    fig = px.scatter(
        df,
        x="headcount",
        y="total_revenue",
        color="region",
        size="branch_efficiency_score",
        hover_name="branch_name",
        color_discrete_sequence=COLORS,
        labels={
            "headcount": "Headcount",
            "total_revenue": "Total Revenue (£)",
            "branch_efficiency_score": "Efficiency Score",
        },
    )
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Branch Headcount vs Revenue")


# ── Digital vs Physical ───────────────────────────────────────────────────────

def digital_adoption_line(df: pd.DataFrame) -> go.Figure:
    """Line — digital adoption rate over time."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year_month"],
            y=df["digital_rate"],
            mode="lines+markers",
            line=dict(color=TEAL, width=2),
            marker=dict(size=4),
            name="Digital Adoption Rate",
            hovertemplate="%{x}<br>Rate: %{y:.1%}<extra></extra>",
        )
    )
    fig.update_yaxes(tickformat=".0%")
    return _apply(fig, "Digital Adoption Rate Over Time")


def channel_volume_bar(df: pd.DataFrame) -> go.Figure:
    """Grouped bar — transaction count by channel per year."""
    agg = (
        df.groupby(["year", "channel"])["transaction_id"]
        .count()
        .reset_index(name="count")
    )
    fig = px.bar(
        agg,
        x="year",
        y="count",
        color="channel",
        barmode="group",
        color_discrete_sequence=COLORS,
        labels={"count": "Transactions", "year": "Year", "channel": "Channel"},
    )
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Transaction Volume by Channel per Year")


def digital_vs_physical_area(df: pd.DataFrame) -> go.Figure:
    """Stacked area — digital vs physical volume over time."""
    df2 = df.copy()
    df2["physical"] = df2["total"] - df2["digital"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df2["year_month"], y=df2["physical"],
        name="Physical", stackgroup="one",
        line=dict(color=SLATE), fillcolor="rgba(100,116,139,0.4)",
    ))
    fig.add_trace(go.Scatter(
        x=df2["year_month"], y=df2["digital"],
        name="Digital", stackgroup="one",
        line=dict(color=TEAL), fillcolor="rgba(13,148,136,0.6)",
    ))
    fig.update_layout(legend=dict(orientation="h", y=1.08))
    return _apply(fig, "Digital vs Physical Channel Volume")


def avg_value_digital_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — avg transaction value, digital vs physical channels."""
    df2 = df.copy()
    df2["channel_type"] = df2["channel"].map(
        lambda c: "Digital" if c in ("mobile_app", "online_banking") else "Physical"
    )
    agg = df2.groupby(["channel", "channel_type"])["amount"].mean().reset_index(name="avg_amount")
    fig = px.bar(
        agg,
        x="channel",
        y="avg_amount",
        color="channel_type",
        color_discrete_map={"Digital": TEAL, "Physical": BLUE},
        text=agg["avg_amount"].map("£{:,.0f}".format),
        labels={"avg_amount": "Avg Transaction Value (£)", "channel": "Channel", "channel_type": "Type"},
    )
    fig.update_traces(textposition="outside")
    return _apply(fig, "Avg Transaction Value: Digital vs Physical")
