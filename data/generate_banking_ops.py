"""
generate_banking_ops.py
Generates a star-schema synthetic banking dataset:
  - Fact_Transactions (100 000 rows)
  - Dim_Customer, Dim_Branch, Dim_Date, Dim_Product, Dim_Channel

Output: data/csv/*.csv
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd

# ── reproducibility ──────────────────────────────────────────────────────────
SEED = 42
rng = np.random.default_rng(SEED)
random.seed(SEED)

# ── output directory ─────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent / "csv"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── constants ────────────────────────────────────────────────────────────────
N_TRANSACTIONS = 100_000
N_CUSTOMERS = 8_000
N_BRANCHES = 60

TRANSACTION_TYPES = ["deposit", "withdrawal", "transfer", "payment", "loan_repayment"]
CHANNELS = ["branch", "ATM", "mobile_app", "online_banking"]
REGIONS = ["North", "South", "East", "West", "Central"]
PRODUCT_LINES = [
    "retail_savings",
    "current_account",
    "personal_loan",
    "credit_card",
    "investment",
]
CUSTOMER_SEGMENTS = ["mass", "affluent", "private_banking"]

# channel → digital flag mapping
DIGITAL_CHANNELS = {"mobile_app", "online_banking"}


# ── dimension: Dim_Date ──────────────────────────────────────────────────────
def build_dim_date(start: str = "2022-01-01", end: str = "2024-12-31") -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame(
        {
            "date_id": range(1, len(dates) + 1),
            "full_date": dates,
            "year": dates.year,
            "quarter": dates.quarter,
            "month": dates.month,
            "month_name": dates.strftime("%B"),
            "week": dates.isocalendar().week.astype(int),
            "day_of_week": dates.day_name(),
            "is_weekend": dates.dayofweek >= 5,
        }
    )
    return df


# ── dimension: Dim_Customer ──────────────────────────────────────────────────
def build_dim_customer(n: int) -> pd.DataFrame:
    segment_weights = [0.70, 0.25, 0.05]  # mass / affluent / private_banking
    segments = rng.choice(CUSTOMER_SEGMENTS, size=n, p=segment_weights)

    # avg_balance varies by segment
    seg_balance = {"mass": (500, 5_000), "affluent": (10_000, 80_000), "private_banking": (100_000, 500_000)}
    avg_balances = np.array(
        [
            rng.uniform(*seg_balance[seg])
            for seg in segments
        ]
    )

    tenure_months = rng.integers(1, 121, size=n)  # 1–120 months (10 years)

    df = pd.DataFrame(
        {
            "customer_id": range(1, n + 1),
            "customer_segment": segments,
            "avg_balance": np.round(avg_balances, 2),
            "tenure_months": tenure_months,
            # CLV proxy = avg_balance * tenure_months * 0.02
            "clv_proxy": np.round(avg_balances * tenure_months * 0.02, 2),
            "age_group": rng.choice(["18-25", "26-35", "36-50", "51-65", "65+"], size=n,
                                    p=[0.10, 0.25, 0.35, 0.20, 0.10]),
        }
    )
    return df


# ── dimension: Dim_Branch ────────────────────────────────────────────────────
def build_dim_branch(n: int) -> pd.DataFrame:
    region_list = rng.choice(REGIONS, size=n)
    headcount = rng.integers(5, 51, size=n)  # 5–50 staff per branch

    df = pd.DataFrame(
        {
            "branch_id": range(1, n + 1),
            "branch_name": [f"Branch_{i:03d}" for i in range(1, n + 1)],
            "region": region_list,
            "headcount": headcount,
            "city": [f"City_{rng.integers(1, 21):02d}" for _ in range(n)],
        }
    )
    return df


# ── dimension: Dim_Product ───────────────────────────────────────────────────
def build_dim_product() -> pd.DataFrame:
    # revenue rate per £ transacted
    rev_rates = {
        "retail_savings": 0.010,
        "current_account": 0.015,
        "personal_loan": 0.060,
        "credit_card": 0.045,
        "investment": 0.025,
    }
    df = pd.DataFrame(
        {
            "product_id": range(1, len(PRODUCT_LINES) + 1),
            "product_line": PRODUCT_LINES,
            "revenue_rate": [rev_rates[p] for p in PRODUCT_LINES],
        }
    )
    return df


# ── dimension: Dim_Channel ───────────────────────────────────────────────────
def build_dim_channel() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "channel_id": range(1, len(CHANNELS) + 1),
            "channel": CHANNELS,
            "is_digital": [c in DIGITAL_CHANNELS for c in CHANNELS],
        }
    )
    return df


# ── fact: Fact_Transactions ──────────────────────────────────────────────────
def build_fact_transactions(
    dim_date: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_branch: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_channel: pd.DataFrame,
    n: int,
) -> pd.DataFrame:
    # --- FK samples ---
    date_ids = rng.choice(dim_date["date_id"].values, size=n)
    customer_ids = rng.choice(dim_customer["customer_id"].values, size=n)

    # channel first – physical txns map to a branch; digital may too (ATM)
    channel_ids = rng.choice(
        dim_channel["channel_id"].values,
        size=n,
        p=[0.20, 0.25, 0.30, 0.25],  # branch / ATM / mobile_app / online_banking
    )
    product_ids = rng.choice(dim_product["product_id"].values, size=n)

    # branch: physical channels always have a branch; digital ones do too (origin branch)
    branch_ids = rng.choice(dim_branch["branch_id"].values, size=n)

    # --- amounts by transaction type ---
    txn_types = rng.choice(
        TRANSACTION_TYPES,
        size=n,
        p=[0.30, 0.25, 0.20, 0.15, 0.10],
    )
    amount_params = {
        "deposit": (2_000, 1_500),
        "withdrawal": (800, 600),
        "transfer": (1_500, 1_000),
        "payment": (400, 300),
        "loan_repayment": (1_200, 500),
    }
    amounts = np.array(
        [
            max(10.0, rng.normal(amount_params[t][0], amount_params[t][1]))
            for t in txn_types
        ]
    )
    amounts = np.round(amounts, 2)

    # --- denormalised columns for easier querying ---
    channel_map = dim_channel.set_index("channel_id")["channel"].to_dict()
    branch_map = dim_branch.set_index("branch_id")[["branch_name", "region"]].to_dict("index")
    product_map = dim_product.set_index("product_id")["product_line"].to_dict()
    segment_map = dim_customer.set_index("customer_id")["customer_segment"].to_dict()
    date_map = dim_date.set_index("date_id")["full_date"].to_dict()

    channels_col = [channel_map[c] for c in channel_ids]
    branch_names = [branch_map[b]["branch_name"] for b in branch_ids]
    regions = [branch_map[b]["region"] for b in branch_ids]
    product_lines = [product_map[p] for p in product_ids]
    customer_segments = [segment_map[c] for c in customer_ids]
    transaction_dates = [date_map[d] for d in date_ids]

    fact = pd.DataFrame(
        {
            "transaction_id": range(1, n + 1),
            "customer_id": customer_ids,
            "branch_id": branch_ids,
            "date_id": date_ids,
            "product_id": product_ids,
            "channel_id": channel_ids,
            "amount": amounts,
            "transaction_type": txn_types,
            "channel": channels_col,
            "branch_name": branch_names,
            "region": regions,
            "product_line": product_lines,
            "customer_segment": customer_segments,
            "transaction_date": transaction_dates,
        }
    )
    return fact


# ── revenue computation ──────────────────────────────────────────────────────
def add_revenue(fact: pd.DataFrame, dim_product: pd.DataFrame) -> pd.DataFrame:
    rate_map = dim_product.set_index("product_line")["revenue_rate"].to_dict()
    fact["revenue"] = (fact["amount"] * fact["product_line"].map(rate_map)).round(2)
    return fact


# ── branch efficiency score ──────────────────────────────────────────────────
def compute_branch_efficiency(
    fact: pd.DataFrame, dim_branch: pd.DataFrame
) -> pd.DataFrame:
    branch_revenue = fact.groupby("branch_id")["revenue"].sum().reset_index()
    branch_revenue.columns = ["branch_id", "total_revenue"]
    merged = dim_branch.merge(branch_revenue, on="branch_id", how="left")
    merged["total_revenue"] = merged["total_revenue"].fillna(0)
    merged["branch_efficiency_score"] = (
        merged["total_revenue"] / merged["headcount"]
    ).round(2)
    return merged[["branch_id", "branch_name", "region", "headcount", "total_revenue", "branch_efficiency_score"]]


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("Building dimensions...")
    dim_date = build_dim_date()
    dim_customer = build_dim_customer(N_CUSTOMERS)
    dim_branch = build_dim_branch(N_BRANCHES)
    dim_product = build_dim_product()
    dim_channel = build_dim_channel()

    print(f"Building Fact_Transactions ({N_TRANSACTIONS:,} rows)...")
    fact = build_fact_transactions(
        dim_date, dim_customer, dim_branch, dim_product, dim_channel, N_TRANSACTIONS
    )
    fact = add_revenue(fact, dim_product)

    # branch efficiency as enriched dimension
    dim_branch_eff = compute_branch_efficiency(fact, dim_branch)

    # ── write CSVs ────────────────────────────────────────────────────────────
    files = {
        "Fact_Transactions.csv": fact,
        "Dim_Customer.csv": dim_customer,
        "Dim_Branch.csv": dim_branch_eff,
        "Dim_Date.csv": dim_date,
        "Dim_Product.csv": dim_product,
        "Dim_Channel.csv": dim_channel,
    }

    for fname, df in files.items():
        path = OUTPUT_DIR / fname
        df.to_csv(path, index=False)
        print(f"  OK {fname:35s} {len(df):>8,} rows  ->  {path.relative_to(Path(__file__).parent.parent)}")

    # ── validation ────────────────────────────────────────────────────────────
    print("\nValidation:")
    assert len(fact) == N_TRANSACTIONS, "Row count mismatch"
    assert fact["transaction_id"].nunique() == N_TRANSACTIONS, "Duplicate transaction IDs"
    assert fact["amount"].min() >= 10.0, "Amount below minimum threshold"
    assert fact["transaction_date"].notna().all(), "Null transaction dates found"
    assert set(fact["channel"].unique()).issubset(set(CHANNELS)), "Unknown channel value"
    assert set(fact["transaction_type"].unique()).issubset(set(TRANSACTION_TYPES)), "Unknown txn type"

    digital_rate = fact["channel"].isin(DIGITAL_CHANNELS).mean()
    print(f"  Transaction count      : {len(fact):>10,}")
    print(f"  Date range             : {fact['transaction_date'].min()} to {fact['transaction_date'].max()}")
    print(f"  Avg transaction amount : £{fact['amount'].mean():>10,.2f}")
    print(f"  Digital adoption rate  : {digital_rate:.1%}")
    print(f"  Total revenue          : £{fact['revenue'].sum():>12,.2f}")
    print(f"  Unique customers       : {fact['customer_id'].nunique():>10,}")
    print(f"  Unique branches        : {fact['branch_id'].nunique():>10,}")
    print("\nDone. All CSV files written to data/csv/")


if __name__ == "__main__":
    main()
