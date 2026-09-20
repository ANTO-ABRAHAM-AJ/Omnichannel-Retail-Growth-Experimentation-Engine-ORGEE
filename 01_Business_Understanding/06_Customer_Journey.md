# Phase 1 — Business Understanding
## 06. Customer Journey

---

## 1. The Mapped Journey

```
Visit
  ↓
Product View
  ↓
Add to Cart
  ↓
Checkout
  ↓
Purchase
  ↓
(Delivered → eligible for repeat purchase / retention tracking)
```

Cross-device identity is stitched at the **login event**: a customer may browse anonymously on mobile, view products, and add items to cart — all under an anonymous session identifier — then log in, at which point their prior anonymous activity becomes linked to a known `customer_id` for the remainder of their journey, including a later purchase completed from an entirely different device. This login-event-based stitching is a realistic, demonstrable approach to solving omnichannel identity resolution, deliberately scoped to avoid overbuilding a production-grade identity graph that this project doesn't need in order to answer its core business questions.

## 2. What the Funnel Data Actually Showed

Out of 500,000 tracked sessions:

| Stage | Volume | % of Total Visits | Drop-off from Previous Stage |
|---|---|---|---|
| Visit | 500,000 | 100.00% | — |
| Product View | 405,699 | 81.14% | 18.86% |
| Add to Cart | 151,078 | 30.22% | 62.76% |
| Checkout | 81,736 | 16.35% | 45.90% |
| Purchase | 47,418 | 9.48% | 41.99% |

**The single largest friction point in the entire journey is Product View → Add to Cart, a 62.76% drop-off** — a larger percentage loss than any other stage, including the final Checkout → Purchase step. This is the clearest, most directly actionable opportunity in the customer journey: more customers who have already engaged with a specific product are lost here than at any later, more committed stage.

## 3. Session Behavior by Type

Sessions were also analyzed by engagement depth (Long, Medium, Short), with longer sessions converting at a meaningfully higher rate than shorter ones — consistent with the intuitive expectation that deeper engagement within a session correlates with purchase intent, and confirming that session-length data is a genuine, usable signal rather than noise.

## 4. The Post-Purchase Journey: Retention

The journey does not end at purchase — Phase 5's cohort retention analysis tracked what happens afterward, and the pattern is the most concentrated finding in the entire project:

| Month Offset | Blended Retention |
|---|---|
| Month 0 (purchase month) | 100.00% |
| Month 1 | 0.48% |
| Month 2 | 0.34% |
| Months 3–12 | 0.17%–0.26% |

Blended retention falls from 100% to just 0.48% within a single month of a customer's first purchase, and remains in a narrow low band for the rest of the year that follows. In practical terms: **the customer journey, for 97% of customers, is a single-purchase journey.** Only 3.00% of customers ever return for a second order (Phase 4/6), and this retention curve shows that whatever repeat-purchase activity does occur is concentrated almost entirely in the first month — after which the opportunity to re-engage a customer drops sharply and stays low.

## 5. What This Means

Two distinct, addressable opportunities emerge from the journey data, and they are different problems requiring different interventions:

1. **Pre-purchase:** the Product View → Add to Cart drop-off is a product-discovery and cart-conversion problem — addressed through Phase 6's Product Analytics and Phase 7's recommendation engine work.
2. **Post-purchase:** the Month 0 → Month 1 retention cliff is a re-engagement and win-back problem — addressed through Phase 6's customer segmentation, which identifies which customers are worth prioritizing for exactly this kind of intervention.
