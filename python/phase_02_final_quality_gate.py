from pathlib import Path
import sys

import pandas as pd


# =============================================================================
# ORGEE — PHASE 2
# FINAL QUALITY GATE
# Omnichannel Retail & Growth Experimentation Engine
# =============================================================================
#
# PURPOSE
# -------
# Final validation gate for the complete ORGEE Phase 2 data foundation.
#
# IMPORTANT
# ---------
# - READ ONLY
# - Does NOT regenerate data
# - Does NOT clean data
# - Does NOT modify existing datasets
# - Does NOT delete records
# - Does NOT build warehouse tables
#
# This script validates:
#
#   1. Processed public data
#   2. Enterprise sessions
#   3. Enterprise events
#   4. Experiments
#   5. Experiment assignments
#   6. Inventory
#   7. Marketing
#   8. Recommendations
#   9. Cross-domain relationships
#  10. Final Phase 2 integrity
#
# =============================================================================


# =============================================================================
# 1. PROJECT PATH
# =============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "data"

PUBLIC_DIR = (
    DATA_DIR
    / "processed"
    / "public"
)

ENTERPRISE_DIR = (
    DATA_DIR
    / "enterprise"
)

SESSIONS_DIR = (
    ENTERPRISE_DIR
    / "sessions"
)

EVENTS_DIR = (
    ENTERPRISE_DIR
    / "events"
)

EXPERIMENTS_DIR = (
    ENTERPRISE_DIR
    / "experiments"
)

INVENTORY_DIR = (
    ENTERPRISE_DIR
    / "inventory"
)

MARKETING_DIR = (
    ENTERPRISE_DIR
    / "marketing"
)

RECOMMENDATIONS_DIR = (
    ENTERPRISE_DIR
    / "recommendations"
)


# =============================================================================
# 2. EXPECTED FILES
# =============================================================================

PUBLIC_FILES = {
    "orders": PUBLIC_DIR / "olist_orders_dataset.csv",
    "order_items": PUBLIC_DIR / "olist_order_items_dataset.csv",
    "products": PUBLIC_DIR / "olist_products_dataset.csv",
    "customers": PUBLIC_DIR / "olist_customers_dataset.csv",
    "sellers": PUBLIC_DIR / "olist_sellers_dataset.csv",
    "payments": PUBLIC_DIR / "olist_order_payments_dataset.csv",
    "reviews": PUBLIC_DIR / "olist_order_reviews_dataset.csv",
    "category_translation": (
        PUBLIC_DIR
        / "product_category_name_translation.csv"
    ),
}


ENTERPRISE_FILES = {
    "sessions": SESSIONS_DIR / "sessions.csv",
    "events": EVENTS_DIR / "events.csv",
    "experiments": EXPERIMENTS_DIR / "experiments.csv",
    "experiment_assignments": (
        EXPERIMENTS_DIR
        / "experiment_assignments.csv"
    ),
    "inventory": (
        INVENTORY_DIR
        / "inventory_observations.csv"
    ),
    "campaigns": (
        MARKETING_DIR
        / "campaigns.csv"
    ),
    "campaign_exposures": (
        MARKETING_DIR
        / "campaign_exposures.csv"
    ),
    "recommendations": (
        RECOMMENDATIONS_DIR
        / "recommendation_events.csv"
    ),
}


# =============================================================================
# 3. EXPECTED VOLUMES
# =============================================================================

EXPECTED_SESSIONS = 500_000
EXPECTED_EVENTS = 3_000_000
EXPECTED_EXPERIMENTS = 3
EXPECTED_ASSIGNMENTS = 298_323
EXPECTED_INVENTORY = 1_000_000
EXPECTED_CAMPAIGNS = 50
EXPECTED_CAMPAIGN_EXPOSURES = 1_000_000


# =============================================================================
# 4. VALIDATION STATE
# =============================================================================

failures = []
warnings = []


def fail(message: str) -> None:

    failures.append(message)

    print(
        f"[FAIL] {message}"
    )


def passed(message: str) -> None:

    print(
        f"[PASS] {message}"
    )


def warning(message: str) -> None:

    warnings.append(message)

    print(
        f"[WARNING] {message}"
    )


def require_columns(
    df: pd.DataFrame,
    columns: set[str],
    dataset_name: str,
) -> bool:

    missing = (
        columns
        - set(df.columns)
    )

    if missing:

        fail(
            f"{dataset_name} missing columns: "
            f"{sorted(missing)}"
        )

        return False

    passed(
        f"{dataset_name} schema passed."
    )

    return True


def load_csv(
    path: Path,
    name: str,
) -> pd.DataFrame | None:

    if not path.exists():

        fail(
            f"{name} file not found: {path}"
        )

        return None

    try:

        df = pd.read_csv(path)

        print(
            f"[LOAD] {name:<25} "
            f"= {len(df):,} rows"
        )

        return df

    except Exception as exc:

        fail(
            f"Unable to load {name}: {exc}"
        )

        return None


def check_unique(
    df: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> None:

    if column not in df.columns:
        return

    null_count = int(
        df[column].isna().sum()
    )

    duplicate_count = int(
        df[column].duplicated().sum()
    )

    if null_count > 0:

        fail(
            f"{dataset_name}.{column} contains "
            f"{null_count:,} null values."
        )

    if duplicate_count > 0:

        fail(
            f"{dataset_name}.{column} contains "
            f"{duplicate_count:,} duplicates."
        )

    if (
        null_count == 0
        and duplicate_count == 0
    ):

        passed(
            f"{dataset_name}.{column} uniqueness passed."
        )


def check_reference(
    child_df: pd.DataFrame,
    child_column: str,
    parent_df: pd.DataFrame,
    parent_column: str,
    relationship: str,
) -> None:

    if (
        child_column not in child_df.columns
        or parent_column not in parent_df.columns
    ):

        return

    child_values = set(
        child_df[child_column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    parent_values = set(
        parent_df[parent_column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    unmatched = (
        child_values
        - parent_values
    )

    if unmatched:

        fail(
            f"{relationship}: "
            f"{len(unmatched):,} unmatched keys."
        )

    else:

        passed(
            f"{relationship}: "
            f"referential integrity passed."
        )


# =============================================================================
# 5. HEADER
# =============================================================================

print()
print("=" * 80)
print(
    "ORGEE — PHASE 2 FINAL QUALITY GATE"
)
print(
    "Omnichannel Retail & Growth Experimentation Engine"
)
print("=" * 80)

print()
print("Project Directory:")
print(PROJECT_DIR)

print()
print("Public Data Directory:")
print(PUBLIC_DIR)

print()
print("Enterprise Data Directory:")
print(ENTERPRISE_DIR)


# =============================================================================
# 6. FILE EXISTENCE
# =============================================================================

print()
print("-" * 80)
print("CHECKING REQUIRED FILES")
print("-" * 80)


for name, path in {
    **PUBLIC_FILES,
    **ENTERPRISE_FILES,
}.items():

    if path.exists():

        passed(
            f"{name:<25} {path.name}"
        )

    else:

        fail(
            f"{name:<25} MISSING — {path}"
        )


# =============================================================================
# 7. LOAD PUBLIC DATA
# =============================================================================

print()
print("-" * 80)
print("LOADING PROCESSED PUBLIC DATA")
print("-" * 80)


orders = load_csv(
    PUBLIC_FILES["orders"],
    "Orders",
)

order_items = load_csv(
    PUBLIC_FILES["order_items"],
    "Order items",
)

products = load_csv(
    PUBLIC_FILES["products"],
    "Products",
)

customers = load_csv(
    PUBLIC_FILES["customers"],
    "Customers",
)

sellers = load_csv(
    PUBLIC_FILES["sellers"],
    "Sellers",
)

payments = load_csv(
    PUBLIC_FILES["payments"],
    "Payments",
)

reviews = load_csv(
    PUBLIC_FILES["reviews"],
    "Reviews",
)

category_translation = load_csv(
    PUBLIC_FILES["category_translation"],
    "Category translations",
)


# =============================================================================
# 8. PUBLIC DATA SCHEMA
# =============================================================================

print()
print("-" * 80)
print("PUBLIC DATA SCHEMA VALIDATION")
print("-" * 80)


if orders is not None:

    require_columns(
        orders,
        {
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        },
        "Orders",
    )


if order_items is not None:

    require_columns(
        order_items,
        {
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        },
        "Order items",
    )


if products is not None:

    require_columns(
        products,
        {
            "product_id",
            "product_category_name",
        },
        "Products",
    )


if customers is not None:

    require_columns(
        customers,
        {
            "customer_id",
            "customer_unique_id",
        },
        "Customers",
    )


if sellers is not None:

    require_columns(
        sellers,
        {
            "seller_id",
        },
        "Sellers",
    )


if payments is not None:

    require_columns(
        payments,
        {
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        },
        "Payments",
    )


if reviews is not None:

    require_columns(
        reviews,
        {
            "review_id",
            "order_id",
            "review_score",
        },
        "Reviews",
    )


# =============================================================================
# 9. PUBLIC DATA VOLUMES
# =============================================================================

print()
print("-" * 80)
print("PUBLIC DATA VOLUME VALIDATION")
print("-" * 80)


PUBLIC_EXPECTED_ROWS = {
    "Orders": (orders, 99_441),
    "Order items": (order_items, 112_650),
    "Products": (products, 32_951),
    "Customers": (customers, 99_441),
    "Sellers": (sellers, 3_095),
    "Payments": (payments, 103_886),
    "Reviews": (reviews, 99_224),
    "Category translations": (
        category_translation,
        71,
    ),
}


for name, (
    df,
    expected,
) in PUBLIC_EXPECTED_ROWS.items():

    if df is None:
        continue

    actual = len(df)

    if actual != expected:

        fail(
            f"{name}: expected "
            f"{expected:,} rows, found "
            f"{actual:,}."
        )

    else:

        passed(
            f"{name}: row count = "
            f"{actual:,}."
        )


# =============================================================================
# 10. PUBLIC KEY VALIDATION
# =============================================================================

print()
print("-" * 80)
print("PUBLIC KEY VALIDATION")
print("-" * 80)


if orders is not None:
    check_unique(
        orders,
        "order_id",
        "orders",
    )


if products is not None:
    check_unique(
        products,
        "product_id",
        "products",
    )


if customers is not None:
    check_unique(
        customers,
        "customer_id",
        "customers",
    )


if sellers is not None:
    check_unique(
        sellers,
        "seller_id",
        "sellers",
    )


# =============================================================================
# 11. PUBLIC RELATIONSHIPS
# =============================================================================

print()
print("-" * 80)
print("PUBLIC REFERENTIAL INTEGRITY")
print("-" * 80)


if (
    orders is not None
    and customers is not None
):

    check_reference(
        orders,
        "customer_id",
        customers,
        "customer_id",
        "ORDERS → CUSTOMERS",
    )


if (
    order_items is not None
    and orders is not None
):

    check_reference(
        order_items,
        "order_id",
        orders,
        "order_id",
        "ORDER_ITEMS → ORDERS",
    )


if (
    order_items is not None
    and products is not None
):

    check_reference(
        order_items,
        "product_id",
        products,
        "product_id",
        "ORDER_ITEMS → PRODUCTS",
    )


if (
    order_items is not None
    and sellers is not None
):

    check_reference(
        order_items,
        "seller_id",
        sellers,
        "seller_id",
        "ORDER_ITEMS → SELLERS",
    )


if (
    payments is not None
    and orders is not None
):

    check_reference(
        payments,
        "order_id",
        orders,
        "order_id",
        "PAYMENTS → ORDERS",
    )


if (
    reviews is not None
    and orders is not None
):

    check_reference(
        reviews,
        "order_id",
        orders,
        "order_id",
        "REVIEWS → ORDERS",
    )


# =============================================================================
# 12. PUBLIC TIMESTAMP QUALITY
# =============================================================================

print()
print("-" * 80)
print("PUBLIC TIMESTAMP QUALITY")
print("-" * 80)


if orders is not None:

    timestamp_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:

        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce",
        )

    timestamp_checks = [
        (
            "order_purchase_timestamp",
            "order_approved_at",
        ),
        (
            "order_approved_at",
            "order_delivered_carrier_date",
        ),
        (
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
        ),
    ]

    for earlier, later in timestamp_checks:

        mask = (
            orders[earlier].notna()
            & orders[later].notna()
        )

        invalid = (
            mask
            & (
                orders[later]
                <
                orders[earlier]
            )
        )

        count = int(
            invalid.sum()
        )

        if count > 0:

            warning(
                f"{earlier} → {later}: "
                f"{count:,} source timestamp anomalies "
                f"remain documented."
            )

        else:

            passed(
                f"{earlier} → {later}: "
                "no anomalies."
            )


# =============================================================================
# 13. LOAD ENTERPRISE DATA
# =============================================================================

print()
print("-" * 80)
print("LOADING ENTERPRISE DATA")
print("-" * 80)


sessions = load_csv(
    ENTERPRISE_FILES["sessions"],
    "Enterprise sessions",
)

events = load_csv(
    ENTERPRISE_FILES["events"],
    "Enterprise events",
)

experiments = load_csv(
    ENTERPRISE_FILES["experiments"],
    "Experiments",
)

assignments = load_csv(
    ENTERPRISE_FILES["experiment_assignments"],
    "Experiment assignments",
)

inventory = load_csv(
    ENTERPRISE_FILES["inventory"],
    "Inventory",
)

campaigns = load_csv(
    ENTERPRISE_FILES["campaigns"],
    "Campaigns",
)

campaign_exposures = load_csv(
    ENTERPRISE_FILES["campaign_exposures"],
    "Campaign exposures",
)

recommendations = load_csv(
    ENTERPRISE_FILES["recommendations"],
    "Recommendation events",
)


# =============================================================================
# 14. ENTERPRISE VOLUMES
# =============================================================================

print()
print("-" * 80)
print("ENTERPRISE DATA VOLUME VALIDATION")
print("-" * 80)


ENTERPRISE_EXPECTED_ROWS = {
    "Enterprise sessions": (
        sessions,
        EXPECTED_SESSIONS,
    ),
    "Enterprise events": (
        events,
        EXPECTED_EVENTS,
    ),
    "Experiments": (
        experiments,
        EXPECTED_EXPERIMENTS,
    ),
    "Experiment assignments": (
        assignments,
        EXPECTED_ASSIGNMENTS,
    ),
    "Inventory": (
        inventory,
        EXPECTED_INVENTORY,
    ),
    "Campaigns": (
        campaigns,
        EXPECTED_CAMPAIGNS,
    ),
    "Campaign exposures": (
        campaign_exposures,
        EXPECTED_CAMPAIGN_EXPOSURES,
    ),
}


for name, (
    df,
    expected,
) in ENTERPRISE_EXPECTED_ROWS.items():

    if df is None:
        continue

    actual = len(df)

    if actual != expected:

        fail(
            f"{name}: expected "
            f"{expected:,} rows, found "
            f"{actual:,}."
        )

    else:

        passed(
            f"{name}: row count = "
            f"{actual:,}."
        )


# =============================================================================
# 15. ENTERPRISE KEY VALIDATION
# =============================================================================

print()
print("-" * 80)
print("ENTERPRISE KEY VALIDATION")
print("-" * 80)


if sessions is not None:

    check_unique(
        sessions,
        "session_id",
        "sessions",
    )

    check_unique(
        sessions,
        "anonymous_id",
        "sessions",
    )


if events is not None:

    check_unique(
        events,
        "event_id",
        "events",
    )


if experiments is not None:

    check_unique(
        experiments,
        "experiment_id",
        "experiments",
    )


if assignments is not None:

    check_unique(
        assignments,
        "experiment_assignment_id",
        "experiment_assignments",
    )


if inventory is not None:

    check_unique(
        inventory,
        "inventory_observation_id",
        "inventory",
    )


if campaigns is not None:

    check_unique(
        campaigns,
        "campaign_id",
        "campaigns",
    )


if campaign_exposures is not None:

    check_unique(
        campaign_exposures,
        "campaign_exposure_id",
        "campaign_exposures",
    )


if recommendations is not None:

    check_unique(
        recommendations,
        "recommendation_event_id",
        "recommendations",
    )


# =============================================================================
# 16. ENTERPRISE CROSS-DOMAIN RELATIONSHIPS
# =============================================================================

print()
print("-" * 80)
print("ENTERPRISE CROSS-DOMAIN REFERENTIAL INTEGRITY")
print("-" * 80)


# -------------------------------------------------------------------------
# Events → Sessions
# -------------------------------------------------------------------------

if (
    events is not None
    and sessions is not None
):

    check_reference(
        events,
        "session_id",
        sessions,
        "session_id",
        "EVENTS → SESSIONS",
    )


# -------------------------------------------------------------------------
# Events → Customers
# -------------------------------------------------------------------------

if (
    events is not None
    and customers is not None
):

    if "customer_id" in events.columns:

        event_customer_ids = (
            events["customer_id"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        valid_customer_ids = set(
            customers["customer_id"]
            .astype(str)
            .str.strip()
        )

        unmatched = (
            set(event_customer_ids)
            -
            valid_customer_ids
        )

        if unmatched:

            fail(
                "EVENTS → CUSTOMERS: "
                f"{len(unmatched):,} unmatched customer IDs."
            )

        else:

            passed(
                "EVENTS → CUSTOMERS: "
                "referential integrity passed."
            )


# -------------------------------------------------------------------------
# Events → Products
# -------------------------------------------------------------------------

if (
    events is not None
    and products is not None
):

    if "product_id" in events.columns:

        event_products = (
            events["product_id"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        valid_products = set(
            products["product_id"]
            .astype(str)
            .str.strip()
        )

        unmatched = (
            set(event_products)
            -
            valid_products
        )

        if unmatched:

            fail(
                "EVENTS → PRODUCTS: "
                f"{len(unmatched):,} unmatched product IDs."
            )

        else:

            passed(
                "EVENTS → PRODUCTS: "
                "referential integrity passed."
            )


# -------------------------------------------------------------------------
# Inventory → Products
# -------------------------------------------------------------------------

if (
    inventory is not None
    and products is not None
):

    check_reference(
        inventory,
        "product_id",
        products,
        "product_id",
        "INVENTORY → PRODUCTS",
    )


# -------------------------------------------------------------------------
# Campaign exposures → Campaigns
# -------------------------------------------------------------------------

if (
    campaign_exposures is not None
    and campaigns is not None
):

    check_reference(
        campaign_exposures,
        "campaign_id",
        campaigns,
        "campaign_id",
        "CAMPAIGN_EXPOSURES → CAMPAIGNS",
    )


# -------------------------------------------------------------------------
# Campaign exposures → Sessions
# -------------------------------------------------------------------------

if (
    campaign_exposures is not None
    and sessions is not None
):

    check_reference(
        campaign_exposures,
        "session_id",
        sessions,
        "session_id",
        "CAMPAIGN_EXPOSURES → SESSIONS",
    )


# -------------------------------------------------------------------------
# Recommendations → Sessions
# -------------------------------------------------------------------------

if (
    recommendations is not None
    and sessions is not None
):

    check_reference(
        recommendations,
        "session_id",
        sessions,
        "session_id",
        "RECOMMENDATIONS → SESSIONS",
    )


# -------------------------------------------------------------------------
# Recommendations → Products
# -------------------------------------------------------------------------

if (
    recommendations is not None
    and products is not None
):

    check_reference(
        recommendations,
        "product_id",
        products,
        "product_id",
        "RECOMMENDATIONS → PRODUCTS",
    )


# -------------------------------------------------------------------------
# Recommendations → Experiments
# -------------------------------------------------------------------------

if (
    recommendations is not None
    and experiments is not None
):

    check_reference(
        recommendations,
        "experiment_id",
        experiments,
        "experiment_id",
        "RECOMMENDATIONS → EXPERIMENTS",
    )


# =============================================================================
# 17. EXPERIMENT ASSIGNMENT INTEGRITY
# =============================================================================

print()
print("-" * 80)
print("EXPERIMENT ASSIGNMENT INTEGRITY")
print("-" * 80)


if (
    assignments is not None
    and experiments is not None
):

    check_reference(
        assignments,
        "experiment_id",
        experiments,
        "experiment_id",
        "ASSIGNMENTS → EXPERIMENTS",
    )


if (
    assignments is not None
    and customers is not None
):

    check_reference(
        assignments,
        "customer_id",
        customers,
        "customer_id",
        "ASSIGNMENTS → CUSTOMERS",
    )


# =============================================================================
# 18. SESSION / CUSTOMER CONSISTENCY
# =============================================================================

print()
print("-" * 80)
print("SESSION / CUSTOMER CONSISTENCY")
print("-" * 80)


if (
    sessions is not None
    and customers is not None
):

    session_customer_ids = (
        sessions["customer_id"]
        .astype(str)
        .str.strip()
    )

    valid_customer_ids = set(
        customers["customer_id"]
        .astype(str)
        .str.strip()
    )

    unmatched = (
        set(session_customer_ids)
        -
        valid_customer_ids
    )

    if unmatched:

        fail(
            "SESSIONS → CUSTOMERS: "
            f"{len(unmatched):,} unmatched customer IDs."
        )

    else:

        passed(
            "SESSIONS → CUSTOMERS: "
            "referential integrity passed."
        )


# =============================================================================
# 19. EVENT TYPE SANITY
# =============================================================================

print()
print("-" * 80)
print("EVENT TYPE SANITY")
print("-" * 80)


if events is not None:

    if "event_type" in events.columns:

        event_types = (
            events["event_type"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if len(event_types) == len(events):

            passed(
                "All events contain event_type."
            )

        else:

            fail(
                "Events contain null event_type values."
            )


# =============================================================================
# 20. RECOMMENDATION FUNNEL
# =============================================================================

print()
print("-" * 80)
print("RECOMMENDATION FUNNEL")
print("-" * 80)


if recommendations is not None:

    if "event_type" in recommendations.columns:

        counts = (
            recommendations["event_type"]
            .value_counts()
        )

        impressions = int(
            counts.get(
                "recommendation_impression",
                0,
            )
        )

        clicks = int(
            counts.get(
                "recommendation_click",
                0,
            )
        )

        conversions = int(
            counts.get(
                "recommendation_conversion",
                0,
            )
        )

        print(
            f"Impressions = {impressions:,}"
        )

        print(
            f"Clicks      = {clicks:,}"
        )

        print(
            f"Conversions = {conversions:,}"
        )

        if clicks > impressions:

            fail(
                "Recommendation clicks exceed impressions."
            )

        elif conversions > clicks:

            fail(
                "Recommendation conversions exceed clicks."
            )

        else:

            passed(
                "Recommendation funnel ordering passed."
            )


# =============================================================================
# 21. EXPERIMENT DISTRIBUTION
# =============================================================================

print()
print("-" * 80)
print("EXPERIMENT DISTRIBUTION")
print("-" * 80)


if experiments is not None:

    if "experiment_id" in experiments.columns:

        experiment_ids = set(
            experiments["experiment_id"]
            .astype(str)
            .str.strip()
        )

        print(
            f"Experiment definitions = "
            f"{len(experiment_ids):,}"
        )

        if len(experiment_ids) == EXPECTED_EXPERIMENTS:

            passed(
                "Expected experiment count passed."
            )

        else:

            fail(
                f"Expected {EXPECTED_EXPERIMENTS} "
                f"experiments, found "
                f"{len(experiment_ids)}."
            )


if assignments is not None:

    if "experiment_id" in assignments.columns:

        print(
            "\nAssignment distribution:"
        )

        distribution = (
            assignments["experiment_id"]
            .value_counts()
            .sort_index()
        )

        for experiment_id, count in (
            distribution.items()
        ):

            print(
                f"    {experiment_id:<12} "
                f"= {count:>10,}"
            )


# =============================================================================
# 22. FINAL QUALITY-GATE DECISION
# =============================================================================

print()
print("=" * 80)
print("ORGEE — PHASE 2 FINAL QUALITY GATE")
print("=" * 80)


print()
print(
    f"Failures  = {len(failures):,}"
)

print(
    f"Warnings  = {len(warnings):,}"
)


if failures:

    print()
    print(
        "FINAL STATUS: FAILED"
    )

    print()
    print("Failures:")

    for item in failures:

        print(
            f"  ✗ {item}"
        )

    print()
    print(
        "Phase 2 is NOT approved for freeze."
    )

    print("=" * 80)

    sys.exit(1)


print()
print(
    "FINAL STATUS: PASSED"
)

if warnings:

    print()
    print(
        "Documented warnings:"
    )

    for item in warnings:

        print(
            f"  ⚠ {item}"
        )

print()
print(
    "Phase 2 data foundation is internally consistent."
)

print(
    "No dataset regeneration is required."
)

print(
    "No dataset modification was performed."
)

print(
    "Phase 2 is READY FOR FREEZE."
)

print()
print("=" * 80)
print(
    "ORGEE — PHASE 2 FINAL QUALITY GATE PASSED"
)
print("=" * 80)
print()


# =============================================================================
# 23. ENTRY POINT
# =============================================================================
