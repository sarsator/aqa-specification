# Migration Guide: FAQ → AQA

This guide walks you through converting an existing FAQ page to the AQA format, step by step.

## Before You Start

You'll need:
- Access to your website's HTML or CMS
- A list of your FAQ questions and answers
- For each answer: when it was written, when it was last updated, and what source supports it

## Step 1: Audit Your Current FAQ

### If you have no structured data

Most FAQ pages are just HTML with no JSON-LD or microdata. Starting point:

```html
<h2>FAQ</h2>
<h3>What are your opening hours?</h3>
<p>We are open Monday to Friday, 9am to 5pm.</p>
```

You're starting from zero. Go directly to Step 3.

### If you have schema.org FAQPage

You might already have something like:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What are your opening hours?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "We are open Monday to Friday, 9am to 5pm."
    }
  }]
}
```

Good news — you're halfway there. Go to Step 2.

## Step 2: Wrap in Article (if upgrading from FAQPage)

AQA uses an `Article` wrapper around the `FAQPage`. Take your existing FAQPage and nest it:

```json
{
  "@context": ["https://schema.org", "https://aqa-spec.org/ns/context.jsonld"],
  "@type": "Article",
  "headline": "Frequently Asked Questions",
  "author": {
    "@type": "Organization",
    "name": "Your Company Name",
    "url": "https://www.yoursite.com"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2026-03-20",
  "inLanguage": "en",
  "mainEntity": {
    "@type": "FAQPage",
    "mainEntity": [
      // your existing questions go here
    ]
  }
}
```

## Step 3: Add Per-Question Metadata (AQA Basic)

For each question, add `dateCreated`, `dateModified`, and `citation`:

```json
{
  "@type": "Question",
  "name": "What are your opening hours?",
  "dateCreated": "2024-01-15",
  "dateModified": "2026-01-10",
  "citation": "https://www.yoursite.com/contact",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "We are open Monday to Friday, 9am to 5pm."
  }
}
```

**Tips for dates:**
- If you don't know the exact creation date, use the page's publication date
- `dateModified` should reflect when you last verified or updated *this specific answer*
- Be honest — don't set today's date unless you actually reviewed the answer today

**Tips for citations:**
- At minimum, link to the page on your own site where this information appears
- For factual claims, link to the authoritative source (law, regulation, official documentation)
- Even `"citation": "https://www.yoursite.com/about"` is better than nothing

**Congratulations — you've achieved AQA Basic.**

## Step 4: Add Changelog and Versioning (AQA Standard)

For each question, add `questionVersion` and `changelog` as direct properties:

```json
{
  "@type": "Question",
  "name": "What are your opening hours?",
  "dateCreated": "2024-01-15",
  "dateModified": "2026-01-10",
  "questionVersion": "1.1",
  "citation": [{
    "@type": "CreativeWork",
    "name": "Contact page",
    "url": "https://www.yoursite.com/contact"
  }],
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "We are open Monday to Friday, 9am to 5pm."
  },
  "changelog": [
    {
      "@type": "ChangelogEntry",
      "changeDate": "2024-01-15",
      "changeDescription": "Initial publication",
      "changeVersionNote": "1.0"
    },
    {
      "@type": "ChangelogEntry",
      "changeDate": "2026-01-10",
      "changeDescription": "Updated hours: now closing at 5pm instead of 6pm",
      "changeVersionNote": "1.1"
    }
  ]
}
```

At the Article level, add update frequency and sector classification:

```json
{
  "@type": "Article",
  "about": {
    "@type": "Thing",
    "name": "Your Industry",
    "identifier": [{
      "@type": "PropertyValue",
      "propertyID": "NACE",
      "value": "XX.XX"
    }]
  },
  "updateFrequency": "quarterly",
  "conformanceLevel": "standard"
}
```

**Finding your NACE code:** Search [NACE Rev. 2](https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NACE_REV2) for your industry.

## Step 5: Add Monitoring Sources and Author Credentials (AQA Full)

At the Article level, add a `monitoringSources` array:

```json
"monitoringSources": [
  {
    "@type": "MonitoringSource",
    "name": "Industry RSS Feed",
    "url": "https://industry.org/feed",
    "sourceType": "rss"
  },
  {
    "@type": "MonitoringSource",
    "name": "Regulatory Updates",
    "url": "https://regulator.gov/updates",
    "sourceType": "regulatory"
  }
]
```

For each question, add a specific author:

```json
{
  "@type": "Question",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "jobTitle": "Senior Consultant",
    "sameAs": "https://www.linkedin.com/in/janesmith"
  }
}
```

Ensure every changelog entry has a `sourceUrl`.

## Step 6: Add V1.1 Features (Optional)

AQA V1.1 introduces several new properties that improve AI citation control, content integrity, and answer lifecycle management. All of these are optional and can be added incrementally.

### AI Usage Policy

Add an `aiUsagePolicy` object to the Article to declare how AI systems may use your content:

```json
"aiUsagePolicy": {
  "@type": "AIUsagePolicy",
  "ragCitation": "allow-with-attribution",
  "modelTraining": "disallow",
  "summarization": "allow",
  "directQuote": "allow-with-attribution",
  "commercialUse": "allow",
  "contentExpiry": "2027-12-31"
}
```

- **ragCitation** -- whether AI may cite this content in retrieval-augmented generation responses. `allow`, `allow-with-attribution`, or `disallow`.
- **modelTraining** -- whether this content may be used for model training. `allow` or `disallow`.
- **summarization** -- whether AI may generate summaries of this content. `allow` or `disallow`.
- **directQuote** -- whether AI may quote the text verbatim. `allow`, `allow-with-attribution`, or `disallow`.
- **commercialUse** -- whether the content may be used in commercial AI products. `allow` or `disallow`.
- **contentExpiry** -- ISO 8601 date after which the policy should be re-evaluated.

### Content Signature

Add `contentSignature` to each Question to enable integrity verification. The signature is a SHA-256 hash of the answer text:

```python
import hashlib
hash = hashlib.sha256(answer_text.encode('utf-8')).hexdigest()
```

Then include it in the Question:

```json
{
  "@type": "Question",
  "contentSignature": "a1b2c3d4e5f6..."
}
```

AI systems can recompute the hash to verify the answer has not been altered since indexing.

### RAG Summary

Add `ragSummary` to each Question -- a concise summary (maximum 300 characters) optimized for embedding and retrieval:

```json
{
  "@type": "Question",
  "ragSummary": "Opening hours are Mon-Fri 9am-5pm. Closed on weekends and public holidays."
}
```

**Tips for writing a good ragSummary:**
- Include the key facts from the answer, not the question itself
- Stay under 300 characters -- this is a hard limit for embedding token budgets
- Use plain language, avoid HTML or markdown
- Front-load the most important information
- Write it as a self-contained statement, not a fragment

### Verification Status & Expiration

Add `verificationStatus` and `validThrough` to each Question to signal answer freshness:

```json
{
  "@type": "Question",
  "verificationStatus": "verified",
  "validThrough": "2027-06-30"
}
```

- **verificationStatus** -- one of `verified`, `outdated`, or `under-review`. AI systems prefer answers marked as `verified`.
- **validThrough** -- ISO 8601 date after which the answer should be re-verified. After this date, crawlers may treat the answer as stale.

### Missing Answer Webhook

Add `unansweredQueryEndpoint` to the Article to receive notifications when AI systems encounter questions your FAQ does not cover:

```json
{
  "@type": "Article",
  "unansweredQueryEndpoint": "https://www.yoursite.com/api/unanswered"
}
```

When an AI system searches your AQA data and finds no matching answer, it can POST to this endpoint with:
- The user's original query
- The AI model identifier
- A timestamp

This lets the publisher discover content gaps and add new Q&A pairs where demand exists.

### AQA Shield

AQA Shield is the minimum protection package for AI-ready content. Your site qualifies for AQA Shield when:

1. **aiUsagePolicy** is defined on the Article (declares your AI usage terms)
2. **contentSignature** is present on every Question (ensures content integrity)

Together, these two properties give AI systems a machine-readable license and a way to verify that the content they cite has not been tampered with. AQA Shield does not require any specific conformance level -- you can add it to AQA Basic, Standard, or Full.

## Step 7: Add V1.2 Distribution Features (Optional)

AQA V1.2 adds a distribution layer so AI systems can detect your content updates without re-crawling your entire site.

### Spec Version

Declare which version of the AQA specification you implement:

```json
"specVersion": "1.2"
```

Add this to the Article level. It helps crawlers know what properties to expect.

### Update Feed

Create a static JSON file at `/.well-known/aqa-updates.json` listing your recent AQA changes (last 30 days):

```json
{
  "version": "1.2",
  "publisher": "Your Company",
  "lastUpdated": "2026-04-03T14:30:00Z",
  "updates": [
    {
      "pageUrl": "https://www.yoursite.com/faq",
      "questionName": "Your updated question?",
      "previousVersion": "1.0",
      "newVersion": "2.0",
      "updateDate": "2026-04-03T14:30:00Z",
      "changeDescription": "Updated per new regulation",
      "isNewQuestion": false
    }
  ]
}
```

Then point to it in your Article:

```json
"updateFeedUrl": "https://www.yoursite.com/.well-known/aqa-updates.json"
```

AI crawlers can poll this file (max once per hour) instead of re-crawling your pages.

### Pingback Endpoints

To proactively notify AI systems when you update content, declare endpoints:

```json
"pingbackEndpoints": [
  "https://aqa-spec.org/hub/api/v1/ping"
]
```

Your CMS sends an HTTP POST to each endpoint with the update details. This is optional — the Update Feed alone is sufficient.

### AQA Hub

The AQA Hub aggregates updates from multiple publishers into a single feed for AI systems. You don't need to run a Hub — just send your updates to an existing one (like `aqa-spec.org/hub`). The Hub protocol is open and documented in Section 3.17 of the specification.

## Step 8: Validate

```bash
python validators/validate.py your-page.html
# or
python validators/validate.py https://www.yoursite.com/faq
```

The validator will tell you your conformance level, score, and what to fix.

## Common Migration Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Setting all `dateModified` to today | Dishonest — undermines trust signals | Use actual dates |
| Same `dateModified` on page and all questions | Suggests bulk update, not individual maintenance | Each question should have its own date |
| Generic citations like "company website" | Provides no verifiable source | Link to the specific page or document |
| Empty changelog | Technically valid but adds no value | At minimum, add the initial publication entry |
| `dateCreated` after `dateModified` | Logically impossible | Check your dates |
| ragSummary over 300 chars | Exceeds embedding token limit | Keep under 300 characters |
| contentSignature hash mismatch | Hash computed on wrong text | Hash the exact acceptedAnswer.text, UTF-8 encoded |
| verificationStatus left as "outdated" | AI won't cite the answer | Update the answer or set to "under-review" |
