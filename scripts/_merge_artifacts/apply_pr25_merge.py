#!/usr/bin/env python3
"""
Hand-merge artifact for PR #25 (Repair failed recipes).

This script applies PR #25's recipe repairs to current main. Unlike a naive
merge that conflicts on non-recipe files, this surgically applies only the
42 recipe-array changes the PR makes to granny/recipes_master.json.

WHY THIS EXISTS:
PR #25 was opened today against the current main but conflicts because of
overlap on scripts/estimate_nutrition.py (PR #25 also has minor edits there
that conflict with other recent merges). This script bypasses that by reading
the PR head's recipes directly via git, applying just the recipe changes,
and leaving estimate_nutrition.py untouched.

WHAT THIS APPLIES:
  - 1 NEW recipe: easy-baked-french-toast-granny
  - 41 REPAIRED recipes (replace existing entries with PR's repaired versions)

NOT APPLIED HERE:
  - PR #25's changes to scripts/estimate_nutrition.py (review the PR diff and
    cherry-pick by hand if desired — adds bread-slice / lowfat-milk /
    cooking-spray ingredient entries plus a few brand mappings).

REQUIREMENTS:
  - Run from inside the Grannysrecipes repo on current main
  - PR #25's branch fetched: `git fetch origin claude/repair-failed-recipes-g9EyF`
  - Or use the PR head SHA directly: 171320bc502298af807297744185cdf24fde440e

HOW TO APPLY:
  cd <Grannysrecipes repo>
  git fetch origin claude/repair-failed-recipes-g9EyF
  python3 scripts/_merge_artifacts/apply_pr25_merge.py [--dry-run]
  python3 scripts/validate-recipes.py
  python3 scripts/build-ingredient-index.py
  git add granny/recipes_master.json granny/ingredient-index.json
  git commit -m "Merge PR #25: 41 recipe repairs + 1 new (manual)"
  # Then close PR #25 with comment linking to this commit.
"""

import json
import subprocess
import sys
from pathlib import Path

PR25_HEAD_SHA = '171320bc502298af807297744185cdf24fde440e'

NEW_IDS = ['easy-baked-french-toast-granny']
REPAIRED_IDS = [
    'almond-butter-sticks-granny', 'bbq-bacon-cheeseburgers-granny',
    'broccoli-cornbread-handwritten-granny', 'butterballs-granny',
    'cherry-winks-granny', 'chewy-oatmeal-cookies-crisco-granny',
    'chicken-portobello-tarragon-cream-granny', 'chocolate-chip-recipe-gr7-granny',
    'corn-muffins-sticks-granny', 'country-style-ribs-corn-granny',
    'cranberry-glazed-ham-kabobs-granny', 'crunchy-cornmeal-pancakes-granny',
    'curry-coconut-chicken-honey-mustard-granny', 'dump-cake-handwritten-granny',
    'easiest-pineapple-upside-down-cake-granny', 'easy-cornbread-granny',
    'fabulous-french-toast-granny', 'garlic-cheese-drop-biscuits-granny',
    'grandmas-biscuits-granny', 'grilled-chicken-monterey-granny',
    'handwritten-baking-recipe-gr1-granny', 'handwritten-recipe-gr5-granny',
    'handwritten-recipe-red-ink-granny', 'health-tonic-granny',
    'homemade-mac-cheese-bacon-granny', 'lemon-poppy-seed-muffins-granny',
    'oatmeal-carmelitas-granny', 'orange-sparkle-granny',
    'peaches-and-cream-ice-cream-granny', 'peanut-blossoms-granny',
    'pillsbury-chocolate-chip-cookies-granny', 'pillsbury-oatmeal-raisin-granny',
    'pumpkin-spice-bread-granny', 'seafood-lasagna-granny',
    'sirloin-steak-marinade-granny', 'southern-cornbread-granny',
    'sweet-muffins-granny', 'sweet-surprise-souffle-granny',
    'tender-cornmeal-pancakes-granny', 'tender-drop-biscuits-granny',
    'toffee-bars-granny',
]

TARGET_IDS = set(NEW_IDS) | set(REPAIRED_IDS)


def fetch_pr_head_recipes():
    """Read recipes_master.json at PR #25 head via `git show`."""
    try:
        out = subprocess.check_output(
            ['git', 'show', f'{PR25_HEAD_SHA}:granny/recipes_master.json'],
            text=True,
        )
    except subprocess.CalledProcessError:
        print(
            'ERROR: could not read PR #25 head. Did you fetch the branch?\n'
            '  git fetch origin claude/repair-failed-recipes-g9EyF\n'
            f'(or fetch by SHA {PR25_HEAD_SHA})',
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(out)['recipes']


def main():
    dry = '--dry-run' in sys.argv
    repo_root = Path(__file__).resolve().parents[2]
    target = repo_root / 'granny' / 'recipes_master.json'
    if not target.exists():
        print(f'ERROR: {target} not found.', file=sys.stderr)
        sys.exit(1)

    pr_recipes_by_id = {r['id']: r for r in fetch_pr_head_recipes()}
    missing = TARGET_IDS - pr_recipes_by_id.keys()
    if missing:
        print(f'ERROR: PR head missing IDs: {sorted(missing)}', file=sys.stderr)
        sys.exit(1)

    main_data = json.loads(target.read_text())
    by_id = {r['id']: i for i, r in enumerate(main_data['recipes'])}
    starting = len(main_data['recipes'])

    added, replaced, skipped = [], [], []

    for rid in NEW_IDS:
        if rid in by_id:
            print(f'SKIP new (already exists): {rid}')
            skipped.append(rid)
        else:
            main_data['recipes'].append(pr_recipes_by_id[rid])
            added.append(rid)

    for rid in REPAIRED_IDS:
        if rid not in by_id:
            print(f'SKIP repair (id missing on main): {rid}')
            continue
        main_data['recipes'][by_id[rid]] = pr_recipes_by_id[rid]
        replaced.append(rid)

    if dry:
        print(f'\n[DRY RUN] Would add {len(added)}, replace {len(replaced)}, skip {len(skipped)}')
        for rid in added: print(f'  + {rid}')
        for rid in replaced: print(f'  ~ {rid}')
        return

    target.write_text(json.dumps(main_data, indent=2, ensure_ascii=False) + '\n')
    print('\n=== PR #25 merge applied ===')
    print(f'Recipes before: {starting}')
    print(f'Recipes after:  {len(main_data["recipes"])}')
    print(f'\nNew added ({len(added)}):')
    for rid in added: print(f'  + {rid}')
    print(f'\nRepaired ({len(replaced)}):')
    for rid in replaced: print(f'  ~ {rid}')
    if skipped:
        print(f'\nSkipped ({len(skipped)}): {skipped}')


if __name__ == '__main__':
    main()
