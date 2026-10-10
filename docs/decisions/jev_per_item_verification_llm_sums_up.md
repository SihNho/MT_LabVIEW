---
name: jev-per-item-verification-llm-sums-up
description: "The user's 2026-09-23 design direction — Jev's best use is verifying INDIVIDUAL items (which node to which node, which connection method, which script to call) as structured typed questions run in a loop, with the LLM only summing up at the end; Jev must never be a side \"advisory\" while the LLM still makes every decision"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-22T20:00:20.545Z
type: decision
status: in-force
date: 2026-09-22
source: memory/jev_per_item_verification_llm_sums_up.md
---

# Jev verifies individual items in a loop; the LLM sums up at the end

On 2026-09-23 the user found the project "too slow" even after Jev was wired in, and measured with me that the
cause was not Jev's latency (397 calls, 230 s total in a day) but that Jev had been attached only as advisory
lines while every decision, log read and next-step choice still passed through Opus/Fable sessions. Their
direction, in their words:

> "Jev의 가장 특장점이 빠른 반응속도이고, 이에 따라서 llm의 많은 부분을 Jev에 위임하면서 빠르게 처리되는 것을
> 기대했는데 너무 느리다고. … 한 번에 Jev를 루프처럼 돌려서 받아와야지."
> "Jev 가장 잘 활용하는 방법 중에서, 개별 index 혹은 개별 아이템들 검증을 돌리는 것이라고 생각함. 예를 들어 몇 번
> 노드와 몇 번 노드를 연결할지, 연결하는 방식은 어떤 방법인지, 어떤 스크립트를 불러야 하는지, 등등 이렇게 먼저
> 구조화 하고 최종적으로 summing up 역할을 llm이 해야한다고 생각함."

And when I asked whether Jev can make such judgements at all, the user's preferred answer was the second option
they offered themselves: **change the LLM's judgement structure to fit Jev**, not ask Jev LLM-shaped questions.

Later the same day the user set the division of labour one level higher: *"llm은 비교적 큼지막한 판단 (어떤 subvi와
어떤 subvi를 어떻게 이어야 할지)하고, 구체적인 배선-노드 연결관계 판단은 Jev가 하는게 맞지 않아?"* — the LLM
states the INTENT (which subVI result goes to which subVI input, in which loop, by which mechanism); Python
enumerates the candidate terminal pairs from the subVI wiki and the current connectivity map; Jev decides per
candidate pair (yes/no per pair, the code takes the best; which op; rule-1a risk); Python + LabVIEW execute and
the graph confirms reachability; the LLM only sums up. The connectivity map itself (reader op → terminal table →
graph, path-finding, diff against the original) is pure Python, no model. Also: the user cannot follow my op
VIs, so hand-drawing an op is never the fallback — tool-building stays my job.

## How I apply it

- **Structure first, then Jev, then LLM.** A stage is built as a table of individual items (per wiring row:
  source uid/terminal, sink uid/terminal, connection method, op script to call). Each cell is a small typed
  question Jev answers against measured tables (NAMES.md, terminal censuses, the op registry), run over all
  items in one loop with no LLM turn between items. The LLM reads the finished table with confidences and
  writes the summary or the stage.
- **Decisions become menus.** Recurring choices (next action after a run, row action proceed/skip/stop, review
  needed yes/no, stage pass yes/no) are mutually exclusive 2–3-way questions over structured evidence (gate id,
  predicted, observed), not open questions over a log. Overlapping 4-way menus measured 40 % yesterday; that
  was the question's fault, not Jev's.
- **Advisory-only is not delegation.** A Jev insertion that prints a line while the LLM still decides removes
  nothing from the LLM path and cannot speed the project up. When I "apply Jev", the answer must actually
  drive the code path, with the LLM reserved for the `unknown` band and genuine design questions (new stage
  design, rule-1a equivalence).
- **Measure each menu on a labelled set before it acts**, and make errors asymmetric: the dangerous direction
  (a defect classified as harmless) gets one LLM look; the safe direction does not.
- The LLM's remaining jobs: define the menus and table schemas at planning time, handle `unknown`, and write
  the summing-up.
