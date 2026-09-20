/*
    ============================================================
    ORGEE — Phase 3 data-quality patch v2 (corrected root cause)
    fix_dim_product_int_columns.sql
    ============================================================

    TRUE ROOT CAUSE (found after the first patch attempt silently
    produced 0 non-null rows again): the source CSV stores every
    numeric value in float-text format — "1.0", "40.0", "287.0" —
    not plain integers. TRY_CONVERT(INT, '1.0') returns NULL in
    SQL Server; direct string-to-INT conversion does not accept a
    decimal point, even for whole numbers. TRY_CONVERT(DECIMAL, ...)
    parses "1.0" correctly, which is exactly why product_weight_g /
    length / height / width (loaded as DECIMAL) came through fine
    in the original Phase 3 load — while every INT-typed column fed
    the same way failed silently.

    This affects THREE columns identically, not just photos_qty:
        product_photos_qty
        product_name_length
        product_description_length

    FIX: convert to DECIMAL first (parses "1.0" correctly), THEN
    round to INT — instead of attempting INT conversion directly
    on the raw decimal-formatted string.

    Supersedes fix_dim_product_photos_qty.sql — run this instead.
    (That first-attempt file addressed only product_photos_qty and
    used the same flawed direct-INT conversion; it has been removed
    from this deliverable as obsolete now that this script covers
    all three affected columns with the correct root-cause fix.)
*/

IF OBJECT_ID('tempdb..#IntColumnsPatch') IS NOT NULL DROP TABLE #IntColumnsPatch;

CREATE TABLE #IntColumnsPatch (
    product_id                  VARCHAR(32),
    product_category_name       VARCHAR(60) NULL,
    product_name_lenght         VARCHAR(20) NULL,
    product_description_lenght VARCHAR(20) NULL,
    product_photos_qty          VARCHAR(20) NULL,
    product_weight_g            VARCHAR(20) NULL,
    product_length_cm           VARCHAR(20) NULL,
    product_height_cm           VARCHAR(20) NULL,
    product_width_cm            VARCHAR(20) NULL
);

DECLARE @BasePath VARCHAR(500) =
    'C:\Users\ANTO ABRAHAM AJ\Downloads\Omnichannel Retail & Growth Experimentation Engine (ORGEE)\data\';

DECLARE @sql NVARCHAR(MAX);
SET @sql = N'
BULK INSERT #IntColumnsPatch
FROM ''' + @BasePath + N'processed\Public\olist_products_dataset.csv''
WITH (FORMAT = ''CSV'', FIRSTROW = 2, FIELDQUOTE = ''"'', CODEPAGE = ''65001'',
      ROWTERMINATOR = ''0x0d0a'', KEEPNULLS, TABLOCK);';
EXEC sp_executesql @sql;

-- ------------------------------------------------------------
-- Patch all 3 affected columns — DECIMAL first, then round to INT
-- ------------------------------------------------------------

UPDATE dp
SET
    dp.product_photos_qty = TRY_CONVERT(INT, TRY_CONVERT(DECIMAL(10,2), NULLIF(pp.product_photos_qty, ''))),
    dp.product_name_length = TRY_CONVERT(INT, TRY_CONVERT(DECIMAL(10,2), NULLIF(pp.product_name_lenght, ''))),
    dp.product_description_length = TRY_CONVERT(INT, TRY_CONVERT(DECIMAL(10,2), NULLIF(pp.product_description_lenght, '')))
FROM dbo.Dim_Product dp
JOIN #IntColumnsPatch pp ON dp.product_id = pp.product_id;

DROP TABLE #IntColumnsPatch;

-- ------------------------------------------------------------
-- Verify the fix — all three should now show non-zero non-null
-- counts close to 32,341 (photos_qty) / similar for the other two
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS total_products,
    COUNT(product_photos_qty) AS non_null_photos_qty,
    COUNT(product_name_length) AS non_null_name_length,
    COUNT(product_description_length) AS non_null_description_length,
    MIN(product_photos_qty) AS min_photos,
    MAX(product_photos_qty) AS max_photos
FROM dbo.Dim_Product;
