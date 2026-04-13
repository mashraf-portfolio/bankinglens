"""
charts.py
All Plotly figure factories for BankLens — dark, modern theme.
Each function receives a pre-aggregated DataFrame and returns a go.Figure.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── palette ───────────────────────────────────────────────────────────────────
C1 = "#0EA5E9"   # sky-500  — primary
C2 = "#0284C7"   # sky-600
C3 = "#38BDF8"   # sky-400
C4 = "#7DD3FC"   # sky-300
C5 = "#0369A1"   # sky-700
C6 = "#22D3EE"   # cyan-400
C7 = "#06B6D4"   # cyan-500
COLORS = [C1, C2, C3, C4, C5, C6, C7]

# background / surface
_BG        = "rgba(0,0,0,0)"          # transparent — card CSS provides surface
_GRID      = "rgba(51,65,85,0.35)"    # #334155 @ 35% opacity
_AXIS_LINE = "rgba(51,65,85,0.6)"
_FONT      = "#CBD5E1"
_FONT_DIM  = "#64748B"

# ── shared layout defaults ─────────────────────────────────────────────────────
_BASE = dict(
    template="plotly_dark",
    font=dict(family="Inter, system-ui, sans-serif", size=12, color=_FONT),
    plot_bgcolor=_BG,
    paper_bgcolor=_BG,
    margin=dict(l=8, r=8, t=52, b=8),
    hoverlabel=dict(
        bgcolor="#1E293B",
        bordercolor="#0EA5E9",
        font=dict(color="#F1F5F9", size=13, family="Inter, sans-serif"),
    ),
    transition=dict(duration=500, easing="cubic-in-out"),
    colorway=COLORS,
)

_XAXIS = dict(
    showgrid=False,
    zeroline=False,
    showline=True,
    linecolor=_AXIS_LINE,
    linewidth=1,
    tickfont=dict(color=_FONT_DIM, size=11),
    title_font=dict(color=_FONT, size=12),
)
_YAXIS = dict(
    showgrid=True,
    gridcolor=_GRID,
    gridwidth=1,
    zeroline=False,
    showline=False,
    tickfont=dict(color=_FONT_DIM, size=11),
    title_font=dict(color=_FONT, size=12),
)
_LEGEND = dict(
    orientation="h",
    y=1.06,
    x=0,
    font=dict(color=_FONT, size=11),
    bgcolor="rgba(0,0,0,0)",
    borderwidth=0,
)


def _apply(fig: go.Figure, title: str = "", height: int = 360) -> go.Figure:
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, color="#F1F5F9"),
            x=0,
            xanchor="left",
            pad=dict(l=4),
        ),
        height=height,
        **_BASE,
    )
    fig.update_xaxes(**_XAXIS)
    fig.update_yaxes(**_YAXIS)
    return fig


def _bar_style(fig: go.Figure, cornerradius: int = 6) -> go.Figure:
    """Apply rounded corners and remove bar borders."""
    fig.update_traces(marker_cornerradius=cornerradius, marker_line_width=0)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Executive Summary
# ══════════════════════════════════════════════════════════════════════════════

def monthly_volume_line(df: pd.DataFrame) -> go.Figure:
    """Dual-axis spline line — transaction count + total amount."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year_month"],
        y=df["transaction_count"],
        name="Transaction Count",
        mode="lines",
        line=dict(color=C1, width=3, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor="rgba(14,165,233,0.08)",
        hovertemplate="<b>%{x}</b><br>Transactions: <b>%{y:,}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["year_month"],
        y=df["total_amount"],
        name="Total Amount (£)",
        mode="lines",
        line=dict(color=C3, width=2, shape="spline", smoothing=0.8, dash="dot"),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Amount: <b>£%{y:,.0f}</b><extra></extra>",
    ))
    fig.update_layout(
        yaxis=dict(title="Transaction Count", **_YAXIS),
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            title="Total Amount (£)",
            tickformat=",.0f",
            tickfont=dict(color=_FONT_DIM, size=11),
            title_font=dict(color=_FONT, size=12),
            zeroline=False,
        ),
        legend=_LEGEND,
    )
    return _apply(fig, "Monthly Transaction Volume")


def revenue_by_product_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — revenue by product line."""
    df_s = df.sort_values("revenue")
    fig = go.Figure(go.Bar(
        x=df_s["revenue"],
        y=df_s["product_line"],
        orientation="h",
        marker=dict(
            color=df_s["revenue"],
            colorscale=[[0, C5], [0.5, C2], [1, C3]],
            showscale=False,
            line_width=0,
        ),
        text=df_s["revenue"].map("£{:,.0f}".format),
        textposition="inside",
        textfont=dict(color="#F1F5F9", size=11, family="Inter, sans-serif"),
        hovertemplate="<b>%{y}</b><br>Revenue: <b>£%{x:,.0f}</b><extra></extra>",
    ))
    _bar_style(fig)
    fig.update_xaxes(showgrid=True, gridcolor=_GRID)
    fig.update_yaxes(showgrid=False, showline=False)
    return _apply(fig, "Revenue by Product Line")


def segment_pie(df: pd.DataFrame) -> go.Figure:
    """Donut — customer count by segment."""
    counts = df["customer_segment"].value_counts().reset_index()
    counts.columns = ["segment", "count"]
    fig = go.Figure(go.Pie(
        labels=counts["segment"],
        values=counts["count"],
        hole=0.55,
        marker=dict(colors=COLORS, line=dict(color="#0F172A", width=3)),
        textinfo="percent",
        textfont=dict(size=13, color="#F1F5F9"),
        hovertemplate="<b>%{label}</b><br>Customers: <b>%{value:,}</b><br>Share: <b>%{percent}</b><extra></extra>",
        pull=[0.03] * len(counts),
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(**_LEGEND, x=0.5, xanchor="center", y=-0.1, orientation="h"),
        annotations=[dict(
            text=f"<b>{counts['count'].sum():,}</b><br><span style='font-size:10px;color:{_FONT_DIM}'>customers</span>",
            x=0.5, y=0.5, font_size=16, showarrow=False, font_color="#F1F5F9",
        )],
    )
    return _apply(fig, "Customers by Segment", height=340)


def txn_type_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — count by transaction type."""
    fig = go.Figure(go.Bar(
        x=df["transaction_type"],
        y=df["count"],
        marker=dict(
            color=df["count"],
            colorscale=[[0, C5], [0.5, C1], [1, C3]],
            showscale=False,
            line_width=0,
        ),
        text=df["count"].map("{:,}".format),
        textposition="outside",
        textfont=dict(color=_FONT, size=11),
        hovertemplate="<b>%{x}</b><br>Count: <b>%{y:,}</b><extra></extra>",
    ))
    _bar_style(fig)
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
    return _apply(fig, "Transactions by Type")


# ══════════════════════════════════════════════════════════════════════════════
# Transaction Trends
# ══════════════════════════════════════════════════════════════════════════════

def monthly_txn_type_area(df: pd.DataFrame) -> go.Figure:
    """Smooth stacked area — monthly volume by transaction type."""
    types = df["transaction_type"].unique()
    fig = go.Figure()
    for i, txn_type in enumerate(types):
        sub = df[df["transaction_type"] == txn_type].sort_values("year_month")
        color = COLORS[i % len(COLORS)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Scatter(
            x=sub["year_month"],
            y=sub["transaction_count"],
            name=txn_type.replace("_", " ").title(),
            mode="lines",
            line=dict(color=color, width=2, shape="spline", smoothing=0.6),
            stackgroup="one",
            fillcolor=f"rgba({r},{g},{b},0.45)",
            hovertemplate=f"<b>{txn_type}</b><br>Month: %{{x}}<br>Count: <b>%{{y:,}}</b><extra></extra>",
        ))
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Monthly Volume by Transaction Type", height=380)


def avg_value_by_channel_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — average transaction value per channel."""
    fig = go.Figure(go.Bar(
        x=df["channel"],
        y=df["avg_amount"],
        marker=dict(color=COLORS[:len(df)], line_width=0),
        text=df["avg_amount"].map("£{:,.0f}".format),
        textposition="outside",
        textfont=dict(color=_FONT, size=12, family="Inter, sans-serif"),
        hovertemplate="<b>%{x}</b><br>Avg Value: <b>£%{y:,.0f}</b><extra></extra>",
    ))
    _bar_style(fig, cornerradius=8)
    fig.update_yaxes(showgrid=True, gridcolor=_GRID, tickprefix="£")
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
    pivot = pivot.reindex(
        index=dow_order,
        columns=[m for m in month_order if m in pivot.columns],
    )
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=list(pivot.columns),
        y=list(pivot.index),
        colorscale=[[0, "#0F172A"], [0.4, C5], [0.7, C2], [1.0, C3]],
        showscale=True,
        colorbar=dict(
            thickness=12,
            len=0.8,
            tickfont=dict(color=_FONT_DIM, size=10),
            outlinewidth=0,
        ),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> · <b>%{x}</b><br>Transactions: <b>%{z:,}</b><extra></extra>",
        xgap=3,
        ygap=3,
    ))
    fig.update_xaxes(side="bottom", tickangle=-30, showgrid=False, showline=False)
    fig.update_yaxes(showgrid=False, showline=False)
    return _apply(fig, "Transaction Heatmap: Day of Week × Month")


# ══════════════════════════════════════════════════════════════════════════════
# Customer Segmentation
# ══════════════════════════════════════════════════════════════════════════════

def clv_box(df: pd.DataFrame) -> go.Figure:
    """Box plot — CLV proxy distribution by segment."""
    fig = go.Figure()
    segments = df["customer_segment"].unique()
    for i, seg in enumerate(segments):
        vals = df[df["customer_segment"] == seg]["clv_proxy"]
        color = COLORS[i % len(COLORS)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Box(
            y=vals,
            name=seg.replace("_", " ").title(),
            marker=dict(color=color, outliercolor=color, size=4),
            line=dict(color=color, width=2),
            fillcolor=f"rgba({r},{g},{b},0.15)",
            boxmean=True,
            hovertemplate=f"<b>{seg}</b><br>CLV: £%{{y:,.0f}}<extra></extra>",
        ))
    fig.update_yaxes(tickprefix="£", showgrid=True, gridcolor=_GRID)
    return _apply(fig, "CLV Proxy Distribution by Segment")


def avg_balance_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — mean avg_balance by segment."""
    agg = (
        df.groupby("customer_segment")["avg_balance"]
        .mean()
        .reset_index()
        .sort_values("avg_balance", ascending=False)
    )
    fig = go.Figure(go.Bar(
        x=agg["customer_segment"],
        y=agg["avg_balance"],
        marker=dict(color=COLORS[:len(agg)], line_width=0),
        text=agg["avg_balance"].map("£{:,.0f}".format),
        textposition="outside",
        textfont=dict(color=_FONT, size=12),
        hovertemplate="<b>%{x}</b><br>Avg Balance: <b>£%{y:,.0f}</b><extra></extra>",
    ))
    _bar_style(fig, cornerradius=8)
    fig.update_yaxes(showgrid=True, gridcolor=_GRID, tickprefix="£")
    return _apply(fig, "Average Balance by Customer Segment")


def tenure_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram — tenure distribution by segment."""
    fig = go.Figure()
    for i, (seg, group) in enumerate(df.groupby("customer_segment")):
        color = COLORS[i % len(COLORS)]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Histogram(
            x=group["tenure_months"],
            name=seg.replace("_", " ").title(),
            nbinsx=40,
            opacity=0.70,
            marker=dict(color=f"rgba({r},{g},{b},0.8)", line_width=0),
            hovertemplate=f"<b>{seg}</b><br>Tenure: %{{x}} months<br>Count: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(barmode="overlay", legend=_LEGEND)
    fig.update_xaxes(title_text="Tenure (months)")
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
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
        custom_data=["customer_segment"],
    )
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=4,
        hovertemplate="<b>%{x}</b> · %{customdata[0]}<br>Customers: <b>%{y:,}</b><extra></extra>",
    )
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Customers by Age Group and Segment")


# ══════════════════════════════════════════════════════════════════════════════
# Branch Performance
# ══════════════════════════════════════════════════════════════════════════════

def branch_efficiency_bar(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Horizontal bar — top N branches by efficiency score."""
    top = df.nlargest(top_n, "branch_efficiency_score").sort_values("branch_efficiency_score")
    regions = top["region"].unique().tolist()
    region_colors = {r: COLORS[i % len(COLORS)] for i, r in enumerate(regions)}
    fig = go.Figure()
    for region, grp in top.groupby("region"):
        color = region_colors[region]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Bar(
            x=grp["branch_efficiency_score"],
            y=grp["branch_name"],
            orientation="h",
            name=region,
            marker=dict(
                color=f"rgba({r},{g},{b},0.85)",
                line_width=0,
            ),
            hovertemplate="<b>%{y}</b><br>Region: " + region + "<br>Efficiency: <b>£%{x:,.0f}</b><extra></extra>",
        ))
    _bar_style(fig, cornerradius=4)
    fig.update_xaxes(showgrid=True, gridcolor=_GRID, tickprefix="£")
    fig.update_yaxes(showgrid=False, showline=False, tickfont=dict(size=10))
    fig.update_layout(barmode="stack", legend=_LEGEND)
    return _apply(fig, f"Top {top_n} Branches — Efficiency Score", height=max(360, top_n * 22))


def region_revenue_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — total revenue by region."""
    fig = go.Figure(go.Bar(
        x=df["region"],
        y=df["total_revenue"],
        marker=dict(
            color=df["total_revenue"],
            colorscale=[[0, C5], [0.5, C1], [1, C3]],
            showscale=False,
            line_width=0,
        ),
        text=df["total_revenue"].map("£{:,.0f}".format),
        textposition="outside",
        textfont=dict(color=_FONT, size=11),
        hovertemplate="<b>%{x}</b><br>Revenue: <b>£%{y:,.0f}</b><extra></extra>",
    ))
    _bar_style(fig, cornerradius=8)
    fig.update_yaxes(showgrid=True, gridcolor=_GRID, tickprefix="£")
    return _apply(fig, "Total Revenue by Region")


def branch_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter — headcount vs total revenue, coloured by region."""
    regions = df["region"].unique().tolist()
    region_colors = {r: COLORS[i % len(COLORS)] for i, r in enumerate(regions)}
    fig = go.Figure()
    for region, grp in df.groupby("region"):
        color = region_colors[region]
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fig.add_trace(go.Scatter(
            x=grp["headcount"],
            y=grp["total_revenue"],
            mode="markers",
            name=region,
            marker=dict(
                size=grp["branch_efficiency_score"].clip(upper=grp["branch_efficiency_score"].quantile(0.95)),
                sizemode="area",
                sizeref=2.0 * grp["branch_efficiency_score"].max() / (22 ** 2),
                color=f"rgba({r},{g},{b},0.75)",
                line=dict(color=color, width=1),
            ),
            text=grp["branch_name"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Headcount: <b>%{x}</b><br>"
                "Revenue: <b>£%{y:,.0f}</b><extra></extra>"
            ),
        ))
    fig.update_xaxes(title_text="Headcount", showgrid=True, gridcolor=_GRID)
    fig.update_yaxes(title_text="Total Revenue (£)", showgrid=True, gridcolor=_GRID, tickprefix="£")
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Branch Headcount vs Revenue", height=400)


# ══════════════════════════════════════════════════════════════════════════════
# Digital vs Physical
# ══════════════════════════════════════════════════════════════════════════════

def digital_adoption_line(df: pd.DataFrame) -> go.Figure:
    """Smooth line with gradient fill — digital adoption rate over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year_month"],
        y=df["digital_rate"],
        mode="lines+markers",
        line=dict(color=C1, width=3, shape="spline", smoothing=0.8),
        marker=dict(
            size=6,
            color=C1,
            line=dict(color="#0F172A", width=2),
        ),
        fill="tozeroy",
        fillcolor="rgba(14,165,233,0.1)",
        name="Digital Adoption Rate",
        hovertemplate="<b>%{x}</b><br>Digital Rate: <b>%{y:.1%}</b><extra></extra>",
    ))
    # 50% reference line
    fig.add_hline(
        y=0.5,
        line_dash="dot",
        line_color="rgba(100,116,139,0.5)",
        line_width=1,
        annotation_text="50%",
        annotation_font_color=_FONT_DIM,
        annotation_font_size=10,
    )
    fig.update_yaxes(tickformat=".0%", showgrid=True, gridcolor=_GRID, range=[0, 1])
    return _apply(fig, "Digital Adoption Rate Over Time", height=340)


def digital_vs_physical_area(df: pd.DataFrame) -> go.Figure:
    """Stacked area — digital vs physical volume over time."""
    df2 = df.copy()
    df2["physical"] = df2["total"] - df2["digital"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df2["year_month"], y=df2["physical"],
        name="Physical",
        mode="lines",
        line=dict(color="#475569", width=2, shape="spline", smoothing=0.6),
        stackgroup="one",
        fillcolor="rgba(71,85,105,0.45)",
        hovertemplate="Month: <b>%{x}</b><br>Physical: <b>%{y:,}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df2["year_month"], y=df2["digital"],
        name="Digital",
        mode="lines",
        line=dict(color=C1, width=2, shape="spline", smoothing=0.6),
        stackgroup="one",
        fillcolor="rgba(14,165,233,0.55)",
        hovertemplate="Month: <b>%{x}</b><br>Digital: <b>%{y:,}</b><extra></extra>",
    ))
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Digital vs Physical Channel Volume")


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
        custom_data=["channel"],
    )
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=6,
        hovertemplate="<b>%{customdata[0]}</b> · %{x}<br>Transactions: <b>%{y:,}</b><extra></extra>",
    )
    fig.update_yaxes(showgrid=True, gridcolor=_GRID)
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Transaction Volume by Channel per Year")


def avg_value_digital_bar(df: pd.DataFrame) -> go.Figure:
    """Bar — avg transaction value, digital vs physical channels."""
    df2 = df.copy()
    df2["channel_type"] = df2["channel"].map(
        lambda c: "Digital" if c in ("mobile_app", "online_banking") else "Physical"
    )
    agg = df2.groupby(["channel", "channel_type"])["amount"].mean().reset_index(name="avg_amount")
    color_map = {"Digital": C1, "Physical": "#475569"}
    fig = px.bar(
        agg,
        x="channel",
        y="avg_amount",
        color="channel_type",
        color_discrete_map=color_map,
        text=agg["avg_amount"].map("£{:,.0f}".format),
        labels={"avg_amount": "Avg Value (£)", "channel": "Channel", "channel_type": "Type"},
        custom_data=["channel_type"],
    )
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=8,
        textposition="outside",
        textfont=dict(color=_FONT, size=12),
        hovertemplate="<b>%{x}</b> (%{customdata[0]})<br>Avg Value: <b>£%{y:,.0f}</b><extra></extra>",
    )
    fig.update_yaxes(showgrid=True, gridcolor=_GRID, tickprefix="£")
    fig.update_layout(legend=_LEGEND)
    return _apply(fig, "Avg Transaction Value: Digital vs Physical")
