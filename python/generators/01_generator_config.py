"""
ORGEE — Enterprise Generation Configuration

Project: Omnichannel Retail & Growth Experimentation Engine
Project Code: ORGEE
Phase: Phase 2 — Hybrid Data Engineering

Source:
    Document 7 — Enterprise Generation Configuration
"""

# ============================================================
# GLOBAL REPRODUCIBILITY
# ============================================================

PRIMARY_SEED = 2026


# ============================================================
# PUBLIC OLIST REFERENCE POPULATIONS
# ============================================================

PUBLIC_POPULATIONS = {
    "customers": 99_441,
    "products": 32_951,
    "sellers": 3_095,
    "orders": 99_441,
    "order_items": 112_650,
    "payments": 103_886,
    "reviews": 99_224,
    "geolocation": 738_332,
    "category_translation": 71,
}


# ============================================================
# ENTERPRISE TARGET VOLUMES
# ============================================================

TARGET_VOLUMES = {
    "sessions": 500_000,
    "events": 3_000_000,
    "marketing_campaigns": 50,
    "campaign_exposures": 1_000_000,
    "inventory_observations": 1_000_000,
    "experiments": 3,
}


# ============================================================
# CUSTOMER PARTICIPATION
# ============================================================

CUSTOMER_ACTIVITY_SEGMENTS = {
    "highly_active": 0.10,
    "active": 0.25,
    "moderate": 0.40,
    "low_activity": 0.25,
}


# ============================================================
# SESSION CONFIGURATION
# ============================================================

SESSION_TYPE_DISTRIBUTION = {
    "short": 0.35,
    "medium": 0.45,
    "long": 0.20,
}


# ============================================================
# DEVICE CONFIGURATION
# ============================================================

DEVICE_DISTRIBUTION = {
    "mobile": 0.55,
    "desktop": 0.35,
    "tablet": 0.10,
}

DEVICE_TYPES = (
    "mobile",
    "desktop",
    "tablet",
)


# ============================================================
# PLATFORM CONFIGURATION
# ============================================================

PLATFORM_DISTRIBUTION = {
    "web": 0.50,
    "mobile_app": 0.40,
    "desktop": 0.10,
}

PLATFORM_TYPES = (
    "web",
    "mobile_app",
    "desktop",
)


# ============================================================
# EVENT CONFIGURATION
# ============================================================

EVENT_TYPES = (
    "session_start",
    "search",
    "product_view",
    "add_to_cart",
    "remove_from_cart",
    "checkout_start",
    "login",
    "purchase_interaction",
)
# NOTE (fix): recommendation_impression / recommendation_click were
# removed from the generic Events vocabulary. Per
# 04_enterprise_data_requirements.md section 8/13, recommendation
# interactions must live only in recommendation_events.csv, not in
# events.csv. They remain defined in RECOMMENDATION_EVENT_TYPES below
# for the dedicated recommendation generator.


# ============================================================
# CUSTOMER JOURNEY / FUNNEL TRANSITIONS
# ============================================================

FUNNEL_TRANSITION_PROBABILITIES = {
    "session_to_search_or_browse": 0.70,
    "search_or_browse_to_product_view": 0.75,
    "product_view_to_add_to_cart": 0.18,
    "add_to_cart_to_checkout": 0.60,
    "checkout_to_purchase_interaction": 0.70,
}


# ============================================================
# LOGIN CONFIGURATION
# ============================================================

LOGIN_CAPABLE_SESSION_RATE = 0.45
# FIX (sizing): raised from 0.25. With sessions now correctly
# starting anonymous (see 04_generate_sessions.py fix), the true
# session-level identification rate depends on both this rate AND
# IDENTITY_LINK_RATE below. 0.25 combined with a 20-25% link rate
# produced only ~3.8% of sessions ever getting identified, which
# starved the Phase 8 recommendation experiment of eligible sample
# (968 sessions). 0.45 is still well under half of sessions, i.e.
# most traffic remains anonymous, matching realistic e-commerce
# return-visitor behavior.

IDENTITY_LINK_RATE_MIN = 0.55
IDENTITY_LINK_RATE_MAX = 0.65
# FIX (sizing): raised from 0.20-0.25. This is the share of
# login-capable sessions that actually complete a successful login
# and get linked. Combined with the rate above, this targets a
# session identification rate in the mid-teens to ~20% overall,
# giving Phase 8 a workable sample size while keeping the majority
# of traffic anonymous.


# ============================================================
# MARKETING CAMPAIGN CONFIGURATION
# ============================================================

CAMPAIGN_CHANNEL_DISTRIBUTION = {
    "email": 0.25,
    "social": 0.25,
    "search": 0.20,
    "display": 0.15,
    "push": 0.15,
}

CAMPAIGN_CHANNELS = (
    "email",
    "social",
    "search",
    "display",
    "push",
)

CAMPAIGN_OBJECTIVES = (
    "acquisition",
    "conversion",
    "retention",
    "engagement",
    "promotion",
)


# ============================================================
# CAMPAIGN EXPOSURE / MARKETING FUNNEL
# ============================================================

CAMPAIGN_EXPOSURE_OUTCOMES = (
    "impression",
    "click",
    "conversion",
)

MARKETING_FUNNEL_PROBABILITIES = {
    "exposure_to_engagement": 0.10,
    "engagement_to_conversion": 0.08,
}


# ============================================================
# INVENTORY CONFIGURATION
# ============================================================

INVENTORY_LOCATION_COUNT = 20

INVENTORY_STATUSES = (
    "in_stock",
    "low_stock",
    "out_of_stock",
)

INVENTORY_MIN_QUANTITY = 0


# ============================================================
# EXPERIMENT CONFIGURATION
# ============================================================

EXPERIMENT_COUNT = 3

EXPERIMENT_PRIMARY_METRIC = "purchase_conversion_rate"

EXPERIMENT_VARIANTS = (
    "control",
    "treatment",
)

EXPERIMENT_ALLOCATION = {
    "control": 0.50,
    "treatment": 0.50,
}

PRIMARY_RECOMMENDATION_EXPERIMENT = {
    "control": "Top Sellers Recommendations",
    "treatment": "Personalized Content-Based Recommendations",
}


# ============================================================
# RECOMMENDATION CONFIGURATION
# ============================================================

RECOMMENDATION_EVENT_TYPES = (
    "recommendation_impression",
    "recommendation_click",
    "recommendation_conversion",
)

RECOMMENDATION_FUNNEL_PROBABILITIES = {
    "impression_to_click": 0.12,
    "click_to_purchase": 0.08,
}


# ============================================================
# TEMPORAL CONFIGURATION
# ============================================================

TEMPORAL_PERIOD_SOURCE = "processed_public_orders_observation_period"


# ============================================================
# SYNTHETIC IDENTIFIERS
# ============================================================

SYNTHETIC_IDENTIFIER_PREFIXES = {
    "anonymous_id": "anon_",
    "session_id": "sess_",
    "campaign_id": "camp_",
    "campaign_exposure_id": "exposure_",
    "inventory_observation_id": "inv_",
    "experiment_id": "exp_",
    "experiment_assignment_id": "assign_",
    "recommendation_event_id": "rec_",
}


# ============================================================
# PUBLIC IDENTIFIERS — NEVER OVERWRITE
# ============================================================

PUBLIC_IDENTIFIER_FIELDS = (
    "customer_id",
    "product_id",
    "order_id",
    "seller_id",
)


# ============================================================
# GENERATION ORDER
# ============================================================

GENERATION_ORDER = (
    "customer_reference",
    "sessions",
    "events",
    "identity_links",
    "marketing_campaigns",
    "campaign_exposures",
    "inventory",
    "experiments",
    "experiment_assignments",
    "recommendation_events",
)


# ============================================================
# ENTITY TARGETS / DERIVED ENTITIES
# ============================================================

DERIVED_VOLUME_ENTITIES = (
    "identity_links",
    "experiment_assignments",
    "recommendation_events",
)


# ============================================================
# VALIDATION GATES
# ============================================================

VALIDATION_GATES = (
    "schema",
    "grain",
    "uniqueness",
    "completeness",
    "referential_integrity",
    "temporal_integrity",
    "distribution",
    "business_logic",
    "integration_readiness",
)


# ============================================================
# BEHAVIORAL RULES
# ============================================================

REQUIRE_FUNNEL_DROPOFF = True
REQUIRE_NON_UNIFORM_DISTRIBUTIONS = True
REQUIRE_REPRODUCIBILITY = True
ALLOW_FABRICATED_BUSINESS_RESULTS = False
ALLOW_PUBLIC_IDENTIFIER_OVERWRITE = False


# ============================================================
# ENTITY GRAINS
# ============================================================

ENTITY_GRAINS = {
    "sessions": "one row per session",
    "events": "one row per customer behavioral event",
    "campaign_exposures": (
        "one row per customer_or_anonymous_identity per campaign exposure"
    ),
    "inventory_observations": "one row per inventory observation",
    "experiment_assignments": (
        "one row per experimental unit per experiment"
    ),
    "recommendation_events": "one row per recommendation interaction",
}


# ============================================================
# IDENTITY RULES
# ============================================================

ANONYMOUS_ID_FORMAT = "anon_<unique_identifier>"

IDENTITY_LINK_REQUIREMENTS = (
    "valid_customer_id",
    "valid_anonymous_id",
    "valid_session_id",
    "valid_login_timestamp",
    "valid_temporal_ordering",
)


# ============================================================
# EXPERIMENT RULES
# ============================================================

EXPERIMENTAL_UNIT = "customer_id"

ONE_PRIMARY_VARIANT_PER_EXPERIMENT = True

ASSIGNMENT_MUST_FALL_WITHIN_EXPERIMENT_PERIOD = True


# ============================================================
# RECOMMENDATION RULES
# ============================================================

RECOMMENDATION_REQUIRED_REFERENCES = (
    "customer_or_anonymous_identity",
    "session_id",
    "product_id",
    "experiment_id_where_applicable",
    "variant_id_where_applicable",
    "timestamp",
)


# ============================================================
# TEMPORAL RULES
# ============================================================

TEMPORAL_RULES = (
    "timestamps_within_configured_period",
    "event_sequence_ordering",
    "session_start_before_session_end",
    "campaign_exposure_within_campaign_period",
    "experiment_assignment_within_experiment_period",
    "login_before_authenticated_activity",
    "recommendation_click_after_impression",
    "recommendation_conversion_after_interaction",
)


# ============================================================
# REPRODUCIBLE SUB-SEEDS
# ============================================================

SUB_SEED_NAMES = (
    "sessions",
    "events",
    "marketing",
    "inventory",
    "experiments",
    "recommendations",
)