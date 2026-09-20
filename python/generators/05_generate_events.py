"""
ORGEE — Event Generator

Generates synthetic customer/anonymous behavioral events
from the ORGEE enterprise session population.

Source:
    Document 7 — Enterprise Generation Configuration

Target:
    3,000,000 events
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

SESSIONS_FILE = (
    SESSION_DIR / "sessions.csv"
)

# FIX: public sessions.csv no longer carries customer_id (it is
# anonymous until a login event identifies it). The internal truth
# file supplies the "true" customer behind each session so this
# generator can correctly reveal it only after a login event fires
# within that session's event sequence.
SESSION_TRUTH_FILE = (
    SESSION_DIR / "_internal_session_customer_truth.csv"
)

PRODUCTS_FILE = (
    PUBLIC_DATA_DIR / "olist_products_dataset.csv"
)

OUTPUT_FILE = (
    EVENT_DIR / "events.csv"
)

CONFIG_FILE = (
    Path(__file__).resolve().parent
    / "01_generator_config.py"
)


# ============================================================
# LOAD CONFIGURATION
# ============================================================

if not CONFIG_FILE.exists():
    raise FileNotFoundError(
        f"Generator configuration not found:\n"
        f"{CONFIG_FILE}"
    )

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


PRIMARY_SEED = int(config.PRIMARY_SEED)

TARGET_VOLUMES = config.TARGET_VOLUMES

TARGET_EVENTS = int(
    TARGET_VOLUMES["events"]
)

TARGET_SESSIONS = int(
    TARGET_VOLUMES["sessions"]
)

FUNNEL_PROBABILITIES = (
    config.FUNNEL_TRANSITION_PROBABILITIES
)

LOGIN_CAPABLE_SESSION_RATE = float(
    config.LOGIN_CAPABLE_SESSION_RATE
)


# ============================================================
# EVENT TYPES
# ============================================================

EVENT_TYPES = tuple(
    config.EVENT_TYPES
)


# ============================================================
# FUNNEL PARAMETERS
# ============================================================

SESSION_TO_BROWSE_PROBABILITY = float(
    FUNNEL_PROBABILITIES[
        "session_to_search_or_browse"
    ]
)

BROWSE_TO_PRODUCT_VIEW_PROBABILITY = float(
    FUNNEL_PROBABILITIES[
        "search_or_browse_to_product_view"
    ]
)

PRODUCT_VIEW_TO_CART_PROBABILITY = float(
    FUNNEL_PROBABILITIES[
        "product_view_to_add_to_cart"
    ]
)

CART_TO_CHECKOUT_PROBABILITY = float(
    FUNNEL_PROBABILITIES[
        "add_to_cart_to_checkout"
    ]
)

CHECKOUT_TO_PURCHASE_PROBABILITY = float(
    FUNNEL_PROBABILITIES[
        "checkout_to_purchase_interaction"
    ]
)


# This remains a generator assumption because
# Document 7 defines the login-capable session rate,
# but not a separate login-success percentage.
LOGIN_SUCCESS_RATE = 0.80


# ============================================================
# RECOMMENDATION PARAMETERS
# ============================================================

RECOMMENDATION_PROBABILITIES = (
    config.RECOMMENDATION_FUNNEL_PROBABILITIES
)

RECOMMENDATION_IMPRESSION_PROBABILITY = 0.08

RECOMMENDATION_CLICK_PROBABILITY = float(
    RECOMMENDATION_PROBABILITIES[
        "impression_to_click"
    ]
)


# ============================================================
# EVENT INTENSITY
# ============================================================

SESSION_EVENT_COUNT_RANGES = {
    "short": (1, 5),
    "medium": (2, 10),
    "long": (4, 20),
}


# ============================================================
# NORMALIZE COUNTS
# ============================================================

def normalize_event_counts(
    raw_counts: np.ndarray,
    target_total: int,
    minimum: np.ndarray,
    maximum: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:

    counts = raw_counts.astype(
        np.int64
    ).copy()

    current_total = int(
        counts.sum()
    )

    # --------------------------------------------------------
    # Increase
    # --------------------------------------------------------

    if current_total < target_total:

        difference = (
            target_total
            - current_total
        )

        while difference > 0:

            available = np.where(
                counts < maximum
            )[0]

            if len(available) == 0:
                raise ValueError(
                    "Unable to increase session event counts "
                    "to target volume."
                )

            index = int(
                rng.choice(available)
            )

            counts[index] += 1
            difference -= 1

    # --------------------------------------------------------
    # Decrease
    # --------------------------------------------------------

    elif current_total > target_total:

        difference = (
            current_total
            - target_total
        )

        while difference > 0:

            available = np.where(
                counts > minimum
            )[0]

            if len(available) == 0:
                raise ValueError(
                    "Unable to reduce session event counts "
                    "to target volume."
                )

            index = int(
                rng.choice(available)
            )

            counts[index] -= 1
            difference -= 1

    if int(counts.sum()) != target_total:
        raise ValueError(
            "Unable to normalize event counts "
            "to configured target."
        )

    return counts


# ============================================================
# SESSION EVENT COUNTS
# ============================================================

def generate_session_event_counts(
    sessions: pd.DataFrame,
    rng: np.random.Generator,
) -> np.ndarray:

    session_types = (
        sessions["session_type"]
        .astype(str)
        .to_numpy()
    )

    raw_counts = np.zeros(
        len(sessions),
        dtype=np.int64,
    )

    minimum = np.zeros(
        len(sessions),
        dtype=np.int64,
    )

    maximum = np.zeros(
        len(sessions),
        dtype=np.int64,
    )

    for session_type, (
        low,
        high,
    ) in SESSION_EVENT_COUNT_RANGES.items():

        mask = (
            session_types
            == session_type
        )

        count = int(
            mask.sum()
        )

        if count == 0:
            continue

        raw_counts[mask] = rng.integers(
            low,
            high + 1,
            size=count,
        )

        minimum[mask] = low
        maximum[mask] = high

    return normalize_event_counts(
        raw_counts,
        TARGET_EVENTS,
        minimum,
        maximum,
        rng,
    )


# ============================================================
# TIMESTAMP GENERATION
# ============================================================

def generate_event_timestamps(
    session_start,
    session_end,
    count: int,
    rng: np.random.Generator,
):

    if count == 1:
        return [session_start]

    start_ns = session_start.value
    end_ns = session_end.value

    if end_ns <= start_ns:
        return [
            pd.Timestamp(start_ns)
            for _ in range(count)
        ]

    offsets = rng.integers(
        0,
        end_ns - start_ns + 1,
        size=count,
    )

    offsets.sort()

    return [
        pd.Timestamp(
            start_ns + int(offset)
        )
        for offset in offsets
    ]


# ============================================================
# EVENT SEQUENCE
# ============================================================

def generate_event_sequence(
    count: int,
    rng: np.random.Generator,
    login_event: bool,
):

    if count <= 0:
        return []

    events = [
        "session_start"
    ]

    if count == 1:
        return events

    # --------------------------------------------------------
    # Initial browse/search
    # --------------------------------------------------------

    if (
        rng.random()
        < SESSION_TO_BROWSE_PROBABILITY
    ):

        if rng.random() < 0.50:
            events.append("search")
        else:
            events.append("product_view")

    else:

        if rng.random() < 0.50:
            events.append("product_view")
        else:
            events.append("search")

    # --------------------------------------------------------
    # Continue journey
    # --------------------------------------------------------

    while len(events) < count:

        last_event = events[-1]

        if last_event == "search":

            if (
                rng.random()
                < BROWSE_TO_PRODUCT_VIEW_PROBABILITY
            ):
                events.append(
                    "product_view"
                )
            else:
                events.append(
                    "search"
                )

        elif last_event == "product_view":

            if (
                rng.random()
                < PRODUCT_VIEW_TO_CART_PROBABILITY
            ):

                events.append(
                    "add_to_cart"
                )

            else:

                if rng.random() < 0.65:
                    events.append(
                        "product_view"
                    )
                else:
                    events.append(
                        "search"
                    )

        elif last_event == "add_to_cart":

            if (
                rng.random()
                < CART_TO_CHECKOUT_PROBABILITY
            ):

                events.append(
                    "checkout_start"
                )

            elif rng.random() < 0.20:

                events.append(
                    "remove_from_cart"
                )

            else:

                events.append(
                    "product_view"
                )

        elif last_event == "remove_from_cart":

            if rng.random() < 0.50:
                events.append(
                    "product_view"
                )
            else:
                events.append(
                    "search"
                )

        elif last_event == "checkout_start":

            if (
                rng.random()
                < CHECKOUT_TO_PURCHASE_PROBABILITY
            ):

                events.append(
                    "purchase_interaction"
                )

            else:

                events.append(
                    "product_view"
                )

        elif last_event == "purchase_interaction":

            if rng.random() < 0.70:
                events.append(
                    "product_view"
                )
            else:
                events.append(
                    "search"
                )

        else:

            events.append(
                "product_view"
            )

    # --------------------------------------------------------
    # Login insertion
    # --------------------------------------------------------

    if login_event and count >= 3:

        login_position = int(
            rng.integers(
                1,
                min(
                    len(events),
                    max(
                        2,
                        count // 2 + 1,
                    ),
                ),
            )
        )

        events.insert(
            login_position,
            "login",
        )

        if len(events) > count:
            events.pop()

    return events[:count]


# ============================================================
# PRODUCTS
# ============================================================

def load_product_ids() -> np.ndarray:

    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(
            f"Products dataset not found:\n"
            f"{PRODUCTS_FILE}"
        )

    products = pd.read_csv(
        PRODUCTS_FILE,
        usecols=["product_id"],
    )

    products = products.dropna(
        subset=["product_id"]
    )

    product_ids = (
        products["product_id"]
        .astype(str)
        .drop_duplicates()
        .to_numpy()
    )

    if len(product_ids) == 0:
        raise ValueError(
            "No valid public product IDs found."
        )

    return product_ids


# ============================================================
# EVENT GENERATION
# ============================================================

def generate_events(
    sessions: pd.DataFrame,
    product_ids: np.ndarray,
    rng: np.random.Generator,
) -> pd.DataFrame:

    event_counts = (
        generate_session_event_counts(
            sessions,
            rng,
        )
    )

    event_session_ids = []
    event_anonymous_ids = []
    event_customer_ids = []
    event_product_ids = []
    event_types = []
    event_devices = []
    event_platforms = []
    event_timestamps = []

    # --------------------------------------------------------
    # Login-capable sessions
    # --------------------------------------------------------

    login_capable_count = int(
        TARGET_SESSIONS
        * LOGIN_CAPABLE_SESSION_RATE
    )

    login_capable_indices = set(
        rng.choice(
            len(sessions),
            size=login_capable_count,
            replace=False,
        )
    )

    successful_login_indices = set()

    for index in login_capable_indices:

        if (
            rng.random()
            < LOGIN_SUCCESS_RATE
        ):
            successful_login_indices.add(
                index
            )

    # --------------------------------------------------------
    # Generate events
    # --------------------------------------------------------

    for index, session in sessions.iterrows():

        count = int(
            event_counts[index]
        )

        sequence = generate_event_sequence(
            count,
            rng,
            index in successful_login_indices,
        )

        timestamps = (
            generate_event_timestamps(
                pd.Timestamp(
                    session[
                        "session_start_timestamp"
                    ]
                ),
                pd.Timestamp(
                    session[
                        "session_end_timestamp"
                    ]
                ),
                len(sequence),
                rng,
            )
        )

        authenticated = False

        for event_type, timestamp in zip(
            sequence,
            timestamps,
        ):

            if event_type == "login":
                authenticated = True

            customer_id = (
                str(session["customer_id"])
                if authenticated
                else None
            )

            if event_type in {
                "product_view",
                "add_to_cart",
                "remove_from_cart",
                "recommendation_impression",
                "recommendation_click",
                "purchase_interaction",
            }:

                product_id = str(
                    rng.choice(product_ids)
                )

            else:

                product_id = None

            event_session_ids.append(
                str(session["session_id"])
            )

            event_anonymous_ids.append(
                str(session["anonymous_id"])
            )

            event_customer_ids.append(
                customer_id
            )

            event_product_ids.append(
                product_id
            )

            event_types.append(
                event_type
            )

            event_devices.append(
                str(session["device_type"])
            )

            event_platforms.append(
                str(session["platform"])
            )

            event_timestamps.append(
                timestamp
            )

    return pd.DataFrame(
        {
            "event_id": [
                f"evt_{i:09d}"
                for i in range(
                    1,
                    len(event_session_ids) + 1,
                )
            ],
            "session_id": event_session_ids,
            "anonymous_id": event_anonymous_ids,
            "customer_id": event_customer_ids,
            "product_id": event_product_ids,
            "event_type": event_types,
            "device_type": event_devices,
            "platform": event_platforms,
            "event_timestamp": event_timestamps,
        }
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_events(
    events: pd.DataFrame,
    sessions: pd.DataFrame,
    product_ids: np.ndarray,
) -> None:

    required_columns = {
        "event_id",
        "session_id",
        "anonymous_id",
        "customer_id",
        "product_id",
        "event_type",
        "device_type",
        "platform",
        "event_timestamp",
    }

    missing_columns = (
        required_columns
        - set(events.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing event columns: "
            f"{sorted(missing_columns)}"
        )

    if len(events) != TARGET_EVENTS:
        raise ValueError(
            f"Expected {TARGET_EVENTS:,} events, "
            f"generated {len(events):,}."
        )

    if events["event_id"].duplicated().any():
        raise ValueError(
            "Duplicate event_id values detected."
        )

    valid_session_ids = set(
        sessions["session_id"].astype(str)
    )

    if not (
        events["session_id"]
        .astype(str)
        .isin(valid_session_ids)
        .all()
    ):
        raise ValueError(
            "Events contain invalid session_id values."
        )

    valid_anonymous_ids = set(
        sessions["anonymous_id"].astype(str)
    )

    if not (
        events["anonymous_id"]
        .astype(str)
        .isin(valid_anonymous_ids)
        .all()
    ):
        raise ValueError(
            "Events contain invalid anonymous_id values."
        )

    valid_product_ids = set(
        map(str, product_ids)
    )

    product_mask = events[
        "product_id"
    ].notna()

    if not (
        events.loc[
            product_mask,
            "product_id",
        ]
        .astype(str)
        .isin(valid_product_ids)
        .all()
    ):
        raise ValueError(
            "Events contain invalid product_id values."
        )

    if not events["event_type"].isin(
        EVENT_TYPES
    ).all():
        raise ValueError(
            "Invalid event_type detected."
        )

    events["event_timestamp"] = pd.to_datetime(
        events["event_timestamp"],
        errors="coerce",
    )

    if events["event_timestamp"].isna().any():
        raise ValueError(
            "Null event timestamps detected."
        )

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

    merged = events.merge(
        session_bounds,
        on="session_id",
        how="left",
        validate="many_to_one",
    )

    outside_session = (
        (
            merged["event_timestamp"]
            < merged[
                "session_start_timestamp"
            ]
        )
        |
        (
            merged["event_timestamp"]
            > merged[
                "session_end_timestamp"
            ]
        )
    )

    if outside_session.any():
        raise ValueError(
            "Events detected outside their session boundaries."
        )

    # --------------------------------------------------------
    # Login ordering
    # --------------------------------------------------------

    login_events = events[
        events["event_type"] == "login"
    ][
        [
            "session_id",
            "event_timestamp",
        ]
    ].rename(
        columns={
            "event_timestamp":
                "login_timestamp"
        }
    )

    if not login_events.empty:

        first_login = (
            login_events
            .groupby("session_id")[
                "login_timestamp"
            ]
            .min()
        )

        authenticated_events = events[
            events["customer_id"].notna()
        ].copy()

        authenticated_events[
            "first_login_timestamp"
        ] = (
            authenticated_events[
                "session_id"
            ].map(first_login)
        )

        invalid_authentication = (
            authenticated_events[
                "event_timestamp"
            ]
            <
            authenticated_events[
                "first_login_timestamp"
            ]
        )

        if invalid_authentication.any():
            raise ValueError(
                "Authenticated activity occurs before login."
            )

    print(
        f"[EVENT] Validation passed — "
        f"{len(events):,} events."
    )

    print(
        f"[EVENT] Sessions represented — "
        f"{events['session_id'].nunique():,}"
    )

    print(
        f"[EVENT] Login events — "
        f"{(events['event_type'] == 'login').sum():,}"
    )

    print(
        f"[EVENT] Product-linked events — "
        f"{events['product_id'].notna().sum():,}"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 70)
    print("ORGEE — EVENT GENERATOR")
    print("=" * 70)

    EVENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not SESSIONS_FILE.exists():
        raise FileNotFoundError(
            f"Session dataset not found:\n"
            f"{SESSIONS_FILE}\n\n"
            "Run the session generator first."
        )

    sessions = pd.read_csv(
        SESSIONS_FILE,
        parse_dates=[
            "session_start_timestamp",
            "session_end_timestamp",
        ],
    )

    if not SESSION_TRUTH_FILE.exists():
        raise FileNotFoundError(
            f"Session identity truth file not found:\n"
            f"{SESSION_TRUTH_FILE}\n\n"
            "Run the session generator first."
        )

    session_truth = pd.read_csv(
        SESSION_TRUTH_FILE,
        usecols=["session_id", "true_customer_id"],
    )

    # FIX: bring the true (pre-login) customer identity into the
    # in-memory frame used for generation only. This is never
    # written back to the public sessions.csv.
    sessions = sessions.drop(
        columns=["customer_id"]
    ).merge(
        session_truth,
        on="session_id",
        how="left",
        validate="one_to_one",
    ).rename(
        columns={"true_customer_id": "customer_id"}
    )

    if len(sessions) != TARGET_SESSIONS:
        raise ValueError(
            f"Expected {TARGET_SESSIONS:,} sessions, "
            f"found {len(sessions):,}."
        )

    product_ids = load_product_ids()

    rng = np.random.default_rng(
        PRIMARY_SEED + 500
    )

    print(
        f"[EVENT] Generating "
        f"{TARGET_EVENTS:,} events..."
    )

    events = generate_events(
        sessions,
        product_ids,
        rng,
    )

    validate_events(
        events,
        sessions,
        product_ids,
    )

    events.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"[EVENT] Generated "
        f"{len(events):,} events."
    )

    print(
        "[EVENT] Output written to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()