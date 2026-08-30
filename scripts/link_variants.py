#!/usr/bin/env python3
# Soli Deo Gloria.
"""
Link same-title recipe variants to a canonical primary.

Household law (memory 990f37e1): Variants = even a little different — keep both,
link with `variants` on the canonical primary; each variant carries `variant_of`.
Canonical selection is human-centric: family collections and named sources beat
reference imports; completeness and readability beat schema neatness or id order.

This tool is ADDITIVE ONLY:
  - An existing non-empty `variant_of` is never rewritten.
  - An existing `variants` list is unioned, never replaced.
  - If any cluster member already points at (or is) an established canonical,
    that canonical is adopted for the whole cluster rather than re-elected.

It also repairs one-directional links left by earlier passes: every id listed
in a canonical's `variants` gains `variant_of` back to it (when empty), and
every `variant_of` target gains the pointing id in its `variants` list.

Clusters are records sharing a normalized title. Records whose content differs
are exactly what a variant IS, so no content comparison gates the link — the
exact-duplicate pass (dedup_exact_duplicates.py) has already removed twins.

Usage:
    python3 scripts/link_variants.py [--apply] [--master PATH] [--report PATH]

Default is DRY RUN.
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
DEFAULT_REPORT = os.path.join(REPO, "admin", "VARIANTS-LINKED.json")

FAMILY_COLLECTIONS = {
    "mommom", "mommom-baker", "grandma-baker", "granny", "granny-hudson", "family",
}


def norm_title(t):
    return " ".join(str(t or "").lower().replace('"', "").replace("“", "").replace("”", "").split())


def is_empty(v):
    return v is None or v == "" or v == [] or v == {}


def completeness(r):
    score = sum(1 for v in r.values() if not is_empty(v))
    for f in ("nutrition", "image_refs", "notes", "source_note", "description", "tips"):
        if not is_empty(r.get(f)):
            score += 2
    return score


def canonical_score(r, position):
    fam = 1 if str(r.get("collection") or "") in FAMILY_COLLECTIONS else 0
    named = 1 if not is_empty(r.get("attribution")) else 0
    suffix = 1 if re.search(r"-\d+$", str(r.get("id") or "")) else 0
    # family first (operator law), then completeness, then a named source,
    # then a clean id, then original file order.
    return (-fam, -completeness(r), -named, suffix, position)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--master", default=DEFAULT_MASTER)
    ap.add_argument("--report", default=DEFAULT_REPORT)
    args = ap.parse_args()

    with open(args.master, encoding="utf-8") as f:
        raw = f.read()
    doc = json.loads(raw)
    escape_ascii = "\\u00" in raw
    recs = doc["recipes"] if isinstance(doc, dict) and "recipes" in doc else doc
    if not isinstance(recs, list):
        print(f"UNAVAILABLE: {args.master} is not a recipe list", file=sys.stderr)
        return 2

    by_id = {}
    for r in recs:
        rid = r.get("id")
        if rid in by_id:
            print(f"UNAVAILABLE: duplicate id {rid!r} — run the exact-dup pass first", file=sys.stderr)
            return 2
        by_id[rid] = r

    clusters = defaultdict(list)
    for pos, r in enumerate(recs):
        if isinstance(r, dict) and r.get("title"):
            clusters[norm_title(r.get("title"))].append((pos, r))

    added_variant_of = 0
    added_variants_entries = 0
    clusters_linked = 0
    conflicts = []
    report_rows = []

    def ensure_in_variants(canon_rec, vid):
        nonlocal added_variants_entries
        cur = canon_rec.get("variants")
        if not isinstance(cur, list):
            cur = [] if is_empty(cur) else [cur]
        if vid not in cur and vid != canon_rec.get("id"):
            cur.append(vid)
            canon_rec["variants"] = cur
            added_variants_entries += 1

    def ensure_variant_of(rec, canon_id):
        nonlocal added_variant_of
        if rec.get("id") == canon_id:
            return
        cur = rec.get("variant_of")
        if is_empty(cur):
            rec["variant_of"] = canon_id
            added_variant_of += 1
        elif cur != canon_id:
            conflicts.append({"id": rec.get("id"), "existing_variant_of": cur, "cluster_canonical": canon_id})

    # Pass 1 — repair one-directional existing links (household-wide asymmetry).
    for r in recs:
        vo = r.get("variant_of")
        if isinstance(vo, str) and vo in by_id:
            ensure_in_variants(by_id[vo], r["id"])
        for vid in (r.get("variants") or [] if isinstance(r.get("variants"), list) else []):
            if vid in by_id:
                ensure_variant_of(by_id[vid], r["id"])

    # Pass 2 — same-title clusters.
    for key, members in clusters.items():
        if len(members) < 2:
            continue
        group = [r for _, r in members]

        # Follow variant_of chains to their root, so a record that is both a
        # variant and a mini-canonical (A -> B while A also lists variants)
        # never gets elected over its own parent. Cycle-guarded.
        def root_of(rid):
            seen = set()
            while rid in by_id and rid not in seen:
                seen.add(rid)
                vo = by_id[rid].get("variant_of")
                if not (isinstance(vo, str) and vo in by_id):
                    return rid
                rid = vo
            return rid

        # adopt an established canonical when one exists inside or via links
        established = []
        for r in group:
            vo = r.get("variant_of")
            if isinstance(vo, str) and vo in by_id:
                established.append(root_of(vo))
            if not is_empty(r.get("variants")):
                established.append(root_of(r["id"]))
        if established:
            # most-claimed target wins; in-cluster preferred over out-of-cluster
            in_cluster = {r["id"] for r in group}
            established.sort(key=lambda c: (c not in in_cluster, -established.count(c)))
            canon_id = established[0]
        else:
            ranked = sorted(members, key=lambda pr: canonical_score(pr[1], pr[0]))
            canon_id = ranked[0][1]["id"]
        canon_rec = by_id.get(canon_id)
        if canon_rec is None:
            conflicts.append({"cluster": key, "reason": f"canonical {canon_id} not in store"})
            continue
        linked_any = False
        for r in group:
            if r["id"] == canon_id:
                continue
            # A member already claimed by a DIFFERENT family keeps its family —
            # linking it here too would put one record under two canonicals.
            existing_vo = r.get("variant_of")
            if isinstance(existing_vo, str) and existing_vo != canon_id and existing_vo in by_id:
                conflicts.append({"id": r.get("id"), "existing_variant_of": existing_vo,
                                  "cluster_canonical": canon_id})
                continue
            before = (r.get("variant_of"), len(canon_rec.get("variants") or []))
            ensure_variant_of(r, canon_id)
            ensure_in_variants(canon_rec, r["id"])
            after = (r.get("variant_of"), len(canon_rec.get("variants") or []))
            if before != after:
                linked_any = True
        # a canonical is not itself a variant of a cluster member
        if isinstance(canon_rec.get("variant_of"), str) and canon_rec["variant_of"] in {r["id"] for r in group}:
            conflicts.append({"id": canon_id, "reason": "canonical carries variant_of into own cluster",
                             "variant_of": canon_rec["variant_of"]})
        if linked_any:
            clusters_linked += 1
            report_rows.append({
                "title": group[0].get("title"),
                "canonical": canon_id,
                "members": [r["id"] for r in group],
            })

    print(f"master: {args.master}")
    print(f"clusters newly/further linked: {clusters_linked}")
    print(f"variant_of added: {added_variant_of} · variants entries added: {added_variants_entries}")
    print(f"conflicts (left untouched, reported): {len(conflicts)}")
    for c in conflicts[:8]:
        print(f"  ! {c}")
    for row in report_rows[:6]:
        print(f"  e.g. {row['title']!r}: canonical={row['canonical']} members={len(row['members'])}")

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply.")
        return 0

    with open(args.master, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=escape_ascii)
        f.write("\n")

    existing = []
    if os.path.exists(args.report):
        try:
            with open(args.report, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            print(f"UNAVAILABLE: report {args.report} unreadable — refusing to overwrite", file=sys.stderr)
            return 2
    existing.append({
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "clusters_linked": clusters_linked,
        "variant_of_added": added_variant_of,
        "variants_entries_added": added_variants_entries,
        "conflicts": conflicts,
        "links": report_rows,
    })
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"\nAPPLIED. Report: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
