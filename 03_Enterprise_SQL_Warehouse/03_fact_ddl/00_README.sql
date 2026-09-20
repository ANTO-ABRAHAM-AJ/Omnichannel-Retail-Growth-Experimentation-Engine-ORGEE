/*
    ORGEE — Phase 3: Run all Fact DDL

    IMPORTANT: run 02_dimension_ddl FIRST — these fact tables reference
    Dim_* tables conceptually (via *_sk columns), even though actual
    FK CONSTRAINTs are added later in 04_keys_constraints, after both
    dimensions and facts exist and are loaded.

    Run 01 through 09 in any order — no FK dependencies between fact
    tables themselves.
*/

PRINT 'Run 01_Fact_Order_Items.sql through 09_Fact_Recommendation_Events.sql individually.';
GO
