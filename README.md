# AQA — AI Question Answer

**An open specification for structured Q&A content optimized for AI comprehension and citation.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec Version](https://img.shields.io/badge/spec-v1.0.0--draft-orange.svg)](SPECIFICATION.md)
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

### Three Conformance Levels

| Level | Effort | What you prove |
|-------|--------|----------------|
| **AQA Basic** | Minimal | Each answer has a known age and at least one source |
| **AQA Standard** | Moderate | Content is actively maintained, changes are tracked, industry context is explicit |
| **AQA Full** | Significant | Full provenance chain — who, what, when, why, from where |

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

## Repository Structure

```
├── SPECIFICATION.md          # Complete technical specification
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
    └── crawler-recommendations.md
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
