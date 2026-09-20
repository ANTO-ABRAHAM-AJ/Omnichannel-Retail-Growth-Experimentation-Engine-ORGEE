# ORGEE — Public Data Contract

## Omnichannel Retail & Growth Experimentation Engine (ORGEE)

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Public Data Contract  
**Status:** LOCKED  

---

# 1. Purpose

This document defines the contract for the public datasets used as the transactional and product foundation of ORGEE.

The purpose of the contract is to establish:

- Dataset ownership and purpose
- Dataset grain
- Primary identifiers
- Foreign-key relationships
- Business meaning
- Data-quality expectations
- Downstream analytical usage
- Core versus supporting datasets

The public datasets will remain unchanged in their raw form.

Cleaning, standardization, transformation, and integration will occur in later data-engineering steps.

---

# 2. Public Data Source

The public foundation consists of the Olist Brazilian e-commerce dataset.

The dataset provides information covering:

- Orders
- Order items
- Products
- Customers
- Sellers
- Payments
- Reviews
- Geolocation
- Product category translation

The public dataset provides the transactional and product foundation of ORGEE.

Enterprise behavioral data required for the omnichannel product-analytics story will be generated separately using Python.

---

# 3. Public Data Architecture

```text
                    PUBLIC DATA
                         |
        +----------------+----------------+
        |                |                |
     Orders         Order Items       Products
        |                |                |
        |                |                |
    Customers       Sellers          Categories
        |                                 |
        +------------ Supporting ---------+
        |
   Payments / Reviews / Geolocation

The public data will later be integrated with enterprise-generated data.

PUBLIC DATA
     |
     +-----------------------------+
     |                             |
Orders / Products           Supporting Data
     |                             |
     +-------------+---------------+
                   |
             DATA ENGINEERING
                   |
          ENTERPRISE DATA
                   |
          SQL DATA WAREHOUSE
```

# 4. Dataset Classification

## 4.1 Core Public Datasets

These datasets form the primary transactional and product foundation.

| Dataset | File | Primary Purpose |
|---|---|---|
| Orders | `olist_orders_dataset.csv` | Order lifecycle and customer-order relationships |
| Order Items | `olist_order_items_dataset.csv` | Products, sellers and monetary item-level transactions |
| Products | `olist_products_dataset.csv` | Product attributes and categories |

## 4.2 Supporting Public Datasets

These datasets enrich the core analytical model.

| Dataset | File | Primary Purpose |
|---|---|---|
| Customers | `olist_customers_dataset.csv` | Customer identity and geography |
| Sellers | `olist_sellers_dataset.csv` | Seller identity and geography |
| Payments | `olist_order_payments_dataset.csv` | Payment method and payment value |
| Reviews | `olist_order_reviews_dataset.csv` | Customer review and satisfaction information |
| Geolocation | `olist_geolocation_dataset.csv` | Geographic enrichment |
| Category Translation | `product_category_name_translation.csv` | Product category translation |

Supporting datasets will only be used where they contribute to a defined business or analytical requirement.

---

# 5. Dataset Contracts

## 5.1 Orders

**Dataset**

`olist_orders_dataset.csv`

**Grain**

One record represents one order.

**Profiling Result**

- Rows: 99,441
- Columns: 8
- Duplicate rows: 0

**Primary Identifier**

`order_id`

Expected property:

- Unique at the order level

**Key Relationships**

`customer_id` identifies the customer record associated with the order.

`order_id` connects the order to:

- Order Items
- Payments
- Reviews

**Columns**

| Column | Business Meaning |
|---|---|
| `order_id` | Unique order identifier |
| `customer_id` | Customer identifier associated with the order |
| `order_status` | Current/status outcome of the order |
| `order_purchase_timestamp` | Timestamp when the order was placed |
| `order_approved_at` | Timestamp when payment/order approval occurred |
| `order_delivered_carrier_date` | Date/time handed to carrier |
| `order_delivered_customer_date` | Date/time delivered to customer |
| `order_estimated_delivery_date` | Estimated delivery date |

**Missing Values**

Observed missing values:

- `order_approved_at`: 160
- `order_delivered_carrier_date`: 1,783
- `order_delivered_customer_date`: 2,965

These missing values must not be blindly replaced.

Their meaning depends on the order lifecycle and status.

**Downstream Usage**

- Revenue/order analysis
- Order lifecycle analysis
- Delivery analysis
- Customer purchase behavior
- Customer journey
- Retention
- Cohort analysis
- RFM
- CLV
- Power BI

---

## 5.2 Order Items

**Dataset**

`olist_order_items_dataset.csv`

**Grain**

One record represents one product item within an order.

An order may contain multiple order-item records.

**Profiling Result**

- Rows: 112,650
- Columns: 7
- Duplicate rows: 0
- Unique orders: 98,666

**Primary / Composite Identifier**

The analytical grain is:

`order_id + order_item_id`

`order_item_id` alone is **NOT** a global unique identifier.

**Key Relationships**

```text
order_id
    ↓
Orders

product_id
    ↓
Products

seller_id
    ↓
Sellers
```

**Columns**

| Column | Business Meaning |
|---|---|
| `order_id` | Order identifier |
| `order_item_id` | Item sequence within an order |
| `product_id` | Product identifier |
| `seller_id` | Seller identifier |
| `shipping_limit_date` | Seller shipping deadline |
| `price` | Item selling price |
| `freight_value` | Freight/shipping value |

**Downstream Usage**

- GMV
- Revenue analysis
- AOV
- Product performance
- Category performance
- Seller performance
- Product recommendations
- Customer purchase behavior

---

## 5.3 Products

**Dataset**

`olist_products_dataset.csv`

**Grain**

One record represents one product.

**Profiling Result**

- Rows: 32,951
- Columns: 9
- Duplicate rows: 0
- Unique `product_id`: 32,951

**Primary Identifier**

`product_id`

**Key Relationship**

```text
product_id
    ↓
Order Items
```

**Columns**

| Column | Business Meaning |
|---|---|
| `product_id` | Unique product identifier |
| `product_category_name` | Product category |
| `product_name_lenght` | Product-name length |
| `product_description_lenght` | Product-description length |
| `product_photos_qty` | Number of product photos |
| `product_weight_g` | Product weight |
| `product_length_cm` | Product length |
| `product_height_cm` | Product height |
| `product_width_cm` | Product width |

**Missing Values**

`product_category_name` and several product-attribute fields contain missing values.

Observed missing values must be handled during the cleaning stage.

Raw values will not be overwritten.

**Downstream Usage**

- Product analytics
- Category analytics
- Product recommendation
- Product performance
- Product attributes
- Business segmentation

---

## 5.4 Customers

**Dataset**

`olist_customers_dataset.csv`

**Grain**

One record represents one customer-order-level customer record.

The dataset contains both:

- `customer_id`
- `customer_unique_id`

These identifiers must not be treated as interchangeable.

**Profiling Result**

- Rows: 99,441
- Columns: 5
- `customer_id`: 99,441 unique
- `customer_unique_id`: 96,096 unique

**Identifiers**

`customer_id`

Used to connect an order to its customer record.

`customer_unique_id`

Represents the persistent customer identity across the dataset.

This distinction is critical for:

- Repeat purchase analysis
- RFM
- CLV
- Cohort analysis
- Retention
- Customer 360

**Columns**

| Column | Business Meaning |
|---|---|
| `customer_id` | Order-associated customer identifier |
| `customer_unique_id` | Persistent customer identity |
| `customer_zip_code_prefix` | Customer geographic prefix |
| `customer_city` | Customer city |
| `customer_state` | Customer state |

**Downstream Usage**

- Customer analytics
- RFM
- CLV
- Cohorts
- Retention
- Customer segmentation
- Customer 360
- Geographic analysis

---

## 5.5 Sellers

**Dataset**

`olist_sellers_dataset.csv`

**Grain**

One record represents one seller.

**Profiling Result**

- Rows: 3,095
- Columns: 4
- Unique `seller_id`: 3,095
- Duplicate rows: 0

**Primary Identifier**

`seller_id`

**Key Relationship**

```text
seller_id
    ↓
Order Items
```

**Columns**

| Column | Business Meaning |
|---|---|
| `seller_id` | Unique seller identifier |
| `seller_zip_code_prefix` | Seller geographic prefix |
| `seller_city` | Seller city |
| `seller_state` | Seller state |

**Downstream Usage**

- Seller analytics
- Marketplace analytics
- Seller performance
- Fulfillment analysis
- Seller quality analysis

---

## 5.6 Payments

**Dataset**

`olist_order_payments_dataset.csv`

**Grain**

One record represents one payment record associated with an order.

An order may contain multiple payment records.

**Profiling Result**

- Rows: 103,886
- Columns: 5
- Unique orders: 99,440

**Key Relationship**

```text
order_id
    ↓
Orders
```

**Columns**

| Column | Business Meaning |
|---|---|
| `order_id` | Order identifier |
| `payment_sequential` | Payment sequence within an order |
| `payment_type` | Payment method |
| `payment_installments` | Number of installments |
| `payment_value` | Payment amount |

**Downstream Usage**

- Payment analysis
- Payment-method analysis
- Revenue validation
- Customer behavior
- AOV
- Payment segmentation

---

## 5.7 Reviews

**Dataset**

`olist_order_reviews_dataset.csv`

**Grain**

One record represents a review record associated with an order.

Multiple records may exist for the same order.

**Profiling Result**

- Rows: 99,224
- Columns: 7
- Duplicate rows: 0
- Unique `review_id`: 98,410
- Unique `order_id`: 98,673

**Key Relationship**

```text
order_id
    ↓
Orders
```

**Columns**

| Column | Business Meaning |
|---|---|
| `review_id` | Review identifier |
| `order_id` | Associated order |
| `review_score` | Customer review score |
| `review_comment_title` | Review title |
| `review_comment_message` | Review text |
| `review_creation_date` | Review creation date |
| `review_answer_timestamp` | Review response timestamp |

**Missing Values**

High missingness exists in:

- `review_comment_title`
- `review_comment_message`

These fields must not be treated as automatically erroneous.

A missing review comment may simply mean that the customer provided a score without written feedback.

**Downstream Usage**

- Customer experience
- Product satisfaction
- Review analytics
- Product analytics
- Customer behavior

---

## 5.8 Geolocation

**Dataset**

`olist_geolocation_dataset.csv`

**Grain**

Geographic records associated with ZIP-code prefixes.

The dataset contains multiple records for some ZIP-code prefixes.

**Profiling Result**

- Rows: 1,000,163
- Columns: 5
- Duplicate rows: 261,831

**Columns**

| Column | Business Meaning |
|---|---|
| `geolocation_zip_code_prefix` | ZIP-code prefix |
| `geolocation_lat` | Latitude |
| `geolocation_lng` | Longitude |
| `geolocation_city` | City |
| `geolocation_state` | State |

**Important Data Quality Observation**

The profiling identified 261,831 duplicate rows.

Therefore:

> DO NOT blindly load geolocation as a unique ZIP-code dimension.

The table requires controlled transformation before analytical use.

**Downstream Usage**

- Geographic analysis
- Customer geography
- Seller geography
- Regional analysis
- Delivery analysis

---

## 5.9 Category Translation

**Dataset**

`product_category_name_translation.csv`

**Grain**

One record represents one product-category translation.

**Profiling Result**

- Rows: 71
- Columns: 2
- Duplicate rows: 0
- 71 unique categories

**Columns**

| Column | Business Meaning |
|---|---|
| `product_category_name` | Original category name |
| `product_category_name_english` | English category name |

**Key Relationship**

```text
product_category_name
        ↓
Products
```

**Downstream Usage**

- Product analytics
- Category analysis
- English-language reporting
- Power BI

---

# 6. Relationship Map

The expected analytical relationships are:

```text
CUSTOMERS
   |
   | customer_id
   ↓
ORDERS
   |
   | order_id
   +------------------+
   |                  |
   ↓                  ↓
ORDER ITEMS        PAYMENTS
   |
   +------------------+
   |                  |
   ↓                  ↓
PRODUCTS           SELLERS
   |
   |
   ↓
CATEGORY TRANSLATION
```

Reviews connect through:

```text
ORDERS
   |
   | order_id
   ↓
REVIEWS
```

Geolocation enriches customers and sellers through ZIP-code prefixes.

---

# 7. Important Grain Rules

The following rules are locked.

### Orders

1 row = 1 order.

### Order Items

1 row = 1 item within an order.

An order may contain multiple items.

### Products

1 row = 1 product.

### Customers

Customer identity must distinguish:

`customer_id`

from:

`customer_unique_id`

### Payments

An order may contain multiple payment records.

### Reviews

An order may contain multiple review records.

### Sellers

1 row = 1 seller.

### Geolocation

Multiple geographic records may exist for a ZIP-code prefix.

---

# 8. Data Quality Contract

Before analytical use, the public datasets must be checked for:

- Duplicate records
- Missing values
- Invalid data types
- Invalid identifiers
- Broken relationships
- Unexpected nulls
- Invalid timestamps
- Invalid numerical values
- Referential-integrity violations
- Unexpected category values

The raw public datasets will remain unchanged.

All transformations will occur in processed layers.

---

# 9. Raw Data Preservation Rule

The original public files are treated as raw source data.

```text
RAW PUBLIC DATA
       ↓
DO NOT MODIFY
       ↓
PROFILE
       ↓
VALIDATE
       ↓
TRANSFORMED DATA
```

The original CSV files must remain reproducible and recoverable.

---

# 10. Public Data → ORGEE Business Questions

The public datasets must support the following business questions.

## Customer

- Who are our most valuable customers?
- How frequently do customers purchase?
- Which customers return?
- Which customer segments generate the most value?

## Product

- Which products generate the most revenue?
- Which categories perform best?
- Which products have strong demand?
- Which product attributes can support personalization?

## Marketplace

- Which sellers perform best?
- Which sellers have higher cancellation or return-related issues?
- How does seller performance affect marketplace outcomes?

## Order

- How are orders changing over time?
- Which order statuses dominate?
- Where are operational problems occurring?

## Payment

- Which payment methods are most common?
- How does payment behavior differ across customers?

## Customer Experience

- What review scores are customers giving?
- Which products or orders have weaker satisfaction?

## Geography

- Which regions generate the most customers and orders?
- How does geography relate to seller/customer distribution?

---

# 11. Public Data Limitations

The public dataset does not directly provide the complete behavioral event layer required by ORGEE.

The following enterprise behavioral concepts are therefore not assumed to exist in the public data:

- Anonymous user events
- Product impressions
- Search events
- Click events
- Add-to-cart events
- Checkout events
- Session identifiers
- Device identifiers
- App/web platform events
- Marketing campaign exposure
- Recommendation impressions
- Experiment assignment

These will be addressed through the enterprise-generated data layer in Phase 2.

---

# 12. Hybrid Data Principle

ORGEE will use a hybrid data ecosystem.

```text
                 ORGEE DATA ECOSYSTEM
                         |
             +-----------+-----------+
             |                       |
       PUBLIC DATA            GENERATED DATA
             |                       |
       Transactions            Behavioral Events
       Products                Sessions
       Customers               Marketing
       Sellers                 Inventory
       Payments                Reviews enrichment
       Reviews                 Identity signals
             |                       |
             +-----------+-----------+
                         |
                  DATA INTEGRATION
                         |
                 SQL DATA WAREHOUSE
                         |
              PRODUCT ANALYTICS
```

The public dataset provides realistic transactional and product data.

Python-generated data provides the behavioral and enterprise dimensions required for:

- Customer Journey Analytics
- Session Analysis
- Funnel Analysis
- Cross-Device Identity Resolution
- Marketing Analytics
- Recommendation Intelligence
- Experimentation

---

# 13. Cross-Device Identity Contract

Cross-device identity will be implemented using a controlled login-event signal.

**Concept:**

```text
Anonymous Mobile User
        ↓
Product View
        ↓
Add to Cart
        ↓
Login Event
        ↓
customer_id identified
        ↓
Desktop Session
        ↓
Purchase
```

The login event provides the linking signal between:

`anonymous_id`

and:

`customer_id`

The system will not claim to implement a production-grade identity graph.

The objective is to demonstrate a realistic analytical identity-stitching mechanism suitable for ORGEE.

---

# 14. Customer 360 Contract

Customer 360 is not a separate phase.

It emerges from integration of:

```text
Customers
    +
Orders
    +
Order Items
    +
Events
    +
Sessions
    +
Reviews
    +
Marketing
    +
Product Data
```

Result:

```text
                    CUSTOMER 360
                         |
       +-----------------+-----------------+
       |                 |                 |
   Behavior          Purchases         Preferences
       |                 |                 |
   Sessions          Orders           Products
       |                 |                 |
       +-----------------+-----------------+
                         |
                  Customer Analytics
```

Customer 360 will support:

- RFM
- CLV
- Retention
- Cohort analysis
- Customer segmentation
- Personalization
- Recommendation
- Executive decision support

---

# 15. Bronze / Silver / Gold Organization

Bronze/Silver/Gold is an implementation organization only.

It does not create additional project phases.

```text
BRONZE
Raw Public + Raw Generated Data
        ↓
SILVER
Cleaned + Standardized + Validated
        ↓
GOLD
Integrated Analytical Data
        ↓
Kimball Star Schema
```

The existing ORGEE architecture remains unchanged.

---

# 16. Data Contract Lock

The following decisions are locked for ORGEE Version 1.0.

| Area | Decision |
|---|---|
| Public foundation | Olist e-commerce dataset |
| Core datasets | Orders, Order Items, Products |
| Supporting datasets | Customers, Sellers, Payments, Reviews, Geolocation, Category Translation |
| Raw data | Preserved unchanged |
| Order grain | One row per order |
| Order Item grain | One row per item within an order |
| Product grain | One row per product |
| Seller grain | One row per seller |
| Customer identity | `customer_id` and `customer_unique_id` treated distinctly |
| Payment grain | Payment record |
| Review grain | Review record |
| Geolocation | Requires controlled transformation |
| Category translation | Category enrichment |
| Behavioral events | Python generated |
| Sessions | Python generated |
| Marketing data | Python generated |
| Inventory data | Python generated |
| Cross-device identity | Login-event-based stitching |
| Customer 360 | Emerges through integration |
| Bronze/Silver/Gold | Optional implementation organization |
| Raw files | Never modified |
| Data cleaning | Performed after profiling and contract |
| Synthetic generation | Performed after public-data contract |
| Project scope | Version 1 only |

---

# 17. Phase 2 Data Flow

The final Phase 2 data flow is:

```text
PUBLIC DATA
     ↓
DATA PROFILING
     ↓
PUBLIC DATA CONTRACT 🔒
     ↓
RAW DATA PRESERVATION
     ↓
DATA QUALITY VALIDATION
     ↓
PUBLIC DATA CLEANING
     ↓
ENTERPRISE DATA REQUIREMENTS
     ↓
PYTHON-GENERATED DATA
     ↓
CROSS-DEVICE IDENTITY
     ↓
CUSTOMER 360 INTEGRATION
     ↓
HYBRID DATASET
     ↓
PHASE 3 — ENTERPRISE SQL DATA WAREHOUSE
```

---

# 18. Phase 2 Success Criteria

Phase 2 will be considered complete only when:

- Public datasets are profiled
- Public data contract is documented
- Dataset grains are understood
- Key relationships are documented
- Raw files are preserved
- Data-quality issues are identified
- Public data cleaning rules are defined
- Enterprise-generated data requirements are defined
- Cross-device identity logic is defined
- Customer 360 integration logic is defined
- Hybrid data architecture is ready
- Data is ready for SQL warehouse design

---

# 19. Important Rule

No dataset should be modified simply because a transformation is convenient.

Every transformation must have a business or analytical reason.

The guiding principle is:

```text
BUSINESS REQUIREMENT
        ↓
DATA REQUIREMENT
        ↓
TRANSFORMATION
        ↓
ANALYTICAL VALUE
```

Not:

```text
TECHNOLOGY
    ↓
RANDOM TRANSFORMATION
    ↓
MORE COMPLEXITY
```

---

# 20. Final Status

**ORGEE Phase 2 Public Data Contract: LOCKED**

The public data foundation is now formally defined.

Next steps:

```text
1. Validate relationships
        ↓
2. Define cleaning rules
        ↓
3. Create processed public datasets
        ↓
4. Define enterprise-generated datasets
        ↓
5. Generate synthetic enterprise data
        ↓
6. Validate hybrid integration
        ↓
7. Prepare SQL warehouse inputs
```

No new project phases are introduced.

No architecture redesign is introduced.

No unnecessary technologies are introduced.

## ORGEE Principle

**Business insight over technology quantity.**

The purpose of the data foundation is to make the later Customer Journey, Customer Analytics, Product Analytics, Recommendation, Experimentation and Executive Decision Support phases reliable and reproducible.
