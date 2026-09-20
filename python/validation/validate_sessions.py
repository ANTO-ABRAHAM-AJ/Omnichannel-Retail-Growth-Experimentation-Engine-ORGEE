"""
ORGEE — SESSION VALIDATION

Validates:
    - Schema
    - Row count
    - Primary-key uniqueness
    - Anonymous-ID uniqueness
    - Required fields
    - Referential integrity with public customers
    - Allowed categorical values
    - Temporal integrity
    - Session duration
    - Expected event count
    - Distribution sanity
    - Identifier format

Source:
    ORGEE Phase 2 — Enterprise Generation Configuration
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SESSION_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "sessions"
    / "sessions.csv"
)

CUSTOMERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_customers_dataset.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_SESSION_COUNT = 500_000

ALLOWED_DEVICES = {
    "mobile",
    "desktop",
    "tablet",
}

ALLOWED_PLATFORMS = {
    "web",
    "mobile_app",
    "desktop",
}

ALLOWED_SESSION_TYPES = {
    "short",
    "medium",
    "long",
}

ALLOWED_ACTIVITY_SEGMENTS = {
    "highly_active",
    "active",
    "moderate",
    "low_activity",
}


# ============================================================
# EXPECTED SCHEMA
# ============================================================

EXPECTED_COLUMNS = [
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
]


# ============================================================
# UTILITY
# ============================================================

def fail(message: str) -> None:
    raise ValueError(
        f"[SESSION VALIDATION FAILED] {message}"
    )


def pass_message(message: str) -> None:
    print(
        f"[SESSION VALIDATION PASSED] {message}"
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_sessions() -> pd.DataFrame:

    print(
        "[SESSION VALIDATION] Loading sessions..."
    )

    if not SESSION_FILE.exists():
        fail(
            f"Session file not found:\n"
            f"{SESSION_FILE}"
        )

    sessions = pd.read_csv(
        SESSION_FILE
    )

    if sessions.empty:
        fail(
            "sessions.csv is empty."
        )

    print(
        f"[SESSION VALIDATION] Loaded "
        f"{len(sessions):,} sessions."
    )

    return sessions


def load_customers() -> pd.DataFrame:

    print(
        "[SESSION VALIDATION] "
        "Loading public customers..."
    )

    if not CUSTOMERS_FILE.exists():
        fail(
            f"Customer reference file not found:\n"
            f"{CUSTOMERS_FILE}"
        )

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        usecols=["customer_id"],
    )

    if customers.empty:
        fail(
            "Public customer reference dataset "
            "is empty."
        )

    customers["customer_id"] = (
        customers["customer_id"]
        .astype(str)
        .str.strip()
    )

    print(
        f"[SESSION VALIDATION] Loaded "
        f"{len(customers):,} public customers."
    )

    return customers


# ============================================================
# SCHEMA VALIDATION
# ============================================================

def validate_schema(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] Checking schema..."
    )

    actual_columns = list(
        sessions.columns
    )

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    if missing_columns:
        fail(
            "Missing required columns: "
            f"{missing_columns}"
        )

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    if unexpected_columns:
        print(
            "[SESSION VALIDATION] Warning — "
            f"unexpected columns detected: "
            f"{unexpected_columns}"
        )

    pass_message(
        "Schema validation passed."
    )


# ============================================================
# ROW COUNT
# ============================================================

def validate_row_count(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] Checking row count..."
    )

    actual_count = len(sessions)

    if actual_count != EXPECTED_SESSION_COUNT:
        fail(
            f"Expected "
            f"{EXPECTED_SESSION_COUNT:,} sessions, "
            f"found {actual_count:,}."
        )

    pass_message(
        f"Row count = {actual_count:,}."
    )


# ============================================================
# PRIMARY KEY VALIDATION
# ============================================================

def validate_session_id(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] Checking session_id..."
    )

    if sessions["session_id"].isna().any():
        fail(
            "Null session_id values detected."
        )

    sessions["session_id"] = (
        sessions["session_id"]
        .astype(str)
        .str.strip()
    )

    if (
        sessions["session_id"]
        .eq("")
        .any()
    ):
        fail(
            "Blank session_id values detected."
        )

    duplicate_count = (
        sessions["session_id"]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        fail(
            f"{duplicate_count:,} duplicate "
            f"session_id values detected."
        )

    pass_message(
        "session_id uniqueness passed."
    )


# ============================================================
# ANONYMOUS ID VALIDATION
# ============================================================

def validate_anonymous_id(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking anonymous_id..."
    )

    if sessions["anonymous_id"].isna().any():
        fail(
            "Null anonymous_id values detected."
        )

    sessions["anonymous_id"] = (
        sessions["anonymous_id"]
        .astype(str)
        .str.strip()
    )

    if (
        sessions["anonymous_id"]
        .eq("")
        .any()
    ):
        fail(
            "Blank anonymous_id values detected."
        )

    duplicate_count = (
        sessions["anonymous_id"]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        fail(
            f"{duplicate_count:,} duplicate "
            f"anonymous_id values detected."
        )

    invalid_format = (
        ~sessions["anonymous_id"]
        .str.startswith("anon_")
    )

    if invalid_format.any():
        fail(
            f"{invalid_format.sum():,} anonymous_id "
            f"values have invalid format."
        )

    pass_message(
        "anonymous_id validation passed."
    )


# ============================================================
# CUSTOMER REFERENTIAL INTEGRITY
# ============================================================

def validate_customer_reference(
    sessions: pd.DataFrame,
    customers: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] Checking "
        "customer referential integrity..."
    )

    if sessions["customer_id"].isna().any():
        fail(
            "Null customer_id values detected."
        )

    sessions["customer_id"] = (
        sessions["customer_id"]
        .astype(str)
        .str.strip()
    )

    if (
        sessions["customer_id"]
        .eq("")
        .any()
    ):
        fail(
            "Blank customer_id values detected."
        )

    valid_customer_ids = set(
        customers["customer_id"]
    )

    session_customer_ids = set(
        sessions["customer_id"]
    )

    orphan_customer_ids = (
        session_customer_ids
        - valid_customer_ids
    )

    if orphan_customer_ids:
        fail(
            f"{len(orphan_customer_ids):,} "
            f"customer_id values do not exist "
            f"in the public customer reference."
        )

    pass_message(
        "Customer referential integrity passed."
    )


# ============================================================
# CATEGORICAL VALIDATION
# ============================================================

def validate_categories(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] Checking "
        "categorical values..."
    )

    for column in [
        "device_type",
        "platform",
        "session_type",
        "activity_segment",
    ]:

        if sessions[column].isna().any():
            fail(
                f"Null values detected in "
                f"{column}."
            )

        sessions[column] = (
            sessions[column]
            .astype(str)
            .str.strip()
        )

    invalid_devices = (
        set(sessions["device_type"])
        - ALLOWED_DEVICES
    )

    if invalid_devices:
        fail(
            f"Invalid device_type values: "
            f"{sorted(invalid_devices)}"
        )

    invalid_platforms = (
        set(sessions["platform"])
        - ALLOWED_PLATFORMS
    )

    if invalid_platforms:
        fail(
            f"Invalid platform values: "
            f"{sorted(invalid_platforms)}"
        )

    invalid_session_types = (
        set(sessions["session_type"])
        - ALLOWED_SESSION_TYPES
    )

    if invalid_session_types:
        fail(
            f"Invalid session_type values: "
            f"{sorted(invalid_session_types)}"
        )

    invalid_segments = (
        set(sessions["activity_segment"])
        - ALLOWED_ACTIVITY_SEGMENTS
    )

    if invalid_segments:
        fail(
            f"Invalid activity_segment values: "
            f"{sorted(invalid_segments)}"
        )

    pass_message(
        "Categorical value validation passed."
    )


# ============================================================
# REQUIRED FIELD VALIDATION
# ============================================================

def validate_required_fields(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking required fields..."
    )

    required_fields = [
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
    ]

    for column in required_fields:

        null_count = (
            sessions[column]
            .isna()
            .sum()
        )

        if null_count > 0:
            fail(
                f"{null_count:,} null values "
                f"detected in {column}."
            )

    pass_message(
        "Required-field completeness passed."
    )


# ============================================================
# TIMESTAMP VALIDATION
# ============================================================

def validate_timestamps(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking timestamps..."
    )

    sessions["session_start_timestamp"] = (
        pd.to_datetime(
            sessions[
                "session_start_timestamp"
            ],
            errors="coerce",
        )
    )

    sessions["session_end_timestamp"] = (
        pd.to_datetime(
            sessions[
                "session_end_timestamp"
            ],
            errors="coerce",
        )
    )

    invalid_start = (
        sessions[
            "session_start_timestamp"
        ]
        .isna()
        .sum()
    )

    invalid_end = (
        sessions[
            "session_end_timestamp"
        ]
        .isna()
        .sum()
    )

    if invalid_start > 0:
        fail(
            f"{invalid_start:,} invalid "
            f"session_start_timestamp values."
        )

    if invalid_end > 0:
        fail(
            f"{invalid_end:,} invalid "
            f"session_end_timestamp values."
        )

    invalid_order = (
        sessions[
            "session_end_timestamp"
        ]
        <
        sessions[
            "session_start_timestamp"
        ]
    )

    if invalid_order.any():
        fail(
            f"{invalid_order.sum():,} sessions have "
            f"end timestamps before start timestamps."
        )

    equal_timestamps = (
        sessions[
            "session_end_timestamp"
        ]
        ==
        sessions[
            "session_start_timestamp"
        ]
    )

    if equal_timestamps.any():
        fail(
            f"{equal_timestamps.sum():,} sessions have "
            "zero duration."
        )

    pass_message(
        "Timestamp ordering passed."
    )


# ============================================================
# SESSION DURATION VALIDATION
# ============================================================

def validate_session_duration(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking session durations..."
    )

    duration_minutes = (
        (
            sessions[
                "session_end_timestamp"
            ]
            -
            sessions[
                "session_start_timestamp"
            ]
        )
        .dt.total_seconds()
        / 60
    )

    upper_limits = {
        "short": 10,
        "medium": 30,
        "long": 90,
    }

    lower_limits = {
        "short": 1,
        "medium": 10,
        "long": 30,
    }

    for session_type in ALLOWED_SESSION_TYPES:

        mask = (
            sessions["session_type"]
            == session_type
        )

        type_durations = (
            duration_minutes[mask]
        )

        if type_durations.empty:
            fail(
                f"No sessions found for "
                f"session_type={session_type}."
            )

        upper_violation = (
            type_durations
            > upper_limits[session_type]
        )

        if upper_violation.any():
            fail(
                f"{upper_violation.sum():,} "
                f"{session_type} sessions exceed "
                f"the configured maximum duration."
            )

        lower_violation = (
            type_durations
            < lower_limits[session_type]
        )

        if lower_violation.any():
            print(
                f"[SESSION VALIDATION] Warning — "
                f"{lower_violation.sum():,} "
                f"{session_type} sessions are below "
                f"the configured minimum duration."
            )

    pass_message(
        "Session duration validation passed."
    )


# ============================================================
# EVENT COUNT VALIDATION
# ============================================================

def validate_event_counts(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking expected event counts..."
    )

    sessions["expected_event_count"] = pd.to_numeric(
        sessions["expected_event_count"],
        errors="coerce",
    )

    if sessions[
        "expected_event_count"
    ].isna().any():
        fail(
            "Invalid expected_event_count values."
        )

    if (
        sessions["expected_event_count"]
        <= 0
    ).any():
        fail(
            "Non-positive expected_event_count "
            "values detected."
        )

    maximums = {
        "short": 5,
        "medium": 10,
        "long": 20,
    }

    for session_type, maximum in maximums.items():

        mask = (
            sessions["session_type"]
            == session_type
        )

        violations = (
            sessions.loc[
                mask,
                "expected_event_count",
            ]
            > maximum
        )

        if violations.any():
            fail(
                f"{violations.sum():,} "
                f"{session_type} sessions exceed "
                f"the configured event-count maximum."
            )

    pass_message(
        "Expected event-count validation passed."
    )


# ============================================================
# DISTRIBUTION VALIDATION
# ============================================================

def validate_distributions(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking distribution sanity..."
    )

    session_type_share = (
        sessions["session_type"]
        .value_counts(normalize=True)
    )

    print(
        "[SESSION VALIDATION] "
        "Session type distribution:"
    )

    for value in [
        "short",
        "medium",
        "long",
    ]:

        share = session_type_share.get(
            value,
            0,
        )

        print(
            f"    {value:<10} = "
            f"{share:.2%}"
        )

    device_share = (
        sessions["device_type"]
        .value_counts(normalize=True)
    )

    print(
        "[SESSION VALIDATION] "
        "Device distribution:"
    )

    for value in [
        "mobile",
        "desktop",
        "tablet",
    ]:

        share = device_share.get(
            value,
            0,
        )

        print(
            f"    {value:<10} = "
            f"{share:.2%}"
        )

    platform_share = (
        sessions["platform"]
        .value_counts(normalize=True)
    )

    print(
        "[SESSION VALIDATION] "
        "Platform distribution:"
    )

    for value in [
        "web",
        "mobile_app",
        "desktop",
    ]:

        share = platform_share.get(
            value,
            0,
        )

        print(
            f"    {value:<12} = "
            f"{share:.2%}"
        )

    for distribution, name, values in [
        (
            session_type_share,
            "session types",
            [
                "short",
                "medium",
                "long",
            ],
        ),
        (
            device_share,
            "device types",
            [
                "mobile",
                "desktop",
                "tablet",
            ],
        ),
        (
            platform_share,
            "platforms",
            [
                "web",
                "mobile_app",
                "desktop",
            ],
        ),
    ]:

        missing = [
            value
            for value in values
            if distribution.get(value, 0) == 0
        ]

        if missing:
            fail(
                f"One or more {name} have "
                f"zero observations: {missing}"
            )

    pass_message(
        "Distribution sanity validation passed."
    )


# ============================================================
# IDENTIFIER FORMAT VALIDATION
# ============================================================

def validate_identifier_formats(
    sessions: pd.DataFrame,
) -> None:

    print(
        "[SESSION VALIDATION] "
        "Checking identifier formats..."
    )

    invalid_session_ids = (
        ~sessions["session_id"]
        .astype(str)
        .str.match(
            r"^sess_\d{9}$"
        )
    )

    if invalid_session_ids.any():
        fail(
            f"{invalid_session_ids.sum():,} "
            f"session_id values have invalid format."
        )

    pass_message(
        "Identifier format validation passed."
    )


# ============================================================
# MAIN VALIDATION
# ============================================================

def main() -> None:

    print()
    print("=" * 70)
    print("ORGEE — SESSION VALIDATION")
    print("=" * 70)

    try:

        sessions = load_sessions()

        customers = load_customers()

        print()

        validate_schema(
            sessions
        )

        validate_required_fields(
            sessions
        )

        validate_row_count(
            sessions
        )

        validate_session_id(
            sessions
        )

        validate_anonymous_id(
            sessions
        )

        validate_identifier_formats(
            sessions
        )

        validate_customer_reference(
            sessions,
            customers,
        )

        validate_categories(
            sessions
        )

        validate_timestamps(
            sessions
        )

        validate_session_duration(
            sessions
        )

        validate_event_counts(
            sessions
        )

        validate_distributions(
            sessions
        )

        print()
        print("=" * 70)
        print(
            "[SESSION VALIDATION] COMPLETE — "
            "ALL CHECKS PASSED"
        )
        print("=" * 70)
        print()

    except Exception as exc:

        print()
        print("=" * 70)
        print(
            "[SESSION VALIDATION] FAILED"
        )
        print("=" * 70)
        print(str(exc))
        print()

        sys.exit(1)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()