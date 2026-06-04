---
name: ebook-builder
description: "Generates and maintains the printable recipe ebook from recipe data. Handles table of contents, category grouping, print CSS, and collection-specific branding for Granny Hudson's Kitchen."
version: 1.0.0
---

# Ebook Builder — Granny Hudson's Kitchen

> From JSON to a cookbook the family can hold.

## Purpose

Generates `ebook/book.html` from recipe data, producing a print-ready cookbook that honors the family's recipes with proper formatting, categorization, and branding.

## When to Fire

- On `/ebook` command
- After significant recipe data changes (batch transcription, category reorganization)
- When the user asks to generate or update the cookbook

## Input

- **Recipe data:** `data/recipes*.json` (check for `recipes_master.json`, `recipes.json`, or sharded files)
- **Print styles:** `ebook/print.css`
- **Output:** `ebook/book.html`

## Generation Rules

### Structure
1. **Cover page** — Collection title, "Granny Hudson's Kitchen", family attribution
2. **Table of contents** — Grouped by category, alphabetized within each category
3. **Recipe pages** — One recipe per logical page (use CSS page-break-after)
4. **Index** — Alphabetical recipe listing at the end

### Per-Recipe Layout
```html
<div class="recipe" data-category="{category}">
  <h2>{title}</h2>
  <div class="recipe-meta">
    <span class="category">{category}</span>
    <span class="source">Granny Hudson</span>
  </div>
  <div class="ingredients">
    <h3>Ingredients</h3>
    <ul><!-- ingredient list --></ul>
  </div>
  <div class="instructions">
    <h3>Instructions</h3>
    <ol><!-- step list --></ol>
  </div>
  <div class="notes"><!-- if notes exist --></div>
</div>
```

### Print Optimization
- Page breaks between recipes (`page-break-after: always`)
- No orphaned headings (keep with next)
- Images sized for print (max-width: 4in for recipe cards)
- Margins: 0.75in all sides
- Font size: 11pt body, 14pt recipe titles

### Data Validation
Before generating, verify:
- All recipe IDs are unique
- All categories are valid
- No empty ingredient lists
- No `[UNCLEAR]` markers without notes explaining them
- Image references (if included) resolve to actual files

### Handling [UNCLEAR] Markers
- Include them in the ebook with visual highlighting
- Add a footnote: "This text was unclear in the original — see handwritten card"
- Do NOT remove or guess — these are honest markers of source fidelity

## Categories

Standard categories: appetizers, beverages, breads, breakfast, desserts, mains, salads, sides, soups, snacks

## Regeneration

Full regeneration replaces `ebook/book.html` entirely. Always:
1. Read current recipe data
2. Sort by category, then alphabetically
3. Generate complete HTML
4. Validate output (all recipes present, no broken references)
5. Report: recipes included, categories, any warnings

---

*Soli Deo Gloria* — These recipes are a family's heritage, and this cookbook is how we preserve them.
