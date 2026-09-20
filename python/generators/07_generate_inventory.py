"""
ORGEE — Inventory Generator

Generates synthetic inventory observations across products
and inventory locations.

Source:
    Document 7 — Enterprise Generation Configuration
"""

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION LOADER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    PROJECT_ROOT
    / "python"
    / "generators"
    / "01_generator_config.py"
)

if not CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"Generator configuration not found:\n{CONFIG_FILE}"
    )

spec = importlib.util.spec_from_file_location(
    "generator_config",
    CONFIG_FILE,
)

if spec is None or spec.loader is None:
    raise ImportError(
        f"Unable to load generator configuration:\n{CONFIG_FILE}"
    )

generator_config = importlib.util.module_from_spec(spec)

spec.loader.exec_module(generator_config)

PRIMARY_SEED = generator_config.PRIMARY_SEED
TARGET_VOLUMES = generator_config.TARGET_VOLUMES


# ============================================================
# PATH CONFIGURATION
# ============================================================

PUBLIC_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
)

INVENTORY_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "inventory"
)

PRODUCTS_FILE = (
    PUBLIC_DATA_DIR
    / "olist_products_dataset.csv"
)

ORDERS_FILE = (
    PUBLIC_DATA_DIR
    / "olist_orders_dataset.csv"
)

OUTPUT_FILE = (
    INVENTORY_OUTPUT_DIR
    / "inventory_observations.csv"
)


# ============================================================
# TARGET CONFIGURATION
# ============================================================

if "inventory_observations" not in TARGET_VOLUMES:
    raise KeyError(
        "TARGET_VOLUMES does not contain "
        "'inventory_observations'."
    )

TARGET_OBSERVATIONS = int(
    TARGET_VOLUMES["inventory_observations"]
)


# ============================================================
# INVENTORY CONFIGURATION
# ============================================================

INVENTORY_LOCATION_COUNT = 20

INVENTORY_STATUSES = (
    "in_stock",
    "low_stock",
    "out_of_stock",
)

# We intentionally create 50,000 product-location
# combinations and 20 observations per combination.
#
# 50,000 × 20 = 1,000,000 observations

PRODUCT_LOCATION_PAIRS = 50_000

if TARGET_OBSERVATIONS % PRODUCT_LOCATION_PAIRS != 0:
    raise ValueError(
        "TARGET_OBSERVATIONS must be divisible by "
        "PRODUCT_LOCATION_PAIRS."
    )

OBSERVATIONS_PER_PAIR = (
    TARGET_OBSERVATIONS
    // PRODUCT_LOCATION_PAIRS
)


# ============================================================
# INVENTORY LOCATION GENERATION
# ============================================================

def generate_inventory_locations() -> list[str]:
    """
    Generate deterministic inventory-location identifiers.
    """

    return [
        f"inv_loc_{i:02d}"
        for i in range(
            1,
            INVENTORY_LOCATION_COUNT + 1,
        )
    ]


# ============================================================
# LOAD PUBLIC PRODUCTS
# ============================================================

def load_products() -> pd.DataFrame:
    """
    Load authoritative public product identifiers.
    """

    print(
        "[INVENTORY] Loading public products..."
    )

    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            f"Products dataset not found:\n"
            f"{PRODUCTS_FILE}"
        )

    products = pd.read_csv(
        PRODUCTS_FILE,
        usecols=[
            "product_id"
        ],
    )

    products["product_id"] = (
        products["product_id"]
        .astype(str)
        .str.strip()
    )

    products = products[
        products["product_id"].notna()
    ]

    products = products[
        products["product_id"] != ""
    ]

    products = products.drop_duplicates(
        subset=[
            "product_id"
        ]
    ).reset_index(
        drop=True
    )

    if products.empty:
        raise ValueError(
            "Public product reference dataset is empty."
        )

    print(
        f"[INVENTORY] Loaded "
        f"{len(products):,} public products."
    )

    return products


# ============================================================
# LOAD PUBLIC OBSERVATION PERIOD
# ============================================================

def load_observation_period() -> tuple[
    pd.Timestamp,
    pd.Timestamp,
]:
    """
    Derive the enterprise behavioral period from
    the public Olist order observation period.
    """

    print(
        "[INVENTORY] Loading public order "
        "observation period..."
    )

    if not ORDERS_FILE.exists():
        raise FileNotFoundError(
            f"Orders dataset not found:\n"
            f"{ORDERS_FILE}"
        )

    orders = pd.read_csv(
        ORDERS_FILE,
        usecols=[
            "order_purchase_timestamp"
        ],
    )

    orders[
        "order_purchase_timestamp"
    ] = pd.to_datetime(
        orders[
            "order_purchase_timestamp"
        ],
        errors="coerce",
    )

    orders = orders.dropna(
        subset=[
            "order_purchase_timestamp"
        ]
    )

    if orders.empty:
        raise ValueError(
            "No valid order timestamps found."
        )

    period_start = (
        orders[
            "order_purchase_timestamp"
        ].min()
    )

    period_end = (
        orders[
            "order_purchase_timestamp"
        ].max()
    )

    if period_start >= period_end:
        raise ValueError(
            "Invalid public observation period."
        )

    print(
        f"[INVENTORY] Period start: "
        f"{period_start}"
    )

    print(
        f"[INVENTORY] Period end:   "
        f"{period_end}"
    )

    return (
        period_start,
        period_end,
    )


# ============================================================
# GENERATE PRODUCT-LOCATION PAIRS
# ============================================================

def generate_product_location_pairs(
    products: pd.DataFrame,
    locations: list[str],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Generate unique product-location combinations.

    Products may appear at multiple locations.
    Not every product must be available at every location.
    """

    product_ids = (
        products[
            "product_id"
        ]
        .to_numpy()
    )

    total_possible_pairs = (
        len(product_ids)
        * len(locations)
    )

    if (
        PRODUCT_LOCATION_PAIRS
        > total_possible_pairs
    ):
        raise ValueError(
            "Requested product-location combinations "
            "exceed the possible unique combinations."
        )

    pairs = set()

    while len(pairs) < PRODUCT_LOCATION_PAIRS:

        remaining = (
            PRODUCT_LOCATION_PAIRS
            - len(pairs)
        )

        batch_size = max(
            1000,
            remaining * 2,
        )

        selected_products = rng.choice(
            product_ids,
            size=batch_size,
            replace=True,
        )

        selected_locations = rng.choice(
            locations,
            size=batch_size,
            replace=True,
        )

        for product_id, location_id in zip(
            selected_products,
            selected_locations,
        ):
            pairs.add(
                (
                    str(product_id),
                    str(location_id),
                )
            )

            if len(pairs) >= PRODUCT_LOCATION_PAIRS:
                break

    pairs_df = pd.DataFrame(
        list(pairs),
        columns=[
            "product_id",
            "inventory_location_id",
        ],
    )

    return pairs_df


# ============================================================
# GENERATE INVENTORY
# ============================================================

def generate_inventory(
    products: pd.DataFrame,
    rng: np.random.Generator,
    period_start: pd.Timestamp,
    period_end: pd.Timestamp,
) -> pd.DataFrame:
    """
    Generate inventory observations.

    Inventory behavior includes:

    - Initial stock
    - Demand-driven depletion
    - Random movement
    - Replenishment
    - Low-stock states
    - Out-of-stock states
    """

    locations = (
        generate_inventory_locations()
    )

    pairs = (
        generate_product_location_pairs(
            products,
            locations,
            rng,
        )
    )

    print(
        f"[INVENTORY] Generated "
        f"{len(pairs):,} product-location "
        f"combinations."
    )

    total_seconds = int(
        (
            period_end
            - period_start
        ).total_seconds()
    )

    rows = []

    observation_number = 1

    # --------------------------------------------------------
    # Process each product-location combination
    # --------------------------------------------------------

    for pair in pairs.itertuples(
        index=False
    ):

        product_id = pair.product_id

        location_id = (
            pair.inventory_location_id
        )

        # ----------------------------------------------------
        # Initial inventory
        # ----------------------------------------------------

        quantity = int(
            rng.integers(
                5,
                201,
            )
        )

        # ----------------------------------------------------
        # Generate ordered observation timestamps
        # ----------------------------------------------------

        offsets = np.sort(
            rng.integers(
                0,
                total_seconds + 1,
                size=OBSERVATIONS_PER_PAIR,
            )
        )

        # ----------------------------------------------------
        # Generate observations
        # ----------------------------------------------------

        for offset in offsets:

            timestamp = (
                period_start
                + pd.to_timedelta(
                    int(offset),
                    unit="s",
                )
            )

            # ------------------------------------------------
            # Demand pressure
            # ------------------------------------------------

            demand_lambda = max(
                0.5,
                quantity * 0.04,
            )

            demand = int(
                rng.poisson(
                    demand_lambda
                )
            )

            demand = min(
                demand,
                quantity,
            )

            quantity -= demand

            # ------------------------------------------------
            # Replenishment
            # ------------------------------------------------

            if quantity <= 10:

                if rng.random() < 0.65:

                    replenishment = int(
                        rng.integers(
                            30,
                            151,
                        )
                    )

                    quantity += (
                        replenishment
                    )

            # ------------------------------------------------
            # Small random stock movement
            # ------------------------------------------------

            random_adjustment = int(
                rng.integers(
                    -3,
                    4,
                )
            )

            quantity += (
                random_adjustment
            )

            # ------------------------------------------------
            # Inventory cannot be negative
            # ------------------------------------------------

            quantity = max(
                0,
                int(quantity),
            )

            # ------------------------------------------------
            # Inventory status
            # ------------------------------------------------

            if quantity == 0:

                inventory_status = (
                    "out_of_stock"
                )

            elif quantity <= 10:

                inventory_status = (
                    "low_stock"
                )

            else:

                inventory_status = (
                    "in_stock"
                )

            # ------------------------------------------------
            # Reserved inventory
            # ------------------------------------------------

            if quantity > 0:

                reserved_quantity = int(
                    rng.integers(
                        0,
                        min(
                            quantity,
                            10,
                        ) + 1,
                    )
                )

            else:

                reserved_quantity = 0

            # ------------------------------------------------
            # Create row
            # ------------------------------------------------

            rows.append(
                {
                    "inventory_observation_id":
                        f"inv_obs_{observation_number:09d}",

                    "product_id":
                        product_id,

                    "inventory_location_id":
                        location_id,

                    "observation_timestamp":
                        timestamp,

                    "available_quantity":
                        quantity,

                    "reserved_quantity":
                        reserved_quantity,

                    "inventory_status":
                        inventory_status,
                }
            )

            observation_number += 1

    inventory = pd.DataFrame(
        rows,
        columns=[
            "inventory_observation_id",
            "product_id",
            "inventory_location_id",
            "observation_timestamp",
            "available_quantity",
            "reserved_quantity",
            "inventory_status",
        ],
    )

    return inventory


# ============================================================
# VALIDATE INVENTORY
# ============================================================

def validate_inventory(
    inventory: pd.DataFrame,
    products: pd.DataFrame,
    period_start: pd.Timestamp,
    period_end: pd.Timestamp,
) -> None:
    """
    Validate generated inventory observations.
    """

    print(
        "[INVENTORY] Running validation..."
    )

    # --------------------------------------------------------
    # Required schema
    # --------------------------------------------------------

    required_columns = {
        "inventory_observation_id",
        "product_id",
        "inventory_location_id",
        "observation_timestamp",
        "available_quantity",
        "reserved_quantity",
        "inventory_status",
    }

    missing_columns = (
        required_columns
        - set(inventory.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing inventory columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Target volume
    # --------------------------------------------------------

    if len(inventory) != TARGET_OBSERVATIONS:

        raise ValueError(
            f"Expected "
            f"{TARGET_OBSERVATIONS:,} inventory "
            f"observations, generated "
            f"{len(inventory):,}."
        )

    # --------------------------------------------------------
    # Primary key uniqueness
    # --------------------------------------------------------

    if (
        inventory[
            "inventory_observation_id"
        ]
        .duplicated()
        .any()
    ):

        raise ValueError(
            "Duplicate inventory_observation_id "
            "values detected."
        )

    # --------------------------------------------------------
    # Required non-null fields
    # --------------------------------------------------------

    required_non_null = [
        "inventory_observation_id",
        "product_id",
        "inventory_location_id",
        "observation_timestamp",
        "inventory_status",
    ]

    for column in required_non_null:

        if inventory[column].isna().any():

            raise ValueError(
                f"Null values detected in "
                f"{column}."
            )

    # --------------------------------------------------------
    # Product referential integrity
    # --------------------------------------------------------

    valid_products = set(
        products[
            "product_id"
        ]
        .astype(str)
    )

    invalid_products = (
        ~inventory[
            "product_id"
        ]
        .astype(str)
        .isin(valid_products)
    )

    if invalid_products.any():

        raise ValueError(
            "Inventory contains invalid "
            "product_id values."
        )

    # --------------------------------------------------------
    # Location validation
    # --------------------------------------------------------

    valid_locations = set(
        generate_inventory_locations()
    )

    invalid_locations = (
        ~inventory[
            "inventory_location_id"
        ]
        .isin(valid_locations)
    )

    if invalid_locations.any():

        raise ValueError(
            "Invalid inventory_location_id "
            "values detected."
        )

    # --------------------------------------------------------
    # Timestamp conversion
    # --------------------------------------------------------

    inventory[
        "observation_timestamp"
    ] = pd.to_datetime(
        inventory[
            "observation_timestamp"
        ],
        errors="coerce",
    )

    if inventory[
        "observation_timestamp"
    ].isna().any():

        raise ValueError(
            "Invalid observation timestamps "
            "detected."
        )

    # --------------------------------------------------------
    # Temporal boundary validation
    # --------------------------------------------------------

    if (
        inventory[
            "observation_timestamp"
        ]
        < period_start
    ).any():

        raise ValueError(
            "Inventory timestamp occurs "
            "before observation period."
        )

    if (
        inventory[
            "observation_timestamp"
        ]
        > period_end
    ).any():

        raise ValueError(
            "Inventory timestamp occurs "
            "after observation period."
        )

    # --------------------------------------------------------
    # Quantity validation
    # --------------------------------------------------------

    if (
        inventory[
            "available_quantity"
        ] < 0
    ).any():

        raise ValueError(
            "Negative available quantity detected."
        )

    if (
        inventory[
            "reserved_quantity"
        ] < 0
    ).any():

        raise ValueError(
            "Negative reserved quantity detected."
        )

    if (
        inventory[
            "reserved_quantity"
        ]
        > inventory[
            "available_quantity"
        ]
    ).any():

        raise ValueError(
            "Reserved quantity exceeds "
            "available quantity."
        )

    # --------------------------------------------------------
    # Status validation
    # --------------------------------------------------------

    if not inventory[
        "inventory_status"
    ].isin(
        INVENTORY_STATUSES
    ).all():

        raise ValueError(
            "Invalid inventory_status detected."
        )

    # --------------------------------------------------------
    # Status consistency
    # --------------------------------------------------------

    quantities = inventory[
        "available_quantity"
    ].to_numpy()

    expected_status = np.where(
        quantities == 0,
        "out_of_stock",
        np.where(
            quantities <= 10,
            "low_stock",
            "in_stock",
        ),
    )

    actual_status = inventory[
        "inventory_status"
    ].to_numpy()

    if not np.array_equal(
        expected_status,
        actual_status,
    ):

        raise ValueError(
            "Inventory status does not match "
            "available quantity."
        )

    # --------------------------------------------------------
    # Product-location grain validation
    # --------------------------------------------------------

    pair_counts = (
        inventory.groupby(
            [
                "product_id",
                "inventory_location_id",
            ]
        )
        .size()
    )

    if not (
        pair_counts
        == OBSERVATIONS_PER_PAIR
    ).all():

        raise ValueError(
            "Product-location observation "
            "counts are inconsistent."
        )

    # --------------------------------------------------------
    # Validation summary
    # --------------------------------------------------------

    print(
        f"[INVENTORY] Validation passed — "
        f"{len(inventory):,} observations."
    )

    print(
        "[INVENTORY] Status distribution:"
    )

    distribution = (
        inventory[
            "inventory_status"
        ]
        .value_counts(
            normalize=True
        )
        .mul(100)
        .sort_index()
        .round(2)
    )

    for status in INVENTORY_STATUSES:

        percentage = distribution.get(
            status,
            0.0,
        )

        print(
            f"    {status:<15} "
            f"{percentage:>6.2f}%"
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 70)

    print(
        "ORGEE — INVENTORY GENERATOR"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    INVENTORY_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load products
    # --------------------------------------------------------

    products = load_products()

    # --------------------------------------------------------
    # Load observation period
    # --------------------------------------------------------

    (
        period_start,
        period_end,
    ) = load_observation_period()

    # --------------------------------------------------------
    # Controlled randomness
    # --------------------------------------------------------

    rng = np.random.default_rng(
        PRIMARY_SEED + 7
    )

    print(
        f"[INVENTORY] Random seed: "
        f"{PRIMARY_SEED + 7}"
    )

    print(
        f"[INVENTORY] Target observations: "
        f"{TARGET_OBSERVATIONS:,}"
    )

    print(
        f"[INVENTORY] Inventory locations: "
        f"{INVENTORY_LOCATION_COUNT}"
    )

    print(
        f"[INVENTORY] Product-location pairs: "
        f"{PRODUCT_LOCATION_PAIRS:,}"
    )

    print(
        f"[INVENTORY] Observations per pair: "
        f"{OBSERVATIONS_PER_PAIR}"
    )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    print(
        "[INVENTORY] Generating inventory..."
    )

    inventory = generate_inventory(
        products=products,
        rng=rng,
        period_start=period_start,
        period_end=period_end,
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_inventory(
        inventory=inventory,
        products=products,
        period_start=period_start,
        period_end=period_end,
    )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    inventory.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("=" * 70)

    print(
        f"[INVENTORY] Generated "
        f"{len(inventory):,} observations."
    )

    print(
        "[INVENTORY] Output written to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()