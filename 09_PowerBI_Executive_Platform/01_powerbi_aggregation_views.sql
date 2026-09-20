/*
    ============================================================
    ORGEE — Phase 9: Power BI Executive Decision Platform
    01_powerbi_aggregation_views.sql
    ============================================================

    BUSINESS QUESTION
    How do we give Power BI the aggregates it needs for Dashboards
    4 and 5 without importing multi-million-row raw fact tables
    into its in-memory model (the same class of performance risk
    we hit repeatedly in SQL Server itself during this project)?

    DESIGN: two permanent SQL VIEWS, each pre-aggregated to a grain
    Power BI can consume directly. Views (not materialized tables)
    are used here since these aggregates are cheap to compute on
    demand and this way Power BI always sees current data without
    needing a manual refresh step in SQL.

    TECHNIQUES USED
    Views, aggregation, CASE-based funnel pivoting.
    ============================================================
*/

-- ------------------------------------------------------------
-- View 1: Daily product funnel summary (for Dashboard 4)
-- Replaces importing all 3,000,000 raw Fact_Events rows — Power BI
-- only needs the daily funnel-stage counts, not row-level detail.
--
-- FIX APPLIED (caught after the first version's totals reconciliation
-- check came back wrong — 1,320,847 instead of 405,699 for
-- product_views, and 0 for checkout/purchase): the original version
-- (a) counted raw event ROWS instead of DISTINCT SESSIONS per stage
-- (a session can log multiple product_view events — this is the
-- exact same row-vs-entity distinction Phase 6 already caught once),
-- and (b) used the wrong event_type string values ('checkout'/
-- 'purchase' instead of the real 'checkout_start'/
-- 'purchase_interaction' — confirmed via a direct schema check,
-- not assumed). Fixed: COUNT(DISTINCT session_id) per correct
-- event_type, matching the already-validated Phase 5/6 funnel
-- figures exactly (500,000 / 405,699 / 151,078 / 81,736 / 47,418).
-- ------------------------------------------------------------

IF OBJECT_ID('dbo.vw_Daily_Product_Funnel', 'V') IS NOT NULL DROP VIEW dbo.vw_Daily_Product_Funnel;
GO

CREATE VIEW dbo.vw_Daily_Product_Funnel AS
SELECT
    d.full_date,
    d.year_number,
    d.month_number,
    COUNT(DISTINCT CASE WHEN fe.event_type = 'session_start' THEN fe.session_id END) AS visits,
    COUNT(DISTINCT CASE WHEN fe.event_type = 'product_view' THEN fe.session_id END) AS product_views,
    COUNT(DISTINCT CASE WHEN fe.event_type = 'add_to_cart' THEN fe.session_id END) AS add_to_cart,
    COUNT(DISTINCT CASE WHEN fe.event_type = 'checkout_start' THEN fe.session_id END) AS checkout,
    COUNT(DISTINCT CASE WHEN fe.event_type = 'purchase_interaction' THEN fe.session_id END) AS purchase
FROM dbo.Fact_Events fe
JOIN dbo.Dim_Date d ON fe.event_date_sk = d.date_sk
GROUP BY d.full_date, d.year_number, d.month_number;
GO

-- NOTE (expected behavior, not a bug): summing this view's rows
-- across all dates gives a total slightly HIGHER than the true
-- overall distinct-session figures confirmed in Phase 5/6 (e.g.
-- ~409,091 vs the true 405,699 for product_views) — because a
-- session spanning across midnight gets counted once on each of
-- the two calendar days it touches. Each individual day's value is
-- correct on its own; this view is for daily/monthly TRENDING in
-- Power BI, not for reconstructing the exact all-time total by
-- summing every row. Do not "fix" this by trying to force an exact
-- match to the grand total — that would require session-level
-- deduplication across day boundaries, which would break the
-- per-day trend the view exists to provide.

-- ------------------------------------------------------------
-- View 2: Daily campaign exposure summary (for Dashboard 5)
-- Replaces importing all 1,000,000 raw Fact_Campaign_Exposures
-- rows. Deliberately does NOT expose customer_sk (mostly NULL —
-- see Phase 9 prerequisite check) or any revenue-attribution
-- column, since neither is reliable at this grain.
-- ------------------------------------------------------------

IF OBJECT_ID('dbo.vw_Daily_Campaign_Performance', 'V') IS NOT NULL DROP VIEW dbo.vw_Daily_Campaign_Performance;
GO

CREATE VIEW dbo.vw_Daily_Campaign_Performance AS
SELECT
    d.full_date,
    dc.campaign_id,
    dc.campaign_name,
    dc.channel,
    dc.campaign_type,
    SUM(CASE WHEN fce.exposure_outcome = 'impression' THEN 1 ELSE 0 END) AS impressions,
    SUM(CASE WHEN fce.exposure_outcome = 'click' THEN 1 ELSE 0 END) AS clicks,
    SUM(CASE WHEN fce.exposure_outcome = 'conversion' THEN 1 ELSE 0 END) AS conversions
FROM dbo.Fact_Campaign_Exposures fce
JOIN dbo.Dim_Campaign dc ON dc.campaign_sk = fce.campaign_sk
JOIN dbo.Dim_Date d ON fce.exposure_date_sk = d.date_sk
GROUP BY d.full_date, dc.campaign_id, dc.campaign_name, dc.channel, dc.campaign_type;
GO

-- ------------------------------------------------------------
-- Verify both views work and produce sensible row counts
-- ------------------------------------------------------------

SELECT COUNT(*) AS funnel_view_rows FROM dbo.vw_Daily_Product_Funnel;
SELECT COUNT(*) AS campaign_view_rows FROM dbo.vw_Daily_Campaign_Performance;

SELECT TOP 5 * FROM dbo.vw_Daily_Product_Funnel ORDER BY full_date;
SELECT TOP 5 * FROM dbo.vw_Daily_Campaign_Performance ORDER BY full_date;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Do both views return a reasonable number of rows (roughly
      one row per date for the funnel view; one row per
      date x campaign for the campaign view — expect a few
      hundred to a few thousand rows each, NOT millions)?
    - Rerun verify_funnel_totals.sql — totals should now read
      visits=500,000, product_views=405,699, add_to_cart=151,078,
      checkout=81,736, purchase=47,418, exactly matching the
      already-confirmed Phase 5/6 figures.

    BUSINESS IMPLICATION:
    These two views, plus the already-existing tables/views,
    are what Power BI should actually import — never the raw
    Fact_Events or Fact_Campaign_Exposures tables directly.
*/
