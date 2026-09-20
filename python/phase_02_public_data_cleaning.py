from pathlib import Path
import pandas as pd


# =============================================================================
# ORGEE — PHASE 2
# PUBLIC DATA CLEANING
# Omnichannel Retail & Growth Experimentation Engine
# =============================================================================
#
# Purpose:
#   Clean and standardize the public Olist datasets according to the
#   locked ORGEE Phase 2 Public Data Cleaning Contract.
#
# IMPORTANT:
#   - Raw files are NEVER modified.
#   - No synthetic data is generated.
#   - No business data is fabricated.
#   - Processed files are written to data/processed/public/
#
# =============================================================================


# =============================================================================
# 1. PROJECT PATHS
# =============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_DIR / "data"

PROCESSED_DATA_DIR = PROJECT_DIR / "data" / "processed" / "public"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# 2. DATASET CONFIGURATION
# =============================================================================

DATASETS = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


# =============================================================================
# 3. HELPER FUNCTIONS
# =============================================================================

def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def standardize_string_columns(df):
    """
    Remove unnecessary leading/trailing whitespace from string columns.

    Business values themselves are not renamed.
    """

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return df


def convert_datetime_columns(df, columns):
    """
    Convert specified columns to pandas datetime.
    Invalid values become NaT rather than fabricated dates.
    """

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    return df


def convert_numeric_columns(df, columns):
    """
    Convert specified columns to numeric.
    Invalid values become NaN rather than fabricated numbers.
    """

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def save_dataset(df, filename):
    """
    Save processed dataset separately from raw data.
    """

    output_path = PROCESSED_DATA_DIR / filename

    df.to_csv(
        output_path,
        index=False
    )

    print(f"Saved: {output_path}")
    print(f"Rows : {len(df):,}")
    print(f"Cols : {len(df.columns):,}")

    return output_path


def report_dataset(df, name):
    """
    Print a concise post-cleaning data-quality report.
    """

    print_section(f"POST-CLEANING VALIDATION — {name.upper()}")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    print("\nMissing values:")

    missing = df.isna().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:
        print("  None")
    else:
        for column, count in missing.items():
            percentage = (count / len(df)) * 100
            print(
                f"  • {column}: {count:,} "
                f"({percentage:.2f}%)"
            )


# =============================================================================
# 4. LOAD RAW DATA
# =============================================================================

print_section("ORGEE — PHASE 2 PUBLIC DATA CLEANING")

print(f"Project Directory:")
print(PROJECT_DIR)

print(f"\nRaw Data Directory:")
print(RAW_DATA_DIR)

print(f"\nProcessed Data Directory:")
print(PROCESSED_DATA_DIR)

print("\nIMPORTANT:")
print("Raw public datasets will NOT be modified.")


def load_dataset(dataset_key):
    filename = DATASETS[dataset_key]

    path = RAW_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"\nDataset not found:\n{path}\n"
        )

    print(f"\nLoading: {filename}")

    return pd.read_csv(path)


# =============================================================================
# 5. ORDERS
# =============================================================================

print_section("CLEANING — ORDERS")

orders = load_dataset("orders")

orders = standardize_string_columns(orders)

orders = convert_datetime_columns(
    orders,
    [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

# Preserve legitimate missing timestamps.
# No missing timestamp is replaced with an artificial value.

orders = orders.drop_duplicates()

save_dataset(
    orders,
    DATASETS["orders"]
)

report_dataset(
    orders,
    "orders"
)


# =============================================================================
# 6. ORDER ITEMS
# =============================================================================

print_section("CLEANING — ORDER ITEMS")

order_items = load_dataset("order_items")

order_items = standardize_string_columns(order_items)

order_items = convert_datetime_columns(
    order_items,
    [
        "shipping_limit_date",
    ],
)

order_items = convert_numeric_columns(
    order_items,
    [
        "order_item_id",
        "price",
        "freight_value",
    ],
)

order_items = order_items.drop_duplicates()

save_dataset(
    order_items,
    DATASETS["order_items"]
)

report_dataset(
    order_items,
    "order_items"
)


# =============================================================================
# 7. PRODUCTS
# =============================================================================

print_section("CLEANING — PRODUCTS")

products = load_dataset("products")

products = standardize_string_columns(products)

products = convert_numeric_columns(
    products,
    [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
)

products = products.drop_duplicates()

# IMPORTANT:
# product_id must remain unique.
# We do NOT fabricate missing product information.

if products["product_id"].duplicated().any():
    raise ValueError(
        "CRITICAL ERROR: product_id is no longer unique."
    )

save_dataset(
    products,
    DATASETS["products"]
)

report_dataset(
    products,
    "products"
)


# =============================================================================
# 8. CUSTOMERS
# =============================================================================

print_section("CLEANING — CUSTOMERS")

customers = load_dataset("customers")

customers = standardize_string_columns(customers)

customers = convert_numeric_columns(
    customers,
    [
        "customer_zip_code_prefix",
    ],
)

customers = customers.drop_duplicates()

# customer_id must remain unique.

if customers["customer_id"].duplicated().any():
    raise ValueError(
        "CRITICAL ERROR: customer_id is no longer unique."
    )

# IMPORTANT:
# customer_unique_id duplicates are legitimate and must NOT be removed.

save_dataset(
    customers,
    DATASETS["customers"]
)

report_dataset(
    customers,
    "customers"
)


# =============================================================================
# 9. SELLERS
# =============================================================================

print_section("CLEANING — SELLERS")

sellers = load_dataset("sellers")

sellers = standardize_string_columns(sellers)

sellers = convert_numeric_columns(
    sellers,
    [
        "seller_zip_code_prefix",
    ],
)

sellers = sellers.drop_duplicates()

if sellers["seller_id"].duplicated().any():
    raise ValueError(
        "CRITICAL ERROR: seller_id is no longer unique."
    )

save_dataset(
    sellers,
    DATASETS["sellers"]
)

report_dataset(
    sellers,
    "sellers"
)


# =============================================================================
# 10. PAYMENTS
# =============================================================================

print_section("CLEANING — PAYMENTS")

payments = load_dataset("payments")

payments = standardize_string_columns(payments)

payments = convert_numeric_columns(
    payments,
    [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ],
)

payments = payments.drop_duplicates()

# IMPORTANT:
# Multiple payment records per order are legitimate.
# Therefore we NEVER deduplicate using order_id alone.

save_dataset(
    payments,
    DATASETS["payments"]
)

report_dataset(
    payments,
    "payments"
)


# =============================================================================
# 11. REVIEWS
# =============================================================================

print_section("CLEANING — REVIEWS")

reviews = load_dataset("reviews")

reviews = standardize_string_columns(reviews)

reviews = convert_datetime_columns(
    reviews,
    [
        "review_creation_date",
        "review_answer_timestamp",
    ],
)

reviews = convert_numeric_columns(
    reviews,
    [
        "review_score",
    ],
)

reviews = reviews.drop_duplicates()

# Missing review comments are preserved.
# A missing comment does NOT mean a negative review.

save_dataset(
    reviews,
    DATASETS["reviews"]
)

report_dataset(
    reviews,
    "reviews"
)


# =============================================================================
# 12. GEOLOCATION
# =============================================================================

print_section("CLEANING — GEOLOCATION")

geolocation = load_dataset("geolocation")

geolocation = standardize_string_columns(geolocation)

geolocation = convert_numeric_columns(
    geolocation,
    [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
    ],
)

# Contract-approved transformation:
# Remove exact duplicate rows only.

before_duplicates = len(geolocation)

geolocation = geolocation.drop_duplicates()

after_duplicates = len(geolocation)

duplicates_removed = (
    before_duplicates - after_duplicates
)

print(
    f"\nExact duplicate rows removed: "
    f"{duplicates_removed:,}"
)

save_dataset(
    geolocation,
    DATASETS["geolocation"]
)

report_dataset(
    geolocation,
    "geolocation"
)


# =============================================================================
# 13. CATEGORY TRANSLATION
# =============================================================================

print_section("CLEANING — CATEGORY TRANSLATION")

category_translation = load_dataset(
    "category_translation"
)

category_translation = standardize_string_columns(
    category_translation
)

category_translation = category_translation.drop_duplicates()

save_dataset(
    category_translation,
    DATASETS["category_translation"]
)

report_dataset(
    category_translation,
    "category_translation"
)


# =============================================================================
# 14. CROSS-DATASET VALIDATION
# =============================================================================

print_section("POST-CLEANING REFERENTIAL INTEGRITY VALIDATION")


def check_relationship(
    child_df,
    child_key,
    parent_df,
    parent_key,
    relationship
):
    child_values = set(
        child_df[child_key]
        .dropna()
        .unique()
    )

    parent_values = set(
        parent_df[parent_key]
        .dropna()
        .unique()
    )

    unmatched = child_values - parent_values

    print(f"\n{relationship}")

    print(
        f"Unmatched keys: "
        f"{len(unmatched):,}"
    )

    if len(unmatched) == 0:
        print("STATUS: PASS")
    else:
        print("STATUS: REVIEW")

        for value in list(unmatched)[:10]:
            print(f"  • {value}")

    return unmatched


# Orders → Customers
check_relationship(
    orders,
    "customer_id",
    customers,
    "customer_id",
    "ORDERS → CUSTOMERS"
)

# Order Items → Orders
check_relationship(
    order_items,
    "order_id",
    orders,
    "order_id",
    "ORDER_ITEMS → ORDERS"
)

# Order Items → Products
check_relationship(
    order_items,
    "product_id",
    products,
    "product_id",
    "ORDER_ITEMS → PRODUCTS"
)

# Order Items → Sellers
check_relationship(
    order_items,
    "seller_id",
    sellers,
    "seller_id",
    "ORDER_ITEMS → SELLERS"
)

# Payments → Orders
check_relationship(
    payments,
    "order_id",
    orders,
    "order_id",
    "PAYMENTS → ORDERS"
)

# Reviews → Orders
check_relationship(
    reviews,
    "order_id",
    orders,
    "order_id",
    "REVIEWS → ORDERS"
)

# Products → Category Translation
category_unmatched = check_relationship(
    products,
    "product_category_name",
    category_translation,
    "product_category_name",
    "PRODUCTS → CATEGORY TRANSLATION"
)


# =============================================================================
# 15. TIMESTAMP LOGICAL VALIDATION
# =============================================================================

print_section("TIMESTAMP LOGICAL VALIDATION")


def count_invalid_timestamp_sequence(
    df,
    earlier_column,
    later_column
):
    valid_rows = (
        df[earlier_column].notna()
        &
        df[later_column].notna()
    )

    invalid = (
        valid_rows
        &
        (df[later_column] < df[earlier_column])
    )

    return int(invalid.sum())


checks = [
    (
        "order_purchase_timestamp",
        "order_approved_at"
    ),
    (
        "order_approved_at",
        "order_delivered_carrier_date"
    ),
    (
        "order_delivered_carrier_date",
        "order_delivered_customer_date"
    ),
]

for earlier, later in checks:

    invalid_count = count_invalid_timestamp_sequence(
        orders,
        earlier,
        later
    )

    print(
        f"{earlier} → {later}: "
        f"{invalid_count:,} invalid sequences"
    )


# =============================================================================
# 16. KEY UNIQUENESS VALIDATION
# =============================================================================

print_section("KEY UNIQUENESS VALIDATION")

key_checks = [
    (
        "orders.order_id",
        orders,
        "order_id"
    ),
    (
        "products.product_id",
        products,
        "product_id"
    ),
    (
        "customers.customer_id",
        customers,
        "customer_id"
    ),
    (
        "sellers.seller_id",
        sellers,
        "seller_id"
    ),
]

for label, df, column in key_checks:

    duplicate_count = int(
        df[column].duplicated().sum()
    )

    print(
        f"{label}: "
        f"{duplicate_count:,} duplicate keys"
    )


# =============================================================================
# 17. FINAL OUTPUT SUMMARY
# =============================================================================

print_section("ORGEE — PHASE 2 PUBLIC DATA CLEANING COMPLETE")

print("\nProcessed datasets created:")

for dataset_key, filename in DATASETS.items():

    output_path = PROCESSED_DATA_DIR / filename

    if output_path.exists():

        print(
            f"  ✓ {filename}"
        )

print("\nRaw datasets:")
print("  ✓ Preserved")
print("  ✓ Not overwritten")
print("  ✓ Not manually modified")

print("\nSynthetic data:")
print("  ✓ NOT generated")

print("\nCustomer 360:")
print("  ✓ NOT built yet")

print("\nCross-device identity:")
print("  ✓ NOT implemented yet")

print("\nEnterprise warehouse:")
print("  ✓ NOT built yet")

print("\nCategory translation exceptions:")

if len(category_unmatched) == 0:

    print("  ✓ None")

else:

    for category in sorted(category_unmatched):

        print(
            f"  ⚠ {category}"
        )

print("\n" + "=" * 80)
print("NEXT STEP")
print("=" * 80)

print(
    """
Review the processed-data validation results.

Do NOT generate synthetic enterprise data yet.

Do NOT build the SQL warehouse yet.

The next stage is to confirm that the processed public datasets
passed the required validation gates before designing the enterprise
data-generation layer.
"""
)

print("=" * 80)