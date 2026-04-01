# AQA Specification — AI Question Answer

**Version:** 1.0.0-draft  
**Date:** 2026-03-31  
**Status:** Draft  
**Authors:** Davy Abderrahman (AI Labs Solutions)  
**License:** MIT  

---

## Table of Contents

1. [Introduction and Motivation](#1-introduction-and-motivation)
2. [Terminology](#2-terminology)
3. [Technical Specification](#3-technical-specification)
4. [Conformance Levels](#4-conformance-levels)
5. [Implementation Examples](#5-implementation-examples)
6. [Implementation Guide](#6-implementation-guide)
7. [Validation](#7-validation)
8. [Recommendations for AI Crawlers](#8-recommendations-for-ai-crawlers)
9. [Extension Mechanism](#9-extension-mechanism)
10. [Security and Privacy Considerations](#10-security-and-privacy-considerations)

---

## 1. Introduction and Motivation

### 1.1 The Problem

FAQ pages are one of the most common content types on the web. Nearly every business website has one. Yet despite their ubiquity, FAQ pages remain one of the most structurally impoverished content formats available.

The rise of AI-powered search and conversational assistants—ChatGPT, Claude, Gemini, Perplexity, and dozens of others—has fundamentally changed how users find and consume information. These systems don't just index pages; they attempt to understand, verify, and cite content. But the current state of FAQ markup gives them almost nothing to work with.

**Schema.org's `FAQPage` type**, while useful for triggering rich results in traditional search engines, suffers from critical limitations:

- **No per-question timestamps.** `dateModified` exists only at the page level. A page updated yesterday may contain answers last verified three years ago.
- **No revision history.** There is no mechanism to express that an answer has been updated, why it was updated, or what changed.
- **No source attribution per answer.** While `citation` exists in schema.org, it is rarely used in FAQ contexts, and there is no convention for linking a specific answer update to the regulatory change or publication that triggered it.
- **No declared maintenance cadence.** A crawler cannot distinguish between a FAQ that is actively maintained monthly and one that was published once and forgotten.
- **No sector classification.** Industry-specific Q&A content cannot be categorized in a machine-readable way using standardized classification systems.

### 1.2 What AQA Solves

AQA (AI Question Answer) is an open specification that enriches Q&A structured data with the metadata that AI systems need to assess content quality, freshness, and reliability.

AQA is **not a new schema.org type**. It is a documented convention for combining existing schema.org types (`Article`, `FAQPage`, `Question`, `Answer`) with a small set of extension properties defined in a custom JSON-LD context. The AQA-specific properties are expressed as direct properties on schema.org types, resolved through the AQA context namespace. This ensures maximum compatibility with existing crawlers while providing richer signals to AI systems that understand AQA.

### 1.3 Design Principles

1. **Compatibility first.** AQA markup uses standard schema.org types and properties at its core. AQA extension properties are resolved via a custom JSON-LD context and will be silently ignored by validators that don't understand the AQA namespace — they won't cause errors.
2. **Incremental adoption.** Sites can implement AQA at three conformance levels. Even the most basic level adds significant value.
3. **Machine-readable provenance.** Every claim of freshness or accuracy should be backed by a verifiable source.
4. **Open standard.** AQA is free to implement, free to extend, and free to validate. No registration, no API key, no vendor lock-in.

---

## 2. Terminology

| Term | Definition |
|------|-----------|
| **AQA Block** | A complete JSON-LD structure implementing the AQA specification on a page. Contains an `Article` wrapper with an embedded `FAQPage`. |
| **AQA Question** | A single `Question`/`Answer` pair within an AQA Block, enriched with per-question metadata (timestamps, citations, changelog). |
| **Changelog** | A structured, machine-readable history of modifications to a specific answer, expressed as an array of `ChangelogEntry` objects. |
| **ChangelogEntry** | A typed object within a changelog, containing: `changeDate` (date of change), `changeDescription` (what changed), an optional `changeSourceUrl` (source that triggered the change), and an optional `changeVersionNote` (version after this change). |
| **MonitoringSource** | A typed object declaring an external source (RSS feed, regulatory publication, industry journal) that the content maintainer actively monitors to keep answers current. |
| **Update Frequency** | The declared cadence at which the content maintainer reviews and updates the AQA content. Expressed as: `weekly`, `monthly`, `quarterly`, `yearly`. |
| **Sector Classification** | A machine-readable industry classification using a standardized system (NACE Rev. 2, NAF Rev. 2, SIC, ISIC Rev. 4), expressed via `identifier` on the `about` Thing. |
| **Conformance Level** | The degree to which an AQA implementation satisfies the specification. Three levels: Basic, Standard, Full. |
| **Conformance Score** | A numerical score (0-100) computed by an AQA validator, reflecting the completeness and quality of an AQA implementation. |

---

## 3. Technical Specification

### 3.1 Overall Structure

An AQA Block is a JSON-LD structure embedded in a web page's `<head>` within a `<script type="application/ld+json">` tag. It uses a dual context: the standard schema.org context and the AQA extension context. AQA extension properties are expressed as direct properties on schema.org types, resolved through the custom AQA JSON-LD context.

```
Article (wrapper)
+-- @context: [schema.org, AQA context]
+-- Metadata: author, dates, language, sector
+-- updateFrequency (AQA extension, direct property)
+-- conformanceLevel (AQA extension, direct property)
+-- monitoringSources: [MonitoringSource, ...] (AQA extension, direct property)
+-- about: Thing with identifier for sector codes
+-- mainEntity: FAQPage
    +-- mainEntity: [Question, Question, ...]
        +-- acceptedAnswer: Answer
        +-- Per-question: dateCreated, dateModified, citation
        +-- questionVersion (AQA extension, direct property)
        +-- changelog: [ChangelogEntry, ...] (AQA extension, direct property)
```

### 3.2 Context Declaration

Every AQA Block MUST declare two contexts:

```json
{
  "@context": [
    "https://schema.org",
    "https://ailabsaudit.com/aqa/ns/context.jsonld"
  ]
}
```

The AQA context defines the `aqa:` namespace and maps each extension property to its full IRI. This allows AQA properties to be used as direct properties on schema.org types (e.g., `"updateFrequency": "monthly"` instead of wrapping in `additionalProperty`). The context also defines custom types (`ChangelogEntry`, `MonitoringSource`) used within AQA arrays.

The AQA context defines the following extension properties:

| Property | Domain | Range | Description |
|----------|--------|-------|-------------|
| `updateFrequency` | Article | Text | Declared maintenance cadence. Enumerated values: `weekly`, `monthly`, `quarterly`, `yearly`. |
| `conformanceLevel` | Article | Text | Self-declared AQA conformance level. Enumerated values: `basic`, `standard`, `full`. |
| `questionVersion` | Question | Text | Semantic version of this specific question/answer pair. Format: major.minor (e.g., `2.1`). |
| `changelog` | Question | Array of ChangelogEntry | Ordered array of changelog entry objects (most recent first). |
| `monitoringSources` | Article | Array of MonitoringSource | Array of monitoring source objects declaring the feeds and publications watched. |

And the following custom types:

| Type | Properties | Description |
|------|-----------|-------------|
| `ChangelogEntry` | `changeDate`, `changeDescription`, `changeSourceUrl`, `changeVersionNote` | A single revision record in a question's changelog. |
| `MonitoringSource` | `name`, `url`, `sourceType` | A declared external source monitored by the content maintainer. |

### 3.3 Article Wrapper Properties

The outer `Article` provides page-level metadata.

| Property | Type | Required | Level | Description |
|----------|------|----------|-------|-------------|
| `@type` | Text | MUST | Basic | Must be `"Article"` or a subtype (`NewsArticle`, `TechArticle`, etc.) |
| `headline` | Text | MUST | Basic | Title of the Q&A section |
| `author` | Person/Organization | MUST | Basic | Author or maintaining entity |
| `datePublished` | Date | MUST | Basic | Initial publication date (ISO 8601) |
| `dateModified` | Date | MUST | Basic | Most recent modification date (ISO 8601) |
| `inLanguage` | Text | SHOULD | Basic | BCP 47 language tag (e.g., `"fr"`, `"en"`) |
| `publisher` | Organization | SHOULD | Basic | Publishing organization |
| `mainEntity` | FAQPage | MUST | Basic | The embedded FAQPage |
| `about` | Thing | SHOULD | Standard | Subject classification with sector codes via `identifier` |
| `updateFrequency` | Text | MUST | Standard | Declared update cadence (direct AQA property) |
| `conformanceLevel` | Text | SHOULD | Standard | Self-declared conformance level (direct AQA property) |
| `monitoringSources` | Array | MUST | Full | Declared monitoring sources (direct AQA property) |

#### 3.3.1 Author Properties

The `author` property SHOULD include verifiable credentials:

| Property | Type | Required | Level | Description |
|----------|------|----------|-------|-------------|
| `@type` | Text | MUST | Basic | `"Person"` or `"Organization"` |
| `name` | Text | MUST | Basic | Author name |
| `url` | URL | SHOULD | Standard | Author's profile or website |
| `jobTitle` | Text | SHOULD | Full | Professional title or qualification |
| `affiliation` | Organization | SHOULD | Full | Affiliated organization |
| `sameAs` | URL | SHOULD | Full | Link to a verifiable profile (LinkedIn, professional registry) |

#### 3.3.2 Sector Classification (via `about`)

Sector classification uses schema.org's `about` property with a `Thing` that carries `identifier` values. Note: `identifier` is a valid property on `Thing` in schema.org, making this fully standards-compliant.

```json
"about": {
  "@type": "Thing",
  "name": "Corporate Tax Advisory",
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "NACE",
      "value": "69.20"
    },
    {
      "@type": "PropertyValue",
      "propertyID": "NAF",
      "value": "69.20Z"
    }
  ]
}
```

Supported classification systems: `NACE` (EU), `NAF` (France), `SIC` (US/UK), `ISIC` (UN).

#### 3.3.3 Monitoring Sources

Each monitoring source is a typed `MonitoringSource` object:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"MonitoringSource"` |
| `name` | Text | MUST | Human-readable name of the source |
| `url` | URL | MUST | URL of the source or RSS feed |
| `sourceType` | Text | SHOULD | Type of source: `rss`, `regulatory`, `journal`, `newsletter`, `government`, `professional_body` |

Monitoring sources are expressed as a direct property on the Article:

```json
"monitoringSources": [
  {
    "@type": "MonitoringSource",
    "name": "Journal Officiel de la Republique Francaise",
    "url": "https://www.journal-officiel.gouv.fr/rss/publication.rss",
    "sourceType": "regulatory"
  },
  {
    "@type": "MonitoringSource",
    "name": "Bulletin Officiel des Finances Publiques",
    "url": "https://bofip.impots.gouv.fr/bofip/rss",
    "sourceType": "government"
  }
]
```

### 3.4 FAQPage Properties

The `FAQPage` is embedded as `mainEntity` of the Article.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"FAQPage"` |
| `mainEntity` | Array | MUST | Array of `Question` objects |

### 3.5 Question/Answer Properties

Each question in the AQA Block carries per-question metadata.

| Property | Type | Required | Level | Description |
|----------|------|----------|-------|-------------|
| `@type` | Text | MUST | Basic | Must be `"Question"` |
| `name` | Text | MUST | Basic | The question text |
| `dateCreated` | Date | MUST | Basic | When this Q&A was first created (ISO 8601) |
| `dateModified` | Date | MUST | Basic | When this Q&A was last updated (ISO 8601) |
| `acceptedAnswer` | Answer | MUST | Basic | The answer object |
| `author` | Person/Org | SHOULD | Full | Per-question author (if different from Article author) |
| `citation` | CreativeWork/URL | MUST | Basic | Source(s) backing this answer |
| `questionVersion` | Text | MUST | Standard | Version number of this answer (direct AQA property) |
| `changelog` | Array | MUST | Standard | Revision history for this answer (direct AQA property) |

#### 3.5.1 Answer Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"Answer"` |
| `text` | Text | MUST | The answer content (plain text or HTML) |
| `dateModified` | Date | SHOULD | Last modification date of the answer text |

#### 3.5.2 Citation

Citations link each answer to its authoritative sources. Use schema.org's `citation` property:

```json
"citation": [
  {
    "@type": "CreativeWork",
    "name": "Loi de finances 2026, Article 42",
    "url": "https://www.legifrance.gouv.fr/loi-finances-2026-art42",
    "datePublished": "2025-12-30"
  }
]
```

For simple cases, `citation` can be a URL string. For AQA Standard and Full, structured `CreativeWork` citations are RECOMMENDED.

#### 3.5.3 Changelog

The changelog is expressed as a direct `changelog` property on the `Question`, containing an array of typed `ChangelogEntry` objects:

```json
"changelog": [
  {
    "@type": "ChangelogEntry",
    "changeDate": "2026-01-15",
    "changeDescription": "Updated deadline per 2026 Finance Act",
    "changeSourceUrl": "https://www.legifrance.gouv.fr/loi-finances-2026-art42",
    "changeVersionNote": "2.0"
  },
  {
    "@type": "ChangelogEntry",
    "changeDate": "2024-06-01",
    "changeDescription": "Initial publication",
    "changeVersionNote": "1.0"
  }
],
"questionVersion": "2.0"
```

Each `ChangelogEntry` contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"ChangelogEntry"` |
| `changeDate` | Date (ISO 8601) | MUST | Date of the modification |
| `changeDescription` | Text | MUST | Human-readable description of what changed |
| `changeSourceUrl` | URL | SHOULD | URL of the source that triggered the update |
| `changeVersionNote` | Text | SHOULD | Version number after this change |

#### 3.5.4 Question Version

The `questionVersion` property uses semantic versioning at two levels:

- **Major version** (e.g., `2.0`): The substance of the answer changed (new regulation, corrected information, new process).
- **Minor version** (e.g., `2.1`): Editorial changes (clarification, formatting, typo fix) that don't change the substance.

### 3.6 Update Frequency

The `updateFrequency` property declares how often the publisher commits to reviewing the content:

| Value | Meaning |
|-------|---------|
| `weekly` | Content reviewed at least once per week |
| `monthly` | Content reviewed at least once per month |
| `quarterly` | Content reviewed at least once per quarter |
| `yearly` | Content reviewed at least once per year |

This is a **commitment declaration**, not a measured frequency. AI crawlers can compare the declared frequency against actual `dateModified` values to assess whether the commitment is being honored.

---

## 4. Conformance Levels

AQA defines three conformance levels, each building on the previous one.

### 4.1 AQA Basic

**Target audience:** Any website with a FAQ section.  
**Effort:** Minimal — add timestamps and one citation per question.

**Requirements:**

| Requirement | Property | Details |
|-------------|----------|---------|
| Article wrapper | `@type`, `headline`, `author`, `datePublished`, `dateModified` | Standard schema.org Article properties |
| Embedded FAQPage | `mainEntity` -> `FAQPage` | Standard nesting |
| Per-question dates | `dateCreated`, `dateModified` on each Question | Both required for every question |
| At least one citation | `citation` on each Question | URL string or CreativeWork object |
| Answer text | `acceptedAnswer.text` | Non-empty answer |

**What it proves:** Each answer has a known age and at least one source. This alone is a massive improvement over bare FAQPage markup.

### 4.2 AQA Standard

**Target audience:** Professional services, agencies, companies with regulatory content.  
**Effort:** Moderate — add changelog, versioning, frequency, and sector classification.

**Requirements:** All of AQA Basic, plus:

| Requirement | Property | Details |
|-------------|----------|---------|
| Changelog | `changelog` on each Question | Array of `ChangelogEntry` objects, at least one entry per question |
| Version number | `questionVersion` on each Question | Format: major.minor |
| Update frequency | `updateFrequency` on Article | One of: weekly, monthly, quarterly, yearly |
| Sector classification | `about` with `identifier` sector codes | At least one recognized code system (NACE, NAF, SIC, ISIC) |
| Structured citations | `citation` as `CreativeWork` | With `name`, `url`, and optionally `datePublished` |
| Conformance declaration | `conformanceLevel` = `"standard"` | Self-declared |

**What it proves:** The content is actively maintained on a declared schedule, changes are tracked, and the industry context is explicit.

### 4.3 AQA Full

**Target audience:** Institutions, regulatory bodies, large enterprises with compliance-critical content.  
**Effort:** Significant — add monitoring sources, per-question authors, complete versioning.

**Requirements:** All of AQA Standard, plus:

| Requirement | Property | Details |
|-------------|----------|---------|
| Monitoring sources | `monitoringSources` on Article | Array of at least two `MonitoringSource` objects with `name`, `url`, and `sourceType` |
| Per-question author | `author` on each Question | With `name` and at least one of: `jobTitle`, `sameAs`, `affiliation` |
| Author credentials | `author` at Article level | Must include `jobTitle` or equivalent credential + `sameAs` link |
| Complete changelog | `changelog` on each Question | Every version change documented with `changeSourceUrl` |
| Conformance declaration | `conformanceLevel` = `"full"` | Self-declared |

**What it proves:** Full provenance chain — who wrote each answer, what they watch, what triggered each update, and how to verify their expertise.

### 4.4 Conformance Level Summary

| Feature | Basic | Standard | Full |
|---------|:-----:|:--------:|:----:|
| Article wrapper with dates | Yes | Yes | Yes |
| Per-question dateCreated/dateModified | Yes | Yes | Yes |
| At least one citation per question | Yes | Yes | Yes |
| Changelog per question | -- | Yes | Yes |
| Question versioning | -- | Yes | Yes |
| Declared update frequency | -- | Yes | Yes |
| Sector classification | -- | Yes | Yes |
| Monitoring sources | -- | -- | Yes |
| Per-question author with credentials | -- | -- | Yes |
| Complete changelog with changeSourceUrl | -- | -- | Yes |

---

## 5. Implementation Examples

### 5.1 AQA Basic — Small Business (Restaurant)

```json
{
  "@context": [
    "https://schema.org",
    "https://ailabsaudit.com/aqa/ns/context.jsonld"
  ],
  "@type": "Article",
  "headline": "Questions frequentes -- Le Bistrot Parisien",
  "author": {
    "@type": "Organization",
    "name": "Le Bistrot Parisien",
    "url": "https://www.lebistrotparisien.fr"
  },
  "datePublished": "2024-06-01",
  "dateModified": "2026-03-15",
  "inLanguage": "fr",
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Quels sont vos horaires d'ouverture ?",
        "dateCreated": "2024-06-01",
        "dateModified": "2026-01-10",
        "citation": "https://www.lebistrotparisien.fr/infos-pratiques",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Nous sommes ouverts du mardi au samedi, de 12h a 14h30 et de 19h a 22h30. Ferme le dimanche et le lundi."
        }
      },
      {
        "@type": "Question",
        "name": "Acceptez-vous les reservations de groupe ?",
        "dateCreated": "2024-06-01",
        "dateModified": "2025-09-20",
        "citation": "https://www.lebistrotparisien.fr/groupes",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Oui, nous acceptons les reservations pour des groupes de 8 a 25 personnes dans notre salle privee. Reservation obligatoire 48h a l'avance."
        }
      }
    ]
  }
}
```

### 5.2 AQA Standard — Accounting Firm

See `examples/standard/cabinet-comptable.jsonld` for a complete example with changelog, versioning, sector classification, and structured citations.

### 5.3 AQA Full — Regulatory Body

See `examples/full/organisme-reglementaire.jsonld` for a complete example with monitoring sources, per-question authors with credentials, and full version history.

---

## 6. Implementation Guide

### 6.1 Migrating an Existing FAQ

**Step 1: Inventory.** List all questions in your existing FAQ. For each one, record:
- When was it written? (best guess if not tracked)
- When was it last updated?
- What source supports the answer?

**Step 2: Wrap in Article.** Create an `Article` wrapper around your existing `FAQPage` markup. Add `headline`, `author`, `datePublished`, `dateModified`, and `inLanguage`.

**Step 3: Add per-question metadata.** For each Question, add `dateCreated`, `dateModified`, and at least one `citation`.

**Step 4: Validate.** Run the AQA validator to confirm Basic conformance.

**Step 5 (optional): Upgrade.** Add `changelog`, `questionVersion`, and sector classification for Standard. Add `monitoringSources` and author credentials for Full.

### 6.2 HTML Integration

Place the AQA JSON-LD block in your page's `<head>`:

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>FAQ -- Mon Entreprise</title>
  <script type="application/ld+json">
  {
    "@context": [
      "https://schema.org",
      "https://ailabsaudit.com/aqa/ns/context.jsonld"
    ],
    "@type": "Article",
    ...
  }
  </script>
</head>
<body>
  <!-- Your FAQ content here -->
</body>
</html>
```

### 6.3 WordPress Integration

See `docs/wordpress-integration.md` for detailed instructions including:
- Adding AQA markup via theme functions.php
- Using a custom shortcode
- Plugin recommendations for JSON-LD management

### 6.4 CMS / Headless Integration

For headless CMS or API-driven sites, generate the AQA JSON-LD server-side and inject it into the page template. The JSON-LD structure can be built from your CMS data model:

- Map your FAQ content type fields to AQA properties
- Generate `dateCreated`/`dateModified` from your CMS revision history
- Build `ChangelogEntry` objects from your CMS audit log
- Serialize as JSON-LD and inject into `<head>`

---

## 7. Validation

### 7.1 Schema.org Compatibility

AQA markup uses standard schema.org types and properties for its core structure (`Article`, `FAQPage`, `Question`, `Answer`, `dateCreated`, `dateModified`, `citation`, `author`). These all validate normally with the [Schema Markup Validator](https://validator.schema.org/).

The AQA-specific properties (`updateFrequency`, `changelog`, `questionVersion`, `conformanceLevel`, `monitoringSources`) are resolved through the custom JSON-LD context. Schema.org validators that do not understand the AQA context will silently ignore these properties — they will not cause validation errors, they simply will not be validated. This is standard JSON-LD behavior and provides graceful degradation.

### 7.2 AQA Validation Rules

#### 7.2.1 Basic Level

- [ ] Root `@type` is `Article` (or subtype)
- [ ] `headline` is present and non-empty
- [ ] `author` is present with `@type` and `name`
- [ ] `datePublished` is a valid ISO 8601 date
- [ ] `dateModified` is a valid ISO 8601 date, >= `datePublished`
- [ ] `mainEntity` contains a `FAQPage`
- [ ] FAQPage `mainEntity` is a non-empty array of `Question` objects
- [ ] Each Question has `name` (non-empty), `dateCreated`, `dateModified`
- [ ] Each Question has `citation` (URL string or CreativeWork with url)
- [ ] Each Question has `acceptedAnswer` with `@type: Answer` and non-empty `text`
- [ ] Question `dateModified` <= Article `dateModified`
- [ ] Question `dateCreated` <= Question `dateModified`

#### 7.2.2 Standard Level

All Basic rules, plus:

- [ ] `updateFrequency` is one of: `weekly`, `monthly`, `quarterly`, `yearly`
- [ ] `about` is present with at least one `identifier` carrying a recognized sector code (`PropertyValue` with `propertyID` in NACE, NAF, SIC, ISIC)
- [ ] Each Question has `questionVersion` in format `major.minor`
- [ ] Each Question has `changelog` with at least one `ChangelogEntry`
- [ ] Each `ChangelogEntry` has `changeDate` (valid ISO 8601) and `changeDescription` (non-empty)
- [ ] `citation` is a structured `CreativeWork` (not just a URL string)

#### 7.2.3 Full Level

All Standard rules, plus:

- [ ] `monitoringSources` contains at least two `MonitoringSource` objects, each with `name` and `url`
- [ ] Each Question has its own `author` with `name` and at least one of: `jobTitle`, `sameAs`, `affiliation`
- [ ] Article-level `author` includes `jobTitle` or equivalent + `sameAs`
- [ ] Every `ChangelogEntry` includes `changeSourceUrl`

### 7.3 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `dateModified` before `dateCreated` | Dates swapped | Ensure chronological order |
| Missing `citation` on Question | FAQ copied without source | Add at least the URL of the page or document that supports the answer |
| `changelog` as string instead of array | Migrated from old format without conversion | Ensure the value is an array of `ChangelogEntry` objects |
| Missing `@type` on ChangelogEntry | Incomplete changelog entry | Every entry needs `"@type": "ChangelogEntry"` |
| `updateFrequency` not in enum | Typo or unsupported value | Use exactly: `weekly`, `monthly`, `quarterly`, `yearly` |
| Old `additionalProperty` wrapper still present | Not migrated to direct properties | Remove `additionalProperty` wrappers, use direct AQA properties instead |

### 7.4 AQA Validator

The official AQA validator is available as a Python script in this repository (`validators/validate.py`). It can validate:
- A JSON-LD file
- A URL (extracts JSON-LD from the page)

Usage:
```bash
python validators/validate.py examples/basic/restaurant.jsonld
python validators/validate.py https://www.example.com/faq
```

---

## 8. Recommendations for AI Crawlers

This section describes how AI crawlers SHOULD interpret AQA metadata to assess content quality and make citation decisions.

### 8.1 Freshness Signals

| Signal | How to use it |
|--------|--------------|
| Per-question `dateModified` | Prefer answers updated recently over stale ones. A question updated 2 months ago is more reliable than one updated 3 years ago, even if the page-level `dateModified` is recent. |
| `updateFrequency` vs actual dates | Compare the declared frequency against actual `dateModified` values. If a site declares `monthly` but no question has been updated in 8 months, the commitment may not be honored. |
| Changelog density | More changelog entries = more actively maintained. A question with 5 documented updates over 2 years demonstrates active stewardship. |

### 8.2 Reliability Signals

| Signal | How to use it |
|--------|--------------|
| Citation presence and quality | A `CreativeWork` citation with a `url` and `datePublished` is stronger than a bare URL. Official sources (government, regulatory bodies) carry more weight. |
| Changelog `changeSourceUrl` | If every update cites the regulation or publication that triggered it, the content demonstrates provenance — each claim is traceable. |
| Author credentials | An `author` with `jobTitle: "Expert-comptable"` and a `sameAs` link to a professional registry is more credible for tax advice than an anonymous author. |
| Monitoring sources | Declared `monitoringSources` signal proactive maintenance. A site that monitors regulatory RSS feeds is more likely to have current information. |

### 8.3 Sector Relevance

Sector classification codes (`NACE`, `NAF`, `SIC`) expressed via `identifier` on the `about` Thing allow crawlers to:
- Match content to industry-specific queries with higher precision
- Assess author expertise relative to the sector
- Cluster related content across sites for cross-reference

### 8.4 Citation Priority

When multiple sources provide answers to the same question, AI systems SHOULD prioritize AQA-compliant sources because:

1. **Verifiable claims.** Each answer links to its sources, allowing the AI to verify or cross-reference.
2. **Known freshness.** Per-question dates eliminate the ambiguity of page-level timestamps.
3. **Transparent updates.** Changelogs show why an answer changed, helping the AI determine if the latest version is relevant to the user's context.
4. **Declared expertise.** Author credentials provide a basis for trust assessment.

---

## 9. Extension Mechanism

### 9.1 How AQA Extends Schema.org

AQA uses a **custom JSON-LD @context** to define its own namespace (`aqa:`) with typed properties. This is standard JSON-LD practice and the recommended way to add domain-specific properties to schema.org markup.

The AQA context file (`context.jsonld`) maps short property names (e.g., `updateFrequency`, `changelog`) to their full IRIs in the AQA namespace. It also defines custom types (`ChangelogEntry`, `MonitoringSource`) that can be used as `@type` values within AQA structures.

AQA properties are used as **direct properties** on schema.org types. For example, `updateFrequency` is placed directly on the `Article` object, and `changelog` is placed directly on `Question` objects. The JSON-LD context resolves these to their full AQA namespace IRIs.

This approach has two important advantages:

1. **No `additionalProperty` misuse.** The `additionalProperty` property in schema.org is only valid on certain types (`Product`, `Place`, `QuantitativeValue`, etc.). It is NOT valid on `Article`, `Question`, or `Thing`. By using direct properties resolved via the JSON-LD context, AQA avoids using `additionalProperty` on types where it does not belong.

2. **Graceful degradation.** Validators and crawlers that do not understand the AQA context will silently ignore the AQA-specific properties. They won't cause errors — they simply won't be processed. The core schema.org structure (`Article`, `FAQPage`, `Question`, `Answer`, `dateCreated`, `dateModified`, `citation`, `author`) remains fully valid and functional.

### 9.2 Extending AQA

Third parties can extend the AQA specification by:

1. Defining additional properties in the `aqa:` namespace (submit a proposal via the GitHub repository)
2. Creating industry-specific profiles that mandate certain values (e.g., an "AQA-Legal" profile that requires specific citation types)
3. Adding properties via their own namespace alongside `aqa:` in the JSON-LD context array

---

## 10. Security and Privacy Considerations

### 10.1 Author Information

AQA Full requires per-question author information including professional credentials. Implementers SHOULD:

- Obtain consent from authors before publishing their professional details in structured data
- Provide only the level of detail necessary (professional title and a link, not personal contact information)
- Comply with applicable privacy regulations (GDPR, CCPA)

### 10.2 Source URLs

Citations and monitoring source URLs should be publicly accessible. Do not include:
- URLs behind authentication
- Internal document management system links
- URLs containing tokens or session identifiers

### 10.3 Changelog Content

Changelog descriptions should summarize changes factually. Avoid including:
- Internal business decisions or strategy
- Confidential client information
- Draft content that was rejected

---

## Appendix A: Complete JSON-LD Template

```json
{
  "@context": [
    "https://schema.org",
    "https://ailabsaudit.com/aqa/ns/context.jsonld"
  ],
  "@type": "Article",
  "headline": "YOUR_HEADLINE",
  "author": {
    "@type": "Person",
    "name": "YOUR_NAME",
    "jobTitle": "YOUR_TITLE",
    "url": "YOUR_URL",
    "sameAs": "YOUR_PROFILE_URL",
    "affiliation": {
      "@type": "Organization",
      "name": "YOUR_ORG"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "YOUR_ORG",
    "url": "YOUR_ORG_URL"
  },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "inLanguage": "fr",
  "about": {
    "@type": "Thing",
    "name": "YOUR_SECTOR_LABEL",
    "identifier": [
      {
        "@type": "PropertyValue",
        "propertyID": "NACE",
        "value": "YOUR_NACE_CODE"
      }
    ]
  },
  "updateFrequency": "monthly",
  "conformanceLevel": "full",
  "monitoringSources": [
    {
      "@type": "MonitoringSource",
      "name": "SOURCE_NAME",
      "url": "SOURCE_URL",
      "sourceType": "regulatory"
    }
  ],
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "YOUR_QUESTION",
        "dateCreated": "YYYY-MM-DD",
        "dateModified": "YYYY-MM-DD",
        "author": {
          "@type": "Person",
          "name": "AUTHOR_NAME",
          "jobTitle": "AUTHOR_TITLE"
        },
        "citation": [
          {
            "@type": "CreativeWork",
            "name": "SOURCE_TITLE",
            "url": "SOURCE_URL",
            "datePublished": "YYYY-MM-DD"
          }
        ],
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "YOUR_ANSWER"
        },
        "questionVersion": "1.0",
        "changelog": [
          {
            "@type": "ChangelogEntry",
            "changeDate": "YYYY-MM-DD",
            "changeDescription": "Initial publication",
            "changeSourceUrl": "SOURCE_URL",
            "changeVersionNote": "1.0"
          }
        ]
      }
    ]
  }
}
```

---

## Appendix B: Classification Code Systems

### NACE Rev. 2 (European Union)

| Code | Description |
|------|-------------|
| 69.20 | Accounting, bookkeeping and auditing activities; tax consultancy |
| 69.10 | Legal activities |
| 68.31 | Real estate agencies |
| 64.19 | Other monetary intermediation |
| 86.21 | General medical practice activities |

### NAF Rev. 2 (France)

NAF codes extend NACE with a letter suffix. Example: NACE 69.20 -> NAF 69.20Z.

### SIC (United States / United Kingdom)

| Code | Description |
|------|-------------|
| 7291 | Tax return preparation services |
| 8111 | Legal services |
| 6531 | Real estate agents and managers |
| 6022 | State commercial banks |

---

*AQA Specification v1.0.0-draft -- (c) 2026 AI Labs Solutions -- MIT License*
