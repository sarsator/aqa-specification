# AQA — AI Question Answer

**An open specification for structured Q&A content optimized for AI comprehension and citation.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec Version](https://img.shields.io/badge/spec-v1.2.0--draft-orange.svg)](SPECIFICATION.md)
[![Schema.org Compatible](https://img.shields.io/badge/schema.org-compatible-green.svg)](https://schema.org)

---

## The Problem

Every website has a FAQ. Almost none of them are built for how information is consumed today.

AI assistants — ChatGPT, Claude, Gemini, Perplexity — are becoming the primary way people find answers. These systems crawl the web, extract structured data, and try to determine what's **trustworthy**, **current**, and **citable**. But today's FAQ markup gives them almost nothing to work with:

- **No per-question freshness.** Schema.org's `FAQPage` has `dateModified` at the page level only. A page updated yesterday may contain answers written three years ago.
- **No revision history.** There's no way to say *"this answer was updated because a new regulation was published."*
- **No source attribution per answer.** No mechanism to link each answer to the document, law, or publication that backs it.
- **No maintenance signal.** A crawler can't tell if a FAQ is actively maintained or abandoned.

This means AI systems treat a meticulously maintained regulatory FAQ the same as a copy-pasted list that hasn't been touched since 2021.

## The Solution

AQA is a **documented convention** for enriching Q&A structured data with the metadata AI systems need. It uses existing schema.org types (`Article`, `FAQPage`, `Question`, `Answer`) combined with a small set of extension properties — no new types, no breaking changes, full backward compatibility.

### What AQA Adds

| Signal | What it tells AI crawlers |
|--------|--------------------------|
| Per-question `dateCreated` / `dateModified` | The exact freshness of each individual answer |
| `citation` per answer | The authoritative source backing each claim |
| `changelog` per answer | Why and when each answer was modified |
| `questionVersion` | How many times the substance of an answer has changed |
| `updateFrequency` | How often the publisher commits to reviewing the content |
| `monitoringSources` | What feeds and publications the publisher watches |
| Sector classification (NACE/NAF/SIC) | The industry context for relevance matching |
| Per-question author with credentials | Who wrote each answer and why they're qualified |
| `aiUsagePolicy` | Granular AI rights: RAG, training, citation, summarization, commercial use |
| `contentSignature` | SHA-256 hash proving answer integrity — anti-hallucination proof |
| `ragSummary` | Token-optimized 300-char summary ready for vector embedding |
| `audienceAnswers` | Audience-specific answer variants (beginner, expert, business...) |
| `dynamicEndpoint` | Real-time API for volatile data (prices, rates, status) |
| `unansweredQueryEndpoint` | Webhook: AI sends missing questions back to the publisher |
| `validThrough` | Per-answer expiration date — AI stops citing after this date |
| `verificationStatus` | verified / outdated / under-review status per answer |
| `specVersion` | Declares which AQA spec version the block implements |
| `updateFeedUrl` | Publisher's AQA Update Feed for change detection |
| `pingbackEndpoints` | Push notifications to AI systems when content changes |
| AQA Hub Protocol | Centralized aggregation of updates across publishers (like IndexNow for FAQ) |

### Three Conformance Levels

| Level | Effort | What you prove |
|-------|--------|----------------|
| **AQA Basic** | Minimal | Each answer has a known age and at least one source |
| **AQA Standard** | Moderate | Content is actively maintained, changes are tracked, industry context is explicit |
| **AQA Full** | Significant | Full provenance chain — who, what, when, why, from where |

### AQA Shield (V1.1)

When every question in an AQA document includes both `aiUsagePolicy` and `contentSignature`, the document qualifies for **AQA Shield** — a combination of legal protection and cryptographic integrity:

- **`aiUsagePolicy`** declares exactly what AI systems are allowed to do with each answer (RAG, training, citation, summarization, commercial use).
- **`contentSignature`** provides a SHA-256 hash of the answer content, enabling AI consumers to verify that the answer has not been altered or hallucinated.

AQA Shield works at any conformance level (Basic, Standard, or Full). It is an orthogonal guarantee that can be added to any existing AQA implementation.

```json
"aiUsagePolicy": {
  "@type": "AIUsagePolicy",
  "ragCitation": "allow-with-attribution",
  "modelTraining": "disallow",
  "contentExpiry": "2027-12-31"
},
"contentSignature": {
  "@type": "ContentSignature",
  "hashAlgorithm": "sha256",
  "hashValue": "a3f2b8c...",
  "signedFields": ["acceptedAnswer.text"],
  "signedAt": "2026-04-03T14:00:00Z"
}
```

### V1.1+ Features

AQA V1.1 and V1.2 introduce 12 new properties, organized in four groups:

- **Protection** — AI Usage Policy, Content Signature (together = AQA Shield)
- **Enrichment** — RAG Summary, Multi-Persona Answers, Agentic Actions, Dynamic Endpoints
- **Feedback** — Missing Answer Webhook, Answer Expiration, Verification Status
- **Distribution** — Update Feed (`/.well-known/aqa-updates.json`), Pingback Endpoints, AQA Hub Protocol

## Quick Start

### 1. Add AQA Basic to your FAQ (5 minutes)

Wrap your existing FAQ markup in an `Article` and add per-question dates and citations:

```html
<script type="application/ld+json">
{
  "@context": ["https://schema.org", "https://ailabsaudit.com/aqa/ns/context.jsonld"],
  "@type": "Article",
  "headline": "Frequently Asked Questions",
  "author": {"@type": "Organization", "name": "Your Company"},
  "datePublished": "2024-01-15",
  "dateModified": "2026-03-20",
  "inLanguage": "en",
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [{
      "@type": "Question",
      "name": "Your question here?",
      "dateCreated": "2024-01-15",
      "dateModified": "2026-03-20",
      "citation": "https://source-url.com/document",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Your answer here."
      }
    }]
  }
}
</script>
```

### 2. Validate

```bash
pip install requests beautifulsoup4 jsonschema extruct
python validators/validate.py your-file.jsonld
```

### 3. Upgrade

See the [Migration Guide](docs/migration-guide.md) to move from Basic to Standard and Full.

> **Note:** For V1.1 features (AQA Shield, RAG Summary, audience variants, etc.), see the [full specification](SPECIFICATION.md).

## Repository Structure

```
├── SPECIFICATION.md          # Complete technical specification (V1.2)
├── schemas/
│   ├── aqa-context.jsonld    # JSON-LD context for AQA extensions
│   └── aqa-schema.json       # JSON Schema for validation
├── examples/
│   ├── basic/                # AQA Basic examples
│   ├── standard/             # AQA Standard examples
│   └── full/                 # AQA Full examples
├── validators/
│   └── validate.py           # Python validation tool
└── docs/
    ├── migration-guide.md    # FAQ → AQA migration guide
    ├── wordpress-integration.md
    ├── faq-vs-aqa-comparison.md
    ├── crawler-recommendations.md
    └── ecosystem-integration.md  # LangChain, LlamaIndex, WordPress, Hub
```

## Philosophy

AQA is an **open standard, free forever**. No API key, no registration, no vendor lock-in. Anyone can implement it, validate it, and build on it.

The goal is to make AQA for AI visibility what OpenGraph became for social sharing: metadata so useful that *not* implementing it becomes a disadvantage.

## Relationship with AI Labs Audit

AQA is an independent, MIT-licensed specification. [AI Labs Audit](https://ailabsaudit.com) is a platform that measures brand visibility across 50+ AI systems — it can measure the effectiveness of AQA implementation, but the format itself is free and vendor-neutral.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome:

- Schema.org compatibility feedback
- Real-world implementation reports
- Sector-specific profile proposals
- Translations of the specification
- Validator improvements

## License

MIT — see [LICENSE](LICENSE).

---

*Created by [Davy Abderrahman](https://ailabsaudit.com) — AI Labs Solutions*
