#!/usr/bin/env python3
# Soli Deo Gloria.
"""
Reviewed pass: link DIFFERENT-title same-dish variants (the "Grandma's Beef
Wellington" vs "Gordon Ramsay's Beef Wellington" case) to a canonical primary.

Titles are normalized by stripping ONLY attribution/elaboration markers:
  - a leading possessive name:      "Karen's Baked Beans"  -> "Baked Beans"
  - a trailing parenthetical:       "Asiago (Fresh Asiago)" -> "Asiago"

A cluster is linked ONLY when a BARE member exists — a record whose full title
equals the stripped core. The bare member (or its existing family root) is the
canonical; the stripped members join its family. Clusters with NO bare member
(e.g. "24-Hour Salad (Vegetable)" vs "(Fruit)", "Cheese Cake (Lemon Jello)" vs
"(Philadelphia)") may be genuinely different dishes sharing a naming pattern,
so they are NEVER auto-linked — they go to the review report for a human eye.

Additive-only, same contract as link_variants.py: existing variant_of is never
rewritten; a member already claimed by a different family is skipped and
reported; no 2-cycles; existing family roots are adopted via chain-walk.

Usage:
    python3 scripts/link_cross_title_variants.py [--apply] [--master PATH] [--report PATH]

Default is DRY RUN and prints EVERY proposed link for review.
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
DEFAULT_REPORT = os.path.join(REPO, "admin", "CROSS-TITLE-VARIANTS-REVIEW.json")

FAMILY_COLLECTIONS = {
    "mommom", "mommom-baker", "grandma-baker", "granny", "granny-hudson", "family",
}
# placeholder cores that name NO dish — never cluster on these
CORE_STOPLIST = {"handwritten recipe", "recipe", "untitled", "unknown"}

# Possessives that are part of a DISH'S OWN NAME, never an attribution — stripping
# them would tab Devil's Cake under generic "Cake" (a false merge caught in review).
DISH_POSSESSIVES = {
    "devil", "devils", "poor man", "angel", "shepherd", "fisherman", "hunter",
    "king", "queen", "monkey", "hornet", "bird", "hobo", "drunkard", "preacher",
    "emperor", "gentleman", "ploughman", "sailor", "beggar", "miner", "logger",
    "millionaire", "millionaires",
}

# Cores too generic to assert "same dish" from a possessive strip alone —
# "Min's Cake" under a record titled just "Cake" claims more than the titles know.
GENERIC_CORES = {"cake", "cookies", "pastry", "bread", "pie", "pudding", "salad", "soup", "candy"}

POSS = re.compile(r"^([A-Z][\w.]*(?:\s+[A-Z][\w.]*){0,2})[’']s\s+")
PAREN = re.compile(r"\s*\(([^)]{2,40})\)\s*$")


def norm(t):
    return " ".join(str(t or "").lower().replace('"', "").split())


def strip_attr(title):
    t = str(title or "").strip()
    stripped = []
    m = POSS.match(t)
    if m and m.group(1).lower().replace(".", "") not in DISH_POSSESSIVES:
        stripped.append(m.group(1))
        t = t[m.end():]
    m = PAREN.search(t)
    if m:
        stripped.append(m.group(1))
        t = PAREN.sub("", t)
    return t.strip(), stripped


def is_empty(v):
    return v is None or v == "" or v == [] or v == {}


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
    by_id = {r.get("id"): r for r in recs}

    def root_of(rid):
        seen = set()
        while rid in by_id and rid not in seen:
            seen.add(rid)
            vo = by_id[rid].get("variant_of")
            if not (isinstance(vo, str) and vo in by_id):
                return rid
            rid = vo
        return rid

    PLACEHOLDER_ING = re.compile(r"see (instructions|recipe|below)|not listed", re.I)

    def ing_words(r):
        ings = r.get("ingredients") or []
        # a lone placeholder row ("See instructions") is NO data, not a mismatch
        if len(ings) == 1:
            txt = ings[0] if isinstance(ings[0], str) else (ings[0].get("text") or ings[0].get("item") or "")
            if PLACEHOLDER_ING.search(str(txt)):
                return set()
        out = set()
        for i in ings:
            txt = i if isinstance(i, str) else (i.get("text") or i.get("item") or "")
            for w in re.findall(r"[a-z]{4,}", str(txt).lower()):
                out.add(w)
        return out

    def same_dish_plausible(a, b):
        # Guard for POSSESSIVE-derived links: "Bailey's Peppermint Cream" (a liqueur
        # drink) must not tab under "Peppermint Cream" (a gelatin candy). When both
        # records list ingredients, require some real overlap; when either has none,
        # let the title judgment stand.
        wa, wb = ing_words(a), ing_words(b)
        if not wa or not wb:
            return True
        overlap = len(wa & wb) / min(len(wa), len(wb))
        return overlap >= 0.25

    clusters = defaultdict(list)
    for r in recs:
        core, stripped = strip_attr(r.get("title"))
        key = norm(core)
        if not key or key in CORE_STOPLIST or len(key) < 4:
            continue
        clusters[key].append((r, bool(stripped)))

    linked = []          # rows for the report: what was linked and why
    deferred = []        # no bare member — a human decides
    conflicts = []
    added_vo = 0
    added_var = 0

    def ensure_links(canon_id, member):
        nonlocal added_vo, added_var
        canon = by_id[canon_id]
        if member.get("id") == canon_id:
            return False
        vo = member.get("variant_of")
        if isinstance(vo, str) and vo and vo != canon_id and vo in by_id:
            conflicts.append({"id": member["id"], "existing_variant_of": vo, "wanted": canon_id})
            return False
        if canon.get("variant_of") == member.get("id"):
            return False                       # never mint a 2-cycle
        changed = False
        if is_empty(member.get("variant_of")):
            member["variant_of"] = canon_id
            added_vo += 1
            changed = True
        cur = canon.get("variants")
        if not isinstance(cur, list):
            cur = [] if is_empty(cur) else [cur]
        if member["id"] not in cur:
            cur.append(member["id"])
            canon["variants"] = cur
            added_var += 1
            changed = True
        return changed

    for key, members in sorted(clusters.items()):
        if len(members) < 2:
            continue
        titles = {m[0].get("title") for m in members}
        strips = [m for m in members if m[1]]
        if not strips or len(titles) < 2:
            continue                            # same-title work was phase 2's
        bares = [r for r, s in members if not s and norm(r.get("title")) == key]
        if not bares or key in GENERIC_CORES:
            deferred.append({"core": key, "members": [
                {"id": r["id"], "title": r.get("title"), "attribution": r.get("attribution")}
                for r, _ in members]})
            continue
        # canonical: the bare member's family root; prefer a family-collection bare
        bares.sort(key=lambda r: (str(r.get("collection")) not in FAMILY_COLLECTIONS, r.get("id")))
        canon_id = root_of(bares[0]["id"])
        if canon_id not in by_id:
            continue
        row = {"core": key, "canonical": canon_id, "linked": [], "already": []}
        for r, s in members:
            if r["id"] == canon_id or root_of(r["id"]) == canon_id:
                if r["id"] != canon_id:
                    row["already"].append(r["id"])
                continue
            # possessive-stripped members carry a person/brand name — verify the
            # dishes plausibly match before claiming they are versions of one thing
            if POSS.match(str(r.get("title") or "")) and not same_dish_plausible(r, by_id[canon_id]):
                deferred.append({"core": key, "members": [
                    {"id": r["id"], "title": r.get("title"), "attribution": r.get("attribution"),
                     "reason": "ingredient overlap below threshold vs canonical " + canon_id}]})
                continue
            if ensure_links(canon_id, r):
                row["linked"].append({"id": r["id"], "title": r.get("title")})
        if row["linked"]:
            linked.append(row)

    print(f"master: {args.master}")
    print(f"clusters linked: {len(linked)} (+{added_vo} variant_of, +{added_var} variants entries)")
    print(f"deferred for human review (no bare-titled member): {len(deferred)}")
    print(f"conflicts (other family, untouched): {len(conflicts)}")
    for row in linked:
        names = ", ".join(f"{m['title']!r}" for m in row["linked"])
        print(f"  LINK {row['core']!r}: canonical={row['canonical']} <- {names}")

    if not args.apply:
        print("\nDRY RUN — nothing written. Review the LINK lines, then --apply.")
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
        "linked": linked,
        "deferred_for_review": deferred,
        "conflicts": conflicts,
    })
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"\nAPPLIED. Report: {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
