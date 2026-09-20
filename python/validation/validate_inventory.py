"""
ORGEE — INVENTORY VALIDATION

Validates:
    inventory_observations.csv

Checks:
    1. File existence
    2. Schema
    3. Required fields
    4. Row count
    5. Observation ID uniqueness
    6. Product referential integrity
    7. Inventory location integrity
    8. Product-location pair count
    9. Observations per pair
    10. Quantity validity
    11. Inventory status validity
    12. Status/quantity consistency
    13. Timestamp validity
    14. Distribution sanity
"""


from pathlib import Path

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "inventory"
    / "inventory_observations.csv"
)

PRODUCTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_products_dataset.csv"
)


# ============================================================
# EXPECTED CONFIGURATION
# ============================================================

EXPECTED_ROW_COUNT = 1_000_000

EXPECTED_LOCATION_COUNT = 20

EXPECTED_PRODUCT_LOCATION_PAIRS = 50_000

EXPECTED_OBSERVATIONS_PER_PAIR = 20


# ============================================================
# ALLOWED VALUES
# ============================================================

ALLOWED_STATUS_VALUES = {
    "in_stock",
    "low_stock",
    "out_of_stock",
}


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "inventory_observation_id",
    "product_id",
    "inventory_location_id",
    "observation_timestamp",
    "available_quantity",
    "reserved_quantity",
    "inventory_status",
}


# ============================================================
# HELPER
# ============================================================

def fail(message: str) -> None:
    raise ValueError(
        f"[INVENTORY VALIDATION FAILED] {message}"
    )


def require_columns(
    dataframe: pd.DataFrame,
) -> None:

    missing = (
        REQUIRED_COLUMNS
        -
        set(dataframe.columns)
    )

    if missing:

        fail(
            "Missing inventory columns: "
            f"{sorted(missing)}\n"
            f"Actual columns: "
            f"{list(dataframe.columns)}"
        )


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("ORGEE — INVENTORY VALIDATION")
print("=" * 70)


# ============================================================
# FILE EXISTENCE
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking required files..."
)


if not INVENTORY_FILE.exists():

    fail(
        f"Inventory file not found:\n"
        f"{INVENTORY_FILE}"
    )


if not PRODUCTS_FILE.exists():

    fail(
        f"Public products file not found:\n"
        f"{PRODUCTS_FILE}"
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Required files exist."
)


# ============================================================
# LOAD INVENTORY
# ============================================================

print(
    "\n[INVENTORY VALIDATION] "
    "Loading inventory..."
)

inventory = pd.read_csv(
    INVENTORY_FILE
)

print(
    f"[INVENTORY VALIDATION] "
    f"Loaded {len(inventory):,} observations."
)


# ============================================================
# SCHEMA
# ============================================================

print(
    "\n[INVENTORY VALIDATION] "
    "Checking schema..."
)

require_columns(
    inventory
)

print(
    "[INVENTORY VALIDATION PASSED] "
    "Schema validation passed."
)


# ============================================================
# REQUIRED FIELDS
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking required fields..."
)

for column in REQUIRED_COLUMNS:

    null_count = int(
        inventory[column]
        .isna()
        .sum()
    )

    if null_count > 0:

        fail(
            f"Column '{column}' contains "
            f"{null_count:,} null values."
        )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Required-field completeness passed."
)


# ============================================================
# ROW COUNT
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking row count..."
)

if len(inventory) != EXPECTED_ROW_COUNT:

    fail(
        f"Expected {EXPECTED_ROW_COUNT:,} inventory "
        f"observations, found {len(inventory):,}."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    f"Row count = {len(inventory):,}."
)


# ============================================================
# OBSERVATION ID
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking inventory_observation_id..."
)

inventory[
    "inventory_observation_id"
] = (
    inventory[
        "inventory_observation_id"
    ]
    .astype(str)
    .str.strip()
)


if (
    inventory[
        "inventory_observation_id"
    ]
    .eq("")
    .any()
):

    fail(
        "Blank inventory_observation_id values detected."
    )


duplicate_observations = (
    inventory[
        "inventory_observation_id"
    ]
    .duplicated()
)


if duplicate_observations.any():

    fail(
        "Duplicate inventory_observation_id values "
        f"detected: {duplicate_observations.sum():,}"
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "inventory_observation_id uniqueness passed."
)


# ============================================================
# PRODUCT IDs
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking product IDs..."
)

inventory["product_id"] = (
    inventory["product_id"]
    .astype(str)
    .str.strip()
)


if (
    inventory["product_id"]
    .eq("")
    .any()
):

    fail(
        "Blank product_id values detected."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Product-ID format validation passed."
)


# ============================================================
# LOAD PUBLIC PRODUCTS
# ============================================================

print(
    "\n[INVENTORY VALIDATION] "
    "Loading public products..."
)

products = pd.read_csv(
    PRODUCTS_FILE,
    usecols=[
        "product_id",
    ],
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
    f"[INVENTORY VALIDATION] "
    f"Loaded {len(valid_product_ids):,} "
    "public products."
)


# ============================================================
# PRODUCT REFERENTIAL INTEGRITY
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking product referential integrity..."
)

inventory_product_ids = set(
    inventory["product_id"]
)


invalid_products = (
    inventory_product_ids
    -
    valid_product_ids
)


if invalid_products:

    fail(
        f"Found {len(invalid_products):,} "
        "product IDs in inventory that do not "
        "exist in the public product reference."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Product referential integrity passed."
)


# ============================================================
# INVENTORY LOCATION IDs
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking inventory locations..."
)

inventory[
    "inventory_location_id"
] = (
    inventory[
        "inventory_location_id"
    ]
    .astype(str)
    .str.strip()
)


if (
    inventory[
        "inventory_location_id"
    ]
    .eq("")
    .any()
):

    fail(
        "Blank inventory_location_id values detected."
    )


location_count = (
    inventory[
        "inventory_location_id"
    ]
    .nunique()
)


if location_count != EXPECTED_LOCATION_COUNT:

    fail(
        f"Expected {EXPECTED_LOCATION_COUNT} "
        f"inventory locations, found "
        f"{location_count}."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    f"Inventory location count = {location_count}."
)


# ============================================================
# PRODUCT-LOCATION PAIRS
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking product-location combinations..."
)

product_location_pairs = (
    inventory[
        [
            "product_id",
            "inventory_location_id",
        ]
    ]
    .drop_duplicates()
)


pair_count = len(
    product_location_pairs
)


if pair_count != EXPECTED_PRODUCT_LOCATION_PAIRS:

    fail(
        f"Expected {EXPECTED_PRODUCT_LOCATION_PAIRS:,} "
        f"product-location pairs, found "
        f"{pair_count:,}."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    f"Product-location pairs = {pair_count:,}."
)


# ============================================================
# OBSERVATIONS PER PAIR
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking observations per product-location pair..."
)

pair_observation_counts = (
    inventory
    .groupby(
        [
            "product_id",
            "inventory_location_id",
        ]
    )
    .size()
)


invalid_pair_counts = (
    pair_observation_counts
    != EXPECTED_OBSERVATIONS_PER_PAIR
)


if invalid_pair_counts.any():

    fail(
        f"{invalid_pair_counts.sum():,} "
        "product-location pairs do not contain exactly "
        f"{EXPECTED_OBSERVATIONS_PER_PAIR} observations."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    f"Each product-location pair contains "
    f"{EXPECTED_OBSERVATIONS_PER_PAIR} observations."
)


# ============================================================
# QUANTITY VALIDATION
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking inventory quantities..."
)

quantity_columns = [
    "available_quantity",
    "reserved_quantity",
]


for column in quantity_columns:

    if not pd.api.types.is_numeric_dtype(
        inventory[column]
    ):

        fail(
            f"{column} must be numeric."
        )


    negative_values = (
        inventory[column]
        < 0
    )


    if negative_values.any():

        fail(
            f"{negative_values.sum():,} negative "
            f"values detected in {column}."
        )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Inventory quantity validation passed."
)


# ============================================================
# QUANTITY RELATIONSHIP
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking quantity relationships..."
)

if (
    inventory["reserved_quantity"]
    >
    inventory["available_quantity"]
    +
    inventory["reserved_quantity"]
).any():

    fail(
        "Invalid reserved_quantity relationship detected."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Quantity relationship validation passed."
)


# ============================================================
# INVENTORY STATUS
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking inventory status..."
)

inventory[
    "inventory_status"
] = (
    inventory[
        "inventory_status"
    ]
    .astype(str)
    .str.strip()
)


invalid_status = (
    ~inventory[
        "inventory_status"
    ].isin(
        ALLOWED_STATUS_VALUES
    )
)


if invalid_status.any():

    values = sorted(
        inventory.loc[
            invalid_status,
            "inventory_status",
        ]
        .unique()
        .tolist()
    )

    fail(
        f"Invalid inventory_status values: "
        f"{values}"
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Inventory status validation passed."
)


# ============================================================
# STATUS / QUANTITY CONSISTENCY
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking status consistency..."
)


invalid_in_stock = (
    (
        inventory[
            "inventory_status"
        ]
        ==
        "in_stock"
    )
    &
    (
        inventory[
            "available_quantity"
        ]
        <= 0
    )
)


invalid_low_stock = (
    (
        inventory[
            "inventory_status"
        ]
        ==
        "low_stock"
    )
    &
    (
        inventory[
            "available_quantity"
        ]
        <= 0
    )
)


invalid_out_of_stock = (
    (
        inventory[
            "inventory_status"
        ]
        ==
        "out_of_stock"
    )
    &
    (
        inventory[
            "available_quantity"
        ]
        != 0
    )
)


status_errors = (
    invalid_in_stock
    |
    invalid_low_stock
    |
    invalid_out_of_stock
)


if status_errors.any():

    fail(
        f"{status_errors.sum():,} rows contain "
        "inconsistent inventory status and "
        "available quantity."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Status consistency validation passed."
)


# ============================================================
# TIMESTAMP VALIDATION
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "Checking timestamps..."
)

inventory[
    "observation_timestamp"
] = pd.to_datetime(
    inventory[
        "observation_timestamp"
    ],
    errors="coerce",
)


invalid_timestamps = (
    inventory[
        "observation_timestamp"
    ]
    .isna()
)


if invalid_timestamps.any():

    fail(
        f"{invalid_timestamps.sum():,} invalid "
        "observation_timestamp values detected."
    )


period_start = (
    inventory[
        "observation_timestamp"
    ]
    .min()
)


period_end = (
    inventory[
        "observation_timestamp"
    ]
    .max()
)


if period_start >= period_end:

    fail(
        "Invalid inventory observation period."
    )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Timestamp validation passed."
)


print(
    f"[INVENTORY VALIDATION] "
    f"Period start: {period_start}"
)


print(
    f"[INVENTORY VALIDATION] "
    f"Period end:   {period_end}"
)


# ============================================================
# STATUS DISTRIBUTION
# ============================================================

print(
    "\n[INVENTORY VALIDATION] "
    "Inventory status distribution:"
)

status_distribution = (
    inventory[
        "inventory_status"
    ]
    .value_counts(
        normalize=True
    )
    *
    100
)


for status in [
    "in_stock",
    "low_stock",
    "out_of_stock",
]:

    percentage = (
        status_distribution
        .get(
            status,
            0.0,
        )
    )

    print(
        f"    {status:<15} = "
        f"{percentage:6.2f}%"
    )


# Every configured status must exist.

for status in ALLOWED_STATUS_VALUES:

    if (
        status_distribution
        .get(status, 0.0)
        ==
        0
    ):

        fail(
            f"Inventory status '{status}' "
            "has zero observations."
        )


print(
    "[INVENTORY VALIDATION PASSED] "
    "Distribution sanity validation passed."
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)

print(
    "[INVENTORY VALIDATION] SUMMARY"
)

print("=" * 70)


print(
    f"Observations           = "
    f"{len(inventory):,}"
)


print(
    f"Unique products        = "
    f"{inventory['product_id'].nunique():,}"
)


print(
    f"Inventory locations    = "
    f"{location_count:,}"
)


print(
    f"Product-location pairs = "
    f"{pair_count:,}"
)


print(
    f"Observations per pair  = "
    f"{EXPECTED_OBSERVATIONS_PER_PAIR}"
)


print(
    f"Period start           = "
    f"{period_start}"
)


print(
    f"Period end             = "
    f"{period_end}"
)


print("=" * 70)


# ============================================================
# COMPLETE
# ============================================================

print(
    "[INVENTORY VALIDATION] "
    "COMPLETE — ALL CHECKS PASSED"
)

print("=" * 70)