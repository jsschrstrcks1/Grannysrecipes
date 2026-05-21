# Recipe Schema — Granny's Archive

```json
{
  "id": "stable-slug-like-aunt-lindas-pound-cake",
  "collection": "granny",
  "collection_display": "Granny Hudson",
  "title": "",
  "category": "desserts",
  "attribution": "",
  "source_note": "e.g., handwritten card, magazine clipping, church cookbook",
  "description": "1–2 sentences, only if supported by text",
  "servings_yield": "",
  "prep_time": "",
  "cook_time": "",
  "total_time": "",
  "ingredients": [
    {"item": "", "quantity": "", "unit": "", "prep_note": ""}
  ],
  "instructions": [
    {"step": 1, "text": ""}
  ],
  "temperature": "",
  "pan_size": "",
  "notes": [""],
  "tags": ["dessert", "holiday", "bread", "casserole"],
  "confidence": {
    "overall": "high|medium|low",
    "flags": []
  },
  "image_refs": ["IMG_001"],
  "page_continuation": {"continues_from": "", "continues_to": ""},

  "conversions": {
    "has_conversions": true,
    "conversion_assumptions": [
      "All-purpose flour: 1 cup = 120g",
      "Granulated sugar: 1 cup = 200g",
      "Brown sugar (packed): 1 cup = 220g",
      "Butter: 1 tbsp = 14g, 1 cup = 227g",
      "Milk/liquids: 1 cup = 240ml"
    ],
    "ingredients_metric": [
      {"item": "", "quantity": "", "unit": "g|ml", "prep_note": ""}
    ],
    "temperature_c": ""
  },

  "nutrition": {
    "status": "complete|partial|insufficient_data",
    "per_serving": {
      "calories": null,
      "fat_g": null,
      "carbs_g": null,
      "protein_g": null,
      "sodium_mg": null,
      "fiber_g": null,
      "sugar_g": null
    },
    "missing_inputs": [],
    "assumptions": []
  },

  "variant_of": "",
  "variant_notes": "",
  "canonical_id": ""
}
```

## Quality Checklist

- [ ] Cross-check ingredient quantities against instructions.
- [ ] Flag implausible amounts (e.g., "4 cups salt" is probably an OCR error).
- [ ] Preserve original voice — don't over-modernize Grandma's wording.
- [ ] Verify temperatures are reasonable (most baking: 300–425°F).
- [ ] Check liquid-to-dry ratios make sense.
- [ ] Ensure baking times align with temperatures and pan sizes.

## Categories

`appetizers, beverages, breads, breakfast, desserts, mains, salads, sides, soups, snacks`

## File Naming

Convention: `category/recipe-name.md` — e.g.,
`desserts/grandmas-apple-pie.md`, `breads/buttermilk-biscuits.md`.

### Front matter

```yaml
---
title: "Recipe Title"
category: desserts
yield: "24 cookies"
prep_time: "15 minutes"
cook_time: "10 minutes"
source: "handwritten card"
tags: [cookies, nuts, holiday]
confidence: high
---
```
