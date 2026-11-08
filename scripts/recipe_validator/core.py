#!/usr/bin/env python3
"""
recipe_validator.core: the ONE shared recipe validator for the household recipe repos.

What it is
    Four repos (Allrecipes, Grandmasrecipes, Grannysrecipes, MomsRecipes) each carried a
    fork of scripts/validate-recipes.py, grown from one ancestor and diverged. This module
    is the superset of every check those forks made. Every difference between the forks is
    CONFIGURATION (scripts/recipe_validator/config.json in each repo): categories, limits,
    keyword lists and feature switches. Nothing in this file is repo-specific.

Copies
    Byte-identical in every repo that carries it. Never edit one copy alone: edit the
    canonical copy, copy it to the others, and compare sha256 sums.

Canonical home
    Grandmasrecipes (the superset fork) once its hook guard is repaired. Until then
    Allrecipes holds the canonical copy.

Behaviour contract
    With a repo's config.json, report text and exit code are byte-identical to that repo's
    original validate-recipes.py on the same data, proved by differential_check.py.
    One deliberate difference: a non-string image_refs entry is an ERROR here, where the
    forks crashed (or, in Grannysrecipes, stringified it). No current data has one.

Python standard library only. Soli Deo Gloria.
"""

import json
import re
from pathlib import Path

CONFIG_KEYS = {
    'repo_label', 'data_file', 'image_dir', 'required_fields', 'optional_fields',
    'valid_categories', 'valid_confidence', 'ingredient_optional_categories',
    'empty_instructions_ok_categories', 'warn_missing_nutrition', 'sanity_limits',
    'sanity_match', 'sanity_skip_quantity_over', 'quantity_parse',
    'sanity_skip_item_substrings', 'limit_overrides', 'temperature_mode', 'temp_min',
    'temp_max', 'temp_min_low', 'cheese_temp_min', 'cheese_temp_max',
    'low_temp_categories', 'low_temp_tags', 'low_temp_title_terms',
    'low_temp_title_id_keywords', 'image_skip_urls', 'image_extensions',
    'meta_count_fields', 'declared_unused', '_notes',
}
SANITY_MATCH_MODES = ('substring', 'word_boundary')
QUANTITY_PARSE_MODES = ('simple', 'range_max')
TEMPERATURE_MODES = ('plain', 'low_temp_min', 'cheese_dual_range')


class ConfigError(Exception):
    pass


def load_config(path):
    path = Path(path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise ConfigError(f"cannot read config {path}: {e}")
    if not isinstance(cfg, dict):
        raise ConfigError(f"config {path} must be a JSON object")
    missing = sorted(CONFIG_KEYS - set(cfg) - {'_notes', 'declared_unused'})
    unknown = sorted(set(cfg) - CONFIG_KEYS)
    if missing:
        raise ConfigError(f"config {path} missing keys: {', '.join(missing)}")
    if unknown:
        raise ConfigError(f"config {path} has unknown keys: {', '.join(unknown)}")
    if cfg['sanity_match'] not in SANITY_MATCH_MODES:
        raise ConfigError(f"sanity_match must be one of {SANITY_MATCH_MODES}")
    if cfg['quantity_parse'] not in QUANTITY_PARSE_MODES:
        raise ConfigError(f"quantity_parse must be one of {QUANTITY_PARSE_MODES}")
    if cfg['temperature_mode'] not in TEMPERATURE_MODES:
        raise ConfigError(f"temperature_mode must be one of {TEMPERATURE_MODES}")
    for ov in cfg['limit_overrides']:
        if set(ov) != {'item', 'keywords', 'limits'}:
            raise ConfigError("each limit_overrides entry needs exactly item, keywords, limits")
    return cfg


class RecipeValidator:
    def __init__(self, config, repo_root, strict=False):
        self.c = config
        self.repo_root = Path(repo_root)
        self.strict = strict
        self.errors = []
        self.warnings = []

    def error(self, recipe_id, message):
        self.errors.append(f"ERROR [{recipe_id}]: {message}")

    def warn(self, recipe_id, message):
        self.warnings.append(f"WARNING [{recipe_id}]: {message}")

    def is_low_temp_context(self, recipe_id, category, title, tags):
        c = self.c
        if category in c['low_temp_categories']:
            return True
        if c['low_temp_tags'] and any(t.lower() in c['low_temp_tags'] for t in tags):
            return True
        if c['low_temp_title_terms']:
            title_lower = title.lower()
            if any(term in title_lower for term in c['low_temp_title_terms']):
                return True
        if c['low_temp_title_id_keywords']:
            kws = c['low_temp_title_id_keywords']
            if any(kw in title.lower() for kw in kws) or \
               any(kw in recipe_id.lower() for kw in kws):
                return True
        return False

    def validate_recipe(self, recipe):
        c = self.c
        recipe_id = recipe.get('id', 'UNKNOWN')
        category = recipe.get('category', '')
        optional_cats = c['ingredient_optional_categories']
        for field in c['required_fields']:
            if field in ('ingredients', 'instructions') and optional_cats and category in optional_cats:
                continue
            if field not in recipe or not recipe[field]:
                self.error(recipe_id, f"Missing required field: {field}")
        if 'id' in recipe:
            if not re.match(r'^[a-z0-9-]+$', recipe['id']):
                self.error(recipe_id, f"Invalid ID format (should be lowercase slug): {recipe['id']}")
        if 'category' in recipe:
            if recipe['category'] not in c['valid_categories']:
                self.warn(recipe_id, f"Unknown category: {recipe['category']}")
        if 'confidence' in recipe and recipe['confidence']:
            overall = recipe['confidence'].get('overall')
            if overall and overall not in c['valid_confidence']:
                self.error(recipe_id, f"Invalid confidence level: {overall}")
        if 'ingredients' in recipe:
            self.validate_ingredients(recipe_id, recipe['ingredients'], recipe.get('title', ''))
        if 'instructions' in recipe:
            self.validate_instructions(recipe_id, recipe['instructions'], category)
        uses_low_temps = False
        if c['temperature_mode'] == 'cheese_dual_range':
            uses_low_temps = self.is_low_temp_context(
                recipe_id, category, recipe.get('title', ''), recipe.get('tags', []))
        if 'temperature' in recipe and recipe['temperature']:
            self.validate_temperature(recipe_id, recipe['temperature'], category,
                                      recipe.get('title', ''), uses_low_temps)
        if 'image_refs' in recipe:
            self.validate_image_refs(recipe_id, recipe['image_refs'])
        if 'nutrition' not in recipe or not recipe['nutrition']:
            if c['warn_missing_nutrition'] and category not in optional_cats:
                self.warn(recipe_id, "Missing nutrition data")
        else:
            self.validate_nutrition(recipe_id, recipe['nutrition'])
        if 'conversions' in recipe and recipe['conversions']:
            self.validate_conversions(recipe_id, recipe['conversions'])

    def validate_ingredients(self, recipe_id, ingredients, title=''):
        if not isinstance(ingredients, list):
            self.error(recipe_id, "Ingredients must be a list")
            return
        overrides = self.c['limit_overrides']
        active = []
        if overrides:
            title_lower = title.lower()
            id_lower = recipe_id.lower()
            for ov in overrides:
                if any(kw in title_lower for kw in ov['keywords']) or \
                   any(kw in id_lower for kw in ov['keywords']):
                    active.append(ov)
        for i, ing in enumerate(ingredients):
            if not isinstance(ing, dict):
                self.error(recipe_id, f"Ingredient {i} must be an object")
                continue
            if 'item' not in ing:
                self.error(recipe_id, f"Ingredient {i} missing 'item' field")
            item = ing.get('item', '').lower()
            qty = ing.get('quantity', '')
            unit = ing.get('unit', '').lower()
            self.check_quantity_sanity(recipe_id, item, qty, unit, active)

    def parse_quantity(self, qty):
        if '/' in str(qty):
            parts = str(qty).split()
            if len(parts) == 2:
                whole = float(parts[0])
                frac_parts = parts[1].split('/')
                return whole + float(frac_parts[0]) / float(frac_parts[1])
            frac_parts = str(qty).split('/')
            return float(frac_parts[0]) / float(frac_parts[1])
        if self.c['quantity_parse'] == 'simple':
            return float(qty.replace('-', '.').split()[0])
        qty_str = str(qty).replace('-', ' ').split()[0]
        if '-' in str(qty):
            range_parts = str(qty).split('-')
            return max(float(p.strip().split()[0]) for p in range_parts if p.strip())
        return float(qty_str)

    def check_quantity_sanity(self, recipe_id, item, qty, unit, active_overrides=()):
        c = self.c
        if not qty or qty == '' or '[UNCLEAR]' in str(qty):
            return
        if any(fp in item for fp in c['sanity_skip_item_substrings']):
            return
        try:
            qty_float = self.parse_quantity(qty)
        except (ValueError, IndexError):
            return
        skip_over = c['sanity_skip_quantity_over']
        if skip_over is not None and qty_float > skip_over:
            return
        word_boundary = c['sanity_match'] == 'word_boundary'
        for check_item, limits in c['sanity_limits'].items():
            if word_boundary:
                matched = re.search(rf'\b{check_item}\b', item)
            else:
                matched = check_item in item
            if matched:
                for ov in active_overrides:
                    if ov['item'] == check_item:
                        limits = ov['limits']
                if 'cup' in unit and 'max_cups' in limits:
                    if qty_float > limits['max_cups']:
                        self.warn(recipe_id, f"Suspicious: {qty} {unit} {item} (max expected: {limits['max_cups']} cups)")
                if 'tbsp' in unit and 'max_tbsp' in limits:
                    if qty_float > limits['max_tbsp']:
                        self.warn(recipe_id, f"Suspicious: {qty} {unit} {item} (max expected: {limits['max_tbsp']} tbsp)")
                if 'tsp' in unit and 'max_tsp' in limits:
                    if qty_float > limits['max_tsp']:
                        self.warn(recipe_id, f"Suspicious: {qty} {unit} {item} (max expected: {limits['max_tsp']} tsp)")

    def validate_instructions(self, recipe_id, instructions, category=''):
        if not isinstance(instructions, list):
            self.error(recipe_id, "Instructions must be a list")
            return
        if len(instructions) == 0 and category not in self.c['empty_instructions_ok_categories']:
            self.error(recipe_id, "Instructions list is empty")
            return
        for i, inst in enumerate(instructions):
            if not isinstance(inst, dict):
                self.error(recipe_id, f"Instruction {i} must be an object")
                continue
            if 'text' not in inst:
                self.error(recipe_id, f"Instruction {i} missing 'text' field")

    def validate_temperature(self, recipe_id, temp, category='', title='', uses_low_temps=False):
        c = self.c
        match = re.search(r'(\d+)\s*°?F', temp)
        if not match:
            return
        temp_f = int(match.group(1))
        t_min, t_max = c['temp_min'], c['temp_max']
        mode = c['temperature_mode']
        if mode == 'cheese_dual_range' and uses_low_temps:
            ch_min, ch_max = c['cheese_temp_min'], c['cheese_temp_max']
            in_cheese_range = ch_min <= temp_f <= ch_max
            in_baking_range = t_min <= temp_f <= t_max
            if not (in_cheese_range or in_baking_range):
                self.warn(recipe_id, f"Temperature {temp_f}°F outside expected ranges (cheese: {ch_min}-{ch_max}°F, baking: {t_min}-{t_max}°F)")
            return
        min_temp = t_min
        if mode == 'low_temp_min' and self.is_low_temp_context(recipe_id, category, title, []):
            min_temp = c['temp_min_low']
        if temp_f < min_temp or temp_f > t_max:
            self.warn(recipe_id, f"Temperature {temp_f}°F outside typical range ({min_temp}-{t_max}°F)")

    def validate_image_refs(self, recipe_id, image_refs):
        if not isinstance(image_refs, list):
            self.error(recipe_id, "image_refs must be a list")
            return
        image_dir = self.repo_root / self.c['image_dir']
        for ref in image_refs:
            if not isinstance(ref, str):
                self.error(recipe_id, f"image_refs entry must be a string: {ref!r}")
                continue
            if self.c['image_skip_urls'] and (ref.startswith('http://') or ref.startswith('https://')):
                continue
            found = False
            for ext in self.c['image_extensions']:
                if (image_dir / f"{ref}{ext}").exists():
                    found = True
                    break
            if not found:
                self.warn(recipe_id, f"Referenced image not found: {ref}")

    def validate_nutrition(self, recipe_id, nutrition):
        status = nutrition.get('status')
        if status == 'insufficient_data':
            if not nutrition.get('missing_inputs'):
                self.warn(recipe_id, "Nutrition status is 'insufficient_data' but missing_inputs is empty")
        elif status in ['complete', 'partial']:
            per_serving = nutrition.get('per_serving', {})
            if not per_serving or all(v is None for v in per_serving.values()):
                self.warn(recipe_id, f"Nutrition status is '{status}' but no nutrition values provided")

    def validate_conversions(self, recipe_id, conversions):
        if conversions.get('has_conversions'):
            if not conversions.get('ingredients_metric'):
                self.warn(recipe_id, "has_conversions is true but ingredients_metric is empty")

    def validate_all(self, recipes_data):
        if 'recipes' not in recipes_data:
            self.error('GLOBAL', "Missing 'recipes' array in JSON")
            return
        recipes = recipes_data['recipes']
        ids_seen = set()
        for recipe in recipes:
            recipe_id = recipe.get('id', 'UNKNOWN')
            if recipe_id in ids_seen:
                self.error(recipe_id, "Duplicate recipe ID")
            ids_seen.add(recipe_id)
            self.validate_recipe(recipe)
        for recipe in recipes:
            variant_of = recipe.get('variant_of')
            if variant_of and variant_of not in ids_seen:
                self.error(recipe.get('id'), f"variant_of references non-existent recipe: {variant_of}")

    def report(self):
        print("\n" + "="*60)
        print("RECIPE VALIDATION REPORT")
        print("="*60)
        if self.errors:
            print(f"\n{len(self.errors)} ERROR(S):")
            for err in self.errors:
                print(f"  {err}")
        else:
            print("\nNo errors found.")
        if self.warnings:
            print(f"\n{len(self.warnings)} WARNING(S):")
            for warn in self.warnings:
                print(f"  {warn}")
        else:
            print("\nNo warnings.")
        print("\n" + "="*60)
        if self.errors:
            return 1
        if self.strict and self.warnings:
            return 1
        return 0


def main_cli(repo_root, config_path, argv):
    strict = '--strict' in argv
    try:
        cfg = load_config(config_path)
    except ConfigError as e:
        print(f"ERROR: {e}")
        return 1
    recipes_file = Path(repo_root) / cfg['data_file']
    if not recipes_file.exists():
        print(f"ERROR: Cannot find {recipes_file}")
        return 1
    print(f"Validating: {recipes_file}")
    try:
        with open(recipes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON - {e}")
        return 1
    validator = RecipeValidator(cfg, repo_root, strict=strict)
    validator.validate_all(data)
    exit_code = validator.report()
    print(f"\nTotal recipes: {len(data.get('recipes', []))}")
    return exit_code
