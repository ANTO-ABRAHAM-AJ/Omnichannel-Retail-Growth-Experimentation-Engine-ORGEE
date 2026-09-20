import pandas as pd
from pathlib import Path


# ============================================================
# ORGEE — PHASE 2
# Public Dataset Profiling
# Omnichannel Retail & Growth Experimentation Engine
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT PATH
# ------------------------------------------------------------

# This script is located inside:
# ORGEE/python/

# Therefore:
# parent      = python/
# parent.parent = ORGEE/
# data        = ORGEE/data/

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"


# ------------------------------------------------------------
# 2. PUBLIC DATASETS
# ------------------------------------------------------------

FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}


# ------------------------------------------------------------
# 3. HEADER
# ------------------------------------------------------------

print("=" * 80)
print("ORGEE — PHASE 2 PUBLIC DATA PROFILING")
print("Omnichannel Retail & Growth Experimentation Engine")
print("=" * 80)

print(f"\nProject Directory:")
print(PROJECT_DIR)

print(f"\nData Directory:")
print(DATA_DIR)


# ------------------------------------------------------------
# 4. CHECK DATA DIRECTORY
# ------------------------------------------------------------

if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"\nData directory not found:\n{DATA_DIR}\n"
        f"\nExpected structure:\n"
        f"{PROJECT_DIR}\\data\\"
    )


# ------------------------------------------------------------
# 5. PROFILE EACH DATASET
# ------------------------------------------------------------

for name, filename in FILES.items():

    file_path = DATA_DIR / filename

    print("\n" + "=" * 80)
    print(f"DATASET: {name.upper()}")
    print(f"FILE: {filename}")
    print("=" * 80)

    # --------------------------------------------------------
    # Check whether file exists
    # --------------------------------------------------------

    if not file_path.exists():
        print("\nWARNING: File not found.")
        print(f"Expected location: {file_path}")
        continue

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_csv(file_path)

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    print("\n--- BASIC INFORMATION ---")

    print(f"Rows:    {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]:,}")

    # --------------------------------------------------------
    # Column names
    # --------------------------------------------------------

    print("\n--- COLUMNS ---")

    for column in df.columns:
        print(f"  • {column}")

    # --------------------------------------------------------
    # Data types
    # --------------------------------------------------------

    print("\n--- DATA TYPES ---")

    for column, dtype in df.dtypes.items():
        print(f"  • {column}: {dtype}")

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n--- MISSING VALUES ---")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("  No missing values.")
    else:
        for column, count in missing.items():
            percentage = (count / len(df)) * 100
            print(
                f"  • {column}: "
                f"{count:,} missing "
                f"({percentage:.2f}%)"
            )

    # --------------------------------------------------------
    # Duplicate rows
    # --------------------------------------------------------

    print("\n--- DUPLICATE ROWS ---")

    duplicate_count = df.duplicated().sum()

    print(f"  {duplicate_count:,} duplicate rows")

    # --------------------------------------------------------
    # Unique values
    # --------------------------------------------------------

    print("\n--- UNIQUE VALUES ---")

    for column in df.columns:

        unique_count = df[column].nunique(dropna=True)

        print(
            f"  • {column}: "
            f"{unique_count:,} unique values"
        )

    # --------------------------------------------------------
    # Sample records
    # --------------------------------------------------------

    print("\n--- SAMPLE RECORDS ---")

    print(df.head(3).to_string(index=False))

    # --------------------------------------------------------
    # End of dataset
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print(f"Completed profiling: {name}")
    print("-" * 80)


# ------------------------------------------------------------
# 6. COMPLETION
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("PUBLIC DATA PROFILING COMPLETE")
print("=" * 80)

print("\nDatasets profiled:")
for name in FILES:
    print(f"  ✓ {name}")

print("\nNext step:")
print("Analyze the profiling results and build the ORGEE Phase 2 Data Contract.")

print("\nDO NOT modify or generate datasets yet.")
print("DO NOT clean the raw public files yet.")

print("\n" + "=" * 80)