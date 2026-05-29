#!/usr/bin/env python3
"""
Hand-merge artifact for PR #21 (Process remaining images: add 6 recipes, delete 10 magazine clippings).

This script applies the additions from PR #21 to the CURRENT main state of
granny/recipes_master.json without losing any data already present on main.

WHY THIS EXISTS:
PR #21 was opened on 2026-01-23 against a much earlier state of main. Since
then, several other PRs have landed (notably claude/setup-recipe-workflow-0Npdl)
that re-canonicalized many recipes — populating image_refs that PR #21 had
empty, splitting/renaming ingredient-id variants, etc. A naive merge of PR #21
into current main would REVERT those improvements (set image_refs back to []
on dozens of recipes), which is data loss we explicitly want to avoid.

WHAT THIS APPLIES:
  - 2 new recipes that PR #21 genuinely adds (cornish-game-hens, stuffed-peppers)
  - Targeted image_refs UNIONS on 5 existing recipes (only adds, never removes)
  - Targeted notes UNIONS on 7 existing recipes (only adds, never removes)

WHAT THIS DOES NOT TOUCH:
  - The 5 IDs that PR head accidentally duplicated. Main already has the
    canonical version with proper image_refs.
  - Any recipe where PR head was simply stale relative to main.
  - granny/ingredient-index.json — re-run scripts/build-ingredient-index.py
    after applying this merge.

HOW TO APPLY:
  cd <Grannysrecipes repo on current main>
  python3 scripts/_merge_artifacts/apply_pr21_merge.py
  python3 scripts/validate-recipes.py   # should pass
  python3 scripts/build-ingredient-index.py
  git add granny/recipes_master.json granny/ingredient-index.json
  git commit -m "Merge PR #21 additions: 2 new recipes + 11 small unions (manual 3-way merge)"

  # Then in GitHub UI: close PR #21 with comment linking to this commit.

  # Optionally also delete the magazine-clipping images that the PR documented:
  #   IMG_4392..IMG_4401 in granny/ and granny/processed/ — only if no other
  #   recipe references them. The script does NOT delete images; review first.
"""

import json
import sys
from pathlib import Path

NEW_RECIPES = [
  {
    "id": "stuffed-peppers-granny",
    "collection": "granny",
    "collection_display": "Granny Hudson",
    "title": "Stuffed Peppers",
    "category": "mains",
    "description": "Classic stuffed bell peppers with ground beef and rice.",
    "temperature": "350°F (175°C)",
    "ingredients": [
      {"item": "big green peppers", "quantity": "4", "unit": ""},
      {"item": "lean hamburger", "quantity": "1-1/4", "unit": "lb"},
      {"item": "chopped onions", "quantity": "1/2", "unit": "cup"},
      {"item": "garlic", "quantity": "1", "unit": "tbsp", "prep_note": "minced"},
      {"item": "egg", "quantity": "1", "unit": ""},
      {"item": "Minute Rice", "quantity": "1/3", "unit": "cup", "prep_note": "boxed"},
      {"item": "milk", "quantity": "1/3", "unit": "cup"},
      {"item": "condensed tomato soup", "quantity": "1", "unit": "large can", "prep_note": "Campbell's family size"}
    ],
    "instructions": [
      {"step": 1, "text": "Wash peppers and cut tops off."},
      {"step": 2, "text": "Put in pepper loosely: hamburger mixed with onions, garlic, egg, rice, and milk."},
      {"step": 3, "text": "Put on top: 1 large can tomato Campbell's sauce condensed family soup."},
      {"step": 4, "text": "Bake at 350 degrees."}
    ],
    "tags": ["main dish", "beef", "peppers", "stuffed"],
    "image_refs": [],
    "confidence": {"overall": "high", "flags": ["typed recipe"]}
  },
  {
    "id": "cornish-game-hens-granny",
    "collection": "granny",
    "collection_display": "Granny Hudson",
    "title": "Cornish Game Hens",
    "category": "mains",
    "attribution": "",
    "source_note": "Handwritten recipe card in red ink",
    "description": "Herb-stuffed Cornish game hens with wine-butter basting, perfect for picnics.",
    "servings_yield": "8 servings",
    "prep_time": "30 minutes",
    "cook_time": "1 hour",
    "total_time": "1 hour 30 minutes",
    "temperature": "425°F (220°C)",
    "ingredients": [
      {"item": "frozen Cornish hens", "quantity": "4", "unit": "", "prep_note": "about 1 lb each"},
      {"item": "herb rice", "quantity": "1", "unit": "pkg", "prep_note": "6 oz"},
      {"item": "butter", "quantity": "1/2", "unit": "cup"},
      {"item": "dry white wine", "quantity": "1/2", "unit": "cup"},
      {"item": "rosemary", "quantity": "1", "unit": "tsp"}
    ],
    "instructions": [
      {"step": 1, "text": "Thaw hens. Cook giblets in 2 1/2 cups water until tender. Drain and save broth. Chop giblets."},
      {"step": 2, "text": "Cook rice according to package directions, using reserved broth instead of water. Add chopped giblets to rice."},
      {"step": 3, "text": "Stuff hens with the rice mixture. Truss well with small skewers and white string."},
      {"step": 4, "text": "Heat butter, wine, and rosemary in a pan until butter is melted."},
      {"step": 5, "text": "Arrange hens in a shallow roasting pan. Brush with butter mixture."},
      {"step": 6, "text": "Roast at 425°F for 1 hour or until done, basting several times with the butter mixture."},
      {"step": 7, "text": "Chill until ready for picnic."}
    ],
    "notes": [
      "This was a family picnic recipe - chill before transporting",
      "Use the giblet broth for extra flavor in the rice"
    ],
    "tags": ["poultry", "main dish", "picnic", "entertaining", "make-ahead"],
    "confidence": {"overall": "high", "flags": []},
    "image_refs": ["Grannys-recipes - 19"]
  }
]

UNIONS = [
  {"id": "dump-cake-granny", "add_image_refs": ["Grannys-recipes - 70"], "add_notes": ["Back of card has additional notes referencing Basic Brownies and chocolate frostings"]},
  {"id": "barbecued-spareribs-orientale-granny", "add_image_refs": [], "add_notes": ["Good served with barbecued fresh vegetables and a tossed salad. Tips: You may precook spareribs ahead of time and simply heat and glaze over charcoal before serving."]},
  {"id": "banana-bread-dewolf-granny", "add_image_refs": ["73"], "add_notes": []},
  {"id": "grandmas-wheat-berrie-muffins-granny", "add_image_refs": ["71"], "add_notes": []},
  {"id": "angel-delight-granny", "add_image_refs": ["79"], "add_notes": []},
  {"id": "beef-vegetable-soup-granny", "add_image_refs": [], "add_notes": ["For added flavor, other vegetables, peas, celery or parsnips may be added to soup. Tips: To sauté Edam, add shredded Edam to skillet and cook 15 to 20 minutes until golden. Stir in carrots and slices. Cook stirring, about 5 minutes until tender."]},
  {"id": "quiche-crepes-granny", "add_image_refs": [], "add_notes": ["Crepes can be served from dish. To remove from dish, loosen with knife tip"]},
  {"id": "beef-meatballs-in-tomato-sauce-granny", "add_image_refs": ["Grannys-recipes - 66"], "add_notes": []},
  {"id": "make-ahead-cookie-mix-granny", "add_image_refs": [], "add_notes": ["See reverse side for cookie recipes using this mix."]},
  {"id": "basic-crust-granny", "add_image_refs": [], "add_notes": ["For use with Pillsbury's Best Self-Rising Flour, omit salt and the 2 tablespoons butter", "Use coconut cream pudding mix for Frosty Orange Delight"]},
  {"id": "italian-meat-loaf-granny", "add_image_refs": [], "add_notes": ["Good served with hot rice or sauteed French-cut green beans in olive oil and garlic.", "To reduce fat, cholesterol and calories, use extra-lean ground beef or ground turkey. Eliminate the egg yolk."]}
]

IMAGE_DELETIONS_REVIEW_FIRST = [
  "granny/IMG_4392 Medium.jpeg", "granny/IMG_4393 Medium.jpeg", "granny/IMG_4394 Medium.jpeg",
  "granny/IMG_4395 Medium.jpeg", "granny/IMG_4396 Medium.jpeg", "granny/IMG_4397 Medium.jpeg",
  "granny/IMG_4398 Medium.jpeg", "granny/IMG_4399 Medium.jpeg", "granny/IMG_4400 Medium.jpeg",
  "granny/IMG_4401 Medium.jpeg",
  "granny/processed/IMG_4392.jpeg", "granny/processed/IMG_4393.jpeg", "granny/processed/IMG_4394.jpeg",
  "granny/processed/IMG_4395.jpeg", "granny/processed/IMG_4396.jpeg", "granny/processed/IMG_4397.jpeg",
  "granny/processed/IMG_4398.jpeg", "granny/processed/IMG_4399.jpeg", "granny/processed/IMG_4400.jpeg",
  "granny/processed/IMG_4401.jpeg"
]


def main():
    repo_root = Path(__file__).resolve().parents[2]
    target = repo_root / 'granny' / 'recipes_master.json'
    if not target.exists():
        print(f'ERROR: {target} not found. Run from Grannysrecipes repo root.', file=sys.stderr)
        sys.exit(1)

    data = json.loads(target.read_text())
    by_id = {r['id']: r for r in data['recipes']}
    starting_count = len(data['recipes'])

    added = []
    union_summary = []

    for new in NEW_RECIPES:
        rid = new['id']
        if rid in by_id:
            print(f'SKIP new (already exists): {rid}')
        else:
            data['recipes'].append(new)
            by_id[rid] = new
            added.append(rid)

    for u in UNIONS:
        rid = u['id']
        if rid not in by_id:
            print(f'SKIP union (id missing): {rid}')
            continue
        r = by_id[rid]
        ex_refs = r.get('image_refs', []) or []
        new_refs = [x for x in u['add_image_refs'] if x not in ex_refs]
        if new_refs:
            r['image_refs'] = ex_refs + new_refs
        ex_notes = r.get('notes', []) or []
        new_notes = [x for x in u['add_notes'] if x not in ex_notes]
        if new_notes:
            r['notes'] = ex_notes + new_notes
        if new_refs or new_notes:
            union_summary.append((rid, len(new_refs), len(new_notes)))

    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

    print('\n=== PR #21 merge applied ===')
    print(f'Recipes before: {starting_count}')
    print(f'Recipes after:  {len(data["recipes"])}')
    print(f'\nNew recipes added ({len(added)}):')
    for rid in added:
        print(f'  + {rid}')
    print(f'\nUnions applied ({len(union_summary)}):')
    for rid, nr, nn in union_summary:
        bits = []
        if nr: bits.append(f'+{nr} image_refs')
        if nn: bits.append(f'+{nn} notes')
        print(f'  ~ {rid}: {", ".join(bits)}')
    print('\nIMAGES the PR proposed to delete (review first, then delete manually if unused):')
    for img in IMAGE_DELETIONS_REVIEW_FIRST:
        print(f'  ? {img}')


if __name__ == '__main__':
    main()
