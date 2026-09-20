"""
ORGEE — EXPERIMENT VALIDATION

Validates:
    1. experiments.csv
    2. experiment_assignments.csv

Checks:
    - File existence
    - Experiment schema
    - Required-field completeness
    - Expected experiment count
    - experiment_id uniqueness
    - Experiment timestamp validity
    - Assignment schema
    - Assignment required-field completeness
    - experiment_assignment_id uniqueness
    - Experiment referential integrity
    - Customer referential integrity
    - Variant validity
    - Assignment timestamp validity
    - One assignment per customer per experiment
    - Assignment coverage
    - Variant allocation
    - Assignment temporal integrity
"""


from pathlib import Path

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "experiments"
)

EXPERIMENTS_FILE = (
    EXPERIMENT_DIR
    / "experiments.csv"
)

ASSIGNMENTS_FILE = (
    EXPERIMENT_DIR
    / "experiment_assignments.csv"
)

CUSTOMERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_customers_dataset.csv"
)


# ============================================================
# EXPECTED CONFIGURATION
# ============================================================

EXPECTED_EXPERIMENTS = 3

EXPECTED_VARIANTS = {
    "control",
    "treatment",
}

EXPECTED_ALLOCATION = 0.50

ALLOCATION_TOLERANCE = 0.01


# ============================================================
# HELPERS
# ============================================================

def fail(message: str) -> None:
    """
    Raise a validation failure.
    """

    raise ValueError(
        f"[EXPERIMENT VALIDATION FAILED] {message}"
    )


def require_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    """
    Validate required columns.
    """

    missing = (
        required_columns
        -
        set(dataframe.columns)
    )

    if missing:

        fail(
            f"Missing {dataset_name} columns: "
            f"{sorted(missing)}\n"
            f"Actual columns: "
            f"{list(dataframe.columns)}"
        )


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("ORGEE — EXPERIMENT VALIDATION")
print("=" * 70)


# ============================================================
# FILE EXISTENCE
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking required files..."
)


if not EXPERIMENTS_FILE.exists():

    fail(
        f"Experiments file not found:\n"
        f"{EXPERIMENTS_FILE}"
    )


if not ASSIGNMENTS_FILE.exists():

    fail(
        f"Experiment assignments file not found:\n"
        f"{ASSIGNMENTS_FILE}"
    )


if not CUSTOMERS_FILE.exists():

    fail(
        f"Customer reference file not found:\n"
        f"{CUSTOMERS_FILE}"
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Required files exist."
)


# ============================================================
# LOAD EXPERIMENTS
# ============================================================

print()
print(
    "[EXPERIMENT VALIDATION] "
    "Loading experiments..."
)

experiments = pd.read_csv(
    EXPERIMENTS_FILE
)

print(
    f"[EXPERIMENT VALIDATION] "
    f"Loaded {len(experiments):,} experiments."
)


# ============================================================
# EXPERIMENT SCHEMA
# ============================================================

print(
    "\n[EXPERIMENT VALIDATION] "
    "Checking experiment schema..."
)

REQUIRED_EXPERIMENT_COLUMNS = {
    "experiment_id",
    "experiment_name",
    "objective",
    "start_timestamp",
    "end_timestamp",
    "primary_metric",
}

require_columns(
    experiments,
    REQUIRED_EXPERIMENT_COLUMNS,
    "experiment",
)

print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Experiment schema validation passed."
)


# ============================================================
# EXPERIMENT REQUIRED FIELDS
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment required fields..."
)

for column in REQUIRED_EXPERIMENT_COLUMNS:

    null_count = int(
        experiments[column]
        .isna()
        .sum()
    )

    if null_count > 0:

        fail(
            f"Experiment column '{column}' "
            f"contains {null_count:,} null values."
        )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Experiment required-field completeness passed."
)


# ============================================================
# EXPERIMENT COUNT
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment count..."
)

if len(experiments) != EXPECTED_EXPERIMENTS:

    fail(
        f"Expected {EXPECTED_EXPERIMENTS} experiments, "
        f"found {len(experiments):,}."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    f"Experiment count = {len(experiments):,}."
)


# ============================================================
# EXPERIMENT ID
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment_id..."
)

experiments["experiment_id"] = (
    experiments["experiment_id"]
    .astype(str)
    .str.strip()
)


if (
    experiments["experiment_id"]
    .eq("")
    .any()
):

    fail(
        "Blank experiment_id values detected."
    )


if (
    experiments["experiment_id"]
    .duplicated()
    .any()
):

    duplicate_count = int(
        experiments[
            "experiment_id"
        ]
        .duplicated()
        .sum()
    )

    fail(
        f"Duplicate experiment_id values detected: "
        f"{duplicate_count:,}"
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "experiment_id uniqueness passed."
)


# ============================================================
# EXPERIMENT TIMESTAMPS
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment timestamps..."
)

experiments[
    "start_timestamp"
] = pd.to_datetime(
    experiments[
        "start_timestamp"
    ],
    errors="coerce",
)

experiments[
    "end_timestamp"
] = pd.to_datetime(
    experiments[
        "end_timestamp"
    ],
    errors="coerce",
)


invalid_start = (
    experiments[
        "start_timestamp"
    ]
    .isna()
)

invalid_end = (
    experiments[
        "end_timestamp"
    ]
    .isna()
)


if invalid_start.any():

    fail(
        f"{invalid_start.sum():,} invalid "
        "experiment start_timestamp values."
    )


if invalid_end.any():

    fail(
        f"{invalid_end.sum():,} invalid "
        "experiment end_timestamp values."
    )


invalid_order = (
    experiments[
        "end_timestamp"
    ]
    <
    experiments[
        "start_timestamp"
    ]
)


if invalid_order.any():

    fail(
        f"{invalid_order.sum():,} experiments have "
        "end_timestamp before start_timestamp."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Experiment timestamp validation passed."
)


# ============================================================
# LOAD CUSTOMERS
# ============================================================

print(
    "\n[EXPERIMENT VALIDATION] "
    "Loading public customers..."
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
    .str.strip()
)


if (
    customers["customer_id"]
    .eq("")
    .any()
):

    fail(
        "Blank customer_id values detected "
        "in public customers."
    )


valid_customer_ids = set(
    customers["customer_id"]
)


print(
    f"[EXPERIMENT VALIDATION] "
    f"Loaded {len(customers):,} customers."
)


# ============================================================
# LOAD ASSIGNMENTS
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Loading experiment assignments..."
)

assignments = pd.read_csv(
    ASSIGNMENTS_FILE
)

print(
    f"[EXPERIMENT VALIDATION] "
    f"Loaded {len(assignments):,} assignments."
)


# ============================================================
# ASSIGNMENT SCHEMA
# ============================================================

print(
    "\n[EXPERIMENT VALIDATION] "
    "Checking assignment schema..."
)

REQUIRED_ASSIGNMENT_COLUMNS = {
    "experiment_assignment_id",
    "experiment_id",
    "customer_id",
    "variant",
    "assignment_timestamp",
}

require_columns(
    assignments,
    REQUIRED_ASSIGNMENT_COLUMNS,
    "experiment assignment",
)


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment schema validation passed."
)


# ============================================================
# ASSIGNMENT REQUIRED FIELDS
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking assignment required fields..."
)

for column in REQUIRED_ASSIGNMENT_COLUMNS:

    null_count = int(
        assignments[column]
        .isna()
        .sum()
    )

    if null_count > 0:

        fail(
            f"Assignment column '{column}' "
            f"contains {null_count:,} null values."
        )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment required-field completeness passed."
)


# ============================================================
# ASSIGNMENT ROW COUNT
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking assignment row count..."
)

if len(assignments) == 0:

    fail(
        "Experiment assignments dataset is empty."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    f"Assignment row count = "
    f"{len(assignments):,}."
)


# ============================================================
# ASSIGNMENT ID
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment_assignment_id..."
)

assignments[
    "experiment_assignment_id"
] = (
    assignments[
        "experiment_assignment_id"
    ]
    .astype(str)
    .str.strip()
)


if (
    assignments[
        "experiment_assignment_id"
    ]
    .eq("")
    .any()
):

    fail(
        "Blank experiment_assignment_id values detected."
    )


if (
    assignments[
        "experiment_assignment_id"
    ]
    .duplicated()
    .any()
):

    duplicate_count = int(
        assignments[
            "experiment_assignment_id"
        ]
        .duplicated()
        .sum()
    )

    fail(
        "Duplicate experiment_assignment_id "
        f"values detected: {duplicate_count:,}"
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment ID uniqueness passed."
)


# ============================================================
# ASSIGNMENT EXPERIMENT IDs
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment referential integrity..."
)

assignments["experiment_id"] = (
    assignments["experiment_id"]
    .astype(str)
    .str.strip()
)


valid_experiment_ids = set(
    experiments["experiment_id"]
)


invalid_experiment_ids = (
    set(
        assignments["experiment_id"]
    )
    -
    valid_experiment_ids
)


if invalid_experiment_ids:

    fail(
        "Found invalid experiment IDs: "
        f"{sorted(invalid_experiment_ids)}"
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Experiment referential integrity passed."
)


# ============================================================
# CUSTOMER REFERENTIAL INTEGRITY
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking customer referential integrity..."
)

assignments["customer_id"] = (
    assignments["customer_id"]
    .astype(str)
    .str.strip()
)


if (
    assignments["customer_id"]
    .eq("")
    .any()
):

    fail(
        "Blank customer_id values detected "
        "in experiment assignments."
    )


invalid_customer_ids = (
    set(
        assignments["customer_id"]
    )
    -
    valid_customer_ids
)


if invalid_customer_ids:

    fail(
        f"Found {len(invalid_customer_ids):,} "
        "customer IDs not present in public customers."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Customer referential integrity passed."
)


# ============================================================
# VARIANT VALIDATION
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experiment variants..."
)

assignments["variant"] = (
    assignments["variant"]
    .astype(str)
    .str.strip()
)


invalid_variants = (
    ~assignments["variant"].isin(
        EXPECTED_VARIANTS
    )
)


if invalid_variants.any():

    values = sorted(
        assignments.loc[
            invalid_variants,
            "variant",
        ]
        .unique()
        .tolist()
    )

    fail(
        f"Invalid variant values: {values}"
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Variant validation passed."
)


# ============================================================
# ASSIGNMENT TIMESTAMPS
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking assignment timestamps..."
)

assignments[
    "assignment_timestamp"
] = pd.to_datetime(
    assignments[
        "assignment_timestamp"
    ],
    errors="coerce",
)


invalid_assignment_timestamps = (
    assignments[
        "assignment_timestamp"
    ]
    .isna()
)


if invalid_assignment_timestamps.any():

    fail(
        f"{invalid_assignment_timestamps.sum():,} "
        "invalid assignment_timestamp values."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment timestamp validation passed."
)


# ============================================================
# ONE ASSIGNMENT PER CUSTOMER PER EXPERIMENT
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking experimental-unit uniqueness..."
)

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

    duplicate_rows = int(
        duplicate_assignments.sum()
    )

    fail(
        f"{duplicate_rows:,} rows violate the rule "
        "of one assignment per customer per experiment."
    )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Experimental-unit uniqueness passed."
)


# ============================================================
# ASSIGNMENT COVERAGE
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking assignment coverage..."
)

assignment_counts = (
    assignments[
        "experiment_id"
    ]
    .value_counts()
    .sort_index()
)


for experiment_id in (
    experiments["experiment_id"]
):

    count = int(
        assignment_counts.get(
            experiment_id,
            0,
        )
    )

    if count == 0:

        fail(
            f"{experiment_id} has no assignments."
        )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment coverage validation passed."
)


# ============================================================
# VARIANT ALLOCATION
# ============================================================

print(
    "\n[EXPERIMENT VALIDATION] "
    "Checking variant allocation..."
)


for experiment_id in (
    experiments["experiment_id"]
):

    subset = assignments[
        assignments[
            "experiment_id"
        ]
        ==
        experiment_id
    ]


    total = len(subset)


    if total == 0:

        fail(
            f"{experiment_id} has zero assignments."
        )


    counts = (
        subset[
            "variant"
        ]
        .value_counts()
    )


    print()

    print(
        f"    {experiment_id}: "
        f"{total:,} assignments"
    )


    for variant in [
        "control",
        "treatment",
    ]:

        count = int(
            counts.get(
                variant,
                0,
            )
        )


        share = (
            count
            /
            total
        )


        print(
            f"        {variant:<10} = "
            f"{count:>8,} "
            f"({share:.2%})"
        )


        if (
            abs(
                share
                -
                EXPECTED_ALLOCATION
            )
            >
            ALLOCATION_TOLERANCE
        ):

            fail(
                f"{experiment_id} {variant} "
                f"allocation = {share:.2%}, "
                f"expected approximately "
                f"{EXPECTED_ALLOCATION:.2%} "
                f"with ±{ALLOCATION_TOLERANCE:.2%} "
                "tolerance."
            )


print()

print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Variant allocation validation passed."
)


# ============================================================
# ASSIGNMENT TEMPORAL INTEGRITY
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "Checking assignment temporal integrity..."
)


experiment_periods = (
    experiments[
        [
            "experiment_id",
            "start_timestamp",
            "end_timestamp",
        ]
    ]
    .set_index(
        "experiment_id"
    )
)


for experiment_id, row in (
    experiment_periods.iterrows()
):

    subset = assignments[
        assignments[
            "experiment_id"
        ]
        ==
        experiment_id
    ]


    invalid_time = (
        (
            subset[
                "assignment_timestamp"
            ]
            <
            row[
                "start_timestamp"
            ]
        )
        |
        (
            subset[
                "assignment_timestamp"
            ]
            >
            row[
                "end_timestamp"
            ]
        )
    )


    if invalid_time.any():

        count = int(
            invalid_time.sum()
        )

        fail(
            f"{count:,} assignments for "
            f"{experiment_id} fall outside "
            "the experiment period."
        )


print(
    "[EXPERIMENT VALIDATION PASSED] "
    "Assignment temporal integrity passed."
)


# ============================================================
# EXPERIMENT SUMMARY
# ============================================================

print()
print("=" * 70)

print(
    "[EXPERIMENT VALIDATION] SUMMARY"
)

print("=" * 70)


print(
    f"Experiments          = "
    f"{len(experiments):,}"
)


print(
    f"Assignments          = "
    f"{len(assignments):,}"
)


print(
    f"Unique customers     = "
    f"{assignments['customer_id'].nunique():,}"
)


print(
    f"Unique assignment IDs = "
    f"{assignments['experiment_assignment_id'].nunique():,}"
)


print(
    f"Experiments assigned = "
    f"{assignments['experiment_id'].nunique():,}"
)


print()

print(
    "[EXPERIMENT VALIDATION] "
    "Assignment distribution:"
)


for experiment_id in (
    experiments["experiment_id"]
):

    subset = assignments[
        assignments[
            "experiment_id"
        ]
        ==
        experiment_id
    ]


    print(
        f"    {experiment_id:<12} = "
        f"{len(subset):>10,} assignments"
    )


print("=" * 70)


# ============================================================
# COMPLETE
# ============================================================

print(
    "[EXPERIMENT VALIDATION] "
    "COMPLETE — ALL CHECKS PASSED"
)

print("=" * 70)