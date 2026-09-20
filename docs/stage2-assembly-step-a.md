---
type: reference
status: current
date: 2026-09-14
tags: [docs, stage2]
---

# Stage 2 — assembly step A: the missing primitive (shift registers) + the first skeleton

Written 2026-09-14 22:4x, at the start of the assembly cycle the user ordered ("Stage 2 조립 시작").
Parent plan: [stage2-plan.md](stage2-plan.md) (peer-reviewed, items 1–8 adopted).

## Why this document exists: one build-order line has no primitive behind it

`docs/stage2-plan.md` "Build order" step 4 says the tracking While loop calls the kernel **"with 3 shift registers"**
(`x,y,z array out`, `Bead is good? array out`, `pos in cal image out` fed back to the next iteration's
`x,y,z array` / `Bead is good? array in` / `pos in cal image in`). That feedback is not cosmetic: on the fixture the
previous frame's x/y is the next frame's starting point, so **without it the numbers are not the reference numbers**
and the acceptance test cannot pass.

Rows 32–36 of `archive/benchmarks/INDEX.md` claim "every construction primitive for the stage-2 assembly now exists".
**That claim is wrong by one item** — measured, not guessed:

- `gscript.while_loop` / `loop_in` create loops and **input tunnels** only.
- `gscript.exit_while(...)` creates **output tunnels** only: it sets the op's `Names 2` to `[]` unconditionally
  (`tools/gscript.py:817`).
- `OpShiftRegs_v0/v1` are **readers** (`Loop.Shift Registers[]`, `RightShiftRegister.Left Registers[]`).
- No op writes a shift register.

So step A of the assembly is: make shift registers a scripted primitive, then use it in the skeleton.

## REVISED 22:5x by the peer review — use the documented creation method, not the library side effect

`archive/peer/2026-09-14-stage2-shiftreg-primitive.md` (codex, ANSWERED 145 s) refused the plan below and named the
defect precisely: **LabVIEW exposes a direct creation method, `Loop.Add Shift Register` (ID `6361000`, input
`Y Position` U32, returns a `RightShiftRegister` reference)** — and this project had already catalogued it at
[NAMES.md:234](NAMES.md), flagged "not yet verified on this machine". The plan called shift-register creation a
"missing primitive" while its own name registry held the API. Using `Exit While Loop.vi`'s `Shift Registers` input
instead would have been, in the reviewer's words, an undocumented side-effect generator; and the reviewer could not
confirm that input's behaviour at all, because `AGENTS.md` forbids peers from opening `.vi` files.

Two further points adopted from the review:

- **`Terminal.Connect Wire` direction confirmed** (labviewwiki, `6349C03`): invoke on the DESTINATION terminal,
  `Wire Source` = the source. So the left register's **outside** terminal is the sink of the initial-value wire, and
  its **inside** terminal is passed as `Wire Source` when wiring the kernel's input. `LeftShiftRegister` derives from
  `Tunnel`, so `Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 apply — both are legal endpoints. That half
  of the plan stands unchanged.
- **The queue fallback is weaker than it looked.** Three separate depth-1 queues have no atomic tuple alignment: if
  one dequeue times out, errors, or a shutdown releases one queue first, x/y/z, good-flags and pos-in-cal skew by an
  iteration against each other, and a blocked dequeue on an empty queue with timeout −1 deadlocks the loop with no
  recoverable previous state. The fallback is therefore demoted: if it is ever needed it must be ONE queue carrying a
  cluster, not three — and that needs the donor cluster stage-2 item 8 says we do not have. Real shift registers are
  now the only planned route.

Revised phases (the runner stops at the first miss; `Exit While Loop`'s `Shift Registers` input is NOT touched):

| phase | what it does | prediction (machine-checkable) |
|---|---|---|
| **A0** | read-only census of `OpExitWhile_v0` — kept only as a record of what that unexercised input is wired to | two `Get Outputs`, one feeding `Shift Registers` (diagnostic; no pass/fail gate on the build) |
| **A1** | build `OpAddShiftReg_v0` = copy of `OpWhileCast_v0` (which already holds a WhileLoop-TYPED reference from the cast-free seed) + Invoke `Loop.Add Shift Register` `6361000` on it, `Y Position` control, `GObject.UID` indicator on the returned reference | the Invoke node carries terminals `reference`, `Y Position`, a return and the error pair. **If it carries only `reference`/`error out`, that is the documented private-member signature** (toolkit-capabilities.md) — the runner stops and `Invoke.Set Method (Allow Private)` `6370003` is the next reviewed batch, not a continuation |
| **A2** | **functional**: scratch While loop, `add_shift_reg(scratch, 0, y)` | `loop_cast(...,'WhileLoop')['shift_reg_uids']` 0 → 1, and its single element == the UID the op returned; `shift_reg_left` reports one `LeftShiftRegister` with outside wire 0 and inside wire 0 (an unwired pair, exactly what the kernel feedback then wires) |
| **A3** | `OpWireSRSrc_v0` / `OpWireSRSink_v0` (the two Connect-Wire ops) | deferred to the next batch — A1/A2 must land first |

Level reached by A1+A2: the op is **functionally** verified (an object is created on a real loop and read back by an
independent reader). Whether a register created this way carries values correctly across iterations is proven later,
by the fixture bit-identity diff of the assembled `Track_v6_CPU.vi`.

## (superseded by the review above) The route as first planned

1. **Creation.** `OpExitWhile_v0`'s donor chain already wires erdosmiller `Exit While Loop.vi`'s **`Shift Registers`**
   input from a second `Get Outputs` fed by the op's `Names 2` control (recorded in
   `tools/recipes/build_opexitwhile.py`'s header, read off the donor). `gscript.exit_while` simply never passes
   anything to it. Extension: `exit_while(..., shift_names=())` → `Names 2`.
   *Unverified assumption, stated as one:* that `Names 2`'s `Get Outputs` reads the SAME node as `Names`'
   (the donor has one node-selector Traverse), and that the library wires the RIGHT register from the named output and
   leaves the LEFT pair unwired. Phase A1 below measures exactly this before anything is built on it.
2. **Wiring the left side.** `Terminal.Connect Wire` (method `6349C03`, `reference` = the SINK terminal,
   `Wire Source` = the source) is proven on this machine by `OpConnectCtl_v0`
   (`tools/recipes/build_opconnectctl_v0.py`, functional in `build_harness_dispI.log`). The shift-register terminals
   are reachable cast-free inside an op by the chain `OpShiftRegs_v1` already contains:
   `WhileLoop → Shift Registers[i] → Left Registers[j] → Outside Terminal (6356001) / Inside Terminals[] (6356000)`.
   Two new ops, each a copy of the same intermediate with the two Connect-Wire inputs swapped:
   - `OpWireSRSrc_v0` — the left register's **inside** terminal is the SOURCE, a named input terminal of a node
     inside the body is the sink (this feeds the kernel).
   - `OpWireSRSink_v0` — the left register's **outside** terminal is the SINK, a node output / control terminal
     outside the loop is the source (this is the initial value).
3. **Node-terminal addressing inside a nested diagram** uses the `OpConnectCtl_v0` source chain with a
   `Traverse Diagram[index] → AbstractDiagram.Nodes[] → IA → Node.Terminals[] → IA` head, so the op can address a
   node on ANY diagram, not only the top level.

## Fallback, decided in advance (so a failure does not stall the cycle)

If the `Shift Registers` route does not create registers, **depth-1 queues stand in for the three registers**:
`Obtain Queue` typed from the initial-value control, seeded once before the loops, `Dequeue` at the top of the
tracking loop, `Enqueue` of the kernel output at the bottom. Single producer, single consumer, depth 1, strict data
dependency dequeue → kernel → enqueue ⇒ iteration *k* reads exactly what iteration *k−1* wrote: **semantically
identical to a shift register**, and every node in it is already functionally verified (INDEX row 34). It is recorded
as a stand-in, not as the final form — the deliverable gets real shift registers as soon as the op exists.

## Phases, each with its prediction contract (the runner stops at the first miss)

| phase | what it does | prediction (machine-checkable) |
|---|---|---|
| **A1** | scratch VI = copy of `HARNESS_copyloop`; a While loop with a node inside; `exit_while(shift_names=[one output name])` | `loop_cast(...,'WhileLoop').Shift Registers[]` length 0 → 1; `shift_reg(...)` inside-terminal wire == that output's wire; `shift_reg_left(...)` reports one `LeftShiftRegister`, outside wire 0 and inside wire 0 |
| **A2** | build `OpWireSRSrc_v0` + `OpWireSRSink_v0` from the `OpShiftRegs_v1` / `OpConnectCtl_v0` donors | both ops `ExecState == 1`, saved; donor md5s unchanged |
| **A3** | **functional**: an accumulator — While loop, shift register seeded with a constant, `Add` inside, stop after N — run it and read the sum | the VI runs; the indicator holds the arithmetically expected accumulation (this is the only step that proves a shift register, not just a well-formed object) |
| **B1** | `Track_v6_CPU.vi` from `EMPTY_v0.vi`: the once-only head — `HARNESS_loadcal`, `make both cosine bandpass`, the 8-image pool, `Q_free`/`Q_img`/`Q_meta`/`Q_res`/`Q_res_meta` | node census exact; `ExecState` may be 0 until the loops close — recorded, not saved |
| **B2** | acquisition While loop (replay mode: `IMAQ ReadFile` of `img%05d.tif` → `IMAQ Copy` into the slot) | tunnels/queue nodes as censused; stop by `Stop` control |
| **B3** | tracking While loop + `PARALLEL_kernel_v3clean` + the three feedback shift registers + P=4 kernel loop already inside the kernel VI | `ExecState 1`, saved |
| **B4** | fixture run + bit-identical diff against `archive/bench-2026-09-07-fixture/` | deferred to the next cycle if B1–B3 consume the batch |

Phases B1–B3 run only if A1–A3 all pass; on an A-phase miss the runner stops, prints the observation, and the
fallback is taken in the NEXT reviewed batch (never by continuing the failed one).

## What is NOT in this step

Live camera mode, `Images Missed` instrumentation, the sink/CSV writer, the display loop, the save path — stage-2
plan items that follow the skeleton. No hardware is touched; no original or vendor VI is written.
