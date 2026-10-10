---
name: score-models-by-total-cost-to-success
description: Choose models by total cost to a working result including retries — and split the expensive planner from a cheap executor/grounder rather than letting the top model do mechanical GUI work
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-04T05:48:13.175Z
type: decision
status: in-force
date: 2026-09-04
source: memory/score_models_by_total_cost_to_success.md
---

# Judge a model by total cost to success — and don't let the top model do mechanical work

Two layers, stated by the user at different times. The second revises how the first is applied.

## The scoring rule (2026-08-26)

**"attempting multiple times with lower model might be more costly than applying higher model."**
A cheaper model that fails, or needs three attempts and human re-steering, consumes more tokens and
far more wall-clock than one successful run on a stronger model — and on this project it also
consumes something scarcer, supervised time on a LabVIEW instance shared with real experiments.
Retries are not free; a failed run has negative value because the fallback is the user working by
hand. When reporting a benchmark, lead with **tool calls to a verified success**, not per-token
price, and count a failure as a failure rather than as a cheap partial.

The measurement behind it: at an identical 40-tool-call budget on the same GUI task, Haiku 4.5
completed **0 of 3** steps (spending its whole budget failing to open the Functions palette) while
Sonnet reached 2 of 3. Neither produced a usable result, so the apparent saving was illusory.

## The revision — split the roles (2026-09-03)

The user pushed back on the way that rule was being applied: the top model at high effort was doing
the *mechanical* half of GUI work itself — reading hundreds of full screenshots and computing click
coordinates — which is "필요 이상으로 비싼 모델을 비싼 effort로" using an expensive model for work
that does not need it. Their proposed architecture, which should be the default going forward:

- **Planner (expensive, few calls)** — decides what to build, resolves names, writes the batch
  script, judges results. This is where a strong model earns its price.
- **Executor / GUI controller (cheap, many calls)** — a *separate sub-session* that runs the script
  and drives clicks, invoked only when needed.
- **Grounder (free, local)** — UI-TARS via Ollama answers "where is X on screen"; it exists and is
  calibrated but had gone unused for over a week while the top model squinted at screenshots
  instead.

So the first rule is not "always use the strongest model" — it is "do not pay for strength on the
steps that do not need it". The strong model stays on judgement; mechanical steps get delegated.

**The tier must be chosen by measurement, not assumption**, and the earlier Haiku-vs-Sonnet result
does not settle it: that test predates both the scripting op fleet and the local grounder, so it
measured "can this model squint at screenshots", not "can it orchestrate a scripted toolchain".
Re-benchmark before quoting it. Note also that the LabVIEW instance is a single shared resource, so
benchmark runs are serial and the wall-clock occupancy — not the token bill — is usually the
binding cost.
