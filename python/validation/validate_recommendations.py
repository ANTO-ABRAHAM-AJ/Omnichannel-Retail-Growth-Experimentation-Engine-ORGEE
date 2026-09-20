"""
ORGEE — RECOMMENDATION VALIDATION

Validates:
    recommendation_events.csv

Checks:
    - Required files
    - Schema
    - Required fields
    - Row count
    - Recommendation event ID uniqueness
    - Session referential integrity
    - Customer referential integrity
    - Anonymous identity integrity
    - Session / anonymous consistency
    - Session / customer consistency
    - Product referential integrity
    - Experiment referential integrity
    - Variant validity
    - Experiment assignment consistency
    - Event-type validity
    - Timestamp validity
    - Recommendation funnel sanity
    - Experiment distribution
    - Variant distribution
    - Primary experiment presence
    - Temporal range
"""

from pathlib import Path

import pandas as pd


# ============================================================
# ORGEE — RECOMMENDATION VALIDATION
# ============================================================

print("=" * 70)
print("ORGEE — RECOMMENDATION VALIDATION")
print("=" * 70)


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RECOMMENDATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "recommendations"
    / "recommendation_events.csv"
)

SESSIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "sessions"
    / "sessions.csv"
)

CUSTOMERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_customers_dataset.csv"
)

PRODUCTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_products_dataset.csv"
)

EXPERIMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "experiments"
    / "experiments.csv"
)

ASSIGNMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "experiments"
    / "experiment_assignments.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_MIN_EVENTS = 1

PRIMARY_EXPERIMENT = "exp_001"

ALLOWED_EVENT_TYPES = {
    "recommendation_impression",
    "recommendation_click",
    "recommendation_conversion",
}

ALLOWED_VARIANTS = {
    "control",
    "treatment",
}


# ============================================================
# HELPERS
# ============================================================

def fail(message: str) -> None:
    raise ValueError(
        f"[RECOMMENDATION VALIDATION FAILED] {message}"
    )


def require_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:

    missing = (
        required_columns
        - set(dataframe.columns)
    )

    if missing:

        fail(
            f"Missing {dataset_name} columns: "
            f"{sorted(missing)}\n"
            f"Actual columns: "
            f"{list(dataframe.columns)}"
        )


# ============================================================
# REQUIRED FILES
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking required files..."
)

required_files = [
    (
        RECOMMENDATION_FILE,
        "Recommendation events",
    ),
    (
        SESSIONS_FILE,
        "Sessions",
    ),
    (
        CUSTOMERS_FILE,
        "Customers",
    ),
    (
        PRODUCTS_FILE,
        "Products",
    ),
    (
        EXPERIMENTS_FILE,
        "Experiments",
    ),
    (
        ASSIGNMENTS_FILE,
        "Experiment assignments",
    ),
]

for file_path, name in required_files:

    if not file_path.exists():

        fail(
            f"{name} file not found:\n"
            f"{file_path}"
        )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Required files exist."
)


# ============================================================
# LOAD RECOMMENDATION EVENTS
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Loading recommendation events..."
)

recommendations = pd.read_csv(
    RECOMMENDATION_FILE
)

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(recommendations):,} "
    "recommendation events."
)


# ============================================================
# SCHEMA
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Checking schema..."
)

REQUIRED_RECOMMENDATION_COLUMNS = {
    "recommendation_event_id",
    "event_type",
    "session_id",
    "anonymous_id",
    "customer_id",
    "product_id",
    "experiment_id",
    "variant",
    "event_timestamp",
}

require_columns(
    recommendations,
    REQUIRED_RECOMMENDATION_COLUMNS,
    "recommendation event",
)

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Schema validation passed."
)


# ============================================================
# REQUIRED FIELDS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking required fields..."
)

for column in REQUIRED_RECOMMENDATION_COLUMNS:

    null_count = int(
        recommendations[column]
        .isna()
        .sum()
    )

    if null_count > 0:

        fail(
            f"Column '{column}' contains "
            f"{null_count:,} null values."
        )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Required-field completeness passed."
)


# ============================================================
# ROW COUNT
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking row count..."
)

if len(recommendations) < EXPECTED_MIN_EVENTS:

    fail(
        "Recommendation event dataset is empty."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    f"Row count = {len(recommendations):,}."
)


# ============================================================
# NORMALIZE IDENTIFIERS
# ============================================================

recommendations[
    "recommendation_event_id"
] = (
    recommendations[
        "recommendation_event_id"
    ]
    .astype(str)
    .str.strip()
)

recommendations["session_id"] = (
    recommendations["session_id"]
    .astype(str)
    .str.strip()
)

recommendations["anonymous_id"] = (
    recommendations["anonymous_id"]
    .astype(str)
    .str.strip()
)

recommendations["customer_id"] = (
    recommendations["customer_id"]
    .astype(str)
    .str.strip()
)

recommendations["product_id"] = (
    recommendations["product_id"]
    .astype(str)
    .str.strip()
)

recommendations["experiment_id"] = (
    recommendations["experiment_id"]
    .astype(str)
    .str.strip()
)

recommendations["variant"] = (
    recommendations["variant"]
    .astype(str)
    .str.strip()
)

recommendations["event_type"] = (
    recommendations["event_type"]
    .astype(str)
    .str.strip()
)


# ============================================================
# EVENT ID UNIQUENESS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking recommendation_event_id..."
)

duplicate_events = (
    recommendations[
        "recommendation_event_id"
    ]
    .duplicated()
)

if duplicate_events.any():

    count = int(
        duplicate_events.sum()
    )

    fail(
        f"Duplicate recommendation_event_id "
        f"values detected: {count:,}"
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Recommendation event ID uniqueness passed."
)


# ============================================================
# LOAD SESSIONS
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Loading enterprise sessions..."
)

sessions = pd.read_csv(
    SESSIONS_FILE,
    usecols=[
        "session_id",
        "anonymous_id",
        "customer_id",
    ],
)

sessions["session_id"] = (
    sessions["session_id"]
    .astype(str)
    .str.strip()
)

sessions["anonymous_id"] = (
    sessions["anonymous_id"]
    .astype(str)
    .str.strip()
)

sessions["customer_id"] = (
    sessions["customer_id"]
    .astype(str)
    .str.strip()
)

valid_session_ids = set(
    sessions["session_id"]
)

session_anonymous_map = (
    sessions
    .set_index("session_id")[
        "anonymous_id"
    ]
    .to_dict()
)

session_customer_map = (
    sessions
    .set_index("session_id")[
        "customer_id"
    ]
    .to_dict()
)

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(sessions):,} sessions."
)


# ============================================================
# LOAD CUSTOMERS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Loading public customers..."
)

customers = pd.read_csv(
    CUSTOMERS_FILE,
    usecols=["customer_id"],
)

customers["customer_id"] = (
    customers["customer_id"]
    .astype(str)
    .str.strip()
)

valid_customer_ids = set(
    customers["customer_id"]
)

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(customers):,} customers."
)


# ============================================================
# LOAD PRODUCTS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Loading public products..."
)

products = pd.read_csv(
    PRODUCTS_FILE,
    usecols=["product_id"],
)

products["product_id"] = (
    products["product_id"]
    .astype(str)
    .str.strip()
)

valid_product_ids = set(
    products["product_id"]
)

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(products):,} products."
)


# ============================================================
# LOAD EXPERIMENTS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Loading experiments..."
)

experiments = pd.read_csv(
    EXPERIMENTS_FILE
)

experiments["experiment_id"] = (
    experiments["experiment_id"]
    .astype(str)
    .str.strip()
)

valid_experiment_ids = set(
    experiments["experiment_id"]
)

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(experiments):,} experiments."
)


# ============================================================
# LOAD EXPERIMENT ASSIGNMENTS
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Loading experiment assignments..."
)

assignments = pd.read_csv(
    ASSIGNMENTS_FILE
)

assignments["experiment_id"] = (
    assignments["experiment_id"]
    .astype(str)
    .str.strip()
)

assignments["customer_id"] = (
    assignments["customer_id"]
    .astype(str)
    .str.strip()
)

assignments["variant"] = (
    assignments["variant"]
    .astype(str)
    .str.strip()
)

valid_assignment_pairs = set(
    zip(
        assignments["experiment_id"],
        assignments["customer_id"],
    )
)

assignment_variant_map = {
    (
        row["experiment_id"],
        row["customer_id"],
    ): row["variant"]
    for _, row in assignments.iterrows()
}

print(
    f"[RECOMMENDATION VALIDATION] "
    f"Loaded {len(assignments):,} assignments."
)


# ============================================================
# EVENT TYPE VALIDATION
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Checking event types..."
)

invalid_event_types = (
    ~recommendations["event_type"].isin(
        ALLOWED_EVENT_TYPES
    )
)

if invalid_event_types.any():

    values = sorted(
        recommendations.loc[
            invalid_event_types,
            "event_type",
        ]
        .unique()
        .tolist()
    )

    fail(
        f"Invalid recommendation event types: "
        f"{values}"
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Event-type validation passed."
)


# ============================================================
# SESSION REFERENTIAL INTEGRITY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking session referential integrity..."
)

invalid_sessions = (
    set(recommendations["session_id"])
    -
    valid_session_ids
)

if invalid_sessions:

    fail(
        f"Found {len(invalid_sessions):,} "
        "invalid session IDs."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Session referential integrity passed."
)


# ============================================================
# CUSTOMER REFERENTIAL INTEGRITY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking customer referential integrity..."
)

invalid_customers = (
    set(recommendations["customer_id"])
    -
    valid_customer_ids
)

if invalid_customers:

    fail(
        f"Found {len(invalid_customers):,} "
        "invalid customer IDs."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Customer referential integrity passed."
)


# ============================================================
# PRODUCT REFERENTIAL INTEGRITY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking product referential integrity..."
)

invalid_products = (
    set(recommendations["product_id"])
    -
    valid_product_ids
)

if invalid_products:

    fail(
        f"Found {len(invalid_products):,} "
        "invalid product IDs."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Product referential integrity passed."
)


# ============================================================
# ANONYMOUS ID VALIDATION
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking anonymous identities..."
)

invalid_anonymous = (
    ~recommendations["anonymous_id"]
    .str.startswith("anon_")
)

if invalid_anonymous.any():

    count = int(
        invalid_anonymous.sum()
    )

    fail(
        f"{count:,} invalid anonymous_id values."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Anonymous identity validation passed."
)


# ============================================================
# SESSION / ANONYMOUS CONSISTENCY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking session-anonymous consistency..."
)

expected_anonymous = (
    recommendations["session_id"]
    .map(session_anonymous_map)
)

anonymous_mismatch = (
    recommendations["anonymous_id"]
    !=
    expected_anonymous
)

if anonymous_mismatch.any():

    count = int(
        anonymous_mismatch.sum()
    )

    fail(
        f"{count:,} recommendation events "
        "have session/anonymous mismatches."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Session-anonymous consistency passed."
)


# ============================================================
# SESSION / CUSTOMER CONSISTENCY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking session-customer consistency..."
)

expected_customer = (
    recommendations["session_id"]
    .map(session_customer_map)
)

customer_mismatch = (
    recommendations["customer_id"]
    !=
    expected_customer
)

if customer_mismatch.any():

    count = int(
        customer_mismatch.sum()
    )

    fail(
        f"{count:,} recommendation events "
        "have session/customer mismatches."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Session-customer consistency passed."
)


# ============================================================
# EXPERIMENT REFERENTIAL INTEGRITY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking experiment referential integrity..."
)

invalid_experiments = (
    set(recommendations["experiment_id"])
    -
    valid_experiment_ids
)

if invalid_experiments:

    fail(
        "Found invalid experiment IDs: "
        f"{sorted(invalid_experiments)}"
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Experiment referential integrity passed."
)


# ============================================================
# VARIANT VALIDATION
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking variants..."
)

invalid_variants = (
    ~recommendations["variant"].isin(
        ALLOWED_VARIANTS
    )
)

if invalid_variants.any():

    values = sorted(
        recommendations.loc[
            invalid_variants,
            "variant",
        ]
        .unique()
        .tolist()
    )

    fail(
        f"Invalid recommendation variants: "
        f"{values}"
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Variant validation passed."
)


# ============================================================
# EXPERIMENT ASSIGNMENT CONSISTENCY
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking experiment assignment consistency..."
)

assignment_keys = list(
    zip(
        recommendations["experiment_id"],
        recommendations["customer_id"],
    )
)

invalid_assignment_keys = [
    key
    for key in assignment_keys
    if key not in valid_assignment_pairs
]

if invalid_assignment_keys:

    fail(
        f"Found {len(invalid_assignment_keys):,} "
        "recommendation events without a matching "
        "experiment assignment."
    )

expected_variants = [
    assignment_variant_map[key]
    for key in assignment_keys
]

variant_mismatch = (
    recommendations["variant"].to_numpy()
    !=
    pd.Series(
        expected_variants
    ).to_numpy()
)

if variant_mismatch.any():

    count = int(
        variant_mismatch.sum()
    )

    fail(
        f"{count:,} recommendation events "
        "have variants inconsistent with "
        "experiment assignments."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Experiment assignment consistency passed."
)


# ============================================================
# TIMESTAMP VALIDATION
# ============================================================

print(
    "[RECOMMENDATION VALIDATION] "
    "Checking timestamps..."
)

recommendations["event_timestamp"] = (
    pd.to_datetime(
        recommendations["event_timestamp"],
        errors="coerce",
    )
)

invalid_timestamps = (
    recommendations["event_timestamp"]
    .isna()
)

if invalid_timestamps.any():

    count = int(
        invalid_timestamps.sum()
    )

    fail(
        f"{count:,} invalid "
        "recommendation event timestamps."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Timestamp validation passed."
)


# ============================================================
# EVENT DISTRIBUTION
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Recommendation event distribution:"
)

event_counts = (
    recommendations["event_type"]
    .value_counts()
)

event_percentages = (
    recommendations["event_type"]
    .value_counts(
        normalize=True
    )
    * 100
)

for event_type in sorted(
    event_counts.index
):

    print(
        f"    {event_type:<30} = "
        f"{event_counts[event_type]:>10,} "
        f"({event_percentages[event_type]:6.2f}%)"
    )


# ============================================================
# FUNNEL COUNTS
# ============================================================

impression_count = int(
    (
        recommendations["event_type"]
        ==
        "recommendation_impression"
    ).sum()
)

click_count = int(
    (
        recommendations["event_type"]
        ==
        "recommendation_click"
    ).sum()
)

conversion_count = int(
    (
        recommendations["event_type"]
        ==
        "recommendation_conversion"
    ).sum()
)


# ============================================================
# FUNNEL SANITY
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Checking recommendation funnel..."
)

if impression_count == 0:

    fail(
        "No recommendation impressions found."
    )

if click_count > impression_count:

    fail(
        "Recommendation clicks exceed impressions."
    )

if conversion_count > click_count:

    fail(
        "Recommendation conversions exceed clicks."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    "Recommendation funnel ordering passed."
)


# ============================================================
# FUNNEL METRICS
# ============================================================

ctr = (
    click_count
    /
    impression_count
)

click_to_conversion = (
    conversion_count
    /
    click_count
    if click_count > 0
    else 0
)

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Recommendation funnel:"
)

print(
    f"    Impressions          = "
    f"{impression_count:,}"
)

print(
    f"    Clicks               = "
    f"{click_count:,}"
)

print(
    f"    Conversions          = "
    f"{conversion_count:,}"
)

print(
    f"    Recommendation CTR   = "
    f"{ctr:.2%}"
)

print(
    f"    Click → Conversion   = "
    f"{click_to_conversion:.2%}"
)


# ============================================================
# EXPERIMENT DISTRIBUTION
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Experiment distribution:"
)

experiment_counts = (
    recommendations["experiment_id"]
    .value_counts()
    .sort_index()
)

for experiment_id, count in (
    experiment_counts.items()
):

    print(
        f"    {experiment_id:<12} = "
        f"{count:>10,}"
    )


# ============================================================
# VARIANT DISTRIBUTION
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Variant distribution:"
)

variant_counts = (
    recommendations["variant"]
    .value_counts()
)

total_recommendations = len(
    recommendations
)

for variant in sorted(
    variant_counts.index
):

    count = int(
        variant_counts[variant]
    )

    share = (
        count
        /
        total_recommendations
    )

    print(
        f"    {variant:<12} = "
        f"{count:>10,} "
        f"({share:.2%})"
    )


# ============================================================
# PRIMARY EXPERIMENT CHECK
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Checking primary experiment..."
)

if PRIMARY_EXPERIMENT not in valid_experiment_ids:

    fail(
        f"Primary experiment "
        f"{PRIMARY_EXPERIMENT} does not exist."
    )

primary_events = recommendations[
    recommendations["experiment_id"]
    ==
    PRIMARY_EXPERIMENT
]

if primary_events.empty:

    fail(
        f"No recommendation events found "
        f"for primary experiment "
        f"{PRIMARY_EXPERIMENT}."
    )

print(
    "[RECOMMENDATION VALIDATION PASSED] "
    f"Primary experiment {PRIMARY_EXPERIMENT} "
    "contains recommendation events."
)


# ============================================================
# TEMPORAL RANGE
# ============================================================

print(
    "\n[RECOMMENDATION VALIDATION] "
    "Recommendation event period:"
)

period_start = (
    recommendations[
        "event_timestamp"
    ].min()
)

period_end = (
    recommendations[
        "event_timestamp"
    ].max()
)

print(
    f"    Period start = "
    f"{period_start}"
)

print(
    f"    Period end   = "
    f"{period_end}"
)

if period_start >= period_end:

    fail(
        "Invalid recommendation event period."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("[RECOMMENDATION VALIDATION] SUMMARY")
print("=" * 70)

print(
    f"Recommendation events = "
    f"{len(recommendations):,}"
)

print(
    f"Impressions           = "
    f"{impression_count:,}"
)

print(
    f"Clicks                = "
    f"{click_count:,}"
)

print(
    f"Conversions           = "
    f"{conversion_count:,}"
)

print(
    f"Unique sessions       = "
    f"{recommendations['session_id'].nunique():,}"
)

print(
    f"Unique customers      = "
    f"{recommendations['customer_id'].nunique():,}"
)

print(
    f"Unique products       = "
    f"{recommendations['product_id'].nunique():,}"
)

print(
    f"Unique experiments    = "
    f"{recommendations['experiment_id'].nunique():,}"
)

print(
    f"Unique event IDs      = "
    f"{recommendations['recommendation_event_id'].nunique():,}"
)

print("=" * 70)

print(
    "[RECOMMENDATION VALIDATION] "
    "COMPLETE — ALL CHECKS PASSED"
)

print("=" * 70)