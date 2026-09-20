"""
ORGEE — Recommendation Generator

Generates synthetic recommendation interaction events
for the ORGEE recommendation and experimentation layers.

Source:
    Document 7 — Enterprise Generation Configuration
"""

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

CURRENT_DIR = Path(__file__).resolve().parent

CONFIG_FILE = (
    CURRENT_DIR
    / "01_generator_config.py"
)

if not CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"Generator configuration not found:\n"
        f"{CONFIG_FILE}"
    )

spec = importlib.util.spec_from_file_location(
    "orgee_generator_config",
    CONFIG_FILE,
)

if spec is None or spec.loader is None:
    raise ImportError(
        "Unable to load generator configuration."
    )

config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

PRIMARY_SEED = int(
    config.PRIMARY_SEED
)

RECOMMENDATION_PROBABILITIES = (
    config.RECOMMENDATION_FUNNEL_PROBABILITIES
)

IMPRESSION_TO_CLICK_PROBABILITY = float(
    RECOMMENDATION_PROBABILITIES[
        "impression_to_click"
    ]
)

CLICK_TO_PURCHASE_PROBABILITY = float(
    RECOMMENDATION_PROBABILITIES[
        "click_to_purchase"
    ]
)

VARIANTS = tuple(
    config.EXPERIMENT_VARIANTS
)

PRIMARY_RECOMMENDATION_EXPERIMENT = (
    config.PRIMARY_RECOMMENDATION_EXPERIMENT
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
)

ENTERPRISE_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
)

SESSION_DIR = (
    ENTERPRISE_DIR
    / "sessions"
)

EXPERIMENT_DIR = (
    ENTERPRISE_DIR
    / "experiments"
)

RECOMMENDATION_DIR = (
    ENTERPRISE_DIR
    / "recommendations"
)


# ============================================================
# INPUT FILES
# ============================================================

SESSIONS_FILE = (
    SESSION_DIR
    / "sessions.csv"
)

EXPERIMENTS_FILE = (
    EXPERIMENT_DIR
    / "experiments.csv"
)

EXPERIMENT_ASSIGNMENTS_FILE = (
    EXPERIMENT_DIR
    / "experiment_assignments.csv"
)

PRODUCTS_FILE = (
    PUBLIC_DATA_DIR
    / "olist_products_dataset.csv"
)


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_FILE = (
    RECOMMENDATION_DIR
    / "recommendation_events.csv"
)


# ============================================================
# EVENT TYPES
# ============================================================

EVENT_TYPES = (
    "recommendation_impression",
    "recommendation_click",
    "recommendation_conversion",
)


# ============================================================
# LOAD DATA
# ============================================================

def load_required_files():

    print(
        "[RECOMMENDATION] Loading sessions..."
    )

    if not SESSIONS_FILE.exists():
        raise FileNotFoundError(
            f"Sessions file not found:\n"
            f"{SESSIONS_FILE}"
        )

    sessions = pd.read_csv(
        SESSIONS_FILE,
        parse_dates=[
            "session_start_timestamp",
            "session_end_timestamp",
        ],
    )

    print(
        f"[RECOMMENDATION] Loaded "
        f"{len(sessions):,} sessions."
    )

    print(
        "[RECOMMENDATION] Loading experiments..."
    )

    if not EXPERIMENTS_FILE.exists():
        raise FileNotFoundError(
            f"Experiments file not found:\n"
            f"{EXPERIMENTS_FILE}"
        )

    experiments = pd.read_csv(
        EXPERIMENTS_FILE,
        parse_dates=[
            "start_timestamp",
            "end_timestamp",
        ],
    )

    print(
        f"[RECOMMENDATION] Loaded "
        f"{len(experiments):,} experiments."
    )

    print(
        "[RECOMMENDATION] Loading experiment assignments..."
    )

    if not EXPERIMENT_ASSIGNMENTS_FILE.exists():
        raise FileNotFoundError(
            f"Experiment assignments not found:\n"
            f"{EXPERIMENT_ASSIGNMENTS_FILE}"
        )

    assignments = pd.read_csv(
        EXPERIMENT_ASSIGNMENTS_FILE,
        parse_dates=[
            "assignment_timestamp",
        ],
    )

    print(
        f"[RECOMMENDATION] Loaded "
        f"{len(assignments):,} assignments."
    )

    print(
        "[RECOMMENDATION] Loading public products..."
    )

    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            f"Products file not found:\n"
            f"{PRODUCTS_FILE}"
        )

    products = pd.read_csv(
        PRODUCTS_FILE,
        usecols=["product_id"],
    )

    products["product_id"] = (
        products["product_id"]
        .astype(str)
    )

    products = products.drop_duplicates(
        subset=["product_id"]
    )

    print(
        f"[RECOMMENDATION] Loaded "
        f"{len(products):,} products."
    )

    return (
        sessions,
        experiments,
        assignments,
        products,
    )


# ============================================================
# BUILD RECOMMENDATION POPULATION
# ============================================================

def build_recommendation_pool(
    sessions,
    experiments,
    assignments,
):

    required_session_columns = {
        "session_id",
        "anonymous_id",
        "customer_id",
        "session_start_timestamp",
        "session_end_timestamp",
    }

    missing = (
        required_session_columns
        - set(sessions.columns)
    )

    if missing:
        raise ValueError(
            f"Missing session columns: {sorted(missing)}"
        )

    required_experiment_columns = {
        "experiment_id",
        "start_timestamp",
        "end_timestamp",
    }

    missing = (
        required_experiment_columns
        - set(experiments.columns)
    )

    if missing:
        raise ValueError(
            "Missing experiment columns: "
            f"{sorted(missing)}"
        )

    required_assignment_columns = {
        "experiment_id",
        "customer_id",
        "variant",
        "assignment_timestamp",
    }

    missing = (
        required_assignment_columns
        - set(assignments.columns)
    )

    if missing:
        raise ValueError(
            "Missing experiment assignment columns: "
            f"{sorted(missing)}"
        )

    sessions = sessions.copy()
    experiments = experiments.copy()
    assignments = assignments.copy()

    sessions["customer_id"] = (
        sessions["customer_id"]
        .astype(str)
    )

    sessions["session_id"] = (
        sessions["session_id"]
        .astype(str)
    )

    sessions["anonymous_id"] = (
        sessions["anonymous_id"]
        .astype(str)
    )

    assignments["customer_id"] = (
        assignments["customer_id"]
        .astype(str)
    )

    assignments["experiment_id"] = (
        assignments["experiment_id"]
        .astype(str)
    )

    experiments["experiment_id"] = (
        experiments["experiment_id"]
        .astype(str)
    )

    # --------------------------------------------------------
    # Primary experiment
    # --------------------------------------------------------

    primary_experiment = (
        sorted(
            assignments[
                "experiment_id"
            ]
            .dropna()
            .unique()
            .tolist()
        )[0]
    )

    print(
        "[RECOMMENDATION] Primary experiment: "
        f"{primary_experiment}"
    )

    primary_experiment_definition = (
        experiments[
            experiments["experiment_id"]
            == primary_experiment
        ]
        .copy()
    )

    if primary_experiment_definition.empty:
        raise ValueError(
            "Primary experiment definition not found."
        )

    primary_assignments = assignments[
        assignments["experiment_id"]
        == primary_experiment
    ].copy()

    primary_assignments = (
        primary_assignments[
            [
                "customer_id",
                "experiment_id",
                "variant",
                "assignment_timestamp",
            ]
        ]
        .drop_duplicates(
            subset=[
                "customer_id",
                "experiment_id",
            ]
        )
    )

    # --------------------------------------------------------
    # Join customer assignment to sessions
    # --------------------------------------------------------

    pool = sessions.merge(
        primary_assignments,
        on="customer_id",
        how="inner",
        validate="many_to_many",
    )

    # --------------------------------------------------------
    # Experiment period
    # --------------------------------------------------------

    experiment = (
        primary_experiment_definition.iloc[0]
    )

    experiment_start = pd.Timestamp(
        experiment["start_timestamp"]
    )

    experiment_end = pd.Timestamp(
        experiment["end_timestamp"]
    )

    # --------------------------------------------------------
    # Eligible session period:
    #
    # session must overlap experiment period AND
    # begin/continue after assignment timestamp.
    # --------------------------------------------------------

    pool["eligible_start"] = (
        pool[
            "session_start_timestamp"
        ]
        .clip(
            lower=experiment_start
        )
    )

    pool["eligible_start"] = pool[
        [
            "eligible_start",
            "assignment_timestamp",
        ]
    ].max(axis=1)

    pool["eligible_end"] = (
        pool[
            "session_end_timestamp"
        ]
        .clip(
            upper=experiment_end
        )
    )

    pool = pool[
        pool["eligible_start"]
        <= pool["eligible_end"]
    ].copy()

    if pool.empty:
        raise ValueError(
            "No sessions occur during the primary "
            "experiment after customer assignment."
        )

    print(
        "[RECOMMENDATION] Eligible sessions: "
        f"{len(pool):,}"
    )

    return pool


# ============================================================
# GENERATE IMPRESSIONS
# ============================================================

def generate_impressions(
    pool,
    products,
    rng,
):

    impression_counts = rng.integers(
        1,
        4,
        size=len(pool),
    )

    repeated_pool = (
        pool.loc[
            pool.index.repeat(
                impression_counts
            )
        ]
        .reset_index(drop=True)
    )

    if repeated_pool.empty:
        raise ValueError(
            "No recommendation impressions generated."
        )

    product_ids = (
        products["product_id"]
        .dropna()
        .astype(str)
        .unique()
    )

    if len(product_ids) == 0:
        raise ValueError(
            "No valid product IDs found."
        )

    repeated_pool[
        "product_id"
    ] = rng.choice(
        product_ids,
        size=len(repeated_pool),
        replace=True,
    )

    starts = pd.to_datetime(
        repeated_pool[
            "eligible_start"
        ],
        errors="coerce",
    )

    ends = pd.to_datetime(
        repeated_pool[
            "eligible_end"
        ],
        errors="coerce",
    )

    if starts.isna().any() or ends.isna().any():
        raise ValueError(
            "Invalid recommendation eligibility timestamps."
        )

    available_seconds = (
        ends - starts
    ).dt.total_seconds()

    offsets = np.array(
        [
            rng.integers(
                0,
                int(seconds) + 1,
            )
            for seconds in available_seconds
        ],
        dtype=np.int64,
    )

    repeated_pool[
        "event_timestamp"
    ] = (
        starts
        + pd.to_timedelta(
            offsets,
            unit="s",
        )
    )

    repeated_pool[
        "event_type"
    ] = "recommendation_impression"

    return repeated_pool


# ============================================================
# GENERATE CLICKS
# ============================================================

def generate_clicks(
    impressions,
    rng,
):

    if impressions.empty:
        return impressions.copy()

    click_mask = (
        rng.random(
            len(impressions)
        )
        < IMPRESSION_TO_CLICK_PROBABILITY
    )

    clicks = (
        impressions.loc[
            click_mask
        ]
        .copy()
        .reset_index(drop=True)
    )

    clicks[
        "event_type"
    ] = "recommendation_click"

    if not clicks.empty:

        remaining_seconds = (
            pd.to_datetime(
                clicks[
                    "eligible_end"
                ]
            )
            - pd.to_datetime(
                clicks[
                    "event_timestamp"
                ]
            )
        ).dt.total_seconds().clip(
            lower=0
        )

        delays = np.array(
            [
                rng.integers(
                    0,
                    int(seconds) + 1,
                )
                for seconds in remaining_seconds
            ],
            dtype=np.int64,
        )

        clicks[
            "event_timestamp"
        ] = (
            pd.to_datetime(
                clicks[
                    "event_timestamp"
                ]
            )
            + pd.to_timedelta(
                delays,
                unit="s",
            )
        )

    return clicks


# ============================================================
# GENERATE CONVERSIONS
# ============================================================

def generate_conversions(
    clicks,
    rng,
):

    if clicks.empty:
        return clicks.copy()

    conversion_mask = (
        rng.random(
            len(clicks)
        )
        < CLICK_TO_PURCHASE_PROBABILITY
    )

    conversions = (
        clicks.loc[
            conversion_mask
        ]
        .copy()
        .reset_index(drop=True)
    )

    conversions[
        "event_type"
    ] = "recommendation_conversion"

    if not conversions.empty:

        remaining_seconds = (
            pd.to_datetime(
                conversions[
                    "eligible_end"
                ]
            )
            - pd.to_datetime(
                conversions[
                    "event_timestamp"
                ]
            )
        ).dt.total_seconds().clip(
            lower=0
        )

        delays = np.array(
            [
                rng.integers(
                    0,
                    int(seconds) + 1,
                )
                for seconds in remaining_seconds
            ],
            dtype=np.int64,
        )

        conversions[
            "event_timestamp"
        ] = (
            pd.to_datetime(
                conversions[
                    "event_timestamp"
                ]
            )
            + pd.to_timedelta(
                delays,
                unit="s",
            )
        )

    return conversions


# ============================================================
# CONSTRUCT FINAL ENTITY
# ============================================================

def construct_recommendation_events(
    impressions,
    clicks,
    conversions,
):

    recommendations = pd.concat(
        [
            impressions,
            clicks,
            conversions,
        ],
        ignore_index=True,
    )

    if recommendations.empty:
        raise ValueError(
            "No recommendation events generated."
        )

    required_columns = [
        "session_id",
        "anonymous_id",
        "customer_id",
        "experiment_id",
        "variant",
        "product_id",
        "event_type",
        "event_timestamp",
    ]

    recommendations = (
        recommendations[
            required_columns
        ]
        .copy()
    )

    recommendations.insert(
        0,
        "recommendation_event_id",
        [
            f"rec_{i:09d}"
            for i in range(
                1,
                len(recommendations) + 1,
            )
        ],
    )

    return recommendations


# ============================================================
# VALIDATION
# ============================================================

def validate_recommendation_events(
    recommendations,
    sessions,
    experiments,
    assignments,
    products,
):

    required_columns = {
        "recommendation_event_id",
        "session_id",
        "anonymous_id",
        "customer_id",
        "experiment_id",
        "variant",
        "product_id",
        "event_type",
        "event_timestamp",
    }

    missing_columns = (
        required_columns
        - set(recommendations.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing recommendation columns: "
            f"{sorted(missing_columns)}"
        )

    if recommendations.empty:
        raise ValueError(
            "Recommendation dataset is empty."
        )

    if (
        recommendations[
            "recommendation_event_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicate recommendation_event_id values."
        )

    required_non_null = [
        "recommendation_event_id",
        "session_id",
        "anonymous_id",
        "customer_id",
        "experiment_id",
        "variant",
        "product_id",
        "event_type",
        "event_timestamp",
    ]

    for column in required_non_null:

        if recommendations[
            column
        ].isna().any():

            raise ValueError(
                f"Null values detected in {column}."
            )

    if not recommendations[
        "event_type"
    ].isin(EVENT_TYPES).all():
        raise ValueError(
            "Invalid recommendation event type."
        )

    if not recommendations[
        "variant"
    ].isin(VARIANTS).all():
        raise ValueError(
            "Invalid experiment variant."
        )

    valid_sessions = set(
        sessions[
            "session_id"
        ].astype(str)
    )

    if not recommendations[
        "session_id"
    ].astype(str).isin(
        valid_sessions
    ).all():
        raise ValueError(
            "Orphan session_id detected."
        )

    valid_products = set(
        products[
            "product_id"
        ].astype(str)
    )

    if not recommendations[
        "product_id"
    ].astype(str).isin(
        valid_products
    ).all():
        raise ValueError(
            "Orphan product_id detected."
        )

    # --------------------------------------------------------
    # Assignment integrity
    # --------------------------------------------------------

    assignment_keys = set(
        zip(
            assignments[
                "customer_id"
            ].astype(str),
            assignments[
                "experiment_id"
            ].astype(str),
        )
    )

    recommendation_keys = zip(
        recommendations[
            "customer_id"
        ].astype(str),
        recommendations[
            "experiment_id"
        ].astype(str),
    )

    invalid_keys = [
        key
        for key in recommendation_keys
        if key not in assignment_keys
    ]

    if invalid_keys:
        raise ValueError(
            "Recommendation events contain customer/"
            "experiment combinations without assignments."
        )

    # --------------------------------------------------------
    # Experiment-period and assignment-time integrity
    # --------------------------------------------------------

    experiment_bounds = experiments[
        [
            "experiment_id",
            "start_timestamp",
            "end_timestamp",
        ]
    ].copy()

    experiment_bounds[
        "experiment_id"
    ] = (
        experiment_bounds[
            "experiment_id"
        ].astype(str)
    )

    assignment_bounds = assignments[
        [
            "customer_id",
            "experiment_id",
            "assignment_timestamp",
        ]
    ].copy()

    assignment_bounds[
        "customer_id"
    ] = (
        assignment_bounds[
            "customer_id"
        ].astype(str)
    )

    assignment_bounds[
        "experiment_id"
    ] = (
        assignment_bounds[
            "experiment_id"
        ].astype(str)
    )

    check = recommendations.merge(
        experiment_bounds,
        on="experiment_id",
        how="left",
        validate="many_to_one",
    )

    check = check.merge(
        assignment_bounds,
        on=[
            "customer_id",
            "experiment_id",
        ],
        how="left",
        validate="many_to_one",
    )

    check["event_timestamp"] = pd.to_datetime(
        check["event_timestamp"],
        errors="coerce",
    )

    if (
        check["event_timestamp"]
        < check["start_timestamp"]
    ).any():
        raise ValueError(
            "Recommendation event occurs before "
            "experiment start."
        )

    if (
        check["event_timestamp"]
        > check["end_timestamp"]
    ).any():
        raise ValueError(
            "Recommendation event occurs after "
            "experiment end."
        )

    if (
        check["event_timestamp"]
        < check["assignment_timestamp"]
    ).any():
        raise ValueError(
            "Recommendation event occurs before "
            "customer experiment assignment."
        )

    # --------------------------------------------------------
    # Session temporal integrity
    # --------------------------------------------------------

    session_bounds = sessions[
        [
            "session_id",
            "session_start_timestamp",
            "session_end_timestamp",
        ]
    ].copy()

    session_bounds["session_id"] = (
        session_bounds["session_id"].astype(str)
    )

    check = recommendations.merge(
        session_bounds,
        on="session_id",
        how="left",
        validate="many_to_one",
    )

    if (
        check["event_timestamp"]
        < check["session_start_timestamp"]
    ).any():
        raise ValueError(
            "Recommendation event occurs before "
            "session start."
        )

    if (
        check["event_timestamp"]
        > check["session_end_timestamp"]
    ).any():
        raise ValueError(
            "Recommendation event occurs after "
            "session end."
        )

    # --------------------------------------------------------
    # Funnel ordering
    # --------------------------------------------------------

    grouped = recommendations.groupby(
        [
            "session_id",
            "product_id",
            "experiment_id",
            "variant",
        ],
        dropna=False,
    )

    for _, group in grouped:

        impressions = group.loc[
            group["event_type"]
            == "recommendation_impression",
            "event_timestamp",
        ]

        clicks = group.loc[
            group["event_type"]
            == "recommendation_click",
            "event_timestamp",
        ]

        conversions = group.loc[
            group["event_type"]
            == "recommendation_conversion",
            "event_timestamp",
        ]

        if (
            not clicks.empty
            and not impressions.empty
            and clicks.min()
            < impressions.min()
        ):
            raise ValueError(
                "Recommendation click occurs "
                "before impression."
            )

        if (
            not conversions.empty
            and not clicks.empty
            and conversions.min()
            < clicks.min()
        ):
            raise ValueError(
                "Recommendation conversion occurs "
                "before click."
            )

    print(
        "[RECOMMENDATION] Validation passed — "
        f"{len(recommendations):,} events."
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    recommendations,
):

    counts = (
        recommendations[
            "event_type"
        ]
        .value_counts()
    )

    print()
    print("=" * 70)
    print("[RECOMMENDATION] Recommendation summary")
    print("=" * 70)

    for event_type in EVENT_TYPES:

        count = int(
            counts.get(
                event_type,
                0,
            )
        )

        print(
            f"  {event_type:<32} "
            f"= {count:,}"
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

    if impressions > 0:
        print(
            "  Recommendation CTR          = "
            f"{clicks / impressions:.2%}"
        )

    if clicks > 0:
        print(
            "  Click → Conversion          = "
            f"{conversions / clicks:.2%}"
        )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("ORGEE — RECOMMENDATION GENERATOR")
    print("=" * 70)

    RECOMMENDATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        sessions,
        experiments,
        assignments,
        products,
    ) = load_required_files()

    rng = np.random.default_rng(
        PRIMARY_SEED + 9
    )

    pool = build_recommendation_pool(
        sessions,
        experiments,
        assignments,
    )

    impressions = generate_impressions(
        pool,
        products,
        rng,
    )

    print(
        f"[RECOMMENDATION] Generated "
        f"{len(impressions):,} impressions."
    )

    clicks = generate_clicks(
        impressions,
        rng,
    )

    print(
        f"[RECOMMENDATION] Generated "
        f"{len(clicks):,} clicks."
    )

    conversions = generate_conversions(
        clicks,
        rng,
    )

    print(
        f"[RECOMMENDATION] Generated "
        f"{len(conversions):,} conversions."
    )

    recommendations = (
        construct_recommendation_events(
            impressions,
            clicks,
            conversions,
        )
    )

    validate_recommendation_events(
        recommendations,
        sessions,
        experiments,
        assignments,
        products,
    )

    print_summary(
        recommendations
    )

    recommendations.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        f"[RECOMMENDATION] Generated "
        f"{len(recommendations):,} recommendation events."
    )

    print(
        "[RECOMMENDATION] Output written to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)
    print("[RECOMMENDATION] COMPLETE")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()