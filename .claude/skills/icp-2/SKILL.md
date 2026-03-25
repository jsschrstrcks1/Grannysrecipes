---
name: icp-2
version: "2.1.0"
description: "ICP-2 — Human-First SEO & Answer Engine Optimization (AEO) standard for 2026"
type: guardrail
enforcement: block
triggers:
  - file_pattern: "**/*.html"
  - file_pattern: "*.html"
---

# ICP-2: Intelligent Content Protocol v2.1

**Successor to**: ICP-Lite v1.4
**Status**: Active standard (blocking enforcement)
**Purpose**: Every page must be findable by humans, citable by AI, and honest about what it knows.
**Principle**: Human first. No SEO theater. No AEO theater.

**Soli Deo Gloria**

---

## What Changed from v2.0

v2.1 incorporates findings from multi-LLM research (GPT + Gemini consensus audit).
Both models were asked: "What do you actually use vs. ignore?" Results:

1. **Relaxed exact-match parity** — JSON-LD description must be *consistent with* ai-summary, not character-identical. Exact-match enforcement was brittle process overhead, not AI value.
2. **Demoted content-protocol tag** — no crawler reads it. Kept for internal tooling only, removed from blocking validation.
3. **Demoted llms.txt** — not an established standard yet. Recommended, not required.
4. **Removed ai-breadcrumbs HTML comments** — both models confirmed: no crawler reads HTML comments. Remove them from pages.
5. **Removed meta keywords** — dead since 2009. Added to anti-theater forbidden list.
6. **Removed geo.region/geo.placename** — irrelevant for these sites.
7. **Added static HTML requirement** — key content must not be behind JS rendering.
8. **Added volatile data discipline** — prices, menus, policies must have as-of dates.
9. **Added multi-surface framing** — pages serve Google, AI assistants, and social previews simultaneously.

---

## The ICP-2 Checklist (Blocking)

When any `.html` file is edited, **all of the following must be true or the edit is blocked**.

### A. Required Head Meta Tags (3 blocking + 1 internal)

```html
<meta name="ai-summary" content="..."/>
<meta name="last-reviewed" content="YYYY-MM-DD"/>
<meta name="description" content="..."/>

<!-- Internal tooling only — not read by any crawler -->
<meta name="content-protocol" content="ICP-2"/>
```

**Rules**:
- `ai-summary`: max 250 chars, first 155 chars must be a complete standalone answer
- `ai-summary` must be factual, specific, no hype, no CTAs
- `last-reviewed`: must be a real date when a human last verified the content
- `description`: traditional meta description, can differ from ai-summary but must be honest
- `content-protocol`: internal only — tells our validation which standard to check against. Not blocking if missing, but should be present for tooling.

### B. Required JSON-LD Structured Data

Every page must have at minimum a JSON-LD block. Prefer specific types (`Article`, `HowTo`, `TouristDestination`) over generic `WebPage` — specific types give AI models much more to work with.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "PAGE TITLE",
  "description": "Consistent with ai-summary (not necessarily identical)",
  "dateModified": "MUST MATCH last-reviewed EXACTLY",
  "datePublished": "YYYY-MM-DD"
}
</script>
```

**Parity rules**:
- JSON-LD `description` must be **consistent with** `ai-summary` — same facts, same meaning, but doesn't need to be character-identical. (Both models confirmed: exact-match adds maintenance burden without AI benefit.)
- JSON-LD `dateModified` must **exactly match** `last-reviewed` — conflicting dates actively confuse both humans and AI about content freshness. This is data integrity.

### C. Content-Type Schema (Required for Entity Pages)

Pages about a specific thing must declare `mainEntity` with the appropriate type:

| Page Type | Schema Type | Key Properties |
|-----------|-------------|----------------|
| Ship | `Product` | name, category, manufacturer |
| Port | `TouristDestination` | name, description, geo |
| Restaurant/Venue | `FoodEstablishment` | name, servesCuisine, priceRange |
| Article/Guide | `Article` | headline, author, datePublished |
| How-To/Planning | `HowTo` | name, step[], tool[] |
| Tool/Calculator | `SoftwareApplication` | name, applicationCategory |
| Person/Author | `Person` | name, jobTitle, knowsAbout |
| Hub/Index | `CollectionPage` | name, description |

### D. Answer-First Body Structure

1. **First paragraph must answer**: What is this? Why does it matter? What can I do here?
   - For complex topics that need context before the answer, lead with a brief orienting sentence, then answer.
2. **Semantic headings**: H2/H3 mapped to real user questions (naturally, not stuffed)
3. **Internal linking**: Every page links to 2+ related pages (ships link ports, ports link ships)
4. **AI-extractable formatting**: Use HTML tables for comparisons and data, ordered lists for steps/rankings, unordered lists for features/options. AI models extract structured HTML (tables, lists, heading hierarchies) more reliably than prose paragraphs. This isn't about formatting for crawlers — it's about making content scannable for humans AND parseable for AI simultaneously.
5. **Semantic HTML5 elements**: Use `<article>`, `<section>`, `<nav>`, `<aside>` to segment content. These help AI identify which part of the page contains the primary content vs. navigation vs. supplementary material.

### E. Static HTML Content (New in v2.1)

Key content — the text a human reads, the facts an AI cites — must be in the static HTML. Do not hide content behind JavaScript rendering, client-side fetch, or dynamic injection. If a search engine or AI crawler can't see it without executing JS, it doesn't exist.

### F. Canonical URL (Required)

```html
<link rel="canonical" href="https://DOMAIN/exact-path.html"/>
```

### G. OpenGraph + Social (Required for public-facing sites)

Only applies to repos with public websites (InTheWake, flickersofmajesty). Recipe repos, sheep repo, and sermon repo are exempt unless they have public pages.

```html
<meta property="og:title" content="..."/>
<meta property="og:description" content="..."/>
<meta property="og:url" content="..."/>
<meta property="og:image" content="..."/>
<meta property="og:type" content="website"/>
```

---

## AEO-Specific Requirements

### 1. Zero-Click Optimization

The `ai-summary` is the page's "answer" for AI citation. Write it as if an AI assistant will read it aloud as the complete answer to someone's question.

**Test**: "If an AI reads only this summary to a user, would they get an accurate, useful answer?"

**Multi-surface reality**: This summary serves Google snippets, AI Overviews, ChatGPT citations, Perplexity answers, and social share previews simultaneously. Write it for all of them — which means write it for humans.

**How AI actually uses your content (March 2026)**: AI models increasingly *synthesize* from multiple sources rather than *extracting* verbatim snippets. This means your page may inform an AI answer without being quoted directly. The best strategy is the same one that works for humans: be the most accurate, specific, and well-structured source on the topic. Original data, unique statistics, and firsthand experience are what make your content indispensable — AI can't synthesize what doesn't exist elsewhere.

### 2. AI Crawler Access

`robots.txt` must explicitly allow AI crawlers:

```
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /
```

Do NOT block AI crawlers unless there is a specific, documented reason.

### 3. llms.txt (Recommended, Not Required)

If the site has a public presence, a `/llms.txt` at site root is recommended containing:
- Site overview (what it is, who it's for)
- Content scope and limitations
- Author credentials (E-E-A-T)
- Citation preference (how to attribute)
- Key content sections with entry points
- What the site does NOT do (no booking, no affiliate sales)

**Note**: Both GPT and Gemini confirmed llms.txt is not an established standard. It may be ignored. Include it as a low-cost bet, not a requirement.

### 4. Freshness Honesty

- Sitemap `lastmod` must reflect **actual** last content modification per page
- No uniform timestamps across all pages
- `last-reviewed` in HTML must match reality
- Stale content (>6 months without review) should be flagged for update

### 5. Volatile Data Discipline (New in v2.1)

When content includes prices, menus, operating hours, policies, or any fact that changes:

- **As-of date** must be visible (YYYY-MM-DD)
- **Verification posture** stated: "Verified in Cruise Planner" / "Observed onboard" / "Community-reported"
- **Disclaimer**: "Subject to change without notice"

This is not SEO theater — both AI models and humans need to know when time-sensitive data was last checked.

### 6. Multimedia Metadata (New in v2.1)

Images, video, and audio are increasingly processed by AI. Help them:
- **Images**: Descriptive `alt` text that states what's in the image factually (not "beautiful sunset photo" — instead "Ship wake at sunrise departing Port Canaveral"). Use WebP format, lazy loading for below-fold.
- **Video**: If embedded, include transcript text in static HTML. AI can't watch videos.
- **Captions**: Table/chart captions should state what the data shows, not just label it.

This isn't about stuffing keywords into alt text — it's about making visual content accessible to both screen readers and AI simultaneously.

### 7. E-E-A-T Author Authority

- Author pages must exist with `Person` schema
- `knowsAbout` must list specific, real expertise areas (not aspirational)
- `sameAs` should link to other presences **only if they actually exist and are active** — do not create social profiles just for SEO
- Content pages should link back to author where it makes sense for the reader (not forced into every page footer for crawlers)

---

## What NOT To Do (Anti-Patterns)

These are theater. ICP-2 explicitly forbids them:

### SEO Theater
1. **Keyword stuffing** — writing for algorithms instead of humans
2. **Fake freshness** — updating `lastmod` without actually reviewing content
3. **Schema spam** — adding structured data that doesn't match visible content
4. **Meta keywords** — dead since 2009, no engine reads them. Remove if present.
5. **Link farming** — artificial internal linking that doesn't help navigation
6. **Forced FAQs** — adding FAQPage schema to pages without genuine Q&A content
7. **Geo meta tags** — `geo.region`, `geo.placename` on non-local sites

### AEO Theater
8. **ai-breadcrumbs HTML comments** — no AI crawler reads HTML comments. Both GPT and Gemini confirmed. Remove them.
9. **AI-blocking** — blocking AI crawlers out of fear rather than policy
10. **Generic summaries** — ai-summary that could apply to any page on the internet
11. **Speculative standards** — ai-plugin.json, .well-known/ai, or other standards that don't exist yet
12. **Exact-match meta gymnastics** — forcing character-identical text across multiple tags adds maintenance burden, not AI value. Be consistent, not identical.
13. **Social profile farming** — creating social accounts just to populate `sameAs` links
14. **JS-hidden content** — putting key content behind JavaScript rendering where crawlers can't reach it

---

## ai-summary Writing Guide

### Templates by Page Type

**Ship**: `[Ship Name] is a [Class] ship ([GT] GT, [capacity] guests, [year]) featuring [2-3 signature features] and [itinerary type] itineraries.`

**Port**: `[Port Name] features [signature experience]. [Key fact]. [What cruisers do here].`

**Restaurant**: `[Name] is [line]'s [type] ([surcharge/included]) featuring [signature items] [availability].`

**Tool**: `[Tool name] helps cruisers [primary benefit]. [What it does in one sentence].`

**Article**: `[Topic] — [key insight or answer]. [Why it matters for cruise planning].`

**Hub**: `[Action verb] all [entity type] by [filters]. [Scope/count].`

### Rules
- Lead with the most important fact
- Use exact numbers (GT, capacity, year, price)
- No marketing language ("amazing", "best", "incredible")
- No CTAs ("book now", "learn more", "click here")
- No vague qualifiers ("many", "several", "various")
- First 155 chars must be a complete thought
- Total max 250 chars

---

## Validation Procedure (Blocking)

When this skill fires on an HTML file edit, check in order:

1. **`ai-summary` exists** and is <= 250 chars
2. **`last-reviewed` exists** and is valid YYYY-MM-DD
3. **`description` meta tag exists**
4. **JSON-LD block exists** with `@type`
5. **JSON-LD `description` is consistent with `ai-summary`** (same facts/meaning)
6. **JSON-LD `dateModified` matches `last-reviewed`** exactly
7. **Canonical URL exists**
8. **Key content is in static HTML** (not behind JS rendering)
9. **OpenGraph tags exist** (og:title, og:description, og:url) — public sites only
10. **First paragraph** is answer-first (not "Welcome to..." or "This page...")
11. **No forbidden anti-patterns** present (meta keywords, ai-breadcrumbs comments)

If ANY check fails:
- **Report the specific failure(s)**
- **Show what needs to be fixed**
- **Block the edit until fixed**

If all checks pass:
- **Confirm ICP-2 compliance**
- **Note any optional enhancements available** (mainEntity, BreadcrumbList, FAQPage, llms.txt)

---

## Migration from ICP-Lite v1.4

Pages with `content-protocol="ICP-Lite v1.4"` are allowed during migration. When editing such a page:
1. Update to ICP-2 compliance
2. Change protocol tag to `ICP-2`
3. Add any missing content-type schema
4. Verify freshness dates are accurate
5. Remove `ai-breadcrumbs` HTML comments if present
6. Remove `meta name="keywords"` if present
7. Remove `meta name="geo.region"` / `geo.placename` if present

---

## Maintenance Schedule

- **On every edit**: ICP-2 validation fires (blocking)
- **Monthly**: Review hub pages for accuracy
- **Quarterly**: Review entity pages (ships, ports)
- **On creation**: New pages must be ICP-2 compliant from the start
- **Annually**: Review llms.txt and reassess emerging standards

---

**End of ICP-2 v2.1 Protocol**
