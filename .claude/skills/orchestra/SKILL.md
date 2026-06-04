---
name: orchestra
description: "Round-robin multi-LLM consultation with full-context debate. GPT proposes, Gemini refines, Grok challenges — each sees the full chain including wheat/chaff verdicts and justifications. Nothing is filtered between rounds."
version: 1.0.0
---

# The Orchestra — Round-Robin Multi-LLM Debate

> Ask the orchestra. Let them debate. Take what survives.

## Usage

```
/orchestra "task description"
```

**Mode:** `recipe` (auto-detected from this repository)
**Domain:** Granny Hudson's recipe transcription and site

## How It Works

Unlike `/orchestrate` (linear pipeline), `/orchestra` runs a round-robin debate where each model sees EVERYTHING from prior rounds — proposals, verdicts, justifications, and rejections. Nothing is filtered. What one model calls chaff, the next might rescue.

```bash
cd /home/user/ken/orchestrator && python3 orchestra.py recipe "task description"
```

## The Rounds

### Round 1: GPT Proposes
- Receives: task + relevant memories
- Produces: proposals (with confidence + justification), low-hanging fruit

### Round 2: Gemini Refines
- Receives: task + GPT's FULL response
- For each GPT proposal: WHEAT | CHAFF | WHEAT_WITH_REFINEMENT (with justification)
- Adds own proposals + low-hanging fruit
- May rescue ideas it thinks GPT undervalued

### Round 3: Grok Challenges
- Receives: task + GPT's FULL response + Gemini's FULL response (including verdicts)
- For EVERY prior proposal: verdict + justification
- Specifically looks for dismissed ideas worth rescuing
- Adds own proposals + identifies blind spots + low-hanging fruit

### Blind Spot Check
- The most contrarian model (Grok) reviews the emerging synthesis
- "What is the single most important thing we're all still missing?"

### Claude Synthesizes
- Sees the full debate chain: every proposal, every verdict, every justification
- Produces attributed plan: "GPT proposed X, Gemini refined to Y, Grok challenged Z"
- Encodes key decisions to cognitive-memory

## Why Full Context Matters

If Claude filters between rounds, rejected ideas die silently. With full context:
- Gemini can disagree with GPT's reasoning, not just its conclusions
- Grok can rescue an idea Gemini dismissed, explaining WHY Gemini was wrong
- The final synthesis is informed by the **debate**, not just the survivors

## Cost Reporting

Every run reports:
- Per-round costs (model, tokens, dollars)
- Total pipeline cost
- Idea survival rate (wheat vs chaff vs rescued)
- Low-hanging fruit from all models

Typical cost: $0.03–$0.08 per full orchestra run.

## Integration

- **cognitive-memory** — recalls relevant memories before Round 1, encodes decisions after
- **consult** — for quick single-model questions (use /orchestra for the full debate)
- **orchestrate** — the older linear pipeline (still available for simpler tasks)

---

*Soli Deo Gloria* — Let the orchestra play. Take what glorifies God.
