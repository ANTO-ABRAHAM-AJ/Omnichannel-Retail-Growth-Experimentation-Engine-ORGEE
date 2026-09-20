"""
ORGEE — Session Generator

Generates synthetic customer/anonymous browsing sessions
using the public Olist customer population.

Source:
    Document 7 — Enterprise Generation Configuration
"""

from pathlib import Path
import importlib

import numpy as np
import pandas as pd


# ============================================================
# GENERATOR CONFIGURATION
# ============================================================

config = importlib.import_module("01_generator_config")

PRIMARY_SEED = config.PRIMARY_SEED
TARGET_VOLUMES = config.TARGET_VOLUMES
CUSTOMER_ACTIVITY_SEGMENTS = config.CUSTOMER_ACTIVITY_SEGMENTS
SESSION_TYPE_DISTRIBUTION = config.SESSION_TYPE_DISTRIBUTION
DEVICE_DISTRIBUTION = config.DEVICE_DISTRIBUTION
PLATFORM_DISTRIBUTION = config.PLATFORM_DISTRIBUTION


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed" / "public"
)

SESSION_OUTPUT_DIR = (
    PROJECT_ROOT / "data" / "enterprise" / "sessions"
)

CUSTOMERS_FILE = (
    PUBLIC_DATA_DIR / "olist_customers_dataset.csv"
)

ORDERS_FILE = (
    PUBLIC_DATA_DIR / "olist_orders_dataset.csv"
)

OUTPUT_FILE = (
    SESSION_OUTPUT_DIR / "sessions.csv"
)

# Internal-only file: the "true" identity behind each session,
# used by downstream generators (events) to decide what customer_id
# to reveal once a login event occurs within that session. This file
# is NOT a Phase 2 deliverable and must not be loaded into the
# warehouse — it exists purely to keep generation internally
# consistent (fix: see 05_generate_events.py and the sessions
# backfill step).
SESSION_TRUTH_FILE = (
    SESSION_OUTPUT_DIR / "_internal_session_customer_truth.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_SESSIONS = TARGET_VOLUMES["sessions"]

SESSION_TYPES = (
    "short",
    "medium",
    "long",
)

DEVICE_TYPES = (
    "mobile",
    "desktop",
    "tablet",
)

PLATFORM_TYPES = (
    "web",
    "mobile_app",
    "desktop",
)


# ============================================================
# CUSTOMER ACTIVITY WEIGHTS
# ============================================================

ACTIVITY_MULTIPLIERS = {
    "highly_active": 3.0,
    "active": 2.0,
    "moderate": 1.0,
    "low_activity": 0.5,
}


# ============================================================
# SESSION DURATION RANGES
# ============================================================

SESSION_DURATION_RANGES = {
    "short": (1, 10),
    "medium": (10, 30),
    "long": (30, 90),
}


# ============================================================
# EVENT INTENSITY RANGES
# ============================================================

SESSION_EVENT_COUNT_RANGES = {
    "short": (2, 5),
    "medium": (5, 10),
    "long": (10, 20),
}


# ============================================================
# CUSTOMER ACTIVITY ASSIGNMENT
# ============================================================

def assign_customer_activity_segments(
    customer_ids: pd.Series,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Assign each public customer to a synthetic activity segment.

    These segments are generation controls only and are not
    analytical findings about Olist customers.
    """

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids.astype(str).to_numpy()
        }
    )

    segment_names = list(
        CUSTOMER_ACTIVITY_SEGMENTS.keys()
    )

    segment_probabilities = list(
        CUSTOMER_ACTIVITY_SEGMENTS.values()
    )

    customers["activity_segment"] = rng.choice(
        segment_names,
        size=len(customers),
        p=segment_probabilities,
    )

    customers["activity_multiplier"] = (
        customers["activity_segment"]
        .map(ACTIVITY_MULTIPLIERS)
    )

    return customers


# ============================================================
# CUSTOMER SESSION WEIGHTS
# ============================================================

def calculate_session_weights(
    customers: pd.DataFrame,
) -> np.ndarray:
    """
    Calculate normalized customer session-selection weights.
    """

    weights = customers[
        "activity_multiplier"
    ].to_numpy(dtype=float)

    if np.any(weights <= 0):
        raise ValueError(
            "Customer activity weights must be positive."
        )

    total_weight = weights.sum()

    if total_weight <= 0:
        raise ValueError(
            "Customer activity weights sum to zero."
        )

    weights = weights / total_weight

    return weights


# ============================================================
# ANONYMOUS ID GENERATION
# ============================================================

def generate_anonymous_ids(
    count: int,
) -> list[str]:
    """
    Generate unique anonymous identifiers.
    """

    return [
        f"anon_{i:09d}"
        for i in range(1, count + 1)
    ]


# ============================================================
# SESSION GENERATION
# ============================================================

def generate_sessions(
    customers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Generate the configured number of synthetic sessions.
    """

    weights = calculate_session_weights(customers)

    selected_customer_indices = rng.choice(
        len(customers),
        size=TARGET_SESSIONS,
        replace=True,
        p=weights,
    )

    selected_customers = customers.iloc[
        selected_customer_indices
    ].reset_index(drop=True)

    # --------------------------------------------------------
    # Session type
    # --------------------------------------------------------

    session_types = rng.choice(
        SESSION_TYPES,
        size=TARGET_SESSIONS,
        p=[
            SESSION_TYPE_DISTRIBUTION["short"],
            SESSION_TYPE_DISTRIBUTION["medium"],
            SESSION_TYPE_DISTRIBUTION["long"],
        ],
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    devices = rng.choice(
        DEVICE_TYPES,
        size=TARGET_SESSIONS,
        p=[
            DEVICE_DISTRIBUTION["mobile"],
            DEVICE_DISTRIBUTION["desktop"],
            DEVICE_DISTRIBUTION["tablet"],
        ],
    )

    # --------------------------------------------------------
    # Platform
    # --------------------------------------------------------

    platforms = rng.choice(
        PLATFORM_TYPES,
        size=TARGET_SESSIONS,
        p=[
            PLATFORM_DISTRIBUTION["web"],
            PLATFORM_DISTRIBUTION["mobile_app"],
            PLATFORM_DISTRIBUTION["desktop"],
        ],
    )

    # --------------------------------------------------------
    # Anonymous identity
    # --------------------------------------------------------

    anonymous_ids = generate_anonymous_ids(
        TARGET_SESSIONS
    )

    # --------------------------------------------------------
    # Session duration
    # --------------------------------------------------------

    durations = np.array(
        [
            rng.integers(
                SESSION_DURATION_RANGES[
                    session_type
                ][0],
                SESSION_DURATION_RANGES[
                    session_type
                ][1] + 1,
            )
            for session_type in session_types
        ]
    )

    # --------------------------------------------------------
    # Expected event intensity
    # --------------------------------------------------------

    event_counts = np.array(
        [
            rng.integers(
                SESSION_EVENT_COUNT_RANGES[
                    session_type
                ][0],
                SESSION_EVENT_COUNT_RANGES[
                    session_type
                ][1] + 1,
            )
            for session_type in session_types
        ]
    )

    # --------------------------------------------------------
    # Session timestamps
    #
    # Behavioral period is derived from the processed
    # public Olist orders observation period.
    # --------------------------------------------------------

    if not ORDERS_FILE.exists():
        raise FileNotFoundError(
            f"Orders dataset not found: {ORDERS_FILE}"
        )

    orders = pd.read_csv(
        ORDERS_FILE,
        usecols=[
            "order_purchase_timestamp"
        ],
    )

    orders["order_purchase_timestamp"] = (
        pd.to_datetime(
            orders["order_purchase_timestamp"],
            errors="coerce",
        )
    )

    orders = orders.dropna(
        subset=["order_purchase_timestamp"]
    )

    if orders.empty:
        raise ValueError(
            "No valid order purchase timestamps found."
        )

    period_start = orders[
        "order_purchase_timestamp"
    ].min()

    period_end = orders[
        "order_purchase_timestamp"
    ].max()

    if pd.isna(period_start) or pd.isna(period_end):
        raise ValueError(
            "Unable to determine public order observation period."
        )

    if period_start >= period_end:
        raise ValueError(
            "Invalid public order observation period."
        )

    total_seconds = int(
        (
            period_end - period_start
        ).total_seconds()
    )

    random_offsets = rng.integers(
        0,
        total_seconds + 1,
        size=TARGET_SESSIONS,
    )

    session_start = (
        period_start
        + pd.to_timedelta(
            random_offsets,
            unit="s",
        )
    )

    session_end = (
        session_start
        + pd.to_timedelta(
            durations,
            unit="m",
        )
    )

    # --------------------------------------------------------
    # Keep session end inside behavioral period.
    #
    # session_end is converted to a Series because the
    # generated timestamps may be represented as DatetimeIndex.
    # --------------------------------------------------------

    session_end = (
        pd.Series(session_end)
        .clip(upper=period_end)
        .to_numpy()
    )

    # --------------------------------------------------------
    # Construct session entity
    # --------------------------------------------------------

    session_ids = [
        f"sess_{i:09d}"
        for i in range(
            1,
            TARGET_SESSIONS + 1,
        )
    ]

    # --------------------------------------------------------
    # FIX: customer_id must NOT be exposed on every session.
    #
    # A session starts anonymous. It only becomes identified once
    # a successful login event occurs within it (see
    # 04_enterprise_data_requirements.md section 7/9 and the
    # identity-link design). The "true" customer behind each
    # anonymous_id is kept in an internal-only truth file so
    # 05_generate_events.py can consistently reveal it after a
    # login event fires. The PUBLIC sessions.csv leaves
    # customer_id null here; it gets selectively backfilled later
    # (see 06_backfill_session_identity.py) only for sessions that
    # actually produced a successful login / identity link.
    # --------------------------------------------------------

    sessions = pd.DataFrame(
        {
            "session_id": session_ids,
            "anonymous_id": anonymous_ids,
            "customer_id": pd.array(
                [pd.NA] * TARGET_SESSIONS,
                dtype="string",
            ),
            "device_type": devices,
            "platform": platforms,
            "session_type": session_types,
            "session_start_timestamp": session_start,
            "session_end_timestamp": session_end,
            "expected_event_count": event_counts,
            "activity_segment": selected_customers[
                "activity_segment"
            ].to_numpy(),
        }
    )

    session_truth = pd.DataFrame(
        {
            "session_id": session_ids,
            "anonymous_id": anonymous_ids,
            "true_customer_id": selected_customers[
                "customer_id"
            ].to_numpy(),
        }
    )

    return sessions, session_truth


# ============================================================
# VALIDATION
# ============================================================

def validate_sessions(
    sessions: pd.DataFrame,
) -> None:
    """
    Validate the generated session entity.
    """

    required_columns = {
        "session_id",
        "anonymous_id",
        "customer_id",
        "device_type",
        "platform",
        "session_type",
        "session_start_timestamp",
        "session_end_timestamp",
        "expected_event_count",
        "activity_segment",
    }

    missing_columns = (
        required_columns
        - set(sessions.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing session columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Target volume
    # --------------------------------------------------------

    if len(sessions) != TARGET_SESSIONS:
        raise ValueError(
            f"Expected {TARGET_SESSIONS:,} sessions, "
            f"generated {len(sessions):,}."
        )

    # --------------------------------------------------------
    # Primary-key uniqueness
    # --------------------------------------------------------

    if sessions["session_id"].duplicated().any():
        raise ValueError(
            "Duplicate session_id values detected."
        )

    # --------------------------------------------------------
    # Anonymous-ID uniqueness
    # --------------------------------------------------------

    if sessions["anonymous_id"].duplicated().any():
        raise ValueError(
            "Duplicate anonymous_id values detected."
        )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    for column in [
        "session_id",
        "anonymous_id",
        "device_type",
        "platform",
        "session_type",
    ]:
        if sessions[column].isna().any():
            raise ValueError(
                f"Null values detected in {column}."
            )

    # FIX: customer_id is EXPECTED to be null at generation time —
    # a session is anonymous until a login event identifies it.
    # It gets selectively backfilled later. Do not require it here.

    # --------------------------------------------------------
    # Temporal integrity
    # --------------------------------------------------------

    if (
        sessions["session_end_timestamp"]
        < sessions["session_start_timestamp"]
    ).any():
        raise ValueError(
            "Session end occurs before session start."
        )

    # --------------------------------------------------------
    # Allowed device values
    # --------------------------------------------------------

    if not sessions["device_type"].isin(
        DEVICE_TYPES
    ).all():
        raise ValueError(
            "Invalid device_type detected."
        )

    # --------------------------------------------------------
    # Allowed platform values
    # --------------------------------------------------------

    if not sessions["platform"].isin(
        PLATFORM_TYPES
    ).all():
        raise ValueError(
            "Invalid platform detected."
        )

    # --------------------------------------------------------
    # Allowed session types
    # --------------------------------------------------------

    if not sessions["session_type"].isin(
        SESSION_TYPES
    ).all():
        raise ValueError(
            "Invalid session_type detected."
        )

    # --------------------------------------------------------
    # Event counts
    # --------------------------------------------------------

    if (
        sessions["expected_event_count"] <= 0
    ).any():
        raise ValueError(
            "Invalid expected event count detected."
        )

    # --------------------------------------------------------
    # Activity segments
    # --------------------------------------------------------

    if not sessions["activity_segment"].isin(
        CUSTOMER_ACTIVITY_SEGMENTS.keys()
    ).all():
        raise ValueError(
            "Invalid activity_segment detected."
        )

    print(
        f"[SESSION] Validation passed — "
        f"{len(sessions):,} sessions."
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    SESSION_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Validate customer reference file
    # --------------------------------------------------------

    if not CUSTOMERS_FILE.exists():
        raise FileNotFoundError(
            f"Customer dataset not found: "
            f"{CUSTOMERS_FILE}"
        )

    # --------------------------------------------------------
    # Load public customers
    # --------------------------------------------------------

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        usecols=["customer_id"],
    )

    if customers.empty:
        raise ValueError(
            "Customer reference dataset is empty."
        )

    # --------------------------------------------------------
    # Reproducible random generator
    # --------------------------------------------------------

    rng = np.random.default_rng(
        PRIMARY_SEED
    )

    # --------------------------------------------------------
    # Assign synthetic customer activity segments
    # --------------------------------------------------------

    customers = assign_customer_activity_segments(
        customers["customer_id"],
        rng,
    )

    # --------------------------------------------------------
    # Generate sessions
    # --------------------------------------------------------

    sessions, session_truth = generate_sessions(
        customers,
        rng,
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_sessions(
        sessions
    )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    sessions.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    session_truth.to_csv(
        SESSION_TRUTH_FILE,
        index=False,
    )

    print(
        f"[SESSION] Generated "
        f"{len(sessions):,} sessions."
    )

    print(
        f"[SESSION] Output written to:\n"
        f"{OUTPUT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()