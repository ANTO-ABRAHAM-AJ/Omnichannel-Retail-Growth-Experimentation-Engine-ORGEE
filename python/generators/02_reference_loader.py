"""
ORGEE — Public Reference Data Loader

Loads the processed public Olist datasets used as the
enterprise integration foundation.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "public"


# ============================================================
# PUBLIC DATASET FILES
# ============================================================

DATASET_FILES = {
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


# ============================================================
# LOADER
# ============================================================

def load_public_data() -> dict[str, pd.DataFrame]:
    """
    Load all processed public Olist datasets.

    Returns:
        Dictionary containing one DataFrame per public entity.
    """

    datasets = {}

    for entity_name, filename in DATASET_FILES.items():

        file_path = PUBLIC_DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required public dataset not found: {file_path}"
            )

        datasets[entity_name] = pd.read_csv(file_path)

    return datasets


# ============================================================
# BASIC REFERENCE VALIDATION
# ============================================================

def validate_reference_data(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """
    Perform basic existence and population checks.
    """

    for entity_name, dataframe in datasets.items():

        if dataframe.empty:
            raise ValueError(
                f"Reference dataset is empty: {entity_name}"
            )

        print(
            f"[REFERENCE] "
            f"{entity_name}: {len(dataframe):,} rows"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    public_data = load_public_data()

    validate_reference_data(public_data)

    print("\nPublic reference data loaded successfully.")