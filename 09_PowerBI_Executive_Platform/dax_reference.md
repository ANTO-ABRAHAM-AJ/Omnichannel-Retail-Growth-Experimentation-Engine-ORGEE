# Phase 9 — Power BI DAX Reference
## ORGEE — Omnichannel Retail & Growth Experimentation Engine

**Location:** ORGEE.pbix, `Table` / `_Measures`
**Companion to:** `data_model_reference.md`. Phase 10's scenario measures are documented separately in `04_phase10_readme.md`.

---

## Customer Measures

### Active Customers
```dax
Active Customers = 
CALCULATE(
    DISTINCTCOUNT(Dim_Customer[customer_unique_id]),
    Fact_Order_Items[order_status] = "delivered",
    CROSSFILTER(Fact_Order_Items[customer_sk], Dim_Customer[customer_sk], BOTH)
)
```
Distinct customers with at least one delivered order. Uses an inline `CROSSFILTER(..., BOTH)` rather than a global bidirectional relationship, so this measure specifically can be filtered by product category (via `Fact_Order_Items`) without changing the default filter direction for every other measure that touches this relationship.

### Repeat Purchase Rate %
```dax
Repeat Purchase Rate % = 
VAR CustomersWithOrders =
    CALCULATETABLE(
        SUMMARIZE(Fact_Order_Items, Dim_Customer[customer_unique_id], "OrderCount", DISTINCTCOUNT(Fact_Order_Items[order_id])),
        Fact_Order_Items[order_status] = "delivered",
        CROSSFILTER(Fact_Order_Items[customer_sk], Dim_Customer[customer_sk], BOTH)
    )
VAR RepeatCustomers = COUNTROWS(FILTER(CustomersWithOrders, [OrderCount] >= 2))
VAR TotalCustomers = COUNTROWS(CustomersWithOrders)
RETURN
    DIVIDE(RepeatCustomers, TotalCustomers) * 100
```
Percentage of customers (with a delivered order) who placed 2 or more delivered orders. Matches the 3.00% figure verified against Phase 4/6's SQL-derived repeat-purchase rate.

### Weighted Retention Rate %
```dax
Weighted Retention Rate % = 
DIVIDE(
    SUM(Customer_Cohort_Retention[retained_customers]),
    SUM(Customer_Cohort_Retention[cohort_size])
) * 100
```
Size-weighted blended retention across cohorts. This is the measure that exposed the unweighted-average bug in Phase 5's original SQL (`AVG(retention_pct)`) — see Phase 9 README, Section 5, for the full root-cause writeup. Correct as originally written here; Phase 5's SQL was corrected to match it.

### Average CLV
```dax
Average CLV = AVERAGE(Customer_RFM_Segments[historical_clv])
```

### Total Historical CLV
```dax
Total Historical CLV = SUM(Customer_RFM_Segments[historical_clv])
```

---

## Revenue & Order Measures

### Total Revenue
```dax
Total Revenue = CALCULATE(SUM(Fact_Order_Items[price]), Fact_Order_Items[order_status] = "delivered")
```
The baseline figure ($13.22M) that every other revenue calculation in Phases 9 and 10 traces back to.

### Delivered Orders
```dax
Delivered Orders = CALCULATE(DISTINCTCOUNT(Fact_Order_Items[order_id]), Fact_Order_Items[order_status] = "delivered")
```

### AOV
```dax
AOV = DIVIDE([Total Revenue], [Delivered Orders])
```

### Revenue per Active Customer
```dax
Revenue per Active Customer = DIVIDE([Total Revenue], [Active Customers])
```
This is the measure tied to the Phase 6 North Star metric, "Monthly Delivered Revenue per Active Customer," and the one the Phase 10 "Customer Value Impact" chart is built on.

---

## Funnel & Conversion Measures

### Purchase Conversion Rate %
```dax
Purchase Conversion Rate % = 
DIVIDE(
    SUM(vw_Daily_Product_Funnel[purchase]),
    SUM(vw_Daily_Product_Funnel[visits])
) * 100
```
Session-funnel based conversion rate (500K visits → 47K purchases). Note this is a different underlying source (`vw_Daily_Product_Funnel`, session-level) than `Total Revenue`/`AOV` (`Fact_Order_Items`, order-level) — the two don't share a `Dim_Product` relationship, which is why the Product page's funnel visual can't be filtered by category (see Phase 9 README, Section 7).

---

## Recommendation Measures

### Recommendation Coverage %
```dax
Recommendation Coverage % = 
DIVIDE(
    DISTINCTCOUNT('reco recommendations'[customer_unique_id]),
    95137
) * 100
```
**⚠️ Maintainability note:** the denominator is a hardcoded constant (`95137`), not a live measure. If the underlying customer base changes (e.g. from regenerating synthetic data), this figure will silently go stale rather than update automatically. Consider replacing `95137` with a `DISTINCTCOUNT` measure against the appropriate customer table if this project is extended further.

### Avg Recommendation Similarity
```dax
Avg Recommendation Similarity = AVERAGE('reco recommendations'[similarity_score])
```

---

## Marketing Measures

### Total Campaign Impressions
```dax
Total Campaign Impressions = SUM(vw_Daily_Campaign_Performance[impressions])
```

### Overall CTR %
```dax
Overall CTR % = 
DIVIDE(
    SUM(vw_Daily_Campaign_Performance[clicks]),
    SUM(vw_Daily_Campaign_Performance[impressions])
) * 100
```

### Overall Campaign Conversion Rate %
```dax
Overall Campaign Conversion Rate % = 
DIVIDE(
    SUM(vw_Daily_Campaign_Performance[conversions]),
    SUM(vw_Daily_Campaign_Performance[impressions])
) * 100
```

---

## Summary

| Measure | Source table | Notes |
|---|---|---|
| Active Customers | Fact_Order_Items, Dim_Customer | Inline CROSSFILTER for category-slicer support |
| Repeat Purchase Rate % | Fact_Order_Items, Dim_Customer | Verified against Phase 4/6 SQL (3.00%) |
| Weighted Retention Rate % | Customer_Cohort_Retention | Size-weighted; exposed and fixed a Phase 5 SQL bug |
| Average / Total Historical CLV | Customer_RFM_Segments | |
| Total Revenue | Fact_Order_Items | Baseline for all Phase 9/10 revenue figures |
| Delivered Orders | Fact_Order_Items | |
| AOV | Total Revenue, Delivered Orders | |
| Revenue per Active Customer | Total Revenue, Active Customers | Tied to Phase 6 North Star metric |
| Purchase Conversion Rate % | vw_Daily_Product_Funnel | Session-level source, not order-level |
| Recommendation Coverage % | reco recommendations | Hardcoded denominator — flagged above |
| Avg Recommendation Similarity | reco recommendations | |
| Total Campaign Impressions / Overall CTR % / Overall Campaign Conversion Rate % | vw_Daily_Campaign_Performance | |
