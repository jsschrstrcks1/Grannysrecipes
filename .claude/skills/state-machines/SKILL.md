---
name: state-machines
description: >-
  Every time code is written or changed, find the implicit state machines in the code being touched
  (boolean flag soup, status strings compared in many places, transitions scattered across handlers,
  "can't happen" combinations nothing forbids) and make the one change that lifts all three of user
  experience (UX), developer experience (DX) and agent experience (AX) without breaking anything. Use on
  every coding task in every household repo, and when Ken asks to "find the implicit state machines",
  "audit the state machines", or to "elevate UX, DX and AX". On an ordinary task it reads only the code
  being changed; the whole-app audit runs only when asked for by name.
version: 1.0.0
license: LicenseRef-Proprietary
category: integrity
keywords:
  - state machine
  - implicit state
  - flag soup
  - status string
  - UX
  - DX
  - AX
  - agent experience
activation: automatic
runtimes:
  - hermes
  - claude-code
  - grok
  - codex
related_skills:
  - careful-not-clever
  - sophos
  - four-questions
allowed-tools: [Read, Grep, Edit, Bash]
---

<!--
  Soli Deo Gloria. "Let all things be done decently and in order." 1 Corinthians 14:40
-->

# State machines: every time we code

**Ken, 2026-11-19:** turn this question into a skill, part of Sophos, called upon every time we code:
*"Find all of the implicit state machines in my app. Make the best decision that will elevate all three:
the user experience (UX), developer experience (DX), and agent experience (AX) always, without breaking
anything."* Scope, his ruling the same day: on an ordinary task, the code being touched; the whole app only
when asked.

## Why

Most bugs this household has paid for were a state nobody named. A chip that read green while its feed was
dead. A stamp that counted "fail" as a pass. A merge that sat half-finished for two weeks because no state
said "stuck". Each was a state machine hiding in booleans and strings, with a combination nothing forbade.
Name the states and the transitions, and the impossible combination becomes impossible.

## On every coding task (the touched-code check)

Before you edit, read the code you are about to change and ask four things:

1. **Is there a state machine here?** Look for: two or more booleans that together mean one thing
   (`loading` + `error` + `done`); a status string compared in more than one place; a value set in one
   handler and checked in another; a comment like "should never happen"; a retry or timeout with no named
   end; three outcomes squeezed into two (pass or fail, with "could not look" reported as pass).
2. **What are its states, and which combinations are impossible?** Write them down, even if only in your
   head. If you cannot list them, that is the finding.
3. **What is the one change that lifts all three?**
   - **UX:** the person using it always sees a true state: never green for unknown, never silence for
     failure, never a spinner with no end.
   - **DX:** the next developer reads the states in one place, with the transitions next to them, and a
     test pins each one.
   - **AX:** an agent can read the state as data (a named value, an exit code, a JSON field), not infer it
     from prose, and a refusal names its code and its remedy.
   Prefer the smallest change that does all three: one named-state value or enum in place of the booleans,
   one transition function in place of scattered assignments, a third state (UNAVAILABLE, UNKNOWN) where two
   were hiding one.
4. **Does it break anything?** Keep the public shape (exports, exit codes, JSON fields, file formats) unless
   the task is to change it. Add or keep a test for each state, including the negative. Run the tests before
   and after. When a better design would change a public shape, say so and leave it for the operator.

If the code you are touching has no state machine, say so in one line and carry on. Do not invent one, and
do not widen the change past the task.

## The whole-app audit (only when asked)

When Ken asks to "find all of the implicit state machines" in a repo or the household, run the full
version: sweep the repo, list every machine with file and line, rank by harm to UX, DX and AX, and show the
plan before acting. Then fix in waves, each with tests, each mirrored where the household mirrors code.
This is the work of 2026-11-08 and 2026-11-09 (Project-Sophos #1574 onward).

## Reporting

Say, in one line, what you found in the touched code and what you did about it, or that there was nothing.
In a close-out, a state machine you named and fixed is a `learned` line; one you found and left is an
`improve` line for the ledger.

## Where it lives

- This skill: `Project-Sophos/skills/state-machines/SKILL.md`, synced to every household repo.
- Doctrine: `docs/SOPHOS-OPERATING-SYSTEM.md`, beside Phase 5b; the Sophos front door names it.
- Hook: `.claude/hooks/state-machines-nudge.mjs` points to this skill on the first code edit of a session.

Soli Deo Gloria.
