# AQA Ecosystem Integration Guide

This guide describes how to integrate AQA structured data into existing AI frameworks, CMS platforms, and RAG pipelines.

## LangChain Integration

### AQALoader — Document Loader

An AQA-aware Document Loader for LangChain that extracts structured Q&A data with full metadata preservation.

```python
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document
import json
import hashlib
import requests

class AQALoader(BaseLoader):
    """Load AQA-structured FAQ pages into LangChain Documents.
    
    Each Question becomes a separate Document with AQA metadata
    preserved in the metadata dict. Uses ragSummary for page_content
    when available, falls back to acceptedAnswer.text.
    """

    def __init__(self, source: str):
        """source: file path or URL to a JSON-LD file or HTML page."""
        self.source = source

    def load(self) -> list[Document]:
        # Extract JSON-LD (simplified — real implementation should
        # handle HTML extraction via beautifulsoup4 or extruct)
        if self.source.startswith("http"):
            resp = requests.get(self.source, timeout=30)
            data = json.loads(resp.text)  # assumes raw JSON-LD
        else:
            with open(self.source) as f:
                data = json.load(f)

        documents = []
        article = data
        faq = article.get("mainEntity", {})
        questions = faq.get("mainEntity", [])

        # Article-level metadata
        article_meta = {
            "aqa_spec_version": article.get("specVersion"),
            "aqa_conformance": article.get("conformanceLevel"),
            "aqa_update_frequency": article.get("updateFrequency"),
            "aqa_publisher": article.get("publisher", {}).get("name"),
        }

        # AI Usage Policy
        policy = article.get("aiUsagePolicy", {})
        if policy:
            article_meta["aqa_rag_allowed"] = policy.get("ragCitation", "allow") != "disallow"
            article_meta["aqa_training_allowed"] = policy.get("modelTraining", "disallow") != "disallow"
            article_meta["aqa_content_expiry"] = policy.get("contentExpiry")

        for q in questions:
            answer = q.get("acceptedAnswer", {})
            answer_text = answer.get("text", "")

            # Use ragSummary for embedding content when available
            page_content = q.get("ragSummary", answer_text)

            # Build per-question metadata
            meta = {
                **article_meta,
                "aqa_question": q.get("name"),
                "aqa_date_created": q.get("dateCreated"),
                "aqa_date_modified": q.get("dateModified"),
                "aqa_version": q.get("questionVersion"),
                "aqa_full_answer": answer_text,
                "aqa_verification_status": q.get("verificationStatus"),
                "aqa_valid_through": q.get("validThrough"),
                "aqa_has_dynamic": q.get("dynamicEndpoint") is not None,
            }

            # Citation sources
            citations = q.get("citation", [])
            if isinstance(citations, list):
                meta["aqa_source_urls"] = [
                    c.get("url") if isinstance(c, dict) else c
                    for c in citations
                ]

            # Signature verification
            sig = q.get("contentSignature")
            if sig and sig.get("hashAlgorithm") == "sha256":
                computed = hashlib.sha256(answer_text.encode("utf-8")).hexdigest()
                meta["aqa_signature_verified"] = computed == sig.get("hashValue")

            # Audience variants
            audiences = q.get("audienceAnswers", [])
            if audiences:
                meta["aqa_audiences"] = [a.get("audience") for a in audiences]

            documents.append(Document(page_content=page_content, metadata=meta))

        return documents
```

**Usage:**

```python
loader = AQALoader("https://www.example.com/faq.jsonld")
docs = loader.load()

# Filter by verification status
verified_docs = [d for d in docs if d.metadata.get("aqa_verification_status") == "verified"]

# Filter by RAG permission
allowed_docs = [d for d in docs if d.metadata.get("aqa_rag_allowed", True)]

# Use with a vector store
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_documents(allowed_docs, OpenAIEmbeddings())
```

## LlamaIndex Integration

### AQAReader — Data Reader

```python
from llama_index.core import Document as LIDocument
from llama_index.core.readers.base import BaseReader
import json

class AQAReader(BaseReader):
    """Read AQA-structured JSON-LD into LlamaIndex Documents.
    
    Each Question becomes a node with AQA metadata preserved.
    """

    def load_data(self, file_path: str) -> list[LIDocument]:
        with open(file_path) as f:
            data = json.load(f)

        documents = []
        article = data
        faq = article.get("mainEntity", {})

        for q in faq.get("mainEntity", []):
            answer_text = q.get("acceptedAnswer", {}).get("text", "")
            rag_summary = q.get("ragSummary")

            # Build metadata dict
            metadata = {
                "question": q.get("name"),
                "date_modified": q.get("dateModified"),
                "version": q.get("questionVersion"),
                "verification_status": q.get("verificationStatus", "verified"),
                "conformance_level": article.get("conformanceLevel"),
                "sector": None,
                "source": self._extract_source_url(q),
            }

            # Extract sector code
            about = article.get("about", {})
            identifiers = about.get("identifier", [])
            for ident in identifiers:
                if ident.get("propertyID") == "NACE":
                    metadata["sector"] = ident.get("value")
                    break

            # Use ragSummary as text for embedding, full answer as extra_info
            text = rag_summary if rag_summary else answer_text
            metadata["full_answer"] = answer_text

            documents.append(LIDocument(text=text, metadata=metadata))

        return documents

    def _extract_source_url(self, question: dict) -> str | None:
        citation = question.get("citation")
        if isinstance(citation, str):
            return citation
        if isinstance(citation, dict):
            return citation.get("url")
        if isinstance(citation, list) and citation:
            first = citation[0]
            return first.get("url") if isinstance(first, dict) else first
        return None
```

**Usage with query engine:**

```python
from llama_index.core import VectorStoreIndex

reader = AQAReader()
documents = reader.load_data("examples/full/organisme-reglementaire.jsonld")

# Filter out expired/outdated content
valid_docs = [
    d for d in documents
    if d.metadata.get("verification_status") != "outdated"
]

index = VectorStoreIndex.from_documents(valid_docs)
query_engine = index.as_query_engine()
response = query_engine.query("What is the corporate tax rate for SMEs?")
```

## WordPress Plugin Architecture

A WordPress plugin implementing AQA should handle the full lifecycle:

### Content Management

```
AQA FAQ (Custom Post Type)
├── Post title → headline
├── Post content → questions (repeater field or sub-posts)
│   ├── Question text → name
│   ├── Answer (WYSIWYG) → acceptedAnswer.text
│   ├── ragSummary (text, 300 char limit)
│   ├── verificationStatus (dropdown)
│   ├── validThrough (date picker)
│   └── Citations (repeater: name, url, abstract)
├── Settings meta box
│   ├── updateFrequency (select)
│   ├── Sector codes (NACE/NAF/SIC)
│   └── aiUsagePolicy (per-permission toggles)
└── Auto-computed on save
    ├── dateModified (per question)
    ├── questionVersion (auto-increment)
    ├── changelog (diff detection)
    └── contentSignature (SHA-256)
```

### JSON-LD Generation

The plugin hooks into `wp_head` and injects the complete AQA JSON-LD:

```php
add_action('wp_head', function() {
    if (!is_singular('aqa_faq')) return;
    
    $aqa_block = aqa_generate_jsonld(get_the_ID());
    echo '<script type="application/ld+json">';
    echo wp_json_encode($aqa_block, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    echo '</script>';
});
```

### Update Feed Generation

The plugin auto-generates `/.well-known/aqa-updates.json`:

```php
// Register rewrite rule
add_action('init', function() {
    add_rewrite_rule(
        '^\.well-known/aqa-updates\.json$',
        'index.php?aqa_update_feed=1',
        'top'
    );
});

// Handle the request
add_action('template_redirect', function() {
    if (!get_query_var('aqa_update_feed')) return;
    
    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: *');
    
    $updates = aqa_get_recent_updates(30); // last 30 days
    echo wp_json_encode([
        'version' => '1.2',
        'publisher' => get_bloginfo('name'),
        'lastUpdated' => gmdate('c'),
        'updates' => $updates,
    ]);
    exit;
});
```

### Hub Pingback on Save

```php
add_action('save_post_aqa_faq', function($post_id) {
    $endpoints = get_option('aqa_pingback_endpoints', []);
    if (empty($endpoints)) return;
    
    $payload = aqa_build_update_payload($post_id);
    
    foreach ($endpoints as $endpoint) {
        wp_remote_post($endpoint, [
            'body' => wp_json_encode($payload),
            'headers' => ['Content-Type' => 'application/json'],
            'timeout' => 5,
            'blocking' => false, // non-blocking
        ]);
    }
});
```

## Validation

Use the Python validator included in this repository to validate any AQA implementation:

```bash
# Validate a local file
python validators/validate.py examples/full/organisme-reglementaire.jsonld

# Validate a live URL
python validators/validate.py https://www.example.com/faq

# JSON output for CI/CD integration
python validators/validate.py file.jsonld --json
```

The validator checks all conformance levels (Basic, Standard, Full) and all V1.1/V1.2 optional features. It reports a score out of 100 and lists any issues found.

## Further Resources

- [SPECIFICATION.md](../SPECIFICATION.md) — Complete technical specification
- [Migration Guide](migration-guide.md) — How to convert an existing FAQ to AQA
- [WordPress Integration](wordpress-integration.md) — Detailed WordPress setup
- [Crawler Recommendations](crawler-recommendations.md) — How AI systems should process AQA
- [FAQ vs AQA Comparison](faq-vs-aqa-comparison.md) — Side-by-side feature comparison
