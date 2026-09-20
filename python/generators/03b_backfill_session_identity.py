"""
ORGEE — Session Identity Backfill (FIX)

Sessions start anonymous. This script is the ONLY place that ever
writes a customer_id into the public sessions.csv, and it does so
only for sessions that actually produced a successful login /
identity link — matching the locked cross-device identity design
(anonymous_id -> successful login -> identity_link -> customer_id).

Must run AFTER:
    04_generate_sessions.py
    05_generate_events.py
    03_generate_identity_links.py

Source:
    Fix for ORGEE Phase 2 review — sessions.customer_id was
    previously populated for 100% of sessions, bypassing the
    login-linking mechanism entirely.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SESSIONS_FILE = (
    PROJECT_ROOT / "data" / "enterprise" / "sessions" / "sessions.csv"
)

IDENTITY_FILE = (
    PROJECT_ROOT / "data" / "enterprise" / "identity" / "identity_links.csv"
)


def main() -> None:

    if not SESSIONS_FILE.exists():
        raise FileNotFoundError(f"Sessions file not found: {SESSIONS_FILE}")

    if not IDENTITY_FILE.exists():
        raise FileNotFoundError(f"Identity links file not found: {IDENTITY_FILE}")

    sessions = pd.read_csv(SESSIONS_FILE)
    identity_links = pd.read_csv(IDENTITY_FILE)

    link_map = identity_links.drop_duplicates(
        subset=["session_id"]
    ).set_index("session_id")["customer_id"]

    before_identified = sessions["customer_id"].notna().sum()

    sessions["customer_id"] = sessions["session_id"].map(link_map)

    after_identified = sessions["customer_id"].notna().sum()

    sessions.to_csv(SESSIONS_FILE, index=False)

    print("=" * 70)
    print("ORGEE — SESSION IDENTITY BACKFILL")
    print("=" * 70)
    print(f"[BACKFILL] Sessions total: {len(sessions):,}")
    print(f"[BACKFILL] Identified before backfill: {before_identified:,}")
    print(f"[BACKFILL] Identified after backfill:  {after_identified:,}")
    print(
        f"[BACKFILL] Identification rate: "
        f"{after_identified / len(sessions):.2%}"
    )
    print(f"[BACKFILL] Output written to:\n{SESSIONS_FILE}")


if __name__ == "__main__":
    main()
