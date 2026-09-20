# ORGEE — Phase 3: Enterprise SQL Data Warehouse

## Star Schema Design Document

**Target engine:** SQL Server

**Methodology:** Kimball dimensional modeling

**Schema type:** Star schema (Type 1 SCD throughout — no historical tracking of dimension changes, consistent with a portfolio-scope analytics warehouse)

## 1. Design Decisions (Locked)

| **Decision**                | **Choice**                                                                   | **Rationale**                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Payments                    | Folded into `Fact_Order_Items` as measures                                   | Payment grain doesn't map cleanly 1:1 to order line items in the Olist dataset; avoids a fan-out fact with ambiguous grain |
| `sessions.activity_segment` | Excluded from the warehouse                                                  | Generation artifact from the Python synthetic-data pipeline, not a real business attribute                                 |
| Date dimension              | Generated (not sourced)                                                      | Standard Kimball practice — spans earliest to latest timestamp across all fact sources                                     |
| Device dimension            | Derived from `device_type` × `platform` combinations seen in sessions/events | Small, low-cardinality lookup — avoids repeating two string columns across two large fact tables                           |
| SCD strategy                | Type 1 (overwrite)                                                           | No requirement in the locked blueprint for historical dimension tracking                                                   |

## 2. Dimension Tables

| **Table**        | **Grain**                                      | **Source**                                                             | **Approx. Rows**         |
| ---------------- | ---------------------------------------------- | ---------------------------------------------------------------------- | ------------------------ |
| `Dim_Customer`   | one row per `customer_id`                      | `olist_customers_dataset.csv`                                          | \~99,441                 |
| `Dim_Product`    | one row per `product_id`                       | `olist_products_dataset.csv` + `product_category_name_translation.csv` | \~32,951                 |
| `Dim_Seller`     | one row per `seller_id`                        | `olist_sellers_dataset.csv`                                            | \~3,095                  |
| `Dim_Date`       | one row per calendar date                      | Generated                                                              | \~1,200 (2016–2018 span) |
| `Dim_Campaign`   | one row per `campaign_id`                      | `campaigns.csv`                                                        | 50                       |
| `Dim_Experiment` | one row per `experiment_id`                    | `experiments.csv`                                                      | 3                        |
| `Dim_Device`     | one row per distinct `(device_type, platform)` | Derived from sessions/events                                           | \~6–10                   |

## 3. Fact Tables

| **Table**                     | **Grain**                              | **Source**                                                                                                    | **Approx. Rows** | **Type**                                      |
| ----------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------- | --------------------------------------------- |
| `Fact_Order_Items`            | one row per order line item            | `olist_order_items_dataset.csv` + `olist_order_payments_dataset.csv` (rolled up) + `olist_orders_dataset.csv` | \~112,650        | Transaction                                   |
| `Fact_Reviews`                | one row per review                     | `olist_order_reviews_dataset.csv`                                                                             | \~99,224         | Transaction                                   |
| `Fact_Sessions`               | one row per session                    | `sessions.csv`                                                                                                | 500,000          | Transaction                                   |
| `Fact_Events`                 | one row per behavioral event           | `events.csv`                                                                                                  | 3,000,000        | Transaction (largest — columnstore candidate) |
| `Fact_Identity_Links`         | one row per anonymous→customer link    | `identity_links.csv`                                                                                          | \~90,000         | Factless / bridge                             |
| `Fact_Campaign_Exposures`     | one row per exposure                   | `campaign_exposures.csv`                                                                                      | 1,000,000        | Transaction                                   |
| `Fact_Inventory_Snapshot`     | one row per inventory observation      | `inventory_observations.csv`                                                                                  | 1,000,000        | Periodic snapshot                             |
| `Fact_Experiment_Assignments` | one row per (customer, experiment)     | `experiment_assignments.csv`                                                                                  | \~298,000        | Factless / bridge                             |
| `Fact_Recommendation_Events`  | one row per recommendation interaction | `recommendation_events.csv`                                                                                   | \~10,000         | Transaction                                   |

## 4. Star Schema Map

Plaintext

```text
                         Dim_Date
                            |
        Dim_Customer -- Fact_Order_Items -- Dim_Product
                            |                    |
                       Dim_Seller           Dim_Product

        Dim_Customer -- Fact_Reviews -- Dim_Date

        Dim_Customer(opt) -- Fact_Sessions -- Dim_Date
              |                    |
         Dim_Device           Dim_Date

        Fact_Events -- Dim_Product(opt)
              |    \
         Dim_Date  Dim_Device
              (links to Fact_Sessions via session_id)

        Fact_Identity_Links (bridges anonymous_id <-> customer_id)
              |         |
        Dim_Customer  Fact_Sessions

        Dim_Campaign -- Fact_Campaign_Exposures -- Dim_Customer(opt)
                              |
                           Dim_Date

        Dim_Product -- Fact_Inventory_Snapshot -- Dim_Date

        Dim_Experiment -- Fact_Experiment_Assignments -- Dim_Customer
                                    |
                                 Dim_Date

        Dim_Experiment -- Fact_Recommendation_Events -- Dim_Customer(opt)
                                    |                          |
                               Dim_Product                 Dim_Date

```

`(opt)` = foreign key is nullable, since the row may represent anonymous/pre-identification activity (this directly reflects the identity-resolution fix from Phase 2 — most sessions/events/exposures are anonymous, only \~18% carry a `customer_id`).

## 5. Source-to-Target Mapping

| **Warehouse Table**           | **Source File(s)**                                                                                | **Key Transformation Notes**                                                                                                                   |
| ----------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `Dim_Customer`                | `olist_customers_dataset.csv`                                                                     | Direct load, surrogate key added                                                                                                               |
| `Dim_Product`                 | `olist_products_dataset.csv`, `product_category_name_translation.csv`                             | Join on `product_category_name` to get English category name                                                                                   |
| `Dim_Seller`                  | `olist_sellers_dataset.csv`                                                                       | Direct load, surrogate key added                                                                                                               |
| `Dim_Date`                    | Generated                                                                                         | `CROSS JOIN` a number sequence against a base date, or `T-SQL` recursive CTE                                                                   |
| `Dim_Campaign`                | `campaigns.csv`                                                                                   | Direct load                                                                                                                                    |
| `Dim_Experiment`              | `experiments.csv`                                                                                 | Direct load                                                                                                                                    |
| `Dim_Device`                  | `DISTINCT device_type, platform` from `sessions.csv`                                              | Deduplicated lookup                                                                                                                            |
| `Fact_Order_Items`            | `olist_order_items_dataset.csv` + `olist_order_payments_dataset.csv` + `olist_orders_dataset.csv` | Payments aggregated (`SUM payment_value`, `MAX installments`) per `order_id`, joined to items and orders to bring in `order_status` and dates. |
| `Fact_Reviews`                | `olist_order_reviews_dataset.csv`                                                                 | Direct load, FK to `Dim_Customer` via `olist_orders_dataset.csv` join                                                                          |
| `Fact_Sessions`               | `sessions.csv`                                                                                    | `customer_id` nullable FK (per Phase 2 identity-resolution fix)                                                                                |
| `Fact_Events`                 | `events.csv`                                                                                      | `customer_id`, `product_id` nullable FKs                                                                                                       |
| `Fact_Identity_Links`         | `identity_links.csv`                                                                              | Direct load                                                                                                                                    |
| `Fact_Campaign_Exposures`     | `campaign_exposures.csv`                                                                          | `customer_id` nullable FK                                                                                                                      |
| `Fact_Inventory_Snapshot`     | `inventory_observations.csv`                                                                      | Direct load                                                                                                                                    |
| `Fact_Experiment_Assignments` | `experiment_assignments.csv`                                                                      | Direct load                                                                                                                                    |
| `Fact_Recommendation_Events`  | `recommendation_events.csv`                                                                       | `customer_id` nullable FK                                                                                                                      |

## 6. Next Steps

1. `02_dimension_ddl` — `CREATE TABLE` scripts for all 7 dimensions
2. `03_fact_ddl` — `CREATE TABLE` scripts for all 9 fact tables
3. `04_keys_constraints` — PK/FK constraints (added after both DDL sets exist)
4. `05_data_load` — `BULK INSERT` scripts from CSV → staging → warehouse
5. `06_indexes` — clustered columnstore index on `Fact_Events`, standard indexes on FK columns elsewhere