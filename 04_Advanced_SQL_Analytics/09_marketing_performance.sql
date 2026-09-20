/*
    ============================================================
    ORGEE — Phase 4: Advanced SQL Analytics
    09_marketing_performance.sql
    ============================================================

    BUSINESS QUESTION
    Which campaigns and channels perform best in terms of
    click-through and conversion? Is spend/exposure allocated toward
    the channels that actually convert?

    NOTE ON SCOPE
    This analysis uses Fact_Campaign_Exposures only — it deliberately
    does NOT touch Fact_Events, session-level behavior, or anything
    resembling funnel/journey analysis, which belongs to Phase 5.
    This stays at the campaign/channel aggregate level, consistent
    with "what happened" rather than "how did the journey unfold."

    NOTE ON DATA SUFFICIENCY
    campaign_exposures has real, non-trivial signal: ~90% impression,
    ~9.2% click, ~0.8% conversion (verified against source data before
    writing this script) — enough spread to support a genuine
    channel/campaign comparison.

    TECHNIQUES USED
    CTE, CASE (funnel-stage pivoting), aggregation, ranking,
    window functions.
    ============================================================
*/

-- ------------------------------------------------------------
-- Channel-level performance: impressions, clicks, conversions,
-- CTR, conversion rate
-- ------------------------------------------------------------

WITH ChannelStats AS (
    SELECT
        channel,
        SUM(CASE WHEN exposure_outcome = 'impression' THEN 1 ELSE 0 END) AS impressions,
        SUM(CASE WHEN exposure_outcome = 'click' THEN 1 ELSE 0 END)      AS clicks,
        SUM(CASE WHEN exposure_outcome = 'conversion' THEN 1 ELSE 0 END) AS conversions,
        COUNT(*) AS total_exposures
    FROM dbo.Fact_Campaign_Exposures
    GROUP BY channel
)
SELECT
    channel, impressions, clicks, conversions, total_exposures,
    ROUND(100.0 * clicks / NULLIF(total_exposures, 0), 2) AS ctr_pct,
    ROUND(100.0 * conversions / NULLIF(total_exposures, 0), 2) AS conversion_rate_pct,
    RANK() OVER (ORDER BY 100.0 * conversions / NULLIF(total_exposures, 0) DESC) AS conversion_rank
FROM ChannelStats
ORDER BY conversion_rank;

-- ------------------------------------------------------------
-- Campaign-level performance, ranked by conversion rate
-- (campaigns with at least 1,000 exposures, to avoid noisy
-- rankings from campaigns barely run)
-- ------------------------------------------------------------

WITH CampaignStats AS (
    SELECT
        dcamp.campaign_id,
        dcamp.campaign_name,
        dcamp.channel,
        dcamp.campaign_type,
        SUM(CASE WHEN fce.exposure_outcome = 'click' THEN 1 ELSE 0 END)      AS clicks,
        SUM(CASE WHEN fce.exposure_outcome = 'conversion' THEN 1 ELSE 0 END) AS conversions,
        COUNT(*) AS total_exposures
    FROM dbo.Fact_Campaign_Exposures fce
    JOIN dbo.Dim_Campaign dcamp ON fce.campaign_sk = dcamp.campaign_sk
    GROUP BY dcamp.campaign_id, dcamp.campaign_name, dcamp.channel, dcamp.campaign_type
    HAVING COUNT(*) >= 1000
)
SELECT TOP 10
    campaign_id, campaign_name, channel, campaign_type,
    clicks, conversions, total_exposures,
    ROUND(100.0 * conversions / total_exposures, 2) AS conversion_rate_pct,
    RANK() OVER (ORDER BY 100.0 * conversions / total_exposures DESC) AS rank
FROM CampaignStats
ORDER BY rank;

-- ------------------------------------------------------------
-- Campaign type performance (engagement vs other objectives)
-- ------------------------------------------------------------

SELECT
    dcamp.campaign_type,
    dcamp.objective,
    COUNT(DISTINCT dcamp.campaign_id) AS campaign_count,
    COUNT(*) AS total_exposures,
    SUM(CASE WHEN fce.exposure_outcome = 'conversion' THEN 1 ELSE 0 END) AS conversions,
    ROUND(
        100.0 * SUM(CASE WHEN fce.exposure_outcome = 'conversion' THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS conversion_rate_pct
FROM dbo.Fact_Campaign_Exposures fce
JOIN dbo.Dim_Campaign dcamp ON fce.campaign_sk = dcamp.campaign_sk
GROUP BY dcamp.campaign_type, dcamp.objective
ORDER BY conversion_rate_pct DESC;

/*
    BUSINESS INTERPRETATION — fill in after running:
    - Which channel(s) genuinely outperform on conversion, not just
      volume
    - Whether the top-converting campaigns share a common channel
      or type

    BUSINESS IMPLICATION — fill in after running:
    - Where marketing spend should shift, based on actual conversion
      performance rather than exposure volume alone
*/
