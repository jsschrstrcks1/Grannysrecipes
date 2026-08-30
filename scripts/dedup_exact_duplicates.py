#!/usr/bin/env python3
# Soli Deo Gloria.
"""
Remove EXACT duplicate recipes from a master recipes file.

Household law (memory 990f37e1, operator directive): Duplicates = EXACT same
recipe (remove entirely). Variants = even a little different (keep both, link
with variants field to the canonical primary). The dedup key is name + source
(memory c865b442) — two records that share a title but carry different
attributions are candidate VARIANTS and are never touched here.

A group is a removable duplicate set only when ALL of:
  - normalized title identical
  - ingredients identical (canonical JSON)
  - instructions identical (canonical JSON)
  - attributions compatible (equal after normalization, or empty on one side)

Keeper selection is human-centric (990f37e1): the most complete record wins
(more filled fields, nutrition, images, notes); ties prefer the id without a
trailing numeric suffix (the original import), then first position in file.
Fields the keeper lacks are merged in from the removed records (never
overwriting non-empty keeper fields; list fields are unioned order-preserving).

Every removal is appended to admin/MERGED-AWAY.json so nothing vanishes
silently. References to removed ids (variant_of, canonical_id, variants,
component_of) anywhere in the master are repointed to the kept id.

Usage:
    python3 scripts/dedup_exact_duplicates.py [--apply] [--master PATH] [--ledger PATH]

Default is DRY RUN: prints what would happen, writes nothing.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_MASTER = os.path.join(REPO, "data", "recipes.json")
DEFAULT_LEDGER = os.path.join(REPO, "admin", "MERGED-AWAY.json")

LIST_FIELDS = {"image_refs", "tags", "notes", "tips", "substitutions", "conversions"}
REF_FIELDS_STR = ("variant_of", "canonical_id", "component_of")
REF_FIELDS_LIST = ("variants", "components")


def norm_title(t):
    return " ".join(str(t or "").lower().replace('"', "").replace("“", "").replace("”", "").split())


def norm_attr(a):
    return " ".join(str(a or "").lower().split())


def canon(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=True, default=str)


def content_key(r):
    # notes are part of the identity: reference-guide records (0 ingredients, 0
    # instructions) carry their entire substance in notes — measured in
    # Grandmasrecipes, where two different guide pages share one title and would
    # otherwise collapse. A recipe differing only in notes is a VARIANT.
    return (
        norm_title(r.get("title")),
        canon(r.get("ingredients")),
        canon(r.get("instructions")),
        canon(r.get("notes")),
    )


def is_empty(v):
    return v is None or v == "" or v == [] or v == {}


def completeness(r):
    score = sum(1 for v in r.values() if not is_empty(v))
    # weight the fields a reader actually benefits from
    for f in ("nutrition", "image_refs", "notes", "source_note", "description", "tips"):
        if not is_empty(r.get(f)):
            score += 2
    return score


def has_numeric_suffix(rid):
    return bool(re.search(r"-\d+$", str(rid or "")))


def attr_compatible(group):
    attrs = {norm_attr(r.get("attribution")) for r in group}
    non_empty = {a for a in attrs if a}
    return len(non_empty) <= 1


def merge_into(keeper, loser):
    merged_fields = []
    for k, v in loser.items():
        if k == "id" or is_empty(v):
            continue
        if k in LIST_FIELDS and isinstance(v, list):
            cur = keeper.get(k) or []
            if not isinstance(cur, list):
                continue
            seen = {canon(x) for x in cur}
            added = [x for x in v if canon(x) not in seen]
            if added:
                keeper[k] = cur + added
                merged_fields.append(k)
        elif is_empty(keeper.get(k)):
            keeper[k] = v
            merged_fields.append(k)
    return merged_fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--check", action="store_true",
                    help="gate mode: exit 3 if any exact duplicate exists, 0 when clean (writes nothing)")
    ap.add_argument("--master", default=DEFAULT_MASTER)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    args = ap.parse_args()
    if args.apply and args.check:
        print("UNAVAILABLE: --apply and --check are mutually exclusive", file=sys.stderr)
        return 2

    with open(args.master, encoding="utf-8") as f:
        raw = f.read()
    doc = json.loads(raw)
    # Match the file's existing escape convention — a master kept with
    # ensure_ascii=True must not be silently rewritten to literal unicode
    # (thousands of lines of formatting churn drown the real 2-line change).
    escape_ascii = "\\u00" in raw
    recs = doc["recipes"] if isinstance(doc, dict) and "recipes" in doc else doc
    if not isinstance(recs, list):
        print(f"UNAVAILABLE: {args.master} is not a recipe list", file=sys.stderr)
        return 2

    groups = defaultdict(list)
    for i, r in enumerate(recs):
        if isinstance(r, dict) and r.get("title"):
            groups[content_key(r)].append((i, r))

    removals = []            # (removed_record, kept_id, merged_fields)
    keep_positions = set(range(len(recs)))
    skipped_attr = 0
    for key, members in groups.items():
        if len(members) < 2:
            continue
        group = [r for _, r in members]
        if not attr_compatible(group):
            skipped_attr += 1
            continue
        ranked = sorted(
            members,
            key=lambda ir: (-completeness(ir[1]), has_numeric_suffix(ir[1].get("id")), ir[0]),
        )
        keeper_idx, keeper = ranked[0]
        for idx, loser in ranked[1:]:
            merged = merge_into(keeper, loser)
            removals.append((loser, keeper.get("id"), merged))
            keep_positions.discard(idx)

    removed_ids = {r.get("id") for r, _, _ in removals}
    kept_for = {r.get("id"): kept for r, kept, _ in removals}

    # Repoint references to removed ids anywhere in the surviving records.
    repointed = 0
    survivors = [recs[i] for i in sorted(keep_positions)]
    surviving_ids = {r.get("id") for r in survivors}
    for r in survivors:
        for f in REF_FIELDS_STR:
            v = r.get(f)
            if isinstance(v, str) and v in removed_ids:
                r[f] = kept_for[v]
                repointed += 1
        for f in REF_FIELDS_STR + REF_FIELDS_LIST:
            v = r.get(f)
            if isinstance(v, list) and any(x in removed_ids for x in v):
                new = []
                for x in v:
                    tgt = kept_for.get(x, x)
                    if tgt != r.get("id") and tgt not in new:
                        new.append(tgt)
                r[f] = new
                repointed += 1

    print(f"master: {args.master}")
    print(f"recipes: {len(recs)} -> {len(survivors)}  (removing {len(removals)})")
    print(f"duplicate groups skipped for attribution mismatch (variants, phase 2): {skipped_attr}")
    print(f"references repointed: {repointed}")
    for r, kept, merged in removals[:10]:
        print(f"  - remove {r.get('id')!r} (keep {kept!r}, title {r.get('title')!r}"
              + (f", merged {merged}" if merged else "") + ")")
    if len(removals) > 10:
        print(f"  ... and {len(removals) - 10} more")

    # sanity: no surviving reference points at a removed id
    for r in survivors:
        for f in REF_FIELDS_STR:
            if isinstance(r.get(f), str) and r.get(f) in removed_ids:
                print(f"SANITY FAIL: {r.get('id')} .{f} still points at removed id", file=sys.stderr)
                return 2

    if args.check:
        # Three states, never two: REPORT (3) when duplicates exist, CLEAN (0) when the
        # tool looked and found none; unreadable input already exited 2 (UNAVAILABLE).
        if removals:
            print(f"\nREPORT — {len(removals)} exact duplicate(s) present. "
                  "Adding a duplicate is a hard error (household law c865b442).")
            return 3
        print("\nCLEAN — looked at every record, no exact duplicates.")
        return 0

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return 0

    if isinstance(doc, dict):
        doc["recipes"] = survivors
        if isinstance(doc.get("meta"), dict):
            for k in ("total_recipes", "total_count"):
                if k in doc["meta"]:
                    doc["meta"][k] = len(survivors)
    else:
        doc = survivors
    with open(args.master, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=escape_ascii)
        f.write("\n")

    ledger = []
    if os.path.exists(args.ledger):
        try:
            with open(args.ledger, encoding="utf-8") as f:
                ledger = json.load(f)
        except Exception:
            print(f"UNAVAILABLE: existing ledger {args.ledger} unreadable — refusing to overwrite", file=sys.stderr)
            return 2
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for r, kept, merged in removals:
        ledger.append({
            "date": now,
            "action": "exact-duplicate-removed",
            "removed_id": r.get("id"),
            "kept_id": kept,
            "title": r.get("title"),
            "merged_fields_into_keeper": merged,
            "removed_record": r,
        })
    os.makedirs(os.path.dirname(args.ledger), exist_ok=True)
    with open(args.ledger, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"\nAPPLIED. Ledger: {args.ledger} ({len(removals)} new entries; full records preserved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
