// bootstrap-stamp-hook.mjs — PostToolUse (Read|Bash): machine evidence of bootstrap (R1).
// Dual-runtime: Claude Code + Grok. Model never writes stamps.
// Spec: docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md
// HLS: loud-bootstrap-impl-claude-code · loud-bootstrap-impl-grok
import {
  RECALL_CMD_RE,
  newStamp,
  saveStamp,
  verifyStamp,
  missingLayers,
  mergeLayersFromDisk,
  appendEvent,
  readStdinJson,
  normalizeHookInput,
  resolveSessionId,
  ALL_LAYERS,
  layerFromFilePath,
  isHouseholdRepo,
  getRepoRoot,
} from "./bootstrap-lib.mjs";

try {
  const raw = readStdinJson();
  const input = normalizeHookInput(raw);
  if (!input) process.exit(0);

  const repoRoot = getRepoRoot(input.raw || input);
  if (!isHouseholdRepo(repoRoot)) process.exit(0);

  const sessionId = resolveSessionId(input);   // SSOT — must match the guard exactly
  const tool = input.tool_name || "";
  const now = new Date().toISOString();

  let layerHit = null;
  if (tool === "Read") {
    layerHit = layerFromFilePath(input.tool_input?.file_path || "");
  } else if (tool === "Bash") {
    if (RECALL_CMD_RE.test(String(input.tool_input?.command || ""))) {
      layerHit = "memory-recall";
    }
  }
  if (!layerHit) process.exit(0);

  let stamp = verifyStamp(sessionId, input.raw || input);
  if (stamp === null || stamp === "forged") {
    stamp = newStamp(sessionId, input.raw || input);
  }
  if (!stamp.layers_read[layerHit]) stamp.layers_read[layerHit] = now;

  // UL-078: union with whatever a concurrent Read wrote since we loaded, so a parallel Read is not
  // clobbered and the bootstrap event is not double-appended.
  stamp = mergeLayersFromDisk(stamp, input.raw || input);

  const missing = missingLayers(stamp);
  if (missing.length === 0 && !stamp.ledgered) {
    stamp.ledgered = appendEvent(
      {
        type: "bootstrap",
        patron: stamp.patron,
        session_id: sessionId,
        layers_read: ALL_LAYERS.length,
        layers_total: ALL_LAYERS.length,
        enforcement: "guard",
      },
      input.raw || input,
    );
  }
  saveStamp(stamp, input.raw || input);
} catch (e) {
  console.error(
    `bootstrap-stamp-hook: internal error (observation lost this call): ${e?.message || e}`,
  );
}
process.exit(0);
