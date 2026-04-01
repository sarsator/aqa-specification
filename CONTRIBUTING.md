# Contributing to AQA

Thank you for your interest in contributing to the AQA specification. This document explains how to participate.

## Ways to Contribute

### Report Issues

- **Specification clarity**: If something in SPECIFICATION.md is ambiguous or contradictory, open an issue.
- **Schema.org compatibility**: If you find that AQA markup doesn't validate or behaves unexpectedly with a specific tool, report it.
- **Real-world implementation problems**: If you tried implementing AQA and hit a roadblock, we want to know.

### Propose Changes

1. Fork the repository
2. Create a branch (`feat/your-proposal` or `fix/your-fix`)
3. Make your changes
4. Submit a pull request with a clear description of **what** you changed and **why**

### Submit Examples

Real-world AQA implementations are valuable. If you've implemented AQA on a site:

1. Add your example to `examples/` in the appropriate level folder
2. Run the validator to confirm conformance
3. Submit a PR

### Sector-Specific Profiles

If your industry has specific requirements (e.g., healthcare, legal, financial services), you can propose a sector profile that:

- Mandates specific citation types
- Requires certain monitoring sources
- Defines industry-standard classification codes

## Guidelines

### Specification Changes

- The specification is versioned using semantic versioning
- Breaking changes require a major version bump
- New optional properties are minor version bumps
- Clarifications and typo fixes are patch version bumps

### Code

- Python code must work with Python 3.10+
- No unnecessary dependencies
- Include tests for new validation rules

### Documentation

- Specification text is in English
- Examples can be bilingual (English + another language)
- Keep language clear and direct — avoid jargon where a simpler term works

### Commit Messages

Use conventional commit format:

```
feat: add support for ISIC classification codes
fix: correct changelog date validation regex
docs: clarify monitoring source types
```

## Code of Conduct

Be respectful, constructive, and focused on improving the specification. We're building an open standard — collaboration is the point.

## Questions?

Open an issue with the `question` label or reach out via the repository discussions.
