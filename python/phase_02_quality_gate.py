"""
ORGEE — Phase 2 Full Quality Gate

Run this from your project root (the folder that directly contains
data/). Checks every enterprise entity against the rules locked in
04_enterprise_data_requirements.md section 14:

    completeness, uniqueness, referential integrity,
    temporal integrity, grain integrity, domain integrity,
    business logic

Also re-checks the 3 specific issues found in the Phase 2 review
(timestamp corruption, session identity leak, recommendation event
leak into generic events).

Usage:
    python phase2_quality_gate.py
"""

from pathlib import Path
import sys

import pandas as pd


ROOT_CANDIDATE = Path(__file__).resolve().parent

def find_project_root(start: Path) -> Path:
    """
    Walk upward from wherever this script lives until we find a
    folder that directly contains a 'data' subfolder with the
    expected enterprise layout. This means the script can be run
    from the project root OR from inside python/, python/generators/,
    etc. without needing to be moved.
    """
    current = start
    for _ in range(6):
        candidate = current / "data" / "enterprise" / "sessions" / "sessions.csv"
        if candidate.exists():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not locate the project root (a folder containing "
        "data/enterprise/sessions/sessions.csv) by walking up from:\n"
        f"{start}\n\n"
        "Make sure this script is saved somewhere inside your ORGEE "
        "project folder."
    )

ROOT = find_project_root(ROOT_CANDIDATE)
DATA = ROOT / "data"

PASS = []
FAIL = []


def check(label: str, condition: bool, detail: str = ""):
    if condition:
        PASS.append(label)
        print(f"[PASS] {label}")
    else:
        FAIL.append(label)
        print(f"[FAIL] {label}" + (f" — {detail}" if detail else ""))


def load(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path, **kwargs)


def main() -> None:

    print("=" * 70)
    print("ORGEE — PHASE 2 FULL QUALITY GATE")
    print("=" * 70)

    # ------------------------------------------------------------
    # Load everything
    # ------------------------------------------------------------

    customers = load(DATA / "processed" / "Public" / "olist_customers_dataset.csv")
    orders = load(DATA / "processed" / "Public" / "olist_orders_dataset.csv")
    products = load(DATA / "processed" / "Public" / "olist_products_dataset.csv")

    sessions = load(
        DATA / "enterprise" / "sessions" / "sessions.csv",
        parse_dates=["session_start_timestamp", "session_end_timestamp"],
    )
    events = load(
        DATA / "enterprise" / "events" / "events.csv",
        parse_dates=["event_timestamp"],
    )
    identity = load(
        DATA / "enterprise" / "identity" / "identity_links.csv",
        parse_dates=["link_timestamp"],
    )
    campaigns = load(
        DATA / "enterprise" / "marketing" / "campaigns.csv",
        parse_dates=["start_date", "end_date"],
    )
    exposures = load(
        DATA / "enterprise" / "marketing" / "campaign_exposures.csv",
        parse_dates=["exposure_timestamp"],
    )
    experiments = load(
        DATA / "enterprise" / "experiments" / "experiments.csv",
        parse_dates=["start_timestamp", "end_timestamp"],
    )
    assignments = load(
        DATA / "enterprise" / "experiments" / "experiment_assignments.csv",
        parse_dates=["assignment_timestamp"],
    )
    inventory = load(
        DATA / "enterprise" / "inventory" / "inventory_observations.csv",
        parse_dates=["observation_timestamp"],
    )
    recs = load(
        DATA / "enterprise" / "recommendations" / "recommendation_events.csv",
        parse_dates=["event_timestamp"],
    )

    valid_customer_ids = set(customers["customer_id"].astype(str))
    valid_product_ids = set(products["product_id"].astype(str))
    valid_session_ids = set(sessions["session_id"].astype(str))
    valid_anon_ids = set(sessions["anonymous_id"].astype(str))
    valid_campaign_ids = set(campaigns["campaign_id"].astype(str))
    valid_experiment_ids = set(experiments["experiment_id"].astype(str))

    # ============================================================
    # 1. UNIQUENESS (primary keys)
    # ============================================================

    print("\n--- Uniqueness ---")

    check("sessions.session_id unique", not sessions["session_id"].duplicated().any())
    check("sessions.anonymous_id unique", not sessions["anonymous_id"].duplicated().any())
    check("events.event_id unique", not events["event_id"].duplicated().any())
    check("identity_links.identity_link_id unique", not identity["identity_link_id"].duplicated().any())
    check("identity_links.anonymous_id unique (one link per anon id)", not identity["anonymous_id"].duplicated().any())
    check("campaigns.campaign_id unique", not campaigns["campaign_id"].duplicated().any())
    check("campaign_exposures.campaign_exposure_id unique", not exposures["campaign_exposure_id"].duplicated().any())
    check("experiments.experiment_id unique", not experiments["experiment_id"].duplicated().any())
    check(
        "experiment_assignments one row per (customer, experiment)",
        not assignments.duplicated(subset=["customer_id", "experiment_id"]).any(),
    )
    check("recommendation_events.recommendation_event_id unique", not recs["recommendation_event_id"].duplicated().any())

    # ============================================================
    # 2. COMPLETENESS (required fields non-null)
    # ============================================================

    print("\n--- Completeness ---")

    check("sessions: session_id/anonymous_id/timestamps non-null",
          sessions[["session_id", "anonymous_id", "session_start_timestamp", "session_end_timestamp"]].notna().all().all())
    check("events: event_id/session_id/anonymous_id/event_type/timestamp non-null",
          events[["event_id", "session_id", "anonymous_id", "event_type", "event_timestamp"]].notna().all().all())
    check("identity_links: no nulls in any column",
          identity.notna().all().all())

    # ============================================================
    # 3. REFERENTIAL INTEGRITY
    # ============================================================

    print("\n--- Referential Integrity ---")

    check(
        "sessions.customer_id (where present) is a valid public customer",
        sessions["customer_id"].dropna().astype(str).isin(valid_customer_ids).all(),
    )
    check(
        "events.session_id → valid sessions",
        events["session_id"].astype(str).isin(valid_session_ids).all(),
    )
    check(
        "events.anonymous_id → valid sessions.anonymous_id",
        events["anonymous_id"].astype(str).isin(valid_anon_ids).all(),
    )
    check(
        "events.customer_id (where present) is a valid public customer",
        events["customer_id"].dropna().astype(str).isin(valid_customer_ids).all(),
    )
    check(
        "events.product_id (where present) is a valid public product",
        events["product_id"].dropna().astype(str).isin(valid_product_ids).all(),
    )
    check(
        "identity_links.customer_id → valid public customer",
        identity["customer_id"].astype(str).isin(valid_customer_ids).all(),
    )
    check(
        "identity_links.session_id → valid sessions",
        identity["session_id"].astype(str).isin(valid_session_ids).all(),
    )
    check(
        "identity_links every link has a matching login event in events.csv",
        identity.merge(
            events[events["event_type"] == "login"][["anonymous_id", "customer_id", "session_id"]].astype(str),
            on=["anonymous_id", "customer_id", "session_id"],
            how="left",
            indicator=True,
        )["_merge"].eq("both").all(),
    )
    check(
        "campaign_exposures.campaign_id → valid campaign",
        exposures["campaign_id"].astype(str).isin(valid_campaign_ids).all(),
    )
    check(
        "experiment_assignments.experiment_id → valid experiment",
        assignments["experiment_id"].astype(str).isin(valid_experiment_ids).all(),
    )
    check(
        "experiment_assignments.customer_id → valid public customer",
        assignments["customer_id"].astype(str).isin(valid_customer_ids).all(),
    )
    check(
        "recommendation_events.experiment_id (where present) → valid experiment",
        recs["experiment_id"].dropna().astype(str).isin(valid_experiment_ids).all(),
    )
    check(
        "recommendation_events.product_id → valid public product",
        recs["product_id"].dropna().astype(str).isin(valid_product_ids).all(),
    )

    # ============================================================
    # 4. TEMPORAL INTEGRITY
    # ============================================================

    print("\n--- Temporal Integrity ---")

    check(
        "sessions: session_end >= session_start",
        (sessions["session_end_timestamp"] >= sessions["session_start_timestamp"]).all(),
    )

    ev_bounds = events.merge(
        sessions[["session_id", "session_start_timestamp", "session_end_timestamp"]],
        on="session_id", how="left",
    )
    check(
        "events: every event falls within its session's start/end window",
        (
            (ev_bounds["event_timestamp"] >= ev_bounds["session_start_timestamp"]) &
            (ev_bounds["event_timestamp"] <= ev_bounds["session_end_timestamp"])
        ).all(),
    )

    login_first = (
        events[events["event_type"] == "login"]
        .groupby("session_id")["event_timestamp"].min()
    )
    auth = events[events["customer_id"].notna()].copy()
    auth["first_login"] = auth["session_id"].map(login_first)
    check(
        "events: authenticated (customer_id-populated) activity never precedes that session's login",
        (auth["event_timestamp"] >= auth["first_login"]).all(),
    )

    exp_bounds = exposures.merge(
        campaigns[["campaign_id", "start_date", "end_date"]], on="campaign_id", how="left",
    )
    check(
        "campaign_exposures fall within their campaign's date range",
        (
            (exp_bounds["exposure_timestamp"] >= exp_bounds["start_date"]) &
            (exp_bounds["exposure_timestamp"] <= exp_bounds["end_date"] + pd.Timedelta(days=1))
        ).all(),
    )

    assign_bounds = assignments.merge(
        experiments[["experiment_id", "start_timestamp", "end_timestamp"]], on="experiment_id", how="left",
    )
    check(
        "experiment_assignments fall within their experiment's period",
        (
            (assign_bounds["assignment_timestamp"] >= assign_bounds["start_timestamp"]) &
            (assign_bounds["assignment_timestamp"] <= assign_bounds["end_timestamp"])
        ).all(),
    )

    # ============================================================
    # 5. DOMAIN INTEGRITY (controlled vocabularies)
    # ============================================================

    print("\n--- Domain Integrity ---")

    ALLOWED_EVENT_TYPES = {
        "session_start", "search", "product_view", "add_to_cart",
        "remove_from_cart", "checkout_start", "login", "purchase_interaction",
    }
    check(
        "events.event_type uses only the approved generic vocabulary "
        "(no recommendation_impression/click leaked in)",
        set(events["event_type"].unique()) == ALLOWED_EVENT_TYPES,
        detail=str(set(events["event_type"].unique()) - ALLOWED_EVENT_TYPES),
    )
    check(
        "identity_links.link_method is always 'successful_login'",
        (identity["link_method"] == "successful_login").all(),
    )
    check(
        "experiment_assignments.variant in {control, treatment}",
        assignments["variant"].isin(["control", "treatment"]).all(),
    )
    check(
        "recommendation_events.event_type in {impression, click, conversion}",
        recs["event_type"].isin(
            ["recommendation_impression", "recommendation_click", "recommendation_conversion"]
        ).all(),
    )
    check(
        "inventory_observations.available_quantity >= 0",
        (inventory["available_quantity"] >= 0).all(),
    )

    # ============================================================
    # 6. GRAIN / BUSINESS LOGIC — the 3 specific fixes
    # ============================================================

    print("\n--- Business Logic (Phase 2 fix regressions) ---")

    check(
        "sessions.customer_id populated ONLY for sessions with a real identity link "
        "(not 100% of sessions)",
        sessions["customer_id"].notna().sum() == len(identity),
        detail=f"sessions identified={sessions['customer_id'].notna().sum()}, identity_links={len(identity)}",
    )
    check(
        "events.csv row count matches target (3,000,000) — no silent Excel truncation",
        len(events) == 3_000_000,
        detail=f"actual={len(events):,}",
    )
    check(
        "event_timestamp / link_timestamp are full datetimes, not truncated",
        events["event_timestamp"].dt.year.notna().all() and identity["link_timestamp"].dt.year.notna().all(),
    )
    check(
        "funnel shows real drop-off (fewer purchases than product views)",
        (events["event_type"] == "purchase_interaction").sum() < (events["event_type"] == "product_view").sum(),
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print("\n" + "=" * 70)
    print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
    print("=" * 70)

    if FAIL:
        print("\nFailed checks:")
        for f in FAIL:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nAll Phase 2 quality gate checks passed. Clear to proceed to Phase 3.")


if __name__ == "__main__":
    main()