"""
ORGEE — Event Validation

Validates the synthetic enterprise behavioral event dataset.

Checks:
    1. Schema
    2. Required fields
    3. Row count
    4. event_id uniqueness
    5. session referential integrity
    6. customer referential integrity
    7. anonymous identity integrity
    8. product referential integrity
    9. event-type validity
    10. timestamp validity
    11. session temporal integrity
    12. customer/session consistency
    13. anonymous/session consistency
    14. product-event requirements
    15. distribution sanity

ORGEE EVENT IDENTITY RULE
-------------------------

At event level:

    event_id          REQUIRED
    session_id        REQUIRED
    anonymous_id      REQUIRED
    event_type        REQUIRED
    event_timestamp   REQUIRED

    customer_id       OPTIONAL
    product_id        OPTIONAL

A customer_id may legitimately be NULL because
ORGEE supports anonymous behavioral activity.

If customer_id is present:
    - it must exist in the public customer reference
    - it must match the customer associated with the session

If product_id is present:
    - it must exist in the public product reference

Product-related events must contain product_id.
"""


from pathlib import Path

import pandas as pd


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

ENTERPRISE_EVENTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "events"
)

ENTERPRISE_SESSIONS_DIR = (
    PROJECT_ROOT
    / "data"
    / "enterprise"
    / "sessions"
)

EVENTS_FILE = (
    ENTERPRISE_EVENTS_DIR
    / "events.csv"
)

SESSIONS_FILE = (
    ENTERPRISE_SESSIONS_DIR
    / "sessions.csv"
)

CUSTOMERS_FILE = (
    PUBLIC_DATA_DIR
    / "olist_customers_dataset.csv"
)

PRODUCTS_FILE = (
    PUBLIC_DATA_DIR
    / "olist_products_dataset.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_EVENT_COUNT = 3_000_000

CHUNK_SIZE = 250_000


# ============================================================
# VALID EVENT TYPES
# ============================================================

VALID_EVENT_TYPES = {
    "session_start",
    "search",
    "product_view",
    "add_to_cart",
    "remove_from_cart",
    "checkout_start",
    "login",
    "recommendation_impression",
    "recommendation_click",
    "purchase_interaction",
}


# ============================================================
# EVENT TYPES THAT REQUIRE PRODUCT_ID
# ============================================================

PRODUCT_EVENT_TYPES = {
    "product_view",
    "add_to_cart",
    "remove_from_cart",
    "recommendation_impression",
    "recommendation_click",
    "purchase_interaction",
}


# ============================================================
# REQUIRED EVENT COLUMNS
#
# customer_id and product_id are intentionally NOT included.
# They are optional / conditionally populated.
# ============================================================

REQUIRED_COLUMNS = {
    "event_id",
    "session_id",
    "anonymous_id",
    "event_type",
    "event_timestamp",
}


# ============================================================
# CONDITIONAL COLUMNS
# ============================================================

CONDITIONAL_COLUMNS = {
    "customer_id",
    "product_id",
}


# ============================================================
# HELPER
# ============================================================

def fail(message: str) -> None:
    """
    Raise a validation failure.
    """

    raise ValueError(
        f"[EVENT VALIDATION FAILED] {message}"
    )


# ============================================================
# LOAD REFERENCE DATA
# ============================================================

def load_reference_data():
    """
    Load authoritative customer, product, and session
    reference data.
    """

    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    print(
        "[EVENT VALIDATION] "
        "Loading public customers..."
    )

    if not CUSTOMERS_FILE.exists():

        fail(
            f"Customer reference dataset not found:\n"
            f"{CUSTOMERS_FILE}"
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

    customer_ids = set(
        customers[
            "customer_id"
        ]
        .dropna()
    )

    print(
        f"[EVENT VALIDATION] "
        f"Loaded {len(customer_ids):,} "
        f"public customers."
    )


    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    print(
        "[EVENT VALIDATION] "
        "Loading public products..."
    )

    if not PRODUCTS_FILE.exists():

        fail(
            f"Product reference dataset not found:\n"
            f"{PRODUCTS_FILE}"
        )

    products = pd.read_csv(
        PRODUCTS_FILE,
        usecols=[
            "product_id",
        ],
    )

    products["product_id"] = (
        products["product_id"]
        .astype(str)
        .str.strip()
    )

    product_ids = set(
        products[
            "product_id"
        ]
        .dropna()
    )

    print(
        f"[EVENT VALIDATION] "
        f"Loaded {len(product_ids):,} "
        f"public products."
    )


    # --------------------------------------------------------
    # SESSIONS
    # --------------------------------------------------------

    print(
        "[EVENT VALIDATION] "
        "Loading enterprise sessions..."
    )

    if not SESSIONS_FILE.exists():

        fail(
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
    )


    # --------------------------------------------------------
    # NORMALIZE SESSION IDENTIFIERS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SESSION TIMESTAMPS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SESSION UNIQUENESS
    # --------------------------------------------------------

    if sessions[
        "session_id"
    ].duplicated().any():

        fail(
            "Duplicate session_id values found "
            "in sessions."
        )


    # --------------------------------------------------------
    # SESSION ID SET
    # --------------------------------------------------------

    session_ids = set(
        sessions[
            "session_id"
        ]
    )


    print(
        f"[EVENT VALIDATION] "
        f"Loaded {len(session_ids):,} sessions."
    )


    return (
        customer_ids,
        product_ids,
        session_ids,
        sessions,
    )


# ============================================================
# SCHEMA VALIDATION
# ============================================================

def validate_schema() -> list[str]:
    """
    Validate the generated events.csv schema.
    """

    print()
    print(
        "[EVENT VALIDATION] "
        "Checking schema..."
    )

    if not EVENTS_FILE.exists():

        fail(
            f"Events dataset not found:\n"
            f"{EVENTS_FILE}"
        )


    header = pd.read_csv(
        EVENTS_FILE,
        nrows=0,
    )

    columns = list(
        header.columns
    )


    # --------------------------------------------------------
    # REQUIRED COLUMNS
    # --------------------------------------------------------

    missing_required = (
        REQUIRED_COLUMNS
        -
        set(columns)
    )

    if missing_required:

        fail(
            "Missing required event columns: "
            f"{sorted(missing_required)}"
        )


    # --------------------------------------------------------
    # CONDITIONAL COLUMNS
    #
    # These must exist in the schema even though their
    # values can legitimately be NULL.
    # --------------------------------------------------------

    missing_conditional = (
        CONDITIONAL_COLUMNS
        -
        set(columns)
    )

    if missing_conditional:

        fail(
            "Missing conditional event columns: "
            f"{sorted(missing_conditional)}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Schema validation passed."
    )


    return columns


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_events() -> None:

    print("=" * 70)
    print("ORGEE — EVENT VALIDATION")
    print("=" * 70)


    # ========================================================
    # SCHEMA
    # ========================================================

    columns = validate_schema()


    # ========================================================
    # LOAD REFERENCE DATA
    # ========================================================

    (
        customer_ids,
        product_ids,
        session_ids,
        sessions,
    ) = load_reference_data()


    # ========================================================
    # SESSION LOOKUP MAPS
    # ========================================================

    session_customer_map = (
        sessions
        .set_index(
            "session_id"
        )[
            "customer_id"
        ]
        .to_dict()
    )


    session_anonymous_map = (
        sessions
        .set_index(
            "session_id"
        )[
            "anonymous_id"
        ]
        .to_dict()
    )


    session_start_map = (
        sessions
        .set_index(
            "session_id"
        )[
            "session_start_timestamp"
        ]
        .to_dict()
    )


    session_end_map = (
        sessions
        .set_index(
            "session_id"
        )[
            "session_end_timestamp"
        ]
        .to_dict()
    )


    # ========================================================
    # COUNTERS
    # ========================================================

    total_rows = 0

    event_type_counts = {}

    product_linked_count = 0

    customer_linked_count = 0

    anonymous_linked_count = 0

    null_customer_count = 0

    null_product_count = 0

    null_anonymous_count = 0

    session_start_count = 0

    login_count = 0

    recommendation_impression_count = 0

    recommendation_click_count = 0

    purchase_count = 0


    # ========================================================
    # ERROR COLLECTION
    # ========================================================

    invalid_event_types = set()

    invalid_session_ids = set()

    invalid_customer_ids = set()

    invalid_product_ids = set()

    invalid_anonymous_ids = set()

    invalid_timestamps = 0

    timestamp_outside_session = 0

    customer_session_mismatches = 0

    anonymous_session_mismatches = 0

    missing_product_for_product_events = 0


    # ========================================================
    # EVENT ID TRACKING
    # ========================================================

    seen_event_ids = set()


    # ========================================================
    # EVENT LOADING
    # ========================================================

    print()

    print(
        "[EVENT VALIDATION] "
        "Loading events..."
    )

    print(
        f"[EVENT VALIDATION] "
        f"Expected rows: "
        f"{EXPECTED_EVENT_COUNT:,}"
    )


    usecols = [
        "event_id",
        "session_id",
        "anonymous_id",
        "customer_id",
        "product_id",
        "event_type",
        "event_timestamp",
    ]


    # Optional columns are not needed for validation,
    # but the schema is allowed to contain them.

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            EVENTS_FILE,
            usecols=usecols,
            chunksize=CHUNK_SIZE,
            dtype=str,
        ),
        start=1,
    ):

        total_rows += len(
            chunk
        )


        print(
            f"[EVENT VALIDATION] "
            f"Processing chunk "
            f"{chunk_number} — "
            f"{total_rows:,} events..."
        )


        # ====================================================
        # REQUIRED FIELDS
        #
        # IMPORTANT:
        # customer_id and product_id are NOT checked here.
        # NULL is valid for those columns.
        # ====================================================

        for column in [
            "event_id",
            "session_id",
            "anonymous_id",
            "event_type",
            "event_timestamp",
        ]:

            if chunk[
                column
            ].isna().any():

                fail(
                    f"Null values detected in "
                    f"required column '{column}'."
                )


        # ====================================================
        # NORMALIZE IDENTIFIERS
        # ====================================================

        for column in [
            "event_id",
            "session_id",
            "anonymous_id",
            "event_type",
        ]:

            chunk[
                column
            ] = (
                chunk[
                    column
                ]
                .astype(str)
                .str.strip()
            )


        # ====================================================
        # EVENT ID UNIQUENESS
        # ====================================================

        current_event_ids = set(
            chunk[
                "event_id"
            ]
        )


        duplicate_inside_chunk = (
            chunk[
                "event_id"
            ]
            .duplicated()
        )


        if duplicate_inside_chunk.any():

            fail(
                "Duplicate event_id values detected "
                "inside event data."
            )


        overlap = (
            current_event_ids
            &
            seen_event_ids
        )


        if overlap:

            fail(
                "Duplicate event_id values detected "
                "across event chunks."
            )


        seen_event_ids.update(
            current_event_ids
        )


        # ====================================================
        # CUSTOMER ID
        #
        # NULL IS VALID.
        # ====================================================

        customer_mask = (
            chunk[
                "customer_id"
            ].notna()
            &
            chunk[
                "customer_id"
            ].ne("")
            &
            chunk[
                "customer_id"
            ].ne("nan")
            &
            chunk[
                "customer_id"
            ].ne("None")
        )


        customer_values = (
            chunk.loc[
                customer_mask,
                "customer_id",
            ]
            .astype(str)
            .str.strip()
        )


        customer_linked_count += (
            len(customer_values)
        )


        null_customer_count += int(
            (
                ~customer_mask
            ).sum()
        )


        # ----------------------------------------------------
        # Validate only non-null customer IDs.
        # ----------------------------------------------------

        invalid_customers = (
            set(customer_values)
            -
            customer_ids
        )


        invalid_customer_ids.update(
            invalid_customers
        )


        # ====================================================
        # PRODUCT ID
        #
        # NULL IS VALID FOR NON-PRODUCT EVENTS.
        # ====================================================

        product_mask = (
            chunk[
                "product_id"
            ].notna()
            &
            chunk[
                "product_id"
            ].ne("")
            &
            chunk[
                "product_id"
            ].ne("nan")
            &
            chunk[
                "product_id"
            ].ne("None")
        )


        product_values = (
            chunk.loc[
                product_mask,
                "product_id",
            ]
            .astype(str)
            .str.strip()
        )


        product_linked_count += (
            len(product_values)
        )


        null_product_count += int(
            (
                ~product_mask
            ).sum()
        )


        # ----------------------------------------------------
        # Validate only non-null product IDs.
        # ----------------------------------------------------

        invalid_products = (
            set(product_values)
            -
            product_ids
        )


        invalid_product_ids.update(
            invalid_products
        )


        # ====================================================
        # ANONYMOUS ID
        # ====================================================

        anonymous_mask = (
            chunk[
                "anonymous_id"
            ].notna()
            &
            chunk[
                "anonymous_id"
            ].ne("")
            &
            chunk[
                "anonymous_id"
            ].ne("nan")
            &
            chunk[
                "anonymous_id"
            ].ne("None")
        )


        anonymous_values = (
            chunk.loc[
                anonymous_mask,
                "anonymous_id",
            ]
            .astype(str)
            .str.strip()
        )


        anonymous_linked_count += (
            len(anonymous_values)
        )


        null_anonymous_count += int(
            (
                ~anonymous_mask
            ).sum()
        )


        invalid_anonymous_mask = (
            ~anonymous_values
            .str.startswith(
                "anon_"
            )
        )


        if invalid_anonymous_mask.any():

            invalid_anonymous_ids.update(
                anonymous_values[
                    invalid_anonymous_mask
                ].tolist()
            )


        # ====================================================
        # SESSION ID
        # ====================================================

        invalid_sessions = (
            set(
                chunk[
                    "session_id"
                ]
            )
            -
            session_ids
        )


        invalid_session_ids.update(
            invalid_sessions
        )


        # ====================================================
        # EVENT TYPES
        # ====================================================

        event_type_values = (
            chunk[
                "event_type"
            ]
            .value_counts()
            .to_dict()
        )


        for event_type, count in (
            event_type_values.items()
        ):

            event_type_counts[
                event_type
            ] = (
                event_type_counts.get(
                    event_type,
                    0,
                )
                +
                int(count)
            )


        invalid_types = (
            set(
                chunk[
                    "event_type"
                ]
            )
            -
            VALID_EVENT_TYPES
        )


        invalid_event_types.update(
            invalid_types
        )


        # ====================================================
        # TIMESTAMP PARSING
        # ====================================================

        chunk[
            "event_timestamp"
        ] = pd.to_datetime(
            chunk[
                "event_timestamp"
            ],
            errors="coerce",
        )


        bad_timestamp_mask = (
            chunk[
                "event_timestamp"
            ].isna()
        )


        invalid_timestamps += int(
            bad_timestamp_mask.sum()
        )


        valid_timestamp_chunk = (
            chunk[
                ~bad_timestamp_mask
            ]
            .copy()
        )


        # ====================================================
        # SESSION TEMPORAL INTEGRITY
        # ====================================================

        for row in valid_timestamp_chunk[
            [
                "session_id",
                "event_timestamp",
            ]
        ].itertuples(
            index=False
        ):

            session_id = str(
                row.session_id
            )

            event_timestamp = (
                row.event_timestamp
            )


            start = (
                session_start_map.get(
                    session_id
                )
            )

            end = (
                session_end_map.get(
                    session_id
                )
            )


            if (
                start is None
                or
                end is None
            ):

                continue


            if (
                event_timestamp < start
                or
                event_timestamp > end
            ):

                timestamp_outside_session += 1


        # ====================================================
        # SESSION / CUSTOMER CONSISTENCY
        #
        # Only rows with a customer_id are checked.
        # ====================================================

        customer_rows = chunk[
            customer_mask
        ]


        for row in customer_rows[
            [
                "session_id",
                "customer_id",
            ]
        ].itertuples(
            index=False
        ):

            session_id = str(
                row.session_id
            )

            customer_id = str(
                row.customer_id
            )


            session_customer = (
                session_customer_map.get(
                    session_id
                )
            )


            if (
                session_customer is not None
                and
                session_customer != customer_id
            ):

                customer_session_mismatches += 1


        # ====================================================
        # SESSION / ANONYMOUS CONSISTENCY
        # ====================================================

        for row in chunk[
            [
                "session_id",
                "anonymous_id",
            ]
        ].itertuples(
            index=False
        ):

            session_id = str(
                row.session_id
            )

            anonymous_id = str(
                row.anonymous_id
            )


            session_anonymous = (
                session_anonymous_map.get(
                    session_id
                )
            )


            if (
                session_anonymous is not None
                and
                session_anonymous != anonymous_id
            ):

                anonymous_session_mismatches += 1


        # ====================================================
        # PRODUCT EVENT REQUIREMENT
        # ====================================================

        product_event_mask = (
            chunk[
                "event_type"
            ].isin(
                PRODUCT_EVENT_TYPES
            )
        )


        missing_product_mask = (
            product_event_mask
            &
            (~product_mask)
        )


        missing_product_for_product_events += int(
            missing_product_mask.sum()
        )


        # ====================================================
        # EVENT COUNTERS
        # ====================================================

        session_start_count += int(
            (
                chunk[
                    "event_type"
                ]
                ==
                "session_start"
            ).sum()
        )


        login_count += int(
            (
                chunk[
                    "event_type"
                ]
                ==
                "login"
            ).sum()
        )


        recommendation_impression_count += int(
            (
                chunk[
                    "event_type"
                ]
                ==
                "recommendation_impression"
            ).sum()
        )


        recommendation_click_count += int(
            (
                chunk[
                    "event_type"
                ]
                ==
                "recommendation_click"
            ).sum()
        )


        purchase_count += int(
            (
                chunk[
                    "event_type"
                ]
                ==
                "purchase_interaction"
            ).sum()
        )


    # ========================================================
    # POST-LOAD
    # ========================================================

    print()

    print(
        f"[EVENT VALIDATION] "
        f"Loaded {total_rows:,} events."
    )


    # ========================================================
    # ROW COUNT
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking row count..."
    )


    if total_rows != EXPECTED_EVENT_COUNT:

        fail(
            f"Expected "
            f"{EXPECTED_EVENT_COUNT:,} events, "
            f"found {total_rows:,}."
        )


    print(
        "[EVENT VALIDATION PASSED] "
        f"Row count = {total_rows:,}."
    )


    # ========================================================
    # EVENT ID
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking event_id..."
    )


    if len(
        seen_event_ids
    ) != total_rows:

        fail(
            "event_id uniqueness validation failed."
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "event_id uniqueness passed."
    )


    # ========================================================
    # SESSION REFERENTIAL INTEGRITY
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking session referential integrity..."
    )


    if invalid_session_ids:

        fail(
            "Invalid session_id values detected: "
            f"{list(invalid_session_ids)[:10]}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Session referential integrity passed."
    )


    # ========================================================
    # CUSTOMER REFERENTIAL INTEGRITY
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking customer referential integrity..."
    )


    # --------------------------------------------------------
    # NULL customer_id values are explicitly allowed.
    # Only non-null customer IDs are validated.
    # --------------------------------------------------------

    if invalid_customer_ids:

        fail(
            "Invalid customer_id values detected: "
            f"{list(invalid_customer_ids)[:10]}"
        )


    if customer_session_mismatches > 0:

        fail(
            "Customer/session identity mismatch detected: "
            f"{customer_session_mismatches:,} rows."
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Customer referential integrity passed."
    )


    # ========================================================
    # PRODUCT REFERENTIAL INTEGRITY
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking product referential integrity..."
    )


    if invalid_product_ids:

        fail(
            "Invalid product_id values detected: "
            f"{list(invalid_product_ids)[:10]}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Product referential integrity passed."
    )


    # ========================================================
    # ANONYMOUS IDENTITY
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking anonymous identity integrity..."
    )


    if invalid_anonymous_ids:

        fail(
            "Invalid anonymous_id values detected: "
            f"{list(invalid_anonymous_ids)[:10]}"
        )


    if anonymous_session_mismatches > 0:

        fail(
            "Anonymous/session identity mismatch detected: "
            f"{anonymous_session_mismatches:,} rows."
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Anonymous identity validation passed."
    )


    # ========================================================
    # EVENT TYPES
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking event types..."
    )


    if invalid_event_types:

        fail(
            "Invalid event types detected: "
            f"{sorted(invalid_event_types)}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Event-type validation passed."
    )


    # ========================================================
    # TIMESTAMP VALIDATION
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking timestamps..."
    )


    if invalid_timestamps > 0:

        fail(
            "Invalid event timestamps detected: "
            f"{invalid_timestamps:,}"
        )


    if timestamp_outside_session > 0:

        fail(
            "Events outside their session boundaries: "
            f"{timestamp_outside_session:,}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Timestamp validation passed."
    )


    # ========================================================
    # PRODUCT EVENT VALIDATION
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "Checking product-event requirements..."
    )


    if (
        missing_product_for_product_events
        > 0
    ):

        fail(
            "Product-linked events without "
            "product_id: "
            f"{missing_product_for_product_events:,}"
        )


    print(
        "[EVENT VALIDATION PASSED] "
        "Product-event validation passed."
    )


    # ========================================================
    # DISTRIBUTION
    # ========================================================

    print()

    print(
        "[EVENT VALIDATION] "
        "Event-type distribution:"
    )


    for event_type in sorted(
        event_type_counts
    ):

        count = (
            event_type_counts[
                event_type
            ]
        )


        share = (
            count
            /
            total_rows
            *
            100
        )


        print(
            f"    {event_type:<30} "
            f"= {count:>10,} "
            f"({share:>6.2f}%)"
        )


    # ========================================================
    # LINKAGE SUMMARY
    # ========================================================

    customer_share = (
        customer_linked_count
        /
        total_rows
        *
        100
    )


    anonymous_only_share = (
        null_customer_count
        /
        total_rows
        *
        100
    )


    product_share = (
        product_linked_count
        /
        total_rows
        *
        100
    )


    no_product_share = (
        null_product_count
        /
        total_rows
        *
        100
    )


    print()

    print(
        "[EVENT VALIDATION] "
        "Identity/linkage summary:"
    )


    print(
        f"    Customer-linked events "
        f"= {customer_linked_count:,} "
        f"({customer_share:.2f}%)"
    )


    print(
        f"    Events without customer_id "
        f"= {null_customer_count:,} "
        f"({anonymous_only_share:.2f}%)"
    )


    print(
        f"    Product-linked events "
        f"= {product_linked_count:,} "
        f"({product_share:.2f}%)"
    )


    print(
        f"    Events without product_id "
        f"= {null_product_count:,} "
        f"({no_product_share:.2f}%)"
    )


    print(
        f"    Anonymous-linked events "
        f"= {anonymous_linked_count:,}"
    )


    # ========================================================
    # KEY EVENT COUNTS
    # ========================================================

    print()

    print(
        "[EVENT VALIDATION] "
        "Key event counts:"
    )


    print(
        f"    session_start              = "
        f"{session_start_count:,}"
    )


    print(
        f"    login                      = "
        f"{login_count:,}"
    )


    print(
        f"    recommendation_impression  = "
        f"{recommendation_impression_count:,}"
    )


    print(
        f"    recommendation_click       = "
        f"{recommendation_click_count:,}"
    )


    print(
        f"    purchase_interaction       = "
        f"{purchase_count:,}"
    )


    # ========================================================
    # EVENT PERIOD
    # ========================================================

    print()

    print(
        "[EVENT VALIDATION] "
        "Event period:"
    )


    period_data = pd.read_csv(
        EVENTS_FILE,
        usecols=[
            "event_timestamp",
        ],
        dtype=str,
    )


    period_data[
        "event_timestamp"
    ] = pd.to_datetime(
        period_data[
            "event_timestamp"
        ],
        errors="coerce",
    )


    print(
        f"    Period start = "
        f"{period_data['event_timestamp'].min()}"
    )


    print(
        f"    Period end   = "
        f"{period_data['event_timestamp'].max()}"
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print(
        "[EVENT VALIDATION] SUMMARY"
    )

    print("=" * 70)


    print(
        f"Events                    = "
        f"{total_rows:,}"
    )


    print(
        f"Unique event IDs          = "
        f"{len(seen_event_ids):,}"
    )


    print(
        f"Unique sessions            = "
        f"{len(session_ids):,}"
    )


    print(
        f"Customer-linked events    = "
        f"{customer_linked_count:,}"
    )


    print(
        f"Events without customer_id = "
        f"{null_customer_count:,}"
    )


    print(
        f"Product-linked events     = "
        f"{product_linked_count:,}"
    )


    print(
        f"Events without product_id = "
        f"{null_product_count:,}"
    )


    print(
        f"Public customers          = "
        f"{len(customer_ids):,}"
    )


    print(
        f"Public products            = "
        f"{len(product_ids):,}"
    )


    print(
        f"session_start             = "
        f"{session_start_count:,}"
    )


    print(
        f"login                     = "
        f"{login_count:,}"
    )


    print(
        f"recommendation_impression = "
        f"{recommendation_impression_count:,}"
    )


    print(
        f"recommendation_click      = "
        f"{recommendation_click_count:,}"
    )


    print(
        f"purchase_interaction      = "
        f"{purchase_count:,}"
    )


    print("=" * 70)


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "[EVENT VALIDATION] "
        "COMPLETE — ALL CHECKS PASSED"
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    validate_events()