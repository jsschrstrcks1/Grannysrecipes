<!-- Soli Deo Gloria. Reasoning log — how and why, not just what. -->

# Reasoning Log

## 2026-08-30 — Variant tabs on the recipe page, phase 3 (syl)

**Asked:** One listing per dish; versions as tabs with provenance (operator directive,
household dup/variant campaign).

**Weighed:** This site already collapsed variants in its lists and resolved families in
findVariants, but presented them as a <select> dropdown. Tabs put the versions in sight:
labeled by attribution (then short source note, then title), canonical first, active tab
inert, aria tablist roles, hover shows full title + variant notes. Identical change
applied across the three family sites and Other Recipes — the scripts share one lineage
and were patched from one verified template (exact-match replacement, node --check on
each).

**Decided:** renderVariantsDropdown -> renderVariantTabs; select-change handler -> tab
click handlers; .variant-tab styles appended beside the dropdown styles. Presentation
only; 0 data records changed.

**Unsure:** Untested in a browser here; logic mirrors the dropdown handler one-for-one.

## 2026-08-30 — Variant linking, phase 2 (syl)

**Asked:** Link same-dish recipes to a canonical primary per operator law 990f37e1
(duplicates removed in phase 1 — this store had none; variants linked here).

**Weighed:** 22 same-title clusters, mostly a summary card beside its full transcription
(joyces-chicken-granny vs joyces-chicken-full-granny). Content differs, so per law they
are variants, not duplicates; a future editorial pass could instead merge card+full pairs
into single records, noted on the phase-2 HLS task.

**Decided:** 22 clusters linked (22 variant_of + 22 variants entries, additive-only).
Integrity: 0 cycles, 0 broken refs, 0 one-directional links. Report:
admin/VARIANTS-LINKED.json. Shards + index regenerated with scripts/shard_recipes.py.

**Unsure:** Whether "-full-" pairs should eventually be merged rather than tabbed; left
as variants per the letter of the law.

