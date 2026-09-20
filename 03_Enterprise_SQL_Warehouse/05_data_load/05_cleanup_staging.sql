/*
    ORGEE — Phase 3: Cleanup Staging (OPTIONAL)

    Only run this after you've confirmed (via the row-count checks
    at the end of 03 and 04, and ideally phase2_quality_gate-style
    checks against the warehouse) that the load succeeded.

    Staging tables are not part of the star schema deliverable —
    dropping them keeps the database clean for your ER diagram /
    documentation phase (09_documentation). If you'd rather keep
    them around for troubleshooting a bit longer, skip this file
    for now — nothing downstream depends on staging being gone.
*/

DROP TABLE IF EXISTS staging.stg_customers;
DROP TABLE IF EXISTS staging.stg_products;
DROP TABLE IF EXISTS staging.stg_category_translation;
DROP TABLE IF EXISTS staging.stg_sellers;
DROP TABLE IF EXISTS staging.stg_orders;
DROP TABLE IF EXISTS staging.stg_order_items;
DROP TABLE IF EXISTS staging.stg_order_payments;
DROP TABLE IF EXISTS staging.stg_order_reviews;
DROP TABLE IF EXISTS staging.stg_sessions;
DROP TABLE IF EXISTS staging.stg_events;
DROP TABLE IF EXISTS staging.stg_identity_links;
DROP TABLE IF EXISTS staging.stg_campaigns;
DROP TABLE IF EXISTS staging.stg_campaign_exposures;
DROP TABLE IF EXISTS staging.stg_experiments;
DROP TABLE IF EXISTS staging.stg_experiment_assignments;
DROP TABLE IF EXISTS staging.stg_inventory_observations;
DROP TABLE IF EXISTS staging.stg_recommendation_events;

DROP SCHEMA IF EXISTS staging;

PRINT 'Staging schema removed.';
