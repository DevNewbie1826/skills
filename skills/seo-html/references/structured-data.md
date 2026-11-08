# Structured data (JSON-LD)

Read this when you write or fix the page's JSON-LD, or an LD-* finding fires.

## Shape

Use one `<script type="application/ld+json">` with an `@graph` list. Every top-level node needs `@context` (`https://schema.org`, not `http`) and every node needs `@type` (LD-01 to LD-04). Give reusable nodes an `@id` like `https://example.com/#org` and point to them instead of repeating them.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#org",
      "name": "Example Guides",
      "url": "https://example.com/",
      "logo": "https://example.com/img/logo.png"
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com/#website",
      "name": "Example Guides",
      "url": "https://example.com/",
      "publisher": { "@id": "https://example.com/#org" }
    },
    {
      "@type": "WebPage",
      "@id": "https://example.com/guides/passport-renewal#webpage",
      "url": "https://example.com/guides/passport-renewal",
      "name": "Passport renewal time in 2026",
      "isPartOf": { "@id": "https://example.com/#website" }
    },
    {
      "@type": "Article",
      "headline": "Passport renewal time in 2026",
      "image": "https://example.com/img/passport-renewal-1200x630.jpg",
      "author": { "@type": "Person", "name": "Jane Park", "url": "https://example.com/about/jane-park" },
      "publisher": { "@id": "https://example.com/#org" },
      "datePublished": "2026-10-01T09:00:00+09:00",
      "dateModified": "2026-10-14T09:00:00+09:00",
      "mainEntityOfPage": { "@id": "https://example.com/guides/passport-renewal#webpage" }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
        { "@type": "ListItem", "position": 2, "name": "Guides", "item": "https://example.com/guides/" },
        { "@type": "ListItem", "position": 3, "name": "Passport renewal time in 2026" }
      ]
    }
  ]
}
```

## Per-type rules

| Type | What the checker wants | ID |
|---|---|---|
| Article, BlogPosting, NewsArticle | headline, author, datePublished, dateModified, image (all recommended, none required by Google) | LD-08 |
| BreadcrumbList | every ListItem has position and name; item on all but the last | LD-09 |
| Product | name plus one of offers, review, aggregateRating | LD-10 |
| Organization, WebSite | name and url | LD-11 |
| FAQPage | allowed, but no Google rich result since 2026-05-07 | LD-07 (info) |

## Values

- Dates in ISO 8601, ideally with a timezone: `2026-10-14` or `2026-10-14T09:00:00+09:00` (LD-12).
- `url`, `@id`, `item`, `image`, `logo` are absolute `https://` URLs (LD-13).
- The Article headline or WebPage name must appear in the visible `<title>` or `<h1>` (LD-14). Markup describes the page; it doesn't add claims the page doesn't make.
- No placeholders: `[Business Name]`, `REPLACE_ME`, `TODO`, lorem ipsum (LD-05).

## Don't use

HowTo, ClaimReview, CourseInfo, EstimatedSalary, LearningVideo, SpecialAnnouncement, VehicleListing, and ReadAction/BorrowAction on Book (LD-06). Google stopped showing these rich results, so they only add weight and risk.

Naver reads schema.org in JSON-LD or Microdata and recommends either, so the same block serves both engines.
