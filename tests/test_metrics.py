"""
test_metrics.py
Pytest suite for BankLens metric computations.
Tests run against the generated CSV data (data/csv/).
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# make src importable without a running Streamlit server
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ── fixtures ──────────────────────────────────────────────────────────────────

CSV_DIR = Path(__file__).parent.parent / "data" / "csv"


@pytest.fixture(scope="session")
def fact() -> pd.DataFrame:
    df = pd.read_csv(CSV_DIR / "Fact_Transactions.csv", parse_dates=["transaction_date"])
    df["year_month"] = df["transaction_date"].dt.to_period("M").astype(str)
    return df


@pytest.fixture(scope="session")
def dim_customer() -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / "Dim_Customer.csv")


@pytest.fixture(scope="session")
def dim_branch() -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / "Dim_Branch.csv")


@pytest.fixture(scope="session")
def dim_product() -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / "Dim_Product.csv")


@pytest.fixture(scope="session")
def dim_channel() -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / "Dim_Channel.csv")


# ── 1. Schema & row-count checks ──────────────────────────────────────────────

class TestSchema:
    def test_fact_row_count(self, fact):
        assert len(fact) == 100_000, "Fact_Transactions must have exactly 100 000 rows"

    def test_fact_required_columns(self, fact):
        required = {
            "transaction_id", "customer_id", "branch_id", "date_id",
            "product_id", "channel_id", "amount", "transaction_type",
            "channel", "branch_name", "region", "product_line",
            "customer_segment", "transaction_date", "revenue",
        }
        assert required.issubset(fact.columns), f"Missing columns: {required - set(fact.columns)}"

    def test_no_null_keys(self, fact):
        for col in ["transaction_id", "customer_id", "branch_id", "product_id", "channel_id"]:
            assert fact[col].notna().all(), f"Null values found in FK column: {col}"

    def test_transaction_ids_unique(self, fact):
        assert fact["transaction_id"].nunique() == len(fact), "Duplicate transaction IDs detected"

    def test_dim_sizes(self, dim_customer, dim_branch, dim_product, dim_channel):
        assert len(dim_customer) == 8_000
        assert len(dim_branch) == 60
        assert len(dim_product) == 5
        assert len(dim_channel) == 4


# ── 2. Transaction Volume metric ──────────────────────────────────────────────

class TestTransactionVolume:
    def test_total_volume(self, fact):
        assert len(fact) == 100_000

    def test_volume_by_channel_covers_all_channels(self, fact):
        expected = {"branch", "ATM", "mobile_app", "online_banking"}
        assert set(fact["channel"].unique()) == expected

    def test_volume_by_type_covers_all_types(self, fact):
        expected = {"deposit", "withdrawal", "transfer", "payment", "loan_repayment"}
        assert set(fact["transaction_type"].unique()) == expected

    def test_monthly_volume_non_negative(self, fact):
        monthly = (
            fact.groupby("year_month")["transaction_id"]
            .count()
            .reset_index(name="count")
        )
        assert (monthly["count"] >= 0).all()

    def test_date_range(self, fact):
        assert fact["transaction_date"].min().year == 2022
        assert fact["transaction_date"].max().year == 2024


# ── 3. Avg Transaction Value by Channel ───────────────────────────────────────

class TestAvgTransactionValue:
    def test_avg_value_positive(self, fact):
        avg_by_channel = fact.groupby("channel")["amount"].mean()
        assert (avg_by_channel > 0).all(), "Avg transaction value must be positive for all channels"

    def test_amount_minimum(self, fact):
        assert fact["amount"].min() >= 10.0, "All transaction amounts must be >= £10"

    def test_all_channel_avgs_above_floor(self, fact):
        """Every channel's avg transaction value must exceed the £10 floor."""
        avgs = fact.groupby("channel")["amount"].mean()
        assert (avgs > 10).all(), f"Some channel avg is at or below £10: {avgs.to_dict()}"


# ── 4. Digital Adoption Rate ──────────────────────────────────────────────────

class TestDigitalAdoptionRate:
    DIGITAL = {"mobile_app", "online_banking"}

    def test_rate_between_0_and_1(self, fact):
        rate = fact["channel"].isin(self.DIGITAL).mean()
        assert 0.0 < rate < 1.0

    def test_rate_roughly_55_percent(self, fact):
        """Generator weights: mobile_app 30% + online_banking 25% = 55% digital."""
        rate = fact["channel"].isin(self.DIGITAL).mean()
        assert 0.50 <= rate <= 0.60, f"Digital adoption rate {rate:.1%} outside expected 50-60% band"

    def test_digital_trend_has_all_months(self, fact):
        monthly = (
            fact.groupby("year_month")["transaction_id"]
            .count()
            .reset_index()
        )
        # 2022–2024 = 36 months
        assert len(monthly) == 36, f"Expected 36 year_month buckets, got {len(monthly)}"


# ── 5. CLV Proxy ──────────────────────────────────────────────────────────────

class TestCLVProxy:
    def test_clv_formula(self, dim_customer):
        """CLV proxy = avg_balance * tenure_months * 0.02  (tolerance: ±0.02 for float rounding)."""
        expected = dim_customer["avg_balance"] * dim_customer["tenure_months"] * 0.02
        diff = (dim_customer["clv_proxy"] - expected).abs()
        assert (diff <= 0.02).all(), f"CLV formula mismatch; max diff = {diff.max():.4f}"

    def test_clv_positive(self, dim_customer):
        assert (dim_customer["clv_proxy"] > 0).all()

    def test_private_banking_clv_greater_than_mass(self, dim_customer):
        avg_clv = dim_customer.groupby("customer_segment")["clv_proxy"].mean()
        assert avg_clv["private_banking"] > avg_clv["mass"], (
            "private_banking segment should have higher avg CLV than mass"
        )


# ── 6. Branch Efficiency Score ────────────────────────────────────────────────

class TestBranchEfficiency:
    def test_efficiency_non_negative(self, dim_branch):
        assert (dim_branch["branch_efficiency_score"] >= 0).all()

    def test_efficiency_formula(self, dim_branch):
        """efficiency = total_revenue / headcount"""
        expected = (dim_branch["total_revenue"] / dim_branch["headcount"]).round(2)
        pd.testing.assert_series_equal(
            dim_branch["branch_efficiency_score"].round(2),
            expected,
            check_names=False,
        )

    def test_all_branches_present(self, dim_branch):
        assert len(dim_branch) == 60


# ── 7. Revenue by Product Line ────────────────────────────────────────────────

class TestRevenueByProduct:
    def test_revenue_non_negative(self, fact):
        assert (fact["revenue"] >= 0).all()

    def test_all_product_lines_have_revenue(self, fact):
        rev = fact.groupby("product_line")["revenue"].sum()
        assert (rev > 0).all(), "Every product line should have positive revenue"

    def test_product_lines_match_dim(self, fact, dim_product):
        fact_lines = set(fact["product_line"].unique())
        dim_lines = set(dim_product["product_line"].unique())
        assert fact_lines == dim_lines

    def test_revenue_rate_applied_correctly(self, fact, dim_product):
        """Spot-check: personal_loan (rate=0.06) should yield higher revenue per £ than retail_savings (0.01)."""
        rev_per_amount = fact.groupby("product_line").apply(
            lambda g: g["revenue"].sum() / g["amount"].sum()
        )
        assert rev_per_amount["personal_loan"] > rev_per_amount["retail_savings"]
