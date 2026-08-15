#!/usr/bin/env node
// A1 (UL-943) — usage-footer Stop gate. The Stop hook receives the transcript,
// so the agent's FINAL MESSAGE is mechanically inspectable: if the usage
// footer is absent, the stop is BLOCKED and the agent must emit it. The
// most-violated doctrine in this repo's recorded history (2026-08-08, a full
// session without footers) stops being silently forgettable.
//
// Livelock escape: Claude Code sets stop_hook_active=true when the agent is
// already continuing from a stop-block. One forced retry only — if the footer
// is STILL absent on the retry, fail OPEN and LOUD (a gate must never brick a
// session; a gate that gave up says so).
//
// Kill-switch (operator debugging only): FOOTER_GATE=0. Fail-open on any
// parse error, loudly.

import { readFileSync } from "node:fs";

function lastAssistantText(transcriptPath) {
  const lines = readFileSync(transcriptPath, "utf8").split("\n").filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i--) {
    let r;
    try { r = JSON.parse(lines[i]); } catch { continue; }
    if (r.type === "assistant" && r.message?.content) {
      const texts = r.message.content.filter((c) => c.type === "text").map((c) => c.text);
      if (texts.length) return texts.join("\n");
    }
  }
  return null;
}

export const FOOTER_RE = /\*Usage — this turn:/;

function main() {
  if (process.env.FOOTER_GATE === "0") return;
  let input;
  try { input = JSON.parse(readFileSync(0, "utf8")); }
  catch (e) { console.error(`[footer-gate] fail-open: unreadable hook input (${e.message})`); return; }
  let text;
  try { text = lastAssistantText(input.transcript_path); }
  catch (e) { console.error(`[footer-gate] fail-open: transcript unreadable (${e.message})`); return; }
  if (text == null) { console.error("[footer-gate] fail-open: no assistant text found"); return; }
  if (FOOTER_RE.test(text)) return;
  if (input.stop_hook_active) {
    console.error("[footer-gate] footer STILL absent after one forced retry — failing open LOUD rather than livelocking. The omission is on the record.");
    return;
  }
  console.log(JSON.stringify({
    decision: "block",
    reason: "Usage footer missing (operator directive 2026-08-07: EVERY reply, no exceptions). End the reply with the one-line footer: *Usage — this turn: ~X tok (out Y · in Z) · session: ~N tok effective · biggest cost: <what>*",
  }));
}

main();
