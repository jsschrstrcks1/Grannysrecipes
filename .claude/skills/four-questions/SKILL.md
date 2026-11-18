---
name: four-questions
description: >-
  After Ken finishes a piece of his own work (a sermon draft, a flock record, a cruise page, a recipe,
  a family-history entry, an email, any task he did or asked for in chat), ask the four never-one-off
  questions in four short lines: what did we learn, what would make it better next time, is this a
  repeatable skill, can it be automated. Use when Ken says "four questions", "never one-off", "what did
  we learn", "close it out", or finishes a task and asks what's next. Light: no custody, no gates, no
  forms. Saving the answers is offered, never forced.
version: 1.1.0
license: LicenseRef-Proprietary
category: habit
keywords:
  - four questions
  - never one-off
  - lessons learned
  - close out
  - skill
  - automate
activation: on-request
runtimes:
  - claude-code
  - claude-ai
related_skills:
  - careful-not-clever
  - memory-recall
allowed-tools: []
---

# Four questions: never do one-off work

*Soli Deo Gloria.* "Whatsoever ye do, do it heartily, as to the Lord" (Colossians 3:23). Work done once
and forgotten has to be done again from nothing. Four short questions after a task keep what it taught.

This is for Ken's own work, the things he does in a day. The same four questions bind agent work as
an invariant (Sophos OS Phase 5b, `Project-Sophos/docs/SOPHOS-OPERATING-SYSTEM.md`), answered through
Tekton's release close-out (`Project-Sophos/docs/TEKTON.md` §Close-out) with custody and gates. This
skill has none of that. It is a habit, not a gate. In household repos a prompt hook
(`four-questions-nudge`) points here when Ken asks in his own words.

## When

When Ken finishes something and asks, or says "four questions", "never one-off", "what did we learn" or
"close it out". Do not ask after every message. Do not ask after small talk. One time per finished task.

## What to do

Answer all four yourself first, from what just happened, in one line each. Then ask Ken to correct or
add. Never make him fill in a blank form.

1. **Learn.** What did we learn? One concrete thing. "The recipe card says 350, not 375" beats
   "attention to detail matters."
2. **Improve.** What would make it better next time? A change someone could actually make.
3. **Skill.** Is this a repeatable skill? If this kind of task has come up before, name the steps that
   repeat. If it is a one-time thing, say "one-time" and why.
4. **Agent.** How would I automate this or turn it into an agent? Name the part a script or a scheduled
   task could do, and the part that needs Ken's judgment and should stay his. Pastoral judgment, voice,
   and anything about a real person stay human.

Keep it to the four lines and one question back. If a line is "nothing", say so plainly. Do not make up
a lesson to fill the slot.

## Saving (offer, never force)

Ask once: "Want me to keep any of these?" Then, only for what he says yes to:

- In a household repo session: a lesson goes to memory
  (`python3 <ken>/orchestrator/memory_ops.py encode <domain> insight "<text>"`), and an improvement goes in
  as an upgrade-ledger candidate (`node <Project-Sophos>/admin/tekton.mjs intake --candidate '<json>'`).
  Say which command ran and what it returned.
- Anywhere else (the Claude app with no repo): give him the four lines as a short note he can paste
  where he keeps them. Do not claim anything was saved when nothing was.

A "skill" or "agent" answer that names real repeated work is worth saying out loud: "this is the third
recipe card we've cleaned up this way; it could be a skill." Then let Ken decide.

## What this is not

- Not a gate. Nothing is refused if Ken skips it.
- Not a sermon outline, a report, or a form.
- Not a replacement for Tekton close-outs on agent work.

*Soli Deo Gloria.*
