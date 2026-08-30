<!-- Soli Deo Gloria. Reasoning log — how and why, not just what. -->

# Reasoning Log

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

