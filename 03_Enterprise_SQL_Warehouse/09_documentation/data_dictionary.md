# ORGEE — Phase 3 Data Dictionary

Covers all 16 tables in the `dbo` schema: 7 dimensions + 9 facts.
`PK` = primary key, `FK` = foreign key, `UK` = unique key/natural key.
"Nullable" on a `customer_sk` column is not an oversight — it directly
reflects the Phase 2 identity-resolution fix: activity is anonymous
until a login event resolves it to a known customer (~18% of
sessions/events end up identified; the rest are legitimately anonymous).

---

## Dimensions

### Dim_Customer
Grain: one row per `customer_id`. Source: `olist_customers_dataset.csv`.

| Column | Type | Key | Notes |
|---|---|---|---|
| customer_sk | INT IDENTITY | PK | Surrogate key |
| customer_id | VARCHAR(32) | UK | Natural key from source |
| customer_unique_id | VARCHAR(32) | | Olist's cross-order customer identifier |
| customer_zip_code_prefix | VARCHAR(10) | | |
| customer_city | VARCHAR(50) | | |
| customer_state | CHAR(2) | | Brazilian state code |
| load_timestamp | DATETIME2 | | ETL audit column |

### Dim_Product
Grain: one row per `product_id`. Source: `olist_products_dataset.csv` + `product_category_name_translation.csv`.

| Column | Type | Key | Notes |
|---|---|---|---|
| product_sk | INT IDENTITY | PK | |
| product_id | VARCHAR(32) | UK | |
| product_category_name | VARCHAR(60) | | Portuguese original; NULL for 610 products (source data gap) |
| product_category_name_english | VARCHAR(60) | | Via translation join |
| product_name_length | INT | | NULL-safe converted (610 source blanks) |
| product_description_length | INT | | NULL-safe converted |
| product_photos_qty | INT | | NULL-safe converted |
| product_weight_g | DECIMAL(10,2) | | NULL-safe converted (2 source blanks) |
| product_length_cm / height_cm / width_cm | DECIMAL(10,2) | | NULL-safe converted |
| load_timestamp | DATETIME2 | | |

### Dim_Seller
Grain: one row per `seller_id`. Source: `olist_sellers_dataset.csv`.

| Column | Type | Key | Notes |
|---|---|---|---|
| seller_sk | INT IDENTITY | PK | |
| seller_id | VARCHAR(32) | UK | |
| seller_zip_code_prefix | VARCHAR(10) | | |
| seller_city | VARCHAR(50) | | |
| seller_state | CHAR(2) | | |

### Dim_Date
Grain: one row per calendar date, 2016-01-01 to 2018-12-31 (generated, buffer either side of actual data range). Not sourced from a CSV.

| Column | Type | Key | Notes |
|---|---|---|---|
| date_sk | INT | PK | Format YYYYMMDD, e.g. 20180807 |
| full_date | DATE | | |
| day_of_month | TINYINT | | |
| day_name | VARCHAR(10) | | |
| day_of_week | TINYINT | | 1=Sunday .. 7=Saturday |
| is_weekend | BIT | | |
| month_number / month_name | TINYINT / VARCHAR(10) | | |
| quarter_number | TINYINT | | |
| year_number | SMALLINT | | |

### Dim_Campaign
Grain: one row per `campaign_id`. Source: `campaigns.csv`.

| Column | Type | Key | Notes |
|---|---|---|---|
| campaign_sk | INT IDENTITY | PK | |
| campaign_id | VARCHAR(20) | UK | e.g. `camp_0001` |
| campaign_name | VARCHAR(50) | | |
| channel | VARCHAR(20) | | email, search, social, display, push |
| campaign_type | VARCHAR(30) | | |
| objective | VARCHAR(20) | | |
| start_date / end_date | DATE | | |

### Dim_Experiment
Grain: one row per `experiment_id`. Source: `experiments.csv`. Only 3 rows — matches the locked Phase 8 experimentation scope.

| Column | Type | Key | Notes |
|---|---|---|---|
| experiment_sk | INT IDENTITY | PK | |
| experiment_id | VARCHAR(20) | UK | e.g. `exp_001` |
| experiment_name | VARCHAR(50) | | |
| objective | VARCHAR(60) | | Full sentence descriptions, up to 47 chars |
| start_timestamp / end_timestamp | DATETIME2 | | |
| primary_metric | VARCHAR(50) | | Locked: purchase conversion rate |
| control_variant_label / treatment_variant_label | VARCHAR(60) | | |

### Dim_Device
Grain: one row per distinct (device_type, platform) combination. Derived, not sourced directly.

| Column | Type | Key | Notes |
|---|---|---|---|
| device_sk | INT IDENTITY | PK | |
| device_type | VARCHAR(20) | UK (composite) | mobile, desktop, tablet |
| platform | VARCHAR(20) | UK (composite) | web, mobile_app, desktop |

---

## Facts

### Fact_Order_Items
Grain: one row per order line item. Sources: `olist_order_items_dataset.csv` + `olist_order_payments_dataset.csv` (rolled up per order) + `olist_orders_dataset.csv` (status/date). **112,650 rows.**

| Column | Type | Key | Notes |
|---|---|---|---|
| order_item_sk | BIGINT IDENTITY | PK | |
| order_id | VARCHAR(32) | | Degenerate dimension |
| order_item_id | SMALLINT | | Line number within the order |
| order_status | VARCHAR(20) | | delivered, shipped, canceled, etc. |
| customer_sk | INT | FK → Dim_Customer | |
| product_sk | INT | FK → Dim_Product | |
| seller_sk | INT | FK → Dim_Seller | |
| order_purchase_date_sk | INT | FK → Dim_Date | |
| price / freight_value | DECIMAL(10,2) | | |
| payment_value_order_total | DECIMAL(10,2) | | SUM across all payments for the order |
| payment_installments_max | TINYINT | | MAX across all payments for the order |
| payment_type_primary | VARCHAR(20) | | The order's first payment method by sequence |

### Fact_Reviews
Grain: one row per **(review_id, order_id)** — not review_id alone; the public Olist dataset has 1,603 rows where the same review_id legitimately appears against a different order_id. **99,224 rows.**

| Column | Type | Key | Notes |
|---|---|---|---|
| review_sk | BIGINT IDENTITY | PK | |
| review_id, order_id | VARCHAR(32) | UK (composite) | |
| customer_sk | INT | FK → Dim_Customer | |
| review_creation_date_sk / review_answer_date_sk | INT | FK → Dim_Date | |
| review_score | TINYINT | | 1–5 |
| review_comment_title / review_comment_message | VARCHAR / VARCHAR(MAX) | | Both frequently NULL (87,658 / 58,274 blanks in source) |

### Fact_Sessions
Grain: one row per session. Source: `sessions.csv`. **500,000 rows.**

| Column | Type | Key | Notes |
|---|---|---|---|
| session_sk | BIGINT IDENTITY | PK | |
| session_id | VARCHAR(20) | UK | |
| anonymous_id | VARCHAR(20) | | Always populated — the device/browser-level identifier |
| customer_sk | INT | FK → Dim_Customer | **Nullable** — populated only for sessions with a real login (90,321 of 500,000 = 18.06%) |
| device_sk | INT | FK → Dim_Device | |
| session_start_date_sk | INT | FK → Dim_Date | |
| session_start_timestamp / session_end_timestamp | DATETIME2 | | |
| session_duration_seconds | INT (computed) | | `DATEDIFF(SECOND, start, end)` — always in sync, never manually inserted |
| session_type | VARCHAR(10) | | short, medium, long |
| expected_event_count | SMALLINT | | |

### Fact_Events
Grain: one row per behavioral event. Source: `events.csv`. **3,000,000 rows — largest table, clustered columnstore indexed.**

| Column | Type | Key | Notes |
|---|---|---|---|
| event_sk | BIGINT IDENTITY | PK (nonclustered) | Clustered slot reserved for the columnstore index |
| event_id | VARCHAR(20) | UK (nonclustered) | |
| session_id | VARCHAR(20) | FK → Fact_Sessions | Fact-to-fact reference |
| anonymous_id | VARCHAR(20) | | |
| customer_sk | INT | FK → Dim_Customer | **Nullable** — populated only after login within that session |
| product_sk | INT | FK → Dim_Product | Nullable — not every event is product-linked |
| device_sk | INT | FK → Dim_Device | |
| event_date_sk | INT | FK → Dim_Date | |
| event_timestamp | DATETIME2 | | |
| event_type | VARCHAR(20) | | session_start, search, product_view, add_to_cart, remove_from_cart, checkout_start, login, purchase_interaction. **No recommendation_impression/click** — those live only in Fact_Recommendation_Events (deliberate design fix). |

### Fact_Identity_Links
Grain: one row per anonymous→customer link (factless/bridge fact). Source: `identity_links.csv`. **90,321 rows** — matches `Fact_Sessions.customer_sk IS NOT NULL` count exactly.

| Column | Type | Key | Notes |
|---|---|---|---|
| identity_link_sk | BIGINT IDENTITY | PK | |
| identity_link_id | VARCHAR(20) | UK | |
| anonymous_id | VARCHAR(20) | UK | One link per anonymous_id |
| session_id | VARCHAR(20) | FK → Fact_Sessions | The session the login occurred in |
| customer_sk | INT | FK → Dim_Customer, **NOT NULL** | Always known — the row only exists because login succeeded |
| link_date_sk | INT | FK → Dim_Date | |
| link_timestamp | DATETIME2 | | |
| link_method | VARCHAR(20) | | Always `successful_login` |

### Fact_Campaign_Exposures
Grain: one row per exposure. Source: `campaign_exposures.csv`. **1,000,000 rows.**

| Column | Type | Key | Notes |
|---|---|---|---|
| campaign_exposure_sk | BIGINT IDENTITY | PK | |
| campaign_exposure_id | VARCHAR(20) | UK | |
| session_id / anonymous_id | VARCHAR(20) | | Nullable |
| campaign_sk | INT | FK → Dim_Campaign | |
| customer_sk | INT | FK → Dim_Customer | **Nullable** — most exposures land on anonymous traffic |
| exposure_date_sk | INT | FK → Dim_Date | |
| exposure_timestamp | DATETIME2 | | |
| channel | VARCHAR(20) | | |
| exposure_outcome | VARCHAR(20) | | impression, click, conversion |

### Fact_Inventory_Snapshot
Grain: one row per inventory observation (periodic snapshot fact). Source: `inventory_observations.csv`. **1,000,000 rows.** Note: this source file uses `DD-MM-YYYY HH:MM` timestamps and CRLF line endings — different from every other enterprise file, which uses ISO format and LF-only.

| Column | Type | Key | Notes |
|---|---|---|---|
| inventory_snapshot_sk | BIGINT IDENTITY | PK | |
| inventory_observation_id | VARCHAR(24) | UK | |
| inventory_location_id | VARCHAR(15) | | e.g. `inv_loc_01` |
| product_sk | INT | FK → Dim_Product | |
| observation_date_sk | INT | FK → Dim_Date | |
| observation_timestamp | DATETIME2 | | |
| available_quantity / reserved_quantity | INT | | |
| inventory_status | VARCHAR(15) | | in_stock, low_stock, out_of_stock |

### Fact_Experiment_Assignments
Grain: one row per (customer, experiment) — factless/bridge fact. Source: `experiment_assignments.csv`. **298,323 rows.** This is the table Phase 8's SRM check and statistical readout query.

| Column | Type | Key | Notes |
|---|---|---|---|
| experiment_assignment_sk | BIGINT IDENTITY | PK | |
| experiment_assignment_id | VARCHAR(30) | UK | |
| experiment_sk | INT | FK → Dim_Experiment, NOT NULL | |
| customer_sk | INT | FK → Dim_Customer, NOT NULL | |
| assignment_date_sk | INT | FK → Dim_Date | |
| assignment_timestamp | DATETIME2 | | |
| variant | VARCHAR(10) | | control, treatment |

### Fact_Recommendation_Events
Grain: one row per recommendation interaction. Source: `recommendation_events.csv`. **10,287 rows.** This is the table Phase 8's primary metric (conversion rate) and secondary metrics (CTR, AOV, revenue/user) get computed from, split by variant.

| Column | Type | Key | Notes |
|---|---|---|---|
| recommendation_event_sk | BIGINT IDENTITY | PK | |
| recommendation_event_id | VARCHAR(24) | UK | |
| session_id / anonymous_id | VARCHAR(20) | | Nullable |
| experiment_sk | INT | FK → Dim_Experiment | Nullable |
| customer_sk | INT | FK → Dim_Customer | Nullable |
| product_sk | INT | FK → Dim_Product | Nullable |
| event_date_sk | INT | FK → Dim_Date | |
| event_timestamp | DATETIME2 | | |
| variant | VARCHAR(10) | | control, treatment |
| event_type | VARCHAR(30) | | recommendation_impression, recommendation_click, recommendation_conversion |
