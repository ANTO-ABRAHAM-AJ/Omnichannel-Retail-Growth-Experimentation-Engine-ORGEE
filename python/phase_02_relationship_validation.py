from pathlib import Path
import pandas as pd


# =============================================================================
# ORGEE — PHASE 2
# PUBLIC DATA RELATIONSHIP VALIDATION
# FINAL QUALITY-GATE VERSION
# Omnichannel Retail & Growth Experimentation Engine
# =============================================================================
#
# Purpose:
#   Validate relationships and grains across the PROCESSED public Olist
#   datasets used as the ORGEE Phase 2 public-data foundation.
#
# Important:
#   - Raw public files are NOT modified.
#   - Processed public files are READ ONLY.
#   - No synthetic data is generated.
#   - No records are deleted.
#   - No warehouse tables are created.
#
# =============================================================================


# =============================================================================
# 1. PROJECT PATHS
# =============================================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

PROCESSED_PUBLIC_DIR = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "public"
)


# =============================================================================
# 2. DATASET PATHS
# =============================================================================

ORDERS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_orders_dataset.csv"
)

ORDER_ITEMS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_order_items_dataset.csv"
)

PRODUCTS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_products_dataset.csv"
)

CUSTOMERS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_customers_dataset.csv"
)

SELLERS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_sellers_dataset.csv"
)

PAYMENTS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_order_payments_dataset.csv"
)

REVIEWS_FILE = (
    PROCESSED_PUBLIC_DIR
    / "olist_order_reviews_dataset.csv"
)

CATEGORY_TRANSLATION_FILE = (
    PROCESSED_PUBLIC_DIR
    / "product_category_name_translation.csv"
)


# =============================================================================
# 3. HEADER
# =============================================================================

print("=" * 80)
print("ORGEE — PHASE 2 PUBLIC DATA RELATIONSHIP VALIDATION")
print("FINAL QUALITY-GATE VERSION")
print("=" * 80)

print()
print("Project Directory:")
print(PROJECT_DIR)

print()
print("Processed Public Data Directory:")
print(PROCESSED_PUBLIC_DIR)


# =============================================================================
# 4. FILE EXISTENCE VALIDATION
# =============================================================================

print()
print("-" * 80)
print("CHECKING PROCESSED PUBLIC DATASETS")
print("-" * 80)

required_files = {
    "orders": ORDERS_FILE,
    "order_items": ORDER_ITEMS_FILE,
    "products": PRODUCTS_FILE,
    "customers": CUSTOMERS_FILE,
    "sellers": SELLERS_FILE,
    "payments": PAYMENTS_FILE,
    "reviews": REVIEWS_FILE,
    "category_translation": CATEGORY_TRANSLATION_FILE,
}

for name, file_path in required_files.items():

    if not file_path.exists():

        raise FileNotFoundError(
            f"\nRequired processed dataset not found:\n"
            f"{file_path}"
        )

    print(
        f"[PASS] {name:<22} "
        f"{file_path.name}"
    )


print()
print(
    "[RELATIONSHIP VALIDATION PASSED] "
    "All processed public datasets exist."
)


# =============================================================================
# 5. LOAD DATASETS
# =============================================================================

print()
print("-" * 80)
print("LOADING PROCESSED PUBLIC DATASETS")
print("-" * 80)


orders = pd.read_csv(
    ORDERS_FILE
)

order_items = pd.read_csv(
    ORDER_ITEMS_FILE
)

products = pd.read_csv(
    PRODUCTS_FILE
)

customers = pd.read_csv(
    CUSTOMERS_FILE
)

sellers = pd.read_csv(
    SELLERS_FILE
)

payments = pd.read_csv(
    PAYMENTS_FILE
)

reviews = pd.read_csv(
    REVIEWS_FILE
)

category_translation = pd.read_csv(
    CATEGORY_TRANSLATION_FILE
)


print(
    f"Orders                 = {len(orders):,}"
)

print(
    f"Order items            = {len(order_items):,}"
)

print(
    f"Products               = {len(products):,}"
)

print(
    f"Customers              = {len(customers):,}"
)

print(
    f"Sellers                = {len(sellers):,}"
)

print(
    f"Payments               = {len(payments):,}"
)

print(
    f"Reviews                = {len(reviews):,}"
)

print(
    f"Category translations  = "
    f"{len(category_translation):,}"
)


# =============================================================================
# 6. BASIC REQUIRED COLUMN VALIDATION
# =============================================================================

print()
print("-" * 80)
print("CHECKING REQUIRED RELATIONSHIP COLUMNS")
print("-" * 80)


required_columns = {

    "orders": [
        "order_id",
        "customer_id",
    ],

    "order_items": [
        "order_id",
        "product_id",
        "seller_id",
    ],

    "products": [
        "product_id",
        "product_category_name",
    ],

    "customers": [
        "customer_id",
        "customer_unique_id",
    ],

    "sellers": [
        "seller_id",
    ],

    "payments": [
        "order_id",
    ],

    "reviews": [
        "order_id",
    ],

    "category_translation": [
        "product_category_name",
    ],
}


dataframes = {
    "orders": orders,
    "order_items": order_items,
    "products": products,
    "customers": customers,
    "sellers": sellers,
    "payments": payments,
    "reviews": reviews,
    "category_translation": category_translation,
}


for dataset_name, columns in required_columns.items():

    dataframe = dataframes[dataset_name]

    missing = [
        column
        for column in columns
        if column not in dataframe.columns
    ]

    if missing:

        raise ValueError(
            f"{dataset_name} is missing required "
            f"columns: {missing}"
        )


print(
    "[RELATIONSHIP VALIDATION PASSED] "
    "Required relationship columns exist."
)


# =============================================================================
# 7. HELPER FUNCTION
# =============================================================================

def validate_relationship(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name,
):
    """
    Validate whether every non-null child key exists
    in the parent dataset.
    """

    child_keys = set(
        child_df[
            child_column
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    parent_keys = set(
        parent_df[
            parent_column
        ]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    unmatched = (
        child_keys
        -
        parent_keys
    )

    print()
    print("-" * 80)
    print(relationship_name)
    print("-" * 80)

    print(
        f"Child table:       {child_column}"
    )

    print(
        f"Parent table:      {parent_column}"
    )

    print(
        f"Child unique keys:  "
        f"{len(child_keys):,}"
    )

    print(
        f"Parent unique keys: "
        f"{len(parent_keys):,}"
    )

    print(
        f"Unmatched keys:     "
        f"{len(unmatched):,}"
    )

    if not unmatched:

        print(
            "[PASS] Relationship validated."
        )

    else:

        print(
            "[REVIEW] Unmatched keys detected."
        )

        print(
            "\nSample unmatched keys:"
        )

        for key in sorted(
            unmatched
        )[:10]:

            print(
                f"  • {key}"
            )

    return unmatched


# =============================================================================
# 8. RELATIONSHIP VALIDATION
# =============================================================================

print()
print("=" * 80)
print("RELATIONSHIP VALIDATION")
print("=" * 80)


relationship_results = {}


relationship_results[
    "orders_to_customers"
] = validate_relationship(
    orders,
    "customer_id",
    customers,
    "customer_id",
    "ORDERS → CUSTOMERS",
)


relationship_results[
    "order_items_to_orders"
] = validate_relationship(
    order_items,
    "order_id",
    orders,
    "order_id",
    "ORDER_ITEMS → ORDERS",
)


relationship_results[
    "order_items_to_products"
] = validate_relationship(
    order_items,
    "product_id",
    products,
    "product_id",
    "ORDER_ITEMS → PRODUCTS",
)


relationship_results[
    "order_items_to_sellers"
] = validate_relationship(
    order_items,
    "seller_id",
    sellers,
    "seller_id",
    "ORDER_ITEMS → SELLERS",
)


relationship_results[
    "payments_to_orders"
] = validate_relationship(
    payments,
    "order_id",
    orders,
    "order_id",
    "PAYMENTS → ORDERS",
)


relationship_results[
    "reviews_to_orders"
] = validate_relationship(
    reviews,
    "order_id",
    orders,
    "order_id",
    "REVIEWS → ORDERS",
)


# =============================================================================
# 9. PRODUCT → CATEGORY TRANSLATION
# =============================================================================

print()
print("-" * 80)
print("PRODUCT CATEGORY TRANSLATION ANALYSIS")
print("-" * 80)

product_categories = set(
    products[
        "product_category_name"
    ]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

translated_categories = set(
    category_translation[
        "product_category_name"
    ]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

untranslated_categories = (
    product_categories
    -
    translated_categories
)

print(
    f"Product categories present       = "
    f"{len(product_categories):,}"
)

print(
    f"Translated categories             = "
    f"{len(product_categories & translated_categories):,}"
)

print(
    f"Categories without translation    = "
    f"{len(untranslated_categories):,}"
)

if untranslated_categories:

    print(
        "\nSample categories without translation:"
    )

    for category in sorted(
        untranslated_categories
    )[:20]:

        print(
            f"  • {category}"
        )

else:

    print(
        "[PASS] All product categories have "
        "translation records."
    )


# =============================================================================
# 10. CUSTOMER IDENTITY GRAIN
# =============================================================================

print()
print("=" * 80)
print("CUSTOMER IDENTITY ANALYSIS")
print("=" * 80)


customer_id_count = (
    customers["customer_id"]
    .nunique()
)

customer_unique_id_count = (
    customers["customer_unique_id"]
    .nunique()
)

customer_id_duplicates = int(
    customers["customer_id"]
    .duplicated()
    .sum()
)

customer_unique_id_duplicates = int(
    customers["customer_unique_id"]
    .duplicated()
    .sum()
)


print(
    f"\nUnique customer_id: "
    f"{customer_id_count:,}"
)

print(
    f"Unique customer_unique_id: "
    f"{customer_unique_id_count:,}"
)

print(
    f"customer_id duplicate rows: "
    f"{customer_id_duplicates:,}"
)

print(
    f"customer_unique_id duplicate rows: "
    f"{customer_unique_id_duplicates:,}"
)


if customer_id_duplicates == 0:

    print(
        "[PASS] customer_id is unique."
    )

else:

    print(
        "[REVIEW] customer_id duplicates detected."
    )


# =============================================================================
# 11. ORDER GRAIN ANALYSIS
# =============================================================================

print()
print("=" * 80)
print("ORDER GRAIN ANALYSIS")
print("=" * 80)


order_item_counts = (
    order_items
    .groupby("order_id")
    .size()
)


print(
    f"\nOrders represented in order_items: "
    f"{order_item_counts.index.nunique():,}"
)

print(
    f"Orders containing multiple items: "
    f"{(order_item_counts > 1).sum():,}"
)

print(
    f"Maximum items in a single order: "
    f"{order_item_counts.max():,}"
)


# =============================================================================
# 12. PAYMENT GRAIN ANALYSIS
# =============================================================================

print()
print("=" * 80)
print("PAYMENT GRAIN ANALYSIS")
print("=" * 80)


payment_counts = (
    payments
    .groupby("order_id")
    .size()
)


print(
    f"\nOrders represented in payments: "
    f"{payment_counts.index.nunique():,}"
)

print(
    f"Orders with multiple payment records: "
    f"{(payment_counts > 1).sum():,}"
)

print(
    f"Maximum payment records for one order: "
    f"{payment_counts.max():,}"
)


# =============================================================================
# 13. REVIEW GRAIN ANALYSIS
# =============================================================================

print()
print("=" * 80)
print("REVIEW GRAIN ANALYSIS")
print("=" * 80)


review_counts = (
    reviews
    .groupby("order_id")
    .size()
)


print(
    f"\nOrders represented in reviews: "
    f"{review_counts.index.nunique():,}"
)

print(
    f"Orders with multiple review records: "
    f"{(review_counts > 1).sum():,}"
)

print(
    f"Maximum review records for one order: "
    f"{review_counts.max():,}"
)


# =============================================================================
# 14. PRODUCT GRAIN
# =============================================================================

print()
print("=" * 80)
print("PRODUCT GRAIN")
print("=" * 80)


product_rows = len(products)

unique_products = (
    products["product_id"]
    .nunique()
)

product_duplicates = (
    product_rows
    -
    unique_products
)


print(
    f"\nProduct rows: "
    f"{product_rows:,}"
)

print(
    f"Unique product_id: "
    f"{unique_products:,}"
)

print(
    f"Duplicate product_id rows: "
    f"{product_duplicates:,}"
)


if product_duplicates == 0:

    print(
        "[PASS] product_id is unique."
    )

else:

    print(
        "[REVIEW] Duplicate product_id detected."
    )


# =============================================================================
# 15. SELLER GRAIN
# =============================================================================

print()
print("=" * 80)
print("SELLER GRAIN")
print("=" * 80)


seller_rows = len(sellers)

unique_sellers = (
    sellers["seller_id"]
    .nunique()
)

seller_duplicates = (
    seller_rows
    -
    unique_sellers
)


print(
    f"\nSeller rows: "
    f"{seller_rows:,}"
)

print(
    f"Unique seller_id: "
    f"{unique_sellers:,}"
)

print(
    f"Duplicate seller_id rows: "
    f"{seller_duplicates:,}"
)


if seller_duplicates == 0:

    print(
        "[PASS] seller_id is unique."
    )

else:

    print(
        "[REVIEW] Duplicate seller_id detected."
    )


# =============================================================================
# 16. FINAL RELATIONSHIP SUMMARY
# =============================================================================

print()
print("=" * 80)
print("RELATIONSHIP VALIDATION SUMMARY")
print("=" * 80)


for relationship, unmatched in (
    relationship_results.items()
):

    status = (
        "PASS"
        if len(unmatched) == 0
        else "REVIEW"
    )

    print(
        f"{relationship:<32} "
        f"{status:<8} "
        f"unmatched={len(unmatched):,}"
    )


# =============================================================================
# 17. FINAL STATUS
# =============================================================================

relationship_failures = {
    name: unmatched
    for name, unmatched
    in relationship_results.items()
    if len(unmatched) > 0
}


print()
print("=" * 80)
print("ORGEE — PHASE 2 PUBLIC DATA RELATIONSHIP VALIDATION COMPLETE")
print("=" * 80)

print()
print("Processed public data was READ ONLY.")
print("Raw public data was NOT modified.")
print("No synthetic data was generated.")
print("No enterprise data was modified.")

if relationship_failures:

    print()
    print(
        "[RELATIONSHIP VALIDATION] "
        "REVIEW REQUIRED"
    )

    print(
        "\nRelationships requiring review:"
    )

    for name, unmatched in (
        relationship_failures.items()
    ):

        print(
            f"  • {name}: "
            f"{len(unmatched):,} unmatched keys"
        )

else:

    print()
    print(
        "[RELATIONSHIP VALIDATION PASSED] "
        "ALL CORE RELATIONSHIPS PASSED"
    )

print()
print("=" * 80)