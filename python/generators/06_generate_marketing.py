"""
ORGEE — Marketing Generator

Generates:
    1. Marketing campaigns
    2. Campaign exposures

Source:
    Document 7 — Enterprise Generation Configuration

Targets:
    Campaigns          = 50
    Campaign Exposures = 1,000,000
"""

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed" / "public"
)

ENTERPRISE_DATA_DIR = (
    PROJECT_ROOT / "data" / "enterprise"
)

SESSION_DIR = (
    ENTERPRISE_DATA_DIR / "sessions"
)

EVENT_DIR = (
    ENTERPRISE_DATA_DIR / "events"
)

MARKETING_DIR = (
    ENTERPRISE_DATA_DIR / "marketing"
)

SESSIONS_FILE = (
    SESSION_DIR / "sessions.csv"
)

EVENTS_FILE = (
    EVENT_DIR / "events.csv"
)

ORDERS_FILE = (
    PUBLIC_DATA_DIR / "olist_orders_dataset.csv"
)

CONFIG_FILE = (
    Path(__file__).resolve().parent
    / "01_generator_config.py"
)

CAMPAIGNS_OUTPUT = (
    MARKETING_DIR / "campaigns.csv"
)

EXPOSURES_OUTPUT = (
    MARKETING_DIR / "campaign_exposures.csv"
)


# ============================================================
# LOAD CONFIGURATION
# ============================================================

spec = importlib.util.spec_from_file_location(
    "org_generator_config",
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

TARGET_VOLUMES = config.TARGET_VOLUMES

TARGET_CAMPAIGNS = int(
    TARGET_VOLUMES[
        "marketing_campaigns"
    ]
)

TARGET_EXPOSURES = int(
    TARGET_VOLUMES[
        "campaign_exposures"
    ]
)


# ============================================================
# DOCUMENT 7 CONFIGURATION
# ============================================================

CHANNELS = tuple(
    config.CAMPAIGN_CHANNELS
)

CHANNEL_PROBABILITIES = np.array(
    [
        config.CAMPAIGN_CHANNEL_DISTRIBUTION[
            channel
        ]
        for channel in CHANNELS
    ],
    dtype=float,
)

OBJECTIVES = tuple(
    config.CAMPAIGN_OBJECTIVES
)

EXPOSURE_OUTCOMES = tuple(
    config.CAMPAIGN_EXPOSURE_OUTCOMES
)

MARKETING_FUNNEL = (
    config.MARKETING_FUNNEL_PROBABILITIES
)

EXPOSURE_TO_CLICK_PROBABILITY = float(
    MARKETING_FUNNEL[
        "exposure_to_engagement"
    ]
)

CLICK_TO_CONVERSION_PROBABILITY = float(
    MARKETING_FUNNEL[
        "engagement_to_conversion"
    ]
)


# ============================================================
# CAMPAIGN NAMES
# ============================================================

CAMPAIGN_NAME_PREFIXES = {
    "acquisition": (
        "New Customer",
        "Welcome",
        "Discover",
        "First Purchase",
        "New Shopper",
    ),
    "conversion": (
        "Conversion",
        "Checkout",
        "Purchase",
        "Shop Now",
        "Limited Offer",
    ),
    "retention": (
        "Customer Return",
        "Loyalty",
        "Come Back",
        "Customer Appreciation",
        "Reactivation",
    ),
    "engagement": (
        "Engage",
        "Discover More",
        "Explore",
        "Product Discovery",
        "Shop & Explore",
    ),
    "promotion": (
        "Special Offer",
        "Seasonal",
        "Promotion",
        "Deal",
        "Savings",
    ),
}


# ============================================================
# CAMPAIGN GENERATION
# ============================================================

def generate_campaigns(
    period_start: pd.Timestamp,
    period_end: pd.Timestamp,
    rng: np.random.Generator,
) -> pd.DataFrame:

    if period_start >= period_end:
        raise ValueError(
            "Invalid campaign observation period."
        )

    total_days = max(
        1,
        (period_end - period_start).days,
    )

    records = []

    for i in range(
        1,
        TARGET_CAMPAIGNS + 1,
    ):

        channel = rng.choice(
            CHANNELS,
            p=CHANNEL_PROBABILITIES,
        )

        objective = rng.choice(
            OBJECTIVES
        )

        campaign_type = (
            f"{objective}_campaign"
        )

        prefix = rng.choice(
            CAMPAIGN_NAME_PREFIXES[
                objective
            ]
        )

        campaign_name = (
            f"{prefix} Campaign {i:02d}"
        )

        max_start_offset = max(
            0,
            total_days - 7,
        )

        start_offset_days = int(
            rng.integers(
                0,
                max_start_offset + 1,
            )
        )

        start_date = (
            period_start
            + pd.Timedelta(
                days=start_offset_days
            )
        )

        duration_days = int(
            rng.integers(
                7,
                31,
            )
        )

        end_date = (
            start_date
            + pd.Timedelta(
                days=duration_days
            )
        )

        if end_date > period_end:
            end_date = period_end

        if end_date <= start_date:
            raise ValueError(
                "Campaign period became invalid."
            )

        records.append(
            {
                "campaign_id":
                    f"camp_{i:04d}",
                "campaign_name":
                    campaign_name,
                "channel":
                    channel,
                "campaign_type":
                    campaign_type,
                "objective":
                    objective,
                "start_date":
                    start_date,
                "end_date":
                    end_date,
            }
        )

    return pd.DataFrame(records)


# ============================================================
# LOAD SESSIONS
# ============================================================

def load_behavioral_population() -> pd.DataFrame:

    if not SESSIONS_FILE.exists():
        raise FileNotFoundError(
            f"Sessions dataset not found:\n"
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
        parse_dates=[
            "session_start_timestamp",
            "session_end_timestamp",
        ],
    )

    if sessions.empty:
        raise ValueError(
            "Sessions dataset is empty."
        )

    sessions = sessions.dropna(
        subset=[
            "session_id",
            "anonymous_id",
            "session_start_timestamp",
            "session_end_timestamp",
        ]
    ).copy()

    sessions["session_id"] = (
        sessions["session_id"].astype(str)
    )

    sessions["anonymous_id"] = (
        sessions["anonymous_id"].astype(str)
    )

    sessions["customer_id"] = (
        sessions["customer_id"].astype("string")
    )

    return sessions


# ============================================================
# CONFIRM ACTIVE POPULATION
# ============================================================

def enrich_population_with_events(
    sessions: pd.DataFrame,
) -> pd.DataFrame:

    if not EVENTS_FILE.exists():
        raise FileNotFoundError(
            f"Events dataset not found:\n"
            f"{EVENTS_FILE}"
        )

    events = pd.read_csv(
        EVENTS_FILE,
        usecols=["session_id"],
    )

    if events.empty:
        raise ValueError(
            "Events dataset is empty."
        )

    active_sessions = set(
        events["session_id"]
        .astype(str)
        .drop_duplicates()
    )

    population = sessions[
        sessions["session_id"].isin(
            active_sessions
        )
    ].copy()

    if population.empty:
        raise ValueError(
            "No active sessions available for "
            "marketing exposure generation."
        )

    return population


# ============================================================
# EXPOSURE GENERATION
# ============================================================

def generate_exposures(
    campaigns: pd.DataFrame,
    population: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Generate campaign exposures using only campaign/session
    combinations that have a valid temporal intersection.
    """

    if campaigns.empty:
        raise ValueError(
            "Campaign dataset is empty."
        )

    if population.empty:
        raise ValueError(
            "Marketing population is empty."
        )

    population = population.copy()

    population[
        "session_start_timestamp"
    ] = pd.to_datetime(
        population[
            "session_start_timestamp"
        ],
        errors="coerce",
    )

    population[
        "session_end_timestamp"
    ] = pd.to_datetime(
        population[
            "session_end_timestamp"
        ],
        errors="coerce",
    )

    if (
        population[
            "session_start_timestamp"
        ].isna().any()
        or
        population[
            "session_end_timestamp"
        ].isna().any()
    ):
        raise ValueError(
            "Invalid session timestamps detected."
        )

    # --------------------------------------------------------
    # Build campaign/session eligibility pools
    #
    # A session is eligible for a campaign when the two
    # observation periods overlap.
    # --------------------------------------------------------

    eligible_sessions_by_campaign = {}

    for campaign in campaigns.itertuples(
        index=False
    ):

        campaign_start = pd.Timestamp(
            campaign.start_date
        )

        campaign_end = pd.Timestamp(
            campaign.end_date
        )

        eligible = population[
            (
                population[
                    "session_end_timestamp"
                ]
                >= campaign_start
            )
            &
            (
                population[
                    "session_start_timestamp"
                ]
                <= campaign_end
            )
        ]

        if eligible.empty:
            raise ValueError(
                "No eligible sessions found for campaign "
                f"{campaign.campaign_id}."
            )

        eligible_sessions_by_campaign[
            campaign.campaign_id
        ] = eligible

    # --------------------------------------------------------
    # Allocate exposure volume across campaigns
    # --------------------------------------------------------

    campaign_indices = rng.integers(
        0,
        len(campaigns),
        size=TARGET_EXPOSURES,
    )

    exposure_campaigns = (
        campaigns.iloc[
            campaign_indices
        ]
        .reset_index(drop=True)
    )

    exposure_records = []

    # --------------------------------------------------------
    # Generate each exposure
    # --------------------------------------------------------

    for index in range(
        TARGET_EXPOSURES
    ):

        campaign = (
            exposure_campaigns.iloc[index]
        )

        campaign_id = str(
            campaign["campaign_id"]
        )

        eligible_sessions = (
            eligible_sessions_by_campaign[
                campaign_id
            ]
        )

        session_index = int(
            rng.integers(
                0,
                len(eligible_sessions),
            )
        )

        session = (
            eligible_sessions.iloc[
                session_index
            ]
        )

        campaign_start = pd.Timestamp(
            campaign["start_date"]
        )

        campaign_end = pd.Timestamp(
            campaign["end_date"]
        )

        session_start = pd.Timestamp(
            session[
                "session_start_timestamp"
            ]
        )

        session_end = pd.Timestamp(
            session[
                "session_end_timestamp"
            ]
        )

        # ----------------------------------------------------
        # Valid temporal intersection
        # ----------------------------------------------------

        effective_start = max(
            campaign_start,
            session_start,
        )

        effective_end = min(
            campaign_end,
            session_end,
        )

        if effective_start > effective_end:
            raise ValueError(
                "Internal temporal eligibility error for "
                f"campaign {campaign_id}."
            )

        # ----------------------------------------------------
        # Exposure timestamp
        # ----------------------------------------------------

        if effective_start == effective_end:

            exposure_timestamp = (
                effective_start
            )

        else:

            random_ns = int(
                rng.integers(
                    effective_start.value,
                    effective_end.value + 1,
                )
            )

            exposure_timestamp = (
                pd.Timestamp(random_ns)
            )

        exposure_records.append(
            {
                "campaign_exposure_id":
                    (
                        f"exposure_"
                        f"{index + 1:09d}"
                    ),

                "campaign_id":
                    campaign_id,

                "session_id":
                    str(
                        session["session_id"]
                    ),

                "anonymous_id":
                    str(
                        session["anonymous_id"]
                    ),

                "customer_id":
                    session["customer_id"],

                "channel":
                    campaign["channel"],

                "exposure_timestamp":
                    exposure_timestamp,
            }
        )

    exposures = pd.DataFrame(
        exposure_records
    )

    # --------------------------------------------------------
    # Generate outcome
    #
    # impression → click → conversion
    # --------------------------------------------------------

    random_values = rng.random(
        TARGET_EXPOSURES
    )

    outcomes = np.full(
        TARGET_EXPOSURES,
        "impression",
        dtype=object,
    )

    click_mask = (
        random_values
        < EXPOSURE_TO_CLICK_PROBABILITY
    )

    outcomes[
        click_mask
    ] = "click"

    click_indices = np.where(
        click_mask
    )[0]

    if len(click_indices) > 0:

        conversion_random = rng.random(
            len(click_indices)
        )

        conversion_mask = (
            conversion_random
            < CLICK_TO_CONVERSION_PROBABILITY
        )

        conversion_indices = (
            click_indices[
                conversion_mask
            ]
        )

        outcomes[
            conversion_indices
        ] = "conversion"

    exposures[
        "exposure_outcome"
    ] = outcomes

    return exposures

    # --------------------------------------------------------
    # Outcome
    #
    # Document 7 schema:
    # impression → click → conversion
    # --------------------------------------------------------

    random_values = rng.random(
        TARGET_EXPOSURES
    )

    outcomes = np.full(
        TARGET_EXPOSURES,
        "impression",
        dtype=object,
    )

    click_mask = (
        random_values
        < EXPOSURE_TO_CLICK_PROBABILITY
    )

    outcomes[
        click_mask
    ] = "click"

    click_indices = np.where(
        click_mask
    )[0]

    if len(click_indices) > 0:

        conversion_random = rng.random(
            len(click_indices)
        )

        conversion_mask = (
            conversion_random
            < CLICK_TO_CONVERSION_PROBABILITY
        )

        conversion_indices = (
            click_indices[
                conversion_mask
            ]
        )

        outcomes[
            conversion_indices
        ] = "conversion"

    exposures = pd.DataFrame(
        {
            "campaign_exposure_id": [
                f"exposure_{i:09d}"
                for i in range(
                    1,
                    TARGET_EXPOSURES + 1,
                )
            ],
            "campaign_id":
                selected_campaigns[
                    "campaign_id"
                ].values,
            "session_id":
                selected_population[
                    "session_id"
                ].values,
            "anonymous_id":
                selected_population[
                    "anonymous_id"
                ].values,
            "customer_id":
                selected_population[
                    "customer_id"
                ].values,
            "channel":
                selected_campaigns[
                    "channel"
                ].values,
            "exposure_timestamp":
                timestamps,
            "exposure_outcome":
                outcomes,
        }
    )

    return exposures


# ============================================================
# CAMPAIGN VALIDATION
# ============================================================

def validate_campaigns(
    campaigns: pd.DataFrame,
) -> None:

    required_columns = {
        "campaign_id",
        "campaign_name",
        "channel",
        "campaign_type",
        "objective",
        "start_date",
        "end_date",
    }

    missing = (
        required_columns
        - set(campaigns.columns)
    )

    if missing:
        raise ValueError(
            f"Missing campaign columns: "
            f"{sorted(missing)}"
        )

    if len(campaigns) != TARGET_CAMPAIGNS:
        raise ValueError(
            f"Expected {TARGET_CAMPAIGNS} campaigns, "
            f"generated {len(campaigns)}."
        )

    if campaigns[
        "campaign_id"
    ].duplicated().any():
        raise ValueError(
            "Duplicate campaign_id values detected."
        )

    if campaigns[
        list(required_columns)
    ].isna().any().any():
        raise ValueError(
            "Null values detected in campaign entity."
        )

    if not campaigns[
        "channel"
    ].isin(CHANNELS).all():
        raise ValueError(
            "Invalid marketing channel detected."
        )

    if not campaigns[
        "objective"
    ].isin(OBJECTIVES).all():
        raise ValueError(
            "Invalid campaign objective detected."
        )

    if (
        campaigns["end_date"]
        < campaigns["start_date"]
    ).any():
        raise ValueError(
            "Campaign end date occurs before "
            "campaign start date."
        )

    print(
        f"[MARKETING] Campaign validation passed — "
        f"{len(campaigns):,} campaigns."
    )


# ============================================================
# EXPOSURE VALIDATION
# ============================================================

def validate_exposures(
    exposures: pd.DataFrame,
    campaigns: pd.DataFrame,
    population: pd.DataFrame,
) -> None:

    required_columns = {
        "campaign_exposure_id",
        "campaign_id",
        "session_id",
        "anonymous_id",
        "customer_id",
        "channel",
        "exposure_timestamp",
        "exposure_outcome",
    }

    missing = (
        required_columns
        - set(exposures.columns)
    )

    if missing:
        raise ValueError(
            f"Missing exposure columns: "
            f"{sorted(missing)}"
        )

    if len(exposures) != TARGET_EXPOSURES:
        raise ValueError(
            f"Expected {TARGET_EXPOSURES:,} exposures, "
            f"generated {len(exposures):,}."
        )

    if exposures[
        "campaign_exposure_id"
    ].duplicated().any():
        raise ValueError(
            "Duplicate campaign_exposure_id values."
        )

    valid_campaign_ids = set(
        campaigns["campaign_id"].astype(str)
    )

    if not exposures[
        "campaign_id"
    ].astype(str).isin(
        valid_campaign_ids
    ).all():
        raise ValueError(
            "Invalid campaign_id values detected."
        )

    valid_session_ids = set(
        population["session_id"].astype(str)
    )

    if not exposures[
        "session_id"
    ].astype(str).isin(
        valid_session_ids
    ).all():
        raise ValueError(
            "Invalid session_id values detected."
        )

    if not exposures[
        "channel"
    ].isin(CHANNELS).all():
        raise ValueError(
            "Invalid exposure channel detected."
        )

    if not exposures[
        "exposure_outcome"
    ].isin(EXPOSURE_OUTCOMES).all():
        raise ValueError(
            "Invalid exposure outcome detected."
        )

    exposures["exposure_timestamp"] = (
        pd.to_datetime(
            exposures["exposure_timestamp"],
            errors="coerce",
        )
    )

    if exposures[
        "exposure_timestamp"
    ].isna().any():
        raise ValueError(
            "Null exposure timestamps detected."
        )

    campaign_bounds = campaigns[
        [
            "campaign_id",
            "start_date",
            "end_date",
        ]
    ].copy()

    campaign_bounds["campaign_id"] = (
        campaign_bounds[
            "campaign_id"
        ].astype(str)
    )

    merged = exposures.merge(
        campaign_bounds,
        on="campaign_id",
        how="left",
        validate="many_to_one",
    )

    outside_campaign = (
        (
            merged["exposure_timestamp"]
            < merged["start_date"]
        )
        |
        (
            merged["exposure_timestamp"]
            > merged["end_date"]
        )
    )

    if outside_campaign.any():
        raise ValueError(
            "Exposure timestamp occurs outside "
            "campaign period."
        )

    print(
        f"[MARKETING] Exposure validation passed — "
        f"{len(exposures):,} exposures."
    )


# ============================================================
# DISTRIBUTION VALIDATION
# ============================================================

def validate_channel_distribution(
    campaigns: pd.DataFrame,
) -> None:

    counts = (
        campaigns["channel"]
        .value_counts(normalize=True)
    )

    expected = {
        "email": 0.25,
        "social": 0.25,
        "search": 0.20,
        "display": 0.15,
        "push": 0.15,
    }

    for channel, target in expected.items():

        actual = float(
            counts.get(
                channel,
                0.0,
            )
        )

        if abs(actual - target) > 0.12:
            raise ValueError(
                "Campaign channel distribution "
                f"outside reasonable range: "
                f"{channel}={actual:.2%}, "
                f"target={target:.2%}"
            )

    print(
        "[MARKETING] Channel distribution "
        "validation passed."
    )


# ============================================================
# SUMMARY
# ============================================================

def print_exposure_summary(
    exposures: pd.DataFrame,
) -> None:

    distribution = (
        exposures[
            "exposure_outcome"
        ]
        .value_counts(normalize=True)
        .sort_index()
    )

    print()
    print(
        "[MARKETING] Exposure outcome distribution:"
    )

    for outcome, proportion in (
        distribution.items()
    ):

        print(
            f"    {outcome:<12} "
            f"{proportion:>7.2%}"
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 70)
    print("ORGEE — MARKETING GENERATOR")
    print("=" * 70)

    MARKETING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    rng = np.random.default_rng(
        PRIMARY_SEED + 600
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

    period_start = orders[
        "order_purchase_timestamp"
    ].min()

    period_end = orders[
        "order_purchase_timestamp"
    ].max()

    print(
        f"[MARKETING] Period start: "
        f"{period_start}"
    )

    print(
        f"[MARKETING] Period end:   "
        f"{period_end}"
    )

    campaigns = generate_campaigns(
        period_start,
        period_end,
        rng,
    )

    validate_campaigns(
        campaigns
    )

    validate_channel_distribution(
        campaigns
    )

    sessions = load_behavioral_population()

    population = (
        enrich_population_with_events(
            sessions
        )
    )

    print(
        f"[MARKETING] Active marketing population: "
        f"{len(population):,} sessions."
    )

    exposures = generate_exposures(
        campaigns,
        population,
        rng,
    )

    validate_exposures(
        exposures,
        campaigns,
        population,
    )

    print_exposure_summary(
        exposures
    )

    campaigns.to_csv(
        CAMPAIGNS_OUTPUT,
        index=False,
    )

    exposures.to_csv(
        EXPOSURES_OUTPUT,
        index=False,
    )

    print()
    print(
        f"[MARKETING] Generated "
        f"{len(campaigns):,} campaigns."
    )

    print(
        f"[MARKETING] Generated "
        f"{len(exposures):,} campaign exposures."
    )

    print(
        "[MARKETING] Campaign output:"
    )

    print(
        CAMPAIGNS_OUTPUT
    )

    print(
        "[MARKETING] Exposure output:"
    )

    print(
        EXPOSURES_OUTPUT
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()