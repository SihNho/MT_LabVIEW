---
name: acceleration-items-2026-09-28
description: "The user's 2026-09-28 approval of four ways to speed up the loop-splitting project — pipeline the next step's offline prep beside the LabVIEW build, less review on a proven pattern, batch gate false positives, up to ~25 rows per step on a proven pattern — and refusal of hand-editing by the user"
metadata:
  node_type: memory
  pinned: false
  originSessionId: a5bcbf27-1eb1-4a4c-b234-98f27fbcff51
  modified: 2026-09-28T08:47:17.039Z
type: decision
status: in-force
date: 2026-09-28
source: memory/acceleration_items_2026_09_28.md
---

# Acceleration items approved 2026-09-28 ("1~4번은 적용하도록 하고. 5번은 어려움")

Measured before the decision (cycles 110–115): each 1.4–2.8 h, $24–54 cycle delivered exactly one saved build step;
LabVIEW builds take minutes; ~9 peer reviews per cycle; card pass rate 13/30, many failures being our own gate or
checker false positives. The user asked "프로젝트를 가속할 방법이 있을지" and approved:

1. **Pipeline** — while one material card builds step N in LabVIEW, another prepares step N+1 offline (plan,
   simulation, dry run, pre-run, prior-art). LabVIEW stays single-user.
2. **Less review on a proven pattern** — no prior-art review for a build step that repeats a pattern already launched
   successfully at least twice; the retrospective runs every 3rd cycle, or when a cycle delivered nothing, or when a
   violation is near threshold.
3. **Gate false positives batched** — log them to a queue and route around within the rules; one tooling card every
   few cycles drains the queue, instead of a card per false positive.
4. **Bigger steps** — up to about 25 rows per build step on a proven pattern (was 10–15 / ≤13).

**Refused: item 5**, the user hand-editing parts of the VI in LabVIEW from an instruction sheet ("5번은 어려움").
Do not propose it again as an accelerator; the build stays scripted.

**"Proven pattern" definition, confirmed by the user the same day ("지금방식 유지"):** a step's pattern (plan op kinds
+ created classes + stagekit/stagexec functions the recipe calls) must be covered by at least TWO OTHER build stages
that launched cleanly; the stage's own earlier runs do not count. Implemented as `stage_prerun.proven_pattern`.

**Second set, same day (speed items, from the measured 642-min breakdown), approved "1~4번 적용":** (1) every new
design is checked against `docs/user-rules.md` (prior-art review question + a USER-RULES line per design item) — the
pool/queue direction had contradicted the user's frame rules; (2) a card RETURNS to judgement at the first unexpected
result, with a SOFT 60-min alert that blocks only new launches — the user rejected a hard 30-min cut ("하다가 멈춰버리는거
아니야?"), since a delivering card took 46 min; (3) Error List: drop only the DUPLICATE scratch full read, the saved file
is always fully read — the user warned that skipping checks causes loops back ("도돌이표"); (4) a repeated failing tool
function goes to scratch-VI verification, not a model escalation.

## How I apply it

- Safety guards are untouched by these items: motor limits and reference, original-file protection, LabVIEW
  timeouts, rule 1a (computation unchanged), the failed-prediction review for a NEW failure class.
- Judge the effect by deliverables per cycle and cost per delivered step, against the 110–115 baseline (one step per
  cycle); report it to the user after a few cycles.
