# ORGEE — Enterprise Entity Design

## Omnichannel Retail & Growth Experimentation Engine

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Project Code:** ORGEE  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Enterprise Entity Design  
**Status:** DRAFT — ENTITY DESIGN IN PROGRESS

---

# 1. Purpose

This document translates the approved ORGEE Enterprise Data Requirements
into a concrete enterprise entity architecture.

The purpose of this document is to define the enterprise-generated data
before any synthetic data generation begins.

For each enterprise entity, the design defines:

- Business purpose
- Grain
- Primary identifier
- Foreign keys
- Columns
- Relationships
- Expected row volume
- Generation logic
- Validation requirements
- Analytical value

Synthetic data generation must not begin until the entity architecture
has been reviewed and approved.

---

# 2. Design Principle

The enterprise data layer follows:

    BUSINESS REQUIREMENT
            ↓
    DATA REQUIREMENT
            ↓
    ENTITY
            ↓
    GRAIN
            ↓
    IDENTIFIERS
            ↓
    RELATIONSHIPS
            ↓
    COLUMNS
            ↓
    ROW VOLUME
            ↓
    GENERATION LOGIC
            ↓
    VALIDATION
            ↓
    SYNTHETIC DATA

No entity will be created solely to increase technical complexity.

Every entity must have a clear business purpose and analytical value.

---

# 3. Enterprise Data Architecture

The enterprise-generated layer will provide the behavioral and
business context missing from the public Olist transactional data.

The initial candidate enterprise entities are:

1. Events
2. Sessions
3. Marketing Campaigns
4. Campaign Exposure
5. Inventory
6. Identity Links
7. Experiments
8. Experiment Assignments
9. Recommendation Events

These entities will be evaluated for:

- Business necessity
- Grain
- Relationship requirements
- Redundancy
- Analytical value
- Generation feasibility
- Validation requirements

The final entity architecture will be locked before synthetic
generation begins.

---

# 4. Public Data Integration Foundation

The enterprise layer will integrate with the validated public
Olist foundation.

Primary public identifiers include:

- customer_id
- product_id
- order_id
- seller_id

Enterprise identifiers include:

- anonymous_id
- session_id
- campaign_id
- exposure_id
- identity_link_id
- experiment_id
- assignment_id
- recommendation_event_id
- event_id
- inventory_observation_id

Public identifiers remain authoritative.

The enterprise layer must not overwrite public identifiers.

---

# 5. ENTITY 01 — EVENTS

## 5.1 Business Purpose

The Events entity captures customer behavioral activity across the
digital customer journey.

It provides the behavioral foundation required for:

- Customer Journey Analytics
- Funnel Analytics
- Session Analytics
- Product Analytics
- Customer 360
- Cross-Device Identity
- Recommendation Intelligence
- Experimentation

Examples of behavioral events include:

- Session Start
- Search
- Product View
- Add to Cart
- Remove from Cart
- Checkout Start
- Login
- Recommendation Impression
- Recommendation Click
- Purchase Interaction

Not every session must contain every event type.

---

## 5.2 Grain

**One row represents one behavioral event.**

Each event is an individual customer or anonymous-user interaction
occurring at a specific point in time.

Example:

    session_id = S001
    event_id = E001
    event_type = product_view
    event_timestamp = 2018-01-15 10:23:41

This represents one product-view event.

---

## 5.3 Primary Key

    event_id

Requirement:

- event_id must be unique
- event_id must identify exactly one behavioral event

---

## 5.4 Foreign Keys / Relationships

Potential relationships:

    events.session_id
            ↓
    sessions.session_id

    events.customer_id
            ↓
    customers.customer_id

    events.product_id
            ↓
    products.product_id

    events.order_id
            ↓
    orders.order_id

Additional enterprise relationships may include:

    events.anonymous_id
            ↓
    identity_links.anonymous_id

    events.experiment_id
            ↓
    experiments.experiment_id

    events.assignment_id
            ↓
    experiment_assignments.assignment_id

Foreign keys are populated according to event type.

For example:

- Product View → product_id expected
- Add to Cart → product_id expected
- Checkout → session/customer context expected
- Purchase interaction → order_id may be associated where applicable
- Login → anonymous_id and customer_id may both be present

---

## 5.5 Columns

| Column | Type | Description |
|---|---|---|
| event_id | string | Unique behavioral event identifier |
| event_timestamp | datetime | Timestamp when the event occurred |
| event_type | string | Type of customer behavioral event |
| session_id | string | Associated session |
| anonymous_id | string | Anonymous visitor identifier where applicable |
| customer_id | string | Public customer identifier where known |
| product_id | string | Associated product where applicable |
| order_id | string | Associated order where applicable |
| device_type | string | Device used for the event |
| platform | string | Web, mobile, or desktop platform |
| experiment_id | string | Associated experiment where applicable |
| assignment_id | string | Associated experiment assignment where applicable |

---

## 5.6 Event Types

The minimum event vocabulary is:

    session_start
    search
    product_view
    add_to_cart
    remove_from_cart
    checkout_start
    login
    recommendation_impression
    recommendation_click
    purchase_interaction

The event vocabulary must remain controlled.

New event types should only be introduced when required by a defined
business capability.

---

## 5.7 Device Types

The enterprise event layer must support:

    mobile
    desktop
    tablet

---

## 5.8 Platforms

The enterprise event layer must support:

    web
    mobile_app
    desktop

The generated distribution should represent realistic omnichannel
behavior.

---

## 5.9 Expected Row Volume

Events should be substantially larger than the public
transactional tables because multiple events can occur within a
single session.

Initial target:

    Approximately 1,000,000 – 3,000,000 events

The final volume will be selected based on:

- Number of sessions
- Average events per session
- Journey design
- Generation performance
- Analytical requirements

The volume must remain computationally practical.

---

## 5.10 Generation Logic

Events will be generated from realistic customer journey behavior.

Conceptual journey:

    SESSION START
          ↓
    SEARCH
          ↓
    PRODUCT VIEW
          ↓
    ADD TO CART
          ↓
    CHECKOUT START
          ↓
    PURCHASE INTERACTION

However, realistic drop-offs must exist.

Examples:

    Session Start
          ↓
    Product View
          ↓
    EXIT

or:

    Session Start
          ↓
    Search
          ↓
    Product View
          ↓
    Add to Cart
          ↓
    EXIT

or:

    Session Start
          ↓
    Product View
          ↓
    Add to Cart
          ↓
    Checkout
          ↓
    Purchase Interaction

The generated event sequence must preserve logical timestamp ordering
within a session.

---

## 5.11 Validation Rules

### Uniqueness

event_id must be unique.

### Referential Integrity

session_id must reference a valid session.

customer_id, product_id, order_id, experiment_id, and assignment_id
must reference valid entities when populated.

### Temporal Integrity

Events belonging to a session must occur within the session period.

### Grain Integrity

One row must represent exactly one behavioral event.

### Business Logic

Event sequences must represent realistic customer journeys.

---

## 5.12 Analytical Value

Events enable:

- Funnel analysis
- Customer journey analysis
- Drop-off analysis
- Product interaction analysis
- Session behavior analysis
- Recommendation interaction analysis
- Experiment behavior analysis
- Customer 360 behavioral signals

---

# 6. ENTITY 02 — SESSIONS

## 6.1 Business Purpose

The Sessions entity represents a customer's or anonymous visitor's
browsing session.

It provides the session-level foundation for:

- Session Analytics
- Funnel Analytics
- Customer Journey Analytics
- Device Analysis
- Conversion Analysis

---

## 6.2 Grain

**One row represents one browsing session.**

A session may contain multiple behavioral events.

    SESSION
       |
       +-- EVENT
       +-- EVENT
       +-- EVENT
       +-- EVENT

---

## 6.3 Primary Key

    session_id

Each session_id must be unique.

---

## 6.4 Foreign Keys / Relationships

    sessions.customer_id
            ↓
    customers.customer_id

    sessions.anonymous_id
            ↓
    identity_links.anonymous_id

    sessions.session_id
            ↑
    events.session_id

---

## 6.5 Columns

| Column | Type | Description |
|---|---|---|
| session_id | string | Unique session identifier |
| anonymous_id | string | Anonymous visitor identifier |
| customer_id | string | Known customer identifier where available |
| session_start | datetime | Session start timestamp |
| session_end | datetime | Session end timestamp |
| device_type | string | Device used during session |
| platform | string | Platform used during session |
| traffic_source | string | Source through which the session originated |
| landing_page_type | string | Initial page/context of the session |
| session_converted | boolean | Whether the session resulted in purchase interaction |
| event_count | integer | Number of events in the session |

---

## 6.6 Expected Row Volume

Initial target:

    Approximately 200,000 – 500,000 sessions

The final volume will be determined after event-volume design.

The relationship should support multiple events per session.

---

## 6.7 Generation Logic

Sessions will be generated across:

- Web
- Mobile app
- Desktop

Both anonymous and identified sessions must exist.

Some sessions may be anonymous.

Some sessions may contain a login event and become associated with a
known customer.

Session durations must be realistic.

The session must satisfy:

    session_start < session_end

---

## 6.8 Validation Rules

- session_id unique
- session_start < session_end
- event timestamps fall within session boundaries
- customer_id references valid public customers when populated
- anonymous_id is present for anonymous sessions
- event_count matches associated events

---

## 6.9 Analytical Value

Sessions support:

- Sessions per customer
- Average session duration
- Events per session
- Conversion by session
- Device performance
- Platform performance
- Funnel analysis
- Journey analysis

---

# 7. ENTITY 03 — MARKETING CAMPAIGNS

## 7.1 Business Purpose

The Marketing Campaigns entity represents marketing initiatives used
for customer acquisition, engagement, and conversion analysis.

---

## 7.2 Grain

**One row represents one marketing campaign.**

---

## 7.3 Primary Key

    campaign_id

---

## 7.4 Columns

| Column | Type | Description |
|---|---|---|
| campaign_id | string | Unique campaign identifier |
| campaign_name | string | Campaign name |
| channel | string | Marketing channel |
| campaign_type | string | Campaign classification |
| objective | string | Campaign objective |
| start_date | date | Campaign start date |
| end_date | date | Campaign end date |
| budget | decimal | Campaign budget |
| target_segment | string | Intended customer segment |

---

## 7.5 Marketing Channels

Initial supported channels:

    email
    social
    search
    display
    push
    affiliate

---

## 7.6 Campaign Objectives

Examples:

    acquisition
    conversion
    retention
    re-engagement
    promotion

---

## 7.7 Expected Row Volume

Initial target:

    Approximately 20 – 50 campaigns

The final number will be selected according to the generated
marketing-analysis requirements.

---

## 7.8 Generation Logic

Campaigns must have valid:

    start_date <= end_date

Campaign periods must overlap the behavioral observation period where
campaign exposure analysis is required.

---

## 7.9 Validation Rules

- campaign_id unique
- valid campaign dates
- supported channel values
- valid objective values
- budget non-negative

---

## 7.10 Analytical Value

Campaign data supports:

- Campaign performance
- Channel performance
- Customer acquisition
- Conversion analysis
- Marketing response analysis

---

# 8. ENTITY 04 — CAMPAIGN EXPOSURE

## 8.1 Business Purpose

Campaign Exposure records when a customer or anonymous visitor is
exposed to a marketing campaign.

It connects marketing activity with customer behavior.

---

## 8.2 Grain

**One row represents one campaign exposure event.**

---

## 8.3 Primary Key

    exposure_id

---

## 8.4 Foreign Keys

    campaign_id
            ↓
    marketing_campaigns.campaign_id

    customer_id
            ↓
    customers.customer_id

    anonymous_id
            ↓
    identity_links.anonymous_id

---

## 8.5 Columns

| Column | Type | Description |
|---|---|---|
| exposure_id | string | Unique exposure identifier |
| campaign_id | string | Associated campaign |
| customer_id | string | Customer exposed where known |
| anonymous_id | string | Anonymous identity where applicable |
| exposure_timestamp | datetime | Time of exposure |
| channel | string | Exposure channel |
| exposure_type | string | Type of exposure |
| clicked | boolean | Whether exposure resulted in click |
| converted | boolean | Whether associated conversion occurred |

---

## 8.6 Exposure Types

Examples:

    impression
    email_open
    notification
    ad_view

---

## 8.7 Expected Row Volume

Initial target:

    Approximately 300,000 – 1,000,000 exposure records

The final volume will depend on:

- Campaign count
- Customer population
- Exposure frequency
- Analytical requirements

---

## 8.8 Generation Logic

Exposure timestamps must fall within the corresponding campaign
period.

A campaign exposure may be:

    exposure
       ↓
    click
       ↓
    session
       ↓
    purchase

Not every exposure must result in a click or conversion.

---

## 8.9 Validation Rules

- exposure_id unique
- campaign_id valid
- exposure timestamp within campaign period
- customer_id valid when populated
- anonymous_id valid when populated
- conversion logic must be temporally valid

---

## 8.10 Analytical Value

Supports:

- Campaign reach
- Channel performance
- Exposure-to-click rate
- Exposure-to-conversion analysis
- Customer response analysis

---

# 9. ENTITY 05 — INVENTORY

## 9.1 Business Purpose

The Inventory entity represents product availability and stock
conditions over time.

It supports inventory analytics and analysis of relationships between
availability and customer behavior.

---

## 9.2 Grain

**One row represents one inventory observation for one product,**
**location, and timestamp.**

---

## 9.3 Primary Key

    inventory_observation_id

---

## 9.4 Foreign Keys

    product_id
            ↓
    products.product_id

---

## 9.5 Columns

| Column | Type | Description |
|---|---|---|
| inventory_observation_id | string | Unique inventory observation |
| product_id | string | Public product identifier |
| inventory_location_id | string | Inventory location |
| observation_timestamp | datetime | Inventory observation time |
| available_quantity | integer | Available stock |
| reserved_quantity | integer | Reserved stock |
| inventory_status | string | Inventory availability state |

---

## 9.6 Inventory Status

Examples:

    in_stock
    low_stock
    out_of_stock

---

## 9.7 Expected Row Volume

Initial target:

    Approximately 500,000 – 1,500,000 inventory observations

The final volume will depend on:

- Product population
- Number of inventory locations
- Observation frequency

---

## 9.8 Generation Logic

Inventory observations must:

- reference valid products
- contain non-negative quantities
- follow chronological order
- allow products to move between inventory states

Example:

    100 units
       ↓
    65 units
       ↓
    20 units
       ↓
    0 units
       ↓
    out_of_stock

---

## 9.9 Validation Rules

- inventory_observation_id unique
- product_id valid
- quantities non-negative
- inventory timestamp valid
- inventory status consistent with quantity

---

## 9.10 Analytical Value

Supports:

- Stock availability
- Out-of-stock analysis
- Product availability
- Inventory health
- Relationship between stock and customer behavior

---

# 10. ENTITY 06 — IDENTITY LINKS

## 10.1 Business Purpose

Identity Links provide the controlled cross-device identity mechanism
required by ORGEE.

The design uses a login-event-based identity stitching mechanism.

Concept:

    Anonymous Mobile User
            ↓
    Product View
            ↓
    Add to Cart
            ↓
    Login Event
            ↓
    customer_id identified
            ↓
    Desktop Session
            ↓
    Purchase

This demonstrates a realistic omnichannel identity concept without
claiming to implement a production-grade identity graph.

---

## 10.2 Grain

**One row represents one identity-link relationship between an**
**anonymous identity and a known customer identity.**

---

## 10.3 Primary Key

    identity_link_id

---

## 10.4 Columns

| Column | Type | Description |
|---|---|---|
| identity_link_id | string | Unique identity-link identifier |
| anonymous_id | string | Anonymous visitor identifier |
| customer_id | string | Public customer identifier |
| link_timestamp | datetime | Timestamp when identity was linked |
| link_method | string | Mechanism that established the link |
| source_session_id | string | Session containing the linking event |

---

## 10.5 Link Method

The primary method is:

    login_event

No probabilistic identity matching is required.

---

## 10.6 Expected Row Volume

Initial target:

    Approximately 20,000 – 60,000 identity links

The final volume will depend on the number of anonymous users who
perform login events.

---

## 10.7 Generation Logic

An identity link can only be created when a login event establishes
the relationship.

The sequence must satisfy:

    anonymous activity
            ↓
    login event
            ↓
    identity link
            ↓
    known customer activity

The same anonymous identity should not be arbitrarily linked to
multiple customers.

---

## 10.8 Validation Rules

- identity_link_id unique
- customer_id valid
- anonymous_id valid
- link timestamp associated with a valid login event
- source_session_id valid
- one anonymous identity must not be linked to conflicting customers

---

## 10.9 Analytical Value

Supports:

- Cross-device behavior
- Anonymous-to-known conversion
- Customer 360
- Omnichannel journey analysis
- Pre-login and post-login behavior

---

# 11. ENTITY 07 — EXPERIMENTS

## 11.1 Business Purpose

The Experiments entity defines controlled business/product
experiments.

The primary ORGEE experiment will support evaluation of the
recommendation engine.

---

## 11.2 Grain

**One row represents one experiment.**

---

## 11.3 Primary Key

    experiment_id

---

## 11.4 Columns

| Column | Type | Description |
|---|---|---|
| experiment_id | string | Unique experiment identifier |
| experiment_name | string | Experiment name |
| objective | string | Experiment objective |
| hypothesis | string | Experiment hypothesis |
| start_date | date | Experiment start |
| end_date | date | Experiment end |
| primary_metric | string | Primary success metric |
| status | string | Experiment status |

---

## 11.5 Primary Experiment

The primary ORGEE experimentation use case is:

    Recommendation A/B Test

Primary metric:

    Purchase Conversion Rate

Secondary metrics:

    Recommendation CTR
    Average Order Value
    Revenue per User
    Purchase Rate

---

## 11.6 Expected Row Volume

Initial target:

    Approximately 1 – 5 experiments

The project does not require multiple experiments merely for
technical complexity.

---

## 11.7 Validation Rules

- experiment_id unique
- valid experiment dates
- primary metric defined
- experiment objective defined
- status valid

---

# 12. ENTITY 08 — EXPERIMENT ASSIGNMENTS

## 12.1 Business Purpose

Experiment Assignments record which experimental variant an
experimental unit receives.

They provide the foundation for:

- Control vs Treatment analysis
- A/B testing
- SRM validation
- Statistical analysis

---

## 12.2 Grain

**One row represents one assignment of one experimental unit to one**
**experiment variant.**

---

## 12.3 Primary Key

    assignment_id

---

## 12.4 Foreign Keys

    experiment_id
            ↓
    experiments.experiment_id

Where applicable:

    customer_id
            ↓
    customers.customer_id

    session_id
            ↓
    sessions.session_id

---

## 12.5 Columns

| Column | Type | Description |
|---|---|---|
| assignment_id | string | Unique assignment identifier |
| experiment_id | string | Associated experiment |
| customer_id | string | Customer experimental unit |
| session_id | string | Associated session where applicable |
| variant | string | Control or treatment |
| assignment_timestamp | datetime | Assignment timestamp |

---

## 12.6 Variants

The primary experiment supports:

    control
    treatment

Conceptually:

    CONTROL
        ↓
    Top Sellers

    TREATMENT
        ↓
    Personalized Recommendations

---

## 12.7 Expected Row Volume

Initial target:

    Approximately 50,000 – 100,000 assignments

The final volume will depend on the selected experimental population.

---

## 12.8 Generation Logic

The primary experiment should approximate:

    50% CONTROL
    50% TREATMENT

The generated assignment data must support the later SRM check.

The SRM validation itself belongs to the experimentation analysis
stage and will use a Chi-Square goodness-of-fit test.

---

## 12.9 Validation Rules

- assignment_id unique
- experiment_id valid
- customer_id valid when used
- session_id valid when used
- variant must be valid
- assignment timestamp must fall within experiment period
- experimental units must not receive conflicting simultaneous
  assignments for the same experiment

---

## 12.10 Analytical Value

Supports:

- A/B testing
- SRM validation
- Conversion comparison
- Treatment effect analysis
- Statistical significance
- Confidence intervals
- Effect size
- Experiment decision

---

# 13. ENTITY 09 — RECOMMENDATION EVENTS

## 13.1 Business Purpose

Recommendation Events capture interactions with the ORGEE
recommendation system.

The recommendation system is intentionally limited to one focused
ML capability:

    Content-Based Recommendation Engine

---

## 13.2 Grain

**One row represents one recommendation-system interaction.**

---

## 13.3 Primary Key

    recommendation_event_id

---

## 13.4 Foreign Keys

    customer_id
            ↓
    customers.customer_id

    session_id
            ↓
    sessions.session_id

    product_id
            ↓
    products.product_id

    experiment_id
            ↓
    experiments.experiment_id

    assignment_id
            ↓
    experiment_assignments.assignment_id

---

## 13.5 Columns

| Column | Type | Description |
|---|---|---|
| recommendation_event_id | string | Unique recommendation interaction |
| event_timestamp | datetime | Recommendation interaction timestamp |
| customer_id | string | Customer receiving recommendation where known |
| anonymous_id | string | Anonymous identity where applicable |
| session_id | string | Associated session |
| recommended_product_id | string | Product recommended |
| recommendation_event_type | string | Impression, click, or conversion |
| experiment_id | string | Associated experiment where applicable |
| assignment_id | string | Associated experiment assignment where applicable |
| recommendation_position | integer | Position of recommended product |

---

## 13.6 Recommendation Event Types

Minimum event types:

    impression
    click
    conversion

---

## 13.7 Expected Row Volume

Initial target:

    Approximately 200,000 – 800,000 recommendation events

The final volume will depend on:

- Number of recommendation sessions
- Recommendations per session
- Experiment population
- Interaction rates

---

## 13.8 Generation Logic

Recommendation events must represent the recommendation journey:

    Recommendation Impression
            ↓
           Click
            ↓
     Product Interaction
            ↓
        Conversion

Not every impression should produce a click.

Not every click should produce a conversion.

The recommendation event must reference a valid product.

---

## 13.9 Validation Rules

- recommendation_event_id unique
- recommended_product_id valid
- session_id valid
- customer_id valid when populated
- experiment_id valid when populated
- assignment_id valid when populated
- event timestamps must follow logical order
- conversion cannot occur before impression

---

## 13.10 Analytical Value

Supports:

- Recommendation CTR
- Recommendation conversion
- Personalized recommendation evaluation
- Recommendation business impact
- A/B experiment analysis

---

# 14. CROSS-ENTITY RELATIONSHIP MODEL

The enterprise architecture follows these major relationships:

    CUSTOMER
       |
       +----------------------+
       |                      |
       ↓                      ↓
    SESSIONS              IDENTITY LINKS
       |                      |
       ↓                      ↓
    EVENTS                ANONYMOUS ID
       |
       +----------+
       |          |
       ↓          ↓
    PRODUCT     ORDER

Marketing:

    MARKETING CAMPAIGN
            ↓
    CAMPAIGN EXPOSURE
            ↓
    CUSTOMER / ANONYMOUS ID
            ↓
    SESSION
            ↓
    EVENT
            ↓
    CONVERSION

Experimentation:

    EXPERIMENT
        ↓
    EXPERIMENT ASSIGNMENT
        ↓
    SESSION / CUSTOMER
        ↓
    RECOMMENDATION EVENT
        ↓
    BEHAVIOR
        ↓
    PURCHASE

Inventory:

    PRODUCT
       ↓
    INVENTORY OBSERVATION
       ↓
    AVAILABILITY
       ↓
    CUSTOMER BEHAVIOR

---

# 15. ENTITY GRAIN SUMMARY

| Entity | Grain |
|---|---|
| Events | One row per behavioral event |
| Sessions | One row per browsing session |
| Marketing Campaigns | One row per marketing campaign |
| Campaign Exposure | One row per campaign exposure |
| Inventory | One row per product-location-time observation |
| Identity Links | One row per anonymous-to-customer identity link |
| Experiments | One row per experiment |
| Experiment Assignments | One row per experimental-unit assignment |
| Recommendation Events | One row per recommendation interaction |

---

# 16. PRIMARY KEY SUMMARY

| Entity | Primary Key |
|---|---|
| Events | event_id |
| Sessions | session_id |
| Marketing Campaigns | campaign_id |
| Campaign Exposure | exposure_id |
| Inventory | inventory_observation_id |
| Identity Links | identity_link_id |
| Experiments | experiment_id |
| Experiment Assignments | assignment_id |
| Recommendation Events | recommendation_event_id |

---

# 17. PUBLIC DATA RELATIONSHIPS

The enterprise layer integrates with the public foundation through
controlled identifiers.

Primary relationships:

    customers.customer_id
            ↑
    events.customer_id
    sessions.customer_id
    campaign_exposure.customer_id
    identity_links.customer_id
    experiment_assignments.customer_id
    recommendation_events.customer_id

    products.product_id
            ↑
    events.product_id
    inventory.product_id
    recommendation_events.recommended_product_id

    orders.order_id
            ↑
    events.order_id

Public identifiers remain unchanged.

---

# 18. ENTERPRISE IDENTIFIER PRINCIPLES

All enterprise-generated identifiers must be unique within their
defined entity.

Examples:

    EVT-XXXXXXXX
    SES-XXXXXXXX
    CMP-XXXXXXXX
    EXP-XXXXXXXX
    IDL-XXXXXXXX
    ASN-XXXXXXXX
    REC-XXXXXXXX
    INV-XXXXXXXX

The exact identifier implementation will be finalized during the
generation-design stage.

Identifiers must not collide with public identifiers.

---

# 19. TEMPORAL DESIGN PRINCIPLES

Enterprise-generated timestamps must respect logical business order.

Examples:

    Session Start
          ↓
    Event
          ↓
    Login
          ↓
    Identity Link
          ↓
    Subsequent Known-Customer Activity

For recommendation interactions:

    Impression
          ↓
    Click
          ↓
    Conversion

For campaigns:

    Campaign Start
          ↓
    Exposure
          ↓
    Behavior
          ↓
    Conversion

For experiments:

    Experiment Start
          ↓
    Assignment
          ↓
    Recommendation Exposure
          ↓
    Behavior
          ↓
    Purchase Outcome
          ↓
    Experiment End

---

# 20. DATA QUALITY GATES

Every enterprise entity must pass the following gates before
integration.

## 20.1 Completeness

Required fields must be populated.

## 20.2 Uniqueness

Primary keys must be unique.

## 20.3 Referential Integrity

Foreign keys must reference valid parent records where applicable.

## 20.4 Temporal Integrity

Dates and timestamps must follow logical business ordering.

## 20.5 Grain Integrity

The generated table must preserve its declared grain.

## 20.6 Domain Integrity

Categorical fields must use controlled values.

## 20.7 Business Logic

Synthetic behavior must represent realistic retail behavior.

---

# 21. EXPECTED INITIAL ROW VOLUME SUMMARY

| Entity | Initial Target |
|---|---|
| Events | 1,000,000 – 3,000,000 |
| Sessions | 200,000 – 500,000 |
| Marketing Campaigns | 20 – 50 |
| Campaign Exposure | 300,000 – 1,000,000 |
| Inventory | 500,000 – 1,500,000 |
| Identity Links | 20,000 – 60,000 |
| Experiments | 1 – 5 |
| Experiment Assignments | 50,000 – 100,000 |
| Recommendation Events | 200,000 – 800,000 |

These are initial engineering targets, not final generated row counts.

Final volumes will be determined during generation design based on
relationships, analytical requirements, and computational practicality.

---

# 22. GENERATION ORDER

The synthetic enterprise data will be generated in dependency order.

    PUBLIC DATA
        ↓
    CUSTOMER / PRODUCT REFERENCE
        ↓
    SESSIONS
        ↓
    IDENTITY LINKS
        ↓
    EVENTS
        ↓
    MARKETING CAMPAIGNS
        ↓
    CAMPAIGN EXPOSURE
        ↓
    INVENTORY
        ↓
    EXPERIMENTS
        ↓
    EXPERIMENT ASSIGNMENTS
        ↓
    RECOMMENDATION EVENTS
        ↓
    CROSS-ENTITY VALIDATION
        ↓
    HYBRID INTEGRATION

The exact Python execution order may be refined during generator
implementation without changing the entity architecture.

---

# 23. CUSTOMER 360 RELATIONSHIP

Customer 360 is not a separate generated entity at this stage.

It emerges from the integration of:

    CUSTOMERS
       +
    ORDERS
       +
    EVENTS
       +
    SESSIONS
       +
    REVIEWS
       +
    MARKETING
       +
    IDENTITY
            ↓
    CUSTOMER 360

Customer 360 will be constructed later through the analytical and
warehouse layers.

---

# 24. RECOMMENDATION RELATIONSHIP

The recommendation layer connects:

    CUSTOMER / SESSION
            ↓
    CUSTOMER BEHAVIOR
            ↓
    PRODUCT PREFERENCES
            ↓
    CONTENT-BASED RECOMMENDATION
            ↓
    RECOMMENDATION EVENT
            ↓
    CLICK / CONVERSION

The recommendation engine itself belongs to Phase 7.

Phase 2 only creates the enterprise data required to support that
capability.

---

# 25. EXPERIMENTATION RELATIONSHIP

The enterprise data must support:

    EXPERIMENT
         ↓
    ASSIGNMENT
         ↓
    CONTROL / TREATMENT
         ↓
    RECOMMENDATION EXPOSURE
         ↓
    CUSTOMER BEHAVIOR
         ↓
    PURCHASE CONVERSION

The primary experiment metric remains:

    Purchase Conversion Rate

The statistical analysis will occur later in Phase 8.

---

# 26. SCOPE CONTROL

The following are intentionally excluded from the Phase 2 enterprise
data design:

- Kafka
- Spark Streaming
- FastAPI
- Docker
- Kubernetes
- Cloud deployment
- Multiple ML models
- Deep learning
- SHAP
- AI decision assistant
- Production-grade identity graph
- Additional unnecessary enterprise entities

The enterprise layer exists to satisfy the locked ORGEE v1.0 business
requirements.

---

# 27. DESIGN STATUS

Current status:

**ENTITY ARCHITECTURE DRAFTED — PENDING VALIDATION AND APPROVAL**

No synthetic data has been generated from this design yet.

No SQL warehouse has been created from this design yet.

No Customer 360 table has been created.

No recommendation model has been created.

No experimentation analysis has been performed.

---

# 28. NEXT STEP

After this entity design is reviewed, the next Phase 2 activity is:

    ENTITY DESIGN
          ↓
    RELATIONSHIP VALIDATION
          ↓
    GRAIN VALIDATION
          ↓
    COLUMN / DATA TYPE FINALIZATION
          ↓
    ROW VOLUME FINALIZATION
          ↓
    GENERATION RULES
          ↓
    PYTHON GENERATORS
          ↓
    SYNTHETIC DATA
          ↓
    DATA QUALITY VALIDATION
          ↓
    HYBRID INTEGRATION

Synthetic data generation must not begin before the entity design is
approved.

---

# FINAL PRINCIPLE

    DESIGN FIRST.

    LOCK THE GRAIN.

    LOCK THE RELATIONSHIPS.

    LOCK THE COLUMNS.

    DEFINE THE GENERATION LOGIC.

    THEN GENERATE.

    THEN VALIDATE.

    THEN INTEGRATE.