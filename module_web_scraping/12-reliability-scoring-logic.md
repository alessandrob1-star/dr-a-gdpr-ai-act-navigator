# 12 - Reliability Scoring Logic

## Purpose

This document defines how the Web Scraping and Source Monitoring module should calculate reliability for regulatory events.

Reliability measures how strongly an event is supported by official or trusted evidence.

It is different from urgency, regulatory impact, and business impact.

## Core Principle

Reliability answers:

```text
How official and well-supported is this regulatory event?
```

A serious news article can describe an important possible regulatory change, but if the event is not confirmed by official sources, reliability should remain limited.

## Reliability Scale

Suggested scale:

```text
0-30   Low reliability
31-55  Warning signal
56-80  Official draft, consultation, or official guidance
81-100 Officially published or strongly confirmed
```

## Source Weights

Initial source authority weights:

```text
Official Journal / EUR-Lex legal act: 95
ELI stable legal act link: 95
European Commission official publication: 80
European AI Office official guidance: 75
EDPB final guideline or recommendation: 75
Official draft or public consultation: 65
Trusted news source: 35
Expert legal or policy commentary: 30
Vendor content: 15
```

These values are intentionally simple for the MVP and can be refined later.

## Validation Status Mapping

Reliability should align with event validation status.

### C_UNCONFIRMED_NEWS

Typical reliability range:

```text
20-45
```

Use when the event is supported only by news, commentary, or other non-binding sources.

### B_OFFICIAL_DRAFT

Typical reliability range:

```text
55-80
```

Use when the event is supported by official draft material, official consultation, official proposal, or official guidance.

### A_OFFICIALLY_PUBLISHED

Typical reliability range:

```text
85-100
```

Use when the event is confirmed by an official binding source such as EUR-Lex or the Official Journal.

## Multiple Sources Rule

Multiple sources can increase confidence, but official evidence should matter more than repeated news coverage.

Example:

```text
Three trusted news articles should not outweigh one official source.
```

Suggested approach:

- start from the strongest evidence source;
- add a small bonus for independent supporting sources;
- cap the score according to validation status.

Example caps:

```text
C_UNCONFIRMED_NEWS max: 45
B_OFFICIAL_DRAFT max: 80
A_OFFICIALLY_PUBLISHED max: 100
```

## Supporting Source Bonus

Suggested bonus logic:

```text
Additional trusted warning source: +3
Additional expert commentary source: +2
Additional official guidance source: +5
Additional official binding source: +5
```

Apply the validation status cap after adding bonuses.

## Example 1 - News Only

Scenario:

Two trusted news sources report upcoming AI Act guidance.

Suggested result:

```text
Strongest source: trusted news source = 35
Additional trusted warning source: +3
Validation status cap: C_UNCONFIRMED_NEWS max 45
Final reliability: 38
```

Dashboard label:

```text
Warning
```

## Example 2 - Official Draft

Scenario:

A European Commission draft guidance page supports an event that was first detected in news.

Suggested result:

```text
Strongest source: official draft = 65
Additional trusted news source: +3
Validation status cap: B_OFFICIAL_DRAFT max 80
Final reliability: 68
```

Dashboard label:

```text
Official Draft / Upcoming
```

## Example 3 - Official Publication

Scenario:

EUR-Lex confirms the legal act.

Suggested result:

```text
Strongest source: EUR-Lex legal act = 95
Additional supporting sources: optional small bonus
Validation status cap: A_OFFICIALLY_PUBLISHED max 100
Final reliability: 95-100
```

Dashboard label:

```text
Official Alert
```

## Reliability vs Risk

Reliability should not be used as the only measure of priority.

An event can be:

- highly reliable but low relevance to a specific company;
- low reliability but potentially high impact if later confirmed;
- highly reliable and urgent, requiring immediate attention.

The final dashboard priority should combine:

- reliability;
- urgency;
- regulatory impact;
- business impact.

## MVP Success Criteria

Reliability scoring is successful if the system can:

- distinguish official sources from warning sources;
- assign explainable reliability scores;
- prevent repeated news from becoming official confirmation;
- support clear dashboard labels;
- provide evidence-backed scoring explanations.

