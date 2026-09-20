# ORGEE — Enterprise Generation Rules

## Omnichannel Retail & Growth Experimentation Engine

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Project Code:** ORGEE  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Enterprise Generation Rules  
**Status:** 🔒 LOCKED

---

# 1. Purpose

This document defines the rules used to generate the synthetic enterprise
data layer for ORGEE.

The enterprise data must complement the public Olist transactional
foundation.

Synthetic generation must:

- Preserve public data
- Preserve public identifiers
- Follow the approved entity grains
- Preserve referential integrity
- Preserve temporal integrity
- Represent realistic retail behavior
- Support the locked ORGEE analytical objectives
- Avoid fabricated business conclusions

The generation process follows:

    ENTITY DESIGN
          ↓
    GENERATION RULES
          ↓
    SYNTHETIC DATA
          ↓
    VALIDATION
          ↓
    HYBRID INTEGRATION

---

# 2. Generation Principles

## 2.1 Public Data Is Authoritative

The following public entities remain authoritative:

- customers
- products
- orders
- order_items
- sellers
- payments
- reviews
- geolocation
- category_translation

Synthetic enterprise data must reference these entities rather than
replace them.

---

## 2.2 Public Identifiers Must Not Be Modified

The following identifiers must remain unchanged:

    customer_id
    product_id
    order_id
    seller_id

Synthetic entities may reference them through foreign keys.

---

## 2.3 Synthetic Data Fills Analytical Gaps

Synthetic data exists because the public dataset does not provide the
complete behavioral and enterprise signals required by ORGEE.

The synthetic layer therefore provides:

    Behavior
    Sessions
    Marketing
    Inventory
    Identity
    Experiments
    Recommendations

---

## 2.4 Business Realism Over Randomness

Synthetic data must not simply consist of independent random values.

Relationships must produce realistic business behavior.

For example:

    Session
       ↓
    Product View
       ↓
    Add to Cart
       ↓
    Checkout
       ↓
    Purchase

must be possible.

However:

    Session
       ↓
    Product View
       ↓
    Purchase

must also be possible.

Not every customer completes every journey.

---

# 3. Observation Period

The enterprise data must operate within the same broad observation
period as the public transactional foundation.

The public Olist data covers approximately:

    2016 — 2018

Enterprise timestamps must therefore be generated within the
compatible analytical observation period.

The exact start and end boundaries will be determined from the
processed public orders data during generator implementation.

The generator must not create enterprise activity outside the defined
observation period unless explicitly required by a later analytical
requirement.

---

# 4. ENTITY 01 — SESSIONS GENERATION

## 4.1 Grain

One row = one browsing session.

---

## 4.2 Target Volume

Initial target:

    200,000 – 500,000 sessions

The final value will be selected during implementation based on
performance and event-volume requirements.

---

## 4.3 Customer Assignment

Sessions will be divided into:

    Known Customer Sessions
    Anonymous Sessions

Known sessions contain:

    customer_id

Anonymous sessions contain:

    anonymous_id

Some sessions may transition from anonymous to known through a
successful login event.

---

## 4.4 Anonymous Identity Generation

Anonymous IDs must be generated independently from public customer IDs.

Example:

    anonymous_id
    ANON-000001
    ANON-000002
    ANON-000003
    ...

Anonymous identifiers must be unique.

---

## 4.5 Customer Selection

Known customer sessions should be sampled from valid public
customer_id values.

Customer activity should not be perfectly uniform.

The generation should allow realistic differences in engagement.

Conceptually:

    Low Activity Customers
            ↓
    Moderate Activity Customers
            ↓
    Highly Engaged Customers

The exact distribution will be implemented without claiming that the
synthetic distribution represents measured Olist behavior.

---

## 4.6 Device Distribution

Sessions should support:

    mobile
    desktop
    tablet

The generator should create a mixed omnichannel population.

The distribution is synthetic and exists to support device-level
analysis.

---

## 4.7 Platform Distribution

Supported platforms:

    web
    mobile_app
    desktop

Platform must remain logically compatible with device type.

---

## 4.8 Session Duration

Each session receives:

    session_start
    session_end

with:

    session_start < session_end

Session durations should vary.

Avoid making every session exactly the same length.

---

## 4.9 Session Conversion

A session may be:

    converted
    not_converted

Conversion status must be derived from associated behavior rather than
being independently assigned after events are generated.

---

# 5. ENTITY 02 — IDENTITY LINKS GENERATION

## 5.1 Purpose

Identity Links provide the controlled login-event-based cross-device
identity mechanism.

Identity Links are created only from successful login events.

---

## 5.2 Target Volume

Initial target:

    20,000 – 60,000 identity links

The final volume will be determined by the number of successful login
events generated.

---

## 5.3 Generation Logic

The relationship must follow:

    anonymous_id
          ↓
    anonymous session
          ↓
    login event
          ↓
    successful authentication
          ↓
    identity link
          ↓
    customer_id

The Identity Link must not be generated independently of a successful
login event.

---

## 5.4 Customer Selection

Each identity link must reference a valid:

    customer_id

from public customers.

---

## 5.5 Anonymous Identity Rule

An anonymous_id must not be linked to conflicting customer IDs.

For example, this is invalid:

    ANON-001 → CUST-001
    ANON-001 → CUST-002

unless a future explicitly approved identity lifecycle requires such
behavior.

For ORGEE v1.0:

    one anonymous identity → one customer identity

---

## 5.6 Link Timestamp

The identity link timestamp must correspond to the successful login
event.

Therefore:

    successful login event timestamp
                ≈
    identity link timestamp

The implementation may use the same timestamp or a small deterministic
offset.

---

## 5.7 Identity-Link Creation Rule

The generator must enforce:

    Successful Login Event
            ↓
    Identity Link

Every generated Identity Link must have:

- A valid `anonymous_id`
- A valid `customer_id`
- A valid `session_id`
- A corresponding successful login event
- A logically valid timestamp

Identity Links must never be created through random customer-to-
anonymous assignment.

---

# 6. ENTITY 03 — EVENTS GENERATION

## 6.1 Grain

One row = one behavioral event.

---

## 6.2 Target Volume

Initial target:

    1,000,000 – 3,000,000 events

---

## 6.3 Event Types

The general Events entity contains the following controlled vocabulary:

    session_start
    search
    product_view
    add_to_cart
    remove_from_cart
    checkout_start
    login
    purchase_interaction

Recommendation-specific events are excluded from the general Events
entity.

They are generated exclusively through the Recommendation Events
entity.

---

## 6.4 Event Distribution

The generator must not create equal quantities of every event type.

For example:

    session_start
          ↓
    many sessions

    product_view
          ↓
    many events

    add_to_cart
          ↓
    fewer events

    checkout_start
          ↓
    fewer events

    purchase_interaction
          ↓
    fewer events

This creates a funnel structure.

The actual proportions are generation parameters and must be documented
in the generator configuration.

---

# 7. CUSTOMER JOURNEY GENERATION

## 7.1 Core Journey

The minimum conceptual journey is:

    Session Start
          ↓
    Search
          ↓
    Product View
          ↓
    Add to Cart
          ↓
    Checkout Start
          ↓
    Purchase Interaction

Recommendation interactions are handled separately by the
Recommendation Events entity.

---

## 7.2 Realistic Drop-Off

Not every session follows the complete path.

Possible journeys include:

### Journey A

    Session Start
    ↓
    Product View
    ↓
    Exit

### Journey B

    Session Start
    ↓
    Search
    ↓
    Product View
    ↓
    Exit

### Journey C

    Session Start
    ↓
    Product View
    ↓
    Add to Cart
    ↓
    Exit

### Journey D

    Session Start
    ↓
    Search
    ↓
    Product View
    ↓
    Add to Cart
    ↓
    Checkout Start
    ↓
    Purchase Interaction

---

## 7.3 Funnel Ordering

The generator must enforce:

    session_start
        ≤
    search
        ≤
    product_view
        ≤
    add_to_cart
        ≤
    checkout_start
        ≤
    purchase_interaction

Only applicable events need to exist.

---

## 7.4 Product Selection

Product events must reference valid public:

    product_id

Products should be sampled from the public product population.

Product selection should allow repeated interaction with products.

---

## 7.5 Order Association

A purchase interaction may be associated with a valid:

    order_id

from the public order dataset when the synthetic event is intended
to represent behavior associated with a completed public transaction.

The generator must not invent public order IDs.

---

# 8. LOGIN EVENT GENERATION

Login events provide the identity-stitching signal.

The logical sequence is:

    Anonymous Session
          ↓
    Behavior
          ↓
    Login Event
          ↓
    Successful Authentication
          ↓
    Identity Link
          ↓
    Customer Identified

For successful login events:

    anonymous_id = populated
    customer_id  = populated
    event_type   = login

The login must occur during the associated session.

After successful login, later events may contain the identified
customer_id.

Every Identity Link must be traceable back to a successful login event.

---

# 9. EVENT DEVICE AND PLATFORM RULES

Each event inherits the session's device/platform context unless a
specific business rule requires otherwise.

Example:

    Session
    device_type = mobile
    platform    = mobile_app

            ↓

    Events inherit:

    device_type = mobile
    platform    = mobile_app

This avoids inconsistent event/session metadata.

---

# 10. ENTITY 04 — MARKETING CAMPAIGNS GENERATION

## 10.1 Grain

One row = one campaign.

---

## 10.2 Target Volume

    20 – 50 campaigns

---

## 10.3 Channels

Supported channels:

    email
    social
    search
    display
    push
    affiliate

---

## 10.4 Objectives

Supported objectives:

    acquisition
    conversion
    retention
    re-engagement
    promotion

---

## 10.5 Campaign Dates

Every campaign must satisfy:

    start_date <= end_date

Campaigns should overlap the observation period.

---

## 10.6 Budget

Budget must be:

    >= 0

The budget is synthetic and exists to support marketing analysis.

---

# 11. ENTITY 05 — CAMPAIGN EXPOSURE GENERATION

## 11.1 Grain

One row = one campaign exposure.

---

## 11.2 Target Volume

    300,000 – 1,000,000 exposures

---

## 11.3 Exposure Relationship

Every exposure must reference:

    campaign_id

and either:

    customer_id

or:

    anonymous_id

according to the identity state.

---

## 11.4 Temporal Rule

Exposure must occur during the campaign period:

    campaign.start_date
            ≤
    exposure_timestamp
            ≤
    campaign.end_date

---

## 11.5 Engagement

An exposure may result in:

    click = false

or:

    click = true

Not every exposure should be clicked.

---

## 11.6 Conversion

Conversion must be less frequent than exposure.

The generator must not force every clicked exposure to convert.

---

## 11.7 Channel Consistency

Exposure channel must match a valid campaign channel.

---

# 12. ENTITY 06 — INVENTORY GENERATION

## 12.1 Grain

One row = one product-location-time inventory observation.

---

## 12.2 Target Volume

    500,000 – 1,500,000 observations

---

## 12.3 Product Relationship

Every inventory observation must reference:

    products.product_id

---

## 12.4 Inventory Location

A controlled set of synthetic inventory locations will be generated.

Example:

    INV_LOC_001
    INV_LOC_002
    INV_LOC_003
    ...

The locations are synthetic operational entities.

---

## 12.5 Quantity Rules

Quantities must be non-negative.

    available_quantity >= 0
    reserved_quantity >= 0

---

## 12.6 Status Rules

Conceptual relationship:

    available_quantity > threshold
            ↓
    in_stock

    low positive quantity
            ↓
    low_stock

    available_quantity = 0
            ↓
    out_of_stock

The threshold will be defined in the generator configuration.

---

## 12.7 Temporal Inventory Behavior

Inventory observations for the same product/location should follow
chronological order.

Inventory can:

    increase
    decrease
    reach zero
    recover

This creates an analytical inventory history rather than independent
random snapshots.

---

# 13. ENTITY 07 — EXPERIMENTS GENERATION

## 13.1 Grain

One row = one experiment.

---

## 13.2 Target Volume

    1 experiment

Additional experiments are not required for ORGEE v1.0.

---

## 13.3 Primary Experiment

The primary and required experiment is:

    Recommendation A/B Test

---

## 13.4 Primary Metric

    Purchase Conversion Rate

---

## 13.5 Secondary Metrics

    Recommendation CTR
    Average Order Value
    Revenue per User
    Purchase Rate

---

## 13.6 Hypothesis

The experiment should support the business hypothesis:

    Personalized recommendations will improve purchase conversion
    relative to the control experience.

This is the experiment hypothesis.

It is not a predetermined result.

---

# 14. ENTITY 08 — EXPERIMENT ASSIGNMENTS GENERATION

## 14.1 Grain

One row = one experimental-unit assignment.

---

## 14.2 Experimental Unit

The primary ORGEE recommendation experiment uses:

    customer

as the experimental unit.

---

## 14.3 Target Volume

    50,000 – 100,000 assignments

---

## 14.4 Assignment Split

Target:

    50% control
    50% treatment

The exact generated counts may differ slightly due to the selected
experimental population size.

---

## 14.5 Assignment Rule

Each customer may receive one assignment for the primary experiment.

Example:

    customer_id | variant
    ------------|---------
    C001        | control
    C002        | treatment
    C003        | control
    C004        | treatment

---

## 14.6 Variant Meaning

Control:

    Top Sellers

Treatment:

    Personalized Content-Based Recommendations

---

## 14.7 SRM Preparation

The assignment generator must preserve an approximately 50/50 split.

Phase 8 will independently test:

    Expected 50/50
          ↓
    Actual Assignment
          ↓
    Chi-Square Goodness-of-Fit
          ↓
    SRM Decision

---

# 15. ENTITY 09 — RECOMMENDATION EVENTS GENERATION

## 15.1 Grain

One row = one recommendation-system interaction.

---

## 15.2 Target Volume

    200,000 – 800,000 events

---

## 15.3 Recommendation Event Types

The dedicated Recommendation Events vocabulary is:

    impression
    click
    conversion

These event types exist exclusively within the Recommendation Events
entity.

They must not be duplicated in the general Events entity.

---

## 15.4 Recommendation Journey

The logical sequence is:

    impression
        ↓
    optional click
        ↓
    optional conversion

A conversion should occur only after an impression and, where the
conversion definition requires click-through behavior, after a click.

---

## 15.5 Recommendation Product

Every recommendation event must reference:

    recommended_product_id

from the public products dataset.

---

## 15.6 Experiment Relationship

For experiment participants:

    experiment_id
    assignment_id

must be populated.

Control participants represent the control recommendation experience.

Treatment participants represent personalized recommendations.

---

## 15.7 Interaction Rates

The generated data must preserve the natural funnel:

    Impressions
        >
    Clicks
        >
    Conversions

The generator must not force all impressions to become clicks or
conversions.

---

# 16. CUSTOMER ACTIVITY RULES

Synthetic customer behavior should support different activity levels.

Conceptual groups:

    Low Activity
    Moderate Activity
    High Activity

This is required so later RFM analysis can identify meaningful
differences in behavior.

The categories are synthetic generation controls and must not be
presented as measured Olist customer segments.

---

# 17. PRODUCT INTERACTION RULES

Products should not be selected completely independently for every
event.

Customer behavior should allow repeated interaction with products.

Examples:

    Customer
       ↓
    View Product A
       ↓
    View Product A again
       ↓
    Add Product A to Cart

This creates meaningful product interaction signals for:

- Product Analytics
- Recommendation Intelligence
- Customer Preferences

---

# 18. PUBLIC ORDER INTEGRATION RULE

Synthetic events may reference public orders.

However:

    Synthetic Generator
            ↓
    must select existing order_id
            ↓
    from processed public orders

It must never create fake public order IDs.

---

# 19. DATE AND TIME RULES

All enterprise timestamps must:

1. Fall within the defined observation period.
2. Use consistent datetime format.
3. Preserve logical ordering.
4. Avoid impossible sequences.
5. Remain compatible with related public transactions.

Examples:

    session_start < event_timestamp < session_end

and:

    campaign_start <= exposure_timestamp <= campaign_end

and:

    experiment_start <= assignment_timestamp <= experiment_end

and:

    login_timestamp <= identity_link_timestamp

---

# 20. REFERENTIAL INTEGRITY RULES

Before integration, the generator must verify:

    events.session_id
            ↓
    sessions.session_id

    events.customer_id
            ↓
    public customers.customer_id

    events.product_id
            ↓
    public products.product_id

    events.order_id
            ↓
    public orders.order_id

    campaign_exposure.campaign_id
            ↓
    marketing_campaigns.campaign_id

    inventory.product_id
            ↓
    public products.product_id

    identity_links.customer_id
            ↓
    public customers.customer_id

    identity_links.anonymous_id
            ↓
    enterprise anonymous identities

    experiment_assignments.experiment_id
            ↓
    experiments.experiment_id

    experiment_assignments.customer_id
            ↓
    public customers.customer_id

    recommendation_events.assignment_id
            ↓
    experiment_assignments.assignment_id

    recommendation_events.experiment_id
            ↓
    experiments.experiment_id

    recommendation_events.recommended_product_id
            ↓
    public products.product_id

---

# 21. GRAIN VALIDATION RULES

The generator must validate every entity according to its declared
grain.

Examples:

### Events

    event_id unique

### Sessions

    session_id unique

### Campaigns

    campaign_id unique

### Exposure

    exposure_id unique

### Inventory

    inventory_observation_id unique

### Identity

    identity_link_id unique

### Experiments

    experiment_id unique

### Assignments

    assignment_id unique

### Recommendation Events

    recommendation_event_id unique

---

# 22. GENERATION DEPENDENCY ORDER

The recommended generation dependency is:

    PUBLIC DATA
        ↓
    REFERENCE DATA LOADING
        ↓
    SESSIONS
        ↓
    EVENTS
        ↓
    SUCCESSFUL LOGIN EVENTS
        ↓
    IDENTITY LINKS
        ↓
    MARKETING CAMPAIGNS
        ↓
    CAMPAIGN EXPOSURE
        ↓
    INVENTORY
        ↓
    EXPERIMENT
        ↓
    EXPERIMENT ASSIGNMENTS
        ↓
    RECOMMENDATION EVENTS
        ↓
    VALIDATION

Identity Links must be derived from successful login events.

Recommendation Events must be generated separately from the general
Events entity.

---

# 23. GENERATION MUST BE REPRODUCIBLE

The Python generators must use a controlled random seed.

Example:

    RANDOM_SEED = 42

The exact seed may be changed during implementation, but it must be
explicitly defined.

The same configuration and seed should reproduce the same synthetic
dataset.

---

# 24. GENERATION CONFIGURATION

Generation parameters should be centralized rather than scattered
throughout multiple scripts.

Configuration should include:

    random_seed
    session_target
    event_target
    campaign_target
    exposure_target
    inventory_target
    identity_link_target
    experiment_target
    assignment_target
    recommendation_event_target

Other behavioral parameters may include:

    device_distribution
    platform_distribution
    event_distribution
    funnel_probabilities
    session_duration_distribution
    experiment_split
    recommendation_interaction_rates

---

# 25. SYNTHETIC DATA MUST NOT MODIFY PUBLIC DATA

Generation scripts must:

    READ
    PUBLIC DATA

and:

    WRITE
    ENTERPRISE DATA

They must never overwrite:

    data/raw/public/

or:

    data/processed/public/

The enterprise data must be stored separately.

---

# 26. ENTERPRISE DATA OUTPUT

Synthetic enterprise data should be written to a dedicated enterprise
data directory.

Target structure:

    data/
    │
    ├── raw/
    │   └── public/
    │
    ├── processed/
    │   └── public/
    │
    └── enterprise/
        ├── events/
        ├── sessions/
        ├── marketing/
        ├── inventory/
        ├── identity/
        ├── experiments/
        └── recommendations/

The exact physical directory structure may be finalized during Python
implementation.

---

# 27. VALIDATION AFTER GENERATION

Every generated entity must pass:

    Completeness
        ↓
    Uniqueness
        ↓
    Referential Integrity
        ↓
    Temporal Integrity
        ↓
    Grain Integrity
        ↓
    Domain Validation
        ↓
    Business Logic Validation

---

# 28. BUSINESS REALISM CHECKS

The generated dataset must support realistic patterns such as:

### Funnel

    Sessions
      >
    Product Views
      >
    Add to Cart
      >
    Checkout
      >
    Purchase

### Recommendation

    Impressions
      >
    Clicks
      >
    Conversions

### Marketing

    Exposures
      >
    Clicks
      >
    Conversions

### Inventory

    Stock
      ↓
    Low Stock
      ↓
    Out of Stock

These relationships are generation objectives.

They are not predetermined analytical findings.

---

# 29. NO FABRICATED BUSINESS FINDINGS

Synthetic generation must not establish predetermined conclusions such
as:

    Treatment always wins
    Campaign X always performs best
    Product X is always the best product
    Mobile always converts better

The generated data should create realistic variation.

Actual analytical findings will be calculated later.

---

# 30. PHASE 7 RECOMMENDATION SUPPORT

The enterprise data must provide the behavioral signals required by
the content-based recommendation engine.

Relevant signals include:

    Product Views
    Add to Cart
    Purchases
    Product Categories
    Recommendation Interactions

The recommendation model itself is not generated in Phase 2.

Phase 2 generates the supporting enterprise behavioral data.

---

# 31. PHASE 8 EXPERIMENTATION SUPPORT

The generated data must support:

    Experiment
        ↓
    Assignment
        ↓
    Control / Treatment
        ↓
    Recommendation Exposure
        ↓
    Customer Behavior
        ↓
    Purchase Conversion

The primary business outcome remains:

    Purchase Conversion Rate

Statistical analysis belongs to Phase 8.

---

# 32. PHASE 5 CUSTOMER JOURNEY SUPPORT

The event/session design must support:

- Funnel analysis
- Session analysis
- Drop-off analysis
- Journey mapping
- Cohort analysis
- Retention analysis

The enterprise data must therefore preserve:

    customer/session identity
    event timestamps
    event sequence
    device
    platform
    product interaction
    conversion behavior

---

# 33. PHASE 6 CUSTOMER ANALYTICS SUPPORT

The generated behavior must support later calculation of:

    Recency
    Frequency
    Monetary Value
    Historical CLV
    Customer Segmentation

The generator must not directly assign:

    Champion
    At Risk
    Lost

Those are analytical outputs calculated later from observed behavior.

---

# 34. GENERATION COMPLETION GATE

Synthetic data generation is considered complete only when:

    All entities generated
            ↓
    All primary keys valid
            ↓
    All foreign keys valid
            ↓
    All grains valid
            ↓
    All timestamps valid
            ↓
    All business rules valid
            ↓
    Enterprise data validated

Only then can the project move toward hybrid integration.

---

# 35. LOCKED DESIGN DECISIONS

The following decisions are inherited from the locked Enterprise Entity
Design.

## Events

General behavioral Events contain only:

    session_start
    search
    product_view
    add_to_cart
    remove_from_cart
    checkout_start
    login
    purchase_interaction

The following are explicitly excluded from Events:

    recommendation_impression
    recommendation_click

---

## Recommendation Events

Recommendation interactions are represented exclusively through:

    impression
    click
    conversion

---

## Experiments

ORGEE v1.0 requires one primary experiment:

    Recommendation A/B Test

Multiple experiments are not required.

---

## Identity

Identity Links are derived exclusively from successful login events.

The relationship is:

    Anonymous Identity
          ↓
    Session Behavior
          ↓
    Successful Login
          ↓
    Identity Link
          ↓
    Customer Identity

No arbitrary or probabilistic identity matching is used.

---

# 🔒 FINAL STATUS

**ORGEE Enterprise Generation Rules v1.0 — LOCKED**

The generation rules are now aligned with the locked Enterprise Entity
Design.

The next step is:

    GENERATION RULES
          ↓
    GENERATION CONFIGURATION
          ↓
    PYTHON GENERATORS
          ↓
    SYNTHETIC DATA
          ↓
    VALIDATION
          ↓
    HYBRID INTEGRATION