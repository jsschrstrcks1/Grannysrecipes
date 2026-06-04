---
name: seo-schema-audit
description: "Validates JSON-LD structured data, Open Graph, Twitter Cards, and AI meta tags for recipe content"
version: 1.0.0
---

# SEO Schema Audit — Recipe Content

## Purpose

Audit and validate structured data markup across recipe pages. This skill ensures JSON-LD schemas, Open Graph tags, Twitter Cards, and AI-oriented meta tags are complete, accurate, and compliant with schema.org specifications and ICP-2 requirements.

## When to Fire

- When creating or editing any HTML page or template
- When adding or modifying JSON-LD structured data
- When updating Open Graph or Twitter Card meta tags
- When reviewing pages for SEO compliance
- When prompted with `/seo-schema-audit` or asked to audit structured data
- Before any page goes live or is merged to production
- When adding or updating recipe pages

## Instructions

### 1. JSON-LD Structured Data Validation

Validate all JSON-LD `<script type="application/ld+json">` blocks against schema.org specs. Focus on the Recipe schema type:

#### Recipe Schema
**Required properties:**
- `@type`: "Recipe"
- `name`: Must match the visible recipe title on the page
- `image`: At least one image URL (multiple images recommended for rich results)
- `author`: Must include `@type` ("Person" or "Organization") and `name`
- `datePublished`: ISO 8601 format (e.g., `2026-03-15`)
- `description`: Must be present and match visible recipe description
- `recipeIngredient`: Array of strings, each a single ingredient line; must match the visible ingredient list exactly
- `recipeInstructions`: Array of `HowToStep` objects, each with `@type: "HowToStep"` and `text`; must match visible steps

**Required for rich results (treat as required):**
- `prepTime`: ISO 8601 duration format (e.g., "PT15M" for 15 minutes)
- `cookTime`: ISO 8601 duration format
- `totalTime`: ISO 8601 duration format; must equal prepTime + cookTime (or be explicitly stated)
- `recipeYield`: Serving size (e.g., "4 servings" or "12 cookies")
- `recipeCategory`: Meal type (e.g., "Dinner", "Dessert", "Appetizer")
- `recipeCuisine`: Cuisine type (e.g., "Italian", "Southern", "Mexican")

**Recommended properties:**
- `keywords`: Comma-separated or array of relevant terms
- `aggregateRating`: If reviews/ratings are displayed, must include `ratingValue` and `ratingCount` or `reviewCount`
- `review`: Individual reviews with `author`, `datePublished`, `reviewBody`, `reviewRating`
- `video`: If a recipe video exists, must include `name`, `description`, `thumbnailUrl`, `uploadDate`
- `suitableForDiet`: Use schema.org diet enumerations (e.g., "https://schema.org/GlutenFreeDiet")

#### NutritionInformation (nested within Recipe)
**When nutrition data is displayed on the page, the schema must include:**
- `@type`: "NutritionInformation"
- `calories`: Format as "XXX calories" (e.g., "350 calories")
- `fatContent`, `saturatedFatContent`, `cholesterolContent`, `sodiumContent`, `carbohydrateContent`, `fiberContent`, `sugarContent`, `proteinContent`: Each as a string with unit (e.g., "12 g")

**Validation rules for NutritionInformation:**
- Values in schema must match values displayed on the page
- If any nutrition field is displayed on the page, it must appear in the schema
- Do not include NutritionInformation in schema if no nutrition data is visible on the page

#### HowToStep Validation
- Each `recipeInstructions` entry should be a `HowToStep` (not plain strings)
- Step order in schema must match visible step order
- Optional but recommended: `name` (step title), `image`, `url` (anchor to step)
- For grouped steps, use `HowToSection` with `@type`, `name`, and `itemListElement` containing `HowToStep` entries

### 2. Nested Schema Handling

- NutritionInformation must be nested within the Recipe schema as the `nutrition` property
- If the page also includes Article-like content (e.g., a story before the recipe), use `@graph` to contain both Recipe and Article schemas, linked via `@id`
- If a recipe includes a video, the VideoObject should be nested within the Recipe schema as the `video` property
- Multiple schemas on a single page must be properly linked and not duplicate data
- Validate that nested schemas do not contradict parent schema data

### 3. Open Graph Validation

Check for all required `<meta property="og:...">` tags:

- `og:title` — Must be present, 60-90 characters recommended
- `og:description` — Must be present, 100-200 characters recommended
- `og:image` — Must be a valid, absolute URL; minimum 1200x630px recommended; should be an appetizing photo of the finished dish
- `og:url` — Must match the canonical URL exactly
- `og:type` — Must be present (typically "article" for recipe pages)
- `og:site_name` — Should match the site's proper name

### 4. Twitter Card Validation

Check for all required `<meta name="twitter:...">` tags:

- `twitter:card` — Must be "summary_large_image" (preferred for recipe content) or "summary"
- `twitter:title` — Must be present
- `twitter:description` — Must be present
- `twitter:image` — Must be a valid, absolute URL; use the primary recipe photo

### 5. AI Meta Tags — ICP-2 Compliance

Validate presence and quality of AI-oriented meta tags:

- `<meta name="ai:summary">` — Must be present; concise summary of the recipe (1-2 sentences)
- `<meta name="ai:target-audience">` — Must be present; should describe the intended cook (e.g., "home cooks looking for quick weeknight dinner ideas")
- Content of these tags must accurately reflect the page's actual content

### 6. Stale Content Detection

Check for `<meta name="last-reviewed">` or `dateModified` in JSON-LD:

- Flag any page where `last-reviewed` or `dateModified` is older than 90 days from the current date
- Report the exact date found and how many days stale it is
- Seasonal recipes (holiday dishes, summer grilling) should be reviewed before their relevant season

### 7. Canonical URL Verification

- `<link rel="canonical">` must be present on every page
- The canonical URL must match the actual file path / route of the page
- `og:url` must match the canonical URL
- `mainEntityOfPage` in JSON-LD should reference the canonical URL
- No trailing slashes unless the site convention uses them consistently

### 8. Data Type Validation

- **Dates**: All dates must be valid ISO 8601 (YYYY-MM-DD or full datetime)
- **Durations**: Must be valid ISO 8601 duration (e.g., "PT30M", "PT1H15M"); reject malformed values like "30 minutes"
- **URLs**: All URLs in schema must be absolute and reachable
- **Currency** (if applicable, e.g., cost per serving): Must use ISO 4217 codes
- **Ratings**: `ratingValue` must be within `bestRating`/`worstRating` bounds
- **Nutrition values**: Must include units (e.g., "12 g", "350 calories")

### 9. Semantic Accuracy Checks

- Schema `name` must match the visible recipe title
- Schema `description` should align with the meta description and visible introductory text
- Schema `image` URLs should reference images actually displayed on the page
- `recipeIngredient` array must match the visible ingredient list — no missing or extra items
- `recipeInstructions` steps must match visible instructions in order and content
- Nutrition values in schema must match displayed nutrition information exactly
- `recipeYield` must match the displayed serving size
- `prepTime`, `cookTime`, and `totalTime` must match displayed times
- Author information must match any visible byline
- Watch for conflicting information between schema markup and displayed page content

### 10. Reporting Format

For each page audited, produce a report structured as:

```
## Schema Audit: [Page Title]

### Schemas Found
- [List each schema type detected]

### Errors (must fix)
- [ ] [Error description with line reference]

### Warnings (should fix)
- [ ] [Warning description with recommendation]

### Passed Checks
- [x] [Check description]
```

Prioritize errors over warnings. Group findings by schema type. For Recipe pages, always verify the complete ingredient and instruction chains match visible content.

---

*Soli Deo Gloria*
