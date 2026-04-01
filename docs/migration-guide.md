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
  "@context": ["https://schema.org", "https://ailabsaudit.com/aqa/ns/context.jsonld"],
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

## Step 6: Validate

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
