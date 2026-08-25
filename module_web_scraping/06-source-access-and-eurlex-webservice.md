# 06 - Source Access and EUR-Lex Webservice

## Purpose

This document defines the access strategy for the sources used by the Web Scraping and Source Monitoring module, with a specific focus on the EUR-Lex webservice.

The goal is to make the official source monitoring layer practical without blocking the MVP on complex integrations.

## Access Strategy

The MVP should start with simple and reliable access methods:

- curated official URLs;
- stable legal links;
- official web pages;
- RSS feeds where available;
- manually collected official documents;
- EUR-Lex webservice for structured official queries.

The system should not rely on uncontrolled broad scraping.

## Source Access Methods

Suggested access method labels:

```text
manual_seed
webpage
rss
api
stable_link
download_reference
```

## Priority Sources

### Priority 1

Required for the MVP:

- EUR-Lex Official Journal;
- EUR-Lex ELI stable links;
- EUR-Lex webservice;
- European Commission AI Office;
- European Commission AI Act policy pages;
- EDPB Guidelines and Recommendations.

### Priority 2

Useful official update sources:

- European Commission Digital Strategy News;
- EDPB News.

### Priority 3

Trusted warning sources:

- IAPP News;
- Euractiv Tech.

### Priority 4

Expert context sources:

- Future of Privacy Forum;
- European Law Blog.

## EUR-Lex Webservice

EUR-Lex webservice access has been approved for the project.

The service can be used to query EUR-Lex directly and retrieve structured XML results.

Technical details:

```text
WSDL:
https://eur-lex.europa.eu/EURLexWebService?wsdl

SOAP endpoint:
https://eur-lex.europa.eu/EURLexWebService

Protocol:
SOAP 1.2

Authentication:
WS-Security UsernameToken

Operation:
doQuery

SOAP action:
https://eur-lex.europa.eu/ws/doQuery

Approved call frequency:
1,000 calls
```

Credentials must be stored outside the repository.

The project should use local environment variables for development, for example:

```text
EURLEX_USERNAME=
EURLEX_PASSWORD=
```

These values must not be committed to GitHub.

## EUR-Lex Query Request

The webservice uses a SOAP 1.2 document-literal request. The body root is the
namespaced `searchRequest` element; `doQuery` is the WSDL operation and SOAP
action, not an additional wrapper in the XML body.

Main request fields:

- `expertQuery`
- `page`
- `pageSize`
- `searchLanguage`
- `limitToLatestConsleg`
- `excludeAllConsleg`
- `showDocumentsAvailableIn`

Example conceptual query:

```xml
<eur:searchRequest xmlns:eur="http://eur-lex.europa.eu/search">
  <eur:expertQuery>DN = 32024R1689</eur:expertQuery>
  <eur:page>1</eur:page>
  <eur:pageSize>10</eur:pageSize>
  <eur:searchLanguage>en</eur:searchLanguage>
</eur:searchRequest>
```

This kind of query can be used to retrieve official information about known legal acts, such as the EU AI Act.

## MVP Use Cases

The EUR-Lex webservice can support:

- checking whether a legal act exists in EUR-Lex;
- searching by CELEX number;
- searching for AI Act and GDPR related documents;
- monitoring official publication signals;
- supporting validation of news and draft events.

## Role in Validation

EUR-Lex is an official source.

A match from EUR-Lex can support:

```text
A_OFFICIALLY_PUBLISHED
```

when the result confirms an official legal act or publication.

News articles should never override EUR-Lex evidence.

## MVP Boundary

The first MVP does not need full EUR-Lex automation immediately.

Recommended implementation order:

1. Test one local SOAP request with credentials.
2. Query a known CELEX number such as the AI Act.
3. Parse the XML response.
4. Store the result as official source evidence.
5. Connect the result to validation status updates.

This keeps the integration focused and demonstrable.

