# ORGEE — Enterprise Generation Configuration

**Project:** Omnichannel Retail & Growth Experimentation Engine

**Project Code:** ORGEE

**Version:** 1.0

**Phase:** Phase 2 — Hybrid Data Engineering

**Document:** Enterprise Generation Configuration

**Status:** LOCKED

---

# 1. Purpose

This document defines the quantitative configuration used by the ORGEE synthetic enterprise-data generators.

The configuration translates the approved enterprise entity design and generation rules into controlled generation parameters.

This document does **not** generate data.

It defines:

- Target row volumes
- Entity generation order
- Population rules
- Probability distributions
- Behavioral distributions
- Funnel transition probabilities
- Device distributions
- Channel distributions
- Identity-link proportions
- Experiment allocation
- Recommendation behavior
- Inventory behavior
- Temporal generation boundaries

The configuration must remain consistent with the ORGEE Phase 2 Enterprise Data Requirements, Entity Design, and Generation Rules.

---

# 2. Generation Principles

Synthetic data must:

1. Preserve the public Olist datasets.
2. Never overwrite public identifiers.
3. Maintain declared entity grain.
4. Maintain referential integrity.
5. Maintain temporal integrity.
6. Produce realistic behavioral patterns.
7. Produce meaningful analytical variation.
8. Avoid perfectly uniform distributions.
9. Avoid fabricated business results.
10. Remain reproducible through controlled random seeds.

The generator must create data that is **analytically useful**, not artificially perfect.

---

# 3. Public Data Population Reference

The synthetic enterprise layer will use the processed public Olist data as its integration foundation.

Reference populations:

| Public Entity | Reference Population |
|---|---:|
| Customers | 99,441 |
| Products | 32,951 |
| Sellers | 3,095 |
| Orders | 99,441 |
| Order Items | 112,650 |
| Payments | 103,886 |
| Reviews | 99,224 |
| Geolocation | 738,332 |
| Category Translation | 71 |

These populations are reference values from the processed public datasets.

The generator must not alter these datasets.

---

# 4. Enterprise Generation Order

Enterprise entities will be generated in dependency order.

```text
Customer Reference
        ↓
Sessions
        ↓
Events
        ↓
Identity Links
        ↓
Marketing Campaigns
        ↓
Campaign Exposures
        ↓
Inventory
        ↓
Experiments
        ↓
Experiment Assignments
        ↓
Recommendation Events
```

Where an entity depends on another generated entity, the parent entity must exist before child generation.

---

# 5. Target Enterprise Population

Initial target volumes:

| Entity | Target Volume |
|---|---:|
| Sessions | 500,000 |
| Events | 3,000,000 |
| Marketing Campaigns | 50 |
| Campaign Exposures | 1,000,000 |
| Inventory Observations | 1,000,000 |
| Identity Links | Derived from login events |
| Experiments | 1 |
| Experiment Assignments | Derived from eligible experimental population |
| Recommendation Events | Derived from recommendation impressions |

These are generation targets, not business findings.

Final generated volumes must be validated after generation.

---

# 6. Customer Participation

Synthetic behavioral activity will reference the public customer population.

Public `customer_id` values remain authoritative.

The generator will not create replacement customer identifiers.

Customer behavioral participation will intentionally be uneven.

Configuration:

| Customer Activity Segment | Approximate Population |
|---|---:|
| Highly Active | 10% |
| Active | 25% |
| Moderate | 40% |
| Low Activity | 25% |

The purpose is to create realistic behavioral variation.

These percentages describe synthetic generation behavior only.

They must not be presented as findings about the original Olist customers.

---

# 7. Anonymous User Population

The enterprise layer will support anonymous browsing before login.

Anonymous identifiers will be generated independently from public `customer_id`.

Identifier format:

```text
anonymous_id
```

Example structure:

```text
anon_<unique_identifier>
```

Anonymous IDs must be unique within the enterprise event ecosystem.

Anonymous users may:

- Browse products
- Search
- Add products to cart
- Begin checkout
- Log in
- Become associated with a public customer

Not every anonymous user must log in.

---

# 8. Session Configuration

Target sessions:

```text
500,000
```

Each session receives:

- `session_id`
- `anonymous_id`
- `customer_id` where known
- `device_type`
- `platform`
- `session_start_timestamp`
- `session_end_timestamp`

A session may contain multiple events.

Target session event intensity:

| Session Type | Approximate Share |
|---|---:|
| Short | 35% |
| Medium | 45% |
| Long | 20% |

The exact event count per session will be generated using controlled random variation rather than a fixed number.

---

# 9. Device Distribution

Initial device configuration:

| Device | Approximate Share |
|---|---:|
| Mobile | 55% |
| Desktop | 35% |
| Tablet | 10% |

The distribution exists to support device-level journey and conversion analysis.

Device values:

```text
mobile
desktop
tablet
```

---

# 10. Platform Distribution

Platform must remain consistent with device where appropriate.

Initial configuration:

| Platform | Approximate Share |
|---|---:|
| Web | 50% |
| Mobile App | 40% |
| Desktop | 10% |

Platform values:

```text
web
mobile_app
desktop
```

Device/platform compatibility must be enforced by the generator.

Conceptual compatibility:

```text
Mobile
    ↓
mobile_app or web

Desktop
    ↓
desktop or web

Tablet
    ↓
mobile_app or web
```

The generator may allow realistic browser/device variation where required, but it must not create clearly impossible device/platform combinations.

---

# 11. Event Configuration

Target events:

```text
3,000,000
```

Primary event types:

```text
session_start
search
product_view
add_to_cart
remove_from_cart
checkout_start
login
purchase_interaction
```

Recommendation-specific events are not part of the generic Events entity.

Recommendation interactions are represented exclusively through the Recommendation Events entity.

Event grain:

```text
One row = one customer behavioral event
```

Each event must contain sufficient identifiers to associate it with:

- Session
- Customer where known
- Anonymous user where applicable
- Product where applicable
- Timestamp
- Device/platform

---

# 12. Customer Journey Distribution

The generated event system must contain realistic funnel progression.

Conceptual journey:

```text
Session Start
      ↓
Search / Browse
      ↓
Product View
      ↓
Add to Cart
      ↓
Checkout
      ↓
Purchase
```

Not every session progresses through the entire journey.

Initial transition configuration:

| Transition | Approximate Probability |
|---|---:|
| Session → Search/Browse | 70% |
| Search/Browse → Product View | 75% |
| Product View → Add to Cart | 18% |
| Add to Cart → Checkout | 60% |
| Checkout → Purchase Interaction | 70% |

These probabilities are **generation parameters**, not expected final analytical results.

The generator must introduce natural variation rather than forcing exact percentages.

---

# 13. Funnel Drop-Off Requirement

The synthetic event layer must intentionally contain meaningful drop-offs.

The generator must NOT make the following journey deterministic:

```text
Session
↓
Search
↓
Product View
↓
Cart
↓
Checkout
↓
Purchase
```

Instead:

```text
Many Sessions
      ↓
Fewer Product Views
      ↓
Fewer Cart Actions
      ↓
Fewer Checkouts
      ↓
Fewer Purchases
```

The actual observed funnel rates will be calculated after generation.

---

# 14. Login Event Configuration

Login events provide the identity-stitching mechanism.

Some anonymous sessions must contain:

```text
anonymous_id
        ↓
login
        ↓
customer_id
```

Initial configuration:

```text
Target login-capable sessions:
approximately 25%
```

Not every login-capable session must successfully authenticate.

Successful login events will contain:

```text
anonymous_id
customer_id
session_id
event_timestamp
event_type = login
```

The login event must occur before subsequent authenticated activity in that session.

Only successful login events may create Identity Links.

---

# 15. Identity-Link Configuration

Identity Links are derived from successful login events.

They are not independently generated.

The enterprise layer must not invent arbitrary customer-device mappings unrelated to behavioral activity.

Relationship:

```text
anonymous_id
      ↓
successful login
      ↓
customer_id
```

Target:

```text
Approximately 20–25% of active anonymous identities
may become linked to a public customer through successful login.
```

Identity-link generation must ensure:

- Valid customer IDs
- Valid anonymous IDs
- Valid session IDs
- Valid login timestamps
- No impossible temporal ordering

The same anonymous identity must not be arbitrarily linked to conflicting customer IDs.

---

# 16. Marketing Campaign Configuration

Target campaigns:

```text
50
```

Campaign attributes:

- `campaign_id`
- `campaign_name`
- `channel`
- `campaign_type`
- `objective`
- `start_date`
- `end_date`

Initial channel distribution:

| Channel | Approximate Share |
|---|---:|
| Email | 25% |
| Social | 25% |
| Search | 20% |
| Display | 15% |
| Push | 15% |

Campaign objectives may include:

```text
acquisition
conversion
retention
engagement
promotion
```

---

# 17. Campaign Exposure Configuration

Target campaign exposures:

```text
1,000,000
```

One row represents one customer/anonymous identity's exposure to one campaign.

Exposure may be associated with:

- Customer
- Anonymous identity
- Campaign
- Channel
- Timestamp

Exposure outcomes may include:

```text
impression
click
conversion
```

Not every exposure should produce engagement.

Not every engagement should produce conversion.

---

# 18. Marketing Funnel

Marketing behavior should follow:

```text
Exposure
   ↓
Engagement
   ↓
Conversion
```

Initial generation parameters:

| Stage | Approximate Probability |
|---|---:|
| Exposure → Engagement | 10% |
| Engagement → Conversion | 8% |

These are synthetic generation parameters.

Actual campaign performance must be calculated from the generated dataset.

---

# 19. Inventory Configuration

Inventory observations represent product availability over time.

Target observations:

```text
1,000,000
```

Each observation may contain:

- `inventory_observation_id`
- `product_id`
- `inventory_location_id`
- `observation_timestamp`
- `available_quantity`
- `reserved_quantity`
- `inventory_status`

Inventory statuses:

```text
in_stock
low_stock
out_of_stock
```

Inventory quantity must remain non-negative.

---

# 20. Inventory Location Configuration

Initial inventory-location population:

```text
20 locations
```

Each inventory observation references:

```text
product_id
inventory_location_id
```

Products may appear at multiple locations.

Not every product must be available at every location.

This allows inventory availability analysis without creating an artificial one-product/one-location relationship.

---

# 21. Inventory Behavior

Inventory quantities should vary over time.

General behavior:

```text
High Stock
    ↓
Sales / Demand
    ↓
Stock Reduction
    ↓
Replenishment
    ↓
Stock Increase
```

The generator must avoid:

- Negative inventory
- Impossible quantities
- Constant inventory
- Universal product availability

Inventory behavior should allow analysis of:

- Stock availability
- Low-stock products
- Out-of-stock conditions
- Potential relationship between availability and customer behavior

---

# 22. Experiment Configuration

Target experiments:

```text
1
```

ORGEE v1.0 uses one primary experiment.

Primary experiment:

```text
Recommendation A/B Test
```

The experiment contains:

- `experiment_id`
- `experiment_name`
- `objective`
- `hypothesis`
- `start_timestamp`
- `end_timestamp`
- `primary_metric`

Primary metric:

```text
purchase_conversion_rate
```

Secondary metrics may include:

```text
recommendation_ctr
average_order_value
revenue_per_user
purchase_rate
```

Multiple experiments are not required for ORGEE v1.0.

---

# 23. Experiment Variant Configuration

Primary recommendation experiment:

```text
Control:
Top Sellers Recommendations

Treatment:
Personalized Content-Based Recommendations
```

Variants:

```text
control
treatment
```

Target allocation:

```text
50% Control
50% Treatment
```

The generator must include natural randomness but target approximately equal assignment.

Actual assignment balance will be validated using the Phase 8 SRM check.

The generator must not encode a predetermined treatment advantage.

---

# 24. Experiment Assignment

Experiment assignment grain:

```text
One row per experimental unit per experiment
```

Experimental unit:

```text
customer_id
```

Where appropriate, anonymous users may be excluded until identity is available.

Assignment must occur within the experiment period.

Each customer should receive only one primary variant assignment for the same experiment.

---

# 25. Recommendation Event Configuration

Recommendation events will support the Phase 7 recommendation engine and Phase 8 experiment.

Recommendation event types:

```text
impression
click
conversion
```

Grain:

```text
One row per recommendation interaction
```

Recommendation events must reference:

- Customer or anonymous identity
- Session
- Product
- Experiment where applicable
- Assignment where applicable
- Timestamp

Recommendation events are generated independently from the generic Events entity and must not be duplicated there.

---

# 26. Recommendation Funnel

Recommendation behavior:

```text
Recommendation Impression
          ↓
Recommendation Click
          ↓
Purchase / Conversion
```

Initial configuration:

| Transition | Approximate Probability |
|---|---:|
| Impression → Click | 12% |
| Click → Purchase | 8% |

These are generation parameters only.

Actual recommendation CTR and conversion must be calculated from generated events.

---

# 27. Temporal Configuration

Enterprise data must overlap with the public Olist transaction period where integration is required.

Primary behavioral period:

```text
Derived from the processed public orders observation period.
```

Generated timestamps must:

- Fall within the configured period
- Follow event sequence ordering
- Respect session start/end
- Respect campaign periods
- Respect experiment periods
- Respect identity-link timing

---

# 28. Event Temporal Ordering

Within a session:

```text
session_start
      ↓
search / browse
      ↓
product_view
      ↓
add_to_cart
      ↓
checkout_start
      ↓
purchase_interaction
```

Login must occur before authenticated customer activity.

Recommendation clicks must occur after recommendation impressions.

Recommendation conversions must occur after recommendation interactions.

Impossible event sequences must fail validation.

Identity Links must be created only from successful login events.

---

# 29. Randomness and Reproducibility

All synthetic generation must use controlled random seeds.

Primary seed:

```text
2026
```

Each generator may derive a deterministic sub-seed from the primary seed.

Example:

```text
sessions
events
marketing
inventory
experiments
recommendations
```

The same configuration and seed must produce reproducible results.

---

# 30. Identifier Rules

Synthetic identifiers must not overwrite public identifiers.

Public identifiers retained:

```text
customer_id
product_id
order_id
seller_id
```

Synthetic identifiers include:

```text
session_id
anonymous_id
campaign_id
campaign_exposure_id
inventory_observation_id
identity_link_id
experiment_id
experiment_assignment_id
recommendation_event_id
event_id
```

Identifiers must be unique at their declared grain.

---

# 31. Referential Integrity Requirements

Generated foreign keys must reference valid parent records.

Examples:

```text
event.session_id
        ↓
sessions.session_id
```

```text
event.product_id
        ↓
products.product_id
```

```text
campaign_exposure.campaign_id
        ↓
campaigns.campaign_id
```

```text
experiment_assignment.experiment_id
        ↓
experiments.experiment_id
```

```text
identity_link.customer_id
        ↓
customers.customer_id
```

```text
recommendation_event.assignment_id
        ↓
experiment_assignments.assignment_id
```

No orphan foreign keys are permitted.

---

# 32. Generation Validation Gates

Every generated entity must pass the following gates:

### Gate 1 — Schema

Correct columns and data types.

### Gate 2 — Grain

One row represents exactly the declared entity grain.

### Gate 3 — Uniqueness

Primary keys contain no duplicates.

### Gate 4 — Completeness

Required fields contain valid values.

### Gate 5 — Referential Integrity

Foreign keys resolve to valid parent entities.

### Gate 6 — Temporal Integrity

Timestamps follow logical ordering.

### Gate 7 — Distribution

Generated distributions remain within reasonable configured ranges.

### Gate 8 — Business Logic

Behavior remains realistic.

### Gate 9 — Integration Readiness

Synthetic entities can connect to the public Olist foundation.

---

# 33. Configuration Status

This configuration is an implementation specification for synthetic-data generation.

It does not represent observed Olist business performance.

All percentages and volumes defined here are generation parameters.

Actual analytical results will be calculated only after:

```text
Generation
    ↓
Validation
    ↓
Integration
    ↓
Analytics
```

---

# 34. Final Generation Principle

```text
CONFIGURATION
      ↓
GENERATION
      ↓
VALIDATION
      ↓
INTEGRATION
      ↓
ANALYSIS
```

The generator must never be designed to produce a predetermined analytical conclusion.

The data must generate the findings.