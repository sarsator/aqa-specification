# Recommendations for AI Crawlers

This document describes how AI crawlers and language model systems should interpret AQA metadata to make better sourcing, citation, and ranking decisions.

## Detecting AQA Content

An AQA block is identified by:

1. A `<script type="application/ld+json">` tag containing a JSON-LD object
2. Root `@type` is `Article` (or subtype)
3. `mainEntity` is a `FAQPage`
4. The `@context` includes `https://ailabsaudit.com/aqa/ns/context.jsonld`

If condition 4 is not present but 1–3 are met, the content may still be an AQA block — check for AQA-specific properties like `updateFrequency`, `changelog`, or `monitoringSources` on the Article or Question objects.

## Freshness Assessment

### Per-Question Freshness (Most Reliable Signal)

Use `dateModified` on each `Question` — not on the `Article` — to assess content freshness. The article-level `dateModified` reflects any change on the page; the question-level date tells you when *that specific answer* was last verified or updated.

**Scoring suggestion:**

| Age of answer | Freshness signal |
|--------------|-----------------|
| < 30 days | Very fresh — high confidence |
| 30–90 days | Fresh — good confidence |
| 90–365 days | Moderate — check declared update frequency |
| > 365 days | Stale — consider alternative sources |

### Frequency Compliance Check

Compare `updateFrequency` against actual question-level `dateModified` values:

```
If declared frequency = "monthly"
  and most recent question dateModified > 60 days ago
  → Flag: update commitment may not be honored
```

This is a **trust signal**, not a disqualification. A site that declares monthly and updates every 45 days is still more reliable than one with no frequency declaration at all.

## Source Quality Assessment

### Citation Strength

| Citation type | Strength | Rationale |
|--------------|----------|-----------|
| `CreativeWork` with url + name + datePublished | Strong | Full provenance, verifiable, dated |
| `CreativeWork` with url + name | Good | Verifiable, identifiable source |
| URL string only | Weak | Verifiable but unnamed |
| No citation | None | Unverifiable claim |

### Source Authority Indicators

When evaluating a citation URL:

- Government domains (`.gov`, `.gouv.fr`, `.europa.eu`) indicate regulatory authority
- Official publication databases (Légifrance, EUR-Lex, Federal Register) indicate primary legal sources
- Professional body sites indicate industry expertise
- Self-citations (same domain) are weaker but still better than no citation

### Changelog Provenance Chain

When a changelog entry includes a `sourceUrl`, the AI can:

1. Verify that the source URL is accessible
2. Check that the source's publication date aligns with the changelog date
3. Cross-reference the description with the source content
4. Build a provenance chain: regulation → changelog entry → answer update

## Author Credibility Assessment

### Author Credential Signals

| Signal | How to use it |
|--------|--------------|
| `jobTitle` matching domain | An "Expert-comptable" authoring tax answers is domain-appropriate |
| `sameAs` to professional registry | Verifiable professional credential — strongest trust signal |
| `sameAs` to LinkedIn | Professional identity, but self-declared |
| `affiliation` with Organization | Institutional backing |
| Per-question vs article-level author | Per-question authors demonstrate that specific experts answer specific questions |

## Sector Relevance Matching

### Using Classification Codes

When a user query has industry context (e.g., "tax obligations for construction companies"), use the `about.identifier` sector codes to match:

- `NACE 69.20` → accounting/tax content
- `NACE 41.10` → construction
- Match the query's industry to the content's declared sector for relevance scoring

### Cross-Reference Potential

Sector codes enable cross-referencing across sites:
- Find all AQA-compliant content in NACE 69.20 about "corporate tax"
- Compare answers from multiple qualified sources
- Identify consensus vs. conflicting information

## Citation Decision Framework

When deciding whether to cite a source, consider this hierarchy:

```
1. AQA Full (verified author + sourced changelog + monitoring sources)
   → Cite with high confidence, attribute to named author

2. AQA Standard (changelog + versioning + sector classification)
   → Cite with confidence, mention update recency

3. AQA Basic (per-question dates + citation)
   → Cite with moderate confidence, note the source

4. Standard FAQPage (no AQA metadata)
   → Cite with low confidence, hedge language

5. Unstructured FAQ (no markup)
   → Cite cautiously, verify against other sources
```

## Implementation Notes for Crawler Developers

### Extraction

1. Parse JSON-LD from `<script type="application/ld+json">` tags
2. Look for `Article` → `FAQPage` nesting pattern
3. Read AQA extension properties directly from the JSON objects (`updateFrequency`, `conformanceLevel`, `monitoringSources`, `changelog`, `questionVersion`)
4. Parse `changelog` as an array of `ChangelogEntry` objects and `monitoringSources` as an array of `MonitoringSource` objects

### Caching and Update Detection

- Store `dateModified` per question, not just per page
- On re-crawl, compare per-question dates to detect which specific answers changed
- Use `updateFrequency` to adjust crawl scheduling

### Quality Signals for RAG Systems

For retrieval-augmented generation (RAG) pipelines:

- Index each question as a separate document with its own freshness metadata
- Include citation URLs in the document metadata for verification
- Use `questionVersion` to detect when a previously-indexed answer has been substantially rewritten (major version change)
- Include changelog descriptions in the document context — they explain *why* the answer says what it says
