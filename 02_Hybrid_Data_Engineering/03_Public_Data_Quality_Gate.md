# ORGEE — Public Data Quality Gate

## Omnichannel Retail & Growth Experimentation Engine

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Project Code:** ORGEE  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Public Data Quality Gate  
**Status:** LOCKED  

---

# 1. Purpose

This document formally evaluates whether the public Olist datasets
have passed the required data-quality gates before ORGEE proceeds to
the enterprise-generated data layer.

This gate is based on the completed:

- Public Data Profiling
- Public Data Relationship Validation
- Public Data Cleaning
- Timestamp Anomaly Investigation

The purpose is not to make the public dataset artificially perfect.

The purpose is to confirm that the public data is sufficiently
understood, validated, documented, and controlled for downstream
integration.

---

# 2. Public Dataset Foundation

The ORGEE public foundation consists of nine datasets:

| Dataset | Status |
|---|---|
| Orders | VALIDATED |
| Order Items | VALIDATED |
| Products | VALIDATED |
| Customers | VALIDATED |
| Sellers | VALIDATED |
| Payments | VALIDATED |
| Reviews | VALIDATED |
| Geolocation | VALIDATED |
| Category Translation | VALIDATED |

All nine datasets have been profiled.

Processed versions have been created separately from the raw data.

---

# 3. Raw Data Preservation Gate

## Result

**PASS**

The raw public datasets were not modified.

The cleaning process created a separate processed-public layer:

    data/
    │
    ├── raw/
    │   └── public/
    │
    ├── processed/
    │   └── public/
    │
    └── generated/

Rules confirmed:

- Raw files were not overwritten.
- Raw files were not manually edited.
- No synthetic records were added to public datasets.
- No public records were intentionally deleted because of business
  anomalies.
- Processed datasets were generated through Python.

---

# 4. Dataset Grain Gate

## Result

**PASS**

The original business grain of the public datasets has been
validated.

| Dataset | Confirmed Grain |
|---|---|
| Orders | One row per order |
| Order Items | One row per item within an order |
| Products | One row per product |
| Customers | One row per customer-order identity record |
| Sellers | One row per seller |
| Payments | One payment record |
| Reviews | One review record |
| Geolocation | One geographic observation |
| Category Translation | One category translation mapping |

Important findings:

### Orders

99,441 orders were identified.

### Order Items

112,650 item records were identified.

98,666 orders are represented in the order-item dataset.

9,803 orders contain multiple items.

Maximum items in one order:

21.

### Payments

99,440 orders are represented.

2,961 orders contain multiple payment records.

Maximum payment records for one order:

29.

### Reviews

98,673 orders are represented.

547 orders contain multiple review records.

Maximum review records for one order:

3.

These multiple-record relationships are legitimate and must not be
collapsed simply to create one row per order.

---

# 5. Primary Identifier Gate

## Result

**PASS**

The following identifiers passed uniqueness validation:

| Dataset | Identifier | Result |
|---|---|---|
| Orders | `order_id` | PASS |
| Products | `product_id` | PASS |
| Customers | `customer_id` | PASS |
| Sellers | `seller_id` | PASS |

No duplicate primary/business keys were detected.

---

# 6. Referential Integrity Gate

## Result

**PASS WITH DOCUMENTED EXCEPTION**

The following relationships passed:

    Orders → Customers
    Order Items → Orders
    Order Items → Products
    Order Items → Sellers
    Payments → Orders
    Reviews → Orders

All returned:

    Unmatched keys = 0

Therefore the core public transactional relationships are intact.

---

# 7. Category Translation Exception

## Result

**DOCUMENTED — NOT A DATASET FAILURE**

The following two product categories do not exist in the category
translation dataset:

    pc_gamer

    portateis_cozinha_e_preparadores_de_alimentos

Product categories in Products:

73

Translated categories:

71

Unmatched categories:

2

## Decision

These categories must NOT be deleted.

The original Portuguese category values must remain unchanged.

No English category name will be fabricated.

Where a translation is unavailable, the analytical translation field
may remain NULL.

The original category remains authoritative.

---

# 8. Customer Identity Gate

## Result

**PASS**

The public customer dataset contains two distinct identifiers:

    customer_id
    customer_unique_id

Observed values:

    customer_id unique:
    99,441

    customer_unique_id unique:
    96,096

    customer_unique_id duplicate records:
    3,345

## Decision

The repeated `customer_unique_id` values are legitimate and must not
be removed.

The distinction is preserved:

    customer_id
          ↓
    Customer-order record

    customer_unique_id
          ↓
    Persistent customer identity

This relationship will support later:

- Customer 360
- Retention
- Cohort analysis
- RFM
- CLV
- Customer segmentation

---

# 9. Missing-Value Gate

## Result

**PASS — LEGITIMATE MISSINGNESS PRESERVED**

Missing values were identified in several datasets.

### Orders

    order_approved_at                    160
    order_delivered_carrier_date       1,783
    order_delivered_customer_date      2,965

### Products

    product_category_name                 610
    product_name_lenght                    610
    product_description_lenght             610
    product_photos_qty                     610
    product_weight_g                         2
    product_length_cm                        2
    product_height_cm                        2
    product_width_cm                         2

### Reviews

    review_comment_title                87,656
    review_comment_message              58,247

## Decision

Missing values are not automatically replaced.

Rules:

- NULL is preserved where it represents legitimate missingness.
- Missing timestamps are not fabricated.
- Missing product characteristics are not fabricated.
- Missing review comments are not interpreted as negative reviews.
- Missing values are not converted to zero without a business reason.

---

# 10. Duplicate Gate

## Result

**PASS**

Duplicate handling followed dataset grain.

### Geolocation

The raw geolocation dataset contained:

    1,000,163 rows
    261,831 exact duplicate rows

The processed dataset contains:

    738,332 rows
    0 exact duplicate rows

## Decision

Exact duplicate geolocation records were removed.

This transformation is reproducible and documented.

No deduplication was performed using ZIP-code prefix alone because
multiple geographic observations can legitimately exist for a ZIP-code
prefix.

---

# 11. Data Type Gate

## Result

**PASS**

The processed datasets have been standardized for analytical use.

### Identifier fields

Identifiers remain identifier values and are not converted into
business measures.

### Timestamp fields

Relevant timestamp columns were converted to datetime values.

### Numeric fields

Relevant numerical columns were converted to numeric types.

Invalid values are not replaced with fabricated values.

---

# 12. Timestamp Integrity Gate

## Result

**REVIEW — DOCUMENTED SOURCE ANOMALIES**

Expected lifecycle:

    Purchase
       ↓
    Approval
       ↓
    Carrier Handover
       ↓
    Customer Delivery

Validation results:

    Purchase → Approval
    0 anomalies

    Approval → Carrier
    1,359 anomalies

    Carrier → Customer Delivery
    23 anomalies

    Approval → Customer Delivery
    61 anomalies

Total unique anomalous orders:

    1,382

Anomalies by order status:

    delivered    1,373
    shipped          9

---

# 13. Timestamp Anomaly Decision

The timestamp anomalies must NOT be corrected by inventing new
timestamps.

The original timestamps are retained.

The anomalous records are documented separately in:

    data/validation/phase_02_timestamp_anomalies.csv

## Locked rule

    Original timestamp
           ↓
    PRESERVE
           ↓
    Anomaly detected
           ↓
    FLAG
           ↓
    DOCUMENT

The following actions are prohibited:

- Deleting anomalous orders
- Replacing timestamps with estimated values
- Moving timestamps into chronological order artificially
- Generating replacement timestamps
- Modifying the original public source

The anomaly report remains the authoritative quality-review artifact.

---

# 14. Numeric Integrity Gate

## Result

**PASS — BASIC VALIDATION COMPLETED**

Numeric fields were converted to appropriate numeric types.

No values were removed merely because they appeared statistically
unusual.

Potential extreme values will be handled during analytical modelling
only when a defined business requirement exists.

---

# 15. Categorical Integrity Gate

## Result

**PASS WITH DOCUMENTED CATEGORY EXCEPTION**

Categorical values were standardized for basic formatting such as
leading and trailing whitespace.

Original business category values were not arbitrarily renamed.

The two untranslated categories remain preserved:

    pc_gamer

    portateis_cozinha_e_preparadores_de_alimentos

---

# 16. Processed Public Data Gate

## Result

**PASS**

Processed versions of all nine public datasets were created.

    data/processed/public/

The processed layer contains:

    olist_orders_dataset.csv
    olist_order_items_dataset.csv
    olist_products_dataset.csv
    olist_customers_dataset.csv
    olist_sellers_dataset.csv
    olist_order_payments_dataset.csv
    olist_order_reviews_dataset.csv
    olist_geolocation_dataset.csv
    product_category_name_translation.csv

The raw datasets remain separate.

---

# 17. Public Data Quality Summary

| Quality Area | Result |
|---|---|
| Dataset profiling | PASS |
| Dataset grain | PASS |
| Primary identifiers | PASS |
| Core referential integrity | PASS |
| Customer identity | PASS |
| Missing-value handling | PASS |
| Duplicate handling | PASS |
| Data-type standardization | PASS |
| Numeric validation | PASS |
| Category validation | PASS WITH EXCEPTION |
| Timestamp validation | REVIEW / DOCUMENTED |
| Raw-data preservation | PASS |
| Processed-data creation | PASS |

---

# 18. Final Public Data Decision

The ORGEE public dataset is considered:

    ANALYTICALLY USABLE

with the following documented exceptions:

    1. Two product categories have no translation mapping.

    2. 1,382 orders contain timestamp-ordering anomalies.

    3. Legitimate NULL values remain in the processed datasets.

These exceptions do not justify deleting or fabricating public data.

---

# 19. Public Data Quality Gate Status

## FINAL STATUS

    ╔══════════════════════════════════════════════╗
    ║                                              ║
    ║     ORGEE PUBLIC DATA FOUNDATION             ║
    ║                                              ║
    ║              QUALITY GATE                    ║
    ║                                              ║
    ║        ✅ PASSED WITH DOCUMENTED             ║
    ║              EXCEPTIONS                      ║
    ║                                              ║
    ╚══════════════════════════════════════════════╝

The public data foundation is now considered ready for the next
Phase 2 stage.

---

# 20. What This Gate Does NOT Approve

Passing this gate does NOT mean that the following have been built:

- Enterprise behavioral data
- Synthetic enterprise data
- Sessions
- Events
- Marketing data
- Inventory data
- Cross-device identity
- Customer 360
- Recommendation data
- Experiment data
- SQL warehouse
- Power BI model

These remain future Phase 2/Phase 3 activities according to the
locked ORGEE architecture.

---

# 21. Next Stage

The next stage is:

    PUBLIC DATA FOUNDATION
            ↓
    QUALITY GATE ✅
            ↓
    ENTERPRISE DATA REQUIREMENTS
            ↓
    ENTITY DESIGN
            ↓
    SYNTHETIC DATA GENERATION
            ↓
    CROSS-DEVICE IDENTITY
            ↓
    CUSTOMER 360 INTEGRATION
            ↓
    HYBRID DATASET
            ↓
    PHASE 3 — SQL DATA WAREHOUSE

Before synthetic generation begins, the enterprise data layer must
be designed.

The design must define:

- Required enterprise entities
- Entity grain
- Primary identifiers
- Foreign keys
- Required columns
- Relationships to public data
- Expected row volumes
- Generation rules
- Business purpose
- Validation rules

No synthetic enterprise data should be generated before this design
is locked.

---

# 22. Phase 2 Gate Rule

Once this document is approved, the public-data foundation must not
be redesigned during synthetic-data generation.

Any future change requires a documented critical technical reason.

---

# 23. Status

**ORGEE — PUBLIC DATA QUALITY GATE: LOCKED**

The public data foundation has passed the required quality gate with
documented exceptions.

The project may now proceed to the **Enterprise Data Requirements
and Entity Design** stage.

---

# FINAL PRINCIPLE

    Understand
        ↓
    Validate
        ↓
    Document
        ↓
    Preserve
        ↓
    Clean
        ↓
    Validate Again
        ↓
    Approve
        ↓
    Generate Enterprise Data