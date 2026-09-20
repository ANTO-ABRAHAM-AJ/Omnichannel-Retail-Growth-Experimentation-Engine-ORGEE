/*
    ORGEE — Phase 3: Load Facts from Staging (v2)
    Run AFTER 03_load_dimensions.sql.
    Every staging column is now text; each block below converts it
    safely with TRY_CONVERT in a leading CTE, then joins to dimensions.

    ORDER MATTERS: Fact_Sessions must load BEFORE Fact_Events and
    Fact_Identity_Links (both carry an FK to Fact_Sessions.session_id).
*/

-- ============================================================
-- Fact_Order_Items  (payments rolled up per order_id)
-- ============================================================

;WITH PaymentAgg AS (
    SELECT
        order_id,
        SUM(TRY_CONVERT(DECIMAL(10,2), payment_value))     AS payment_value_order_total,
        MAX(TRY_CONVERT(TINYINT, payment_installments))    AS payment_installments_max
    FROM staging.stg_order_payments
    GROUP BY order_id
),
PaymentPrimary AS (
    SELECT
        order_id, payment_type,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY TRY_CONVERT(SMALLINT, payment_sequential)
        ) AS rn
    FROM staging.stg_order_payments
),
OrdersConv AS (
    SELECT
        order_id, customer_id, order_status,
        TRY_CONVERT(DATETIME2(7), order_purchase_timestamp, 120) AS order_purchase_timestamp
    FROM staging.stg_orders
),
ItemsConv AS (
    SELECT
        order_id,
        TRY_CONVERT(SMALLINT, order_item_id)   AS order_item_id,
        product_id, seller_id,
        TRY_CONVERT(DECIMAL(10,2), price)          AS price,
        TRY_CONVERT(DECIMAL(10,2), freight_value)      AS freight_value
    FROM staging.stg_order_items
)
INSERT INTO dbo.Fact_Order_Items (
    order_id, order_item_id, order_status, customer_sk, product_sk, seller_sk,
    order_purchase_date_sk, price, freight_value, payment_value_order_total,
    payment_installments_max, payment_type_primary
)
SELECT
    oi.order_id, oi.order_item_id, o.order_status,
    dc.customer_sk, dp.product_sk, ds.seller_sk,
    CAST(CONVERT(VARCHAR(8), o.order_purchase_timestamp, 112) AS INT),
    oi.price, oi.freight_value,
    pa.payment_value_order_total, pa.payment_installments_max, pp.payment_type
FROM ItemsConv oi
JOIN OrdersConv o              ON oi.order_id = o.order_id
LEFT JOIN dbo.Dim_Customer dc  ON o.customer_id = dc.customer_id
LEFT JOIN dbo.Dim_Product dp   ON oi.product_id = dp.product_id
LEFT JOIN dbo.Dim_Seller ds    ON oi.seller_id = ds.seller_id
LEFT JOIN PaymentAgg pa        ON oi.order_id = pa.order_id
LEFT JOIN PaymentPrimary pp    ON oi.order_id = pp.order_id AND pp.rn = 1;

-- ============================================================
-- Fact_Reviews
-- ============================================================

;WITH ReviewsConv AS (
    SELECT
        review_id, order_id,
        TRY_CONVERT(TINYINT, review_score)                       AS review_score,
        review_comment_title, review_comment_message,
        TRY_CONVERT(DATETIME2(7), review_creation_date, 120)            AS review_creation_date,
        TRY_CONVERT(DATETIME2(7), review_answer_timestamp, 120)           AS review_answer_timestamp
    FROM staging.stg_order_reviews
)
INSERT INTO dbo.Fact_Reviews (
    review_id, order_id, customer_sk, review_creation_date_sk,
    review_answer_date_sk, review_score, review_comment_title, review_comment_message
)
SELECT
    r.review_id, r.order_id, dc.customer_sk,
    CAST(CONVERT(VARCHAR(8), r.review_creation_date, 112) AS INT),
    CAST(CONVERT(VARCHAR(8), r.review_answer_timestamp, 112) AS INT),
    r.review_score, r.review_comment_title, r.review_comment_message
FROM ReviewsConv r
JOIN staging.stg_orders o      ON r.order_id = o.order_id
LEFT JOIN dbo.Dim_Customer dc  ON o.customer_id = dc.customer_id;

-- ============================================================
-- Fact_Sessions  (must load before Fact_Events / Fact_Identity_Links)
-- ============================================================

;WITH SessionsConv AS (
    SELECT
        session_id, anonymous_id, customer_id, device_type, platform, session_type,
        TRY_CONVERT(DATETIME2(7), session_start_timestamp, 120)   AS session_start_timestamp,
        TRY_CONVERT(DATETIME2(7), session_end_timestamp, 120)       AS session_end_timestamp,
        TRY_CONVERT(SMALLINT, expected_event_count)              AS expected_event_count
    FROM staging.stg_sessions
)
INSERT INTO dbo.Fact_Sessions (
    session_id, anonymous_id, customer_sk, device_sk, session_start_date_sk,
    session_start_timestamp, session_end_timestamp, session_type, expected_event_count
)
SELECT
    s.session_id, s.anonymous_id, dc.customer_sk, dd.device_sk,
    CAST(CONVERT(VARCHAR(8), s.session_start_timestamp, 112) AS INT),
    s.session_start_timestamp, s.session_end_timestamp, s.session_type, s.expected_event_count
FROM SessionsConv s
LEFT JOIN dbo.Dim_Customer dc  ON s.customer_id = dc.customer_id
LEFT JOIN dbo.Dim_Device dd    ON s.device_type = dd.device_type AND s.platform = dd.platform;

-- ============================================================
-- Fact_Events
-- ============================================================

;WITH EventsConv AS (
    SELECT
        event_id, session_id, anonymous_id, customer_id, product_id,
        event_type, device_type, platform,
        TRY_CONVERT(DATETIME2(7), event_timestamp, 120) AS event_timestamp
    FROM staging.stg_events
)
INSERT INTO dbo.Fact_Events (
    event_id, session_id, anonymous_id, customer_sk, product_sk, device_sk,
    event_date_sk, event_timestamp, event_type
)
SELECT
    e.event_id, e.session_id, e.anonymous_id, dc.customer_sk, dp.product_sk, dd.device_sk,
    CAST(CONVERT(VARCHAR(8), e.event_timestamp, 112) AS INT),
    e.event_timestamp, e.event_type
FROM EventsConv e
LEFT JOIN dbo.Dim_Customer dc  ON e.customer_id = dc.customer_id
LEFT JOIN dbo.Dim_Product dp   ON e.product_id = dp.product_id
LEFT JOIN dbo.Dim_Device dd    ON e.device_type = dd.device_type AND e.platform = dd.platform;

-- ============================================================
-- Fact_Identity_Links
-- ============================================================

;WITH IdentityConv AS (
    SELECT
        identity_link_id, anonymous_id, customer_id, session_id,
        TRY_CONVERT(DATETIME2(7), link_timestamp, 120) AS link_timestamp,
        link_method
    FROM staging.stg_identity_links
)
INSERT INTO dbo.Fact_Identity_Links (
    identity_link_id, anonymous_id, session_id, customer_sk,
    link_date_sk, link_timestamp, link_method
)
SELECT
    il.identity_link_id, il.anonymous_id, il.session_id, dc.customer_sk,
    CAST(CONVERT(VARCHAR(8), il.link_timestamp, 112) AS INT),
    il.link_timestamp, il.link_method
FROM IdentityConv il
JOIN dbo.Dim_Customer dc ON il.customer_id = dc.customer_id;

-- ============================================================
-- Fact_Campaign_Exposures
-- ============================================================

;WITH ExposuresConv AS (
    SELECT
        campaign_exposure_id, campaign_id, session_id, anonymous_id, customer_id, channel,
        TRY_CONVERT(DATETIME2(7), exposure_timestamp, 120) AS exposure_timestamp,
        exposure_outcome
    FROM staging.stg_campaign_exposures
)
INSERT INTO dbo.Fact_Campaign_Exposures (
    campaign_exposure_id, session_id, anonymous_id, campaign_sk, customer_sk,
    exposure_date_sk, exposure_timestamp, channel, exposure_outcome
)
SELECT
    ce.campaign_exposure_id, ce.session_id, ce.anonymous_id,
    dcamp.campaign_sk, dc.customer_sk,
    CAST(CONVERT(VARCHAR(8), ce.exposure_timestamp, 112) AS INT),
    ce.exposure_timestamp, ce.channel, ce.exposure_outcome
FROM ExposuresConv ce
LEFT JOIN dbo.Dim_Campaign dcamp ON ce.campaign_id = dcamp.campaign_id
LEFT JOIN dbo.Dim_Customer dc    ON ce.customer_id = dc.customer_id;

-- ============================================================
-- Fact_Inventory_Snapshot
-- ============================================================

;WITH InventoryConv AS (
    -- fix: this file's timestamps are DD-MM-YYYY HH:MM (not the ISO
    -- format used by every other enterprise file) — rearranged to
    -- ISO before TRY_CONVERT. inventory_status/inventory_location_id
    -- defensively stripped of a stray trailing \r.
    SELECT
        inventory_observation_id, product_id,
        RTRIM(REPLACE(inventory_location_id, CHAR(13), '')) AS inventory_location_id,
        TRY_CONVERT(
            DATETIME2(7),
            SUBSTRING(observation_timestamp, 7, 4) + '-' +
            SUBSTRING(observation_timestamp, 4, 2) + '-' +
            SUBSTRING(observation_timestamp, 1, 2) + ' ' +
            SUBSTRING(observation_timestamp, 12, 5) + ':00',
            120
        ) AS observation_timestamp,
        TRY_CONVERT(INT, available_quantity)                 AS available_quantity,
        TRY_CONVERT(INT, reserved_quantity)                     AS reserved_quantity,
        RTRIM(REPLACE(inventory_status, CHAR(13), ''))            AS inventory_status
    FROM staging.stg_inventory_observations
)
INSERT INTO dbo.Fact_Inventory_Snapshot (
    inventory_observation_id, inventory_location_id, product_sk,
    observation_date_sk, observation_timestamp, available_quantity,
    reserved_quantity, inventory_status
)
SELECT
    io.inventory_observation_id, io.inventory_location_id, dp.product_sk,
    CAST(CONVERT(VARCHAR(8), io.observation_timestamp, 112) AS INT),
    io.observation_timestamp, io.available_quantity, io.reserved_quantity, io.inventory_status
FROM InventoryConv io
LEFT JOIN dbo.Dim_Product dp ON io.product_id = dp.product_id;

-- ============================================================
-- Fact_Experiment_Assignments
-- ============================================================

;WITH AssignConv AS (
    SELECT
        experiment_assignment_id, experiment_id, customer_id, variant,
        TRY_CONVERT(DATETIME2(7), assignment_timestamp, 120) AS assignment_timestamp
    FROM staging.stg_experiment_assignments
)
INSERT INTO dbo.Fact_Experiment_Assignments (
    experiment_assignment_id, experiment_sk, customer_sk,
    assignment_date_sk, assignment_timestamp, variant
)
SELECT
    ea.experiment_assignment_id, dexp.experiment_sk, dc.customer_sk,
    CAST(CONVERT(VARCHAR(8), ea.assignment_timestamp, 112) AS INT),
    ea.assignment_timestamp, ea.variant
FROM AssignConv ea
JOIN dbo.Dim_Experiment dexp ON ea.experiment_id = dexp.experiment_id
JOIN dbo.Dim_Customer dc     ON ea.customer_id = dc.customer_id;

-- ============================================================
-- Fact_Recommendation_Events
-- ============================================================

;WITH RecConv AS (
    SELECT
        recommendation_event_id, session_id, anonymous_id, customer_id,
        experiment_id, variant, product_id, event_type,
        TRY_CONVERT(DATETIME2(7), event_timestamp, 120) AS event_timestamp
    FROM staging.stg_recommendation_events
)
INSERT INTO dbo.Fact_Recommendation_Events (
    recommendation_event_id, session_id, anonymous_id, experiment_sk,
    customer_sk, product_sk, event_date_sk, event_timestamp, variant, event_type
)
SELECT
    re.recommendation_event_id, re.session_id, re.anonymous_id,
    dexp.experiment_sk, dc.customer_sk, dp.product_sk,
    CAST(CONVERT(VARCHAR(8), re.event_timestamp, 112) AS INT),
    re.event_timestamp, re.variant, re.event_type
FROM RecConv re
LEFT JOIN dbo.Dim_Experiment dexp ON re.experiment_id = dexp.experiment_id
LEFT JOIN dbo.Dim_Customer dc     ON re.customer_id = dc.customer_id
LEFT JOIN dbo.Dim_Product dp      ON re.product_id = dp.product_id;

-- ============================================================
-- Row count check — compare against staging counts to confirm
-- no rows were silently dropped by a join
-- ============================================================

SELECT 'Fact_Order_Items' AS fact_table, COUNT(*) AS row_count FROM dbo.Fact_Order_Items
UNION ALL SELECT 'Fact_Reviews', COUNT(*) FROM dbo.Fact_Reviews
UNION ALL SELECT 'Fact_Sessions', COUNT(*) FROM dbo.Fact_Sessions
UNION ALL SELECT 'Fact_Events', COUNT(*) FROM dbo.Fact_Events
UNION ALL SELECT 'Fact_Identity_Links', COUNT(*) FROM dbo.Fact_Identity_Links
UNION ALL SELECT 'Fact_Campaign_Exposures', COUNT(*) FROM dbo.Fact_Campaign_Exposures
UNION ALL SELECT 'Fact_Inventory_Snapshot', COUNT(*) FROM dbo.Fact_Inventory_Snapshot
UNION ALL SELECT 'Fact_Experiment_Assignments', COUNT(*) FROM dbo.Fact_Experiment_Assignments
UNION ALL SELECT 'Fact_Recommendation_Events', COUNT(*) FROM dbo.Fact_Recommendation_Events;

-- ============================================================
-- Conversion-failure spot check — should return 0 rows.
-- If not, some staging timestamp text didn't survive TRY_CONVERT.
-- ============================================================

SELECT 'Fact_Events NULL event_timestamp despite staging value' AS check_name, COUNT(*) AS bad_rows
FROM dbo.Fact_Events fe
JOIN staging.stg_events se ON fe.event_id = se.event_id
WHERE fe.event_timestamp IS NULL AND se.event_timestamp IS NOT NULL AND se.event_timestamp <> '';
