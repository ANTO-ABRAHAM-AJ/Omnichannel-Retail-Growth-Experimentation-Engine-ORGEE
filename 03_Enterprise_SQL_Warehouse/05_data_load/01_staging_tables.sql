/*
    ORGEE — Phase 3: Staging Tables (v2 — robust text-landing pattern)

    LESSON LEARNED from the load attempts: BULK INSERT's native type
    conversion is fragile on real-world CSV data — it fails on blank
    numeric/date fields (products, order dates), on longer-than-
    expected text (experiments.objective), and even on some
    well-formatted timestamps for reasons that weren't worth chasing
    row-by-row (inventory_observations).

    Fix: EVERY column except plain short IDs now lands as VARCHAR.
    All numeric/date conversion happens explicitly and safely with
    TRY_CONVERT(...) in 03_load_dimensions.sql and 04_load_facts.sql,
    where a failed conversion becomes NULL instead of aborting the
    entire load.
*/

IF SCHEMA_ID('staging') IS NULL
    EXEC('CREATE SCHEMA staging');
GO

-- ============================================================
-- PUBLIC DATA (Olist)
-- ============================================================

IF OBJECT_ID('staging.stg_customers', 'U') IS NOT NULL DROP TABLE staging.stg_customers;
CREATE TABLE staging.stg_customers (
    customer_id              VARCHAR(32),
    customer_unique_id       VARCHAR(32),
    customer_zip_code_prefix VARCHAR(10),
    customer_city            VARCHAR(50),
    customer_state           VARCHAR(5)
);
GO

IF OBJECT_ID('staging.stg_products', 'U') IS NOT NULL DROP TABLE staging.stg_products;
CREATE TABLE staging.stg_products (
    product_id                  VARCHAR(32),
    product_category_name       VARCHAR(60)  NULL,
    product_name_lenght         VARCHAR(20)  NULL,
    product_description_lenght  VARCHAR(20)  NULL,
    product_photos_qty          VARCHAR(20)  NULL,
    product_weight_g            VARCHAR(20)  NULL,
    product_length_cm           VARCHAR(20)  NULL,
    product_height_cm           VARCHAR(20)  NULL,
    product_width_cm            VARCHAR(20)  NULL
);
GO

IF OBJECT_ID('staging.stg_category_translation', 'U') IS NOT NULL DROP TABLE staging.stg_category_translation;
CREATE TABLE staging.stg_category_translation (
    product_category_name         VARCHAR(60),
    product_category_name_english VARCHAR(60)
);
GO

IF OBJECT_ID('staging.stg_sellers', 'U') IS NOT NULL DROP TABLE staging.stg_sellers;
CREATE TABLE staging.stg_sellers (
    seller_id              VARCHAR(32),
    seller_zip_code_prefix VARCHAR(10),
    seller_city            VARCHAR(50),
    seller_state            VARCHAR(5)
);
GO

IF OBJECT_ID('staging.stg_orders', 'U') IS NOT NULL DROP TABLE staging.stg_orders;
CREATE TABLE staging.stg_orders (
    order_id                       VARCHAR(32),
    customer_id                    VARCHAR(32),
    order_status                   VARCHAR(20),
    order_purchase_timestamp       VARCHAR(35),
    order_approved_at              VARCHAR(35) NULL,
    order_delivered_carrier_date   VARCHAR(35) NULL,
    order_delivered_customer_date  VARCHAR(35) NULL,
    order_estimated_delivery_date  VARCHAR(35) NULL
);
GO

IF OBJECT_ID('staging.stg_order_items', 'U') IS NOT NULL DROP TABLE staging.stg_order_items;
CREATE TABLE staging.stg_order_items (
    order_id            VARCHAR(32),
    order_item_id       VARCHAR(10),
    product_id          VARCHAR(32),
    seller_id           VARCHAR(32),
    shipping_limit_date VARCHAR(35),
    price                VARCHAR(20),
    freight_value          VARCHAR(20)
);
GO

IF OBJECT_ID('staging.stg_order_payments', 'U') IS NOT NULL DROP TABLE staging.stg_order_payments;
CREATE TABLE staging.stg_order_payments (
    order_id              VARCHAR(32),
    payment_sequential    VARCHAR(10),
    payment_type          VARCHAR(20),
    payment_installments  VARCHAR(10),
    payment_value          VARCHAR(20)
);
GO

IF OBJECT_ID('staging.stg_order_reviews', 'U') IS NOT NULL DROP TABLE staging.stg_order_reviews;
CREATE TABLE staging.stg_order_reviews (
    review_id                VARCHAR(32),
    order_id                 VARCHAR(32),
    review_score             VARCHAR(5),
    review_comment_title     VARCHAR(150) NULL,
    review_comment_message   VARCHAR(MAX) NULL,
    review_creation_date     VARCHAR(35),
    review_answer_timestamp  VARCHAR(35)
);
GO

-- ============================================================
-- ENTERPRISE DATA (Python-generated)
-- ============================================================

IF OBJECT_ID('staging.stg_sessions', 'U') IS NOT NULL DROP TABLE staging.stg_sessions;
CREATE TABLE staging.stg_sessions (
    session_id               VARCHAR(20),
    anonymous_id             VARCHAR(20),
    customer_id              VARCHAR(32) NULL,
    device_type              VARCHAR(20),
    platform                 VARCHAR(20),
    session_type             VARCHAR(10),
    session_start_timestamp  VARCHAR(35),
    session_end_timestamp    VARCHAR(35),
    expected_event_count     VARCHAR(10),
    activity_segment         VARCHAR(20)
);
GO

IF OBJECT_ID('staging.stg_events', 'U') IS NOT NULL DROP TABLE staging.stg_events;
CREATE TABLE staging.stg_events (
    event_id          VARCHAR(20),
    session_id        VARCHAR(20),
    anonymous_id      VARCHAR(20),
    customer_id       VARCHAR(32) NULL,
    product_id        VARCHAR(32) NULL,
    event_type        VARCHAR(20),
    device_type       VARCHAR(20),
    platform          VARCHAR(20),
    event_timestamp   VARCHAR(35)
);
GO

IF OBJECT_ID('staging.stg_identity_links', 'U') IS NOT NULL DROP TABLE staging.stg_identity_links;
CREATE TABLE staging.stg_identity_links (
    identity_link_id  VARCHAR(20),
    anonymous_id      VARCHAR(20),
    customer_id       VARCHAR(32),
    session_id        VARCHAR(20),
    link_timestamp    VARCHAR(35),
    link_method       VARCHAR(20)
);
GO

IF OBJECT_ID('staging.stg_campaigns', 'U') IS NOT NULL DROP TABLE staging.stg_campaigns;
CREATE TABLE staging.stg_campaigns (
    campaign_id    VARCHAR(20),
    campaign_name  VARCHAR(50),
    channel        VARCHAR(20),
    campaign_type  VARCHAR(30),
    objective      VARCHAR(60),
    start_date     VARCHAR(35),
    end_date       VARCHAR(35)
);
GO

IF OBJECT_ID('staging.stg_campaign_exposures', 'U') IS NOT NULL DROP TABLE staging.stg_campaign_exposures;
CREATE TABLE staging.stg_campaign_exposures (
    campaign_exposure_id  VARCHAR(20),
    campaign_id           VARCHAR(20),
    session_id            VARCHAR(20) NULL,
    anonymous_id          VARCHAR(20) NULL,
    customer_id           VARCHAR(32) NULL,
    channel               VARCHAR(20),
    exposure_timestamp    VARCHAR(35),
    exposure_outcome      VARCHAR(20)
);
GO

IF OBJECT_ID('staging.stg_experiments', 'U') IS NOT NULL DROP TABLE staging.stg_experiments;
CREATE TABLE staging.stg_experiments (
    experiment_id      VARCHAR(20),
    experiment_name    VARCHAR(50),
    objective          VARCHAR(60),
    start_timestamp    VARCHAR(35),
    end_timestamp      VARCHAR(35),
    primary_metric     VARCHAR(50),
    control_variant    VARCHAR(60),
    treatment_variant  VARCHAR(60)
);
GO

IF OBJECT_ID('staging.stg_experiment_assignments', 'U') IS NOT NULL DROP TABLE staging.stg_experiment_assignments;
CREATE TABLE staging.stg_experiment_assignments (
    experiment_assignment_id  VARCHAR(30),
    experiment_id             VARCHAR(20),
    customer_id               VARCHAR(32),
    variant                   VARCHAR(10),
    assignment_timestamp      VARCHAR(35)
);
GO

IF OBJECT_ID('staging.stg_inventory_observations', 'U') IS NOT NULL DROP TABLE staging.stg_inventory_observations;
CREATE TABLE staging.stg_inventory_observations (
    inventory_observation_id  VARCHAR(24),
    product_id                VARCHAR(32),
    inventory_location_id     VARCHAR(15),
    observation_timestamp     VARCHAR(35),
    available_quantity        VARCHAR(10),
    reserved_quantity         VARCHAR(10),
    inventory_status          VARCHAR(15)
);
GO

IF OBJECT_ID('staging.stg_recommendation_events', 'U') IS NOT NULL DROP TABLE staging.stg_recommendation_events;
CREATE TABLE staging.stg_recommendation_events (
    recommendation_event_id  VARCHAR(24),
    session_id               VARCHAR(20) NULL,
    anonymous_id              VARCHAR(20) NULL,
    customer_id                VARCHAR(32) NULL,
    experiment_id                VARCHAR(20) NULL,
    variant                        VARCHAR(10) NULL,
    product_id                      VARCHAR(32) NULL,
    event_type                       VARCHAR(30),
    event_timestamp                   VARCHAR(35)
);
GO
