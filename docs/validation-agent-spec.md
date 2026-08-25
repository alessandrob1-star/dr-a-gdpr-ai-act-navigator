# Validation Agent Specification

> **Implementation note:** this document defines the regulatory-validation
> behavior of the monitoring pipeline. In the current MVP it is implemented by
> deterministic services in `module_web_scraping/`, not exposed as an additional
> runtime agent alongside the four agents in `module_agents/`.

## Purpose

The Validation Agent checks whether a regulatory signal collected by the Source Monitoring Agent is supported by official evidence.

This is one of the key differentiators of the project: the system does not treat every news article as a legal alert. It separates early warning signals from official legal or regulatory evidence.

## Core Responsibility

For each new monitored item, the Validation Agent must answer:

```text
Is this regulatory signal confirmed by an official source?
```

The answer determines the regulatory event status, reliability score, and dashboard treatment.

## Validation Statuses

### C_UNCONFIRMED_NEWS

This status means the signal exists only in news, expert commentary, or non-binding external sources.

Use when:

- an article reports that a law, guideline, deadline, or proposal is expected;
- no official publication or official draft has been found;
- the source is useful but not legally authoritative.

Dashboard treatment:

- show as `Warning`;
- do not show as official legal alert;
- reliability should remain limited.

Typical reliability range:

```text
20-45 / 100
```

### B_OFFICIAL_DRAFT

This status means the signal is supported by an official draft, consultation, proposal, political agreement, or official policy page.

Use when:

- the European Commission, AI Office, EDPB, EUR-Lex procedure page, or another official institution has published a draft or proposal;
- the measure is not yet binding law;
- implementation timing may still change.

Dashboard treatment:

- show as `Official Draft / Upcoming`;
- make clear that it is not yet fully binding;
- increase monitoring priority.

Typical reliability range:

```text
55-80 / 100
```

### A_OFFICIALLY_PUBLISHED

This status means the measure has been officially published or confirmed by a binding legal source.

Use when:

- the item appears in the Official Journal;
- the item has an EUR-Lex legal act page;
- the item has a stable ELI link;
- the source confirms entry into force or a compliance deadline.

Dashboard treatment:

- show as `Official Alert`;
- display effective date and compliance deadline when available;
- make it eligible for risk scoring.

Typical reliability range:

```text
85-100 / 100
```

## Evidence Sources

The Validation Agent should check sources in this priority order:

1. EUR-Lex Official Journal and ELI links.
2. EUR-Lex legal act or procedure pages.
3. European Commission official pages.
4. European AI Office official pages.
5. EDPB guidelines, recommendations, and public consultations.
6. Other EU institutional sources.
7. Trusted news or expert sources.

Only the first six categories can move an event above `C_UNCONFIRMED_NEWS`.

## Validation Workflow

1. Receive a new `monitored_items` record.
2. Extract key search terms:
   - regulation area;
   - main topic;
   - possible legal act name;
   - date references;
   - institution names;
   - deadline or entry-into-force language.
3. Search existing `regulatory_events` for a related event.
4. If a related event exists, attach the item to it.
5. If no event exists, create a new `regulatory_events` record.
6. Check official sources for confirmation.
7. Create a `validation_results` record.
8. Update event status and reliability score.
9. Send the updated event to the scoring layer when appropriate.

## Official Evidence Rules

### Strong Evidence

Strong evidence can produce `A_OFFICIALLY_PUBLISHED`.

Examples:

- Official Journal publication;
- EUR-Lex legal act page;
- ELI stable link;
- official regulation text;
- official entry-into-force notice.

### Medium Evidence

Medium evidence can produce `B_OFFICIAL_DRAFT`.

Examples:

- European Commission proposal;
- political agreement announcement;
- public consultation;
- draft guidelines;
- EDPB draft document;
- AI Office draft guidance.

### Weak Evidence

Weak evidence should remain `C_UNCONFIRMED_NEWS`.

Examples:

- news article;
- legal blog analysis;
- vendor article;
- newsletter;
- conference recap;
- opinion piece.

Weak evidence can support an existing event, but it should not make the event official.

## Reliability Score Logic

Reliability is not the same as business risk.

Reliability measures how strongly the event is supported by official evidence.

Suggested initial scoring:

```text
Official Journal / EUR-Lex binding act: 95
Official ELI legal act page: 95
European Commission official publication: 80
European AI Office official guidance: 75
EDPB final guideline: 75
Official draft / consultation: 65
Trusted news source: 35
Expert blog: 30
Vendor content: 15
```

If multiple sources support the same event, the score can increase, but official evidence should matter much more than repeated news coverage.

Example:

```text
Three news articles should not outweigh one official source.
```

## Urgency Extraction

The Validation Agent should also extract dates when possible.

Important date types:

- `publication_date`
- `entry_into_force_date`
- `application_date`
- `compliance_deadline`
- `consultation_deadline`

The agent should store dates only when they are clearly stated by the source.

If a date is uncertain, it should be mentioned in the summary but not treated as a confirmed deadline.

## Event Update Rules

An event can move upward in status:

```text
C_UNCONFIRMED_NEWS -> B_OFFICIAL_DRAFT -> A_OFFICIALLY_PUBLISHED
```

An event can also remain unchanged if new items add no stronger evidence.

An event should not automatically move downward unless the official source states that the proposal was withdrawn, delayed, rejected, or superseded.

## Dashboard Output

For each validated event, the dashboard should receive:

- event title;
- regulation area;
- validation status;
- reliability score;
- official evidence link when available;
- supporting news links;
- key dates;
- short explanation;
- recommended attention level.

Example:

```text
Title: AI Act high-risk classification guidance
Status: B_OFFICIAL_DRAFT
Reliability: 68/100
Reason: The signal is supported by draft guidelines published by the European Commission, but no final binding publication has been found yet.
Recommended attention: Monitor closely.
```

## MVP Boundaries

The first version should not try to fully interpret legal obligations.

It should focus on:

- finding signals;
- validating signals;
- grouping related sources;
- identifying official evidence;
- extracting clear dates;
- assigning a transparent reliability status.

Detailed legal interpretation and company-specific impact assessment should happen in later modules.

