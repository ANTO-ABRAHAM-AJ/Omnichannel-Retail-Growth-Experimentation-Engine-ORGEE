"""
ORGEE — Cross-Entity Validation

Validates relationships across the ORGEE enterprise datasets.

This validation does NOT generate or modify data.
It verifies that independently generated entities remain
consistent when connected together.

Entities checked:

    Public Customers
    Public Products
    Enterprise Sessions
    Enterprise Events
    Identity Links
    Marketing Campaigns
    Marketing Exposures
    Experiments
    Experiment Assignments
    Recommendation Events
    Inventory Observations
"""

from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PUBLIC_DIR = (
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

CUSTOMERS_FILE = (
    PUBLIC_DIR
    / "olist_customers_dataset.csv"
)

PRODUCTS_FILE = (
    PUBLIC_DIR
    / "olist_products_dataset.csv"
)

SESSIONS_FILE = (
    ENTERPRISE_DIR
    / "sessions"
    / "sessions.csv"
)

EVENTS_FILE = (
    ENTERPRISE_DIR
    / "events"
    / "events.csv"
)

IDENTITY_FILE = (
    ENTERPRISE_DIR
    / "identity"
    / "identity_links.csv"
)

CAMPAIGNS_FILE = (
    ENTERPRISE_DIR
    / "marketing"
    / "campaigns.csv"
)

EXPOSURES_FILE = (
    ENTERPRISE_DIR
    / "marketing"
    / "campaign_exposures.csv"
)

EXPERIMENTS_FILE = (
    ENTERPRISE_DIR
    / "experiments"
    / "experiments.csv"
)

ASSIGNMENTS_FILE = (
    ENTERPRISE_DIR
    / "experiments"
    / "experiment_assignments.csv"
)

RECOMMENDATIONS_FILE = (
    ENTERPRISE_DIR
    / "recommendations"
    / "recommendation_events.csv"
)

INVENTORY_FILE = (
    ENTERPRISE_DIR
    / "inventory"
    / "inventory_observations.csv"
)


# ============================================================
# HELPERS
# ============================================================

def load_csv(
    path: Path,
    name: str,
    **kwargs,
) -> pd.DataFrame:

    print(
        f"[CROSS ENTITY] Loading {name}..."
    )

    if not path.exists():
        raise FileNotFoundError(
            f"{name} file not found:\n{path}"
        )

    df = pd.read_csv(
        path,
        **kwargs,
    )

    print(
        f"[CROSS ENTITY] Loaded "
        f"{len(df):,} {name}."
    )

    return df


def passed(message: str) -> None:

    print(
        f"[CROSS ENTITY VALIDATION PASSED] "
        f"{message}"
    )


def fail(message: str) -> None:

    raise ValueError(
        f"[CROSS ENTITY VALIDATION FAILED] "
        f"{message}"
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    customers = load_csv(
        CUSTOMERS_FILE,
        "public customers",
        usecols=["customer_id"],
    )

    products = load_csv(
        PRODUCTS_FILE,
        "public products",
        usecols=["product_id"],
    )

    sessions = load_csv(
        SESSIONS_FILE,
        "enterprise sessions",
        parse_dates=[
            "session_start_timestamp",
            "session_end_timestamp",
        ],
    )

    events = load_csv(
        EVENTS_FILE,
        "enterprise events",
        parse_dates=[
            "event_timestamp",
        ],
    )

    identity = load_csv(
        IDENTITY_FILE,
        "identity links",
        parse_dates=[
            "link_timestamp",
        ],
    )

    campaigns = load_csv(
        CAMPAIGNS_FILE,
        "marketing campaigns",
        parse_dates=[
            "start_date",
            "end_date",
        ],
    )

    exposures = load_csv(
        EXPOSURES_FILE,
        "campaign exposures",
        parse_dates=[
            "exposure_timestamp",
        ],
    )

    experiments = load_csv(
        EXPERIMENTS_FILE,
        "experiments",
        parse_dates=[
            "start_timestamp",
            "end_timestamp",
        ],
    )

    assignments = load_csv(
        ASSIGNMENTS_FILE,
        "experiment assignments",
        parse_dates=[
            "assignment_timestamp",
        ],
    )

    recommendations = load_csv(
        RECOMMENDATIONS_FILE,
        "recommendation events",
        parse_dates=[
            "event_timestamp",
        ],
    )

    inventory = load_csv(
        INVENTORY_FILE,
        "inventory observations",
        parse_dates=[
            "observation_timestamp",
        ],
    )

    return (
        customers,
        products,
        sessions,
        events,
        identity,
        campaigns,
        exposures,
        experiments,
        assignments,
        recommendations,
        inventory,
    )


# ============================================================
# NORMALIZE IDENTIFIERS
# ============================================================

def normalize_ids(
    customers,
    products,
    sessions,
    events,
    identity,
    campaigns,
    exposures,
    experiments,
    assignments,
    recommendations,
    inventory,
):

    for df, columns in [

        (
            customers,
            ["customer_id"],
        ),

        (
            products,
            ["product_id"],
        ),

        (
            sessions,
            [
                "session_id",
                "anonymous_id",
                "customer_id",
            ],
        ),

        (
            events,
            [
                "session_id",
                "anonymous_id",
                "customer_id",
                "product_id",
            ],
        ),

        (
            identity,
            [
                "identity_link_id",
                "anonymous_id",
                "customer_id",
                "session_id",
            ],
        ),

        (
            campaigns,
            ["campaign_id"],
        ),

        (
            exposures,
            [
                "campaign_exposure_id",
                "campaign_id",
                "session_id",
                "anonymous_id",
                "customer_id",
            ],
        ),

        (
            experiments,
            ["experiment_id"],
        ),

        (
            assignments,
            [
                "experiment_id",
                "customer_id",
            ],
        ),

        (
            recommendations,
            [
                "recommendation_event_id",
                "session_id",
                "anonymous_id",
                "customer_id",
                "experiment_id",
                "product_id",
            ],
        ),

        (
            inventory,
            [
                "inventory_observation_id",
                "product_id",
                "inventory_location_id",
            ],
        ),

    ]:

        for column in columns:

            if column in df.columns:

                df[column] = (
                    df[column]
                    .astype("string")
                    .str.strip()
                )


# ============================================================
# PUBLIC CUSTOMER INTEGRITY
# ============================================================

def validate_public_customer_links(
    customers,
    sessions,
    events,
    identity,
    exposures,
    assignments,
    recommendations,
):

    print()
    print(
        "[CROSS ENTITY] Checking public customer "
        "relationships..."
    )

    valid_customers = set(
        customers["customer_id"]
        .dropna()
    )

    # --------------------------------------------------------
    # Sessions
    # --------------------------------------------------------

    session_customer_mask = (
        sessions["customer_id"].notna()
    )

    invalid = (
        ~sessions.loc[
            session_customer_mask,
            "customer_id",
        ].isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Sessions contain customer IDs "
            "not present in public customers."
        )

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    event_customer_mask = (
        events["customer_id"].notna()
    )

    invalid = (
        ~events.loc[
            event_customer_mask,
            "customer_id",
        ].isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Events contain customer IDs "
            "not present in public customers."
        )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    identity_customer_mask = (
        identity["customer_id"].notna()
    )

    invalid = (
        ~identity.loc[
            identity_customer_mask,
            "customer_id",
        ].isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Identity links contain customer IDs "
            "not present in public customers."
        )

    # --------------------------------------------------------
    # Marketing
    # --------------------------------------------------------

    exposure_customer_mask = (
        exposures["customer_id"].notna()
    )

    invalid = (
        ~exposures.loc[
            exposure_customer_mask,
            "customer_id",
        ].isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Campaign exposures contain customer IDs "
            "not present in public customers."
        )

    # --------------------------------------------------------
    # Experiments
    # --------------------------------------------------------

    invalid = (
        ~assignments["customer_id"]
        .isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Experiment assignments contain customer IDs "
            "not present in public customers."
        )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    invalid = (
        ~recommendations["customer_id"]
        .isin(valid_customers)
    )

    if invalid.any():
        fail(
            "Recommendation events contain customer IDs "
            "not present in public customers."
        )

    passed(
        "Public customer referential relationships passed."
    )


# ============================================================
# PUBLIC PRODUCT INTEGRITY
# ============================================================

def validate_product_links(
    products,
    events,
    inventory,
    recommendations,
):

    print(
        "[CROSS ENTITY] Checking public product "
        "relationships..."
    )

    valid_products = set(
        products["product_id"]
        .dropna()
    )

    # Events
    mask = events["product_id"].notna()

    if not (
        events.loc[
            mask,
            "product_id",
        ]
        .isin(valid_products)
        .all()
    ):
        fail(
            "Events contain product IDs "
            "not present in public products."
        )

    # Inventory
    if not (
        inventory["product_id"]
        .isin(valid_products)
        .all()
    ):
        fail(
            "Inventory contains product IDs "
            "not present in public products."
        )

    # Recommendations
    if not (
        recommendations["product_id"]
        .isin(valid_products)
        .all()
    ):
        fail(
            "Recommendation events contain product IDs "
            "not present in public products."
        )

    passed(
        "Public product referential relationships passed."
    )


# ============================================================
# SESSION ↔ EVENT
# ============================================================

def validate_session_event_relationship(
    sessions,
    events,
):

    print(
        "[CROSS ENTITY] Checking session ↔ event "
        "relationships..."
    )

    session_reference = (
        sessions[
            [
                "session_id",
                "anonymous_id",
                "customer_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ]
        .drop_duplicates(
            "session_id"
        )
        .set_index(
            "session_id"
        )
    )

    event_session_ids = set(
        events["session_id"]
    )

    valid_session_ids = set(
        session_reference.index
    )

    if not event_session_ids.issubset(
        valid_session_ids
    ):
        fail(
            "Events reference sessions "
            "that do not exist."
        )

    # --------------------------------------------------------
    # Check anonymous identity consistency
    # --------------------------------------------------------

    event_session_check = events.merge(
        session_reference,
        left_on="session_id",
        right_index=True,
        how="left",
        suffixes=(
            "_event",
            "_session",
        ),
        validate="many_to_one",
    )

    if not (
        event_session_check[
            "anonymous_id_event"
        ]
        == event_session_check[
            "anonymous_id_session"
        ]
    ).all():
        fail(
            "Event anonymous_id does not match "
            "its parent session."
        )

    # --------------------------------------------------------
    # Customer consistency
    #
    # Only compare authenticated event customer IDs.
    # --------------------------------------------------------

    authenticated = (
        event_session_check[
            "customer_id_event"
        ].notna()
    )

    customer_mismatch = (
        event_session_check.loc[
            authenticated,
            "customer_id_event",
        ]
        !=
        event_session_check.loc[
            authenticated,
            "customer_id_session",
        ]
    )

    if customer_mismatch.any():
        fail(
            "Authenticated event customer_id does not "
            "match parent session customer_id."
        )

    passed(
        "Session ↔ event relationship passed."
    )


# ============================================================
# IDENTITY ↔ SESSION
# ============================================================

def validate_identity_session_relationship(
    sessions,
    identity,
):

    print(
        "[CROSS ENTITY] Checking identity ↔ session "
        "relationships..."
    )

    session_reference = (
        sessions[
            [
                "session_id",
                "anonymous_id",
                "customer_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ]
        .drop_duplicates(
            "session_id"
        )
    )

    merged = identity.merge(
        session_reference,
        on="session_id",
        how="left",
        suffixes=(
            "_identity",
            "_session",
        ),
        validate="many_to_one",
    )

    if merged[
        "anonymous_id_session"
    ].isna().any():
        fail(
            "Identity links reference "
            "non-existent sessions."
        )

    if not (
        merged["anonymous_id_identity"]
        ==
        merged["anonymous_id_session"]
    ).all():
        fail(
            "Identity-link anonymous_id does not "
            "match the corresponding session."
        )

    identity_customer = (
        merged["customer_id_identity"]
        .notna()
    )

    mismatch = (
        merged.loc[
            identity_customer,
            "customer_id_identity",
        ]
        !=
        merged.loc[
            identity_customer,
            "customer_id_session",
        ]
    )

    if mismatch.any():
        fail(
            "Identity-link customer_id does not "
            "match the corresponding session."
        )

    # Timestamp must belong to session
    outside = (
        (
            merged["link_timestamp"]
            <
            merged["session_start_timestamp"]
        )
        |
        (
            merged["link_timestamp"]
            >
            merged["session_end_timestamp"]
        )
    )

    if outside.any():
        fail(
            "Identity-link timestamp falls outside "
            "the linked session."
        )

    passed(
        "Identity ↔ session relationship passed."
    )


# ============================================================
# MARKETING ↔ CAMPAIGN
# ============================================================

def validate_marketing_relationships(
    campaigns,
    exposures,
    sessions,
):

    print(
        "[CROSS ENTITY] Checking marketing ↔ campaign "
        "relationships..."
    )

    campaign_reference = (
        campaigns[
            [
                "campaign_id",
                "channel",
                "start_date",
                "end_date",
            ]
        ]
        .drop_duplicates(
            "campaign_id"
        )
    )

    merged = exposures.merge(
        campaign_reference,
        on="campaign_id",
        how="left",
        suffixes=(
            "_exposure",
            "_campaign",
        ),
        validate="many_to_one",
    )

    if merged[
        "channel_campaign"
    ].isna().any():
        fail(
            "Campaign exposures reference "
            "non-existent campaigns."
        )

    if not (
        merged["channel_exposure"]
        ==
        merged["channel_campaign"]
    ).all():
        fail(
            "Campaign exposure channel does not "
            "match campaign channel."
        )

    outside_campaign = (
        (
            merged["exposure_timestamp"]
            <
            merged["start_date"]
        )
        |
        (
            merged["exposure_timestamp"]
            >
            merged["end_date"]
        )
    )

    if outside_campaign.any():
        fail(
            "Campaign exposure timestamp falls "
            "outside campaign period."
        )

    # --------------------------------------------------------
    # Exposure ↔ session
    # --------------------------------------------------------

    session_reference = (
        sessions[
            [
                "session_id",
                "anonymous_id",
                "customer_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ]
        .drop_duplicates(
            "session_id"
        )
    )

    merged = exposures.merge(
        session_reference,
        on="session_id",
        how="left",
        suffixes=(
            "_exposure",
            "_session",
        ),
        validate="many_to_one",
    )

    if merged[
        "anonymous_id_session"
    ].isna().any():
        fail(
            "Campaign exposures reference "
            "non-existent sessions."
        )

    if not (
        merged["anonymous_id_exposure"]
        ==
        merged["anonymous_id_session"]
    ).all():
        fail(
            "Campaign exposure anonymous_id does "
            "not match its session."
        )

    exposure_customer = (
        merged["customer_id_exposure"].notna()
    )

    customer_mismatch = (
        merged.loc[
            exposure_customer,
            "customer_id_exposure",
        ]
        !=
        merged.loc[
            exposure_customer,
            "customer_id_session",
        ]
    )

    if customer_mismatch.any():
        fail(
            "Campaign exposure customer_id does "
            "not match its session."
        )

    outside_session = (
        (
            merged["exposure_timestamp"]
            <
            merged["session_start_timestamp"]
        )
        |
        (
            merged["exposure_timestamp"]
            >
            merged["session_end_timestamp"]
        )
    )

    if outside_session.any():
        fail(
            "Campaign exposure timestamp falls "
            "outside session period."
        )

    passed(
        "Marketing ↔ campaign ↔ session "
        "relationships passed."
    )


# ============================================================
# EXPERIMENT ↔ ASSIGNMENT
# ============================================================

def validate_experiment_relationships(
    experiments,
    assignments,
):

    print(
        "[CROSS ENTITY] Checking experiment ↔ assignment "
        "relationships..."
    )

    experiment_reference = (
        experiments[
            [
                "experiment_id",
                "start_timestamp",
                "end_timestamp",
            ]
        ]
        .drop_duplicates(
            "experiment_id"
        )
    )

    merged = assignments.merge(
        experiment_reference,
        on="experiment_id",
        how="left",
        validate="many_to_one",
    )

    if merged[
        "start_timestamp"
    ].isna().any():
        fail(
            "Experiment assignments reference "
            "non-existent experiments."
        )

    outside = (
        (
            merged["assignment_timestamp"]
            <
            merged["start_timestamp"]
        )
        |
        (
            merged["assignment_timestamp"]
            >
            merged["end_timestamp"]
        )
    )

    if outside.any():
        fail(
            "Experiment assignment occurs outside "
            "experiment period."
        )

    # Every experiment should have both variants
    variant_counts = (
        assignments.groupby(
            [
                "experiment_id",
                "variant",
            ]
        )
        .size()
    )

    for experiment_id in experiments[
        "experiment_id"
    ]:

        for variant in (
            "control",
            "treatment",
        ):

            if (
                experiment_id,
                variant,
            ) not in variant_counts.index:

                fail(
                    f"{experiment_id} has no "
                    f"{variant} assignments."
                )

    passed(
        "Experiment ↔ assignment relationship passed."
    )


# ============================================================
# ASSIGNMENT ↔ RECOMMENDATION
# ============================================================

def validate_recommendation_relationships(
    sessions,
    experiments,
    assignments,
    recommendations,
):

    print(
        "[CROSS ENTITY] Checking assignment ↔ "
        "recommendation relationships..."
    )

    # --------------------------------------------------------
    # Recommendation experiment
    # --------------------------------------------------------

    valid_experiments = set(
        experiments["experiment_id"]
    )

    if not (
        recommendations["experiment_id"]
        .isin(valid_experiments)
        .all()
    ):
        fail(
            "Recommendation events reference "
            "unknown experiments."
        )

    # --------------------------------------------------------
    # Exact assignment lookup
    # --------------------------------------------------------

    assignment_reference = (
        assignments[
            [
                "customer_id",
                "experiment_id",
                "variant",
                "assignment_timestamp",
            ]
        ]
        .drop_duplicates(
            [
                "customer_id",
                "experiment_id",
            ]
        )
    )

    merged = recommendations.merge(
        assignment_reference,
        on=[
            "customer_id",
            "experiment_id",
        ],
        how="left",
        suffixes=(
            "_recommendation",
            "_assignment",
        ),
        validate="many_to_one",
    )

    if merged[
        "variant_assignment"
    ].isna().any():
        fail(
            "Recommendation events contain "
            "customer/experiment combinations "
            "without assignments."
        )

    if not (
        merged["variant_recommendation"]
        ==
        merged["variant_assignment"]
    ).all():
        fail(
            "Recommendation variant does not "
            "match experiment assignment."
        )

    if (
        merged["event_timestamp"]
        <
        merged["assignment_timestamp"]
    ).any():
        fail(
            "Recommendation event occurs before "
            "experiment assignment."
        )

    # --------------------------------------------------------
    # Session consistency
    # --------------------------------------------------------

    session_reference = (
        sessions[
            [
                "session_id",
                "anonymous_id",
                "customer_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ]
        .drop_duplicates(
            "session_id"
        )
    )

    merged = recommendations.merge(
        session_reference,
        on="session_id",
        how="left",
        suffixes=(
            "_recommendation",
            "_session",
        ),
        validate="many_to_one",
    )

    if merged[
        "anonymous_id_session"
    ].isna().any():
        fail(
            "Recommendation events reference "
            "non-existent sessions."
        )

    if not (
        merged["anonymous_id_recommendation"]
        ==
        merged["anonymous_id_session"]
    ).all():
        fail(
            "Recommendation anonymous_id does "
            "not match its session."
        )

    if not (
        merged["customer_id_recommendation"]
        ==
        merged["customer_id_session"]
    ).all():
        fail(
            "Recommendation customer_id does "
            "not match its session."
        )

    if (
        merged["event_timestamp"]
        <
        merged["session_start_timestamp"]
    ).any():

        fail(
            "Recommendation event occurs before "
            "session start."
        )

    if (
        merged["event_timestamp"]
        >
        merged["session_end_timestamp"]
    ).any():

        fail(
            "Recommendation event occurs after "
            "session end."
        )

    passed(
        "Assignment ↔ recommendation ↔ session "
        "relationships passed."
    )


# ============================================================
# INVENTORY ↔ PRODUCT
# ============================================================

def validate_inventory_relationship(
    products,
    inventory,
):

    print(
        "[CROSS ENTITY] Checking inventory ↔ "
        "product relationship..."
    )

    valid_products = set(
        products["product_id"]
    )

    if not (
        inventory["product_id"]
        .isin(valid_products)
        .all()
    ):
        fail(
            "Inventory contains products that "
            "do not exist in public product data."
        )

    pair_counts = (
        inventory.groupby(
            [
                "product_id",
                "inventory_location_id",
            ]
        )
        .size()
    )

    if pair_counts.empty:
        fail(
            "No inventory product-location "
            "relationships found."
        )

    passed(
        "Inventory ↔ product relationship passed."
    )


# ============================================================
# GLOBAL TEMPORAL CONSISTENCY
# ============================================================

def validate_temporal_relationships(
    sessions,
    events,
    exposures,
    recommendations,
):

    print(
        "[CROSS ENTITY] Checking global temporal "
        "relationships..."
    )

    # Events
    event_bounds = events.merge(
        sessions[
            [
                "session_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ],
        on="session_id",
        how="left",
        validate="many_to_one",
    )

    if (
        event_bounds["event_timestamp"]
        < event_bounds["session_start_timestamp"]
    ).any():

        fail(
            "Event occurs before parent session."
        )

    if (
        event_bounds["event_timestamp"]
        > event_bounds["session_end_timestamp"]
    ).any():

        fail(
            "Event occurs after parent session."
        )

    # Marketing
    exposure_bounds = exposures.merge(
        sessions[
            [
                "session_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ],
        on="session_id",
        how="left",
        validate="many_to_one",
    )

    if (
        exposure_bounds["exposure_timestamp"]
        < exposure_bounds["session_start_timestamp"]
    ).any():

        fail(
            "Marketing exposure occurs before "
            "parent session."
        )

    if (
        exposure_bounds["exposure_timestamp"]
        > exposure_bounds["session_end_timestamp"]
    ).any():

        fail(
            "Marketing exposure occurs after "
            "parent session."
        )

    # Recommendations
    recommendation_bounds = recommendations.merge(
        sessions[
            [
                "session_id",
                "session_start_timestamp",
                "session_end_timestamp",
            ]
        ],
        on="session_id",
        how="left",
        validate="many_to_one",
    )

    if (
        recommendation_bounds["event_timestamp"]
        < recommendation_bounds[
            "session_start_timestamp"
        ]
    ).any():

        fail(
            "Recommendation event occurs before "
            "parent session."
        )

    if (
        recommendation_bounds["event_timestamp"]
        > recommendation_bounds[
            "session_end_timestamp"
        ]
    ).any():

        fail(
            "Recommendation event occurs after "
            "parent session."
        )

    passed(
        "Global temporal relationships passed."
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    customers,
    products,
    sessions,
    events,
    identity,
    campaigns,
    exposures,
    experiments,
    assignments,
    recommendations,
    inventory,
):

    print()
    print(
        "=" * 70
    )

    print(
        "[CROSS ENTITY VALIDATION] SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"Public customers        = "
        f"{len(customers):,}"
    )

    print(
        f"Public products         = "
        f"{len(products):,}"
    )

    print(
        f"Enterprise sessions     = "
        f"{len(sessions):,}"
    )

    print(
        f"Enterprise events       = "
        f"{len(events):,}"
    )

    print(
        f"Identity links          = "
        f"{len(identity):,}"
    )

    print(
        f"Marketing campaigns     = "
        f"{len(campaigns):,}"
    )

    print(
        f"Campaign exposures      = "
        f"{len(exposures):,}"
    )

    print(
        f"Experiments             = "
        f"{len(experiments):,}"
    )

    print(
        f"Experiment assignments  = "
        f"{len(assignments):,}"
    )

    print(
        f"Recommendation events   = "
        f"{len(recommendations):,}"
    )

    print(
        f"Inventory observations  = "
        f"{len(inventory):,}"
    )

    print(
        "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "ORGEE — CROSS-ENTITY VALIDATION"
    )

    print(
        "=" * 70
    )

    (
        customers,
        products,
        sessions,
        events,
        identity,
        campaigns,
        exposures,
        experiments,
        assignments,
        recommendations,
        inventory,
    ) = load_data()

    normalize_ids(
        customers,
        products,
        sessions,
        events,
        identity,
        campaigns,
        exposures,
        experiments,
        assignments,
        recommendations,
        inventory,
    )

    print()

    validate_public_customer_links(
        customers,
        sessions,
        events,
        identity,
        exposures,
        assignments,
        recommendations,
    )

    validate_product_links(
        products,
        events,
        inventory,
        recommendations,
    )

    validate_session_event_relationship(
        sessions,
        events,
    )

    validate_identity_session_relationship(
        sessions,
        identity,
    )

    validate_marketing_relationships(
        campaigns,
        exposures,
        sessions,
    )

    validate_experiment_relationships(
        experiments,
        assignments,
    )

    validate_recommendation_relationships(
        sessions,
        experiments,
        assignments,
        recommendations,
    )

    validate_inventory_relationship(
        products,
        inventory,
    )

    validate_temporal_relationships(
        sessions,
        events,
        exposures,
        recommendations,
    )

    print_summary(
        customers,
        products,
        sessions,
        events,
        identity,
        campaigns,
        exposures,
        experiments,
        assignments,
        recommendations,
        inventory,
    )

    print()
    print(
        "=" * 70
    )

    print(
        "[CROSS ENTITY VALIDATION] COMPLETE — "
        "ALL CHECKS PASSED"
    )

    print(
        "=" * 70
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()