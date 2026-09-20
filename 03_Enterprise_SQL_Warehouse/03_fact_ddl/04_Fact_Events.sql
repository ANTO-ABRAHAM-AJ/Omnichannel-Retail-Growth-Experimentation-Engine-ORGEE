/*
    ORGEE — Phase 3: Fact_Events
    Grain: one row per behavioral event
    Source: events.csv
    Volume: 3,000,000 rows — the largest table in the warehouse.
    A clustered columnstore index is planned for this table in
    06_indexes (better compression + scan performance for the
    funnel/journey analytics in Phase 4-5 than a rowstore clustered
    index on a table this size and this write-once/read-many).

    NOTE: customer_sk and product_sk are both NULLABLE.
    customer_sk: null until a login event identifies the session
    (matches Fact_Sessions — see Phase 2 identity-resolution fix).
    product_sk: null for events not tied to a specific product
    (e.g. session_start, checkout_start, login).
*/

IF OBJECT_ID('dbo.Fact_Events', 'U') IS NOT NULL
    DROP TABLE dbo.Fact_Events;
GO

CREATE TABLE dbo.Fact_Events (
    event_sk            BIGINT          IDENTITY(1,1)  NOT NULL,

    event_id               VARCHAR(20)                 NOT NULL,   -- e.g. 'evt_000000001'
    session_id                VARCHAR(20)               NOT NULL,
    anonymous_id                 VARCHAR(20)             NOT NULL,

    customer_sk               INT                       NULL,      -- nullable: pre-login events
    product_sk                   INT                    NULL,      -- nullable: not all events are product-linked
    device_sk                       INT                 NULL,
    event_date_sk                     INT                NULL,

    event_timestamp             DATETIME2                NOT NULL,
    event_type                     VARCHAR(20)            NOT NULL,  -- session_start, search, product_view,
                                                                      -- add_to_cart, remove_from_cart,
                                                                      -- checkout_start, login, purchase_interaction

    load_timestamp                 DATETIME2  DEFAULT SYSUTCDATETIME() NOT NULL,

    CONSTRAINT PK_Fact_Events PRIMARY KEY NONCLUSTERED (event_sk),
    CONSTRAINT UQ_Fact_Events_event_id UNIQUE NONCLUSTERED (event_id)
);
GO

-- NOTE: PK/UQ intentionally declared NONCLUSTERED here because the
-- clustered index slot on this table is reserved for the columnstore
-- index that will be added in 06_indexes.
