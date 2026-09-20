"""
ORGEE — IDENTITY LINK VALIDATION

Validates:
    - Schema
    - Required fields
    - Row count
    - identity_link_id uniqueness
    - Anonymous-ID format
    - Customer referential integrity
    - Session referential integrity
    - Session ↔ anonymous consistency
    - Session ↔ customer consistency
    - Timestamp validity
    - Identity-link timestamp within session period
    - Duplicate identity mappings
"""

from pathlib import Path

import pandas as pd


# ============================================================
# ORGEE — IDENTITY LINK VALIDATION
# ============================================================

print("=" * 70)
print("ORGEE — IDENTITY LINK VALIDATION")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

IDENTITY_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "identity"
    / "identity_links.csv"
)

CUSTOMERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "public"
    / "olist_customers_dataset.csv"
)

SESSIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "sessions"
    / "sessions.csv"
)


# ============================================================
# HELPERS
# ============================================================

def fail(message: str) -> None:
    raise ValueError(
        f"[IDENTITY VALIDATION FAILED] {message}"
    )


def pass_message(message: str) -> None:
    print(
        f"[IDENTITY VALIDATION PASSED] {message}"
    )


# ============================================================
# LOAD IDENTITY LINKS
# ============================================================

def load_identity() -> pd.DataFrame:

    print(
        "[IDENTITY VALIDATION] "
        "Loading identity links..."
    )

    if not IDENTITY_FILE.exists():
        fail(
            f"Identity links file not found:\n"
            f"{IDENTITY_FILE}"
        )

    identity = pd.read_csv(
        IDENTITY_FILE
    )

    if identity.empty:
        fail(
            "Identity links dataset is empty."
        )

    print(
        f"[IDENTITY VALIDATION] Loaded "
        f"{len(identity):,} identity links."
    )

    return identity


# ============================================================
# SCHEMA
# ============================================================

def validate_schema(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking schema..."
    )

    required_columns = {
        "identity_link_id",
        "anonymous_id",
        "customer_id",
        "session_id",
        "link_timestamp",
    }

    missing_columns = (
        required_columns
        - set(identity.columns)
    )

    if missing_columns:
        fail(
            f"Missing columns: "
            f"{sorted(missing_columns)}"
        )

    pass_message(
        "Schema validation passed."
    )


# ============================================================
# REQUIRED FIELDS
# ============================================================

def validate_required_fields(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking required fields..."
    )

    required_columns = [
        "identity_link_id",
        "anonymous_id",
        "customer_id",
        "session_id",
        "link_timestamp",
    ]

    for column in required_columns:

        null_count = int(
            identity[column]
            .isna()
            .sum()
        )

        if null_count > 0:
            fail(
                f"{null_count:,} null values "
                f"found in {column}."
            )

    pass_message(
        "Required-field completeness passed."
    )


# ============================================================
# ID NORMALIZATION
# ============================================================

def normalize_ids(
    identity: pd.DataFrame,
) -> None:

    for column in [
        "identity_link_id",
        "anonymous_id",
        "customer_id",
        "session_id",
    ]:

        identity[column] = (
            identity[column]
            .astype(str)
            .str.strip()
        )

        if (
            identity[column]
            .eq("")
            .any()
        ):
            fail(
                f"Blank values detected in "
                f"{column}."
            )


# ============================================================
# IDENTITY LINK ID
# ============================================================

def validate_identity_link_id(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking identity_link_id..."
    )

    duplicate_count = int(
        identity[
            "identity_link_id"
        ]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        fail(
            f"{duplicate_count:,} duplicate "
            "identity_link_id values detected."
        )

    pass_message(
        "identity_link_id uniqueness passed."
    )


# ============================================================
# ANONYMOUS ID FORMAT
# ============================================================

def validate_anonymous_ids(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking anonymous IDs..."
    )

    invalid_anonymous = (
        ~identity[
            "anonymous_id"
        ]
        .str.startswith("anon_")
    )

    if invalid_anonymous.any():

        fail(
            f"{invalid_anonymous.sum():,} "
            "invalid anonymous_id values detected."
        )

    pass_message(
        "Anonymous-ID format validation passed."
    )


# ============================================================
# LOAD CUSTOMERS
# ============================================================

def load_customers() -> set[str]:

    print(
        "[IDENTITY VALIDATION] "
        "Loading public customers..."
    )

    if not CUSTOMERS_FILE.exists():
        fail(
            f"Customer file not found:\n"
            f"{CUSTOMERS_FILE}"
        )

    customers = pd.read_csv(
        CUSTOMERS_FILE,
        usecols=["customer_id"],
    )

    if customers.empty:
        fail(
            "Public customer reference is empty."
        )

    customer_ids = (
        customers["customer_id"]
        .astype(str)
        .str.strip()
    )

    valid_customers = set(
        customer_ids
    )

    print(
        f"[IDENTITY VALIDATION] Loaded "
        f"{len(valid_customers):,} "
        "public customers."
    )

    return valid_customers


# ============================================================
# CUSTOMER REFERENTIAL INTEGRITY
# ============================================================

def validate_customer_reference(
    identity: pd.DataFrame,
    valid_customers: set[str],
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking customer referential integrity..."
    )

    identity_customers = set(
        identity["customer_id"]
    )

    invalid_customers = (
        identity_customers
        -
        valid_customers
    )

    if invalid_customers:
        fail(
            f"Found {len(invalid_customers):,} "
            "customer IDs not present in "
            "public customers."
        )

    pass_message(
        "Customer referential integrity passed."
    )


# ============================================================
# LOAD SESSIONS
# ============================================================

def load_sessions() -> pd.DataFrame:

    print(
        "[IDENTITY VALIDATION] "
        "Loading enterprise sessions..."
    )

    if not SESSIONS_FILE.exists():
        fail(
            f"Sessions file not found:\n"
            f"{SESSIONS_FILE}"
        )

    sessions = pd.read_csv(
        SESSIONS_FILE,
        usecols=[
            "session_id",
            "anonymous_id",
            "customer_id",
            "session_start_timestamp",
            "session_end_timestamp",
        ],
    )

    if sessions.empty:
        fail(
            "Enterprise sessions dataset is empty."
        )

    for column in [
        "session_id",
        "anonymous_id",
        "customer_id",
    ]:

        sessions[column] = (
            sessions[column]
            .astype(str)
            .str.strip()
        )

    sessions[
        "session_start_timestamp"
    ] = pd.to_datetime(
        sessions[
            "session_start_timestamp"
        ],
        errors="coerce",
    )

    sessions[
        "session_end_timestamp"
    ] = pd.to_datetime(
        sessions[
            "session_end_timestamp"
        ],
        errors="coerce",
    )

    if (
        sessions[
            "session_start_timestamp"
        ].isna()
        .any()
    ):
        fail(
            "Invalid session_start_timestamp "
            "values detected."
        )

    if (
        sessions[
            "session_end_timestamp"
        ].isna()
        .any()
    ):
        fail(
            "Invalid session_end_timestamp "
            "values detected."
        )

    duplicate_sessions = int(
        sessions["session_id"]
        .duplicated()
        .sum()
    )

    if duplicate_sessions > 0:
        fail(
            f"{duplicate_sessions:,} duplicate "
            "session_id values found in sessions."
        )

    print(
        f"[IDENTITY VALIDATION] Loaded "
        f"{len(sessions):,} sessions."
    )

    return sessions


# ============================================================
# SESSION REFERENTIAL INTEGRITY
# ============================================================

def validate_session_reference(
    identity: pd.DataFrame,
    sessions: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking session IDs..."
    )

    valid_sessions = set(
        sessions["session_id"]
    )

    identity_sessions = set(
        identity["session_id"]
    )

    invalid_sessions = (
        identity_sessions
        -
        valid_sessions
    )

    if invalid_sessions:
        fail(
            f"Found {len(invalid_sessions):,} "
            "session IDs not present in sessions."
        )

    pass_message(
        "Session referential integrity passed."
    )


# ============================================================
# SESSION ↔ ANONYMOUS CONSISTENCY
# ============================================================

def validate_session_anonymous(
    identity: pd.DataFrame,
    sessions: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking session-anonymous consistency..."
    )

    session_anonymous_map = (
        sessions
        .set_index("session_id")[
            "anonymous_id"
        ]
        .to_dict()
    )

    expected_anonymous = (
        identity["session_id"]
        .map(session_anonymous_map)
    )

    mismatch = (
        identity["anonymous_id"]
        !=
        expected_anonymous
    )

    if mismatch.any():

        count = int(
            mismatch.sum()
        )

        fail(
            f"{count:,} identity links contain "
            "a session/anonymous mismatch."
        )

    pass_message(
        "Session-anonymous consistency passed."
    )


# ============================================================
# SESSION ↔ CUSTOMER CONSISTENCY
# ============================================================

def validate_session_customer(
    identity: pd.DataFrame,
    sessions: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking session-customer consistency..."
    )

    session_customer_map = (
        sessions
        .set_index("session_id")[
            "customer_id"
        ]
        .to_dict()
    )

    expected_customer = (
        identity["session_id"]
        .map(session_customer_map)
    )

    mismatch = (
        identity["customer_id"]
        !=
        expected_customer
    )

    if mismatch.any():

        count = int(
            mismatch.sum()
        )

        fail(
            f"{count:,} identity links contain "
            "a session/customer mismatch."
        )

    pass_message(
        "Session-customer consistency passed."
    )


# ============================================================
# DUPLICATE MAPPING VALIDATION
# ============================================================

def validate_duplicate_mappings(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking duplicate identity mappings..."
    )

    duplicate_mapping = (
        identity
        .duplicated(
            subset=[
                "anonymous_id",
                "customer_id",
                "session_id",
            ],
            keep=False,
        )
    )

    if duplicate_mapping.any():

        count = int(
            duplicate_mapping.sum()
        )

        fail(
            f"{count:,} rows contain duplicate "
            "anonymous/customer/session mappings."
        )

    pass_message(
        "Duplicate identity mapping validation passed."
    )


# ============================================================
# TIMESTAMP VALIDATION
# ============================================================

def validate_timestamps(
    identity: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking timestamps..."
    )

    identity["link_timestamp"] = (
        pd.to_datetime(
            identity["link_timestamp"],
            errors="coerce",
        )
    )

    invalid_count = int(
        identity[
            "link_timestamp"
        ]
        .isna()
        .sum()
    )

    if invalid_count > 0:
        fail(
            f"{invalid_count:,} invalid "
            "link_timestamp values detected."
        )

    pass_message(
        "Timestamp validation passed."
    )


# ============================================================
# LINK TIMESTAMP WITHIN SESSION
# ============================================================

def validate_link_timestamp_within_session(
    identity: pd.DataFrame,
    sessions: pd.DataFrame,
) -> None:

    print(
        "[IDENTITY VALIDATION] "
        "Checking identity-link timestamp "
        "against session period..."
    )

    session_periods = (
        sessions[
            [
                "session_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ]
        .set_index("session_id")
    )

    expected_start = (
        identity["session_id"]
        .map(
            session_periods[
                "session_start_timestamp"
            ]
        )
    )

    expected_end = (
        identity["session_id"]
        .map(
            session_periods[
                "session_end_timestamp"
            ]
        )
    )

    outside_period = (
        (
            identity["link_timestamp"]
            <
            expected_start
        )
        |
        (
            identity["link_timestamp"]
            >
            expected_end
        )
    )

    if outside_period.any():

        count = int(
            outside_period.sum()
        )

        fail(
            f"{count:,} identity links have "
            "link_timestamp outside their "
            "session period."
        )

    pass_message(
        "Identity-link temporal integrity passed."
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    identity: pd.DataFrame,
) -> None:

    print()
    print("=" * 70)
    print("[IDENTITY VALIDATION] SUMMARY")
    print("=" * 70)

    print(
        f"Identity links       = "
        f"{len(identity):,}"
    )

    print(
        f"Unique anonymous IDs = "
        f"{identity['anonymous_id'].nunique():,}"
    )

    print(
        f"Unique customers     = "
        f"{identity['customer_id'].nunique():,}"
    )

    print(
        f"Unique sessions      = "
        f"{identity['session_id'].nunique():,}"
    )

    print(
        f"Unique link IDs      = "
        f"{identity['identity_link_id'].nunique():,}"
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    identity = load_identity()

    validate_schema(
        identity
    )

    validate_required_fields(
        identity
    )

    normalize_ids(
        identity
    )

    validate_identity_link_id(
        identity
    )

    validate_anonymous_ids(
        identity
    )

    valid_customers = load_customers()

    validate_customer_reference(
        identity,
        valid_customers,
    )

    sessions = load_sessions()

    validate_session_reference(
        identity,
        sessions,
    )

    validate_session_anonymous(
        identity,
        sessions,
    )

    validate_session_customer(
        identity,
        sessions,
    )

    validate_duplicate_mappings(
        identity
    )

    validate_timestamps(
        identity
    )

    validate_link_timestamp_within_session(
        identity,
        sessions,
    )

    print_summary(
        identity
    )

    print()
    print("=" * 70)
    print(
        "[IDENTITY VALIDATION] "
        "COMPLETE — ALL CHECKS PASSED"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()