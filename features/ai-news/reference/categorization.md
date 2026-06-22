# Categorization SOP

> Every news item gets exactly one primary category and up to two tags. This keeps the index scannable and the output structured.

---

## Primary Categories

### MODEL
New model releases, version updates, benchmarks, capability jumps, deprecations.

> Examples: GPT-5 release, Claude 3.5 Sonnet update, Gemini 2.0 benchmark results, Llama 4 weights drop

### TOOL
New developer tools, APIs, SDKs, integrations, plugins, agent frameworks, IDEs.

> Examples: Cursor new feature, LangChain v0.3, Anthropic MCP update, new Hugging Face Space, OpenAI Realtime API

### RESEARCH
Papers, technical findings, new techniques, evals, safety research, alignment work.

> Examples: new attention mechanism paper, RLHF improvement, ARC-AGI new results, jailbreak study

### PRODUCT
Consumer-facing product updates, UX changes, new apps built on AI, enterprise deals.

> Examples: ChatGPT new interface, Perplexity Pro update, Adobe Firefly in Photoshop, Microsoft Copilot rollout

### BUSINESS
Funding rounds, acquisitions, partnerships, hiring, valuation, market moves.

> Examples: Anthropic raises $X, OpenAI acquires Y, Google partnership with Z, xAI Series C

### POLICY
Government regulation, AI safety policy, copyright law, export controls, EU AI Act, executive orders.

> Examples: EU AI Act enforcement update, US AI executive order, China AI regulation, copyright ruling

### PEOPLE
Executive moves, researcher departures, new hires at key labs, public statements that shift narrative.

> Examples: key researcher leaves OpenAI, new Anthropic safety lead, Yann LeCun op-ed, Altman interview

### SAFETY
Alignment research, red-teaming findings, risk assessments, safety benchmarks, existential risk discourse.

> Examples: new jailbreak method, Anthropic safety paper, model welfare research, AIS policy

---

## Tags (pick up to 2 per item)

| Tag | Use when... |
|-----|-------------|
| `#breaking` | Major announcement, released today, no prior leaks |
| `#leaked` | Information came from leak/rumor, not official |
| `#open-source` | Model weights or code released publicly |
| `#multimodal` | Involves vision, audio, or video — not text only |
| `#agents` | Involves autonomous agents, agentic workflows |
| `#coding` | Primarily a coding / dev tool update |
| `#image-gen` | Image generation models or tools |
| `#video-gen` | Video generation models or tools |
| `#voice` | Voice / audio / speech models |
| `#reasoning` | Chain-of-thought, o1-style, math, logic models |
| `#context-window` | Long context, memory, retrieval updates |
| `#pricing` | Pricing changes, new tiers, cost comparisons |
| `#safety-concern` | Potential risk, misuse, or harm flagged |
| `#vs-previous` | Directly comparable to a tool/model covered before |

---

## Priority Levels

Assign a priority to each item to determine placement in the daily brief:

| Level | Label | Meaning |
|-------|-------|---------|
| P1 | `🔴 MAJOR` | Frontier model release, GPT/Claude/Gemini level event, paradigm shift |
| P2 | `🟠 SIGNIFICANT` | Major tool, funding >$500M, key policy, notable researcher move |
| P3 | `🟡 NOTABLE` | Useful update, interesting paper, product improvement |
| P4 | `⚪ FYI` | Minor update, duplicate story, background context |

---

## How to Apply

For each news item, write a one-line categorization header:

```
**[CATEGORY]** `#tag1` `#tag2` — 🔴 MAJOR
```

Example:
```
**[MODEL]** `#breaking` `#reasoning` — 🔴 MAJOR
```

This header appears at the top of each news block in the daily output file.
