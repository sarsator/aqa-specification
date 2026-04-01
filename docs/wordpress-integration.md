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
