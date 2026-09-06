// bootstrap-guard.mjs — PreToolUse: loud half of household bootstrap (R2).
// Denies repo mutations when the session lacks a complete, HMAC-valid stamp.
// Dual-runtime: Claude Code + Grok (via normalizeHookInput).
// Escape hatch: HOUSEHOLD_BOOTSTRAP_GUARD_BLOCK=0 → warn-only.
// Spec: docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md
// HLS: loud-bootstrap-impl-claude-code · loud-bootstrap-impl-grok
import fs from "node:fs";
import path from "node:path";
import {
  getRepoRoot,
  isHouseholdRepo,
  verifyStamp,
  loadStamp,
  newStamp,
  saveStamp,
  missingLayers,
  appendEvent,
  readStdinJson,
  normalizeHookInput,
  sessionIdValid,
  resolveSessionId,
  getRuntime,
} from "./bootstrap-lib.mjs";

const MUTATING_BASH_RE = new RegExp(
  [
    String.raw`\bgit\b[^|&;]*?\b(commit|push|merge|rebase|reset)\b`,
    String.raw`(^|[;&|]\s*)rm\s`,
    String.raw`(^|[;&|]\s*)mv\s`,
    String.raw`\bsed\s+-i\b`,
    String.raw`library\.mjs['"]?\s+(register|checkout|release|complete|verify|reassign)\b`,
  ].join("|"),
);

function realOr(p) {
  const resolved = path.resolve(p);
  let ancestor = resolved;
  const suffix = [];
  for (;;) {
    try { return path.join(fs.realpathSync(ancestor), ...suffix); }
    catch (error) {
      if (error.code !== "ENOENT" && error.code !== "ENOTDIR") return resolved;
      const parent = path.dirname(ancestor);
      if (parent === ancestor) return resolved;
      suffix.unshift(path.basename(ancestor));
      ancestor = parent;
    }
  }
}

// Is `fp` inside `root`? Literal prefix first; then by REAL identity. #3077 landed this on
// its own probe: a repo reached through a symlinked prefix (macOS /var → /private/var,
// /tmp → /private/tmp) has its guard's module path resolved by Node to the REAL location,
// so the fallback repo root is the realpath while the tool input carries the alias — the
// literal comparison then reads an in-repo edit as out-of-repo and ALLOWS it. Same rule
// hls-claim-guard.mjs already applies (self-attack 2026-07-28). A not-yet-existing Write
// target resolves its nearest existing ancestor, preserving the missing suffix.
function insideRepo(fp, root) {
  const a = path.resolve(fp);
  const r = path.resolve(root);
  if (a.startsWith(r + path.sep)) return true;
  const ra = realOr(a);
  const rr = realOr(r);
  return ra === rr || ra.startsWith(rr + path.sep);
}

function isRepoMutation(input, repoRoot) {
  const tool = input.tool_name || "";
  if (tool === "Edit" || tool === "Write" || tool === "NotebookEdit") {
    const fp = String(input.tool_input?.file_path || input.tool_input?.notebook_path || "");
    if (!fp || !repoRoot) return false;
    return insideRepo(fp, repoRoot);
  }
  if (tool === "Bash") {
    return MUTATING_BASH_RE.test(String(input.tool_input?.command || ""));
  }
  return false;
}

function deny(blocking, msg) {
  console.error(msg);
  // Grok: JSON decision; Claude: exit 2. Both runtimes honor exit 2 on PreToolUse.
  if (blocking) {
    try {
      process.stdout.write(JSON.stringify({ decision: "deny", reason: msg }) + "\n");
    } catch {
      /* ignore */
    }
    process.exit(2);
  }
  process.exit(0);
}

try {
  const raw = readStdinJson();
  const input = normalizeHookInput(raw);
  if (!input) process.exit(0);

  const repoRoot = getRepoRoot(input.raw || input);
  // Outside household repos: no belt (Grok may be in ~/ unrelated work).
  if (!isHouseholdRepo(repoRoot)) process.exit(0);

  if (!isRepoMutation(input, repoRoot)) process.exit(0);

  const idValid = sessionIdValid(input.session_id);
  const sessionId = resolveSessionId(input);   // SSOT — must match the stamp writer exactly
  const stamp = verifyStamp(sessionId, input.raw || input);
  const missing = missingLayers(stamp);

  if (idValid && stamp && stamp !== "forged" && missing.length === 0) {
    // Bootstrapped — allow (Grok optional explicit allow).
    if (getRuntime() === "grok") {
      try {
        process.stdout.write(JSON.stringify({ decision: "allow" }) + "\n");
      } catch {
        /* ignore */
      }
    }
    process.exit(0);
  }

  const blocking = process.env.HOUSEHOLD_BOOTSTRAP_GUARD_BLOCK !== "0";
  const forged = stamp === "forged";
  const toolDesc =
    input.tool_name === "Bash"
      ? `Bash: ${String(input.tool_input?.command || "").slice(0, 120)}`
      : `${input.tool_name}: ${input.tool_input?.file_path || ""}`;

  // The verdict is already settled above: this is a guarded mutation whose stamp
  // was not affirmatively verified, so it WILL be denied. Everything from here to
  // saveStamp is BOOKKEEPING, and bookkeeping must never be able to turn that
  // denial into permission. Without this boundary an I/O failure here escapes to
  // the outer catch, which exits 0 (allow) — and because stampRoot() lives outside
  // repoRoot while isRepoMutation() only guards Write/Edit paths INSIDE repoRoot,
  // the guard's own state is unguarded, so a single `chmod` on the stamp dir
  // disarmed the guard for the rest of the session (measured DENIED -> ALLOWED,
  // persisting across further Writes and a `git commit`).
  // A failure to RECORD a denial is not consent to proceed.
  // HLS p1-guard-found-validating-p0-read-order-enforcement… / open-claw-stuff#2727;
  // same class as guard-hook-fail-open-on-error and hls-p0-the-c5-guard-fails-open.
  let ledgered = null; // null = not attempted (cap reached); false = skipped/failed; true = written
  try {
    let counter = loadStamp(sessionId, input.raw || input);
    if (!counter || typeof counter !== "object") {
      counter = newStamp(sessionId, input.raw || input);
    }
    if (forged) {
      counter = newStamp(sessionId, input.raw || input);
      counter.forge_detected = true;
    }
    counter.denials = (counter.denials || 0) + 1;
    if (counter.denials <= 3) {
      ledgered = appendEvent(
        {
          type: "bootstrap_guard_denial",
          patron: counter.patron,
          session_id: sessionId,
          denied_tool: input.tool_name,
          missing_layers: missing,
          forged,
          blocked: blocking,
          sessionid_invalid: !idValid,
        },
        input.raw || input,
      );
    }
    saveStamp(counter, input.raw || input);
  } catch (bookkeepingError) {
    // Loud, but never fatal to the verdict — fall through to deny().
    console.error(
      `bootstrap-guard: denial bookkeeping failed (${bookkeepingError?.message || bookkeepingError}) — denying anyway. A failure to record a denial must never become permission to proceed.`,
    );
  }

  const pointer = getRuntime() === "grok" ? "GROK.md" : "CLAUDE.md";
  const msg = [
    forged
      ? "BOOTSTRAP GUARD: stamp failed HMAC verification — a hand-written stamp is testimony, not evidence (spec R1/R5). Forgery is itself a governance finding."
      : !idValid
        ? "BOOTSTRAP GUARD: this session has no stable session_id, so its bootstrap cannot be attributed — a shared `unknown` stamp would let any un-read session inherit another's reads. Refusing (loud-bootstrap-sessionid-contract). The runtime must supply session_id, or use the escape hatch."
        : `BOOTSTRAP GUARD: this session has not completed the Layer 0/1 read order (missing: ${missing.join(", ")}).`,
    `Denied: ${toolDesc}`,
    // #3077: a leaf repo (Project-Sophos, the recipe repos) carries the guard but no library, so
    // there is no ledger to append to — say so rather than let a missing row read as "no denial".
    ...(ledgered === false
      ? [`Denial NOT ledgered: the ledger for ${repoRoot} is absent or could not be written — this message is the record.`]
      : []),
    `Read the layers in ${pointer} §Read order (front door skills/sophos first); the stamp hook records reads automatically.`,
    "Operator escape hatch: HOUSEHOLD_BOOTSTRAP_GUARD_BLOCK=0 (warn-only). Spec: docs/HOUSEHOLD-LOUD-BOOTSTRAP-REQUIREMENT.md",
  ].join("\n");

  deny(blocking, msg);
} catch (e) {
  console.error(
    `bootstrap-guard: internal error, failing OPEN (named limit — guard bugs must not brick sessions): ${e?.message || e}`,
  );
  process.exit(0);
}
