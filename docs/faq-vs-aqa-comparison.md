# FAQ vs AQA: A Comparison

This document shows side by side what a traditional FAQ looks like versus the same content in AQA format, and what AI crawlers can extract from each.

## Traditional FAQ (schema.org FAQPage)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the corporate tax rate for SMEs?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The reduced rate is 15% on the first €42,500 of profit for qualifying SMEs. The standard rate of 25% applies above that threshold."
      }
    }
  ]
}
```

### What an AI crawler knows:

| Signal | Available? | Value |
|--------|-----------|-------|
| Question text | ✅ | "What is the corporate tax rate for SMEs?" |
| Answer text | ✅ | The answer content |
| When this answer was written | ❌ | Unknown |
| When this answer was last verified | ❌ | Unknown |
| What source backs this answer | ❌ | Unknown |
| Has this answer ever been updated | ❌ | Unknown |
| Why was it updated | ❌ | Unknown |
| Who wrote this answer | ❌ | Unknown |
| What industry is this for | ❌ | Must infer from context |
| How often is this maintained | ❌ | Unknown |

**Result:** The AI has the text but no basis for assessing its reliability, freshness, or authority. It's treated the same as any other FAQ on the internet.

---

## AQA Standard (same content)

```json
{
  "@context": ["https://schema.org", "https://aqa-spec.org/ns/context.jsonld"],
  "@type": "Article",
  "headline": "Corporate Tax FAQ",
  "author": {
    "@type": "Person",
    "name": "Marie Dupont",
    "url": "https://www.cabinet-dupont.fr/equipe/marie"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2026-03-25",
  "inLanguage": "fr",
  "about": {
    "@type": "Thing",
    "name": "Accounting and tax consultancy",
    "identifier": [
      {"@type": "PropertyValue", "propertyID": "NACE", "value": "69.20"}
    ]
  },
  "updateFrequency": "monthly",
  "conformanceLevel": "standard",
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the corporate tax rate for SMEs?",
        "dateCreated": "2024-01-15",
        "dateModified": "2026-03-25",
        "citation": [{
          "@type": "CreativeWork",
          "name": "Article 219 du Code général des impôts",
          "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006303680",
          "datePublished": "2024-01-01"
        }],
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "The reduced rate is 15% on the first €42,500 of profit for qualifying SMEs (revenue < €10M, fully paid-up capital held 75%+ by individuals). The standard rate of 25% applies above that threshold. Note: the 2026 Finance Act raised the ceiling from €42,500 to €50,000 for fiscal years starting January 1, 2026."
        },
        "questionVersion": "3.0",
        "changelog": [
          {"@type": "ChangelogEntry", "changeDate": "2024-01-15", "changeDescription": "Initial publication with 2024 rates", "changeSourceUrl": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006303680", "changeVersionNote": "1.0"},
          {"@type": "ChangelogEntry", "changeDate": "2025-01-10", "changeDescription": "Confirmed rates unchanged for 2025", "changeVersionNote": "2.0"},
          {"@type": "ChangelogEntry", "changeDate": "2026-03-25", "changeDescription": "Updated: 2026 Finance Act raised reduced-rate ceiling from €42,500 to €50,000", "changeSourceUrl": "https://www.legifrance.gouv.fr/loi-finances-2026-art15", "changeVersionNote": "3.0"}
        ]
      }
    ]
  }
}
```

### What an AI crawler now knows:

| Signal | Available? | Value |
|--------|-----------|-------|
| Question text | ✅ | "What is the corporate tax rate for SMEs?" |
| Answer text | ✅ | Detailed answer with 2026 update |
| When this answer was written | ✅ | January 15, 2024 |
| When this answer was last verified | ✅ | March 25, 2026 (2 days ago) |
| What source backs this answer | ✅ | Article 219 CGI on Légifrance |
| Has this answer ever been updated | ✅ | Yes, 3 times (version 3.0) |
| Why was it updated | ✅ | "2026 Finance Act raised reduced-rate ceiling" |
| Who wrote this answer | ✅ | Marie Dupont, accountant |
| What industry is this for | ✅ | NACE 69.20 (Accounting/tax consultancy) |
| How often is this maintained | ✅ | Monthly review committed |

**Result:** The AI has full context to assess this answer's reliability. It can cite it with confidence, attribute it properly, and prioritize it over unverified sources.

---

## Impact on AI Citation

### Without AQA

> "According to various sources, the corporate tax rate for SMEs is 15% on the first €42,500..."

The AI hedges with "various sources" because it can't verify any single source.

### With AQA

> "According to Cabinet Dupont's tax FAQ (last updated March 2026, citing Article 219 CGI), the reduced corporate tax rate is 15% on the first €50,000 of profit following the 2026 Finance Act."

The AI can cite specifically, mention the date, and reference the underlying legal source.

---

## V1.1: Beyond Citation

### Without V1.1

> The AI cites the answer but has no rights framework, no integrity proof, and no way to tell the publisher what questions are missing.

### With V1.1

> The AI checks usage rights before citing. It verifies the content hash matches. It selects the expert-level answer for a technical user. It calls the dynamic endpoint for real-time rates. And when a user asks a question not covered, it pings the webhook — so the publisher knows exactly what content to create next.

---

## Summary

| Capability | Traditional FAQ | AQA Basic | AQA Standard | AQA Full |
|-----------|:-:|:-:|:-:|:-:|
| Question/Answer text | ✅ | ✅ | ✅ | ✅ |
| Per-question freshness | ❌ | ✅ | ✅ | ✅ |
| Source attribution | ❌ | ✅ | ✅ | ✅ |
| Revision history | ❌ | ❌ | ✅ | ✅ |
| Version tracking | ❌ | ❌ | ✅ | ✅ |
| Maintenance commitment | ❌ | ❌ | ✅ | ✅ |
| Industry classification | ❌ | ❌ | ✅ | ✅ |
| Monitoring sources | ❌ | ❌ | ❌ | ✅ |
| Expert author per answer | ❌ | ❌ | ❌ | ✅ |
| Full provenance chain | ❌ | ❌ | ❌ | ✅ |
| AI usage rights declaration | ❌ | opt | opt | opt |
| Content integrity (hash) | ❌ | opt | opt | opt |
| RAG-optimized summary | ❌ | opt | opt | opt |
| Multi-audience answers | ❌ | opt | opt | opt |
| Real-time data endpoint | ❌ | opt | opt | opt |
| Missing answer feedback | ❌ | opt | opt | opt |
| Per-answer expiration | ❌ | opt | opt | opt |
| Verification status | ❌ | opt | opt | opt |
