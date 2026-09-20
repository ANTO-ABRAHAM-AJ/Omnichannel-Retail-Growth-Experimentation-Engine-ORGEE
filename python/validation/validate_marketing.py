"""
ORGEE — MARKETING VALIDATION

Validates:

1. campaigns.csv
2. campaign_exposures.csv

Aligned with the actual ORGEE marketing generator output.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# ORGEE — MARKETING VALIDATION
# ============================================================

print("=" * 70)
print("ORGEE — MARKETING VALIDATION")
print("=" * 70)


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MARKETING_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "marketing"
)

CAMPAIGNS_FILE = (
    MARKETING_DIR
    / "campaigns.csv"
)

EXPOSURES_FILE = (
    MARKETING_DIR
    / "campaign_exposures.csv"
)

SESSIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "sessions"
    / "sessions.csv"
)


# ============================================================
# EXPECTED VOLUMES
# ============================================================

EXPECTED_CAMPAIGNS = 50
EXPECTED_EXPOSURES = 1_000_000


# ============================================================
# ALLOWED VALUES
# ============================================================

ALLOWED_CHANNELS = {
    "email",
    "push",
    "sms",
    "social",
    "display",
    "search",
}

# IMPORTANT:
# These values match the actual ORGEE marketing generator
# output for exposure_outcome.

ALLOWED_EXPOSURE_OUTCOMES = {
    "impression",
    "click",
    "conversion",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def fail(message: str) -> None:
    raise ValueError(
        f"[MARKETING VALIDATION FAILED] {message}"
    )


def require_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:

        fail(
            f"Missing {dataset_name} columns: "
            f"{sorted(missing_columns)}\n"
            f"Actual columns: "
            f"{list(dataframe.columns)}"
        )


# ============================================================
# FILE EXISTENCE
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking required files..."
)

required_files = [
    (
        CAMPAIGNS_FILE,
        "Campaign",
    ),
    (
        EXPOSURES_FILE,
        "Campaign exposure",
    ),
    (
        SESSIONS_FILE,
        "Sessions",
    ),
]

for file_path, name in required_files:

    if not file_path.exists():

        fail(
            f"{name} file not found:\n"
            f"{file_path}"
        )

print(
    "[MARKETING VALIDATION PASSED] "
    "Required files exist."
)


# ============================================================
# LOAD CAMPAIGNS
# ============================================================

print(
    "\n[MARKETING VALIDATION] "
    "Loading campaigns..."
)

campaigns = pd.read_csv(
    CAMPAIGNS_FILE
)

print(
    f"[MARKETING VALIDATION] "
    f"Loaded {len(campaigns):,} campaigns."
)


# ============================================================
# CAMPAIGN SCHEMA
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign schema..."
)

REQUIRED_CAMPAIGN_COLUMNS = {
    "campaign_id",
    "campaign_name",
    "channel",
    "campaign_type",
    "objective",
    "start_date",
    "end_date",
}

require_columns(
    campaigns,
    REQUIRED_CAMPAIGN_COLUMNS,
    "campaign",
)

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign schema validation passed."
)


# ============================================================
# CAMPAIGN REQUIRED FIELDS
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign required fields..."
)

for column in REQUIRED_CAMPAIGN_COLUMNS:

    if campaigns[column].isna().any():

        null_count = int(
            campaigns[column]
            .isna()
            .sum()
        )

        fail(
            f"Campaign column '{column}' "
            f"contains {null_count:,} null values."
        )

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign required-field completeness passed."
)


# ============================================================
# CAMPAIGN ROW COUNT
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign row count..."
)

if len(campaigns) != EXPECTED_CAMPAIGNS:

    fail(
        f"Expected {EXPECTED_CAMPAIGNS:,} campaigns, "
        f"found {len(campaigns):,}."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    f"Campaign row count = {len(campaigns):,}."
)


# ============================================================
# CAMPAIGN ID
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign_id..."
)

campaigns["campaign_id"] = (
    campaigns["campaign_id"]
    .astype(str)
    .str.strip()
)

if campaigns[
    "campaign_id"
].eq("").any():

    fail(
        "Blank campaign_id values detected."
    )

if campaigns[
    "campaign_id"
].duplicated().any():

    duplicate_count = int(
        campaigns[
            "campaign_id"
        ]
        .duplicated()
        .sum()
    )

    fail(
        "Duplicate campaign_id values detected: "
        f"{duplicate_count:,}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "campaign_id uniqueness passed."
)


# ============================================================
# CAMPAIGN CHANNEL
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign channels..."
)

campaigns["channel"] = (
    campaigns["channel"]
    .astype(str)
    .str.strip()
)

invalid_channels = (
    ~campaigns["channel"].isin(
        ALLOWED_CHANNELS
    )
)

if invalid_channels.any():

    values = sorted(
        campaigns.loc[
            invalid_channels,
            "channel",
        ]
        .unique()
        .tolist()
    )

    fail(
        "Invalid campaign channel values: "
        f"{values}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign channel validation passed."
)


# ============================================================
# CAMPAIGN DATES
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign dates..."
)

campaigns["start_date"] = pd.to_datetime(
    campaigns["start_date"],
    errors="coerce",
)

campaigns["end_date"] = pd.to_datetime(
    campaigns["end_date"],
    errors="coerce",
)

invalid_start = (
    campaigns["start_date"]
    .isna()
)

invalid_end = (
    campaigns["end_date"]
    .isna()
)

if invalid_start.any():

    count = int(
        invalid_start.sum()
    )

    fail(
        f"Invalid start_date values: "
        f"{count:,}"
    )


if invalid_end.any():

    count = int(
        invalid_end.sum()
    )

    fail(
        f"Invalid end_date values: "
        f"{count:,}"
    )


invalid_date_order = (
    campaigns["end_date"]
    <
    campaigns["start_date"]
)

if invalid_date_order.any():

    count = int(
        invalid_date_order.sum()
    )

    fail(
        f"{count:,} campaigns have "
        "end_date before start_date."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign date validation passed."
)


# ============================================================
# LOAD SESSIONS
# ============================================================

print(
    "\n[MARKETING VALIDATION] "
    "Loading enterprise sessions..."
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

sessions["session_id"] = (
    sessions["session_id"]
    .astype(str)
    .str.strip()
)

sessions["anonymous_id"] = (
    sessions["anonymous_id"]
    .astype(str)
    .str.strip()
)

sessions["customer_id"] = (
    sessions["customer_id"]
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

if sessions[
    "session_start_timestamp"
].isna().any():

    fail(
        "Invalid session_start_timestamp "
        "values detected in sessions."
    )

if sessions[
    "session_end_timestamp"
].isna().any():

    fail(
        "Invalid session_end_timestamp "
        "values detected in sessions."
    )

valid_session_ids = set(
    sessions["session_id"]
)

session_anonymous_map = (
    sessions
    .set_index("session_id")[
        "anonymous_id"
    ]
    .to_dict()
)

session_customer_map = (
    sessions
    .set_index("session_id")[
        "customer_id"
    ]
    .to_dict()
)

session_start_map = (
    sessions
    .set_index("session_id")[
        "session_start_timestamp"
    ]
    .to_dict()
)

session_end_map = (
    sessions
    .set_index("session_id")[
        "session_end_timestamp"
    ]
    .to_dict()
)

print(
    f"[MARKETING VALIDATION] "
    f"Loaded {len(sessions):,} sessions."
)


# ============================================================
# LOAD EXPOSURES
# ============================================================

print(
    "\n[MARKETING VALIDATION] "
    "Loading campaign exposures..."
)

exposures = pd.read_csv(
    EXPOSURES_FILE
)

print(
    f"[MARKETING VALIDATION] "
    f"Loaded {len(exposures):,} campaign exposures."
)


# ============================================================
# EXPOSURE SCHEMA
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure schema..."
)

REQUIRED_EXPOSURE_COLUMNS = {
    "campaign_exposure_id",
    "campaign_id",
    "session_id",
    "anonymous_id",
    "customer_id",
    "channel",
    "exposure_timestamp",
    "exposure_outcome",
}

require_columns(
    exposures,
    REQUIRED_EXPOSURE_COLUMNS,
    "campaign exposure",
)

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure schema validation passed."
)


# ============================================================
# EXPOSURE REQUIRED FIELDS
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure required fields..."
)

for column in REQUIRED_EXPOSURE_COLUMNS:

    if exposures[column].isna().any():

        null_count = int(
            exposures[column]
            .isna()
            .sum()
        )

        fail(
            f"Exposure column '{column}' "
            f"contains {null_count:,} null values."
        )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure required-field completeness passed."
)


# ============================================================
# EXPOSURE ROW COUNT
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure row count..."
)

if len(exposures) != EXPECTED_EXPOSURES:

    fail(
        f"Expected {EXPECTED_EXPOSURES:,} exposures, "
        f"found {len(exposures):,}."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    f"Exposure row count = {len(exposures):,}."
)


# ============================================================
# EXPOSURE ID
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign_exposure_id..."
)

exposures[
    "campaign_exposure_id"
] = (
    exposures[
        "campaign_exposure_id"
    ]
    .astype(str)
    .str.strip()
)

if exposures[
    "campaign_exposure_id"
].eq("").any():

    fail(
        "Blank campaign_exposure_id "
        "values detected."
    )

if exposures[
    "campaign_exposure_id"
].duplicated().any():

    duplicate_count = int(
        exposures[
            "campaign_exposure_id"
        ]
        .duplicated()
        .sum()
    )

    fail(
        "Duplicate campaign_exposure_id "
        "values detected: "
        f"{duplicate_count:,}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "campaign_exposure_id uniqueness passed."
)


# ============================================================
# CAMPAIGN REFERENTIAL INTEGRITY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign referential integrity..."
)

exposures["campaign_id"] = (
    exposures["campaign_id"]
    .astype(str)
    .str.strip()
)

valid_campaign_ids = set(
    campaigns["campaign_id"]
)

invalid_campaign_ids = (
    set(exposures["campaign_id"])
    -
    valid_campaign_ids
)

if invalid_campaign_ids:

    fail(
        f"Found {len(invalid_campaign_ids):,} "
        "campaign IDs in exposures that do not "
        "exist in campaigns."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign referential integrity passed."
)


# ============================================================
# SESSION REFERENTIAL INTEGRITY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking session referential integrity..."
)

exposures["session_id"] = (
    exposures["session_id"]
    .astype(str)
    .str.strip()
)

invalid_session_ids = (
    set(exposures["session_id"])
    -
    valid_session_ids
)

if invalid_session_ids:

    fail(
        f"Found {len(invalid_session_ids):,} "
        "session IDs in campaign exposures "
        "that do not exist in sessions."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Session referential integrity passed."
)


# ============================================================
# EXPOSURE CHANNEL
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure channels..."
)

exposures["channel"] = (
    exposures["channel"]
    .astype(str)
    .str.strip()
)

invalid_exposure_channels = (
    ~exposures["channel"].isin(
        ALLOWED_CHANNELS
    )
)

if invalid_exposure_channels.any():

    values = sorted(
        exposures.loc[
            invalid_exposure_channels,
            "channel",
        ]
        .unique()
        .tolist()
    )

    fail(
        "Invalid exposure channel values: "
        f"{values}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure channel validation passed."
)


# ============================================================
# CAMPAIGN / EXPOSURE CHANNEL CONSISTENCY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking campaign/exposure channel consistency..."
)

campaign_channel_map = (
    campaigns
    .set_index("campaign_id")[
        "channel"
    ]
    .to_dict()
)

expected_channels = (
    exposures["campaign_id"]
    .map(campaign_channel_map)
)

channel_mismatch = (
    exposures["channel"]
    !=
    expected_channels
)

if channel_mismatch.any():

    count = int(
        channel_mismatch.sum()
    )

    fail(
        f"{count:,} exposures have a "
        "channel inconsistent with their campaign."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Campaign/exposure channel consistency passed."
)


# ============================================================
# EXPOSURE TIMESTAMP
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure timestamps..."
)

exposures[
    "exposure_timestamp"
] = pd.to_datetime(
    exposures[
        "exposure_timestamp"
    ],
    errors="coerce",
)

invalid_timestamps = (
    exposures[
        "exposure_timestamp"
    ].isna()
)

if invalid_timestamps.any():

    count = int(
        invalid_timestamps.sum()
    )

    fail(
        f"Invalid exposure_timestamp "
        f"values: {count:,}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure timestamp validation passed."
)


# ============================================================
# EXPOSURE / CAMPAIGN TEMPORAL INTEGRITY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure/campaign temporal integrity..."
)

campaign_start_map = (
    campaigns
    .set_index("campaign_id")[
        "start_date"
    ]
    .to_dict()
)

campaign_end_map = (
    campaigns
    .set_index("campaign_id")[
        "end_date"
    ]
    .to_dict()
)

expected_campaign_start = (
    exposures["campaign_id"]
    .map(campaign_start_map)
)

expected_campaign_end = (
    exposures["campaign_id"]
    .map(campaign_end_map)
)

outside_campaign_period = (
    (
        exposures["exposure_timestamp"]
        < expected_campaign_start
    )
    |
    (
        exposures["exposure_timestamp"]
        > expected_campaign_end
    )
)

if outside_campaign_period.any():

    count = int(
        outside_campaign_period.sum()
    )

    fail(
        f"{count:,} exposures occur "
        "outside their campaign period."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure/campaign temporal integrity passed."
)


# ============================================================
# EXPOSURE / SESSION TEMPORAL INTEGRITY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure/session temporal integrity..."
)

expected_session_start = (
    exposures["session_id"]
    .map(session_start_map)
)

expected_session_end = (
    exposures["session_id"]
    .map(session_end_map)
)

outside_session_period = (
    (
        exposures["exposure_timestamp"]
        < expected_session_start
    )
    |
    (
        exposures["exposure_timestamp"]
        > expected_session_end
    )
)

if outside_session_period.any():

    count = int(
        outside_session_period.sum()
    )

    fail(
        f"{count:,} exposures occur "
        "outside their session period."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure/session temporal integrity passed."
)


# ============================================================
# SESSION / ANONYMOUS CONSISTENCY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking session-anonymous consistency..."
)

exposures["anonymous_id"] = (
    exposures["anonymous_id"]
    .astype(str)
    .str.strip()
)

expected_anonymous = (
    exposures["session_id"]
    .map(session_anonymous_map)
)

anonymous_mismatch = (
    exposures["anonymous_id"]
    !=
    expected_anonymous
)

if anonymous_mismatch.any():

    count = int(
        anonymous_mismatch.sum()
    )

    fail(
        f"{count:,} exposures have "
        "session/anonymous mismatches."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Session-anonymous consistency passed."
)


# ============================================================
# SESSION / CUSTOMER CONSISTENCY
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking session-customer consistency..."
)

exposures["customer_id"] = (
    exposures["customer_id"]
    .astype(str)
    .str.strip()
)

expected_customer = (
    exposures["session_id"]
    .map(session_customer_map)
)

customer_mismatch = (
    exposures["customer_id"]
    !=
    expected_customer
)

if customer_mismatch.any():

    count = int(
        customer_mismatch.sum()
    )

    fail(
        f"{count:,} exposures have "
        "session/customer mismatches."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Session-customer consistency passed."
)


# ============================================================
# ANONYMOUS ID FORMAT
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking anonymous IDs..."
)

invalid_anonymous = (
    ~exposures["anonymous_id"]
    .str.startswith("anon_")
)

if invalid_anonymous.any():

    count = int(
        invalid_anonymous.sum()
    )

    fail(
        f"{count:,} invalid anonymous_id values."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Anonymous-ID format validation passed."
)


# ============================================================
# CUSTOMER ID COMPLETENESS
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking customer IDs..."
)

if exposures[
    "customer_id"
].eq("").any():

    count = int(
        exposures[
            "customer_id"
        ].eq("").sum()
    )

    fail(
        f"{count:,} blank customer_id values."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Customer-ID completeness passed."
)


# ============================================================
# EXPOSURE OUTCOME
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Checking exposure outcomes..."
)

exposures[
    "exposure_outcome"
] = (
    exposures[
        "exposure_outcome"
    ]
    .astype(str)
    .str.strip()
)

invalid_outcomes = (
    ~exposures[
        "exposure_outcome"
    ].isin(
        ALLOWED_EXPOSURE_OUTCOMES
    )
)

if invalid_outcomes.any():

    values = sorted(
        exposures.loc[
            invalid_outcomes,
            "exposure_outcome",
        ]
        .unique()
        .tolist()
    )

    fail(
        "Invalid exposure outcome values: "
        f"{values}"
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure outcome validation passed."
)


# ============================================================
# EXPOSURE PERIOD
# ============================================================

print(
    "[MARKETING VALIDATION] "
    "Exposure period:"
)

exposure_start = (
    exposures[
        "exposure_timestamp"
    ].min()
)

exposure_end = (
    exposures[
        "exposure_timestamp"
    ].max()
)

print(
    f"    Period start = "
    f"{exposure_start}"
)

print(
    f"    Period end   = "
    f"{exposure_end}"
)

if exposure_start >= exposure_end:

    fail(
        "Invalid exposure observation period."
    )

print(
    "[MARKETING VALIDATION PASSED] "
    "Exposure period validation passed."
)


# ============================================================
# OUTCOME DISTRIBUTION
# ============================================================

print(
    "\n[MARKETING VALIDATION] "
    "Exposure outcome distribution:"
)

outcome_counts = (
    exposures[
        "exposure_outcome"
    ]
    .value_counts()
)

outcome_percentages = (
    exposures[
        "exposure_outcome"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)

for outcome in sorted(
    outcome_counts.index
):

    print(
        f"    {outcome:<15} = "
        f"{outcome_counts[outcome]:>10,} "
        f"({outcome_percentages[outcome]:6.2f}%)"
    )


# ============================================================
# EXPOSURE CAMPAIGN DISTRIBUTION
# ============================================================

print(
    "\n[MARKETING VALIDATION] "
    "Campaign exposure distribution:"
)

exposure_by_campaign = (
    exposures[
        "campaign_id"
    ]
    .value_counts()
    .sort_index()
)

print(
    f"    Campaigns receiving exposures = "
    f"{len(exposure_by_campaign):,}"
)

print(
    f"    Minimum exposures/campaign    = "
    f"{exposure_by_campaign.min():,}"
)

print(
    f"    Maximum exposures/campaign    = "
    f"{exposure_by_campaign.max():,}"
)

print(
    f"    Mean exposures/campaign       = "
    f"{exposure_by_campaign.mean():,.2f}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("[MARKETING VALIDATION] SUMMARY")
print("=" * 70)

print(
    f"Campaigns            = "
    f"{len(campaigns):,}"
)

print(
    f"Campaign exposures   = "
    f"{len(exposures):,}"
)

print(
    f"Unique campaigns     = "
    f"{exposures['campaign_id'].nunique():,}"
)

print(
    f"Unique sessions      = "
    f"{exposures['session_id'].nunique():,}"
)

print(
    f"Unique anonymous IDs = "
    f"{exposures['anonymous_id'].nunique():,}"
)

print(
    f"Unique customers     = "
    f"{exposures['customer_id'].nunique():,}"
)

print(
    f"Unique exposure IDs  = "
    f"{exposures['campaign_exposure_id'].nunique():,}"
)

print("=" * 70)

print(
    "[MARKETING VALIDATION] "
    "COMPLETE — ALL CHECKS PASSED"
)

print("=" * 70)