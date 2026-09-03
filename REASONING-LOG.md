<!-- Soli Deo Gloria. Reasoning log — how and why, not just what. -->

# Reasoning Log

## 2026-09-03 — observe hook: dead container path replaced by machine-neutral dispatch (open-claw-stuff #3094)

**Asked.** Household loop (patron yumi): close the dead-path defect the hls-dead-path-hooks task left open here.

**Weighed.** The PostToolUse observe hook pointed at `/home/user/ken/...`, absent on this Mac, so observation capture never ran and nothing said so. Alternatives: point it at a Mac path (the same defect mirrored — rejected); drop the hook (capture is doctrine — rejected); the canonical dispatch, which resolves by layout and fails loud-not-fatal — chosen, the same fix Project-Sophos #13 applied.

**Decided.** Installed `observe-tool-use-dispatch.sh` from canonical and repointed the settings entry to `$CLAUDE_PROJECT_DIR`. Probed: this layout → NOT FOUND on stderr, exit 0; inert fake ken via HOUSEHOLD_KEN_ROOT → runs, exit 0. No machine path remains in settings.

**Unsure.** Until `HOUSEHOLD_KEN_ROOT` is exported or a ken checkout sits beside this repo, capture still does not run here — now loudly instead of silently; whether the operator wants it running on the Mac at all is their call.

## 2026-09-03 — onboard the loud-bootstrap hook set (open-claw-stuff #3093)

**Asked.** Household loop (patron yumi): close the guard gap the distribution check reports for this repo.

**Weighed.** CLAUDE.md here asserts the household guards; the repo carried none of the hook files and no registrations, so the user-level dispatcher (which delegates only to repos carrying the guard file) admitted an unstamped Write — measured with an inert probe, exit 0. The remedy is the canonical installer, not a hand copy; the alternative of relying on user-level dispatch alone is exactly the false-CALM the parent task names.

**Decided.** Ran `admin/onboard-loud-bootstrap.mjs` from a canonical clone at the #3077 fix: five hook files plus four settings registrations. Re-probed: DENIED (exit 2), no orphan .household-library, stamped session still allowed.

**Unsure.** core.hooksPath is unset here, so the .githooks chain (including the reasoning-log guard) is dead in git — a separate household task (hh-hookspath-arming-parity); I did not arm it in this change.

## 2026-08-30 — Grandma's memorial album moved out (syl)

**Asked.** Operator (cleanup item 6): the Memorial/Grandma images belong to Grandma, not
Granny — move them to the Grandmasrecipes repo.

**Weighed.** 618 files, 394 MB — most of this repo's weight, and the wrong person's
archive. Verified landed in Grandmasrecipes (commit 255f4f2b, pushed) BEFORE removal
here, so the history never has a moment where the album exists nowhere. Reviewed samples
plus a document-likeness triage over all 606 photos found no recipe content, so nothing
recipe-linked in THIS repo's data depended on the folder (no record references any
Memorial path — checked).

**Decided.** git rm Memorial/Grandma; the album now lives in
Grandmasrecipes/Memorial/Grandma with a README pointer there.

**Unsure.** Nothing material — the copy was verified on the remote before the removal
committed.

## 2026-08-30 — Rebuilding the empty records, as far as honesty reaches (syl)

**Asked.** Operator: investigate the records with no ingredients/instructions and try to
rebuild them. (Correction to the earlier phrasing: it is 4 records showing 8 validator
errors, not 8 records.)

**Weighed.** All four point at scans that were never committed (gr-190, gr-240 — part of
a ~60-ref gap of unpushed images). The archive itself could not supply the text, so the
paths were: neighboring scans (gr-189 IS the Fish Is Good Food pamphlet PHOTO side —
panels and Gorton's branding match the record; its text side is the missing gr-190), and
brand research for the three "typed coupon card" records, since those are published
branded recipes, not family compositions. Fabricating from training memory was not on
the table.

**Decided.** Lactaid Rice Pudding and Kikkoman Yucatan Grilled Pork rebuilt from the
brands' own published recipes (lactaid.com via The Dairy Alliance credited mirror;
kikkomanusa.com), each marked RESEARCHED RECONSTRUCTION with the source URL, medium
confidence, and a verify-against-the-card note. The Enova muffins could NOT be recovered
(discontinued brand, recipe gone from the indexable web) — the record says so and stays a
stub rather than getting an invented ingredient list; same for the fish pamphlet text
side, whose record gained the verified gr-189 photo ref and Gorton's attribution. Bonus
verified fix while in the scans: the handwritten Beef Rice Meatballs card (gr-66) says
mix with 1/4 cup tomato juice — the transcription said 1/2; corrected with a note.
Validator errors 8 -> 4, both remaining are the deliberate honest stubs.

**Unsure.** Whether the coupon cards carried exactly the brands' web-published versions —
the notes say to verify when the physical cards are found and rescanned as gr-240. The
missing-scan gap (60 refs, gr-1xx-3xx) needs the originals pushed from wherever they
live; that is an operator-side step no agent can do from here.

## 2026-08-30 — Reader display settings on recipe pages (syl)

**Asked.** Operator: recipe pages show a LOT of data — add a settings area so readers
pick sections. Default view: the recipe with instructions first, then nutrition facts;
everything else unchecked. And (mid-work directive): with ALL settings on, the recipe
still leads and nutrition still follows it. Also answered: no, this did not exist before
— this session had only added variant tabs.

**Weighed.** The four sites share one script lineage, so one transformation was verified
on Allrecipes then applied with per-pattern exact-match counts (Grandmas needed its own
function-signature anchor and had an unconditional milk-substitution div to wrap). The
template was REORDERED, not just gated: description, source note, quick facts, and the
milk-substitution panel moved from above the ingredients to after nutrition, so section
order no longer depends on which toggles are on. The gear panel lists only sections the
current page actually has; prefs persist in localStorage (per browser, never server).

**Decided.** Defaults: nutrition ON; description, source, quick facts, milk-sub, notes,
tags, tips, confidence/flags, original scan all OFF. Verified in a real browser
(Playwright against a locally served copy): section order ingredients → instructions →
nutrition → optionals; nutrition visible and quick facts hidden by default; the gear
lists only present sections; checking Notes reveals it; the choice SURVIVES a reload.

**Unsure.** A pre-existing page error fires on recipe.html opened without a recipe hash
("Cannot read properties of null (reading style)") — reproduced on HEAD before this
change, left for its own fix. The conversion-notes block stays tied to the metric button
rather than the gear, deliberately — it already has a control.

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

