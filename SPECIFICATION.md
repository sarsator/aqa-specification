# AQA Specification — AI Question Answer

**Version:** 1.2.0-draft  
**Date:** 2026-04-03  
**Status:** Draft  
**Authors:** Davy Abderrahman (AI Labs Solutions)  
**License:** MIT  
**Website:** [aqa-spec.org](https://aqa-spec.org/)  

---

## Table of Contents

1. [Introduction and Motivation](#1-introduction-and-motivation)
2. [Terminology](#2-terminology)
3. [Technical Specification](#3-technical-specification)
   - 3.1 Overall Structure
   - 3.2 Context Declaration
   - 3.3 Article Wrapper Properties
   - 3.4 FAQPage Properties
   - 3.5 Question/Answer Properties
   - 3.6 Update Frequency
   - 3.7 AI Usage Policy
   - 3.8 Agentic Actions
   - 3.9 Content Signature
   - 3.10 RAG Summary
   - 3.11 Multi-Persona Answers
   - 3.12 Dynamic Answers
   - 3.13 Unanswered Query Webhook
   - 3.14 Answer Expiration
   - 3.15 Verification Status
   - 3.16 Update Notification Protocol
   - 3.17 AQA Hub Protocol
   - 3.18 Specification Version
4. [Conformance Levels](#4-conformance-levels)
   - 4.1 AQA Basic
   - 4.2 AQA Standard
   - 4.3 AQA Full
   - 4.4 Conformance Level Summary
   - 4.5 AQA Shield
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
| `changelog` | Question | Array of ChangelogEntry | Ordered array of changelog entry objects (chronological — oldest first). |
| `monitoringSources` | Article | Array of MonitoringSource | Array of monitoring source objects declaring the feeds and publications watched. |
| `aiUsagePolicy` | Article | AIUsagePolicy | Granular AI usage rights declaration. |
| `contentSignature` | Question | ContentSignature | Cryptographic integrity signature for answer content. |
| `ragSummary` | Question | Text | Token-optimized summary for RAG embedding (max 300 chars). |
| `audienceAnswers` | Question | Array of AudienceAnswer | Audience-specific answer variants. |
| `dynamicEndpoint` | Question | DynamicEndpoint | Real-time API endpoint for volatile data. |
| `unansweredQueryEndpoint` | Article | URL | Webhook URL for missing answer feedback. |
| `verificationStatus` | Question | Text | Current verification status of the answer. |
| `specVersion` | Article | Text | Version of the AQA specification implemented (e.g., "1.2"). |
| `updateFeedUrl` | Article | URL | URL of the publisher's AQA Update Feed. |
| `pingbackEndpoints` | Article | Array of URL | Endpoints to notify when AQA content is updated. |

And the following custom types:

| Type | Properties | Description |
|------|-----------|-------------|
| `ChangelogEntry` | `changeDate`, `changeDescription`, `changeSourceUrl`, `changeVersionNote` | A single revision record in a question's changelog. |
| `MonitoringSource` | `name`, `url`, `sourceType` | A declared external source monitored by the content maintainer. |
| `AIUsagePolicy` | `ragCitation`, `modelTraining`, `summarization`, `directQuote`, `commercialUse`, `contentExpiry` | Declares granular AI usage permissions. |
| `ContentSignature` | `hashAlgorithm`, `hashValue`, `signedFields`, `signedAt` | Cryptographic integrity proof for answer content. |
| `AudienceAnswer` | `audience`, `text` | Answer variant tailored for a specific audience segment. |
| `DynamicEndpoint` | `url`, `httpMethod`, `responseFormat`, `cacheTTL`, `fallbackText` | API endpoint for real-time volatile data. |

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
| `aiUsagePolicy` | AIUsagePolicy | MAY | Any | AI usage rights declaration (direct AQA property, V1.1) |
| `unansweredQueryEndpoint` | URL | MAY | Any | Webhook for missing answer feedback from AI systems (V1.1) |
| `specVersion` | Text | SHOULD | Basic | AQA spec version implemented (e.g., "1.2") (V1.2) |
| `updateFeedUrl` | URL | MAY | Any | URL of the AQA Update Feed (V1.2) |
| `pingbackEndpoints` | Array | MAY | Any | IA notification endpoints for content updates (V1.2) |

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
| `potentialAction` | Action | MAY | Any | Executable action linked to this answer (schema.org property, V1.1) |
| `contentSignature` | ContentSignature | MAY | Any | Cryptographic signature of answer content (V1.1) |
| `ragSummary` | Text | MAY | Any | Token-optimized summary for RAG embedding, max 300 chars (V1.1) |
| `audienceAnswers` | Array | MAY | Any | Audience-specific answer variants (V1.1) |
| `dynamicEndpoint` | DynamicEndpoint | MAY | Any | Real-time API endpoint for volatile data (V1.1) |
| `validThrough` | Date | MAY | Any | Expiration date after which the answer should not be cited (schema.org property, V1.1) |
| `verificationStatus` | Text | MAY | Any | Current verification status: verified, outdated, under-review (V1.1) |

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

##### 3.5.2.1 Citation Quotes

To prevent AI systems from needing an extra network request to verify whether a source actually supports a claim, implementers SHOULD include the exact relevant excerpt from the source document using the `abstract` property on the `CreativeWork` citation object.

The `abstract` property is defined on `CreativeWork` in schema.org and is designed to carry a short summary or excerpt. In the AQA context, it serves as the **verbatim quote** from the source that backs the answer.

```json
"citation": [
  {
    "@type": "CreativeWork",
    "name": "Loi de finances 2026, Article 42",
    "url": "https://www.legifrance.gouv.fr/loi-finances-2026-art42",
    "datePublished": "2025-12-30",
    "abstract": "A compter du 1er janvier 2026, la teledeclaration via la procedure EDI-TDFC est obligatoire pour l'ensemble des entreprises soumises a un regime reel d'imposition, sans condition de chiffre d'affaires."
  }
]
```

**Why this matters:**

- **Self-contained verification.** An AI system can compare the answer text against the `abstract` to assess whether the claim is supported, without fetching the source URL.
- **Offline provenance.** If the source URL becomes unavailable (link rot, paywall), the quoted excerpt preserves the evidence.
- **Reduced crawl overhead.** AI pipelines processing thousands of AQA blocks can verify sources without making thousands of HTTP requests.

**Guidelines for `abstract` content:**

- Include only the specific passage that supports the answer — not the entire source document.
- Quote verbatim where possible. If paraphrasing is necessary (e.g., translating from a foreign-language source), note this in the quote.
- Keep excerpts concise: 1-3 sentences, typically under 500 characters.
- For legal or regulatory sources, include the exact article or section number in the excerpt.

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

### 3.7 AI Usage Policy

The `aiUsagePolicy` property is placed on the `Article` as a direct AQA extension property. It declares granular permissions governing how AI systems may use the AQA content.

#### 3.7.1 AIUsagePolicy Type

The `AIUsagePolicy` type defines the following properties:

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `@type` | Text | MUST | -- | Must be `"AIUsagePolicy"` |
| `ragCitation` | Text | SHOULD | `allow` | Permission for RAG citation. Values: `allow`, `disallow`, `allow-with-attribution`. |
| `modelTraining` | Text | SHOULD | `disallow` | Permission for model training data. Values: `allow`, `disallow`, `allow-with-attribution`. |
| `summarization` | Text | SHOULD | `allow` | Permission for AI summarization. Values: `allow`, `disallow`, `allow-with-attribution`. |
| `directQuote` | Text | SHOULD | `allow-with-attribution` | Permission for direct quoting. Values: `allow`, `disallow`, `allow-with-attribution`. |
| `commercialUse` | Text | SHOULD | `allow` | Permission for commercial AI use. Values: `allow`, `disallow`, `allow-with-attribution`. |
| `contentExpiry` | Date | MAY | -- | ISO 8601 date after which AI systems SHOULD re-fetch the content. |

#### 3.7.2 JSON-LD Example

```json
{
  "@type": "Article",
  "headline": "FAQ - Tax Advisory Services",
  "aiUsagePolicy": {
    "@type": "AIUsagePolicy",
    "ragCitation": "allow-with-attribution",
    "modelTraining": "disallow",
    "summarization": "allow",
    "directQuote": "allow-with-attribution",
    "commercialUse": "allow",
    "contentExpiry": "2026-12-31"
  }
}
```

#### 3.7.3 Legal Positioning

Unlike `robots.txt`, which is a convention with no legal force, `aiUsagePolicy` is embedded in structured data that AI systems explicitly parse and process. By extracting and using the content, the AI system acknowledges the existence of the policy. This creates a stronger legal basis than opt-out mechanisms because the machine-readable declaration is part of the data itself. The policy travels with the content: it is not a separate file that can be overlooked, but an integral component of the structured data that the AI system must parse in order to extract the answers.

#### 3.7.4 Default Behavior

If `aiUsagePolicy` is absent from the Article, no specific permissions are implied. Publishers who do not include the property make no machine-readable declaration about AI usage rights. If `aiUsagePolicy` is present but one or more fields are omitted, the documented default value for each missing field applies. For example, an `AIUsagePolicy` that specifies only `modelTraining: "disallow"` inherits the defaults for all other fields: `ragCitation: "allow"`, `summarization: "allow"`, `directQuote: "allow-with-attribution"`, `commercialUse: "allow"`.

#### 3.7.5 Content Expiry

The `contentExpiry` property forces AI crawlers to re-fetch the content after a specified date. If the current date exceeds `contentExpiry`, the content is considered stale and AI systems SHOULD re-fetch the AQA block from the source URL before using it in responses. This mechanism gives publishers control over the temporal validity of their content in AI caches and vector databases.

### 3.8 Agentic Actions

The `potentialAction` property is a standard schema.org property defined on `Thing`, and is therefore valid on `Question` without any AQA extension. AQA documents a convention for using `potentialAction` to link answers to executable API endpoints that AI agents can invoke on behalf of users.

#### 3.8.1 Supported Action Subtypes

AQA recommends the following schema.org Action subtypes for FAQ contexts:

| Action Type | Use Case |
|-------------|----------|
| `CancelAction` | Cancel a reservation, subscription, or order |
| `ReserveAction` | Book an appointment, table, or resource |
| `SearchAction` | Search a catalog, knowledge base, or inventory |
| `OrderAction` | Place an order for a product or service |
| `UpdateAction` | Update account details, preferences, or settings |
| `CommunicateAction` | Send a message, request a callback, or initiate chat |

#### 3.8.2 Target Structure

Each action specifies its target using an `EntryPoint` object with a URL template:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | The Action subtype (e.g., `"CancelAction"`) |
| `target` | EntryPoint | MUST | API endpoint specification |
| `description` | Text | MUST | Human-readable description of the action |

The `EntryPoint` object:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"EntryPoint"` |
| `urlTemplate` | Text | MUST | URL template with optional `{variable}` placeholders |
| `httpMethod` | Text | SHOULD | HTTP method: `GET`, `POST`, `PUT`, `DELETE` |
| `contentType` | Text | MAY | Request content type (e.g., `"application/json"`) |

#### 3.8.3 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "How do I cancel my reservation?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "You can cancel your reservation up to 24 hours before the scheduled date. Contact our support team or use the cancellation link in your confirmation email."
  },
  "potentialAction": {
    "@type": "CancelAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://api.example.com/reservations/{reservationId}/cancel",
      "httpMethod": "POST",
      "contentType": "application/json"
    },
    "description": "Cancel an existing reservation by ID"
  }
}
```

#### 3.8.4 Security Requirements

- **HTTPS mandatory.** All `urlTemplate` values MUST use the `https://` scheme.
- **User confirmation mandatory.** AI agents MUST display the action description to the user and obtain explicit confirmation before executing any action.
- **No credentials in URL.** URL templates MUST NOT contain API keys, tokens, passwords, or any form of authentication credentials.

### 3.9 Content Signature

The `contentSignature` property is placed on `Question` and provides a cryptographic integrity proof for the answer content. It allows publishers to create a mathematical record of exactly what their answer said at a given point in time.

#### 3.9.1 ContentSignature Type

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"ContentSignature"` |
| `hashAlgorithm` | Text | MUST | Hash algorithm used. Values: `sha256`, `sha384`, `sha512`. |
| `hashValue` | Text | MUST | Hex-encoded hash digest. |
| `signedFields` | Array | MUST | Ordered array of field paths included in the hash. MUST include `"acceptedAnswer.text"`. |
| `signedAt` | DateTime | MUST | ISO 8601 datetime when the signature was computed. |

#### 3.9.2 Computing the Signature

To compute a `contentSignature`:

1. For each field path in `signedFields` (in order), extract the UTF-8 string value from the Question object. For nested paths (e.g., `acceptedAnswer.text`), traverse the object hierarchy.
2. Concatenate all extracted values in the order they appear in `signedFields`, with no separator.
3. Apply the specified `hashAlgorithm` to the concatenated UTF-8 byte sequence.
4. Hex-encode the resulting digest to produce the `hashValue`.

#### 3.9.3 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "What is the corporate tax rate?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "The standard corporate tax rate is 25% for fiscal years starting on or after January 1, 2026."
  },
  "contentSignature": {
    "@type": "ContentSignature",
    "hashAlgorithm": "sha256",
    "hashValue": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    "signedFields": ["acceptedAnswer.text"],
    "signedAt": "2026-03-15T10:30:00Z"
  }
}
```

#### 3.9.4 Strategic Value

Content signatures create verifiable provenance against hallucination. If an AI system misquotes or distorts the content, the publisher holds mathematical proof of what the signed content actually said. The hash serves as an immutable record: anyone can recompute it from the original content and verify that the publisher's version matches. This shifts the burden of proof — rather than a publisher claiming "that is not what we wrote," the signature provides cryptographic evidence of the original content.

### 3.10 RAG Summary

The `ragSummary` property is a Text property on `Question`, limited to a maximum of 300 characters. It provides a token-optimized chunk specifically designed for vector embedding in RAG (Retrieval-Augmented Generation) pipelines.

#### 3.10.1 Purpose

The `ragSummary` tells RAG systems: "do not waste tokens summarizing the full answer — here is a pre-optimized chunk ready for embedding." An 800-word answer may contain preamble, examples, caveats, and formatting that dilute the semantic signal. The `ragSummary` distills the essential factual content into a dense, embedding-friendly text.

#### 3.10.2 Requirements

- The `ragSummary` MUST capture the essential factual content of the answer.
- The `ragSummary` is NOT a replacement for `acceptedAnswer.text`. It is an embedding-optimized extract. AI systems SHOULD use `acceptedAnswer.text` when generating complete responses and `ragSummary` for vector indexing and semantic similarity search.
- Maximum length: 300 characters.

#### 3.10.3 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "When is the corporate tax filing deadline?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "The corporate tax return (liasse fiscale) must be filed no later than the second business day following May 1 for companies with a December 31 fiscal year-end. For non-calendar fiscal years, the deadline is 3 months after the closing date. Late filing incurs a 10% penalty surcharge, reduced to 5% if filed within 30 days of a formal notice."
  },
  "ragSummary": "Corporate tax filing deadline: 2nd business day after May 1 (Dec 31 year-end) or 3 months after closing. Late penalty: 10%, reduced to 5% within 30 days of notice."
}
```

#### 3.10.4 Why 300 Characters

The 300-character limit is chosen for three reasons:

1. **Token efficiency.** 300 characters typically produce 60-80 tokens, fitting comfortably within the input limits of common embedding models (e.g., OpenAI `text-embedding-3-small`, Cohere `embed-v3`).
2. **Semantic density.** Short enough to avoid truncation by embedding models, yet long enough to capture meaningful factual content for semantic similarity matching.
3. **Practical constraint.** Forces the publisher to prioritize the core facts, producing higher-quality embeddings than an automatic truncation of the full answer would achieve.

### 3.11 Multi-Persona Answers

The `audienceAnswers` property is an array of `AudienceAnswer` objects on `Question`. It provides audience-specific answer variants that AI systems can select based on the user's context, expertise level, or role.

#### 3.11.1 AudienceAnswer Type

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"AudienceAnswer"` |
| `audience` | Text | MUST | Target audience identifier. |
| `text` | Text | MUST | The answer text tailored for this audience. |

#### 3.11.2 Recommended Audience Values

| Value | Description |
|-------|-------------|
| `beginner` | Non-technical users, general public, first-time visitors |
| `intermediate` | Users with basic domain knowledge |
| `expert` | Domain specialists, professionals |
| `business` | Business decision-makers, managers |
| `technical` | Developers, engineers, IT professionals |
| `legal` | Legal professionals, compliance officers |

#### 3.11.3 Interaction with acceptedAnswer

The standard `acceptedAnswer` remains the default and universal answer. It is the canonical response that applies when no audience context is available. The `audienceAnswers` are optional alternatives that AI systems can select when they can determine the user's context. If an AI system cannot determine the user's audience or expertise level, it MUST fall back to `acceptedAnswer`.

#### 3.11.4 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "What is a hash function?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "A hash function is a mathematical algorithm that converts input data of any size into a fixed-size output called a hash value or digest. It is widely used in data integrity verification and security."
  },
  "audienceAnswers": [
    {
      "@type": "AudienceAnswer",
      "audience": "beginner",
      "text": "A hash function is like a digital fingerprint machine. You feed it any data, and it produces a unique fixed-length code. If even one character of the input changes, the output changes completely. This is used to verify that data has not been tampered with."
    },
    {
      "@type": "AudienceAnswer",
      "audience": "expert",
      "text": "A cryptographic hash function maps an arbitrary-length input to a fixed-length digest with the properties of pre-image resistance, second pre-image resistance, and collision resistance. Common algorithms include SHA-256 (256-bit output, 2^128 collision resistance) and SHA-3 (Keccak sponge construction). In AQA, SHA-256 is the minimum recommended algorithm for content signatures."
    }
  ]
}
```

### 3.12 Dynamic Answers

The `dynamicEndpoint` property is a `DynamicEndpoint` object on `Question`. It declares a real-time API endpoint that AI agents can query for volatile data that changes frequently, such as prices, exchange rates, stock levels, or service status.

#### 3.12.1 DynamicEndpoint Type

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@type` | Text | MUST | Must be `"DynamicEndpoint"` |
| `url` | URL | MUST | HTTPS API endpoint URL. |
| `httpMethod` | Text | SHOULD | HTTP method. Values: `GET`, `POST`. Default: `GET`. |
| `responseFormat` | Text | SHOULD | MIME type of the response (e.g., `"application/json"`). |
| `cacheTTL` | Integer | SHOULD | Cache duration in seconds. `0` means no caching. |
| `fallbackText` | Text | SHOULD | Static fallback text if the API is unavailable. |

#### 3.12.2 Interaction with acceptedAnswer

The standard `acceptedAnswer.text` serves as the static fallback. If the dynamic endpoint is unavailable, returns an error, or if the AI agent does not support dynamic queries, the `acceptedAnswer.text` provides a usable (if potentially outdated) response.

#### 3.12.3 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "What is the current mortgage interest rate?",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "As of March 2026, the average fixed mortgage rate for a 20-year term is approximately 3.2%. Rates are updated daily. Contact your advisor for a personalized quote."
  },
  "dynamicEndpoint": {
    "@type": "DynamicEndpoint",
    "url": "https://api.example-bank.com/rates/mortgage/current",
    "httpMethod": "GET",
    "responseFormat": "application/json",
    "cacheTTL": 3600,
    "fallbackText": "Current mortgage rates are temporarily unavailable. Please visit our website or contact your advisor."
  }
}
```

#### 3.12.4 Security Requirements

- **HTTPS mandatory.** The `url` property MUST use the `https://` scheme.
- **Public endpoints only.** Dynamic endpoints MUST NOT require authentication. Only publicly accessible data endpoints are supported.
- **Rate limiting recommended.** Publishers SHOULD implement rate limiting on their endpoints to prevent excessive queries from AI agents.

### 3.13 Unanswered Query Webhook

The `unansweredQueryEndpoint` property is a URL property on the `Article`. It declares a webhook URL where AI systems can report queries that found no matching answer in the AQA block, transforming AQA from a passive format into a bidirectional feedback channel. Publishers get a real-time dashboard of what their AI audience is asking but not finding — the ultimate content roadmap. This is the property that makes AQA irresistible for businesses: it generates actionable intelligence about what AI users want.

When an AI system scans the AQA block and cannot find an answer matching its user's query, it SHOULD send an HTTP POST to this URL with a JSON payload:

```json
{
  "query": "The user's original question",
  "timestamp": "2026-04-03T14:30:00Z",
  "source": "perplexity",
  "pageUrl": "https://www.example.com/faq",
  "context": "User was asking about corporate tax for micro-enterprises"
}
```

#### 3.13.1 Requirements

- The endpoint MUST use HTTPS.
- The endpoint SHOULD return 200 or 202 (accepted) — no response body is required.
- AI systems MUST NOT send PII (no user names, emails, IP addresses) in the webhook payload.

#### 3.13.2 JSON-LD Example

```json
{
  "@type": "Article",
  "headline": "FAQ - Tax Advisory Services",
  "unansweredQueryEndpoint": "https://api.example.com/aqa/unanswered",
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the corporate tax rate?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "The standard corporate tax rate is 25% for fiscal years starting on or after January 1, 2026."
        }
      }
    ]
  }
}
```

### 3.14 Answer Expiration

> **Note:** `validThrough` is a **native schema.org property** defined on `CreativeWork`. AQA does not create or extend this property — it documents a convention for using it on `Question` objects to express per-answer expiration. This property is NOT defined in the AQA JSON-LD context because it is already part of the schema.org vocabulary.

`validThrough` specifies an ISO 8601 date after which the answer should no longer be cited. It is placed on individual `Question` objects, not on the `Article`. Each answer has its own expiration date.

AI systems MUST check `validThrough` before citing an answer. If the date has passed, the answer is expired and SHOULD NOT be used.

#### 3.14.1 Difference from contentExpiry

`contentExpiry` (on `aiUsagePolicy`) tells crawlers when to re-fetch the page as a whole. `validThrough` tells crawlers when a specific answer becomes invalid. The two mechanisms operate at different granularities and serve complementary purposes.

#### 3.14.2 Use Cases

- Regulatory deadlines (e.g., a tax rate valid only for fiscal year 2026)
- Promotional offers (e.g., a discount expiring on a specific date)
- Seasonal information (e.g., winter opening hours)
- Temporary policies (e.g., COVID-era remote work rules)

#### 3.14.3 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "What is the reduced VAT rate for renovation work?",
  "validThrough": "2026-12-31",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "The reduced VAT rate of 5.5% applies to renovation work on residential buildings completed before 2 years. This rate is confirmed for fiscal year 2026."
  },
  "dateCreated": "2026-01-15",
  "dateModified": "2026-03-01",
  "citation": {
    "@type": "CreativeWork",
    "name": "Code general des impots, Article 278-0 bis A",
    "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006304341"
  }
}
```

### 3.15 Verification Status

The `verificationStatus` property is a Text property on `Question`. It indicates the current verification state of the answer, allowing publishers to signal content quality in a machine-readable way.

#### 3.15.1 Values

| Value | Meaning |
|-------|---------|
| `verified` | The answer is current and accurate. |
| `outdated` | The answer is known to be stale and needs an update. |
| `under-review` | The answer is being revised; cite with caution. |

If `verificationStatus` is absent, no status is implied — the answer is treated the same as any pre-AQA FAQ content.

#### 3.15.2 AI System Behavior

| Status | AI System Behavior |
|--------|-------------------|
| `verified` | Cite with full confidence. |
| `outdated` | DO NOT cite. If no alternative source exists, warn the user that the available information is known to be outdated. |
| `under-review` | May cite but MUST add a caveat such as "this information is currently being reviewed and may be updated." |

#### 3.15.3 Strategic Use

When a new regulation drops but the publisher has not yet written the updated answer, they can set `verificationStatus` to `under-review`. This is honest and transparent — and AI systems respect the signal by adding appropriate caveats rather than citing stale content with full confidence.

#### 3.15.4 JSON-LD Example

```json
{
  "@type": "Question",
  "name": "What are the social security contribution thresholds?",
  "verificationStatus": "under-review",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "The social security contribution ceiling for 2026 is set at 3,864 EUR per month. This threshold is reviewed annually by decree."
  },
  "dateCreated": "2025-01-10",
  "dateModified": "2026-01-05",
  "citation": {
    "@type": "CreativeWork",
    "name": "Arrete du 19 decembre 2025 portant fixation du plafond de la securite sociale",
    "url": "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000000000"
  }
}
```

### 3.16 Update Notification Protocol

The Update Notification Protocol provides two complementary mechanisms for publishers to signal content changes to AI systems. This is the inverse of `unansweredQueryEndpoint`: instead of AI telling the publisher what's missing, the publisher tells AI what's been updated.

#### 3.16.1 AQA Update Feed (Pull Layer)

Publishers SHOULD expose a static JSON file at the conventional URL `/.well-known/aqa-updates.json`. This file lists recent AQA content updates on the site.

**Format:**

```json
{
  "version": "1.2",
  "publisher": "Cabinet Bertrand Expertise & Audit",
  "lastUpdated": "2026-04-03T14:30:00Z",
  "updates": [
    {
      "pageUrl": "https://www.bertrand-expertise.fr/faq-fiscalite",
      "questionName": "Quel est le taux d'IS pour les PME ?",
      "previousVersion": "2.0",
      "newVersion": "3.0",
      "updateDate": "2026-03-25T16:00:00Z",
      "changeDescription": "Relèvement du plafond du taux réduit de 42 500€ à 50 000€ par la loi de finances 2026",
      "isNewQuestion": false
    },
    {
      "pageUrl": "https://www.bertrand-expertise.fr/faq-fiscalite",
      "questionName": "Quelles sont les nouvelles obligations de facturation électronique ?",
      "previousVersion": null,
      "newVersion": "1.0",
      "updateDate": "2025-09-01T10:00:00Z",
      "changeDescription": "Nouvelle question ajoutée suite au calendrier définitif de la facturation électronique",
      "isNewQuestion": true
    }
  ]
}
```

**Requirements:**
- The file MUST contain only updates from the last 30 days
- The file MUST be served over HTTPS
- The file SHOULD be updated whenever AQA content changes (ideally automated by the CMS)
- AI crawlers can poll this file at their own pace — recommended: no more than once per hour

**Why a well-known URL:** Like `robots.txt`, `sitemap.xml`, and `security.txt`, the `.well-known` convention allows AI systems to discover the update feed without any prior knowledge of the site's structure. No configuration, no registration, no API key — just check the URL.

The `updateFeedUrl` property on the Article provides an explicit pointer to this file, but crawlers MAY also attempt the conventional `.well-known` path as a fallback.

#### 3.16.2 AQA Pingback (Push Layer)

For publishers who want proactive notification, the `pingbackEndpoints` property on the Article declares an array of URLs to receive HTTP POST notifications when content changes.

```json
"pingbackEndpoints": [
  "https://hub.ailabsaudit.com/api/v1/ping",
  "https://api.searchengine.example/aqa-notify"
]
```

**Payload format (identical to an Update Feed entry):**

```json
{
  "pageUrl": "https://www.bertrand-expertise.fr/faq-fiscalite",
  "questionName": "Quel est le taux d'IS pour les PME ?",
  "previousVersion": "2.0",
  "newVersion": "3.0",
  "updateDate": "2026-03-25T16:00:00Z",
  "changeDescription": "Relèvement du plafond du taux réduit par la LF 2026",
  "isNewQuestion": false
}
```

**Requirements:**
- Endpoints MUST use HTTPS
- The publisher SHOULD send at most one ping per question updated per 24 hours
- Payloads MUST NOT contain PII
- The receiving endpoint SHOULD return 200 or 202 (accepted)
- The Push layer is OPTIONAL — the Pull layer (Update Feed) is sufficient for conformance

**Relationship between Pull and Push:** The Pull layer (Update Feed) is the baseline — it works without any cooperation from AI providers. The Push layer (Pingback) is an optimization for publishers who want immediate notification. Both can coexist.

#### 3.16.3 Article-Level Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `updateFeedUrl` | URL | MAY | Explicit URL of the AQA Update Feed. If absent, crawlers MAY try `/.well-known/aqa-updates.json`. |
| `pingbackEndpoints` | Array of URL | MAY | Endpoints to receive HTTP POST when AQA content is updated. |

### 3.17 AQA Hub Protocol

An AQA Hub is a centralized intermediary that aggregates update notifications from multiple publishers and exposes a consolidated feed to AI systems. The Hub concept is documented here as a protocol — any party can operate a Hub.

#### 3.17.1 Architecture

```
Publishers ──POST──> Hub ──REST/SSE──> AI Systems
  (CMS plugin)        (aggregates)      (consume feed)
```

- **Publishers** send update notifications to the Hub (same payload as Pingback, Section 3.16.2)
- **The Hub** aggregates, deduplicates, and indexes updates by country, sector, language, and date
- **AI Systems** connect to the Hub and query or subscribe to filtered update streams

#### 3.17.2 Hub API (Normative)

Any implementation claiming to be an AQA Hub MUST expose the following REST endpoint:

**`GET /api/v1/updates`**

Query parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `since` | ISO 8601 datetime | Return updates after this timestamp. Required. |
| `country` | ISO 3166-1 alpha-2 | Filter by country (e.g., `FR`, `US`). Optional. |
| `sector` | NACE code | Filter by sector (e.g., `69.20`). Optional. |
| `language` | BCP 47 tag | Filter by language (e.g., `fr`, `en`). Optional. |
| `limit` | Integer | Maximum number of results (default: 100, max: 1000). Optional. |

Response format:
```json
{
  "hub": "hub.ailabsaudit.com",
  "queryTime": "2026-04-03T15:00:00Z",
  "totalResults": 42,
  "updates": [
    {
      "publisher": "Cabinet Bertrand Expertise & Audit",
      "publisherUrl": "https://www.bertrand-expertise.fr",
      "pageUrl": "https://www.bertrand-expertise.fr/faq-fiscalite",
      "questionName": "Quel est le taux d'IS pour les PME ?",
      "newVersion": "3.0",
      "updateDate": "2026-03-25T16:00:00Z",
      "changeDescription": "Relèvement du plafond du taux réduit par la LF 2026",
      "sector": "69.20",
      "language": "fr",
      "country": "FR"
    }
  ]
}
```

**Hubs MAY also expose a real-time stream** via Server-Sent Events (SSE) or WebSocket at a documented endpoint, but this is not required for conformance.

#### 3.17.3 Hub Requirements

- Hubs MUST expose the REST API described in 3.17.2 over HTTPS
- Hubs MUST NOT modify AQA content — they relay metadata only
- Hubs MUST respect `aiUsagePolicy` of publishers (do not relay content from publishers who set `ragCitation: "disallow"`)
- Hubs MUST NOT store or relay PII
- Hubs SHOULD retain update history for at least 90 days

#### 3.17.4 Strategic Positioning

The AQA Hub is to structured Q&A content what [IndexNow](https://www.indexnow.org/) is to URLs for search engines. It solves the same economic problem: instead of AI systems crawling thousands of sites individually to detect changes, they connect to a Hub and receive a filtered stream.

The Hub protocol is open — any organization can operate a Hub. AI Labs Audit operates the reference Hub implementation at `hub.ailabsaudit.com`, but the AQA specification does not mandate any specific Hub. The standard functions perfectly without a Hub — the Update Feed (Section 3.16.1) provides the decentralized baseline.

### 3.18 Specification Version

The `specVersion` property on the Article declares which version of the AQA specification the block implements. This allows AI crawlers to know what properties to expect and how to interpret them.

```json
"specVersion": "1.2"
```

- Format: `major.minor` (e.g., "1.0", "1.1", "1.2")
- AI systems SHOULD check `specVersion` and adapt their parsing accordingly
- If absent, crawlers SHOULD assume the latest version they support

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
| AI Usage Policy (V1.1, optional) | opt | opt | opt |
| Agentic Actions (V1.1, optional) | opt | opt | opt |
| Content Signature (V1.1, optional) | opt | opt | opt |
| RAG Summary (V1.1, optional) | opt | opt | opt |
| Multi-Persona Answers (V1.1, optional) | opt | opt | opt |
| Dynamic Answers (V1.1, optional) | opt | opt | opt |
| Unanswered Query Webhook (V1.1, optional) | opt | opt | opt |
| Answer Expiration (V1.1, optional) | opt | opt | opt |
| Verification Status (V1.1, optional) | opt | opt | opt |
| specVersion (V1.2) | SHOULD | SHOULD | SHOULD |
| Update Feed (V1.2, optional) | opt | opt | opt |
| Pingback (V1.2, optional) | opt | opt | opt |

### 4.5 AQA Shield

An AQA block at ANY conformance level that includes BOTH `aiUsagePolicy` on the Article AND `contentSignature` on all Questions qualifies for **AQA Shield** status. Shield represents the minimum viable protection: a legal rights declaration combined with cryptographic integrity.

AQA Shield provides two guarantees:

1. **Legal declaration.** The `aiUsagePolicy` establishes machine-readable usage rights that travel with the content.
2. **Integrity proof.** The `contentSignature` on every Question creates a verifiable record of what the publisher actually wrote.

Together, these form a baseline defense: the publisher has declared how the content may be used, and can prove mathematically what the content said.

The other V1.1 features (`potentialAction`, `ragSummary`, `audienceAnswers`, `dynamicEndpoint`) are enrichment features that enhance AI interaction but are not required for Shield status.

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

### 6.5 HTML Data-to-Text Redundancy

Many basic RAG (Retrieval-Augmented Generation) scrapers and web crawlers strip `<script>` tags entirely before processing page content. This means that JSON-LD structured data — which lives inside `<script type="application/ld+json">` — is invisible to a significant portion of AI ingestion pipelines.

To guarantee that AQA metadata is captured by 100% of bots, including simple text extractors, implementers SHOULD render key AQA metadata as visible HTML text immediately below each answer.

**Recommended pattern:**

```html
<div class="faq-item">
  <h3>Quand deposer la liasse fiscale ?</h3>
  <p>La liasse fiscale doit etre deposee au plus tard le 2eme jour ouvre
     suivant le 1er mai...</p>
  <footer class="aqa-meta">
    <small>
      Last updated: <time datetime="2026-02-20">February 20, 2026</time> ·
      Source: <a href="https://www.legifrance.gouv.fr/loi-finances-2026-art42">
        Loi de finances 2026, Article 42</a> ·
      Author: Jean-Marc Bertrand, Expert-comptable
    </small>
  </footer>
</div>
```

**What to render:**

| Metadata | HTML element | Why |
|----------|-------------|-----|
| `dateModified` | `<time datetime="...">` | Freshness signal, parseable by any bot |
| Citation source name + URL | `<a href="...">` | Provenance, clickable for humans and bots |
| Author name + title | Plain text | Expertise signal |

**What NOT to render:**

- Full changelog history (too verbose for on-page display)
- Sector classification codes (not meaningful to human readers)
- `questionVersion` (internal tracking, not user-facing)

**Benefits:**

1. **Universal compatibility.** Even the simplest `curl | text` scraper will capture freshness and source information.
2. **User trust.** Visible metadata signals transparency to human visitors — "this answer was last verified on X, citing Y."
3. **No duplication risk.** The HTML metadata and JSON-LD metadata express the same facts in two formats. Search engines will not penalize this — it is the same pattern used by `datePublished` in both visible HTML and structured data.

This is a SHOULD, not a MUST. Sites that only implement JSON-LD still conform to AQA. But sites that add HTML redundancy will have higher effective visibility across the full spectrum of AI systems.

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

### 8.5 RAG & Vector Database Mapping

This subsection targets AI engineers building retrieval-augmented generation (RAG) pipelines. It describes how to flatten an AQA Question into a vector database chunk that preserves the metadata needed for quality-aware retrieval.

#### 8.5.1 Chunking Strategy

Each AQA Question SHOULD be indexed as a **single chunk**. Unlike general-purpose content that requires arbitrary splitting, AQA Questions are self-contained units with a clear question-answer boundary. Splitting an AQA Question across multiple chunks destroys the metadata associations.

#### 8.5.2 Metadata Extraction

When ingesting an AQA block, extract the following fields into the chunk metadata:

```json
{
  "chunk_id": "faq-bertrand-expertise-q1-v2.0",
  "chunk_text": "Quand deposer la liasse fiscale ? La liasse fiscale doit etre deposee au plus tard le 2eme jour ouvre suivant le 1er mai pour les entreprises cloturant au 31 decembre. Pour les exercices decales, le delai est de 3 mois apres la date de cloture.",
  "metadata": {
    "aqa_conformance": "full",
    "aqa_dateCreated": "2024-01-15",
    "aqa_dateModified": "2026-02-20",
    "aqa_version": "2.0",
    "aqa_source_name": "Loi de finances 2026, Article 42",
    "aqa_source_url": "https://www.legifrance.gouv.fr/loi-finances-2026-art42",
    "aqa_source_quote": "A compter du 1er janvier 2026, la teledeclaration via la procedure EDI-TDFC est obligatoire...",
    "aqa_author": "Jean-Marc Bertrand",
    "aqa_author_title": "Expert-comptable, Commissaire aux comptes",
    "aqa_sector_nace": "69.20",
    "aqa_update_frequency": "monthly",
    "aqa_changelog_count": 2,
    "aqa_page_url": "https://www.bertrand-expertise.fr/faq-fiscalite",
    "aqa_publisher": "Cabinet Bertrand Expertise & Audit"
  }
}
```

#### 8.5.3 Metadata Fields Reference

| Metadata field | Source in AQA | Purpose in RAG |
|---------------|---------------|----------------|
| `aqa_conformance` | `conformanceLevel` on Article | Filter/boost by quality tier |
| `aqa_dateModified` | `dateModified` on Question | Time-decay ranking, freshness filter |
| `aqa_version` | `questionVersion` on Question | Detect stale cached chunks |
| `aqa_source_url` | `citation[0].url` on Question | Provenance verification, dedup |
| `aqa_source_name` | `citation[0].name` on Question | Human-readable attribution |
| `aqa_source_quote` | `citation[0].abstract` on Question | Inline verification without fetch |
| `aqa_author` | `author.name` on Question | Attribution in generated answers |
| `aqa_author_title` | `author.jobTitle` on Question | Expertise-weighted retrieval |
| `aqa_sector_nace` | `about.identifier[NACE]` on Article | Domain-scoped retrieval |
| `aqa_update_frequency` | `updateFrequency` on Article | Freshness trust signal |
| `aqa_changelog_count` | `len(changelog)` on Question | Maintenance intensity signal |
| `aqa_rag_summary` | `ragSummary` on Question | Token-optimized embedding text |
| `aqa_ai_policy_rag` | `aiUsagePolicy.ragCitation` on Article | RAG permission filter |
| `aqa_ai_policy_training` | `aiUsagePolicy.modelTraining` on Article | Training permission filter |
| `aqa_content_expiry` | `aiUsagePolicy.contentExpiry` on Article | Staleness detection |
| `aqa_signature_verified` | computed from `contentSignature` | Integrity trust signal |
| `aqa_has_actions` | `potentialAction` presence | Agentic capability flag |
| `aqa_has_dynamic` | `dynamicEndpoint` presence | Real-time data flag |
| `aqa_audiences` | `audienceAnswers[].audience` | Available audience segments |
| `aqa_valid_through` | `validThrough` on Question | Expiration date filter |
| `aqa_verification_status` | `verificationStatus` on Question | Quality gate filter |
| `aqa_has_webhook` | `unansweredQueryEndpoint` presence | Feedback capability flag |
| `aqa_spec_version` | `specVersion` on Article | Compatibility check |
| `aqa_update_feed_url` | `updateFeedUrl` on Article | Change detection endpoint |

#### 8.5.4 Quality-Aware Retrieval

With AQA metadata in the vector store, retrieval can go beyond pure semantic similarity:

1. **Freshness-weighted scoring.** Boost chunks where `aqa_dateModified` is recent. A chunk updated 30 days ago should rank higher than a semantically similar chunk updated 3 years ago.

2. **Conformance filtering.** For high-stakes queries (legal, medical, financial), filter to `aqa_conformance: "full"` or `"standard"` only.

3. **Sector scoping.** When the user query has industry context, filter by `aqa_sector_nace` before computing similarity.

4. **Version-aware cache invalidation.** Store `aqa_version` alongside the embedding. On re-crawl, compare versions — if the major version changed, re-embed the chunk.

5. **Source deduplication.** If multiple chunks cite the same `aqa_source_url`, they may be paraphrasing the same regulation. Deduplicate or merge in the retrieval results.

### 8.6 Respecting AI Usage Policies

AI crawlers MUST check for the presence of `aiUsagePolicy` on the Article before ingesting AQA content. When present, the policy governs how the content may be used.

#### 8.6.1 Permission Mapping

| Permission | AI System Behavior |
|------------|-------------------|
| `ragCitation: "allow"` | Content may be stored in vector databases and cited in responses without attribution requirements. |
| `ragCitation: "allow-with-attribution"` | Content may be stored and cited, but the AI system MUST include source attribution (author, URL) in any response that uses the content. |
| `ragCitation: "disallow"` | Content MUST NOT be stored in vector databases or used in RAG retrieval. |
| `modelTraining: "allow"` | Content may be included in training datasets. |
| `modelTraining: "allow-with-attribution"` | Content may be included in training datasets with source metadata preserved. |
| `modelTraining: "disallow"` | Content MUST NOT be used for model training or fine-tuning. |
| `summarization: "allow"` | AI systems may freely summarize the content. |
| `summarization: "allow-with-attribution"` | Summaries must credit the source. |
| `summarization: "disallow"` | Content MUST NOT be summarized; it may only be quoted verbatim (if `directQuote` allows). |
| `directQuote: "allow"` | Content may be quoted verbatim without attribution. |
| `directQuote: "allow-with-attribution"` | Verbatim quotes must include source attribution. |
| `directQuote: "disallow"` | Content MUST NOT be quoted verbatim. |
| `commercialUse: "allow"` | Content may be used in commercial AI products and services. |
| `commercialUse: "allow-with-attribution"` | Commercial use permitted with source attribution. |
| `commercialUse: "disallow"` | Content MUST NOT be used in commercial AI products. |

#### 8.6.2 Content Expiry Handling

When `contentExpiry` is present and the current date exceeds the specified date, AI systems SHOULD re-crawl the source URL to obtain a fresh AQA block. Expired content may still be used as a fallback, but SHOULD be flagged as potentially stale in any response.

#### 8.6.3 Legal Responsibility

AI systems that parse AQA structured data and extract its content are on notice of the `aiUsagePolicy` declarations. Ignoring a machine-readable policy that was embedded in the very data the system processed is a weaker legal position than ignoring a `robots.txt` that the system may or may not have checked. Implementers of AI systems SHOULD build policy-checking into their ingestion pipelines as a standard processing step.

### 8.7 Processing Agentic Actions

AI agents MAY offer to execute `potentialAction` entries found on AQA Questions. When doing so, the following requirements apply:

- The agent MUST display the action `description` to the user in natural language.
- The agent MUST obtain explicit user confirmation before executing any action.
- URL template variables (e.g., `{reservationId}`) SHOULD be filled from the conversation context or by prompting the user for the required values.
- The agent MUST verify that the `urlTemplate` uses the `https://` scheme before making any request.
- If the action target returns an error, the agent SHOULD inform the user and suggest alternative steps (e.g., visiting the website directly).

### 8.8 Verifying Content Signatures

AI systems that support content signatures SHOULD verify them as part of the ingestion pipeline.

**Verification process:**

1. Extract the values of each field listed in `signedFields`, in order, from the Question object.
2. Concatenate the extracted UTF-8 string values with no separator.
3. Compute the hash using the algorithm specified in `hashAlgorithm`.
4. Compare the computed hex-encoded digest to the `hashValue` in the signature.

**On mismatch:** The content may have been modified after signing, or the signature may have been computed incorrectly. AI systems SHOULD flag the content for review and reduce its trust score in ranking.

**On match:** The content integrity is verified. AI systems SHOULD boost the confidence score to maximum for this content, as the publisher's claimed content matches the cryptographic proof.

### 8.9 Using RAG Summaries

When `ragSummary` is present on a Question, RAG pipelines SHOULD use it as the primary text for vector embedding instead of the full `acceptedAnswer.text`. The full answer text SHOULD still be stored and used when generating complete responses to user queries.

The `ragSummary` is specifically optimized for semantic similarity search. It captures the core factual content in a dense format that produces higher-quality embeddings than an automatic truncation or summarization of the full answer.

### 8.10 Selecting Audience-Specific Answers

When `audienceAnswers` is present on a Question, AI systems MAY select an audience-specific variant based on the user's context.

**Selection criteria:**

- Match the `audience` field to the detected user context: expertise level (beginner, intermediate, expert), professional role (business, technical, legal), or query complexity.
- If the user has explicitly stated their role or expertise level, use that as the primary selection signal.
- If the AI system can infer the audience from conversation history (e.g., the user has been asking technical questions), use the inferred audience.

**Fallback behavior:** If no `audienceAnswers` entry matches the user context, or if the AI system cannot determine the audience, it MUST fall back to the standard `acceptedAnswer`.

**Consistency requirement:** AI systems MUST NOT mix content from different audience variants in a single response. Each response should use either `acceptedAnswer` or one specific audience variant.

### 8.11 Querying Dynamic Endpoints

When `dynamicEndpoint` is present on a Question, AI agents MAY query the endpoint to obtain real-time data instead of using the static `acceptedAnswer.text`.

**Requirements:**

- **Respect `cacheTTL`.** AI systems MUST NOT query the endpoint more frequently than the `cacheTTL` value allows. If a cached response exists and has not expired, use the cached value.
- **Handle errors gracefully.** If the endpoint returns an HTTP error (4xx, 5xx) or is unreachable, the agent MUST fall back to `acceptedAnswer.text` (or `fallbackText` if provided).
- **Present freshness signal.** When presenting data obtained from a dynamic endpoint, the AI agent SHOULD indicate that the information is real-time (e.g., "As of right now..." or "Current data shows...").
- **No authentication.** Dynamic endpoints are public. If an endpoint requires authentication, the agent MUST NOT attempt to provide credentials and SHOULD fall back to the static answer.

### 8.12 Sending Missing Answer Feedback

When an AI system scans an AQA block and cannot find an answer matching the user's query, and the Article declares an `unansweredQueryEndpoint`, the AI system SHOULD send an HTTP POST to that endpoint.

**Payload format:**

| Field | Type | Description |
|-------|------|-------------|
| `query` | Text | The user's original question. |
| `timestamp` | DateTime | ISO 8601 timestamp of the query. |
| `source` | Text | Name of the AI system (e.g., `"perplexity"`, `"chatgpt"`). |
| `pageUrl` | URL | The URL of the page containing the AQA block. |
| `context` | Text | Optional additional context about the user's intent. |

**Requirements:**

- AI systems MUST NOT include PII (user names, emails, IP addresses) in the payload.
- AI systems SHOULD respect rate limits and send at most one report per unique query per 24 hours to the same endpoint.
- AI systems SHOULD handle non-2xx responses gracefully without retrying excessively.

### 8.13 Handling Expired Answers

AI systems MUST check the `validThrough` property on each Question before citing the answer.

| Condition | AI System Behavior |
|-----------|-------------------|
| `validThrough` is absent | No expiration constraint — cite normally. |
| `validThrough` is in the future (more than 7 days) | Cite normally. |
| `validThrough` is within the next 7 days | Cite with a freshness warning (e.g., "This information is valid until [date] and may change soon."). |
| `validThrough` is in the past | Do not cite. Seek alternative sources. If no alternative exists, inform the user that the available answer has expired. |

### 8.14 Interpreting Verification Status

When `verificationStatus` is present on a Question, AI systems MUST adjust their citation behavior accordingly:

| Status | AI System Behavior |
|--------|-------------------|
| `verified` | Cite with full confidence. The publisher confirms the answer is current and accurate. |
| `outdated` | Do not cite. Seek alternative sources. If no alternative exists, inform the user that the available answer is known to be outdated. |
| `under-review` | May cite but MUST add an explicit caveat to the user (e.g., "This information is currently being reviewed by the publisher and may be updated."). |

If `verificationStatus` is absent, the AI system SHOULD treat the answer as having no declared status and apply its standard quality assessment logic.

### 8.15 Processing Update Feeds

AI crawlers SHOULD check for AQA Update Feeds to detect content changes efficiently.

**Discovery:**
1. Check the `updateFeedUrl` property in the AQA block
2. If absent, attempt `https://{domain}/.well-known/aqa-updates.json`

**Polling frequency:**
- Recommended: once per hour maximum
- Respect HTTP cache headers (`Cache-Control`, `ETag`, `Last-Modified`)
- Use conditional requests (`If-Modified-Since`, `If-None-Match`) to minimize bandwidth

**Processing:**
- Compare `updateDate` with the crawler's last visit
- For updates with `isNewQuestion: true`, fetch the page to index the new question
- For version changes, re-fetch and re-embed the updated answer

### 8.16 Connecting to AQA Hubs

AI systems MAY connect to AQA Hubs for efficient change detection across multiple publishers.

**Recommended workflow:**
1. Query `GET /api/v1/updates?since={last_check}` periodically
2. Filter by relevant sectors and languages for your use case
3. For each update, re-fetch the source page and update the cached content
4. If the Hub provides a real-time stream (SSE/WebSocket), prefer it over polling

**Fallback:** If the Hub is unavailable, fall back to polling individual publishers' Update Feeds.

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

### 10.4 Agentic Action Security

The `potentialAction` property exposes API endpoints that AI agents may invoke. Implementers MUST observe the following security requirements:

- **HTTPS mandatory.** All `potentialAction` URL templates MUST use the `https://` scheme. AI agents MUST reject any action target that uses plain `http://`.
- **No auto-execution.** AI agents MUST NOT automatically execute actions without explicit user consent. Every action invocation requires the user to review the action description and confirm.
- **Rate limiting.** Publishers SHOULD implement rate limiting on action endpoints to prevent abuse from automated agents.
- **No credentials in URLs.** URL templates MUST NOT contain API keys, tokens, passwords, or session identifiers. If an action requires authentication, it should be handled through a separate authentication flow, not through URL parameters.

### 10.5 Content Signature Considerations

Content signatures in AQA V1.1 provide integrity verification, not authentication.

- **No PKI.** V1.1 does not include a public key infrastructure. Signatures prove that content matches a declared hash, but do not cryptographically bind the hash to a specific publisher identity. Future versions may add public key references to enable publisher authentication.
- **Stale signatures.** The `signedAt` datetime allows consumers to detect how old a signature is. A signature computed months ago on content that has since been modified (but not re-signed) indicates a maintenance gap.
- **Hash algorithm strength.** SHA-256 is the minimum recommended algorithm. Publishers handling highly sensitive content SHOULD consider SHA-384 or SHA-512.

### 10.6 Dynamic Endpoint Security

Dynamic endpoints expose real-time API surfaces. Implementers MUST observe the following requirements:

- **HTTPS mandatory.** The `url` property MUST use the `https://` scheme.
- **Public data only.** Dynamic endpoints MUST NOT require authentication. They are designed for publicly available data (prices, rates, status). Sensitive or personalized data MUST NOT be served through dynamic endpoints.
- **Rate limiting and CORS.** Publishers SHOULD implement rate limiting to prevent excessive queries and appropriate CORS headers to control cross-origin access.
- **Cache respect.** AI systems SHOULD respect the declared `cacheTTL` to avoid generating excessive traffic. Ignoring `cacheTTL` and polling an endpoint every second constitutes abusive behavior analogous to a DDoS attack.

### 10.7 Unanswered Query Webhook Privacy

The `unansweredQueryEndpoint` webhook creates a data flow from AI systems to publishers. This channel requires strict privacy controls:

- **AI systems MUST NOT include PII** in webhook payloads. No user names, email addresses, IP addresses, session identifiers, or any data that could identify an individual user.
- **Publishers MUST NOT attempt to correlate** webhook data with individual users. The webhook data represents aggregate demand signals, not individual user tracking.
- **Webhook data should be used exclusively for content improvement** — identifying gaps in the FAQ coverage, prioritizing new content creation, and understanding what AI audiences need. Using webhook data for advertising targeting, user profiling, or any purpose other than content improvement violates the spirit of AQA.

### 10.8 Update Feed and Pingback Security

- Update Feed files and Pingback endpoints MUST use HTTPS
- Payloads MUST NOT contain PII or answer content — only metadata (question name, version, URL, change description)
- Publishers SHOULD implement rate limiting on Pingback sends (max 1 per question per 24h)
- Hubs receiving Pingback POSTs SHOULD validate payload structure and reject malformed requests
- Hubs MUST authenticate publishers before accepting updates (mechanism out of scope for V1.2, but TLS client certificates or API keys are recommended)

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
  "specVersion": "1.2",
  "updateFeedUrl": "https://YOUR_DOMAIN/.well-known/aqa-updates.json",
  "pingbackEndpoints": [
    "https://hub.ailabsaudit.com/api/v1/ping"
  ],
  "monitoringSources": [
    {
      "@type": "MonitoringSource",
      "name": "SOURCE_NAME",
      "url": "SOURCE_URL",
      "sourceType": "regulatory"
    }
  ],
  "aiUsagePolicy": {
    "@type": "AIUsagePolicy",
    "ragCitation": "allow-with-attribution",
    "modelTraining": "disallow",
    "summarization": "allow",
    "directQuote": "allow-with-attribution",
    "commercialUse": "allow",
    "contentExpiry": "YOUR_EXPIRY_DATE"
  },
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
        ],
        "potentialAction": {
          "@type": "SearchAction",
          "target": {
            "@type": "EntryPoint",
            "urlTemplate": "YOUR_API_URL?q={query}",
            "httpMethod": "GET"
          },
          "description": "YOUR_ACTION_DESCRIPTION"
        },
        "contentSignature": {
          "@type": "ContentSignature",
          "hashAlgorithm": "sha256",
          "hashValue": "YOUR_SHA256_HASH",
          "signedFields": ["acceptedAnswer.text"],
          "signedAt": "YOUR_SIGN_DATETIME"
        },
        "ragSummary": "YOUR_RAG_OPTIMIZED_SUMMARY_MAX_300_CHARS",
        "audienceAnswers": [
          {
            "@type": "AudienceAnswer",
            "audience": "beginner",
            "text": "YOUR_BEGINNER_ANSWER"
          },
          {
            "@type": "AudienceAnswer",
            "audience": "expert",
            "text": "YOUR_EXPERT_ANSWER"
          }
        ],
        "dynamicEndpoint": {
          "@type": "DynamicEndpoint",
          "url": "YOUR_API_ENDPOINT",
          "httpMethod": "GET",
          "responseFormat": "application/json",
          "cacheTTL": 3600,
          "fallbackText": "YOUR_STATIC_FALLBACK"
        }
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

*AQA Specification v1.2.0-draft -- (c) 2026 AI Labs Solutions -- MIT License*
