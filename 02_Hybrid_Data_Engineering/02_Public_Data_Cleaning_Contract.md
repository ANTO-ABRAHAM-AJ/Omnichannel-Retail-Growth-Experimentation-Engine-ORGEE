# ORGEE — Public Data Cleaning Contract

## Omnichannel Retail & Growth Experimentation Engine

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Project Code:** ORGEE  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Public Data Cleaning Contract  
**Status:** LOCKED  

---

# 1. Purpose

This document defines the controlled cleaning and standardization rules
for the public datasets used as the transactional and product foundation
of ORGEE.

The purpose of cleaning is to improve analytical reliability while
preserving the original business meaning, relationships, and grain of
the public datasets.

The raw public datasets must never be modified.

---

# 2. Data Processing Principle

The ORGEE data pipeline follows:

```text
Raw Public Data
        ↓
Controlled Cleaning
        ↓
Validation
        ↓
Processed Public Data
        ↓
Hybrid Data Integration
        ↓
Enterprise SQL Warehouse
```

Cleaning must be:

- Reproducible
- Documented
- Minimal
- Deterministic
- Business-preserving
- Validated

---

# 3. Raw Data Preservation

The original public datasets are treated as immutable source data.

Rules:

- Raw CSV files must never be overwritten.
- Raw files must never be manually edited.
- Cleaning must be performed through Python scripts.
- Every transformation must be reproducible.
- Processed datasets must be stored separately from raw datasets.
- The raw-to-processed transformation must remain traceable.

---

# 4. Dataset Scope

The public data foundation currently contains:

1. orders
2. order_items
3. products
4. customers
5. sellers
6. payments
7. reviews
8. geolocation
9. category_translation

All nine datasets are retained as part of the public-data foundation.

---

# 5. Grain Preservation

The original grain of each dataset must be preserved.

## Orders

Grain:

One row per order.

Primary business identifier:

`order_id`

---

## Order Items

Grain:

One row per item within an order.

Business identifiers:

`order_id`
`order_item_id`

Multiple items per order must remain separate.

---

## Products

Grain:

One row per product.

Business identifier:

`product_id`

`product_id` must remain unique.

---

## Customers

Grain:

One row per customer-order identity record represented by
`customer_id`.

Identifiers:

`customer_id`
`customer_unique_id`

Both identifiers must be preserved.

`customer_unique_id` must not be incorrectly deduplicated into
`customer_id`.

---

## Sellers

Grain:

One row per seller.

Business identifier:

`seller_id`

`seller_id` must remain unique.

---

## Payments

Grain:

One payment record per payment sequence associated with an order.

Identifiers:

`order_id`
`payment_sequential`

Multiple payment records for an order must remain separate.

---

## Reviews

Grain:

One review record associated with an order.

Identifiers:

`review_id`
`order_id`

Multiple review records must not be arbitrarily collapsed.

---

## Geolocation

Grain:

One geolocation observation associated with a ZIP-code prefix/location
record.

The dataset contains duplicate rows and must be handled according to
the geolocation-specific rule defined below.

---

## Category Translation

Grain:

One category translation mapping.

Business identifier:

`product_category_name`

The translation dataset must not be used as the primary product table.

---

# 6. Data Type Standardization

The following fields must be converted to appropriate analytical
data types during processing.

## Identifier Columns

Identifiers remain strings.

Examples:

- order_id
- customer_id
- customer_unique_id
- product_id
- seller_id
- review_id

Leading zeros and identifier formatting must not be destroyed.

---

## Timestamp Columns

Timestamp fields must be converted from strings into proper datetime
types.

Examples:

- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date
- shipping_limit_date
- review_creation_date
- review_answer_timestamp

---

## Numeric Columns

Numeric measurements must be converted to appropriate numeric types.

Examples:

- price
- freight_value
- payment_value
- payment_installments
- review_score
- product_weight_g
- product_length_cm
- product_height_cm
- product_width_cm

---

# 7. Missing Value Rules

Missing values must not automatically be replaced with zero.

A missing value must be interpreted according to the business meaning
of the field.

---

## Orders

Known missing fields:

- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date

Rule:

Preserve legitimate missing timestamps as NULL.

Do not replace missing delivery timestamps with artificial dates.

---

## Products

Known missing fields include:

- product_category_name
- product_name_lenght
- product_description_lenght
- product_photos_qty
- product_weight_g
- product_length_cm
- product_height_cm
- product_width_cm

Rule:

Preserve legitimate missing product attributes as NULL unless a
documented downstream analytical transformation requires otherwise.

Do not fabricate product characteristics.

---

## Reviews

Known missing fields:

- review_comment_title
- review_comment_message

Rule:

Preserve missing textual review fields as NULL.

A missing comment does not mean a negative review.

---

# 8. Duplicate Handling

Duplicate handling must be based on dataset grain.

---

## Orders

No duplicate rows were identified.

Rule:

Do not remove any rows solely because of repeated values in
non-key columns.

---

## Order Items

No duplicate rows were identified.

Rule:

Preserve the original item-level records.

---

## Products

No duplicate rows were identified.

`product_id` is unique.

Rule:

Preserve all product records.

---

## Customers

No duplicate rows were identified at the row level.

`customer_id` is unique.

Rule:

Preserve all records.

Do not remove records because `customer_unique_id` appears multiple
times.

The repeated `customer_unique_id` values represent an important
customer-identity relationship and must be retained.

---

## Sellers

No duplicate rows were identified.

`seller_id` is unique.

Rule:

Preserve all seller records.

---

## Payments

No duplicate rows were identified.

Multiple payment records for one order are legitimate.

Rule:

Do not deduplicate payment records using `order_id` alone.

---

## Reviews

No duplicate rows were identified at the complete-row level.

Multiple review records associated with an order must be preserved
unless a later business rule explicitly defines an analytical
aggregation.

---

## Geolocation

The geolocation dataset contains duplicate rows.

Rule:

Duplicate geolocation records may be removed only when the complete
record is identical.

This transformation must be documented and reproducible.

---

## Category Translation

No duplicate rows were identified.

Rule:

Preserve the mapping records.

---

# 9. Referential Integrity Rules

The following validated relationships must remain intact.

```text
ORDERS
   │
   └── customer_id → CUSTOMERS.customer_id

ORDER_ITEMS
   │
   ├── order_id → ORDERS.order_id
   ├── product_id → PRODUCTS.product_id
   └── seller_id → SELLERS.seller_id

PAYMENTS
   │
   └── order_id → ORDERS.order_id

REVIEWS
   │
   └── order_id → ORDERS.order_id

PRODUCTS
   │
   └── product_category_name → CATEGORY_TRANSLATION
```

The first six relationships passed validation.

---

# 10. Category Translation Exception

Relationship validation identified two product categories that do not
exist in the translation dataset:

- `pc_gamer`
- `portateis_cozinha_e_preparadores_de_alimentos`

Rule:

These product categories must not be deleted.

Their original category values must be preserved.

Where English translation is unavailable, the processed dataset may
retain the original category value and represent the translated value
as NULL.

No category name may be fabricated.

---

# 11. Customer Identity Rules

Two customer identifiers are retained:

`customer_id`

and

`customer_unique_id`

Rules:

- `customer_id` remains the order/customer-instance identifier.
- `customer_unique_id` remains the persistent customer identity.
- Both fields must be preserved.
- They must not be merged into a single field.
- Customer-level analytics such as retention, RFM and CLV should use
  the appropriate persistent identity level.

This distinction is important for Customer 360.

---

# 12. Timestamp Integrity

Timestamp fields must be validated for:

- Parseability
- Missingness
- Logical ordering
- Invalid future/past relationships where applicable

The following order lifecycle must be respected where timestamps exist:

```text
Order Purchase
      ↓
Order Approval
      ↓
Carrier Handover
      ↓
Customer Delivery
```

The cleaning process must not invent missing timestamps merely to
satisfy chronological ordering.

---

# 13. Numeric Integrity

Numeric fields must be checked for:

- Invalid data types
- Unexpected negative values
- Impossible measurements
- Null handling
- Extreme values requiring investigation

Values must not be removed solely because they are statistically
unusual.

Potential outliers must first be evaluated against business meaning.

---

# 14. Categorical Standardization

Categorical values may be standardized for:

- Leading/trailing whitespace
- Consistent text representation
- Empty strings

However:

Original business categories must not be renamed arbitrarily.

Any mapping or standardization must be documented.

---

# 15. Data Quality Validation After Cleaning

After processing, the following checks are mandatory:

### Completeness

Confirm expected columns exist.

### Uniqueness

Validate primary/business keys.

### Referential Integrity

Re-run relationship validation.

### Grain

Confirm the original table grain remains valid.

### Data Types

Confirm standardized data types.

### Missing Values

Confirm missing-value treatment follows this contract.

### Range Validation

Check numeric and categorical values for invalid records.

### Timestamp Validation

Check chronological consistency.

---

# 16. No Fabricated Data

The public-data cleaning process must never:

- Invent customers
- Invent orders
- Invent products
- Invent sellers
- Invent payments
- Invent reviews
- Invent timestamps
- Invent product attributes
- Invent category translations

Synthetic enterprise data will be generated separately.

---

# 17. Separation From Synthetic Data

Public data cleaning and enterprise-data generation are separate
activities.

Public data:

```text
Public Source
     ↓
Cleaning
     ↓
Validation
     ↓
Processed Public Data
```

Enterprise-generated data:

```text
Business Requirements
        ↓
Synthetic Data Design
        ↓
Python Generation
        ↓
Validation
```

They will only be integrated after both sides independently pass
validation.

---

# 18. Cross-Device Identity

Cross-device identity resolution does not modify the original public
customer identifiers.

It will be implemented later using the synthetic customer-event
layer.

The locked mechanism is:

```text
Anonymous ID
     ↓
Login Event
     ↓
Customer ID
     ↓
Identity Link
```

This remains separate from public-data cleaning.

---

# 19. Bronze / Silver / Gold Organization

If implemented, the processing organization may follow:

```text
Bronze
Raw Public Data
      ↓
Silver
Cleaned / Standardized Data
      ↓
Gold
Analytical Data Warehouse
```

This is an implementation organization only.

It does not create additional project phases.

---

# 20. Processing Output

The cleaning process must create a separate processed-data location.

Recommended structure:

```text
data/
│
├── raw/
│   └── public/
│
├── processed/
│   └── public/
│
└── generated/
```

Raw files remain untouched.

Processed files are generated by code.

Generated enterprise datasets remain separate from public processed
datasets until the integration stage.

---

# 21. Locked Cleaning Principles

The following principles are mandatory:

1. Preserve business meaning.
2. Preserve table grain.
3. Preserve valid relationships.
4. Preserve original identifiers.
5. Never fabricate missing information.
6. Never silently delete records.
7. Never overwrite raw data.
8. Make every transformation reproducible.
9. Validate after transformation.
10. Document exceptions.

---

# 22. Phase 2 Execution Gate

The public-data cleaning stage is considered complete only when:

- Cleaning script is created.
- Raw files remain unchanged.
- Processed files are generated separately.
- Data types are validated.
- Missing-value rules are applied.
- Duplicate rules are applied.
- Referential integrity is revalidated.
- Grain is revalidated.
- Timestamp integrity is checked.
- Numeric integrity is checked.
- Category translation exceptions are documented.
- Processing results are documented.

Only after these checks pass will ORGEE proceed to the
enterprise-data generation stage.

---

# 23. Status

**PUBLIC DATA CLEANING CONTRACT — LOCKED**

The rules defined in this document are the approved rules for
processing the ORGEE public datasets.

No cleaning transformation should be added during execution unless
a critical technical issue is discovered.

Any critical exception must be documented before implementation.

---

# FINAL PRINCIPLE

```text
Raw Data
   ↓
Understand
   ↓
Validate
   ↓
Define Rules
   ↓
Clean Reproducibly
   ↓
Validate Again
   ↓
Integrate
   ↓
Analyze
```

Business meaning must always take priority over cosmetic cleaning.