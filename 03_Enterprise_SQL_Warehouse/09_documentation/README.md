# ORGEE — Phase 3: Enterprise SQL Data Warehouse

**Engine:** SQL Server
**Methodology:** Kimball star schema, Type 1 SCD throughout
**Status:** Complete — 16/16 tables built, loaded, indexed, and validated (28/28 checks passing)

## What's in here

| Folder | Contents |
|---|---|
| `01_schema_design` | Design doc: dimension/fact list, grain definitions, star schema map, source-to-target mapping |
| `02_dimension_ddl` | `CREATE TABLE` scripts for all 7 dimensions |
| `03_fact_ddl` | `CREATE TABLE` scripts for all 9 facts |
| `04_keys_constraints` | Foreign key constraints, one script per fact table |
| `05_data_load` | Staging tables, `BULK INSERT` scripts, and the staging → warehouse transform (dimensions then facts) |
| `06_indexes` | Clustered columnstore index on `Fact_Events` + supporting nonclustered indexes |
| `07_warehouse_build` | Master script — rebuilds the entire warehouse from a clean database in one run (requires SQLCMD Mode) |
| `08_validation` | 28-check SQL validation suite: row counts, grain, referential integrity, business logic, index confirmation |
| `09_documentation` | This README, the data dictionary, and the ER diagram |

## Schema at a glance

**7 dimensions:** Customer, Product, Seller, Date, Campaign, Experiment, Device
**9 facts:** Order_Items, Reviews, Sessions, Events, Identity_Links, Campaign_Exposures, Inventory_Snapshot, Experiment_Assignments, Recommendation_Events

Full column-level detail is in [`data_dictionary.md`](./data_dictionary.md). The relationship map is in [`er_diagram.md`](./er_diagram.md) (Mermaid — renders directly in GitHub).

## Design decisions worth knowing

**Anonymous-until-login identity model.** Every `customer_sk` foreign key on `Fact_Sessions`, `Fact_Events`, `Fact_Campaign_Exposures`, and `Fact_Recommendation_Events` is **nullable**. This isn't an oversight — it's the direct product of the Phase 2 identity-resolution fix: a session/event starts anonymous and is only tied to a known customer once a successful login event resolves it. Roughly 18% of sessions end up identified; the rest are legitimately anonymous browsing. **Always `LEFT JOIN` to `Dim_Customer`** when querying these tables — an inner join silently drops the majority of rows.

**Payments folded into `Fact_Order_Items`.** Rather than a separate `Fact_Payments`, payment measures (total value, max installments, primary payment type) are rolled up per `order_id` and attached to each order's line items — payment grain doesn't map cleanly 1:1 to order items in this dataset.

**`Fact_Reviews` grain is `(review_id, order_id)`, not `review_id` alone.** The public Olist review dataset genuinely contains 1,603 rows where the same `review_id` appears against a different `order_id` — verified, not a data error on our part.

**`Fact_Events` uses a clustered columnstore index**, not a traditional clustered B-tree. At 3,000,000 rows and growing only through appends (never updated in place), columnstore gives far better compression and aggregation performance for the funnel/cohort analytics Phase 4–5 will run. Its primary key is deliberately `NONCLUSTERED` to leave the clustered slot free for this.

**`inventory_observations.csv` is a format outlier.** Every other enterprise CSV uses ISO timestamps (`YYYY-MM-DD HH:MM:SS`) with LF-only line endings. This one file uses `DD-MM-YYYY HH:MM` with CRLF endings — a leftover from before the Phase 2 regeneration, since inventory generation was never part of that fix. The load scripts handle this explicitly; see the comments in `05_data_load/02_bulk_load_staging.sql` and `04_load_facts.sql`.

## Rebuilding from scratch

Run `07_warehouse_build/master_build.sql` against a clean database (enable SQLCMD Mode in SSMS first: Query menu → SQLCMD Mode). It runs every script in `02` through `06` in the correct dependency order and ends with a full row-count check. Update the `@BasePath` variable inside `05_data_load/02_bulk_load_staging.sql` to point at your local CSV location before running.

## Validating an existing build

Run `08_validation/08_warehouse_validation.sql`. It checks row counts (via catalog metadata, not full table scans — safe even on memory-constrained machines), grain/uniqueness, referential integrity, and the business-logic invariants specific to this project's history (identity resolution consistency, no event-type leakage, real funnel drop-off, clean inventory data). Ends with a clear PASS/FAIL summary.
