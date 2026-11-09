#!/usr/bin/env python3
"""
differential_check.py: proves the shared validator reproduces a repo's ORIGINAL
validate-recipes.py byte for byte (stdout, stderr, exit code), normal and --strict.

Usage:
    git -C <repo> show HEAD:scripts/validate-recipes.py > /some/scratch/orig.py
    python scripts/recipe_validator/differential_check.py /some/scratch/orig.py [--mode real|fixtures|both] [--workdir DIR]

Modes
    real      The repo's real data. The original reads its data path from its own
              __file__, so it is copied for the run only to <repo>/scripts/.validate-recipes.orig.py
              (refused if that name already exists) and removed afterwards, success or not.
    fixtures  Synthetic edge cases (every switch, limit, temperature context, image lookup,
              non-recipe category, global failure) run through both validators in a scratch
              mirror of the repo layout, so both print the same paths.
    both      (default) real, then fixtures.

Fixtures avoid inputs on which the forks crash (non-string quantity/id/title/temperature/
image ref): a traceback cannot be compared, and for a non-string image ref the shared
validator deliberately reports an ERROR instead.

Exit codes: 0 IDENTICAL everywhere; 1 DIFFERENT somewhere; 2 UNAVAILABLE (could not run).
Byte-identical copy in every repo that carries it. Python stdlib only. Soli Deo Gloria.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ORIG_NAME = '.validate-recipes.orig.py'
PKG_FILES = ('core.py', '__init__.py', 'config.json')


def run_script(script, cwd, args):
    p = subprocess.run([sys.executable, str(script)] + args, cwd=str(cwd),
                       capture_output=True, timeout=600)
    return p.returncode, p.stdout, p.stderr


def compare(label, orig_script, new_script, cwd):
    """Run both, normal and --strict. Returns True when every pair is identical."""
    ok = True
    for args in ([], ['--strict']):
        o = run_script(orig_script, cwd, args)
        n = run_script(new_script, cwd, args)
        name = f"{label} {' '.join(args) or '(normal)'}"
        if o == n:
            lines = o[1].decode('utf-8', 'replace').count('\n')
            print(f"IDENTICAL  {name}: exit {o[0]}, stdout {len(o[1])} bytes / {lines} lines, stderr {len(o[2])} bytes")
        else:
            ok = False
            print(f"DIFFERENT  {name}: exit {o[0]} vs {n[0]}")
            for which, a, b in (('stdout', o[1], n[1]), ('stderr', o[2], n[2])):
                if a != b:
                    al, bl = a.decode('utf-8', 'replace').splitlines(), b.decode('utf-8', 'replace').splitlines()
                    for i in range(max(len(al), len(bl))):
                        x = al[i] if i < len(al) else '<missing>'
                        y = bl[i] if i < len(bl) else '<missing>'
                        if x != y:
                            print(f"    {which} line {i + 1}:\n      original: {x}\n      new:      {y}")
                            break
    return ok


def check_real(original):
    target = REPO / 'scripts' / ORIG_NAME
    if target.exists():
        print(f"UNAVAILABLE: {target} already exists; refusing to overwrite it")
        return None
    shutil.copyfile(original, target)
    try:
        return compare(f"real data ({REPO.name})", target, REPO / 'scripts' / 'validate-recipes.py', REPO)
    finally:
        target.unlink()
        print(f"removed temporary {target}: {'yes' if not target.exists() else 'NO, STILL PRESENT'}")


def ing(item, qty='', unit=''):
    return {'item': item, 'quantity': qty, 'unit': unit}


STEP = [{'step': 1, 'text': 'Mix.'}]
NUT_OK = {'status': 'complete', 'per_serving': {'calories': 100}}


def fixture_recipes():
    """Edge cases for every check and switch in the four forks."""
    R = []

    def add(rid, **kw):
        r = {'id': rid, 'title': kw.pop('title', rid.replace('-', ' ').title()), 'category': kw.pop('category', 'desserts'),
             'ingredients': kw.pop('ingredients', [ing('water', '1', 'cup')]), 'instructions': kw.pop('instructions', STEP)}
        r.update(kw)
        R.append(r)

    # required fields, id, category, confidence
    R.append({'title': 'No id at all', 'category': 'desserts', 'ingredients': [ing('egg', '1')], 'instructions': STEP})
    add('missing-title', title='')
    R.append({'id': 'no-category', 'title': 'No category', 'ingredients': [ing('egg', '1')], 'instructions': STEP})
    add('Bad_ID')
    add('unknown-cat', category='desserts-ish')
    add('list-cat', category=['desserts'])
    for cat in ('cheese', 'basics', 'tips', 'reference', 'techniques', 'remedies', 'cakes', 'main dishes', 'fermentation', 'marinades'):
        add(f'cat-{cat.replace(" ", "-")}', category=cat)
    add('conf-bad', confidence={'overall': 'certain'})
    add('conf-ok', confidence={'overall': 'high'})
    add('conf-none', confidence={'notes': 'x'})
    add('conf-empty', confidence={})
    # non-recipe categories without ingredients / instructions
    for cat in ('tips', 'reference', 'basics', 'techniques', 'desserts'):
        R.append({'id': f'nonrecipe-absent-{cat}', 'title': 'Note', 'category': cat})
        R.append({'id': f'nonrecipe-empty-{cat}', 'title': 'Note', 'category': cat, 'ingredients': [], 'instructions': []})
    # ingredient / instruction shapes
    add('ing-not-list', ingredients='flour, sugar')
    add('ing-not-dict', ingredients=['flour'])
    add('ing-no-item', ingredients=[{'quantity': '2', 'unit': 'cups'}])
    add('ins-not-list', instructions='Bake it.')
    add('ins-empty', instructions=[])
    add('ins-not-dict', instructions=['Bake it.'])
    add('ins-no-text', instructions=[{'step': 1}])
    # quantity sanity: items x units x quantities
    items = ['salt', 'Salt', 'table salt', 'salted peanuts', 'unsalted butter', 'kosher salt', 'salmon', 'saltine crackers',
             'sugar', 'brown sugar', 'flour', 'all-purpose flour', 'butter', 'peanut butter', 'baking soda', 'baking powder',
             'water']
    qtys = ['1', '3', '5', '7', '9', '11', '13', '17', '25', '49', '51', '60', '0.6', '1.5', '2 3/4', '3/4', '1/2',
            '3-4', '1-2', '10-12', '4 - 5', '2-', '-', 'abc', '', '[UNCLEAR]', 'about 2', '5 1/2', '1/2 cup']
    units = ['cup', 'cups', 'Cup', 'tbsp', 'TBSP', 'tsp', 'teaspoon', 'lb', '']
    n = 0
    for item in items:
        rows = []
        for q in qtys:
            for u in units:
                rows.append(ing(item, q, u))
        n += 1
        add(f'qty-{n}', ingredients=rows)
    # limit overrides by keyword in title / id
    salty = [ing('salt', q, u) for q in ('1', '2', '3', '5', '10', '20', '40', '50') for u in ('cup', 'tbsp', 'tsp')]
    sweet = [ing('sugar', q, 'cups') for q in ('5', '7', '9', '11')]
    add('pork-marinade', ingredients=salty)
    add('x-1', title='Pickle Brine for Feta', ingredients=salty + sweet)
    add('strawberry-jam', ingredients=sweet)
    add('x-2', title='Orange Marmalade', ingredients=sweet + salty)
    add('plain-cake', ingredients=salty + sweet)
    # temperatures under every context
    temps = ['350°F', '350 F', '350F', '40°F', '49°F', '50°F', '60°F', '150°F', '199°F', '200°F', '210°F', '220°F',
             '221°F', '230°F', '550°F', '551°F', '600°F', '180°C', 'Preheat oven to 375', 'Moderate oven', '85-95°F',
             'Bake at 425°F then 350°F']
    contexts = [
        ('t-plain', {}),
        ('t-cheesecat', {'category': 'cheese'}),
        ('t-dairycat', {'category': 'dairy'}),
        ('t-candycat', {'category': 'candy'}),
        ('t-tag-yogurt', {'tags': ['yogurt']}),
        ('t-tag-bread-upper', {'tags': ['Bread']}),
        ('t-tag-other', {'tags': ['quick']}),
        ('t-title', {'title': 'Homemade Bread'}),
        ('t-title-creme', {'title': 'Crème fraîche'}),
        ('t-title-icecream', {'title': 'Vanilla Ice Cream'}),
        ('t-title-coldbrew', {'title': 'Cold brew coffee'}),
        ('t-title-ricotta', {'title': 'Fresh Ricotta'}),
        ('tvorog-cake', {}),
        ('homemade-jam', {}),
        ('t-pretzel-id', {'title': 'Soft snack'}),
    ]
    for rid, extra in contexts:
        for i, t in enumerate(temps):
            add(f'{rid}-{i}', temperature=t, **dict(extra))
    add('t-empty', temperature='')
    # image refs
    for i, refs in enumerate([['img-present.jpg'], ['img-noext'], ['img-png'], ['img-gif'], ['https://example.com/a.jpg'],
                              ['http://example.com/a.jpg'], ['missing.jpg'], [''], ['sub/inner.jpg'], ['img-present'],
                              [], ['img-present.jpg', 'missing-2.png', 'https://x.test/y']]):
        add(f'img-{i}', image_refs=refs)
    add('img-not-list', image_refs='img-present.jpg')
    # nutrition and conversions
    add('nut-ok', nutrition=NUT_OK)
    add('nut-empty', nutrition={})
    add('nut-insufficient', nutrition={'status': 'insufficient_data', 'missing_inputs': []})
    add('nut-insufficient-ok', nutrition={'status': 'insufficient_data', 'missing_inputs': ['servings']})
    add('nut-complete-none', nutrition={'status': 'complete', 'per_serving': {'calories': None}})
    add('nut-partial-empty', nutrition={'status': 'partial', 'per_serving': {}})
    add('nut-partial-missing', nutrition={'status': 'partial'})
    add('nut-other', nutrition={'status': 'estimated'})
    add('nut-tips', category='tips')
    add('conv-bad', conversions={'has_conversions': True, 'ingredients_metric': []})
    add('conv-ok', conversions={'has_conversions': True, 'ingredients_metric': ['250 ml water']})
    add('conv-false', conversions={'has_conversions': False})
    # duplicates and variants
    add('dup-id')
    add('dup-id', title='Second copy')
    add('variant-good', variant_of='dup-id')
    add('variant-bad', variant_of='no-such-recipe')
    return R


def scenarios():
    """(name, file bytes or None for 'file absent')."""
    good = {'meta': {'total_recipes': 0}, 'recipes': fixture_recipes()}
    clean = {'meta': {}, 'recipes': [{'id': 'clean-one', 'title': 'Clean', 'category': 'desserts',
                                      'ingredients': [ing('water', '1', 'cup')], 'instructions': STEP,
                                      'nutrition': NUT_OK}]}
    return [
        ('edge-cases', json.dumps(good, indent=2, ensure_ascii=False).encode('utf-8')),
        ('clean-single', json.dumps(clean, indent=2).encode('utf-8')),
        ('empty-recipes', b'{"recipes": []}'),
        ('no-recipes-key', b'{"meta": {}}'),
        ('invalid-json', b'{"recipes": [ {"id": "x",, } ]'),
        ('missing-file', None),
    ]


def build_mirror(root, original, cfg):
    scripts = root / 'scripts'
    pkg = scripts / 'recipe_validator'
    pkg.mkdir(parents=True)
    shutil.copyfile(original, scripts / ORIG_NAME)
    shutil.copyfile(REPO / 'scripts' / 'validate-recipes.py', scripts / 'validate-recipes.py')
    for f in PKG_FILES:
        shutil.copyfile(HERE / f, pkg / f)
    img = root / cfg['image_dir']
    (img / 'sub').mkdir(parents=True, exist_ok=True)
    for name in ('img-present.jpg', 'img-noext.jpg', 'img-png.PNG', 'img-gif.gif', 'sub/inner.jpg'):
        (img / name).write_bytes(b'\x89')


def check_fixtures(original, workdir):
    cfg = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
    ok = True
    base = Path(tempfile.mkdtemp(prefix='recipe-diff-', dir=workdir))
    try:
        for name, payload in scenarios():
            root = base / name
            build_mirror(root, original, cfg)
            data_file = root / cfg['data_file']
            data_file.parent.mkdir(parents=True, exist_ok=True)
            if payload is not None:
                data_file.write_bytes(payload)
            ok = compare(f"fixture {name}", root / 'scripts' / ORIG_NAME,
                         root / 'scripts' / 'validate-recipes.py', root) and ok
        n = len(fixture_recipes())
        print(f"(edge-cases fixture holds {n} recipes)")
    finally:
        shutil.rmtree(base)
    return ok


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('original', help='path to the ORIGINAL validate-recipes.py (e.g. from git show HEAD:...)')
    p.add_argument('--mode', choices=('real', 'fixtures', 'both'), default='both')
    p.add_argument('--workdir', help='scratch directory for the fixture mirror (default: system temp)')
    a = p.parse_args(argv)
    original = Path(a.original)
    if not original.is_file():
        print(f"UNAVAILABLE: original validator not found: {original}")
        return 2
    results = []
    if a.mode in ('real', 'both'):
        results.append(check_real(original))
    if a.mode in ('fixtures', 'both'):
        results.append(check_fixtures(original, a.workdir))
    if any(r is None for r in results):
        print("VERDICT: UNAVAILABLE")
        return 2
    if all(results):
        print("VERDICT: IDENTICAL")
        return 0
    print("VERDICT: DIFFERENT")
    return 1


if __name__ == '__main__':
    sys.exit(main())
