# Risk and Reliability Scoring Draft

## Purpose

This document defines the first scoring logic for regulatory events.

The goal is to keep the scoring explainable. The system should not produce a number without showing why that number exists.

For the MVP, scoring is divided into separate dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

## Key Principle

Reliability and risk are different concepts.

Reliability answers:

```text
How official and well-supported is this regulatory event?
```

Risk answers:

```text
How important or dangerous is this event for the company?
```

A news article may describe a very serious possible regulation, but if it is not confirmed by official sources, reliability remains low.

An official regulation may have high reliability, but low company-specific risk if it does not apply to the company profile.

## Reliability Score

Reliability measures the strength of the evidence supporting an event.

Suggested scale:

```text
0-30   Low reliability
31-55  Warning signal
56-80  Official draft or official guidance
81-100 Officially published or strongly confirmed
```

Suggested source weights:

```text
Official Journal / EUR-Lex legal act: 95
ELI stable legal act link: 95
European Commission official publication: 80
European AI Office official guidance: 75
EDPB final guideline: 75
Official draft / public consultation: 65
Trusted news source: 35
Expert legal blog: 30
Vendor content: 15
```

Repeated news coverage can slightly increase confidence, but it should not replace official confirmation.

Example:

```text
Three trusted news articles may move reliability from 35 to 45.
They should not move it to 80 without official evidence.
```

## Urgency Score

Urgency measures how soon the company may need to act.

Suggested scale:

```text
0-25   No clear deadline or long-term monitoring
26-50  Future deadline, not immediate
51-75  Deadline approaching
76-100 Immediate or already applicable
```

Suggested rules:

```text
Already applicable: 90
Deadline within 30 days: 85
Deadline within 90 days: 70
Deadline within 6 months: 55
Deadline within 12 months: 40
No deadline found: 20
Draft with uncertain timing: 30
```

Urgency should use only dates clearly stated in the source.

If a date is mentioned only by a news article and not confirmed officially, the date can be stored as a note but should not drive a high urgency score.

## Regulatory Impact Score

Regulatory impact measures the legal severity of the event.

Suggested scale:

```text
0-25   Informational or low legal effect
26-50  Guidance or interpretation
51-75  Operational compliance obligation
76-100 High penalty, restriction, prohibition, or market access impact
```

Suggested examples:

```text
GDPR personal data breach notification: 80
AI Act prohibited practice: 95
AI Act high-risk system obligation: 85
AI Act transparency obligation: 65
GPAI model provider obligation: 80
EDPB guidance clarification: 55
General policy news: 25
```

This score is about the regulation itself, not yet about whether it applies to a specific company.

## Business Impact Score

Business impact measures how relevant the event is to the company profile.

This score requires data from the Company Profile module.

Suggested scale:

```text
0-25   Not relevant or barely relevant
26-50  Possibly relevant
51-75  Relevant to operations
76-100 Directly affects core product, market access, or legal exposure
```

Example factors:

- company uses AI systems;
- company develops AI systems;
- company provides GPAI models;
- company processes personal data;
- company processes sensitive personal data;
- company operates in the EU;
- company serves EU users;
- company works in high-risk sectors;
- company uses automated decision-making or profiling;
- company transfers personal data outside the EU.

For the MVP, this score can start with rule-based logic using questionnaire answers.

## Overall Priority

Overall priority combines the separate scores into a dashboard-friendly value.

Suggested formula:

```text
Overall Priority =
Reliability Weight +
Urgency Weight +
Regulatory Impact Weight +
Business Impact Weight
```

For the MVP, a simple weighted average is easier to explain than a complex formula.

Suggested weights:

```text
Reliability: 25%
Urgency: 25%
Regulatory Impact: 25%
Business Impact: 25%
```

Alternative later:

```text
Overall Priority =
Reliability x Urgency x Regulatory Impact x Business Impact
```

The multiplication formula creates stronger separation between low and high risk events, but it is less intuitive for an MVP demo.

## Priority Bands

Suggested bands:

```text
0-24    Low
25-49   Medium
50-74   High
75-100  Critical
```

Dashboard labels:

```text
Low: Monitor
Medium: Review
High: Action recommended
Critical: Immediate attention
```

## Example 1: Trusted News Only

Scenario:

A trusted news source reports that new AI Act high-risk guidance may be released soon.

Suggested scores:

```text
Reliability: 35
Urgency: 30
Regulatory Impact: 80
Business Impact: depends on company profile
```

Dashboard treatment:

```text
Warning, not official alert.
```

## Example 2: Official Draft Published

Scenario:

The European Commission publishes draft guidelines on high-risk AI classification.

Suggested scores:

```text
Reliability: 65
Urgency: 45
Regulatory Impact: 85
Business Impact: depends on company profile
```

Dashboard treatment:

```text
Official draft, monitor closely.
```

## Example 3: Official Journal Publication

Scenario:

A relevant AI Act amendment is published in the Official Journal with an application date.

Suggested scores:

```text
Reliability: 95
Urgency: based on deadline
Regulatory Impact: based on legal effect
Business Impact: depends on company profile
```

Dashboard treatment:

```text
Official alert, eligible for risk assessment.
```

## MVP Boundaries

The first version should avoid pretending to provide legal advice.

The scoring should be presented as decision support:

- what happened;
- how official it is;
- how soon it may matter;
- why it may affect the company;
- what should be reviewed next.

The dashboard should make clear that official legal interpretation and final compliance decisions require qualified human review.

