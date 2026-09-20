"""
ORGEE — Experiment Generator

Generates synthetic experiment definitions and experiment assignments
using the public Olist customer population.

Source:
    Document 7 — Enterprise Generation Configuration
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "public"
ENTERPRISE_DATA_DIR = PROJECT_ROOT / "data" / "enterprise"
EXPERIMENT_OUTPUT_DIR = ENTERPRISE_DATA_DIR / "experiments"

CUSTOMERS_FILE = (
    PUBLIC_DATA_DIR / "olist_customers_dataset.csv"
)

ORDERS_FILE = (
    PUBLIC_DATA_DIR / "olist_orders_dataset.csv"
)

EXPERIMENTS_OUTPUT_FILE = (
    EXPERIMENT_OUTPUT_DIR / "experiments.csv"
)

ASSIGNMENTS_OUTPUT_FILE = (
    EXPERIMENT_OUTPUT_DIR / "experiment_assignments.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

PRIMARY_SEED = 2026

TARGET_EXPERIMENTS = 3

CONTROL_SHARE = 0.50
TREATMENT_SHARE = 0.50

VARIANTS = (
    "control",
    "treatment",
)


# ============================================================
# EXPERIMENT DEFINITIONS
# ============================================================

EXPERIMENT_DEFINITIONS = [
    {
        "experiment_id": "exp_001",
        "experiment_name": "Recommendation Strategy A/B Test",
        "objective": "compare recommendation strategies",
        "primary_metric": "purchase_conversion_rate",
    },
    {
        "experiment_id": "exp_002",
        "experiment_name": "Recommendation Engagement Test",
        "objective": "evaluate recommendation engagement",
        "primary_metric": "purchase_conversion_rate",
    },
    {
        "experiment_id": "exp_003",
        "experiment_name": "Personalization Experience Test",
        "objective": "evaluate personalized recommendation experience",
        "primary_metric": "purchase_conversion_rate",
    },
]


# ============================================================
# CONFIGURATION VALIDATION
# ============================================================

def validate_configuration() -> None:
    """
    Validate static experiment configuration.
    """

    if TARGET_EXPERIMENTS != len(EXPERIMENT_DEFINITIONS):
        raise ValueError(
            "TARGET_EXPERIMENTS does not match "
            "the number of experiment definitions."
        )

    if not np.isclose(
        CONTROL_SHARE + TREATMENT_SHARE,
        1.0,
    ):
        raise ValueError(
            "Control and treatment shares must sum to 1."
        )

    if not np.isclose(
        CONTROL_SHARE,
        0.50,
    ):
        raise ValueError(
            "Control allocation must remain 50%."
        )

    if not np.isclose(
        TREATMENT_SHARE,
        0.50,
    ):
        raise ValueError(
            "Treatment allocation must remain 50%."
        )

    experiment_ids = [
        item["experiment_id"]
        for item in EXPERIMENT_DEFINITIONS
    ]

    if len(experiment_ids) != len(set(experiment_ids)):
        raise ValueError(
            "Duplicate experiment_id detected."
        )


# ============================================================
# LOAD PUBLIC OBSERVATION PERIOD
# ============================================================

def load_public_observation_period() -> tuple[
    pd.Timestamp,
    pd.Timestamp,
]:
    """
    Derive enterprise experiment period from
    the processed public Olist order observation period.
    """

    if not ORDERS_FILE.exists():
        raise FileNotFoundError(
            f"Orders dataset not found:\n{ORDERS_FILE}"
        )

    orders = pd.read_csv(
        ORDERS_FILE,
        usecols=[
            "order_purchase_timestamp",
        ],
    )

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    )

    orders = orders.dropna(
        subset=[
            "order_purchase_timestamp",
        ]
    )

    if orders.empty:
        raise ValueError(
            "No valid order timestamps found."
        )

    period_start = orders[
        "order_purchase_timestamp"
    ].min()

    period_end = orders[
        "order_purchase_timestamp"
    ].max()

    if period_start >= period_end:
        raise ValueError(
            "Invalid public observation period."
        )

    return period_start, period_end


# ============================================================
# GENERATE EXPERIMENT DEFINITIONS
# ============================================================

def generate_experiments(
    period_start: pd.Timestamp,
    period_end: pd.Timestamp,
) -> pd.DataFrame:
    """
    Generate configured experiment definitions.

    Experiment periods remain inside the public
    behavioral observation period.
    """

    total_seconds = int(
        (
            period_end - period_start
        ).total_seconds()
    )

    minimum_period = (
        90 * 24 * 60 * 60
    )

    if total_seconds < minimum_period:
        raise ValueError(
            "Observation period is too short "
            "for experiment generation."
        )

    rng = np.random.default_rng(
        PRIMARY_SEED + 800
    )

    experiments = []

    for index, definition in enumerate(
        EXPERIMENT_DEFINITIONS,
        start=1,
    ):

        start_fraction = (
            0.15
            + ((index - 1) * 0.20)
        )

        start_offset = int(
            total_seconds
            * start_fraction
        )

        experiment_start = (
            period_start
            + pd.to_timedelta(
                start_offset,
                unit="s",
            )
        )

        duration_days = int(
            rng.integers(
                45,
                91,
            )
        )

        experiment_end = (
            experiment_start
            + pd.Timedelta(
                days=duration_days
            )
        )

        if experiment_end > period_end:
            experiment_end = period_end

        if experiment_start >= experiment_end:
            raise ValueError(
                f"Invalid experiment period for "
                f"{definition['experiment_id']}."
            )

        # ----------------------------------------------------
        # Variant strategy definitions
        # ----------------------------------------------------

        if definition["experiment_id"] == "exp_001":

            control_strategy = (
                "Top Sellers Recommendations"
            )

            treatment_strategy = (
                "Personalized Content-Based Recommendations"
            )

        elif definition["experiment_id"] == "exp_002":

            control_strategy = (
                "Standard Recommendation Experience"
            )

            treatment_strategy = (
                "Personalized Recommendation Experience"
            )

        else:

            control_strategy = (
                "Generic Product Recommendations"
            )

            treatment_strategy = (
                "Content-Based Personalized Recommendations"
            )

        experiments.append(
            {
                "experiment_id": definition[
                    "experiment_id"
                ],
                "experiment_name": definition[
                    "experiment_name"
                ],
                "objective": definition[
                    "objective"
                ],
                "start_timestamp": experiment_start,
                "end_timestamp": experiment_end,
                "primary_metric": definition[
                    "primary_metric"
                ],
                "control_variant": control_strategy,
                "treatment_variant": treatment_strategy,
            }
        )

    return pd.DataFrame(
        experiments
    )


# ============================================================
# LOAD EXPERIMENTAL POPULATION
# ============================================================

def load_experimental_population() -> pd.DataFrame:
    """
    Load public customer population.

    Public customer_id values remain authoritative.
    """

    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(
            f"Customer dataset not found:\n{CUSTOMERS_FILE}"
        )

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        usecols=[
            "customer_id",
        ],
    )

    customers["customer_id"] = (
        customers["customer_id"]
        .astype(str)
    )

    customers = customers.dropna(
        subset=[
            "customer_id",
        ]
    )

    customers = customers.drop_duplicates(
        subset=[
            "customer_id",
        ]
    )

    if customers.empty:
        raise ValueError(
            "Experimental customer population is empty."
        )

    return customers


# ============================================================
# GENERATE EXPERIMENT ASSIGNMENTS
# ============================================================

def generate_assignments(
    customers: pd.DataFrame,
    experiments: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate one assignment per customer per experiment.

    Target allocation:

        50% control
        50% treatment

    Assignment is deterministic under the configured seed.
    """

    rng = np.random.default_rng(
        PRIMARY_SEED + 801
    )

    assignments = []

    customer_ids = customers[
        "customer_id"
    ].to_numpy()

    for experiment in experiments.itertuples(
        index=False
    ):

        shuffled_customer_ids = (
            customer_ids.copy()
        )

        rng.shuffle(
            shuffled_customer_ids
        )

        customer_count = len(
            shuffled_customer_ids
        )

        control_count = int(
            round(
                customer_count
                * CONTROL_SHARE
            )
        )

        control_ids = (
            shuffled_customer_ids[
                :control_count
            ]
        )

        treatment_ids = (
            shuffled_customer_ids[
                control_count:
            ]
        )

        experiment_start = pd.Timestamp(
            experiment.start_timestamp
        )

        experiment_end = pd.Timestamp(
            experiment.end_timestamp
        )

        duration_seconds = int(
            (
                experiment_end
                - experiment_start
            ).total_seconds()
        )

        total_assignments = (
            len(control_ids)
            + len(treatment_ids)
        )

        assignment_timestamps = (
            experiment_start
            + pd.to_timedelta(
                rng.integers(
                    0,
                    duration_seconds + 1,
                    size=total_assignments,
                ),
                unit="s",
            )
        )

        # ----------------------------------------------------
        # Control
        # ----------------------------------------------------

        for position, customer_id in enumerate(
            control_ids
        ):

            assignments.append(
                {
                    "experiment_assignment_id": (
                        f"assign_{experiment.experiment_id}"
                        f"_c_{position + 1:06d}"
                    ),
                    "experiment_id": (
                        experiment.experiment_id
                    ),
                    "customer_id": str(
                        customer_id
                    ),
                    "variant": "control",
                    "assignment_timestamp": (
                        assignment_timestamps[
                            position
                        ]
                    ),
                }
            )

        # ----------------------------------------------------
        # Treatment
        # ----------------------------------------------------

        treatment_start_position = len(
            control_ids
        )

        for position, customer_id in enumerate(
            treatment_ids
        ):

            assignments.append(
                {
                    "experiment_assignment_id": (
                        f"assign_{experiment.experiment_id}"
                        f"_t_{position + 1:06d}"
                    ),
                    "experiment_id": (
                        experiment.experiment_id
                    ),
                    "customer_id": str(
                        customer_id
                    ),
                    "variant": "treatment",
                    "assignment_timestamp": (
                        assignment_timestamps[
                            treatment_start_position
                            + position
                        ]
                    ),
                }
            )

    return pd.DataFrame(
        assignments
    )


# ============================================================
# VALIDATE EXPERIMENTS
# ============================================================

def validate_experiments(
    experiments: pd.DataFrame,
) -> None:
    """
    Validate experiment definitions.
    """

    required_columns = {
        "experiment_id",
        "experiment_name",
        "objective",
        "start_timestamp",
        "end_timestamp",
        "primary_metric",
        "control_variant",
        "treatment_variant",
    }

    missing = (
        required_columns
        - set(experiments.columns)
    )

    if missing:
        raise ValueError(
            f"Missing experiment columns: "
            f"{sorted(missing)}"
        )

    if len(experiments) != TARGET_EXPERIMENTS:
        raise ValueError(
            f"Expected {TARGET_EXPERIMENTS} experiments, "
            f"generated {len(experiments)}."
        )

    if experiments[
        "experiment_id"
    ].duplicated().any():

        raise ValueError(
            "Duplicate experiment_id detected."
        )

    if (
        experiments["start_timestamp"]
        >= experiments["end_timestamp"]
    ).any():

        raise ValueError(
            "Experiment end occurs before "
            "experiment start."
        )

    if experiments[
        "primary_metric"
    ].isna().any():

        raise ValueError(
            "Missing primary metric detected."
        )

    print(
        f"[EXPERIMENT] Validation passed — "
        f"{len(experiments)} experiments."
    )


# ============================================================
# VALIDATE ASSIGNMENTS
# ============================================================

def validate_assignments(
    assignments: pd.DataFrame,
    experiments: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:
    """
    Validate experiment assignments.
    """

    required_columns = {
        "experiment_assignment_id",
        "experiment_id",
        "customer_id",
        "variant",
        "assignment_timestamp",
    }

    missing = (
        required_columns
        - set(assignments.columns)
    )

    if missing:
        raise ValueError(
            f"Missing assignment columns: "
            f"{sorted(missing)}"
        )

    # --------------------------------------------------------
    # Assignment ID uniqueness
    # --------------------------------------------------------

    if assignments[
        "experiment_assignment_id"
    ].duplicated().any():

        raise ValueError(
            "Duplicate experiment_assignment_id detected."
        )

    # --------------------------------------------------------
    # Customer referential integrity
    # --------------------------------------------------------

    valid_customer_ids = set(
        customers["customer_id"]
    )

    invalid_customers = (
        ~assignments["customer_id"].isin(
            valid_customer_ids
        )
    )

    if invalid_customers.any():

        raise ValueError(
            "Experiment assignment contains "
            "invalid customer_id values."
        )

    # --------------------------------------------------------
    # Experiment referential integrity
    # --------------------------------------------------------

    valid_experiment_ids = set(
        experiments["experiment_id"]
    )

    invalid_experiments = (
        ~assignments["experiment_id"].isin(
            valid_experiment_ids
        )
    )

    if invalid_experiments.any():

        raise ValueError(
            "Experiment assignment contains "
            "invalid experiment_id values."
        )

    # --------------------------------------------------------
    # Variant validation
    # --------------------------------------------------------

    if not assignments[
        "variant"
    ].isin(VARIANTS).all():

        raise ValueError(
            "Invalid experiment variant detected."
        )

    # --------------------------------------------------------
    # One assignment per customer per experiment
    # --------------------------------------------------------

    duplicate_assignments = (
        assignments
        .duplicated(
            subset=[
                "experiment_id",
                "customer_id",
            ],
            keep=False,
        )
    )

    if duplicate_assignments.any():

        raise ValueError(
            "A customer has multiple assignments "
            "within the same experiment."
        )

    # --------------------------------------------------------
    # Assignment timestamp validation
    # --------------------------------------------------------

    experiment_periods = experiments[
        [
            "experiment_id",
            "start_timestamp",
            "end_timestamp",
        ]
    ]

    merged = assignments.merge(
        experiment_periods,
        on="experiment_id",
        how="left",
    )

    outside_period = (
        (
            merged["assignment_timestamp"]
            < merged["start_timestamp"]
        )
        |
        (
            merged["assignment_timestamp"]
            > merged["end_timestamp"]
        )
    )

    if outside_period.any():

        raise ValueError(
            "Assignment timestamp falls outside "
            "experiment period."
        )

    # --------------------------------------------------------
    # Allocation validation
    #
    # IMPORTANT:
    # Do NOT use groupby().apply() here.
    # The explicit count -> total -> share calculation
    # avoids the Pandas reset_index collision.
    # --------------------------------------------------------

    allocation = (
        assignments
        .groupby(
            [
                "experiment_id",
                "variant",
            ]
        )
        .size()
        .reset_index(
            name="count"
        )
    )

    totals = (
        allocation
        .groupby(
            "experiment_id"
        )["count"]
        .sum()
        .reset_index(
            name="total"
        )
    )

    allocation = allocation.merge(
        totals,
        on="experiment_id",
        how="left",
    )

    allocation["share"] = (
        allocation["count"]
        / allocation["total"]
    )

    for experiment_id in (
        experiments["experiment_id"]
    ):

        experiment_allocation = allocation[
            allocation["experiment_id"]
            == experiment_id
        ]

        for variant in VARIANTS:

            row = experiment_allocation[
                experiment_allocation["variant"]
                == variant
            ]

            if row.empty:

                raise ValueError(
                    f"Missing {variant} allocation "
                    f"for {experiment_id}."
                )

            share = float(
                row["share"].iloc[0]
            )

            if not np.isclose(
                share,
                0.50,
                atol=0.001,
            ):

                raise ValueError(
                    f"Unexpected allocation for "
                    f"{experiment_id} / {variant}: "
                    f"{share:.4f}"
                )

    print(
        "[EXPERIMENT] Assignment validation passed."
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    experiments: pd.DataFrame,
    assignments: pd.DataFrame,
) -> None:
    """
    Print experiment generation summary.
    """

    print()
    print(
        "=" * 70
    )

    print(
        "[EXPERIMENT] Experiment summary:"
    )

    for experiment in experiments.itertuples(
        index=False
    ):

        experiment_assignments = (
            assignments[
                assignments["experiment_id"]
                == experiment.experiment_id
            ]
        )

        control_count = (
            experiment_assignments[
                experiment_assignments["variant"]
                == "control"
            ]
            .shape[0]
        )

        treatment_count = (
            experiment_assignments[
                experiment_assignments["variant"]
                == "treatment"
            ]
            .shape[0]
        )

        total = (
            control_count
            + treatment_count
        )

        print(
            f"  {experiment.experiment_id}: "
            f"{total:,} assignments"
        )

        print(
            f"      control   = "
            f"{control_count:,} "
            f"({control_count / total:.2%})"
        )

        print(
            f"      treatment = "
            f"{treatment_count:,} "
            f"({treatment_count / total:.2%})"
        )

    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print(
        "=" * 70
    )

    print(
        "ORGEE — EXPERIMENT GENERATOR"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # Configuration validation
    # --------------------------------------------------------

    validate_configuration()

    # --------------------------------------------------------
    # Public observation period
    # --------------------------------------------------------

    print(
        "[EXPERIMENT] Loading public order observation period..."
    )

    period_start, period_end = (
        load_public_observation_period()
    )

    print(
        f"[EXPERIMENT] Period start: "
        f"{period_start}"
    )

    print(
        f"[EXPERIMENT] Period end: "
        f"{period_end}"
    )

    # --------------------------------------------------------
    # Generate experiments
    # --------------------------------------------------------

    print()
    print(
        f"[EXPERIMENT] Generating "
        f"{TARGET_EXPERIMENTS} experiments..."
    )

    experiments = generate_experiments(
        period_start,
        period_end,
    )

    validate_experiments(
        experiments
    )

    # --------------------------------------------------------
    # Load customers
    # --------------------------------------------------------

    print()
    print(
        "[EXPERIMENT] Loading public customers..."
    )

    customers = load_experimental_population()

    print(
        f"[EXPERIMENT] Loaded "
        f"{len(customers):,} customers."
    )

    # --------------------------------------------------------
    # Generate assignments
    # --------------------------------------------------------

    print()
    print(
        "[EXPERIMENT] Generating experiment assignments..."
    )

    assignments = generate_assignments(
        customers,
        experiments,
    )

    print(
        f"[EXPERIMENT] Generated "
        f"{len(assignments):,} assignments."
    )

    # --------------------------------------------------------
    # Validate assignments
    # --------------------------------------------------------

    print(
        "[EXPERIMENT] Running validation..."
    )

    validate_assignments(
        assignments,
        experiments,
        customers,
    )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    EXPERIMENT_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Write experiments
    # --------------------------------------------------------

    experiments.to_csv(
        EXPERIMENTS_OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Write assignments
    # --------------------------------------------------------

    assignments.to_csv(
        ASSIGNMENTS_OUTPUT_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_summary(
        experiments,
        assignments,
    )

    print()
    print(
        f"[EXPERIMENT] Generated "
        f"{len(experiments)} experiments."
    )

    print(
        f"[EXPERIMENT] Generated "
        f"{len(assignments):,} experiment assignments."
    )

    print()
    print(
        "[EXPERIMENT] Experiment output:"
    )

    print(
        EXPERIMENTS_OUTPUT_FILE
    )

    print()
    print(
        "[EXPERIMENT] Assignment output:"
    )

    print(
        ASSIGNMENTS_OUTPUT_FILE
    )

    print()
    print(
        "=" * 70
    )

    print(
        "[EXPERIMENT] COMPLETE"
    )

    print(
        "=" * 70
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()