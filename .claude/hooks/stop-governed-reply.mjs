#!/usr/bin/env node
// A2 (UL-943) — governed-reply Stop gate: sophosGovern over the agent's own
// final message. The kernel finally governs the agent's prose, not only the
// pipeline's. BLOCK-grade findings block the stop and hand the findings back —
// the agent revises, or carries the finding into the text with its evidence.
// Warn-grade findings print loud but do not block (the A-6 medium-band
// philosophy applied to the agent).
//
// The query is the last USER message (so query-dependent policies engage);
// the reply is judged flat (no SOPHOS_AMPLIFY forced) with a self-report
// verdict — this gate is about the kernel's block-grade floor (fabricated
// quantities, contradictions), not the perception layer.
//
// HONEST LIMITS, stated where they bind: (1) the kernel's 35 policies have
// jurisdiction gaps — a pass here is NOT proof a reply was fully vetted, and
// citing it as such would be the false-CALM; (2) false blocks are possible
// (an unsourced-but-true duration in prose); the cost is one forced revision
// where the agent states its evidence or rephrases — then the stop_hook_active
// escape fails open LOUD. One retry, never a livelock.
//
// Kill-switch (operator debugging only): REPLY_GOVERN=0.

import { readFileSync, existsSync } from "node:fs";
import { pathToFileURL, fileURLToPath } from "node:url";
import { join, resolve, dirname } from "node:path";

// UL-964: resolve the household root REGARDLESS of session root, so a
// user-level (multi-root) registration still reaches the kernel. Order:
// operator override → project dir if it holds the kernel → this hook file's
// own repo (root/.claude/hooks/<this>). Null → fail open LOUD as ungoverned.
function householdRoot() {
  const hookRepo = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
  const pd = process.env.CLAUDE_PROJECT_DIR;
  // Sibling layouts included (fleet rollout: this file is SYNCED into every
  // household repo; from a recipe repo the kernel lives in ../open-claw-stuff).
  const candidates = [
    process.env.HOUSEHOLD_OCS_ROOT,
    pd,
    pd && join(pd, "open-claw-stuff"),
    pd && resolve(pd, "..", "open-claw-stuff"),
    hookRepo,
    resolve(hookRepo, "..", "open-claw-stuff"),
  ].filter(Boolean);
  for (const c of candidates) {
    try { if (existsSync(join(c, "atlas", "server", "sophos.mjs"))) return c; } catch { /* next */ }
  }
  return null;
}

function lastMessages(transcriptPath) {
  const lines = readFileSync(transcriptPath, "utf8").split("\n").filter(Boolean);
  let assistant = null, user = null;
  for (let i = lines.length - 1; i >= 0; i--) {
    let r;
    try { r = JSON.parse(lines[i]); } catch { continue; }
    if (!assistant && r.type === "assistant" && r.message?.content) {
      const t = r.message.content.filter((c) => c.type === "text").map((c) => c.text).join("\n");
      if (t) assistant = t;
    } else if (assistant && !user && r.type === "user" && r.message?.content) {
      const parts = Array.isArray(r.message.content) ? r.message.content : [{ type: "text", text: String(r.message.content) }];
      const t = parts.filter((c) => c.type === "text").map((c) => c.text).join("\n");
      if (t) { user = t; break; }
    }
  }
  return { assistant, user };
}

async function main() {
  if (process.env.REPLY_GOVERN === "0") return;
  let input;
  try { input = JSON.parse(readFileSync(0, "utf8")); }
  catch (e) { console.error(`[reply-govern] fail-open: unreadable hook input (${e.message})`); return; }

  let msgs;
  try { msgs = lastMessages(input.transcript_path); }
  catch (e) { console.error(`[reply-govern] fail-open: transcript unreadable (${e.message})`); return; }
  if (!msgs.assistant) { console.error("[reply-govern] fail-open: no assistant text"); return; }

  let sophosGovern;
  try {
    const root = householdRoot();
    if (!root) { console.error("[reply-govern] fail-open: no candidate root holds the kernel (HOUSEHOLD_OCS_ROOT, CLAUDE_PROJECT_DIR, hook location) — an UNGOVERNED stop is reported, not hidden"); return; }
    ({ sophosGovern } = await import(pathToFileURL(join(root, "atlas", "server", "sophos.mjs")).href));
  } catch (e) { console.error(`[reply-govern] fail-open: kernel unloadable (${e.message}) — an ungoverned stop is reported, not hidden`); return; }

  let g;
  try {
    g = sophosGovern(
      { passed: true, confidence: "high", notes: "agent self-report" },
      msgs.assistant, [], msgs.user || "", null, {},
    );
  } catch (e) { console.error(`[reply-govern] fail-open: kernel threw (${e.message})`); return; }

  const blocks = (g.findings || []).filter((f) => f.severity === "block");
  const warns = (g.findings || []).filter((f) => f.severity === "warn");
  if (warns.length) {
    console.error(`[reply-govern] advisory (non-blocking): ${warns.map((f) => f.policy).join(", ")}`);
  }
  if (!blocks.length) return;
  if (input.stop_hook_active) {
    console.error(`[reply-govern] block-grade findings persist after one forced retry (${blocks.map((f) => f.policy).join(", ")}) — failing open LOUD; the findings are on the record for the operator.`);
    return;
  }
  console.log(JSON.stringify({
    decision: "block",
    reason: `Sophos kernel BLOCK on your reply: ${blocks.map((f) => `[${f.policy}] ${f.detail}`).join("; ")}. Revise the claim, attach its evidence in the text, or state the uncertainty explicitly.`,
  }));
}

main();
