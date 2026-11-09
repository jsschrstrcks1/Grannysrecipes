#!/usr/bin/env python3
"""
import_batch.py: the ONE batch importer for the household recipe repos.

Replaces the hand-written scripts/add_*_batchN.py importers. Input is a JSON file holding
a list of recipe objects. Byte-identical in every repo that carries it; repo differences
come from scripts/recipe_validator/config.json.

Usage:
    python scripts/recipe_validator/import_batch.py BATCH.json            # dry run, writes nothing
    python scripts/recipe_validator/import_batch.py BATCH.json --apply    # write
    options: --config PATH (default: config.json beside this file)
             --repo-root PATH (default: the repo holding this file)

What it guarantees
    * Dry run by default. Only --apply writes.
    * Skips ids already in the data file AND ids repeated within the batch (first wins).
    * Validates every NEW recipe with the shared validator before writing. Any ERROR
      refuses the whole write. Warnings are printed and do not block.
    * Never modifies an existing recipe. New recipes are appended exactly as given;
      content is never rewritten, so uncertain text stays "[UNCLEAR]".
    * Updates only the meta count fields named in config meta_count_fields that already
      exist in the file's meta. No other meta field is touched.
    * Preserves the file's JSON style: indent=2, ensure_ascii matching the file (raw
      non-ASCII present means ensure_ascii=False), trailing newline as found. A file that
      would not re-serialise byte-identically is refused rather than rewritten.
    * Atomic write: a temp file in the same directory, then os.replace.

Exit codes
    0  dry run complete, or applied (including "nothing new to add")
    1  usage, unreadable input, bad config, or a file whose style cannot be preserved
    2  refused: a new recipe failed validation; nothing written

Python standard library only. Soli Deo Gloria.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from recipe_validator.core import RecipeValidator, load_config, ConfigError  # noqa: E402

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_REFUSED = 2


def detect_style(raw):
    """Return (ensure_ascii, trailing_newline) for the raw bytes of a JSON file."""
    ensure_ascii = not any(b > 127 for b in raw)
    trailing_newline = raw.endswith(b'\n')
    return ensure_ascii, trailing_newline


def serialize(data, ensure_ascii, trailing_newline):
    text = json.dumps(data, indent=2, ensure_ascii=ensure_ascii)
    if trailing_newline:
        text += '\n'
    return text.encode('utf-8')


def plan_import(data, batch, validator):
    """Decide what the batch does to data. Pure: data is not modified.

    Returns dict with keys: added (list of recipes), skipped_existing, skipped_batch_dup,
    errors, warnings (lists of strings).
    """
    existing_ids = set()
    for r in data.get('recipes', []):
        if isinstance(r, dict):
            rid = r.get('id')
            if isinstance(rid, str):
                existing_ids.add(rid)

    added, skipped_existing, skipped_dup, pre_errors = [], [], [], []
    seen = set()
    for i, recipe in enumerate(batch):
        if not isinstance(recipe, dict):
            pre_errors.append(f"ERROR [batch item {i}]: recipe must be an object")
            continue
        rid = recipe.get('id')
        if rid is not None and not isinstance(rid, str):
            pre_errors.append(f"ERROR [batch item {i}]: id must be a string: {rid!r}")
            continue
        if rid in existing_ids:
            skipped_existing.append(rid)
            continue
        if rid is not None and rid in seen:
            skipped_dup.append(rid)
            continue
        if rid is not None:
            seen.add(rid)
        added.append(recipe)

    for recipe in added:
        validator.validate_recipe(recipe)
    known = existing_ids | seen
    for recipe in added:
        variant_of = recipe.get('variant_of')
        if variant_of and variant_of not in known:
            validator.error(recipe.get('id'), f"variant_of references non-existent recipe: {variant_of}")

    return {
        'added': added,
        'skipped_existing': skipped_existing,
        'skipped_batch_dup': skipped_dup,
        'errors': pre_errors + validator.errors,
        'warnings': list(validator.warnings),
    }


def atomic_write(path, payload):
    path = Path(path)
    mode = None
    try:
        mode = path.stat().st_mode & 0o7777
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def run(batch_path, apply=False, config_path=None, repo_root=None, out=print):
    here = Path(__file__).resolve().parent
    config_path = Path(config_path) if config_path else here / 'config.json'
    repo_root = Path(repo_root) if repo_root else here.parent.parent

    try:
        cfg = load_config(config_path)
    except ConfigError as e:
        out(f"ERROR: {e}")
        return EXIT_USAGE

    data_path = repo_root / cfg['data_file']
    try:
        raw = data_path.read_bytes()
        data = json.loads(raw.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        out(f"ERROR: cannot read data file {data_path}: {e}")
        return EXIT_USAGE
    if not isinstance(data, dict) or not isinstance(data.get('recipes'), list):
        out(f"ERROR: {data_path} has no 'recipes' list")
        return EXIT_USAGE

    try:
        batch = json.loads(Path(batch_path).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        out(f"ERROR: cannot read batch file {batch_path}: {e}")
        return EXIT_USAGE
    if not isinstance(batch, list):
        out(f"ERROR: batch file {batch_path} must hold a JSON list of recipe objects")
        return EXIT_USAGE

    ensure_ascii, trailing_newline = detect_style(raw)
    if serialize(data, ensure_ascii, trailing_newline) != raw:
        out(f"ERROR: {data_path} does not re-serialise byte-identically "
            f"(indent=2, ensure_ascii={ensure_ascii}); refusing to rewrite it")
        return EXIT_USAGE

    out(f"Data file: {data_path} ({len(data['recipes'])} recipes)")
    out(f"Batch: {batch_path} ({len(batch)} recipes)")

    validator = RecipeValidator(cfg, repo_root)
    plan = plan_import(data, batch, validator)

    for rid in plan['skipped_existing']:
        out(f"  SKIP {rid} (already in data file)")
    for rid in plan['skipped_batch_dup']:
        out(f"  SKIP {rid} (duplicate within batch)")
    for r in plan['added']:
        out(f"  NEW  {r.get('id')} ({r.get('title', '')})")

    out(f"Validation of {len(plan['added'])} new recipe(s): "
        f"{len(plan['errors'])} error(s), {len(plan['warnings'])} warning(s)")
    for e in plan['errors']:
        out(f"  {e}")
    for w in plan['warnings']:
        out(f"  {w}")

    if plan['errors']:
        out("REFUSED: validation errors in new recipes; nothing written.")
        return EXIT_REFUSED

    new_total = len(data['recipes']) + len(plan['added'])
    meta = data.get('meta') if isinstance(data.get('meta'), dict) else {}
    meta_changes = [(f, meta[f]) for f in cfg['meta_count_fields'] if f in meta]
    for f, old in meta_changes:
        out(f"  meta.{f}: {old} -> {new_total}")

    if not plan['added']:
        out("Nothing new to add; nothing written.")
        return EXIT_OK

    if not apply:
        out("DRY RUN: nothing written. Re-run with --apply to write.")
        return EXIT_OK

    data['recipes'].extend(plan['added'])
    for f, _ in meta_changes:
        meta[f] = new_total
    atomic_write(data_path, serialize(data, ensure_ascii, trailing_newline))
    out(f"APPLIED: wrote {data_path} ({len(plan['added'])} added, {new_total} total).")
    return EXIT_OK


def main(argv=None):
    p = argparse.ArgumentParser(description="Import a JSON batch of recipes (dry run unless --apply).")
    p.add_argument('batch', help='JSON file holding a list of recipe objects')
    p.add_argument('--apply', action='store_true', help='write the data file (default: dry run)')
    p.add_argument('--config', help='config.json path (default: beside this file)')
    p.add_argument('--repo-root', help='repo root (default: the repo holding this file)')
    args = p.parse_args(argv)
    return run(args.batch, apply=args.apply, config_path=args.config, repo_root=args.repo_root)


if __name__ == '__main__':
    sys.exit(main())
