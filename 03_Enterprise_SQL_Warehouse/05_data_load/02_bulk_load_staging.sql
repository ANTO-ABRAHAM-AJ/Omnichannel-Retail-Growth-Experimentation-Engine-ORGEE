/*
    ORGEE — Phase 3: Bulk Load Staging Tables

    Set @BasePath below to your project root ONCE — every load below
    is built from it via dynamic SQL, so you only edit one line if
    you ever move the folder or run this on another machine.

    IMPORTANT — line endings differ between the two data sources:
        Public (Olist) CSVs   -> CRLF   -> ROWTERMINATOR = '0x0d0a'
        Enterprise CSVs        -> LF only -> ROWTERMINATOR = '0x0a'
    Using the wrong terminator silently corrupts the last column of
    every row (a trailing \r gets appended to it) — verified against
    your actual files before writing this script.
*/

DECLARE @BasePath VARCHAR(500) =
    'C:\Users\ANTO ABRAHAM AJ\Downloads\Omnichannel Retail & Growth Experimentation Engine (ORGEE)\data\';

DECLARE @sql NVARCHAR(MAX);

-- ============================================================
-- PUBLIC DATA  (CRLF line endings)
-- ============================================================

SET @sql = N'
BULK INSERT staging.stg_customers
FROM ''' + @BasePath + N'processed\Public\olist_customers_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_products
FROM ''' + @BasePath + N'processed\Public\olist_products_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_category_translation
FROM ''' + @BasePath + N'processed\Public\product_category_name_translation.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_sellers
FROM ''' + @BasePath + N'processed\Public\olist_sellers_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_orders
FROM ''' + @BasePath + N'processed\Public\olist_orders_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_order_items
FROM ''' + @BasePath + N'processed\Public\olist_order_items_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_order_payments
FROM ''' + @BasePath + N'processed\Public\olist_order_payments_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_order_reviews
FROM ''' + @BasePath + N'processed\Public\olist_order_reviews_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

-- ============================================================
-- ENTERPRISE DATA  (LF-only line endings)
-- ============================================================

SET @sql = N'
BULK INSERT staging.stg_sessions
FROM ''' + @BasePath + N'enterprise\sessions\sessions.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_events
FROM ''' + @BasePath + N'enterprise\events\events.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_identity_links
FROM ''' + @BasePath + N'enterprise\identity\identity_links.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_campaigns
FROM ''' + @BasePath + N'enterprise\marketing\campaigns.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_campaign_exposures
FROM ''' + @BasePath + N'enterprise\marketing\campaign_exposures.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_experiments
FROM ''' + @BasePath + N'enterprise\experiments\experiments.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_experiment_assignments
FROM ''' + @BasePath + N'enterprise\experiments\experiment_assignments.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_inventory_observations
FROM ''' + @BasePath + N'enterprise\inventory\inventory_observations.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);'; -- fix: this ONE enterprise file
      -- uses CRLF (DD-MM-YYYY HH:MM format), unlike every other
      -- enterprise file which is LF-only ISO format. Verified against
      -- all 1,000,000 rows.
EXEC sp_executesql @sql;

SET @sql = N'
BULK INSERT staging.stg_recommendation_events
FROM ''' + @BasePath + N'enterprise\recommendations\recommendation_events.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

-- ============================================================
-- Row count sanity check
-- ============================================================

SELECT 'stg_customers' AS staging_table, COUNT(*) AS row_count FROM staging.stg_customers
UNION ALL SELECT 'stg_products', COUNT(*) FROM staging.stg_products
UNION ALL SELECT 'stg_category_translation', COUNT(*) FROM staging.stg_category_translation
UNION ALL SELECT 'stg_sellers', COUNT(*) FROM staging.stg_sellers
UNION ALL SELECT 'stg_orders', COUNT(*) FROM staging.stg_orders
UNION ALL SELECT 'stg_order_items', COUNT(*) FROM staging.stg_order_items
UNION ALL SELECT 'stg_order_payments', COUNT(*) FROM staging.stg_order_payments
UNION ALL SELECT 'stg_order_reviews', COUNT(*) FROM staging.stg_order_reviews
UNION ALL SELECT 'stg_sessions', COUNT(*) FROM staging.stg_sessions
UNION ALL SELECT 'stg_events', COUNT(*) FROM staging.stg_events
UNION ALL SELECT 'stg_identity_links', COUNT(*) FROM staging.stg_identity_links
UNION ALL SELECT 'stg_campaigns', COUNT(*) FROM staging.stg_campaigns
UNION ALL SELECT 'stg_campaign_exposures', COUNT(*) FROM staging.stg_campaign_exposures
UNION ALL SELECT 'stg_experiments', COUNT(*) FROM staging.stg_experiments
UNION ALL SELECT 'stg_experiment_assignments', COUNT(*) FROM staging.stg_experiment_assignments
UNION ALL SELECT 'stg_inventory_observations', COUNT(*) FROM staging.stg_inventory_observations
UNION ALL SELECT 'stg_recommendation_events', COUNT(*) FROM staging.stg_recommendation_events;
