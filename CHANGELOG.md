# Changelog

All notable changes to the AQA specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1-draft] — 2026-04-03

### Fixed

- Removed 3 orphaned properties from aqa-context.jsonld (`sectorCode`, `sectorLabel`, `sectorSystem`) that were never used — sector classification uses `about.identifier` instead
- Clarified in Section 3.14 that `validThrough` is a native schema.org property, not an AQA extension — AQA documents a convention for its use
- Fixed changelog ordering specification: changed from "most recent first" to "chronological — oldest first" to match all examples
- Added AQA Shield JSON-LD code example to README.md

---

## [1.2.0-draft] — 2026-04-03

### Added

Distribution:
- Update Notification Protocol (Section 3.16) — Pull layer (`/.well-known/aqa-updates.json`) + Push layer (`pingbackEndpoints`)
- AQA Hub Protocol (Section 3.17) — centralized update aggregation across publishers, REST API spec, strategic positioning as "IndexNow for FAQ"
- `specVersion` property — declares which AQA spec version the block implements
- `updateFeedUrl` property — explicit pointer to the publisher's AQA Update Feed
- `pingbackEndpoints` property — array of URLs to notify when content changes

Documentation:
- New document: `docs/ecosystem-integration.md` — LangChain AQALoader, LlamaIndex AQAReader, WordPress plugin architecture, Hub integration
- Sections 8.15-8.16: crawler recommendations for Update Feeds and Hub connectivity
- Section 10.8: security considerations for Update Feed and Pingback

### Changed

- Specification version bumped to 1.2.0-draft
- JSON-LD context extended with 3 new properties (specVersion, updateFeedUrl, pingbackEndpoints)
- JSON Schema $id updated to v1.2.0
- Python validator extended with V1.2 validation rules (V12-SV, V12-UF, V12-PB)
- Full examples updated with specVersion, updateFeedUrl, and pingbackEndpoints
- README updated with Distribution features group
- All documentation synchronized

---

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
