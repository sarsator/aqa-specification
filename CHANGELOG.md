# Changelog

All notable changes to the AQA specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0-draft] — 2026-04-03

### Added

**9 optional V1.1 features (work at any conformance level):**

Protection:
- AI Usage Policy (`aiUsagePolicy`) — granular rights: RAG citation, model training, summarization, direct quote, commercial use + content expiry date
- Content Signature (`contentSignature`) — SHA-256 hash of answer text for cryptographic integrity proof

Enrichment:
- RAG Summary (`ragSummary`) — token-optimized 300-char summary for vector embedding
- Multi-Persona Answers (`audienceAnswers`) — audience-specific answer variants (beginner, expert, business, technical, legal)
- Agentic Actions (`potentialAction`) — link answers to executable API endpoints via schema.org Action/EntryPoint
- Dynamic Endpoints (`dynamicEndpoint`) — real-time API for volatile data (prices, rates, stock, status)

Feedback & Quality:
- Missing Answer Webhook (`unansweredQueryEndpoint`) — AI systems POST missing queries back to the publisher
- Answer Expiration (`validThrough`) — per-answer expiration date, AI stops citing after this date
- Verification Status (`verificationStatus`) — verified / outdated / under-review per answer

**AQA Shield badge:**
- aiUsagePolicy + contentSignature on all questions = AQA Shield status
- Legal protection + cryptographic integrity at any conformance level

**Citation Quotes (Section 3.5.2.1):**
- `abstract` property on CreativeWork citations for inline source verification

**HTML Data-to-Text Redundancy (Section 6.5):**
- Recommendation to render AQA metadata as visible HTML for RAG scrapers that strip `<script>` tags

**RAG & Vector Database Mapping (Section 8.5):**
- Chunking strategy, metadata extraction, quality-aware retrieval guide for AI engineers

### Changed

- Specification version bumped to 1.1.0-draft
- JSON-LD context extended with 14 new properties and 4 new types (AIUsagePolicy, ContentSignature, AudienceAnswer, DynamicEndpoint)
- JSON Schema updated to v1.1.0 with 5 new `$defs`
- Python validator extended with `validate_v11_features()` function
- Full examples enriched with all V1.1 features and real SHA-256 hashes
- All documentation updated for V1.1

---

## [1.0.0-draft] — 2026-03-31

### Added

- Initial specification document (SPECIFICATION.md)
- JSON-LD context file (aqa-context.jsonld) defining AQA extension properties
- JSON Schema for validation (aqa-schema.json)
- Three conformance levels: Basic, Standard, Full
- Python validator (validate.py) supporting file and URL input
- Six example implementations across all conformance levels:
  - Basic: comptable-pme.jsonld, restaurant.jsonld
  - Standard: cabinet-avocats.jsonld, agence-immobiliere.jsonld
  - Full: institution-financiere.jsonld, organisme-reglementaire.jsonld
- Documentation: migration guide, WordPress integration, FAQ vs AQA comparison, crawler recommendations
- AQA extension properties: updateFrequency, changelog, monitoringSources, sectorClassification, conformanceLevel, questionVersion
- MIT license
