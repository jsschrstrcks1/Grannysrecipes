---
name: link-integrity
description: "Validates internal links, image references, and page connectivity for Granny Hudson's Kitchen. Catches broken recipe links, missing images, and dead anchors."
version: 1.0.0
---

# Link Integrity — Granny Hudson's Kitchen

> A broken link to a recipe is a lost family memory.

## Purpose

Validates that all internal links, image references, and cross-page connections work correctly across the recipe website.

## When to Fire

- After Edit/Write of any `.html` file
- On `/links` command
- When renaming or reorganizing recipe data files
- Before deployment

## Site Structure

```
index.html          — Recipe listing / search page
recipe.html         — Individual recipe display (dynamic)
ebook/book.html     — Printable cookbook
ebook/print.css     — Print styles
data/               — Recipe images and JSON data
scripts/            — Processing scripts
```

## Check Categories

### 1. Internal Page Links
- `index.html` → `recipe.html` (with recipe ID parameter)
- `recipe.html` → `index.html` (back to listing)
- Navigation links (if present)
- Ebook table of contents → recipe anchors

### 2. Recipe Image References
- Every `<img src>` in recipe display resolves to an actual file in `data/`
- Recipe JSON image paths match actual filenames
- Processed image paths (`data/processed/`) are preferred over originals
- Ebook image references resolve

### 3. Script References
- `<script src>` tags point to existing files
- CSS `<link>` tags point to existing stylesheets
- Service worker references (if present) resolve

### 4. Data Integrity
- Recipe IDs referenced in HTML exist in recipe JSON
- Category filters reference valid categories
- Search index references match actual recipe data

### 5. Ebook Internal Links
- Table of contents anchors match recipe `id` attributes in `book.html`
- Category section links resolve
- Print CSS `url()` references resolve

## Audit Report Format

```
## Link Integrity — Granny Hudson's Kitchen — [date]
**Files checked:** [count]
**Broken:** [count]

| Source | Link/Reference | Issue |
|--------|---------------|-------|
| recipe.html | data/img-042.jpeg | File not found |
```

## Integration

- **recipe-validation** — Data integrity overlaps with link integrity
- **ebook-builder** — Ebook links must be validated after generation
- **seo-schema-audit** — Canonical URLs must be valid links
- **careful-not-clever** — Don't silently fix broken links. Report them.

---

*Soli Deo Gloria* — Every link is a path to a family recipe. Keep them all working.
