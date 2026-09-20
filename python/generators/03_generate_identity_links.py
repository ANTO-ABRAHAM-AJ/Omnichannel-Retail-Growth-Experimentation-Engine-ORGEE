"""
ORGEE — Identity Link Generator

Creates anonymous_id → customer_id identity links from
successful login events.

Source:
    Document 7 — Enterprise Generation Configuration
"""

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


# ============================================================
# PROJECT / CONFIGURATION
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
    "orgee_generator_config",
    CONFIG_FILE,
)

if spec is None or spec.loader is None:
    raise ImportError(
        "Unable to load generator configuration."
    )

config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


PRIMARY_SEED = int(config.PRIMARY_SEED)

IDENTITY_LINK_RATE_MIN = float(
    config.IDENTITY_LINK_RATE_MIN
)

IDENTITY_LINK_RATE_MAX = float(
    config.IDENTITY_LINK_RATE_MAX
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

EVENTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "events"
)

IDENTITY_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "identity"
)

EVENTS_FILE = EVENTS_DIR / "events.csv"

OUTPUT_FILE = (
    IDENTITY_DIR
    / "identity_links.csv"
)


# ============================================================
# IDENTITY LINK GENERATION
# ============================================================

def generate_identity_links(
    events: pd.DataFrame,
) -> pd.DataFrame:
    """
    Derive identity links from successful login events.

    Relationship:

        anonymous_id
              ↓
        successful login
              ↓
        customer_id
    """

    required_columns = {
        "anonymous_id",
        "customer_id",
        "session_id",
        "event_timestamp",
        "event_type",
    }

    missing_columns = (
        required_columns
        - set(events.columns)
    )

    if missing_columns:
        raise ValueError(
            "Events dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    events = events.copy()

    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # Successful login events
    # --------------------------------------------------------

    login_events = events[
        (events["event_type"] == "login")
        & events["anonymous_id"].notna()
        & events["customer_id"].notna()
        & events["session_id"].notna()
        & events["event_timestamp"].notna()
    ].copy()

    if login_events.empty:
        raise ValueError(
            "No successful login events found."
        )

    # --------------------------------------------------------
    # One anonymous identity → one customer relationship
    # --------------------------------------------------------

    login_events = (
        login_events
        .sort_values("event_timestamp")
        .drop_duplicates(
            subset=["anonymous_id"],
            keep="first",
        )
    )

    # --------------------------------------------------------
    # Select a deterministic rate inside configured range
    #
    # Document 7:
    # approximately 20–25%
    # --------------------------------------------------------

    rng = np.random.default_rng(
        PRIMARY_SEED + 300
    )

    identity_link_rate = float(
        rng.uniform(
            IDENTITY_LINK_RATE_MIN,
            IDENTITY_LINK_RATE_MAX,
        )
    )

    target_count = max(
        1,
        int(
            round(
                len(login_events)
                * identity_link_rate
            )
        ),
    )

    target_count = min(
        target_count,
        len(login_events),
    )

    selected = (
        login_events
        .sample(
            n=target_count,
            random_state=PRIMARY_SEED + 301,
        )
        .sort_values("event_timestamp")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Construct identity-link entity
    # --------------------------------------------------------

    identity_links = pd.DataFrame(
        {
            "identity_link_id": [
                f"identity_{i:08d}"
                for i in range(
                    1,
                    len(selected) + 1,
                )
            ],
            "anonymous_id": (
                selected["anonymous_id"]
                .astype(str)
                .to_numpy()
            ),
            "customer_id": (
                selected["customer_id"]
                .astype(str)
                .to_numpy()
            ),
            "session_id": (
                selected["session_id"]
                .astype(str)
                .to_numpy()
            ),
            "link_timestamp": (
                selected["event_timestamp"]
                .to_numpy()
            ),
            "link_method": (
                "successful_login"
            ),
        }
    )

    return identity_links


# ============================================================
# VALIDATION
# ============================================================

def validate_identity_links(
    identity_links: pd.DataFrame,
    events: pd.DataFrame,
) -> None:
    """
    Validate identity-link requirements.
    """

    required_columns = {
        "identity_link_id",
        "anonymous_id",
        "customer_id",
        "session_id",
        "link_timestamp",
        "link_method",
    }

    missing_columns = (
        required_columns
        - set(identity_links.columns)
    )

    if missing_columns:
        raise ValueError(
            "Identity links are missing columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # Primary-key uniqueness
    # --------------------------------------------------------

    if (
        identity_links[
            "identity_link_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "Duplicate identity_link_id values detected."
        )

    # --------------------------------------------------------
    # Anonymous identity uniqueness
    # --------------------------------------------------------

    if (
        identity_links[
            "anonymous_id"
        ]
        .duplicated()
        .any()
    ):
        raise ValueError(
            "An anonymous_id is linked more than once."
        )

    # --------------------------------------------------------
    # Required values
    # --------------------------------------------------------

    for column in [
        "anonymous_id",
        "customer_id",
        "session_id",
        "link_timestamp",
    ]:
        if identity_links[column].isna().any():
            raise ValueError(
                f"Null values detected in {column}."
            )

    # --------------------------------------------------------
    # Source login events
    # --------------------------------------------------------

    login_events = events[
        events["event_type"] == "login"
    ][
        [
            "anonymous_id",
            "customer_id",
            "session_id",
            "event_timestamp",
        ]
    ].copy()

    login_events["anonymous_id"] = (
        login_events["anonymous_id"].astype(str)
    )

    login_events["customer_id"] = (
        login_events["customer_id"].astype(str)
    )

    login_events["session_id"] = (
        login_events["session_id"].astype(str)
    )

    login_events["event_timestamp"] = pd.to_datetime(
        login_events["event_timestamp"],
        errors="coerce",
    )

    source_keys = login_events[
        [
            "anonymous_id",
            "customer_id",
            "session_id",
        ]
    ].drop_duplicates()

    merged = identity_links.merge(
        source_keys,
        on=[
            "anonymous_id",
            "customer_id",
            "session_id",
        ],
        how="left",
        indicator=True,
    )

    if (merged["_merge"] != "both").any():
        raise ValueError(
            "Identity link found without a corresponding "
            "successful login event."
        )

    # --------------------------------------------------------
    # Verify exact login timestamp
    # --------------------------------------------------------

    timestamp_source = (
        login_events
        .rename(
            columns={
                "event_timestamp":
                    "source_login_timestamp"
            }
        )
    )

    timestamp_check = identity_links.merge(
        timestamp_source,
        on=[
            "anonymous_id",
            "customer_id",
            "session_id",
        ],
        how="left",
    )

    if (
        timestamp_check["link_timestamp"]
        != timestamp_check["source_login_timestamp"]
    ).any():
        raise ValueError(
            "Identity link timestamp does not match "
            "the source login timestamp."
        )

    # --------------------------------------------------------
    # Link method
    # --------------------------------------------------------

    if not (
        identity_links["link_method"]
        == "successful_login"
    ).all():
        raise ValueError(
            "Invalid identity-link method detected."
        )

    print(
        f"[IDENTITY] Validation passed — "
        f"{len(identity_links):,} identity links."
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    if not EVENTS_FILE.exists():
        raise FileNotFoundError(
            "Events dataset not found.\n"
            f"Expected: {EVENTS_FILE}\n\n"
            "Run the session and event generators first."
        )

    IDENTITY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "[IDENTITY] Loading events..."
    )

    events = pd.read_csv(
        EVENTS_FILE,
        parse_dates=["event_timestamp"],
    )

    print(
        f"[IDENTITY] Loaded "
        f"{len(events):,} events."
    )

    identity_links = generate_identity_links(
        events
    )

    validate_identity_links(
        identity_links,
        events,
    )

    identity_links.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"[IDENTITY] Generated "
        f"{len(identity_links):,} identity links."
    )

    print(
        "[IDENTITY] Output written to:"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()