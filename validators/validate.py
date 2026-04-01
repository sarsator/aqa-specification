#!/usr/bin/env python3
"""
AQA Validator — Validates AQA (AI Question Answer) structured data blocks.

Usage:
    python validate.py <file_or_url> [--level basic|standard|full] [--json]

Examples:
    python validate.py examples/basic/restaurant.jsonld
    python validate.py https://www.example.com/faq
    python validate.py examples/full/organisme-reglementaire.jsonld --json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    requests = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import extruct
except ImportError:
    extruct = None


class Level(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    severity: Severity
    rule: str
    message: str
    path: str = ""
    level: Level = Level.BASIC


@dataclass
class ValidationResult:
    conformance_level: Level | None = None
    score: int = 0
    issues: list[Issue] = field(default_factory=list)
    properties_present: list[str] = field(default_factory=list)
    properties_missing: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    questions_count: int = 0
    source: str = ""

    def add_issue(self, severity: Severity, rule: str, message: str,
                  path: str = "", level: Level = Level.BASIC):
        self.issues.append(Issue(severity, rule, message, path, level))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]


# --- Helpers ---

ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:?\d{2})?)?$"
)
VERSION_RE = re.compile(r"^\d+\.\d+$")
VALID_FREQUENCIES = {"weekly", "monthly", "quarterly", "yearly"}
VALID_CONFORMANCE = {"basic", "standard", "full"}
VALID_ARTICLE_TYPES = {"Article", "NewsArticle", "TechArticle", "BlogPosting", "WebPage"}
VALID_SECTOR_SYSTEMS = {"NACE", "NAF", "SIC", "ISIC"}
VALID_SOURCE_TYPES = {"rss", "regulatory", "journal", "newsletter", "government", "professional_body"}


def is_valid_date(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return bool(ISO_DATE_RE.match(value))


def parse_date(value: str) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, TypeError):
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None


def is_url(value: str) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def get_sector_codes(about: dict) -> list[dict]:
    """Extract sector classification codes from about.identifier array."""
    identifiers = about.get("identifier", [])
    if not isinstance(identifiers, list):
        return []
    return [
        p for p in identifiers
        if isinstance(p, dict) and p.get("propertyID") in VALID_SECTOR_SYSTEMS
    ]


# --- Extraction ---

def extract_from_file(filepath: str) -> list[dict]:
    """Extract JSON-LD from a file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    content = path.read_text(encoding="utf-8")

    if path.suffix in (".jsonld", ".json"):
        data = json.loads(content)
        return [data] if isinstance(data, dict) else data

    # HTML file — extract JSON-LD from script tags
    if BeautifulSoup is None:
        raise ImportError("beautifulsoup4 is required for HTML parsing: pip install beautifulsoup4")

    soup = BeautifulSoup(content, "html.parser")
    blocks = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                blocks.append(data)
            elif isinstance(data, list):
                blocks.extend(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return blocks


def extract_from_url(url: str) -> list[dict]:
    """Extract JSON-LD from a URL."""
    if requests is None:
        raise ImportError("requests is required for URL fetching: pip install requests")

    resp = requests.get(url, timeout=30, headers={
        "User-Agent": "AQA-Validator/1.0 (+https://github.com/ailabsaudit/aqa-specification)"
    })
    resp.raise_for_status()

    # Try extruct first (most robust)
    if extruct is not None:
        data = extruct.extract(resp.text, syntaxes=["json-ld"], uniform=True)
        blocks = data.get("json-ld", [])
        if blocks:
            return blocks

    # Fallback to BeautifulSoup
    if BeautifulSoup is None:
        raise ImportError(
            "beautifulsoup4 or extruct is required for URL extraction: "
            "pip install beautifulsoup4 extruct"
        )

    soup = BeautifulSoup(resp.text, "html.parser")
    blocks = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                blocks.append(data)
            elif isinstance(data, list):
                blocks.extend(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return blocks


def extract_jsonld(source: str) -> list[dict]:
    """Extract JSON-LD blocks from a file path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        return extract_from_url(source)
    return extract_from_file(source)


# --- Validation ---

def find_aqa_blocks(blocks: list[dict]) -> list[dict]:
    """Filter blocks that look like AQA blocks (Article with FAQPage mainEntity)."""
    aqa_blocks = []
    for block in blocks:
        block_type = block.get("@type", "")
        if block_type in VALID_ARTICLE_TYPES:
            main_entity = block.get("mainEntity", {})
            if isinstance(main_entity, dict) and main_entity.get("@type") == "FAQPage":
                aqa_blocks.append(block)
    return aqa_blocks


def validate_basic(block: dict, result: ValidationResult):
    """Validate AQA Basic requirements."""

    # Article type
    block_type = block.get("@type")
    if block_type not in VALID_ARTICLE_TYPES:
        result.add_issue(Severity.ERROR, "BASIC-001",
                         f"@type must be Article or subtype, got: {block_type}")
    else:
        result.properties_present.append("@type")

    # Headline
    headline = block.get("headline")
    if not headline or not isinstance(headline, str):
        result.add_issue(Severity.ERROR, "BASIC-002", "headline is required and must be non-empty")
        result.properties_missing.append("headline")
    else:
        result.properties_present.append("headline")

    # Author
    author = block.get("author")
    if not isinstance(author, dict):
        result.add_issue(Severity.ERROR, "BASIC-003", "author is required")
        result.properties_missing.append("author")
    else:
        if not author.get("name"):
            result.add_issue(Severity.ERROR, "BASIC-003a", "author.name is required")
        if not author.get("@type"):
            result.add_issue(Severity.ERROR, "BASIC-003b",
                             "author.@type is required (Person or Organization)")
        result.properties_present.append("author")

    # Dates
    date_published = block.get("datePublished")
    date_modified = block.get("dateModified")

    if not date_published:
        result.add_issue(Severity.ERROR, "BASIC-004", "datePublished is required")
        result.properties_missing.append("datePublished")
    elif not is_valid_date(date_published):
        result.add_issue(Severity.ERROR, "BASIC-004a",
                         f"datePublished is not a valid ISO 8601 date: {date_published}")
    else:
        result.properties_present.append("datePublished")

    if not date_modified:
        result.add_issue(Severity.ERROR, "BASIC-005", "dateModified is required")
        result.properties_missing.append("dateModified")
    elif not is_valid_date(date_modified):
        result.add_issue(Severity.ERROR, "BASIC-005a",
                         f"dateModified is not a valid ISO 8601 date: {date_modified}")
    else:
        result.properties_present.append("dateModified")

    # Date order check
    if date_published and date_modified:
        dp = parse_date(date_published)
        dm = parse_date(date_modified)
        if dp and dm and dm < dp:
            result.add_issue(Severity.ERROR, "BASIC-005b",
                             "dateModified cannot be before datePublished")

    # inLanguage
    if block.get("inLanguage"):
        result.properties_present.append("inLanguage")
    else:
        result.add_issue(Severity.WARNING, "BASIC-006",
                         "inLanguage is recommended", level=Level.BASIC)

    # mainEntity -> FAQPage
    main_entity = block.get("mainEntity", {})
    if not isinstance(main_entity, dict) or main_entity.get("@type") != "FAQPage":
        result.add_issue(Severity.ERROR, "BASIC-007",
                         "mainEntity must be a FAQPage object")
        return

    questions = main_entity.get("mainEntity", [])
    if not isinstance(questions, list) or len(questions) == 0:
        result.add_issue(Severity.ERROR, "BASIC-008",
                         "FAQPage must contain at least one Question in mainEntity")
        return

    result.questions_count = len(questions)
    article_date_modified = parse_date(str(date_modified)) if date_modified else None

    for i, q in enumerate(questions):
        q_path = f"questions[{i}]"
        validate_question_basic(q, result, q_path, article_date_modified)


def validate_question_basic(q: dict, result: ValidationResult, path: str,
                            article_date_modified: date | None):
    """Validate a single question at Basic level."""
    if q.get("@type") != "Question":
        result.add_issue(Severity.ERROR, "BASIC-Q01",
                         "@type must be Question", path=path)

    name = q.get("name")
    if not name or not isinstance(name, str):
        result.add_issue(Severity.ERROR, "BASIC-Q02",
                         "name (question text) is required", path=path)

    # Per-question dates
    dc = q.get("dateCreated")
    dm = q.get("dateModified")

    if not dc:
        result.add_issue(Severity.ERROR, "BASIC-Q03",
                         "dateCreated is required on each Question", path=path)
    elif not is_valid_date(dc):
        result.add_issue(Severity.ERROR, "BASIC-Q03a",
                         f"dateCreated is not valid ISO 8601: {dc}", path=path)

    if not dm:
        result.add_issue(Severity.ERROR, "BASIC-Q04",
                         "dateModified is required on each Question", path=path)
    elif not is_valid_date(dm):
        result.add_issue(Severity.ERROR, "BASIC-Q04a",
                         f"dateModified is not valid ISO 8601: {dm}", path=path)

    if dc and dm:
        dc_d = parse_date(dc)
        dm_d = parse_date(dm)
        if dc_d and dm_d and dm_d < dc_d:
            result.add_issue(Severity.ERROR, "BASIC-Q05",
                             "dateModified cannot be before dateCreated", path=path)
        if dm_d and article_date_modified and dm_d > article_date_modified:
            result.add_issue(Severity.WARNING, "BASIC-Q06",
                             "Question dateModified is after Article dateModified", path=path)

    # Citation
    citation = q.get("citation")
    if not citation:
        result.add_issue(Severity.ERROR, "BASIC-Q07",
                         "citation is required on each Question", path=path)
    else:
        _validate_citation(citation, result, path, Level.BASIC)

    # acceptedAnswer
    answer = q.get("acceptedAnswer")
    if not isinstance(answer, dict):
        result.add_issue(Severity.ERROR, "BASIC-Q08",
                         "acceptedAnswer is required", path=path)
    else:
        if answer.get("@type") != "Answer":
            result.add_issue(Severity.ERROR, "BASIC-Q08a",
                             "acceptedAnswer.@type must be Answer", path=path)
        if not answer.get("text"):
            result.add_issue(Severity.ERROR, "BASIC-Q08b",
                             "acceptedAnswer.text must be non-empty", path=path)


def _validate_citation(citation: Any, result: ValidationResult, path: str, level: Level):
    """Validate citation field."""
    if isinstance(citation, str):
        if not is_url(citation):
            result.add_issue(Severity.ERROR, "CIT-001",
                             f"citation URL is invalid: {citation}", path=path)
        if level >= Level.STANDARD:
            result.add_issue(Severity.WARNING, "CIT-002",
                             "Standard+ should use structured CreativeWork citations, not URL strings",
                             path=path, level=Level.STANDARD)
    elif isinstance(citation, dict):
        _validate_creative_work(citation, result, path)
    elif isinstance(citation, list):
        for j, c in enumerate(citation):
            _validate_citation(c, result, f"{path}.citation[{j}]", level)
    else:
        result.add_issue(Severity.ERROR, "CIT-003",
                         "citation must be a URL string, CreativeWork, or array", path=path)


def _validate_creative_work(cw: dict, result: ValidationResult, path: str):
    """Validate a CreativeWork citation."""
    if cw.get("@type") != "CreativeWork":
        result.add_issue(Severity.WARNING, "CIT-CW01",
                         "citation @type should be CreativeWork", path=path)
    if not cw.get("name"):
        result.add_issue(Severity.WARNING, "CIT-CW02",
                         "citation CreativeWork should have a name", path=path)
    if not cw.get("url"):
        result.add_issue(Severity.ERROR, "CIT-CW03",
                         "citation CreativeWork must have a url", path=path)
    elif not is_url(cw["url"]):
        result.add_issue(Severity.ERROR, "CIT-CW04",
                         f"citation url is not a valid URL: {cw['url']}", path=path)


def validate_standard(block: dict, result: ValidationResult):
    """Validate AQA Standard requirements (on top of Basic)."""

    # Update frequency — direct property
    freq = block.get("updateFrequency")
    if not freq:
        result.add_issue(Severity.ERROR, "STD-001",
                         "updateFrequency is required for Standard level",
                         level=Level.STANDARD)
        result.properties_missing.append("updateFrequency")
    elif freq not in VALID_FREQUENCIES:
        result.add_issue(Severity.ERROR, "STD-001a",
                         f"updateFrequency must be one of {VALID_FREQUENCIES}, got: {freq}",
                         level=Level.STANDARD)
    else:
        result.properties_present.append("updateFrequency")

    # Sector classification — via about.identifier
    about = block.get("about")
    if not isinstance(about, dict):
        result.add_issue(Severity.ERROR, "STD-002",
                         "about (sector classification) is required for Standard level",
                         level=Level.STANDARD)
        result.properties_missing.append("about (sector)")
    else:
        valid_sectors = get_sector_codes(about)
        if not valid_sectors:
            result.add_issue(Severity.ERROR, "STD-002a",
                             "about.identifier must contain at least one sector code (NACE, NAF, SIC, or ISIC)",
                             level=Level.STANDARD)
        else:
            result.properties_present.append("sectorClassification")

    # Conformance level declaration — direct property
    conf = block.get("conformanceLevel")
    if conf:
        result.properties_present.append("conformanceLevel")
        if conf not in VALID_CONFORMANCE:
            result.add_issue(Severity.WARNING, "STD-003",
                             f"conformanceLevel should be one of {VALID_CONFORMANCE}, got: {conf}",
                             level=Level.STANDARD)

    # Per-question Standard checks
    main_entity = block.get("mainEntity", {})
    questions = main_entity.get("mainEntity", [])
    if not isinstance(questions, list):
        return

    for i, q in enumerate(questions):
        q_path = f"questions[{i}]"

        # Version — direct property
        version = q.get("questionVersion")
        if not version:
            result.add_issue(Severity.ERROR, "STD-Q01",
                             "questionVersion is required for Standard level",
                             path=q_path, level=Level.STANDARD)
        elif not isinstance(version, str) or not VERSION_RE.match(version):
            result.add_issue(Severity.WARNING, "STD-Q01a",
                             f"questionVersion should be major.minor format, got: {version}",
                             path=q_path, level=Level.STANDARD)

        # Changelog — direct property, array of ChangelogEntry objects
        changelog = q.get("changelog")
        if not changelog:
            result.add_issue(Severity.ERROR, "STD-Q02",
                             "changelog is required for Standard level",
                             path=q_path, level=Level.STANDARD)
        elif not isinstance(changelog, list):
            result.add_issue(Severity.ERROR, "STD-Q02a",
                             "changelog must be an array of ChangelogEntry objects",
                             path=q_path, level=Level.STANDARD)
        elif len(changelog) == 0:
            result.add_issue(Severity.ERROR, "STD-Q02b",
                             "changelog must have at least one entry",
                             path=q_path, level=Level.STANDARD)
        else:
            for j, entry in enumerate(changelog):
                e_path = f"{q_path}.changelog[{j}]"
                if not isinstance(entry, dict):
                    result.add_issue(Severity.ERROR, "STD-Q02c",
                                     "changelog entry must be an object",
                                     path=e_path, level=Level.STANDARD)
                    continue
                entry_date = entry.get("changeDate")
                if not entry_date:
                    result.add_issue(Severity.ERROR, "STD-Q02d",
                                     "changelog entry must have a changeDate",
                                     path=e_path, level=Level.STANDARD)
                elif not is_valid_date(entry_date):
                    result.add_issue(Severity.ERROR, "STD-Q02e",
                                     f"changelog changeDate is not valid ISO 8601: {entry_date}",
                                     path=e_path, level=Level.STANDARD)
                if not entry.get("changeDescription"):
                    result.add_issue(Severity.ERROR, "STD-Q02f",
                                     "changelog entry must have a changeDescription",
                                     path=e_path, level=Level.STANDARD)

        # Structured citations
        citation = q.get("citation")
        if isinstance(citation, str):
            result.add_issue(Severity.WARNING, "STD-Q03",
                             "Standard level should use structured CreativeWork citations",
                             path=q_path, level=Level.STANDARD)


def validate_full(block: dict, result: ValidationResult):
    """Validate AQA Full requirements (on top of Standard)."""

    # Monitoring sources — direct property, array of MonitoringSource objects
    sources = block.get("monitoringSources")
    if not sources:
        result.add_issue(Severity.ERROR, "FULL-001",
                         "monitoringSources is required for Full level",
                         level=Level.FULL)
        result.properties_missing.append("monitoringSources")
    elif not isinstance(sources, list):
        result.add_issue(Severity.ERROR, "FULL-001a",
                         "monitoringSources must be an array of MonitoringSource objects",
                         level=Level.FULL)
    elif len(sources) < 2:
        result.add_issue(Severity.ERROR, "FULL-001b",
                         "monitoringSources must contain at least 2 sources",
                         level=Level.FULL)
    else:
        result.properties_present.append("monitoringSources")
        for j, src in enumerate(sources):
            s_path = f"monitoringSources[{j}]"
            if not isinstance(src, dict):
                result.add_issue(Severity.ERROR, "FULL-001c",
                                 "monitoring source must be an object",
                                 path=s_path, level=Level.FULL)
                continue
            if not src.get("name"):
                result.add_issue(Severity.ERROR, "FULL-001d",
                                 "monitoring source must have a name",
                                 path=s_path, level=Level.FULL)
            if not src.get("url"):
                result.add_issue(Severity.ERROR, "FULL-001e",
                                 "monitoring source must have a url",
                                 path=s_path, level=Level.FULL)
            st = src.get("sourceType")
            if st and st not in VALID_SOURCE_TYPES:
                result.add_issue(Severity.WARNING, "FULL-001f",
                                 f"sourceType '{st}' is not a recognized type",
                                 path=s_path, level=Level.FULL)

    # Article-level author credentials
    author = block.get("author", {})
    if isinstance(author, dict):
        has_credential = author.get("jobTitle") or author.get("sameAs")
        if not has_credential:
            result.add_issue(Severity.ERROR, "FULL-002",
                             "Article author must include jobTitle or sameAs for Full level",
                             level=Level.FULL)

    # Per-question author and changelog sourceUrl
    main_entity = block.get("mainEntity", {})
    questions = main_entity.get("mainEntity", [])
    if not isinstance(questions, list):
        return

    for i, q in enumerate(questions):
        q_path = f"questions[{i}]"

        # Per-question author
        q_author = q.get("author")
        if not isinstance(q_author, dict):
            result.add_issue(Severity.ERROR, "FULL-Q01",
                             "Each question must have its own author for Full level",
                             path=q_path, level=Level.FULL)
        else:
            if not q_author.get("name"):
                result.add_issue(Severity.ERROR, "FULL-Q01a",
                                 "Per-question author must have a name",
                                 path=q_path, level=Level.FULL)
            has_cred = (q_author.get("jobTitle") or q_author.get("sameAs")
                        or q_author.get("affiliation"))
            if not has_cred:
                result.add_issue(Severity.ERROR, "FULL-Q01b",
                                 "Per-question author must have jobTitle, sameAs, or affiliation",
                                 path=q_path, level=Level.FULL)

        # Changelog entries must have changeSourceUrl
        changelog = q.get("changelog")
        if isinstance(changelog, list):
            for j, entry in enumerate(changelog):
                if isinstance(entry, dict) and not entry.get("changeSourceUrl"):
                    result.add_issue(Severity.ERROR, "FULL-Q02",
                                     "Every changelog entry must include changeSourceUrl for Full level",
                                     path=f"{q_path}.changelog[{j}]",
                                     level=Level.FULL)


def compute_score(result: ValidationResult, target_level: Level) -> int:
    """Compute a conformance score (0-100) based on validation results."""
    if not result.issues and result.questions_count > 0:
        return 100

    total_checks = 0
    passed_checks = 0

    basic_errors = [i for i in result.errors if i.level == Level.BASIC]
    basic_total = 12 + (result.questions_count * 7)
    basic_passed = max(0, basic_total - len(basic_errors))
    total_checks += basic_total
    passed_checks += basic_passed

    if target_level in (Level.STANDARD, Level.FULL):
        std_errors = [i for i in result.errors if i.level == Level.STANDARD]
        std_total = 3 + (result.questions_count * 3)
        std_passed = max(0, std_total - len(std_errors))
        total_checks += std_total
        passed_checks += std_passed

    if target_level == Level.FULL:
        full_errors = [i for i in result.errors if i.level == Level.FULL]
        full_total = 3 + (result.questions_count * 3)
        full_passed = max(0, full_total - len(full_errors))
        total_checks += full_total
        passed_checks += full_passed

    if total_checks == 0:
        return 0

    return round((passed_checks / total_checks) * 100)


def determine_achieved_level(result: ValidationResult) -> Level | None:
    """Determine the highest conformance level achieved."""
    basic_errors = [i for i in result.errors if i.level == Level.BASIC]
    if basic_errors:
        return None

    standard_errors = [i for i in result.errors if i.level == Level.STANDARD]
    if standard_errors:
        return Level.BASIC

    full_errors = [i for i in result.errors if i.level == Level.FULL]
    if full_errors:
        return Level.STANDARD

    return Level.FULL


def generate_recommendations(result: ValidationResult) -> list[str]:
    """Generate actionable recommendations based on validation issues."""
    recs = []
    rules_seen = set()

    for issue in result.issues:
        if issue.rule in rules_seen:
            continue
        rules_seen.add(issue.rule)

        if issue.rule == "BASIC-Q07":
            recs.append(
                "Add a citation (URL or CreativeWork) to each Question. "
                "Even a link to your own page is better than nothing."
            )
        elif issue.rule == "BASIC-Q03":
            recs.append(
                "Add dateCreated to each Question. If you don't know the exact date, "
                "use the page publication date as an estimate."
            )
        elif issue.rule == "STD-001":
            recs.append(
                "Add updateFrequency to the Article. "
                "This tells AI crawlers how often you review your content."
            )
        elif issue.rule == "STD-Q02":
            recs.append(
                "Add a changelog array to each Question with ChangelogEntry objects. "
                "Even a single 'Initial publication' entry adds value."
            )
        elif issue.rule == "STD-002":
            recs.append(
                "Add sector classification via the about.identifier property with NACE, NAF, or SIC codes."
            )
        elif issue.rule == "FULL-001":
            recs.append(
                "Add monitoringSources — an array of MonitoringSource objects declaring "
                "the feeds and publications you watch."
            )
        elif issue.rule == "FULL-Q01":
            recs.append(
                "Add a per-question author with professional credentials. "
                "This strengthens trust signals for AI citation."
            )
        elif issue.rule.startswith("CIT-002") or issue.rule == "STD-Q03":
            recs.append(
                "Upgrade URL citations to structured CreativeWork objects with name, url, "
                "and datePublished for stronger provenance."
            )

    if result.conformance_level == Level.BASIC:
        recs.append(
            "You've achieved AQA Basic! To reach Standard, add: changelog, questionVersion, "
            "updateFrequency, and sector classification."
        )
    elif result.conformance_level == Level.STANDARD:
        recs.append(
            "You've achieved AQA Standard! To reach Full, add: monitoringSources, "
            "per-question authors with credentials, and changeSourceUrl on all changelog entries."
        )

    return recs


def validate(block: dict, source: str = "") -> ValidationResult:
    """Run full AQA validation on a block."""
    result = ValidationResult(source=source)

    validate_basic(block, result)
    validate_standard(block, result)
    validate_full(block, result)

    result.conformance_level = determine_achieved_level(result)

    if result.conformance_level == Level.FULL:
        target = Level.FULL
    elif result.conformance_level == Level.STANDARD:
        target = Level.FULL
    elif result.conformance_level == Level.BASIC:
        target = Level.STANDARD
    else:
        target = Level.BASIC

    result.score = compute_score(result, target)
    result.recommendations = generate_recommendations(result)

    return result


# --- Output ---

def format_report(result: ValidationResult) -> str:
    """Format a human-readable validation report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  AQA VALIDATION REPORT")
    lines.append("=" * 60)

    if result.source:
        lines.append(f"\n  Source: {result.source}")

    level_display = result.conformance_level.value.upper() if result.conformance_level else "NONE"
    lines.append(f"  Conformance Level: AQA {level_display}")
    lines.append(f"  Score: {result.score}/100")
    lines.append(f"  Questions: {result.questions_count}")

    errors = result.errors
    warnings = result.warnings

    lines.append(f"\n  Issues: {len(errors)} errors, {len(warnings)} warnings")
    lines.append("-" * 60)

    if errors:
        lines.append("\n  ERRORS:")
        for e in errors:
            path_str = f" ({e.path})" if e.path else ""
            lines.append(f"  [{e.rule}] {e.message}{path_str}")

    if warnings:
        lines.append("\n  WARNINGS:")
        for w in warnings:
            path_str = f" ({w.path})" if w.path else ""
            lines.append(f"  [{w.rule}] {w.message}{path_str}")

    if result.properties_present:
        lines.append(f"\n  Properties present: {', '.join(result.properties_present)}")
    if result.properties_missing:
        lines.append(f"  Properties missing: {', '.join(result.properties_missing)}")

    if result.recommendations:
        lines.append("\n  RECOMMENDATIONS:")
        for r in result.recommendations:
            lines.append(f"  -> {r}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json_report(result: ValidationResult) -> str:
    """Format a JSON validation report."""
    report = {
        "source": result.source,
        "conformanceLevel": result.conformance_level.value if result.conformance_level else None,
        "score": result.score,
        "questionsCount": result.questions_count,
        "issues": [
            {
                "severity": i.severity.value,
                "rule": i.rule,
                "message": i.message,
                "path": i.path,
                "level": i.level.value,
            }
            for i in result.issues
        ],
        "propertiesPresent": result.properties_present,
        "propertiesMissing": result.properties_missing,
        "recommendations": result.recommendations,
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="AQA Validator — Validate AQA structured data blocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s examples/basic/restaurant.jsonld
  %(prog)s https://www.example.com/faq
  %(prog)s examples/full/organisme-reglementaire.jsonld --json
  %(prog)s examples/standard/cabinet-avocats.jsonld --level standard
        """,
    )
    parser.add_argument("source", help="File path or URL to validate")
    parser.add_argument("--level", choices=["basic", "standard", "full"],
                        help="Target conformance level (default: auto-detect)")
    parser.add_argument("--json", action="store_true",
                        help="Output report in JSON format")

    args = parser.parse_args()

    try:
        blocks = extract_jsonld(args.source)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Missing dependency: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting JSON-LD: {e}", file=sys.stderr)
        sys.exit(1)

    aqa_blocks = find_aqa_blocks(blocks)

    if not aqa_blocks:
        if not blocks:
            print("No JSON-LD blocks found.", file=sys.stderr)
        else:
            print("JSON-LD found but no AQA blocks detected.", file=sys.stderr)
            print("An AQA block requires an Article with a FAQPage mainEntity.", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for i, block in enumerate(aqa_blocks):
        source_label = args.source
        if len(aqa_blocks) > 1:
            source_label = f"{args.source} [block {i + 1}/{len(aqa_blocks)}]"

        result = validate(block, source=source_label)

        if args.json:
            print(format_json_report(result))
        else:
            print(format_report(result))

        if result.conformance_level is None:
            exit_code = 2
        elif args.level and result.conformance_level.value != args.level:
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
