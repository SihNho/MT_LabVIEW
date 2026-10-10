---
name: preserve-the-original-computation
description: The invariant in the parallelization is the image-analysis model and its numerical results; wiring and scheduling may change freely
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-13T15:59:58.617Z
type: decision
status: in-force
date: 2026-09-13
source: memory/preserve_the_original_computation.md
---

# Preserve the image-analysis model and its numbers — not the wiring

The user's instruction, 2026-08-30: *"원본의 연산방법 자체를 바꾸면 안돼."* — and then, when Claude
started treating any structural difference as suspect, the decisive clarification: *"내가 말한
연산 방법은 수학적으로 이미지 분산의 결과를 바꾸는 설정이야. 병렬화를 해서 변수 연결 방법이
바뀐다고는 해도 이미지를 분석해서 수치화하는 모델과 그 연산 방법 및 결과가 바뀌면 안된다는 말이지."*

So the boundary is precise, and it is not "change nothing":

- **Free to change — this is the whole point of the work.** How variables are connected and how work
  is scheduled: shift registers becoming auto-indexed tunnels, iterations running on parallel loop
  instances, tunnels replacing chained wires, the order in which independent beads are processed.
- **Must not change — this is the invariant.** The **mathematical model that analyses the image and
  turns it into numbers**, the method by which that computation is carried out, and **the results it
  produces**. Any setting or step that would alter the numerical outcome of the image analysis is
  off limits.

The practical test that follows: a restructuring is legitimate exactly when the same image and the
same calibration data yield the same X/Y/Z. Structural difference alone is not a violation —
Claude briefly treated "the decomposition changed" as automatically disqualifying, which is too
strict and would block the parallelization itself. The question to ask of any proposed change is
narrow and answerable: **does this alter the analysis maths or its output?** If yes, it is
forbidden; if it only moves data around, it is exactly what was asked for.

Where this bites in practice: substituting one sub-kernel for another (for example replacing a
kernel that processes two beads in one shared transform with two single-bead calls) is legitimate
**if and only if** the per-bead numbers are the same. A shared transform used purely for speed is
plumbing; a shared transform that changes what is computed is the model. Establish which before
substituting, and when it cannot be established, ask rather than assume.

## Carrying something over does not require understanding it (user, 2026-09-13)

While digging into the rotor driver's `Baseline Startpoint` constant to work out what its units meant, the
user cut it short:

> *"애초에 configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야? 확실히 모르잖아."*

The instrument configuration — ports, baud rates, baselines, startup constants — **is preserved as-is**. It is
part of what works, and it is exactly the category where confident-looking inference has already been wrong
several times in one session. So the requirement is to **carry it over unchanged**, not to re-derive its meaning
first.

The general failure this names: treating "I do not fully understand X" as a reason to keep excavating X, when
the task only ever required preserving it. Understanding is needed to **change** something safely; it is not a
precondition for **keeping** it.

The constructive form, which is also cheaper: when a new feature must drive existing machinery (a scheduler row
commanding a motor, say), **copy the call pattern the working code already uses** — the same subVI, fed the same
values from the same source — rather than reconstructing the semantics from first principles. That makes the new
path correct by construction, and it keeps the unknown constant unknown *and harmless*. Documenting what
something is remains worthwhile for the map; it is not a gate on progress.
