---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing
  or creating PRs - requires running verification commands and confirming output before
  making any success claims; evidence before assertions always
version: 2.0.0
license: LicenseRef-Proprietary
category: integrity
keywords:
- verification
- completion
- testing
- evidence-before-assertion
- test-pass-claim
- regression
compatibility:
  claude-code: '>=2.1'
kind: skill
runtimes:
- hermes
- claude-code
- grok
- codex
capabilities:
- read
- shell
runtime_bindings:
  claude-code:
    allowed-tools:
    - Bash
    - Read
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "The change is logically equivalent" | Prediction, not verification |
| "I've reviewed the code and it looks correct" | Review ≠ execution |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When verification cannot be run

If verification is not possible in the current environment (no test runner, no browser, no DB, no network), say so explicitly:

> *I cannot verify this claim in the current environment. Required: `<command>`. Expected output: `<description>`. Please run before merging.*

Honest gaps beat invented confirmations. "I made the change but couldn't run the tests" is professionally acceptable. "Tests pass" without running them is not.

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## Troubleshooting

| Failure mode | Corrective step |
|---|---|
| You wrote "tests pass" without running them | Stop. Run the tests. Update the claim with the real result. |
| The command failed; you described it as "a minor warning" | Quote the actual error. Decide whether to fix or report. |
| You ran a partial command (e.g., one test file) and claimed full coverage | Re-run the full suite. Adjust the claim. |
| The environment lacks the verifier | Say so. Don't claim verification anyway. |

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

## Inspiration

Two lineages merged 2026-07-05 (ecosystem-audit reconciliation). The Iron Law / Gate Function / rationalization-table core is the household-consensus variant deployed at six locations (ken, manateecreeksheep, Romans, InTheWake, Family-History), itself derived from the superpowers pattern. The honest-gap template ("When verification cannot be run") and the troubleshooting table are this repo's original v1.0.0 contributions, preserved as the superset. The pattern shows up across the household: recipe transcription marks `[UNCLEAR]` rather than guessing, sermon evaluation runs the rubric rather than assuming the score, flock validation runs `validate_flock.py` rather than declaring the database consistent.
