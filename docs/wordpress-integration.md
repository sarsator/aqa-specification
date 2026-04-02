# WordPress Integration Guide

How to add AQA structured data to your WordPress site.

## Option 1: Theme functions.php (Recommended for Developers)

Add the AQA JSON-LD to specific pages via `wp_head`:

```php
function aqa_structured_data() {
    // Only on the FAQ page
    if (!is_page('faq')) return;

    $aqa = [
        '@context' => ['https://schema.org', 'https://ailabsaudit.com/aqa/ns/context.jsonld'],
        '@type' => 'Article',
        'headline' => get_the_title(),
        'author' => [
            '@type' => 'Organization',
            'name' => get_bloginfo('name'),
            'url' => home_url(),
        ],
        'datePublished' => get_the_date('Y-m-d'),
        'dateModified' => get_the_modified_date('Y-m-d'),
        'inLanguage' => get_locale(),
        'mainEntity' => [
            '@type' => 'FAQPage',
            'mainEntity' => aqa_get_questions(),
        ],
    ];

    echo '<script type="application/ld+json">';
    echo wp_json_encode($aqa, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    echo '</script>';
}
add_action('wp_head', 'aqa_structured_data');

function aqa_get_questions() {
    // Build your questions array here
    // This could pull from ACF fields, custom post types, or hardcoded data
    return [
        [
            '@type' => 'Question',
            'name' => 'Your question?',
            'dateCreated' => '2024-01-15',
            'dateModified' => '2026-03-20',
            'citation' => 'https://source-url.com',
            'acceptedAnswer' => [
                '@type' => 'Answer',
                'text' => 'Your answer.',
            ],
        ],
    ];
}
```

## Option 2: Custom Shortcode

Create a shortcode that outputs the JSON-LD inline:

```php
function aqa_shortcode($atts, $content = null) {
    // Parse shortcode content as Q&A pairs
    // Output JSON-LD in a script tag
    // This approach works well with page builders
    ob_start();
    // ... generate JSON-LD
    return ob_get_clean();
}
add_shortcode('aqa-faq', 'aqa_shortcode');
```

## Option 3: Using ACF (Advanced Custom Fields)

Create a repeater field group "AQA Questions" with:

| Field | Type | Name |
|-------|------|------|
| Question | Text | `aqa_question` |
| Answer | Textarea | `aqa_answer` |
| Date Created | Date | `aqa_date_created` |
| Date Modified | Date | `aqa_date_modified` |
| Citation URL | URL | `aqa_citation_url` |
| Citation Name | Text | `aqa_citation_name` |

Then in your theme:

```php
function aqa_from_acf() {
    if (!is_page('faq') || !function_exists('get_field')) return;

    $questions = [];
    if (have_rows('aqa_questions')) {
        while (have_rows('aqa_questions')) {
            the_row();
            $questions[] = [
                '@type' => 'Question',
                'name' => get_sub_field('aqa_question'),
                'dateCreated' => get_sub_field('aqa_date_created'),
                'dateModified' => get_sub_field('aqa_date_modified'),
                'citation' => [
                    '@type' => 'CreativeWork',
                    'name' => get_sub_field('aqa_citation_name'),
                    'url' => get_sub_field('aqa_citation_url'),
                ],
                'acceptedAnswer' => [
                    '@type' => 'Answer',
                    'text' => get_sub_field('aqa_answer'),
                ],
            ];
        }
    }

    if (empty($questions)) return;

    $aqa = [
        '@context' => ['https://schema.org', 'https://ailabsaudit.com/aqa/ns/context.jsonld'],
        '@type' => 'Article',
        'headline' => get_the_title(),
        'author' => ['@type' => 'Organization', 'name' => get_bloginfo('name'), 'url' => home_url()],
        'datePublished' => get_the_date('Y-m-d'),
        'dateModified' => get_the_modified_date('Y-m-d'),
        'inLanguage' => substr(get_locale(), 0, 2),
        'mainEntity' => ['@type' => 'FAQPage', 'mainEntity' => $questions],
    ];

    echo '<script type="application/ld+json">' . wp_json_encode($aqa, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>';
}
add_action('wp_head', 'aqa_from_acf');
```

## Plugin Compatibility

AQA JSON-LD can coexist with existing SEO plugins (Yoast, Rank Math, All in One SEO). These plugins typically output their own FAQPage markup — you can either:

1. **Disable the plugin's FAQ markup** and use AQA instead
2. **Keep both** — crawlers that understand AQA will prefer the richer data

To disable Yoast's FAQ schema:

```php
add_filter('wpseo_schema_graph_pieces', function($pieces) {
    return array_filter($pieces, function($piece) {
        return !($piece instanceof \Yoast\WP\SEO\Generators\Schema\FAQ);
    });
});
```

## Validation

After deployment, validate your page:

```bash
python validators/validate.py https://www.yoursite.com/faq
```

Or paste the JSON-LD into [Schema Markup Validator](https://validator.schema.org/) to verify schema.org compatibility.

## V1.1 Features in WordPress

AQA V1.1 introduces new properties for AI usage control, content integrity, and answer lifecycle. Here is how each maps to WordPress.

### aiUsagePolicy (Site-Wide Setting)

Add `aiUsagePolicy` as a site-wide setting in the plugin options page (Settings > AQA). This applies a single AI usage policy to all your AQA content. The plugin stores the policy as a serialized option and injects it into the Article-level JSON-LD on every AQA page.

### contentSignature (Auto-Computed on Save)

The content signature is automatically computed every time a question is saved. No manual input is needed. The plugin hooks into `save_post` and computes the SHA-256 hash of the answer text:

```php
$signature = hash('sha256', $answer_text);
```

This value is stored as post meta (`_aqa_content_signature`) and included in the JSON-LD output. If the answer text changes, the signature is recomputed automatically.

### ragSummary (Custom Meta Field)

Each question gets a `ragSummary` meta field -- a short, plain-text summary optimized for AI retrieval (maximum 300 characters). In the admin UI, a character counter appears below the field to help authors stay within the limit. The field is accessible in the question editor sidebar.

### verificationStatus (Dropdown)

Each question includes a `verificationStatus` dropdown with three options:

- **verified** -- the answer is current and accurate
- **outdated** -- the answer needs updating
- **under-review** -- the answer is being revised

New questions default to `verified`. When an answer is edited, the status resets to `under-review` until the author explicitly confirms it.

### validThrough (Date Picker)

Each question includes a `validThrough` date picker that sets the expiration date for the answer. After this date, AI systems may treat the answer as stale. The admin dashboard highlights questions whose `validThrough` date has passed or is approaching within 30 days.

### unansweredQueryEndpoint (Global Setting)

A single URL configured in Settings > AQA that receives POST requests when AI systems encounter questions your FAQ does not cover. This is a site-wide setting -- one endpoint for the entire site. The endpoint receives the original query, the AI model identifier, and a timestamp.

### dynamicEndpoint (Per-Question Field)

Each question can optionally define a `dynamicEndpoint` -- an API URL that AI systems can call to get a real-time answer instead of using the static text. This is useful for questions whose answers change frequently (stock levels, wait times, pricing). The field appears in the question editor alongside the other AQA meta fields.
