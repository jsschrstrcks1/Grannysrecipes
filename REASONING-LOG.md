<!-- Soli Deo Gloria. Reasoning log — how and why, not just what. -->

# Reasoning Log

## 2026-08-30 — Follow-up C: cross-title same-dish variants, a REVIEWED pass (syl)

**Asked.** Operator: proceed — the "Grandma's Beef Wellington vs Gordon Ramsay's Beef
Wellington" class, deliberately left out of the mechanical phase 2.

**Weighed.** Candidates come from stripping ONLY attribution markers (leading possessive
names, trailing parentheticals); a cluster links ONLY when a bare-titled member exists to
be the canonical — clusters without one (Cheese Cake (Lemon Jello) vs (Philadelphia)) may
be different dishes and are DEFERRED to admin/CROSS-TITLE-VARIANTS-REVIEW.json, never
auto-linked. The dry-run lists were read line by line, and review caught three real
traps, each now a guard in the tool: dish-name possessives (Devil's Cake is not anyone's
attribution of "Cake"; Millionaire's Shortbread is its own dish), generic cores (Min's
Cake under a record titled just "Cake" claims more than titles know), and an
ingredient-overlap check born from Bailey's Peppermint Cream — a liqueur drink that would
have tabbed under a gelatin candy. Placeholder ingredient lists ("See instructions")
count as no-data so sparse records are judged by title, not fake mismatch.

**Decided.** Links applied additive-only with the phase-2 contract (no rewrites, no
2-cycles, family roots adopted). Where the overlap guard deferred pairs that eyes-on
review confirmed same-dish (apple pie 1796 vs modern, mix vs scratch biscuits,
bread-machine versions, Chef's Hamburgers, Sara's ancients Sponge Cake, Ethelyn's Carrot
Casserole), they were hand-linked and recorded as hand_reviewed_links in the report.
Integrity after: 0 cycles, 0 broken refs, 0 one-directional links; dedup --check CLEAN;
shards + indexes regenerated.

**Unsure.** The deferred clusters in the review report are genuinely ambiguous and wait
for Ken. The threshold (0.25 word overlap) is a judgment; its false-defers were caught by
hand this pass, but a future pass should re-eyeball anything it defers.

## 2026-08-30 — Follow-up B: the card/-full- twin transcriptions, verified against the scans (syl)

**Asked.** Operator: proceed — merge the summary-card + "-full-" pairs into single records.

**Weighed.** They were not card+full pairs: both sides carried complete transcriptions of
the SAME source, citing different image refs. Reading the actual scans showed (a) the
base records' image refs were systematically wrong (a roast, herbs, blueberry jam, a fish
dinner standing in for soufflé, chicken, hens), and (b) BOTH transcriptions carried real
errors the card contradicts — scrambled column quantities (soufflé: flour/sugar/milk all
wrong on both sides), a dropped ingredient (Savory Beef lost its 1/2 cup celery and
halved the sour cream on both sides), an invented quantity (1/3 cup Minute Rice that the
sheet does not state), and one wholly UNSOURCED basting sauce (butter/Dijon/
Worcestershire on Deviled Cornish Hens — nowhere on the card). So each merge was done
against the scan, not by picking a transcription.

**Decided.** 7 of 8 pairs merged (201 → 194 records), every keeper corrected to its
verified scan, image refs reduced to the verified ones, every removed record and every
displaced unsourced fragment preserved whole in admin/MERGED-AWAY.json, and each keeper
notes exactly what the scan settled. Joyce's Chicken did NOT merge: its source scan is
unlocated (all cited refs provably show other dishes), the two transcriptions conflict,
so both stay as linked variants marked low-confidence with the gap stated on the record.
Gates: dedup --check CLEAN, 0 dangling refs, shards regenerated.

**Unsure.** The corned-beef card's step 2/3 sentence split is hard to read at scan
resolution (noted on the record). Whether the soufflé card's "1 Tbsp. baking powder" is
the packet's own typo is not mine to judge — it is what the card says. Joyce's Chicken
needs the original card found and rescanned.

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

