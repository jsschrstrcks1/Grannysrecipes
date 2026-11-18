#!/usr/bin/env python3
"""
Tests for the shared recipe validator (core.py) and batch importer (import_batch.py).
Every claim is tested with a NEGATIVE case beside the positive one.
Byte-identical in every repo that carries it. Run:
    python3 scripts/recipe_validator/test_recipe_validator.py
Python stdlib only. Soli Deo Gloria.
"""

import contextlib
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from recipe_validator import core  # noqa: E402
from recipe_validator import import_batch  # noqa: E402

BASE = {
    'repo_label': 'test', 'data_file': 'data/recipes.json', 'image_dir': 'data',
    'required_fields': ['id', 'title', 'ingredients', 'instructions', 'category'],
    'optional_fields': [], 'valid_categories': ['desserts', 'tips', 'cheese'],
    'valid_confidence': ['high', 'medium', 'low'],
    'ingredient_optional_categories': [], 'empty_instructions_ok_categories': [],
    'warn_missing_nutrition': False,
    'sanity_limits': {'salt': {'max_cups': 0.5, 'max_tbsp': 3, 'max_tsp': 6},
                      'sugar': {'max_cups': 6}, 'flour': {'max_cups': 3.5}},
    'sanity_match': 'substring', 'sanity_skip_quantity_over': None, 'quantity_parse': 'simple',
    'sanity_skip_item_substrings': [], 'limit_overrides': [],
    'temperature_mode': 'plain', 'temp_min': 200, 'temp_max': 550, 'temp_min_low': 50,
    'cheese_temp_min': 50, 'cheese_temp_max': 220,
    'low_temp_categories': [], 'low_temp_tags': [], 'low_temp_title_terms': [],
    'low_temp_title_id_keywords': [], 'image_skip_urls': False, 'image_extensions': [''],
    'meta_count_fields': ['total_recipes'], 'declared_unused': {}, '_notes': [],
}
STEP = [{'step': 1, 'text': 'Mix.'}]


def cfg(**over):
    c = copy.deepcopy(BASE)
    c.update(over)
    return c


def recipe(rid='good-one', **kw):
    r = {'id': rid, 'title': kw.pop('title', 'Good One'), 'category': kw.pop('category', 'desserts'),
         'ingredients': kw.pop('ingredients', [{'item': 'water', 'quantity': '1', 'unit': 'cup'}]),
         'instructions': kw.pop('instructions', STEP)}
    r.update(kw)
    return r


def run_v(r, c, root='.'):
    v = core.RecipeValidator(c, root)
    v.validate_recipe(r)
    return v


def ing(item, qty, unit):
    return [{'item': item, 'quantity': qty, 'unit': unit}]


class CoreChecks(unittest.TestCase):
    def test_required_fields(self):
        self.assertTrue(any('Missing required field: title' in e for e in run_v(recipe(title=''), cfg()).errors))
        self.assertEqual(run_v(recipe(), cfg()).errors, [])

    def test_ingredient_optional_categories(self):
        r = {'id': 'a-tip', 'title': 'Tip', 'category': 'tips'}
        self.assertEqual(run_v(r, cfg(ingredient_optional_categories=['tips'])).errors, [])
        self.assertEqual(len(run_v(r, cfg()).errors), 2)  # negative: not waived without the switch

    def test_empty_instructions_ok(self):
        r = recipe(category='tips', instructions=[])
        c = cfg(ingredient_optional_categories=['tips'])
        self.assertIn('ERROR [good-one]: Instructions list is empty', run_v(r, c).errors)
        c['empty_instructions_ok_categories'] = ['tips']
        self.assertEqual(run_v(r, c).errors, [])

    def test_warn_missing_nutrition(self):
        self.assertIn('WARNING [good-one]: Missing nutrition data', run_v(recipe(), cfg(warn_missing_nutrition=True)).warnings)
        self.assertEqual(run_v(recipe(), cfg()).warnings, [])
        tip = recipe(category='tips')
        self.assertEqual(run_v(tip, cfg(warn_missing_nutrition=True, ingredient_optional_categories=['tips'])).warnings, [])

    def test_sanity_match_modes(self):
        r = recipe(ingredients=ing('salted peanuts', '2', 'cups'))
        self.assertEqual(len(run_v(r, cfg()).warnings), 1)                          # substring matches "salt"
        self.assertEqual(run_v(r, cfg(sanity_match='word_boundary')).warnings, [])  # word boundary does not
        r2 = recipe(ingredients=ing('salt', '2', 'cups'))
        self.assertEqual(len(run_v(r2, cfg(sanity_match='word_boundary')).warnings), 1)

    def test_skip_quantity_over(self):
        r = recipe(ingredients=ing('sugar', '60', 'cups'))
        self.assertEqual(len(run_v(r, cfg()).warnings), 1)
        self.assertEqual(run_v(r, cfg(sanity_skip_quantity_over=50)).warnings, [])

    def test_quantity_parse_modes(self):
        r = recipe(ingredients=ing('flour', '3-4', 'cups'))
        self.assertEqual(run_v(r, cfg()).warnings, [])  # simple reads "3.4"
        self.assertEqual(len(run_v(r, cfg(quantity_parse='range_max')).warnings), 1)  # range_max reads 4
        frac = recipe(ingredients=ing('flour', '3 3/4', 'cups'))
        self.assertEqual(len(run_v(frac, cfg()).warnings), 1)
        self.assertEqual(run_v(recipe(ingredients=ing('flour', '[UNCLEAR]', 'cups')), cfg()).warnings, [])

    def test_skip_item_substrings(self):
        r = recipe(ingredients=ing('kosher salt', '2', 'cups'))
        self.assertEqual(len(run_v(r, cfg()).warnings), 1)
        self.assertEqual(run_v(r, cfg(sanity_skip_item_substrings=['kosher salt'])).warnings, [])

    def test_limit_overrides(self):
        ov = [{'item': 'salt', 'keywords': ['brine'], 'limits': {'max_cups': 2}}]
        salty = ing('salt', '1', 'cup')
        self.assertEqual(run_v(recipe(title='Turkey Brine', ingredients=salty), cfg(limit_overrides=ov)).warnings, [])
        self.assertEqual(run_v(recipe(rid='turkey-brine', title='Turkey', ingredients=salty), cfg(limit_overrides=ov)).warnings, [])
        self.assertEqual(len(run_v(recipe(title='Cake', ingredients=salty), cfg(limit_overrides=ov)).warnings), 1)

    def test_temperature_plain(self):
        self.assertIn('WARNING [good-one]: Temperature 150°F outside typical range (200-550°F)',
                      run_v(recipe(temperature='150°F'), cfg()).warnings)
        self.assertEqual(run_v(recipe(temperature='350°F'), cfg()).warnings, [])

    def test_temperature_low_temp_min(self):
        c = cfg(temperature_mode='low_temp_min', low_temp_categories=['cheese'], low_temp_title_id_keywords=['ricotta'])
        self.assertEqual(run_v(recipe(category='cheese', temperature='150°F'), c).warnings, [])
        self.assertEqual(run_v(recipe(title='Fresh Ricotta', temperature='150°F'), c).warnings, [])
        self.assertIn('WARNING [good-one]: Temperature 40°F outside typical range (50-550°F)',
                      run_v(recipe(category='cheese', temperature='40°F'), c).warnings)
        self.assertEqual(len(run_v(recipe(temperature='150°F'), c).warnings), 1)  # no context

    def test_temperature_cheese_dual_range(self):
        c = cfg(temperature_mode='cheese_dual_range', low_temp_tags=['yogurt'], low_temp_title_terms=['bread'])
        self.assertEqual(run_v(recipe(tags=['Yogurt'], temperature='110°F'), c).warnings, [])
        self.assertEqual(run_v(recipe(title='Rye Bread', temperature='230°F'), c).warnings, [])
        w = run_v(recipe(tags=['yogurt'], temperature='600°F'), c).warnings
        self.assertEqual(w, ['WARNING [good-one]: Temperature 600°F outside expected ranges (cheese: 50-220°F, baking: 200-550°F)'])
        self.assertEqual(len(run_v(recipe(temperature='110°F'), c).warnings), 1)  # no context

    def test_image_refs(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'data').mkdir()
            (Path(d) / 'data' / 'pic.jpg').write_bytes(b'x')
            self.assertEqual(run_v(recipe(image_refs=['pic.jpg']), cfg(), d).warnings, [])
            self.assertEqual(len(run_v(recipe(image_refs=['pic']), cfg(), d).warnings), 1)
            self.assertEqual(run_v(recipe(image_refs=['pic']), cfg(image_extensions=['', '.jpg']), d).warnings, [])
            url = recipe(image_refs=['https://example.com/a.jpg'])
            self.assertEqual(len(run_v(url, cfg(), d).warnings), 1)
            self.assertEqual(run_v(url, cfg(image_skip_urls=True), d).warnings, [])

    def test_non_string_image_ref_is_error(self):
        v = run_v(recipe(image_refs=[5]), cfg())
        self.assertEqual(v.errors, ['ERROR [good-one]: image_refs entry must be a string: 5'])
        self.assertEqual(run_v(recipe(image_refs=['x.jpg']), cfg()).errors, [])

    def test_duplicates_and_variants(self):
        v = core.RecipeValidator(cfg(), '.')
        v.validate_all({'recipes': [recipe('a'), recipe('a'), recipe('b', variant_of='zzz'), recipe('c', variant_of='a')]})
        self.assertEqual(v.errors, ['ERROR [a]: Duplicate recipe ID', 'ERROR [b]: variant_of references non-existent recipe: zzz'])

    def test_strict_exit_code(self):
        v = run_v(recipe(category='nope'), cfg())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(v.report(), 0)
            v.strict = True
            self.assertEqual(v.report(), 1)

    def test_config_closed_shape(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'c.json'
            p.write_text(json.dumps(cfg()))
            self.assertEqual(core.load_config(p)['temp_min'], 200)
            bad = cfg(); bad['temp_minn'] = 1
            p.write_text(json.dumps(bad))
            self.assertRaises(core.ConfigError, core.load_config, p)
            bad = cfg(); del bad['temp_min']
            p.write_text(json.dumps(bad))
            self.assertRaises(core.ConfigError, core.load_config, p)
            p.write_text(json.dumps(cfg(temperature_mode='hot')))
            self.assertRaises(core.ConfigError, core.load_config, p)

    def test_this_repos_config(self):
        c = core.load_config(HERE / 'config.json')
        self.assertTrue((HERE.parent.parent / c['data_file']).exists())


class Importer(unittest.TestCase):
    def make(self, data, ensure_ascii=True, newline=True, config=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'data').mkdir()
        self.data_path = self.root / 'data' / 'recipes.json'
        text = json.dumps(data, indent=2, ensure_ascii=ensure_ascii) + ('\n' if newline else '')
        self.data_path.write_bytes(text.encode('utf-8'))
        self.cfg_path = self.root / 'config.json'
        self.cfg_path.write_text(json.dumps(config or cfg()))
        self.addCleanup(self.tmp.cleanup)
        return text.encode('utf-8')

    def run_batch(self, batch, apply):
        bp = self.root / 'batch.json'
        bp.write_text(json.dumps(batch, ensure_ascii=False), encoding='utf-8')
        lines = []
        code = import_batch.run(bp, apply=apply, config_path=self.cfg_path, repo_root=self.root, out=lines.append)
        return code, '\n'.join(lines)

    def base(self):
        return {'meta': {'total_recipes': 2, 'recipe_count': 999, 'title': 'T'},
                'recipes': [recipe('old-one'), recipe('old-two', title='Crème brûlée')]}

    def test_dry_run_writes_nothing(self):
        raw = self.make(self.base())
        code, out = self.run_batch([recipe('new-one')], apply=False)
        self.assertEqual(code, 0)
        self.assertIn('DRY RUN', out)
        self.assertEqual(self.data_path.read_bytes(), raw)
        code, _ = self.run_batch([recipe('new-one')], apply=True)  # negative: --apply does write
        self.assertEqual(code, 0)
        self.assertNotEqual(self.data_path.read_bytes(), raw)

    def test_duplicates_skipped(self):
        self.make(self.base())
        code, out = self.run_batch([recipe('old-one', title='Changed!'), recipe('new-one'), recipe('new-one', title='Dup'),
                                    recipe('new-two')], apply=True)
        self.assertEqual(code, 0)
        self.assertIn('SKIP old-one (already in data file)', out)
        self.assertIn('SKIP new-one (duplicate within batch)', out)
        recs = json.loads(self.data_path.read_text())['recipes']
        self.assertEqual([r['id'] for r in recs], ['old-one', 'old-two', 'new-one', 'new-two'])
        self.assertEqual(recs[0]['title'], 'Good One')     # existing not overwritten
        self.assertEqual(recs[2]['title'], 'Good One')     # first in-batch copy wins

    def test_error_refuses_whole_write(self):
        raw = self.make(self.base())
        code, out = self.run_batch([recipe('fine-one'), recipe('Bad_ID')], apply=True)
        self.assertEqual(code, 2)
        self.assertIn('REFUSED', out)
        self.assertIn('ERROR [Bad_ID]: Invalid ID format', out)
        self.assertEqual(self.data_path.read_bytes(), raw)  # the fine recipe was not written either
        code, _ = self.run_batch([recipe('fine-one')], apply=True)  # negative: all good writes
        self.assertEqual(code, 0)

    def test_warnings_do_not_block(self):
        self.make(self.base())
        code, out = self.run_batch([recipe('odd-cat', category='weird')], apply=True)
        self.assertEqual(code, 0)
        self.assertIn('WARNING [odd-cat]: Unknown category: weird', out)

    def test_existing_recipes_byte_identical(self):
        for ensure_ascii, newline in ((True, True), (False, False)):
            with self.subTest(ensure_ascii=ensure_ascii, newline=newline):
                data = self.base()
                raw = self.make(data, ensure_ascii, newline)
                self.run_batch([recipe('new-one', title='Café [UNCLEAR] cake')], apply=True)
                new = json.loads(self.data_path.read_text(encoding='utf-8'))
                self.assertEqual(new['recipes'][2]['title'], 'Café [UNCLEAR] cake')  # content verbatim
                new['recipes'] = new['recipes'][:2]
                new['meta']['total_recipes'] = 2
                rebuilt = import_batch.serialize(new, ensure_ascii, newline)
                self.assertEqual(rebuilt, raw)  # everything but the intended changes is byte-identical
                new['recipes'][0]['title'] = 'tampered'  # negative: the comparison has teeth
                self.assertNotEqual(import_batch.serialize(new, ensure_ascii, newline), raw)

    def test_style_preserved(self):
        self.make(self.base(), ensure_ascii=False, newline=False)
        self.run_batch([recipe('new-one', title='Café')], apply=True)
        b = self.data_path.read_bytes()
        self.assertIn('Café'.encode('utf-8'), b)
        self.assertFalse(b.endswith(b'\n'))
        self.assertTrue(b.startswith(b'{\n  "meta": {\n    "total_recipes"'))
        self.make(self.base(), ensure_ascii=True, newline=True)  # negative: ASCII file stays escaped
        self.run_batch([recipe('new-one', title='Café')], apply=True)
        b = self.data_path.read_bytes()
        self.assertIn(b'Caf\\u00e9', b)
        self.assertNotIn('Café'.encode('utf-8'), b)
        self.assertTrue(b.endswith(b'\n'))

    def test_unpreservable_style_refused(self):
        self.make(self.base())
        raw = json.dumps(self.base(), indent=4).encode()
        self.data_path.write_bytes(raw)
        code, out = self.run_batch([recipe('new-one')], apply=True)
        self.assertEqual(code, 1)
        self.assertIn('does not re-serialise', out)
        self.assertEqual(self.data_path.read_bytes(), raw)

    def test_meta_counts_only_where_present(self):
        self.make(self.base(), config=cfg(meta_count_fields=['total_recipes', 'total_count']))
        self.run_batch([recipe('new-one')], apply=True)
        meta = json.loads(self.data_path.read_text())['meta']
        self.assertEqual(meta['total_recipes'], 3)
        self.assertNotIn('total_count', meta)       # named in config but absent: not added
        self.assertEqual(meta['recipe_count'], 999)  # present but not named: untouched
        self.make(self.base(), config=cfg(meta_count_fields=[]))  # negative: no fields, no change
        self.run_batch([recipe('new-one')], apply=True)
        self.assertEqual(json.loads(self.data_path.read_text())['meta']['total_recipes'], 2)

    def test_atomic_write_leaves_no_temp(self):
        self.make(self.base())
        self.run_batch([recipe('new-one')], apply=True)
        self.assertEqual(sorted(p.name for p in (self.root / 'data').iterdir()), ['recipes.json'])

    def test_bad_batch_shapes(self):
        raw = self.make(self.base())
        code, _ = self.run_batch({'recipes': []}, apply=True)
        self.assertEqual(code, 1)
        code, out = self.run_batch(['not a recipe'], apply=True)
        self.assertEqual(code, 2)
        self.assertIn('recipe must be an object', out)
        self.assertEqual(self.data_path.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
