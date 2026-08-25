# 13 - Scoring Model Summary

## Purpose

This document summarizes the scoring model used by the Web Scraping and Source Monitoring module.

The goal is to explain how regulatory events are prioritized before being displayed in the dashboard.

## Core Principle

The platform should not treat every alert in the same way.

Each regulatory event should be scored across separate dimensions:

- reliability;
- urgency;
- regulatory impact;
- business impact;
- overall priority.

This keeps the output explainable and avoids mixing source credibility with business relevance.

## Reliability

Reliability measures how official and well-supported a regulatory event is.

Main drivers:

- official legal publication;
- official guidance;
- official draft or consultation;
- trusted news source;
- expert commentary.

Example:

```text
EUR-Lex official publication -> high reliability
Trusted news article only -> limited reliability
```

Reliability answers:

```text
Can we trust that this regulatory event is real and officially supported?
```

## Urgency

Urgency measures how soon the event may require attention.

Main drivers:

- already applicable obligation;
- deadline within 30 days;
- deadline within 90 days;
- application date within 6 months;
- official consultation deadline;
- no confirmed date.

Urgency should be based on validated dates whenever possible.

Urgency answers:

```text
How soon might this matter?
```

## Regulatory Impact

Regulatory impact measures the legal significance of the event.

Examples:

```text
AI Act prohibited practice -> very high
AI Act high-risk obligation -> high
GDPR data breach notification -> high
AI Act transparency obligation -> medium-high
General policy commentary -> low-medium
```

Regulatory impact answers:

```text
How serious is this regulatory topic in general?
```

## Business Impact

Business impact depends on the company profile.

This score should eventually use the Company Profile module.

Examples:

- high-risk AI guidance matters more to HR, education, credit, healthcare, and critical infrastructure AI systems;
- GDPR data breach guidance matters more to companies processing personal data;
- GPAI obligations matter more to model providers;
- international transfer guidance matters more to companies using non-EU providers.

Business impact answers:

```text
How relevant is this event to this specific company?
```

## Overall Priority

Overall priority combines the separate scores into a dashboard-friendly label.

Suggested labels:

```text
Low
Medium
High
Critical
```

Suggested attention labels:

```text
Low -> Monitor
Medium -> Review
High -> Action recommended
Critical -> Immediate attention
```

## Suggested MVP Formula

For the MVP, use a simple weighted average.

Suggested weights:

```text
Reliability: 25%
Urgency: 25%
Regulatory impact: 25%
Business impact: 25%
```

This is easier to explain in a demo than a complex formula.

Later, the model can evolve into a more advanced scoring engine.

## Example

Scenario:

An official draft guidance on AI Act high-risk classification is detected.

Possible scores:

```text
Reliability: 65
Urgency: 55
Regulatory impact: 85
Business impact: 80
Overall priority: High
```

Dashboard output:

```text
Official Draft / Upcoming
Action recommended
```

## MVP Success Criteria

The scoring model is successful if it can:

- separate source reliability from business risk;
- prioritize official alerts over weak signals;
- highlight urgent validated deadlines;
- explain why an event is high or low priority;
- provide clear labels for dashboard users.

