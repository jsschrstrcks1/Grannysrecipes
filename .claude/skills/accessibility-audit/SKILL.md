---
name: accessibility-audit
description: "Audits WCAG 2.1 AA compliance for Granny Hudson's Kitchen — validates image alt text, color contrast, heading hierarchy, form labels, keyboard navigation, and screen reader compatibility on recipe pages."
version: 1.0.0
---

# Accessibility Audit — Granny Hudson's Kitchen

> These recipes are for everyone — including those who use screen readers, keyboard navigation, or assistive technology.

## Purpose

Validates WCAG 2.1 AA compliance across the recipe website pages: index.html, recipe.html. Ensures recipe content, search features, and interactive elements are accessible to all users.

## When to Fire

- After Edit/Write of any `.html` or `.css` file
- On `/a11y` command
- Before deployment
- When adding interactive features (search, calculators, filters)

## Recipe-Specific Accessibility Concerns

### Recipe Image Alt Text
- Handwritten recipe card images: alt text should describe the recipe name and that it's a handwritten card
- "Grandma Baker's handwritten recipe card for buttermilk biscuits" — NOT "recipe-card-042.jpeg"
- Food photography: describe the finished dish, not just "food photo"
- If the image IS the recipe (handwritten card), alt text must convey that this is the primary source

### Recipe Data Presentation
- Ingredient lists must use semantic `<ul>` or `<ol>`, not `<div>` stacks
- Instruction steps must use ordered lists `<ol>`
- Nutrition facts (if present) should use a `<table>` with proper headers
- Serving size, prep time, and cook time should be in a `<dl>` or labeled with ARIA

### Search and Filtering
- Search inputs need visible `<label>` elements
- Filter controls need ARIA labels
- Search results must be announced to screen readers (aria-live region)
- Category filters must be keyboard-navigable

## WCAG 2.1 AA Checklist

### 1. Images (`<img>`)
- [ ] Every `<img>` has meaningful `alt` text (not just filename)
- [ ] Decorative images use `alt=""` and `role="presentation"`
- [ ] Recipe card images have descriptive alt text including recipe name

### 2. Color Contrast
- [ ] Normal text: 4.5:1 contrast ratio minimum
- [ ] Large text (≥18pt or ≥14pt bold): 3:1 minimum
- [ ] Recipe headings are readable against background
- [ ] Link text is distinguishable from body text (not just by color)
- [ ] `[UNCLEAR]` markers are visually distinct AND accessible

### 3. Heading Hierarchy
- [ ] Single `<h1>` per page (site/page title)
- [ ] Recipe title is `<h2>`
- [ ] Sections (Ingredients, Instructions, Notes) are `<h3>`
- [ ] No skipped levels (h1→h3 without h2)

### 4. Keyboard Navigation
- [ ] All interactive elements reachable via Tab
- [ ] Focus indicators visible on all focusable elements
- [ ] Skip-to-content link present
- [ ] Recipe navigation (prev/next) keyboard accessible
- [ ] Modal dialogs trap focus correctly

### 5. Forms and Inputs
- [ ] Search input has `<label>` (visible or sr-only)
- [ ] Form errors are announced to screen readers
- [ ] Required fields marked with both visual indicator AND aria-required

### 6. Screen Reader Compatibility
- [ ] Landmark roles: `<header>`, `<main>`, `<nav>`, `<footer>`
- [ ] Recipe schema data accessible (not just in JSON-LD)
- [ ] Dynamic content changes announced via aria-live regions

### 7. Print Accessibility (Ebook)
- [ ] `ebook/book.html` has proper heading hierarchy
- [ ] Print CSS doesn't hide essential content
- [ ] Table of contents uses semantic list structure

## Audit Report Format

```
## Accessibility Audit — Granny Hudson's Kitchen
**Date:** [YYYY-MM-DD]
**Pages checked:** [list]
**WCAG Level:** 2.1 AA

| # | Issue | Page | Element | WCAG Criterion | Fix |
|---|-------|------|---------|---------------|-----|
| 1 | Missing alt text | recipe.html | img#card-042 | 1.1.1 | Add descriptive alt |

**Summary:** [X issues found, Y critical, Z minor]
```

## Integration

- **seo-schema-audit** — Schema validation complements a11y (structured data helps screen readers)
- **ebook-builder** — Ebook HTML must pass a11y checks too
- **careful-not-clever** — Accessibility is not optional. Don't skip it to save time.

---

*Soli Deo Gloria* — These recipes belong to everyone in the family, including those who experience them differently.
