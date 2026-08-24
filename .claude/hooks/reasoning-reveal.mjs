#!/usr/bin/env node
// reasoning-reveal.mjs — make the WHY of a consequential action visible while
// it happens, and auditable afterwards.
//
// WHY THIS EXISTS. The household already proves a great deal about actions:
// the Sophos publish gate proves tests were run, the bootstrap guard proves the
// posture was read, the dangerous-command guard proves the shape was safe. All
// of them govern WHAT is done. None of them records WHY, so the reasoning
// behind an action survives only in a transcript nobody re-reads — and a
// transcript is testimony, not evidence.
//
// This session produced the concrete case. A guard was reported as broken on a
// probe that called a method which did not exist; the probe returned null and
// null was read as "not tripped". The action (file a P1) looked identical from
// the outside to a well-grounded one. What distinguished them was the reasoning,
// and the reasoning was the one thing nothing captured.
//
// WHAT IT DOES, AND WHAT IT CANNOT DO. A hook sees the tool call, never the
// model's internal reasoning — so this cannot "extract" a thought. What it can
// do is hold every consequential action to a stated, checkable rationale and
// make a missing one LOUD instead of invisible:
//
//   - REVEAL   : print a one-line trace to stderr as the action happens, so the
//                operator sees the intent at the moment it matters.
//   - RECORD   : append it to a per-session JSONL trail that can be audited
//                beside the Sophos ledger.
//   - FLAG     : mark actions whose rationale is absent or vacuous, reusing the
//                citation rule already calibrated against 851 real ledger
//                artifacts in admin/verify-substance.mjs — a rationale must
//                point at something a reader could check and find false.
//
// It is OBSERVE-ONLY. It never denies. A reasoning recorder that can block
// becomes a second gate with none of a gate's review, and an agent blocked by
// its own narration would learn to narrate for the blocker rather than for the
// reader. Denial belongs to the guards that were designed for it.
//
// Fail-open, loudly (household precedent: bootstrap-guard, dangerous-command-guard):
// a bug in an observer must never brick a session.
//
// Soli Deo Gloria.

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const TRAIL_DIR = process.env.REASONING_TRAIL_DIR
  || path.join(os.homedir(), ".claude", "reasoning-trail");

// Consequential = it changes something outside the session. Reads are not
// traced: tracing everything is the same as tracing nothing, and the noise is
// what makes an operator stop reading.
const MUTATING_TOOLS = new Set(["Edit", "Write", "NotebookEdit"]);
const MUTATING_BASH = new RegExp(
  [
    String.raw`\bgit\b[^|&;]*?\b(commit|push|merge|rebase|reset|revert)\b`,
    String.raw`(^|[;&|]\s*)(rm|mv|cp)\s`,
    String.raw`\bsed\s+-i\b`,
    String.raw`\b(gh)\s+(pr|issue|release)\s+(create|merge|close|edit|comment)\b`,
    String.raw`library\.mjs['"]?\s+(register|checkout|release|complete|verify|reassign)\b`,
    String.raw`>\s*[^|&;\s]`, // redirection into a file
  ].join("|"),
);

/**
 * Does this rationale point at anything a reader could check and find false?
 *
 * Deliberately the SAME rule as admin/verify-substance.mjs rather than a second
 * opinion about what counts as evidence — one household definition, calibrated
 * once. Ordinals are stripped first so "2nd pass" cannot pose as a citation.
 */
const POSITIONAL = [/\b\d+\s*(?:st|nd|rd|th)\b/gi, /\b(?:round|pass|attempt|step)\s*#?\s*\d+\b/gi];
const CITATION = /\d|[\w-]+\/[\w./-]+|\b[\w-]+\.[\w-]{2,}\b|\b[a-z]+[A-Z][a-zA-Z]*\b|\b[a-z]+_[a-z_]+\b/;

export function citesSomething(text) {
  let s = String(text ?? "");
  for (const re of POSITIONAL) s = s.replace(re, " ");
  return CITATION.test(s);
}

/** The rationale a runtime may attach to a call. Absent is the common case. */
export function statedReason(input) {
  const ti = input?.tool_input ?? input?.toolInput ?? {};
  for (const k of ["reasoning", "reason", "why", "rationale", "description", "intent"]) {
    const v = ti[k] ?? input?.[k];
    if (typeof v === "string" && v.trim()) return { text: v.trim(), field: k };
  }
  return null;
}

export function isConsequential(toolName, command) {
  if (MUTATING_TOOLS.has(toolName)) return true;
  if (toolName === "Bash") return MUTATING_BASH.test(String(command || ""));
  return false;
}

/** One line an operator can actually read at a glance. */
export function revealLine({ tool, target, reason, grade }) {
  const mark = grade === "cited" ? "▸" : grade === "thin" ? "▪" : "▫";
  const what = target ? `${tool}: ${String(target).slice(0, 68)}` : tool;
  const why = reason ? String(reason).replace(/\s+/g, " ").slice(0, 120) : "(no stated reason)";
  return `${mark} why ${what}\n    ${why}`;
}

export function gradeReason(reason) {
  if (!reason) return "unstated";
  return citesSomething(reason.text) ? "cited" : "thin";
}

function main() {
  const raw = JSON.parse(fs.readFileSync(0, "utf8"));
  const tool = String(raw.tool_name ?? raw.toolName ?? "");
  const ti = raw.tool_input ?? raw.toolInput ?? {};
  const command = ti.command ?? ti.cmd ?? "";
  const target = ti.file_path ?? ti.notebook_path ?? ti.path ?? command ?? "";

  if (!isConsequential(tool, command)) return 0;

  const reason = statedReason(raw);
  const grade = gradeReason(reason);

  // REVEAL — stderr so it rides alongside the action, not buried in a file.
  process.stderr.write(revealLine({ tool, target, reason: reason?.text, grade }) + "\n");

  // RECORD — one JSONL line per consequential action, per session.
  const session = String(raw.session_id ?? raw.sessionId ?? "unknown").replace(/[^\w-]/g, "");
  fs.mkdirSync(TRAIL_DIR, { recursive: true });
  fs.appendFileSync(
    path.join(TRAIL_DIR, `${session}.jsonl`),
    JSON.stringify({
      at: new Date().toISOString(),
      session_id: session,
      tool,
      target: String(target).slice(0, 300),
      reason: reason ? reason.text.slice(0, 1000) : null,
      reason_field: reason?.field ?? null,
      grade, // cited | thin | unstated
      cwd: raw.cwd ?? null,
    }) + "\n",
  );
  return 0;
}

/**
 * Only read stdin when actually RUN as the hook. Without this the module blocks
 * on fs.readFileSync(0) the moment anything imports it — which is exactly what
 * happened the first time its own test file imported it.
 *
 * Compare canonical paths, not URL spellings: macOS aliases /tmp to /private/tmp
 * and hooks are commonly invoked through symlinked or aliased paths, where a
 * string compare silently reports "not main" and the hook does nothing at all.
 * (Same failure already cost this household a monitor that exited 0 printing
 * nothing — a hook that never runs looks identical to a quiet one.)
 */
function isMainModule() {
  if (!process.argv[1]) return false;
  try {
    return fs.realpathSync(fileURLToPath(import.meta.url)) === fs.realpathSync(process.argv[1]);
  } catch {
    return false;
  }
}

if (isMainModule()) {
  try {
    process.exit(main());
  } catch (e) {
    // Loud, but never blocking — see header.
    process.stderr.write(`reasoning-reveal: internal error, continuing (observe-only): ${e?.message || e}\n`);
    process.exit(0);
  }
}
