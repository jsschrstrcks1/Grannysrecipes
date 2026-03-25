---
name: content-freshness
description: "Tracks content freshness across Granny Hudson's Kitchen web pages. Flags stale pages, monitors recipe data currency, and ensures the website reflects the latest transcription work."
version: 1.0.0
---

# Content Freshness — Granny Hudson's Kitchen

> A family recipe website should reflect the family's latest work.

## Purpose

Tracks whether the website pages are current with the underlying recipe data. Flags pages that haven't been regenerated after data changes, stale `last-reviewed` dates, and recipes that may need re-transcription.

## When to Fire

- On `/freshness` command
- At session start (quick check)
- After bulk recipe data updates

## Freshness Checks

### 1. Page vs. Data Currency
- Compare `index.html` generation date against latest recipe data modification
- If recipes were added/modified since the page was last built, flag for regeneration
- Check if `ebook/book.html` is current with recipe data

### 2. Last-Reviewed Meta Tags
- Scan `<meta name="last-reviewed">` on all HTML pages
- Flag any page not reviewed in >90 days
- Priority: `index.html` > `recipe.html` > `ebook/book.html`

### 3. Transcription Currency
- Check for recipes still marked `[UNCLEAR]` that may have been resolved
- Flag recipes with `transcription_date` older than 6 months (may benefit from re-review with improved image processing)
- Check for new source images in `data/` that haven't been transcribed yet

### 4. Script Currency
- Check if `scripts/validate-recipes.py` has been run recently
- Check if nutrition estimates are current (if nutrition-estimator skill is active)
- Check if search indexes are rebuilt after data changes

## Freshness Report Format

```
## Freshness Report — Granny Hudson's Kitchen — [date]

### Page Currency
| Page | Last Updated | Data Last Modified | Status |
|------|-------------|-------------------|--------|
| index.html | 2026-03-01 | 2026-03-20 | ⚠️ Stale |
| ebook/book.html | 2026-02-15 | 2026-03-20 | ⚠️ Stale |

### Transcription Status
- Recipes with [UNCLEAR]: [count]
- Unprocessed images: [count]
- Last transcription session: [date]

### Overall: [Fresh / Slightly Stale / Needs Attention]
```

## Integration

- **recipe-validation** — Validation should run on stale data before declaring fresh
- **ebook-builder** — Stale ebook triggers regeneration recommendation
- **nutrition-estimator** — Stale nutrition data flagged
- **cognitive-memory** — Remember freshness state across sessions

---

*Soli Deo Gloria* — Faithful stewardship means keeping the archive current.
