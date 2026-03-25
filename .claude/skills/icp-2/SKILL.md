---
name: icp-2
version: "2.0.0"
description: "ICP-2 — Human-First SEO & Answer Engine Optimization (AEO) standard for 2026"
type: guardrail
enforcement: block
triggers:
  - file_pattern: "**/*.html"
  - file_pattern: "*.html"
---

# ICP-2: Intelligent Content Protocol v2.0

**Successor to**: ICP-Lite v1.4
**Status**: Active standard (blocking enforcement)
**Purpose**: Every page must be findable by humans, citable by AI, and honest about what it knows.
**Principle**: Human first. No SEO theater.

**Soli Deo Gloria**

---

## What Changed from ICP-Lite v1.4

ICP-2 keeps everything good from v1.4 and adds the 2026 reality:

1. **Answer Engine Optimization (AEO)** — pages must be structured for AI citation, not just Google ranking
2. **Content-type schema** — `Article`, `HowTo`, `TouristDestination` required where applicable (not just `WebPage`)
3. **Freshness honesty** — per-page `lastmod` in sitemap, no uniform timestamps
4. **llms.txt expansion** — citation guidelines, content pillars, author authority
5. **Zero-click readiness** — `ai-summary` optimized as the ideal AI-cited answer
6. **AI crawler access** — robots.txt must not block GPTBot, ClaudeBot, PerplexityBot, Google-Extended
7. **Blocking enforcement** — non-compliance is a hard stop, not a suggestion
8. **No speculative standards** — we don't implement ai-plugin.json, .well-known/ai, or other standards that don't exist yet. When a real standard emerges, we'll adopt it.

---

## The ICP-2 Checklist (Blocking)

When any `.html` file is edited, **all of the following must be true or the edit is blocked**.

### A. Required Head Meta Tags (4)

```html
<!-- ICP-2 -->
<meta name="ai-summary" content="..."/>
<meta name="last-reviewed" content="YYYY-MM-DD"/>
<meta name="content-protocol" content="ICP-2"/>
<meta name="description" content="..."/>
```

**Rules**:
- `ai-summary`: max 250 chars, first 155 chars must be a complete standalone answer
- `ai-summary` must be factual, specific, no hype, no CTAs
- `last-reviewed`: must be a real date when a human last verified the content
- `content-protocol`: internal tooling tag, must say `ICP-2` (or `ICP-Lite v1.4` during migration). No crawler reads this — it exists so our own validation knows which standard to check against.
- `description`: traditional meta description, can differ from ai-summary but must be honest

### B. Required JSON-LD Structured Data

Every page must have at minimum:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "PAGE TITLE",
  "description": "MUST MATCH ai-summary EXACTLY",
  "dateModified": "MUST MATCH last-reviewed EXACTLY",
  "datePublished": "YYYY-MM-DD"
}
</script>
```

**Parity rules** (blocking):
- JSON-LD `description` must exactly match `ai-summary` meta tag
- JSON-LD `dateModified` must exactly match `last-reviewed` meta tag

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
2. **Semantic headings**: H2/H3 mapped to real user questions (naturally, not stuffed)
3. **Internal linking**: Every page links to 2+ related pages (ships link ports, ports link ships)

### E. Canonical URL (Required)

```html
<link rel="canonical" href="https://DOMAIN/exact-path.html"/>
```

### F. OpenGraph + Social (Required for public-facing sites)

Only applies to repos with public websites (InTheWake, flickersofmajesty). Recipe repos, sheep repo, and sermon repo are exempt unless they have public pages.

```html
<meta property="og:title" content="..."/>
<meta property="og:description" content="..."/>
<meta property="og:url" content="..."/>
<meta property="og:image" content="..."/>
<meta property="og:type" content="website"/>
```

---

## AEO-Specific Requirements (New in ICP-2)

### 1. Zero-Click Optimization

The `ai-summary` is the page's "answer" for AI citation. Write it as if an AI assistant will read it aloud as the complete answer to someone's question.

**Test**: "If an AI reads only this summary to a user, would they get an accurate, useful answer?"

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

### 3. llms.txt Requirements

The site root must have `/llms.txt` containing:
- Site overview (what it is, who it's for)
- Content scope and limitations
- Author credentials (E-E-A-T)
- Citation preference (how to attribute)
- Key content sections with entry points
- What the site does NOT do (no booking, no affiliate sales)

### 4. Freshness Honesty

- Sitemap `lastmod` must reflect **actual** last content modification per page
- No uniform timestamps across all pages
- `last-reviewed` in HTML must match reality
- Stale content (>6 months without review) should be flagged for update

### 5. E-E-A-T Author Authority

- Author pages must exist with `Person` schema
- `knowsAbout` must list specific, real expertise areas (not aspirational)
- `sameAs` should link to other presences **only if they actually exist and are active** — do not create social profiles just for SEO
- Content pages should link back to author where it makes sense for the reader (not forced into every page footer for crawlers)

---

## What NOT To Do (Anti-Patterns)

These are SEO theater. ICP-2 explicitly forbids them:

1. **Keyword stuffing** — writing for algorithms instead of humans
2. **Fake freshness** — updating `lastmod` without actually reviewing content
3. **Schema spam** — adding structured data that doesn't match visible content
4. **Meta-tag gymnastics** — stuffing meta keywords or invisible text
5. **Link farming** — artificial internal linking that doesn't help navigation
6. **Forced FAQs** — adding FAQPage schema to pages without genuine Q&A content
7. **AI-blocking** — blocking AI crawlers out of fear rather than policy
8. **Generic summaries** — ai-summary that could apply to any page on the internet

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
3. **`content-protocol` exists** and says `ICP-2` or `ICP-Lite v1.4`
4. **`description` meta tag exists**
5. **JSON-LD block exists** with `@type`
6. **JSON-LD `description` matches `ai-summary`** exactly
7. **JSON-LD `dateModified` matches `last-reviewed`** exactly
8. **Canonical URL exists**
9. **OpenGraph tags exist** (og:title, og:description, og:url)
10. **First paragraph** is answer-first (not "Welcome to..." or "This page...")

If ANY check fails:
- **Report the specific failure(s)**
- **Show what needs to be fixed**
- **Block the edit until fixed**

If all checks pass:
- **Confirm ICP-2 compliance**
- **Note any optional enhancements available** (mainEntity, BreadcrumbList, FAQPage)

---

## Migration from ICP-Lite v1.4

Pages with `content-protocol="ICP-Lite v1.4"` are allowed during migration. When editing such a page:
1. Update to ICP-2 compliance
2. Change protocol tag to `ICP-2`
3. Add any missing content-type schema
4. Verify freshness dates are accurate

---

## Maintenance Schedule

- **On every edit**: ICP-2 validation fires (blocking)
- **Monthly**: Review hub pages for accuracy
- **Quarterly**: Review entity pages (ships, ports)
- **On creation**: New pages must be ICP-2 compliant from the start
- **Annually**: Review and update llms.txt

---

**End of ICP-2 Protocol**
