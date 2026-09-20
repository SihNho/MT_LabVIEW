---
type: plan
status: superseded
date: 2026-09-16
tags: [cycle-10, plan, hardware, owner-chain]
superseded_by: pre-rig-master-plan.md
---

# Cycle 10 plan — the owner-chain reader, then the measurements it unlocks (including hardware)

> # ⛔ SUPERSEDED 2026-09-16 — read [pre-rig-master-plan.md](pre-rig-master-plan.md) instead
>
> The user re-scoped this: *"내가 명시하기 전까지는 rig 조립 직전까지 할 수 있는 모든 플랜이 필요함."* Its
> technical content survives as **Phase A** of the master plan; this file is kept for the reasoning only.
>
> **⚠️ One claim below is WRONG and must not be reused.** The "H2, replaced" section argues that ASI focus is
> **operator-driven**, inferred from the subVI's inputs being control references. The user corrected this on
> 2026-09-16: *"나는 실제 실험 중 ASI를 매뉴얼하게 조작한 적이 없음 (조이스틱 하드웨어는 제외). 소프트웨어적으로
> off-focus 되었을때 포커스 재조종 들어간 것."* Focus is **software-driven**, and `keystone-op-spec.md:594` already
> named the trigger — *"the autofocus Case 10407 driven by bead 2's cal-slice index"*. See the ⚠️ block in
> `camera-acquisition-facts.md`.

Three user decisions on 2026-09-16 set this cycle. Two of them change direction, so this plan goes to the
prior-art review before anything is built.

## The decisions

1. **"build reader and tools first."** The fork was: build `OpOwnerChain_v0`, or honour the outcome review's
   "further readers are tooling drift" and go straight to a delivery slice. The user chose the reader.
2. **Hardware is no longer deferred.** *"You eventually need to operate the motors and machines before
   reassembling the rig. It includes the motor operation, reading, et cetera. I'll let you know when the rig is
   reassembled… Don't need to hastle around me before I tell you."* The 2026-08-27 motor ban is superseded for
   this window; rig-bound measurements move from "one later batched session" into the current queue.
3. **No serial on the frame path.** *"I don't want to have even a single frame loss coming from the motor
   communication if possible… serial communication through VISA can somehow stall the loop."* And the fact
   behind it: the sample stage drifts by itself (thermal drift, sample-holder pin), so **focus re-adjustment is
   continuous, not rare**, frequency unknown but "not trivial".

### Why step 2 needs a wider acceptance set — the citation I got wrong

This plan (and `docs/diagram-hierarchy.md`) cited `docs/NAMES.md:823` for the owner-chain semantics. That line is
about reading constant *values*. The fact actually lives at **`docs/NAMES.md:864-866`**, and it is scoped in its
own heading: **"Owner chain inside a case frame"** — a node's `Generic.Owner` is its frame Diagram, and that
Diagram's `Owner` is the **CaseStructure**. It was measured on CaseStructure and on nothing else, and
`archive/peer/2026-09-15-cycle8-plan-rule-audit.md:124` had already argued against generalising exactly this.

The main VI holds 84 structures across **six** classes (3 WhileLoop, 17 ForLoop, 37 CaseStructure, 21 FlatSequence,
4 Sequence, 2 EventStructure). Note that the recipe's own B6 gate tests `CaseStructure#10407` — the one class the
semantics were already measured on, so passing it says nothing about the other five.

**So step 2 validates one known case per class before any 170-diagram walk**, using ground truth we already hold:
`WhileLoop#637` → body diagram 43; `ForLoop#1359` and `CaseStructure#10407` on diagram 43. For FlatSequence — the
class `docs/diagram-hierarchy.md:66-69` flags as suspect — the discriminating check is a **round trip**: the frame
Diagram's owner should be the FlatSequence, and that FlatSequence should appear in its parent diagram's node-uid
list in `diagram_tree_main.json`. If it does not, that settles the doc's own open hypothesis (the JSON omits
FlatSequence nodes) rather than leaving it as a caveat.

## Why the reader, stated as a defect rather than a wish

`docs/diagram-hierarchy.md` resolved **129 of 170 diagrams**; 41 failed the margin test, and several FlatSequence
matches produced a structure uid that appears on no diagram at all. The method is nearest-structure **position
matching**, and this VI was rearranged by Clean Up Diagram, so position carries no meaning — the 21× margin that
justifies `gscript.loop_diagram` was measured on loops 700 px apart and does not generalise to structures tens of
pixels apart. Consequences that are currently unreliable rather than unknown:

- **which loop encloses the 11 PI motor / rotor call sites** — the doc's own verdict is "a strong indication, not
  a conclusion", and the requirement calls motor reading a frame-rate bottleneck;
- **the unconditional per-frame path**, which the whole split order depends on;
- **the frame loop's true member list** (body + nested frames), which the reseed `Or` collapse needs.

## Steps

> **REVISED 2026-09-16 by the prior-art review** (`archive/peer/2026-09-16-priorart-prior-art.md`, eight findings,
> zero `novel`). Every citation below was opened and confirmed before the revision was accepted.

| # | step | level of verification |
|---|---|---|
| 1 | **RUN `OpOwnerChain_v0`** — the recipe **already exists** (`tools/recipes/build_opownerchain_v0.py`, written 2026-09-15 18:59) and was **already corrected** for the failure its own prior-art review predicted: wire 751 has THREE consumers (163, 1221 and **482**), and the un-re-fed orphan is what broke `OpWireSource_v5`'s first rewire. It was never launched. This step is a *run*, not a build | structural B1–B5 + functional B6 (`CaseStructure#10407` → owner class `Diagram`, uid 639) |
| 2 | **Validate the owner semantics PER STRUCTURE CLASS, then re-walk** — the acceptance set is widened before the 170-diagram walk | functional, per class |
| 3 | **Which loop owns the 11 motor / rotor call sites** (`MOV.vi` ×7, `VEL.vi` ×4, `POS?`/`TMN?`/`TMX?`/`GOH`, `Magnet2Force` ×2, Autonics `SetCommand.vi` on diagrams 32/111) | functional, offline from 2 |
| 4 | **The unconditional per-frame path** — what executes every iteration vs. conditionally | functional, offline from 2 |
| 5 | **Every VISA/serial call site in the frame loop's true membership**, enumerated — this is decision 3's audit, and the list is what the restructure must empty | functional, offline from 2 |

## Hardware work this cycle (new — was deferred, now permitted)

Ordered cheapest-first, each a measurement with a number attached. The ASI **piezo** stays excluded; its detached
state is verified from the recorded rig state before anything touches that axis.

| # | measurement | why it matters now |
|---|---|---|
| H1 | **true `WHERE`-length VISA round-trip latency**, p50 and **p99** — SCOPED: `tools/bench/serial_roundtrip_asi.ps1` already exists and `archive/bench-2026-09-12-camera-identity/` already holds round-trip numbers. What is genuinely missing is the real command length with a real tail, not another mean | decision 3 is about stalls, so the tail is the quantity |
| H2 | **REPLACED — see below.** The original wording ("how often focus fires during a quiet period with no commanded motion") was refuted before it cost a rig session | |
| H3 | **per-frame cost of motor reading**, against the requirement's claim that it is a bottleneck. Largely arithmetic over numbers we already have (`docs/motion-path-audit.md:58-62, :90-98, :108-120`) once step 3 says which loop the call sites are in | step 3 says where; this says what it costs |
| ~~H4~~ | **DROPPED — already passed, 2026-09-13.** `archive/benchmarks/INDEX.md` row 31: hardware acceptance PASSED 20:22 and the visible −3-turn / `PAB 0` test PASSED 20:28 with the user watching — `PIC -10` moved −7.2°, the signed copy read **−7.2°** where the original read **+3 092 376 445.92°**. I proposed re-running a test that passed, misled by a stale "남은 것" line in `docs/questions-for-user-2026-09-14.md` that its own evening superseded | |

### H2, replaced: settle the MECHANISM offline before spending a rig session on the rate

The user's fact is that the stage drifts by itself and focus correction is continuous. Our own measurement
(`docs/camera-acquisition-facts.md:133-138`, `:169`) says the ASI focus subVI's `+Inc` / `-Inc` / `Focus inc`
inputs are **control references** — "the shape of a VI that acts only when a key or button says so" — and that the
serial is "paid only while a focus key is held".

These are not in conflict about *whether* focus is frequent; the user has run the instrument and I have not. They
are in conflict about **what drives it**, and that decides how it can ever be measured. Had H2 been run as
written — a quiet period with nobody at the keyboard — it would have recorded ≈ zero actuations and "concluded"
that focus is rare, contradicting the user's direct experience and burning a hardware session to do it.

**Offline first, no rig needed:** does any code path *write* those control references (a `Value` property write,
a local, a subVI call), or are they front-panel only? The answer splits the design:

| if | then |
|---|---|
| operator-driven | the rate is a property of the human correcting drift; measure it by logging actuations during a real run, and the frame-loss risk is real but arrives in operator-timed bursts |
| code-driven | there is an autofocus control loop we have not identified, and it must be found before any split order is fixed |

Rotor counter is at **0**, not the old 100,000-pulse baseline. Restore with `PIC 100000` before the original VI
is ever run again; the new VI does not need it.

## Prior-art disposition — all 8 verdicts ACCEPTED, none refuted (2026-09-16)

`archive/peer/2026-09-16-priorart-prior-art.md` (opus/high, $3.47, ANSWERED) returned eight non-`novel` verdicts.
Every citation was opened and checked; all held. The revisions above are the response. Two consequences the steps
below must carry, because they shrink this cycle further:

- **Step 3 is a RE-RUN, not a measurement.** `tools/bench/which_loop_owns_motor.py` already ran
  (`which_loop_owns_motor.log`, 2026-09-15 18:34) and resolved 18 of 19 motor/rotor call sites down to their
  owning structure. It prints the remaining blocker verbatim, 18 times: *"cannot step above this structure without
  the structure→home-diagram link."* Step 3 is that script re-run once step 1 supplies the link — minutes, not a
  cycle. **It is also the direction check on step 1**: the link that is missing is structure → the diagram it sits
  on, not node → its owner, and the latter already works.
- **Step 5's body-only half is already written down.** `docs/frame-loop-anatomy.md:40-55` lists the frame loop's
  six body subVIs with the terminals that identify them, including the ASI focus subVI **uid 48**. What is new is
  only the **nested-frame** membership delta. Do not re-derive the body list.
- **H4 is deleted, not deferred.** It was already executed in hardware with the user watching
  (`archive/benchmarks/INDEX.md` row 31: `PIC -10` → the signed copy read **−7.2°**; the visible `PAB 0` test
  passed 2026-09-13 20:28). Repeating it would have been a rig session spent on a closed question.

**How this cycle is released to build.** The gate (`guard_cycle`) reads the NEWEST `*priorart*.md` and blocks while
any verdict there is unrefuted. Since nothing was refuted, the release is not a `REFUTED:` line — it is a **fresh
prior-art review of this revised plan**. Run it before the first build; if it returns `novel`, the gate opens on
its own.

## What this plan does NOT do

It does not build a delivery slice, and it does not touch the acquisition/tracking split. Judgement returns after
step 4 and H1–H2, because the split order depends on their numbers. It also does not revisit the camera design
(free-running camera, `Buffer Number Mode = Last`, no eviction machinery) — that is settled and separately owes a
peer review before construction, not before measurement.
