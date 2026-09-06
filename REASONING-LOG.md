<!-- Soli Deo Gloria. Reasoning log — how and why, not just what. -->

# Reasoning Log

## 2026-09-06 — preserve observer diagnostics across the cluster resolver merge

**Asked.** Resume the authorized guard rollout and verify Granny's installed stack.

**Weighed.** Fresh main 0f94bf2 passes 12 of 14 hook tests. Its cluster-root resolver merge replaced the reviewed observer-failure diagnostic with a silent successful exit. The new fallback also let the missing-observer fixture reach a real household observer. Both failures were reproduced before editing.

**Decided.** Restore the nonfatal failure diagnostic while retaining every resolver candidate. Pin the fixture cluster root to a disposable directory and test payload forwarding and failure reporting through that fallback. All 15 hook tests, shell syntax, diff checks and privacy checks pass. Recipe validation still reports four errors and 59 warnings across 194 recipes; recipe data and validators are unchanged.

**Unsure.** Independent review and installed verification are pending. A successful dispatcher invocation does not establish downstream persistence. This repair does not establish household-wide deployment or settle Mom's earlier Git-hook arming refusal.

_Runtime: Codex_

## 2026-09-06 — merge train: land PR #39 with the CURRENT canonical loud-bootstrap hooks

**Asked.** Ken (2026-09-05): "merge them careful not clever" — land the open yumi PRs, this repo's hook rollout stack included.

**Weighed.** The PR's copies of the loud-bootstrap hooks were a 2026-09-03 snapshot of a canonical branch that has since changed on open-claw-stuff main (household markers adopted, the read-order guard's own secret made fail-closed, the stamp hook's parallel-read merge). Merging the snapshot as-is would install a guard that matches no canonical commit. The household's own tool for this, admin/onboard-loud-bootstrap.mjs, copies the CURRENT canonical trio and is idempotent.

**Decided.** Merge the PR (its intent is exactly "resync from canonical"), then run onboard-loud-bootstrap from open-claw-stuff main on the merged tree so the trio is byte-identical to canonical, and gate the result on an INERT live probe of this repo's guard: an unstamped Write inside the repo is denied (exit 2), an outside Write allowed, and any drift from canonical is refused rather than reported clean.

**Unsure.** Synced copies drift again the moment canonical moves; the named limit of spec §5.2 stands. This repo's reasoning-log guard reads .git/COMMIT_EDITMSG, which does not exist in a git worktree, so the [no-reasoning] opt-out is invisible here — registered as a finding rather than worked around; this entry is the honest record instead.

## 2026-09-05 — integrate the preserved observation, discovery and arming stack

**Asked.** Finish Granny's remaining guard stack in isolation, preserving sibling history and family content; publish for independent review, not deployment.

**Weighed.** Repaired onboarding 5f488807 and original stack head 0c774f9f share an ancestor. Merged the original histories without rewriting them. Only this log conflicted; exact inclusion checks preserve all nine sections from one conflict side and ten from the other. The original arming banner claimed downstream checks that Granny does not carry. Grandma main 5c289f9e contains independently reviewed corrections and fixture tests.

**Decided.** Adopt those truthful arming/observer-failure changes and five integration tests; protect arm and observer registrations alongside the bootstrap guards. Fourteen tests pass, plus privacy and shell syntax checks. Recipe validation remains at four errors and 59 warnings across 194 recipes. Existing log evidence explains the two incomplete records as deliberately honest stubs awaiting absent sources; no recipe repair is inferred here. Recipe, image, site, privacy and Granny pre-commit files are unchanged from main. Original root/observer/arming commits remain ancestors of this integration.

**Unsure.** Independent integration review, remote checks and live installation are still pending. Root discovery on this machine may require explicit environment paths, and absent observer roots remain a reported runtime gap. Configuration and executable bits are not proof of downstream enforcement; required-hook checks retain their documented substring/working-tree limitations.

## 2026-09-05 — adopt reviewed v2 bootstrap integrity without replacing sibling work

**Asked.** Continue the authorized household guard rollout under parent HLS task hh-dangerous-command-guard-parity; adopt Granny's stale onboarding safely, preserving recipe data and settings.

**Weighed.** PR38 at 3245a712 contains valuable leaf detection but an old signature serializer and secret verification. Canonical PR3308 merged as dc5d62f1 with the complete reviewed trio (reviewed source 35be2379). Partial copying would retain compatibility gaps. The existing required-hooks list also omitted the newly registered guards.

**Decided.** In an isolated branch based on PR38, adopt the canonical trio, eight isolated adoption tests and v2 transition document. Adopt Grandma's required-hook removal test from 6c8aec68 and protect the three registered guard basenames. Nine tests pass; privacy check and shell syntax pass. Recipe validation reports four missing-field errors in two existing records and 59 warnings across 194 recipes; git diff confirms recipe data, validator and settings are unchanged from the onboarding base. No recipe or memorial files are staged. This is source adoption pending independent leaf review, not deployment or HLS completion.

**Unsure.** Existing recipe errors require a separate evidence-backed repair, never invented ingredients. Later stack PRs39–41 still need reconciliation and retesting; the arming script's overbroad live-guard announcement is not repaired here. Runtime registrations and explicit stamp-root overrides still require rollout checks. HMAC remains local friction, disk union is not a lock, and required-hooks protects working-tree substrings rather than proving event matchers or staged-index integrity.

## 2026-09-03 — .household-root: the doctrine and runtime roots, discoverable by reading (open-claw-stuff #3098)

**Asked.** Household loop (patron yumi): make this repo able to say where Sophos is from here.

**Weighed.** Hooks fire unevenly across repos (this one registers few), so the discovery file exists precisely for the case where no hook runs — it is read, not executed. The generator writes layouts, never a machine path (UL-173/UL-337). Alternative of hand-writing the file: rejected, the generator is the SSOT and its output is what the household tests pin.

**Decided.** Generated `.household-root` with `admin/write-household-root-file.mjs`; verified it names both roots, instructs fail-loud on non-resolution, and carries no absolute machine path. Stacked on this repo's open hook branch.

**Unsure.** On this Mac the runtime clone is `~/ocs-work`, not `open-claw-stuff`, so the sibling/ancestor steps in the file do not find it by name here and a reader must say so — the standing naming mismatch (open-claw-stuff #2993), not something this file can fix.

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
