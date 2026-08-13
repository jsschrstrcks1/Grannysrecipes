#!/usr/bin/env node
// A.B.O.R.T. destructive-command guard — PreToolUse hook (Claude + Grok).
//
// Inspects live shell commands only (Bash / run_terminal_command). Blocks exit 2
// (+ Grok deny JSON) if the command matches a catastrophic, irreversible pattern.
// SSOT detector: cluster/lib/dangerous-command.mjs
//
// Referencing a dangerous string in a FILE (Write/Edit) is fine — this only
// inspects live shell tool calls. Subagents hit the same PreToolUse path.
//
// Sophos OS §5 destructive_execution — operational gate outside sophosGovern.
// HLS: destructive-command-hook-grok (dual-runtime extension of Claude belt).

import crypto from "node:crypto";
import {
  normalizeHookInput,
  appendEvent,
  getRuntime,
  getPatron,
} from "./bootstrap-lib.mjs";

// Read + parse the event FIRST, so a minimal inline check can still run even if
// the detector import fails.
let rawText = "";
try {
  for await (const chunk of process.stdin) rawText += chunk;
} catch {
  /* no stdin */
}

let command = "";
let normalized = null;
try {
  const evt = JSON.parse(rawText || "{}");
  normalized = normalizeHookInput(evt);
  // Only inspect shell tools. After normalize, Grok run_terminal_command → Bash.
  // Missing tool_name with a command still inspected (bias-to-block; Claude suite).
  if (normalized?.tool_name && normalized.tool_name !== "Bash") process.exit(0);
  command = String(normalized?.tool_input?.command || "");
} catch {
  process.exit(0); // unparseable → not our danger
}
if (!command.trim()) process.exit(0);

function deny(msg, meta = {}) {
  process.stderr.write(msg);
  // Best-effort ledger (never breaks the deny path).
  try {
    const sessionId = normalized?.session_id || "unknown";
    const cmdHash = crypto.createHash("sha256").update(command).digest("hex").slice(0, 16);
    appendEvent(
      {
        type: "destructive_command_denial",
        patron: getPatron(),
        session_id: sessionId,
        command_hash: cmdHash,
        rule_id: meta.rule_id || null,
        runtime: getRuntime(),
      },
      normalized?.raw || normalized,
    );
  } catch {
    /* ignore */
  }
  try {
    if (getRuntime() === "grok") {
      process.stdout.write(
        JSON.stringify({ decision: "deny", reason: msg.replace(/\n+$/, "") }) + "\n",
      );
    }
  } catch {
    /* ignore */
  }
  process.exit(2);
}

// Load the shared detector. On import failure DO NOT fail open — a guard-module
// bug must not become a universal false-pass for live shell tool calls.
//
// TWO candidates, and the second is load-bearing. `admin/onboard-loud-bootstrap.mjs` installs this
// guard into sibling repos and copies the detector alongside it as `.claude/hooks/lib/` — but those
// repos have no `cluster/` directory, so the SSOT path cannot resolve there. Until 2026-08-07 this
// file tried only `../../cluster/lib/`, which meant a freshly onboarded repo fell through to the
// six INLINE patterns below. Verified by simulating an onboard into a scratch dir: the guard printed
// "detector unavailable, allowing", exited 0, and ALLOWED wipe-class shapes while the copied detector
// sat unread beside it.
//
// Residual (guard-hook-fail-open-on-error): even with the dual-path load, if BOTH candidates fail
// the old path still allowed any command that did not match the thin INLINE list. That is still
// fail-open for the live agent shell. Default is now DENY (exit 2) when the detector cannot load.
// Operator escape only: DANGEROUS_COMMAND_GUARD_FAIL_OPEN=1 restores allow-if-no-inline-match
// (with a loud stderr warning). Test harness may set DANGEROUS_COMMAND_GUARD_FORCE_DETECTOR_FAIL=1.
const DETECTOR_CANDIDATES = [
  "../../cluster/lib/dangerous-command.mjs",   // canonical repo: the SSOT
  "./lib/dangerous-command.mjs",               // onboarded repo: the copy installed beside this hook
];
let scanCommand, explain;
try {
  if (process.env.DANGEROUS_COMMAND_GUARD_FORCE_DETECTOR_FAIL === "1") {
    throw new Error("forced detector load failure (test)");
  }
  let lastErr;
  for (const rel of DETECTOR_CANDIDATES) {
    try { ({ scanCommand, explain } = await import(new URL(rel, import.meta.url))); break; }
    catch (err) { lastErr = err; }
  }
  if (!scanCommand) throw lastErr;
} catch (e) {
  const INLINE = [
    /\brm\s+(?:-\S+\s+)*-[A-Za-z]*[rR][A-Za-z]*\s+(?:-\S+\s+)*(?:['"]?)(?:\/|~|\$\{?HOME\}?|\*)(?:['"\s/]|$)/i,
    /--no-preserve-root/i,
    /\bdd\b[^\n]*\bof=\/dev\/\w/i,
    /\bmkfs(?:\.\w+)?\b/i,
    /\w*\(\)\s*\{[^}]*\|[^}]*&[^}]*\}\s*;/,
    /\b(?:curl|wget|fetch)\b[^\n|]*\|\s*(?:sudo\s+)?(?:sh|bash|zsh|dash|python3?|perl|ruby|node)\b/i,
  ];
  if (INLINE.some((re) => re.test(command))) {
    deny(
      `⛔ dangerous-command-guard: detector unavailable AND the command matches a catastrophic inline pattern — BLOCKED (fail-closed). ${e?.message || e}\n`,
    );
  }
  // Default: fail CLOSED on live shell when the detector cannot load.
  // Escape is operator-only (or intentional test of the old residual path).
  if (process.env.DANGEROUS_COMMAND_GUARD_FAIL_OPEN === "1") {
    process.stderr.write(
      `⚠ dangerous-command-guard: detector unavailable, FAIL_OPEN=1 allowing (no inline catastrophic match) — ${e?.message || e}\n`,
    );
    process.exit(0);
  }
  deny(
    `⛔ dangerous-command-guard: detector unavailable — BLOCKED (fail-closed). ` +
      `Fix the detector import path, or set DANGEROUS_COMMAND_GUARD_FAIL_OPEN=1 only if you mean to allow. ` +
      `${e?.message || e}\n`,
  );
}

let result;
try {
  result = scanCommand(command);
} catch (error) {
  deny(
    `⛔ dangerous-command-guard: detector runtime error — BLOCKED (fail-closed). ` +
      `${error?.name || "Error"}: ${String(error?.message || error).slice(0, 200)}\n`,
    { rule_id: "detector-runtime-error" },
  );
}
if (result.blocked) {
  const body = "⛔ A.B.O.R.T. destructive-command guard\n" + explain(result) + "\n";
  deny(body, { rule_id: result.matched?.[0]?.id || null });
}
process.exit(0);
