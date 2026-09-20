# ORGEE — Enterprise Data Requirements

## Omnichannel Retail & Growth Experimentation Engine

**Project:** Omnichannel Retail & Growth Experimentation Engine  
**Project Code:** ORGEE  
**Version:** 1.0  
**Phase:** Phase 2 — Hybrid Data Engineering  
**Document:** Enterprise Data Requirements  
**Status:** LOCKED

---

# 1. Purpose

The public Olist datasets provide the transactional and product
foundation of ORGEE.

However, the public dataset does not contain the complete behavioral
and enterprise data required for the ORGEE analytical objectives.

Therefore, ORGEE requires a separate enterprise-generated data layer.

The enterprise layer will provide the behavioral and business context
required for:

- Customer Journey Analytics
- Session Analytics
- Funnel Analytics
- Customer 360
- Cross-Device Identity
- Marketing Analytics
- Recommendation Intelligence
- Experimentation
- Inventory Analytics
- Executive Decision Support

---

# 2. Hybrid Data Principle

ORGEE will contain two controlled data sources.

```text
PUBLIC DATA
    |
    |-- Orders
    |-- Order Items
    |-- Products
    |-- Customers
    |-- Sellers
    |-- Payments
    |-- Reviews
    |-- Geolocation
    |-- Category Translation
    |
    +----------------------+
                           |
                           ↓
                    DATA INTEGRATION
                           ↑
                           |
    +----------------------+
    |
ENTERPRISE-GENERATED DATA
    |
    |-- Behavioral Data
    |-- Session Data
    |-- Marketing Data
    |-- Inventory Data
    |-- Identity Data
    |-- Experiment Data
    |-- Recommendation Data
```

The two layers must remain independently valid before integration.

---

# 3. Enterprise Data Requirements

The enterprise layer must provide data for the following business
capabilities.

| Business Capability | Required Enterprise Data |
|---|---|
| Customer Journey | Events, Sessions |
| Funnel Analytics | Events |
| Customer 360 | Events, Sessions, Marketing, Identity |
| Cross-Device Identity | Anonymous IDs, Login Events, Identity Links |
| Marketing Analytics | Campaigns, Campaign Exposure |
| Recommendation Intelligence | Recommendation Events |
| Experimentation | Experiments, Assignments, Outcomes |
| Inventory Analytics | Inventory Snapshots / Observations |
| Product Analytics | Behavioral Product Events |
| Executive Analytics | Integrated enterprise signals |

---

# 4. Entity Design Principle

Every enterprise entity must have:

- Clearly defined grain
- Primary identifier
- Foreign-key relationships where applicable
- Business meaning
- Generation logic
- Validation rules
- Expected row volume
- Relationship to public data

No entity should be created merely to increase technical complexity.

The guiding rule is:

```text
BUSINESS REQUIREMENT
        ↓
DATA REQUIREMENT
        ↓
ENTITY
        ↓
GRAIN
        ↓
GENERATION
        ↓
ANALYTICAL VALUE
```

---

# 5. Enterprise Entities

The following entities are the approved enterprise entities for ORGEE
Phase 2.

These entities were finalized through the Enterprise Entity Design and
subsequently translated into the Enterprise Generation Rules and
Enterprise Generation Configuration.

The approved enterprise entities are:

1. Events
2. Sessions
3. Marketing Campaigns
4. Campaign Exposure
5. Inventory
6. Identity Links
7. Experiments
8. Experiment Assignments
9. Recommendation Events

---

## 5.1 Events

Purpose:

Capture customer behavioral activity across the digital journey.

Examples include:

- Product view
- Search
- Add to cart
- Remove from cart
- Checkout start
- Purchase interaction
- Login

Recommendation-system interactions are represented separately through
the Recommendation Events entity.

Grain:

One row per behavioral event.

---

## 5.2 Sessions

Purpose:

Represent a customer's browsing/session context.

Examples:

- Web session
- Mobile session
- Session start
- Session end
- Device/platform context

Grain:

One row per session.

---

## 5.3 Marketing Campaigns

Purpose:

Represent marketing initiatives used for customer acquisition,
engagement, and conversion analysis.

Examples:

- Campaign
- Channel
- Campaign period
- Campaign objective

Grain:

One row per campaign.

---

## 5.4 Campaign Exposure

Purpose:

Represent customer exposure to marketing campaigns.

Examples:

- Customer exposed to campaign
- Exposure channel
- Exposure timestamp
- Conversion relationship

Grain:

One row per campaign exposure.

---

## 5.5 Inventory

Purpose:

Represent product inventory availability and operational state.

Examples:

- Product
- Inventory location
- Available quantity
- Inventory timestamp

Grain:

One inventory observation/snapshot per product-location-time context.

---

## 5.6 Identity Links

Purpose:

Represent controlled cross-device identity stitching.

Example:

```text
anonymous_id
      ↓
successful login event
      ↓
customer_id
```

Identity Links are created from successful login events.

Identity Links must not be independently generated as arbitrary
customer-to-anonymous mappings.

Grain:

One identity-link record.

The entity must not claim to implement a production-grade identity
graph.

---

## 5.7 Experiments

Purpose:

Represent controlled product/business experiments.

The primary ORGEE v1.0 experiment is:

```text
Recommendation A/B Test
```

The experiment compares:

```text
Control
    ↓
Top Sellers Recommendations

Treatment
    ↓
Personalized Content-Based Recommendations
```

Primary metric:

```text
Purchase Conversion Rate
```

Grain:

One row per experiment.

ORGEE v1.0 requires one primary experiment and does not require
multiple experiments for technical complexity.

> **Changelog note (post-Phase 8):** The enterprise entity design's
> row-volume estimate for this entity (Section 5.7 in
> `05_Enterprise_Entity_Design.md`) always allowed a range of
> 1-5 experiments. That range was exercised: the project ultimately
> generated 3 experiments (`Dim_Experiment` = 3 rows), with the
> recommendation A/B test (`exp_001`) remaining the one experiment
> actually analyzed end-to-end in Phase 8. See Phase 8's README for
> the full reasoning. This note is added for traceability and does
> not change the locked decision above.

---

## 5.8 Experiment Assignments

Purpose:

Represent assignment of customers/sessions to experiment variants.

The primary ORGEE experimentation unit is:

```text
customer_id
```

The primary experiment uses:

```text
control
treatment
```

with an approximately:

```text
50% control
50% treatment
```

allocation.

Grain:

One assignment per experimental unit per experiment.

---

## 5.9 Recommendation Events

Purpose:

Capture recommendation-system interactions.

Examples:

- Recommendation impression
- Recommendation click
- Recommendation conversion

Grain:

One row per recommendation interaction.

Recommendation Events are maintained separately from the generic Events
entity.

---

# 6. Relationship With Public Data

The enterprise layer must connect to the public foundation using
controlled identifiers.

Primary integration concepts include:

```text
customer_id
product_id
order_id
seller_id
anonymous_id
session_id
campaign_id
experiment_id
```

The public identifiers must not be overwritten.

Public identifiers remain authoritative throughout the enterprise
integration process.

---

# 7. Customer Identity Integration

The enterprise layer must support:

```text
Anonymous User
      ↓
anonymous_id
      ↓
Session / Behavioral Activity
      ↓
Successful Login Event
      ↓
Identity Link
      ↓
customer_id
      ↓
Persistent Customer Identity
```

The public customer identity remains authoritative.

The enterprise layer only adds behavioral and identity-link information.

Identity Links are created only when a successful login event establishes
the relationship.

The same anonymous identity must not be arbitrarily linked to
conflicting customer identities.

---

# 8. Event Requirements

The event layer must be capable of representing a realistic customer
journey.

Minimum conceptual journey:

```text
Session Start
      ↓
Search
      ↓
Product View
      ↓
Add to Cart
      ↓
Checkout
      ↓
Purchase
```

Not every session must complete every step.

The generated data must contain realistic funnel drop-offs.

The generic Events entity must support the following minimum event
vocabulary:

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

Recommendation-specific interactions are excluded from the generic
Events vocabulary.

They are represented through the Recommendation Events entity.

---

# 9. Session Requirements

Sessions must support:

- Session identification
- Anonymous/customer identity
- Device/platform
- Session start
- Session end
- Event association

A session may contain multiple events.

```text
SESSION
   |
   +-- EVENT
   +-- EVENT
   +-- EVENT
   +-- EVENT
```

Sessions must support both anonymous and identified customer activity.

A session may transition from anonymous to identified through a
successful login event.

---

# 10. Marketing Requirements

Marketing data must support analysis of:

- Campaign reach
- Exposure
- Engagement
- Conversion
- Channel performance
- Customer response

Marketing data must be linkable to customers or anonymous identities
where appropriate.

Campaign exposures must occur within valid campaign periods.

Marketing behavior should support the conceptual relationship:

```text
Campaign
    ↓
Exposure
    ↓
Engagement
    ↓
Conversion
```

Not every exposure must result in engagement or conversion.

---

# 11. Inventory Requirements

Inventory data must support:

- Product availability
- Stock levels
- Inventory changes
- Product-level operational analysis
- Relationship between availability and customer behavior

Inventory must remain analytically separate from transactional order
data until integration.

Inventory observations must maintain:

- Valid product relationships
- Valid inventory locations
- Non-negative quantities
- Valid timestamps
- Logical inventory state transitions

---

# 12. Experimentation Requirements

Experimentation data must support:

```text
Experiment
     ↓
Variant
     ↓
Assignment
     ↓
Recommendation Exposure
     ↓
Behavior
     ↓
Conversion
```

The design must allow comparison between control and treatment groups.

The primary ORGEE v1.0 experiment is:

```text
Recommendation A/B Test
```

The primary variants are:

```text
control
treatment
```

The primary metric is:

```text
Purchase Conversion Rate
```

The experiment assignment should target approximately:

```text
50% Control
50% Treatment
```

The generated assignment balance will later be validated through the
Phase 8 Sample Ratio Mismatch check.

The experimentation data must not encode a predetermined business
result.

---

# 13. Recommendation Requirements

Recommendation data must support:

- Recommendation impressions
- Recommendation clicks
- Product interaction
- Conversion relationship
- Recommendation performance analysis

The recommendation event vocabulary is:

```text
impression
click
conversion
```

The generated recommendation data must connect to:

- Products
- Customers or anonymous identities
- Sessions
- Experiments where applicable
- Experiment assignments where applicable

The recommendation event journey should follow:

```text
Recommendation Impression
          ↓
Recommendation Click
          ↓
Conversion
```

Not every impression must produce a click.

Not every click must produce a conversion.

Recommendation Events are maintained separately from generic behavioral
Events.

---

# 14. Enterprise Data Quality Requirements

Every generated enterprise entity must pass:

### Completeness

Required fields must be populated according to defined rules.

### Uniqueness

Primary identifiers must be unique at the defined grain.

### Referential Integrity

Foreign keys must point to valid parent entities.

### Temporal Integrity

Events and relationships must follow logical time ordering.

### Grain Integrity

The generated data must preserve the declared entity grain.

### Domain Integrity

Categorical fields must use controlled values.

### Business Logic

Generated behavior must represent realistic business patterns.

---

# 15. Synthetic Data Principle

Enterprise data will be generated synthetically.

Synthetic generation must not modify the public Olist datasets.

```text
PUBLIC DATA
      ↓
PRESERVE

ENTERPRISE REQUIREMENTS
      ↓
SYNTHETIC GENERATION
      ↓
VALIDATION
```

Synthetic data exists to fill the analytical gaps in the public
dataset.

It must not replace the public transactional foundation.

The enterprise layer must be stored separately from the public data
until the controlled hybrid integration stage.

---

# 16. Entity Count

The ORGEE Phase 2 enterprise layer contains nine approved entities.

The approved entities are:

1. Events
2. Sessions
3. Marketing Campaigns
4. Campaign Exposure
5. Inventory
6. Identity Links
7. Experiments
8. Experiment Assignments
9. Recommendation Events

The detailed architecture for these entities is defined in:

```text
Enterprise Data Requirements
        ↓
Enterprise Entity Design
        ↓
Enterprise Generation Rules
        ↓
Enterprise Generation Configuration
```

No additional enterprise entity is required for ORGEE v1.0 unless a
future business requirement creates a documented need.

---

# 17. Generation Sequence

```text
ENTERPRISE DATA REQUIREMENTS
        ↓
ENTITY RELATIONSHIPS
        ↓
GRAIN DEFINITION
        ↓
IDENTIFIER DESIGN
        ↓
ROW VOLUME DESIGN
        ↓
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
```

The generation configuration contains the quantitative parameters used
by the Python generators.

Generation must remain reproducible through controlled random seeds.

---

# 18. Current Status

The enterprise data layer is currently:

**REQUIREMENTS DEFINED — ENTITY ARCHITECTURE LOCKED**

The approved enterprise architecture consists of nine entities.

The requirements are aligned with:

- Enterprise Entity Design
- Enterprise Generation Rules
- Enterprise Generation Configuration

No additional enterprise entities should be introduced without a
documented business requirement and architecture review.

Synthetic enterprise data generation may proceed according to the
approved Phase 2 design.

---

# 19. Next Step

The enterprise requirements have been translated into the approved
entity architecture.

The Phase 2 workflow now proceeds as:

```text
ENTERPRISE DATA REQUIREMENTS
        ↓
ENTERPRISE ENTITY DESIGN
        ↓
ENTERPRISE GENERATION RULES
        ↓
ENTERPRISE GENERATION CONFIGURATION
        ↓
PYTHON GENERATORS
        ↓
SYNTHETIC DATA
        ↓
DATA QUALITY VALIDATION
        ↓
HYBRID INTEGRATION
```

The next implementation activity is the Python synthetic-data
generation layer.

Synthetic data must not be generated outside the approved entity
architecture and configuration.

---

# FINAL PRINCIPLE

```text
REQUIREMENTS FIRST.

DESIGN THE DATA.

LOCK THE GRAIN.

LOCK THE RELATIONSHIPS.

DEFINE THE GENERATION RULES.

CONFIGURE THE GENERATOR.

THEN GENERATE.

THEN VALIDATE.

THEN INTEGRATE.
```

**ORGEE Phase 2 Enterprise Data Requirements — LOCKED**