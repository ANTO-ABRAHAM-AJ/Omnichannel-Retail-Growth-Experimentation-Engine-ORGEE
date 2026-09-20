# Phase 1 — Business Understanding
## 10. Project Timeline

---

## 1. Phase Sequence and Dependencies

| Phase | Deliverable | Depends On | What It Would Break If Skipped |
|---|---|---|---|
| 1 | Business Understanding | — | No documented rationale for any later scope decision |
| 2 | Hybrid Data Engineering | Phase 1 | Every later phase, which all rely on this data foundation |
| 3 | Enterprise SQL Data Warehouse | Phase 2 | All SQL analytics, since Phase 4 onward queries this warehouse directly |
| 4 | Advanced SQL Analytics | Phase 3 | The revenue and category findings referenced throughout Phases 6, 9, and 10 |
| 5 | Customer Journey Analytics | Phase 3 | The funnel and retention figures referenced in Phases 6, 9, and this document |
| 6 | Customer & Product Analytics | Phase 3, 4 | The RFM/CLV segmentation and North Star metric that Phase 10's scenarios are measured against |
| 7 | Recommendation Intelligence | Phase 3, 6 | The baseline evaluation that Phase 8's A/B test is designed to confirm or refute |
| 8 | Experimentation Framework | Phase 7 | The DO NOT SHIP decision that Phase 9's Product page and this document both rely on |
| 9 | Power BI Executive Decision Platform | Phase 4–8 | The interactive layer every other phase's findings are surfaced through |
| 10 | Decision Scenarios & What-If Analysis | Phase 9 | The scenario tool that lets Phase 7's baseline figures actually be manipulated by a decision-maker |

## 2. Note on Sequencing: Why Phase 1 Was Finalized Last

Phase 1 — this document — was intentionally finalized **after** the other nine phases were built, reviewed, and independently verified, rather than written up front and left unchanged. This was a deliberate methodological choice, not a shortcut: an accurate executive summary, business problem statement, and set of objectives are more credible when they describe what a project actually became, including its negative findings, than when they only restate what was planned before any data had been seen. Every figure and finding across all ten of Phase 1's documents was checked against the verified, final output of Phases 2 through 10 — not drafted speculatively in advance and left unreconciled.

## 3. Actual Build and Review Order

1. **Phases 2–8 built**, each independently reviewed for correctness before moving to the next — including data-correctness issues that were found and fixed as they surfaced during review, rather than only at the very end.
2. **A specific methodology bug was caught during Phase 9 QA and traced back to Phase 5**: the blended customer retention curve, originally computed in Phase 5's SQL as an unweighted average across cohorts, was found to disagree with the Power BI dashboard's size-weighted calculation by more than 10× at the one-month mark. The root cause (a handful of very small early cohorts skewing an unweighted average) was identified, Phase 5's SQL was corrected to match the statistically sounder weighted methodology, re-run, and verified to reconcile exactly with Phase 9's figure — and, independently, the corrected monthly retention percentages were confirmed to sum to within 0.02 percentage points of Phase 4's separately-verified overall repeat-purchase rate.
3. **Phase 9 built** — five Power BI dashboards — followed by a dedicated interactivity pass (synced category and date slicers, cross-page drill-through, verified against the underlying data-model relationships) and a separate visual/design consistency pass across all five pages (unified color palette, corrected number formatting, corrected title typos, and removal of a stray filter state left over from testing).
4. **Phase 10 built** — the interactive What-If scenario page — including its own full interactivity pass (preset scenario buttons built with bookmarks, a reset control, conditional formatting, and reordered KPI cards for a consistent Current → Scenario reading order).
5. **Phase 1 finalized last**, informed by the verified, completed state of the other nine phases — the order this document describes.
