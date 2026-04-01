# Changelog

All notable changes to the AQA specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
