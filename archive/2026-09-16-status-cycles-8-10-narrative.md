---
type: narrative
status: historical
date: 2026-09-16
tags: [status-archive, cycle-8, cycle-9, cycle-10, overload, camera, reseed]
---

# STATUS narrative, cycles 8–10 — moved out of STATUS.md on 2026-09-16

STATUS.md had grown to 454 lines against its own ~100-line threshold (CLAUDE.md rule 4). Everything below is the
reasoning and history that was crowding out the current state. **Nothing here is deleted and nothing here is
current** — the live decisions it produced are in STATUS.md; this is why they were made.

---

## Cycle discipline — the four devices, and what each refuses

| device | what it refuses / reports |
|---|---|
| `tools/audit_cycle.py` | mechanical compliance of a cycle (bgrun discipline, runs terminated, failing logs reviewed, reviews annotated, originals untouched) + the cost lines. No judgement, no thresholds |
| `tools/retrospective.py --cycle N` | dispatches a FIXED question set about HOW the cycle ran, with the audit, the raw build logs and CLAUDE.md attached — Claude writes neither the questions nor the evidence |
| `tools/violations.py` | counts the `VIOLATION: <slug>` lines retrospectives record, **from the files** |
| `tools/hooks/guard_cycle.py` | refuses the next RECIPE build while the previous cycle has no newer retrospective, while a slug is at threshold, while the outcome review is due, or while a prior-art verdict is unrefuted |

Cost of the overnight window covering cycles 1–7 **plus** earlier rotor work (not cycle 7 alone): 130 builds,
23 failing logs, 83 peer reviews, 212 min inside bgrun.

## 2026-09-15 afternoon — review gained a THIRD layer, and it judged the project

Review became three layers (CLAUDE.md rule 5): hypothesis (`guard_peer`), cycle (`retrospective`), **outcome**
(`outcome_review.py`, every 5 cycles or 7 days, codex only, gated in `guard_cycle.py`). Also: `peer.ps1` gained
`-Agent claude` (rule/consistency auditor, sonnet — it CANNOT discharge a failed prediction), pinned codex to
`gpt-5.6-sol`/medium, records the model in every archive, and `-Kind review` REFUSES confirm-bait while appending
the adversarial instruction set. `guard_peer` additionally requires `outcome: ANSWERED` from an external peer.
Verification 13/13: `tools/bench/verify_review_layers_run2.log`. A fourth layer (prior-art) was added the same day;
see `memory/prior_art_review_is_the_fourth_peer.md`.

**The first outcome review fired all 7 slugs** (`archive/peer/2026-09-15-outcome-review-20260915.md`):
*"the next problem is not missing tooling; it is failure to cross the boundary from replay proof to experiment
product."* 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and **zero runnable experimental
VIs**; of the five functions the requirement names, none has moved into a product.

## Cycle 7 (reseed) — closed

The reseed measurements (four selector feeders, Case #5540's two frames, the `ReseedMux.vi` design) live in
`docs/stage2-assembly-step-e.md`. They and the NEXT list the outcome review superseded moved to
`archive/2026-09-15-status-cycle7-reseed-measurements.md`. One item survives into the delivery cycle: **Census A —
Case #10445** must be read before it is collapsed into an `Or`, as part of the reseed slice rather than its own cycle.

## How the OVERLOAD decision was reached, and what it cancelled

The user's ruling (2026-09-15): *"큐를 버리고 새로 들어오는 프레임을 읽는 것이 가장 바람직함. 이는 시계열
데이터의 엄밀성을 위함."* A result computed from a stale frame is a sample attached to the wrong moment; an explicit
gap is honest, a late sample is not.

### Three documents said the opposite, and both plan reviewers found it independently

(`archive/peer/2026-09-15-cycle8-plan-{attack,rule-audit}.md`.)

| doc | what it said |
|---|---|
| `docs/frame-ownership-design.md:77` | "if no free slot is available, acquisition **drops the new frame** and counts it" |
| `docs/restructure-plan-4.6.md:386` | "the acquisition loop **drops the new frame** and counts it" |
| `docs/stage2-plan.md:47-48` | `Q_img` timeout 0, "counted as dropped **by the tracker**" |

Drop-new and evict-oldest are **different state machines**, and only the second matches the user's stated reason:
under sustained overload drop-new yields a *contiguous but lagged* stream (the tracker stays ~8 frames behind),
evict-oldest yields a *current but sparse* one. The user asked for current-with-gaps. **All three documents were
given superseding banners on 2026-09-16** during the lint pass — they had gone a day without being corrected.

### The hazard that eviction would have created

A descriptor `{frame=N, slot=S}` can reach tracking *after* slot S has been refilled with frame M — the kernel then
computes a result **labelled N from frame M's pixels**. Worse than a missing frame, and the fixture cannot show it
(no overflow there). The rule-1a defence ("the original already loses frames") covers *whether* loss happens, never
*which* frame is discarded. The mitigations being designed were: an extra FILLING slot owned by neither side,
LabVIEW's **`Lossy Enqueue Element`**, and generation numbers or pixel sentinels.

**USER'S RULING that set the acceptance test for this area:** *"2번의 프레임 로스가 치명적이지 않기 위해서는
Buffer number가 갱신되어야 한다… buffer number 갱신이 어려운 상황인데 IMAQ 메모리만 바뀌었다 라고 한다면 정말
데이터 커럽션으로 봐야할듯."* — the pixels and the buffer number must change together, and the consumer must verify
them. The identity already exists in the original: `get buff image-lost frames.vi` carries `Buffer to extract`,
`current image number` and `Missed frames?`, paired with `LastBufferNumber` (measured, `boundary_manifest` wires
5416 / 3747 / 3689).

**AUTHORISED FALLBACK (user, same message):** if the handoff cannot be made provably safe, acquisition and tracking
stay in ONE sequential loop — *"Acquisition 및 추적은 동일 루프에 두고 시퀀셜 처리를 하는 것도 괜찮을 것 같음."*
This costs little: the requirement's parallelisation is mostly about getting motor reading, the scheduler, saving
and display OUT of the frame loop, none of which depends on splitting acquisition from tracking.

### Then the camera constraint dissolved the whole problem

*"카메라는 기본적으로 자신의 루프를 컴퓨터와 독립적으로 돌아야 하며 그렇게 돌고 있음… 따라서 Lossy Enqueue
Element 혹은 기타 다른 어떠한 방법도 카메라 frame acquisition에 영향을 주어서는 안됨."* The camera acquires on its
own clock into the driver's ring buffer; the PC is a **reader, never a gate**. Our own measurements already named the
mechanism — `docs/camera-acquisition-facts.md:66`: **`Buffer Number Mode` = `Last` "returns the newest buffer and
never waits"** (the default is `Next`, and line 375 notes the default is exactly what couples a consumer to the
camera's sequence).

**`Next` was considered and rejected on measurement.** It never duplicates, but it waits for a buffer that has not
arrived yet, so the loop period quantises to an integer multiple of the frame period: at 8 ms of work on a 150 Hz
camera it processes **74.9 Hz against `Last`'s 123.0 Hz** — 2.8× the frames lost, in exactly the regime we care
about. `Last`'s duplicates only occur when we are FASTER than the camera (i.e. when skipping costs nothing) and are
removed by the buffer-number check the user mandated. The one real argument for `Next` — evenly spaced samples — was
retired by the user: **the frame rate is hardware-controlled, so frame N happened at N/framerate regardless of when
we see it.** Skipping yields a uniform grid with holes, not irregular sampling.

**Live-behaviour risks are NOT to be pre-empted further (user):** *"최종적으로 확인하기 전에는 알 수 없는 부분임.
그 전에 할 수 있는 테스트는 모두 한 것 같음. 문제가 생긴다면 그 때 확인하고 고쳐야."*

## Step 0a — how the in-copy migration question was lost three times, then settled

**The failure was ADDRESSING, never capability.** Both runs of `tools/recipes/probe_relocate_route.py` are void:
**there is no rule about where a new Diagram lands in Traverse order, and every attempt to find one was wrong.**
`count("Diagram") - 1` ("the newest is last") was wrong; so was the replacement, `list(uids(...)).index(uid)` —
`uids()` is a SET comprehension, so that was hash order, and attempt 4 measured the same body at index **1** while
`new_since` reported `i=1` independently. Address a created object by **UID** via `new_since` / `fidx`, never by
arithmetic on a count (`docs/NAMES.md`).

An earlier version of the STATUS block asserted "a newly created Diagram lands at Traverse index 0" as measured
fact. It was corrected in NAMES.md the same evening and left standing in STATUS — the prior-art reviewer caught the
contradiction (`archive/peer/2026-09-15-priorart-testrun1-flatindex.md`).

The probe used `body_index = count("Diagram") - 1`, so `drop_subvi` put the subVI on **some other, pre-existing
diagram** — no error, and the gate passed on a whole-VI count that never looked at where the object landed. The plan
reviewer predicted exactly this before the measurement
(`archive/peer/2026-09-15-probe0a-run1-two-gate-fails.md`): *"'on diagram index 2' is printed from the input
argument, not measured from the resulting object."*

Two further defects, both confirmed: run 2's baseline was **run 1's leftover in-memory VI** (same scratch path,
LabVIEW serves the cached VI — use a UNIQUE scratch name per run; the donor on disk was never modified), and
`while_loop()` returns **elapsed seconds, not a UID**, which run 1's log reported as a UID.

### Attempt 4 (`probe_migrate_v2.py`, 3/3, 18:27) — the route works

On a fresh copy of `HARNESS_copyloop`, using only calls the 162/162 queue core already used:

| gate | result |
|---|---|
| K1 | the new loop body (uid 472, **Traverse index 1**) holds **`['StrToPath.vi']` and nothing else** — verified by LISTING the diagram, not by a whole-VI count |
| K2 | `wire_control("File Path" -> StrToPath.string)` created **exactly one** new LoopTunnel |
| K3 | that tunnel's inner wire **IS** the `string` terminal's wire — sink wire 527, `in_wires [527]`, `index_mode 0` |

**CAVEAT attempt 5 was built to settle:** K3's wire may have been a BROKEN wire. The source was the control
`File Path` (a Path) and the sink is `StrToPath.vi`'s `string` (a String) — a type mismatch — and `docs/NAMES.md`
warns that *"a wire-uid gate does not prove a wire is GOOD (a type-mismatched wire reads equal at both ends)"*.

### Attempt 5 (`probe_migrate_v3.py`, 5/5, 18:30) — the migrated state COMPILES

On `HARNESS_track`, chosen because it removes BOTH competing explanations at once: a **For** loop with an
auto-indexed array tunnel is legal with no `N` and no conditional terminal, and the border wire is String → String
so it cannot be a type mismatch.

| gate | result |
|---|---|
| M1 | donor starts legal, ExecState 1 |
| M2 | one For loop, one tunnel from `Bead is good? array in`, **IndexMode 1** (auto-indexed) |
| M3 | new body (uid 882, index 1) holds **`['StrToPath.vi']`** and nothing else |
| M4 | `Image Name` → `string`: one new tunnel, **sink wire 938 == tunnel `in_wires [938]`** |
| **M5** | **`ExecState == 1` — the VI is legal after the migration** |

`GObject.Move` is not needed and was never used. What remains untested is SCALE (75 nodes, 21 sibling couplings)
and RUNTIME behaviour, not feasibility.

**A stale block survived below this one until the 2026-09-16 lint** — it still asked "does the migrated state
COMPILE?" and demanded `VI.Get Errors` (method 452), a reader `docs/toolkit-capabilities.md` records as having
FAILED twice. A cold start reading STATUS in order would have built it.

## The seam measurement that kept plan A alive

`boundary_manifest.py 43` was the wrong instrument (it audits a whole diagram, and its 77 is `len(net)==1`, not a
crossing count — peer-refuted, `archive/peer/2026-09-15-frameloop-seam-77-crossings.md`).
`tools/bench/slice_cutset_acq_track.py` computed the real figure offline from the existing wire-graph JSON: the
kernel's measured slice is **22 of 75 nodes**; the ASI focus subVI #48 and the EventStructure #10153 are **outside**
it; **21 nets cross to sibling nodes**, 18 are internal, 49 already run to the loop border. So **subVI extraction
stays impossible** (21 + 49 ≈ 70 terminals vs a 28-terminal connector pane) but **in-place replacement is not
blocked by interface width**. Also corrected: the 49 "to border" nets are marked *unresolved* by the script that
produced them — the richer census finds **31** actual loop tunnels.

Two seam constraints to honour in any design: the tracking seam is an **immutable, frame-identified result message
BEFORE `save trace.vi` #376** (the 22-node slice is a *reachability* slice, not a component — lifting it drags file
ownership and accumulated `total data array` state into tracking); and the ASI loop must **exclusively own the VISA
session**, because case #10407's `Outgoing Handle` carries resource ownership, not just a value.

## Why the ordering was refuted

The strategy decision (restructure inside a copy) stands; the ORDERING that came with it was refuted by the plan
review (`archive/peer/2026-09-15-restructure-in-copy-plan.md`). My ordering rested on "kernel + one serial round trip
= 5.06 ms of 6.00", but `docs/camera-acquisition-facts.md` **already answered this on 2026-09-12**, 44 lines above
the line I quoted: *"the frame loop does NOT transact serial every iteration"* — the ASI wrapper's unconditional
top-level diagram is five nodes and its VISA case is a **gate only**; the real per-frame cost is **two UI-thread
property reads**. There is no ~2.5 ms ASI prize on ordinary frames, so ASI-first has no performance support.

**But the ASI loop is back on the critical path — user, 2026-09-15: "실제 사용 결과 ASI로 focus 조정은 꽤나 빈번하게
발생함."** The plan review deprioritised ASI because its serial is conditional; that reasoning assumed focus activity
is rare, and it is not. The frame loop's cost is therefore **bimodal** — cheap ordinarily, +~2 ms whenever focus acts,
inside a 6.00 ms budget — so the defect is **frames dropped during focus adjustment (p99), not average throughput**.

The user's objection is what produced this — *"A안은 모터 병렬화 포기한다는거 아니야?"* Motor CONTROL was already
its own loop (diagram 20) so nothing is given up there, but the hot-path-only plan would have left the ASI serial
subVI #48 and the ten property nodes in the frame loop.

## Superseded work order, for the record only

The 2026-09-13 order was "restructuring LAST"; the user superseded it on 2026-09-14 20:3x with
**"순서: 재구성(stage 2~) 먼저 → 나머지"** (`docs/questions-for-user-2026-09-14.md`). Execution had been following the
later direction all along, but the STATUS block still carried the old text until the outcome review caught the
contradiction.

```
[SUPERSEDED] 1. TOOLING -> 3. GATES G4/G7/G8/G9 -> 4. MEASUREMENTS -> 5. USER DECISIONS -> 2. RESTRUCTURE
```

Decided in that era and still true: two separate top-level VIs (CPU / GPU); rotor = 4th row of `CycleSchedule`,
absolute degrees, translation then rotation; `Value` property nodes → locals by rule. Plan:
`docs/restructure-plan-4.6.md`.

Earlier states: `archive/STATUS-2026-09-14-full-before-condense.md`,
`archive/2026-09-15-status-stage2-cycles-1-7.md`.
