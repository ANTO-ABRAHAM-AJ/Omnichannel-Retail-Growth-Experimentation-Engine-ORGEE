from pathlib import Path
import pandas as pd


# =============================================================================
# ORGEE — PHASE 2 TIMESTAMP ANOMALY INVESTIGATION
# Omnichannel Retail & Growth Experimentation Engine
# =============================================================================

PROJECT_DIR = Path(
    r"C:\Users\ANTO ABRAHAM AJ\Downloads\Omnichannel Retail & Growth Experimentation Engine (ORGEE)"
)

PROCESSED_DATA_DIR = PROJECT_DIR / "data" / "processed" / "public"
OUTPUT_DIR = PROJECT_DIR / "data" / "validation"

ORDERS_FILE = PROCESSED_DATA_DIR / "olist_orders_dataset.csv"


# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "phase_02_timestamp_anomalies.csv"


# =============================================================================
# HEADER
# =============================================================================

print("=" * 80)
print("ORGEE — PHASE 2 TIMESTAMP ANOMALY INVESTIGATION")
print("Omnichannel Retail & Growth Experimentation Engine")
print("=" * 80)

print()
print("Project Directory:")
print(PROJECT_DIR)

print()
print("Processed Orders File:")
print(ORDERS_FILE)

print()
print("Output Directory:")
print(OUTPUT_DIR)


# =============================================================================
# LOAD DATA
# =============================================================================

print()
print("-" * 80)
print("LOADING PROCESSED ORDERS DATA")
print("-" * 80)

if not ORDERS_FILE.exists():
    raise FileNotFoundError(
        f"\nProcessed orders file was not found:\n{ORDERS_FILE}\n"
        "Make sure Phase 2 public-data cleaning has completed successfully."
    )

df = pd.read_csv(ORDERS_FILE)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# =============================================================================
# REQUIRED TIMESTAMP COLUMNS
# =============================================================================

timestamp_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

missing_columns = [
    column for column in timestamp_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"\nRequired timestamp columns are missing:\n{missing_columns}"
    )


# =============================================================================
# CONVERT TIMESTAMP COLUMNS
# =============================================================================

print()
print("-" * 80)
print("CONVERTING TIMESTAMP COLUMNS")
print("-" * 80)

for column in timestamp_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )

print("Timestamp conversion complete.")


# =============================================================================
# TIMESTAMP ANOMALY RULES
# =============================================================================

# Rule 1:
# Approval should not occur before purchase.
invalid_purchase_approval = (
    df["order_purchase_timestamp"].notna()
    & df["order_approved_at"].notna()
    & (
        df["order_approved_at"]
        < df["order_purchase_timestamp"]
    )
)


# Rule 2:
# Carrier handoff should not occur before approval.
invalid_approval_carrier = (
    df["order_approved_at"].notna()
    & df["order_delivered_carrier_date"].notna()
    & (
        df["order_delivered_carrier_date"]
        < df["order_approved_at"]
    )
)


# Rule 3:
# Customer delivery should not occur before carrier handoff.
invalid_carrier_customer = (
    df["order_delivered_carrier_date"].notna()
    & df["order_delivered_customer_date"].notna()
    & (
        df["order_delivered_customer_date"]
        < df["order_delivered_carrier_date"]
    )
)


# Rule 4:
# Customer delivery should not occur before approval.
invalid_approval_customer = (
    df["order_approved_at"].notna()
    & df["order_delivered_customer_date"].notna()
    & (
        df["order_delivered_customer_date"]
        < df["order_approved_at"]
    )
)


# =============================================================================
# PRINT SUMMARY
# =============================================================================

print()
print("-" * 80)
print("TIMESTAMP ANOMALY SUMMARY")
print("-" * 80)

print(
    f"Purchase → Approval anomalies: "
    f"{invalid_purchase_approval.sum():,}"
)

print(
    f"Approval → Carrier anomalies: "
    f"{invalid_approval_carrier.sum():,}"
)

print(
    f"Carrier → Customer Delivery anomalies: "
    f"{invalid_carrier_customer.sum():,}"
)

print(
    f"Approval → Customer Delivery anomalies: "
    f"{invalid_approval_customer.sum():,}"
)


# =============================================================================
# BUILD ANOMALY DATASET
# =============================================================================

anomaly_mask = (
    invalid_purchase_approval
    | invalid_approval_carrier
    | invalid_carrier_customer
    | invalid_approval_customer
)

anomalies = df.loc[
    anomaly_mask,
    [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
].copy()


# =============================================================================
# ADD ANOMALY FLAGS
# =============================================================================

anomalies["purchase_approval_issue"] = (
    invalid_purchase_approval.loc[anomalies.index]
)

anomalies["approval_carrier_issue"] = (
    invalid_approval_carrier.loc[anomalies.index]
)

anomalies["carrier_customer_issue"] = (
    invalid_carrier_customer.loc[anomalies.index]
)

anomalies["approval_customer_issue"] = (
    invalid_approval_customer.loc[anomalies.index]
)


# =============================================================================
# CALCULATE TIME DIFFERENCES
# =============================================================================

anomalies["approval_minus_purchase_hours"] = (
    (
        anomalies["order_approved_at"]
        - anomalies["order_purchase_timestamp"]
    ).dt.total_seconds() / 3600
)


anomalies["carrier_minus_approval_hours"] = (
    (
        anomalies["order_delivered_carrier_date"]
        - anomalies["order_approved_at"]
    ).dt.total_seconds() / 3600
)


anomalies["customer_minus_carrier_hours"] = (
    (
        anomalies["order_delivered_customer_date"]
        - anomalies["order_delivered_carrier_date"]
    ).dt.total_seconds() / 3600
)


# =============================================================================
# ANOMALY CLASSIFICATION
# =============================================================================

def classify_anomaly(row):

    issues = []

    if row["purchase_approval_issue"]:
        issues.append("PURCHASE_AFTER_APPROVAL")

    if row["approval_carrier_issue"]:
        issues.append("APPROVAL_AFTER_CARRIER")

    if row["carrier_customer_issue"]:
        issues.append("CARRIER_AFTER_CUSTOMER_DELIVERY")

    if row["approval_customer_issue"]:
        issues.append("APPROVAL_AFTER_CUSTOMER_DELIVERY")

    return " | ".join(issues)


anomalies["anomaly_type"] = anomalies.apply(
    classify_anomaly,
    axis=1
)


# =============================================================================
# SAVE COMPLETE ANOMALY REPORT
# =============================================================================

anomalies.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("-" * 80)
print("ANOMALY REPORT CREATED")
print("-" * 80)

print(f"Total anomalous orders: {len(anomalies):,}")
print(f"Saved to:")
print(OUTPUT_FILE)


# =============================================================================
# SHOW REPRESENTATIVE RECORDS
# =============================================================================

print()
print("-" * 80)
print("REPRESENTATIVE ANOMALIES")
print("-" * 80)

if len(anomalies) == 0:

    print("No timestamp anomalies detected.")

else:

    display_columns = [
        "order_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "anomaly_type",
    ]

    print(
        anomalies[
            display_columns
        ]
        .head(20)
        .to_string(index=False)
    )


# =============================================================================
# ANOMALY TYPE COUNTS
# =============================================================================

print()
print("-" * 80)
print("ANOMALY TYPE COUNTS")
print("-" * 80)

print(
    anomalies["anomaly_type"]
    .value_counts()
    .to_string()
)


# =============================================================================
# ORDER STATUS BREAKDOWN
# =============================================================================

print()
print("-" * 80)
print("ANOMALIES BY ORDER STATUS")
print("-" * 80)

print(
    anomalies["order_status"]
    .value_counts(dropna=False)
    .to_string()
)


# =============================================================================
# FINAL STATUS
# =============================================================================

print()
print("=" * 80)
print("ORGEE — TIMESTAMP INVESTIGATION COMPLETE")
print("=" * 80)

print()
print("IMPORTANT:")
print("• Raw public data was NOT modified.")
print("• Processed public data was NOT modified.")
print("• No records were deleted.")
print("• No synthetic data was generated.")
print("• No SQL warehouse was created.")
print("• Anomaly records were exported for review.")

print()
print("Next step:")
print("Review the anomaly report before defining the final")
print("Phase 2 timestamp-quality rules.")

print("=" * 80)