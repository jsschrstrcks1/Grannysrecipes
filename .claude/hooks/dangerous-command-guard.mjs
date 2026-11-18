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
// The stdin read is the guard's OWN trust boundary: until it finishes there is no command to
// inspect, so an unbounded read is an unbounded window in which the guard has decided NOTHING.
// Measured 2026-08-18 with inert `echo PROBE` payloads: stdin opened and never closed => this
// hook never returned a verdict, and two ORPHANED copies (PPID=1) spun at ~100% CPU for 19
// minutes. Bound it, and fail CLOSED on the bound — the same posture the detector-load path
// below already takes, for the same stated reason: a false block is an annoyance, a false pass
// is irreversible. The in-process bound is deliberately SHORTER than the `timeout` on this
// hook's `.claude/settings.json` entry, so THIS code decides rather than the harness's
// hook-timeout semantics, which are not specified to fail closed.
//
// `Number(x) || fallback` is deliberately NOT used: it maps a legitimate "0" to the fallback,
// which is exactly how a tuning knob silently loses its zero (UL-895).
function envInt(name, fallback) {
  const raw = process.env[name];
  if (raw === undefined || raw === "") return fallback;
  const n = Number(raw);
  return Number.isFinite(n) && n >= 0 ? n : fallback;
}
const STDIN_MS = envInt("DANGEROUS_COMMAND_GUARD_STDIN_MS", 5000);
const STDIN_MAX_BYTES = envInt("DANGEROUS_COMMAND_GUARD_STDIN_MAX_BYTES", 1024 * 1024);

function denyUninspectable(why) {
  process.stderr.write(
    `\u26d4 A.B.O.R.T. destructive-command guard\n` +
      `BLOCKED (fail-closed): the guard could not read the tool call to inspect it — ${why}. ` +
      `A command this guard has not read is a command it has not cleared.\n`,
  );
  try {
    if (getRuntime() === "grok") {
      process.stdout.write(
        JSON.stringify({ decision: "deny", reason: `guard could not read stdin: ${why}` }) + "\n",
      );
    }
  } catch {
    /* ignore */
  }
  try {
    appendEvent({
      type: "destructive_command_denial",
      patron: getPatron(),
      session_id: "unknown",
      command_hash: null,
      rule_id: "stdin-uninspectable",
      runtime: getRuntime(),
    });
  } catch {
    /* best effort — never breaks the deny path */
  }
  process.exit(2);
}

let rawText = "";
try {
  rawText = await new Promise((resolve, reject) => {
    let buf = "";
    let settled = false;
    const done = (fn, arg) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      fn(arg);
    };
    const timer = setTimeout(
      () => done(reject, new Error(`stdin did not close within ${STDIN_MS}ms`)),
      STDIN_MS,
    );
    // Never hold the process open on the timer alone.
    if (typeof timer.unref === "function") timer.unref();
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      buf += chunk;
      if (Buffer.byteLength(buf, "utf8") > STDIN_MAX_BYTES) {
        done(reject, new Error(`stdin exceeded ${STDIN_MAX_BYTES} bytes`));
      }
    });
    process.stdin.on("end", () => done(resolve, buf));
    // An stdin ERROR keeps the pre-existing "no stdin" behaviour (empty -> exit 0 downstream):
    // a hook invoked with no readable stdin is not gating a shell call. NAMED RESIDUAL, not
    // silently absorbed — closing it is a separate scope decision, not this change.
    process.stdin.on("error", () => done(resolve, ""));
  });
} catch (err) {
  denyUninspectable(err?.message || String(err));
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
