# Bootstrap stamp integrity transition

Soli Deo Gloria.

The corrected seal includes nested read evidence. Legacy seals omitted those fields and cannot prove the read sequence; they are intentionally not migrated or accepted.

Default stamp storage moves from `household-bootstrap/household` to `household-bootstrap/household-v2` under the existing runtime home. This separates old writers during rolling deployment. Existing files and secrets remain untouched. An updated session earns a new stamp by completing the ordinary observed reads and memory recall. Possession of the new secret still permits forgery: this is local friction and evidence, not a hardware trust boundary.

Deploy the complete bootstrap trio together (library, guard, stamp writer). Reconcile the canonical hook source first, then distribute identical copies to leaf repositories and verify each installed settings registration. A legacy hook left active retains its old weaknesses; the new store does not repair it remotely.

`HOUSEHOLD_BOOTSTRAP_ROOT` remains an explicit operator override. If configured, select a dedicated v2 location for all updated readers and writers; do not share that override location with legacy writers. Do not delete old state or disable a guard to complete the transition.

Acceptance: unstamped leaf writes deny, observed reads enable the session, missing-secret verification creates no secret, altered nested evidence fails verification, invalid disk stamps cannot contribute reads, and valid previously recorded layers survive the disk merge. Re-run the hook suite and the installed-leaf probes before declaring rollout complete.
