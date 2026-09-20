---
type: reference
status: current
date: 2026-09-15
tags: [docs, stage2]
---

# Stage 2 — assembly step B: the replay core `Track_v6_CPU_core_v0.vi` (overnight cycle 3, 2026-09-14 23:4x)

Parents: [stage2-plan.md](stage2-plan.md) build order; [step A](stage2-assembly-step-a.md) (`add_shift_reg`),
[step A3](stage2-assembly-step-a3.md) (`wire_sr`). All construction primitives for a loop with kernel feedback now
exist (INDEX rows 32–38).

## What this slice is — and is not

The smallest VI that produces stage-2 NUMBERS on the fixture, in one LabVIEW run, with the feedback carried by real
shift registers:

```
[head, once]   HARNESS_loadcal (cal002 baked as default) → Array of cal clusters, cross size, x,y,(blankz) array
               make both cosine bandpass(cross size) → the two windows;  IMAQ Create → working image
[While loop]   Frame Paths[i] (auto-indexed IN) → IMAQ ReadFile → Image Out → PARALLEL_kernel_v3clean
               x,y,z / good / pos: 3 shift registers (left OUTSIDE ← initial-value controls; kernel out → right)
               x,y,z array out → auto-indexed OUT tunnel → 2-D indicator `XYZ`; stop ← Stop Flags[i] (auto-indexed)
```

No queues, no acquisition loop, no display, no reseed Case — those are cycles 4+ (plan items 1, 2, 3, 8). Acceptance
here: **x,y,z bit-identical to the archived reference (`archive/bench-2026-09-07-fixture/`, session 16:00,
`ff` values) for every frame before the first lost bead** (frame ≈ 11798); plain feedback ≡ the original's reseed
rule until then. Frames after the first loss are diffed and REPORTED, not gated (the reseed Case is plan item 3).

## REVISED route (23:5x, after the plan review `…-stage2-step-b-replay-core-plan.md`)

The review killed B0 (a `New VI Object` op cannot be parameterised: `style` is a typed ring, unretargetable by
script) and B2's tunnel-mode mutation, and demanded a ≥ 600 s run timeout. The replacement uses only proven
primitives and needs NO array control and NO stop logic:

- **The replay core is a FOR loop over `N`** (N wired by `connect_terminals`, row 30; `exit_loop` gives the
  auto-indexed `XYZ` output; parallelism OFF — the feedback is sequential by nature).
- **Frame path = an auto-indexed `Frame Paths` STRING-array control + a one-node sub-VI `StrToPath.vi`.** The
  fixture's 10,043 frame ids have **124 gaps** (reference jsonl: min 4, max 11824), so `Loop Counter` cannot index
  them; Python already knows every frame's full path, so it supplies the STRINGS and the array sets N. No
  `Format Into String` anywhere: the review (`…-revised-forloop-route.md`) showed a copied instance keeps its donor's
  argument count (5 or 6 in every small lab VI, `tools/bench/census_fis_donors.log`), a node's arity is not
  scriptable, and a mismatch is NI error 83/84 at RUN time. `String To Path` is 1-in/1-out — no arity —
  harvested with `copy_into(prepare=set_node_label)` from `background VIs_COPY\save N xyz traces.vi` (n7 uid 194)
  into `StrToPath.vi` (`tools/recipes/build_strtopath.py`: control, indicator, pane, functional round-trip of three
  strings incl. a space and a UNC path). The string-array control is the proven trick: `create_control` on
  `Get Controls.vi`'s `Control Names` terminal (a String[] control, row 33's build), then delete that wire and the
  helper node (gate: the control persists by UID, rank 1 String, terminal unwired).
- **Register ops rebuilt with the ForLoop seed** (`OpLoopCast_v1` donor): `OpAddShiftRegF_v0`, `OpWireSRF_*_v0` —
  the same recipes with `SRC` swapped; a WhileLoop-seeded op errors 1055 on a ForLoop reference (measured, row 28).
- B3's "exact-type gate per register": the fleet cannot read type descriptors, so the gate is FUNCTIONAL instead
  (v2 review): after the structural build, a 1-frame run (exact = the three initialisers reach the kernel) and a
  2-frame run (exact = the three `RightIn` feedbacks work) against the reference, then 200, then `--full`; B4 runs
  with `hard_timeout_s=600`, phases timed, and exits without further COM calls on a Run timeout.

Cycle 3 delivered the toolkit (INDEX row 39: `OpForLoop_v1`, the ForLoop-seed register ops, `OpMoveByIndex_v0` +
`StrToPath.vi`); cycle 4 = the assembly + fixture diff, recipe `tools/recipes/build_track_v6_core.py`.

### Cycle-4 assembly notes (00:4x) — two construction details not in the route above, each gated

1. **Kernel state/param controls** (`x,y,z array`, `Bead is good? array in`, `pos in cal image in`,
   `4 pack remainder`, `# of bead 4 packs`) are made by `create_control` on a TEMPORARY top-level kernel instance,
   which is then deleted (+ Remove Bad Wires) — `create_control` addresses top-level `Nodes[]` only, and the real
   kernel lives inside the loop. Gate: the five controls persist, terminals unwired. (Same trick as the String[]
   control, verified in row 39.)
2. **`Frame Paths` → `StrToPath.string`** is wired with `wire_control` (which creates a NON-indexed tunnel — the
   wire is array→scalar and therefore broken at that instant) and the tunnel's `IndexMode` is then set to 1. This is
   the plan review's "route 3"; it is applied BEFORE anything else depends on the inner terminal, and it is gated:
   the tunnel reads IndexMode 1 and `StrToPath.string` carries a wire, then ExecState 1 at the end. If the gate
   fails the batch stops (no fallback is attempted unreviewed).
3. Register wiring order per register: `LeftOutCtl` (control → left outside) FIRST, so the register takes the
   control's exact type; `LeftIn` → kernel input; `exit_loop` (auto-indexed output tunnel for `x,y,z array out`)
   before `RightIn`, so the register's right side is a branch off an already-wired output.
4. Fixture run: one COM run with `hard_timeout_s=600`, phases timed; acceptance = exact equality with the reference
   `ff` rows for every frame before the first lost bead (`--n=200` for a first pass).

The section below is the superseded first plan.

## (superseded) The one missing primitive: a front-panel ARRAY-OF-PATH control (and a Boolean array for the stop)

Peer research `archive/peer/2026-09-14-stage2-replay-path-array-control-route.md` ranked the routes; adopted:
**`New VI Object` twice** — an Array control owned by the Panel, then a Path (or Boolean) element owned by that
array (NI: an array control is a shell holding an element control). NI ships the pattern as a donor:
`examples\…\VI Scripting\Creating Objects\Drop Digital Numeric Inside Cluster.vi` (a container as `owner refnum`),
plus `Adding Objects.vi`. Unverified: the exact ring spellings for the Array and Path styles in LabVIEW 2026, and
whether the returned Array reference is accepted directly as the element's owner. Rejected: string→path wiring
(distinct types), Unflatten (Python would have to emit LabVIEW's binary Path format), `String to Type` grammar
(undocumented).

Op: `OpNewFPArray_v0` = the donor copied, its New VI Object nodes' `style` / class / position fed from controls,
`Set Name` on the result; returns the new control's label + UID. Built once, used twice (Path, Boolean).

## Phases (one runner; the first miss stops it, nothing saved on a miss)

| phase | does | prediction |
|---|---|---|
| **B0** | scratch: `OpNewFPArray_v0` places `Frame Paths` (Array of Path) on `EMPTY_v0`'s copy | `panel_wiring` shows exactly one new object; a node's terminal wired from it is typed 1-D Path (verified by wiring it into `IMAQ ReadFile.File Path` through an auto-indexed tunnel → ExecState 1) |
| **B1** | head: loadcal (`make_default` cal002 first), windows, `IMAQ Create`; controls for the kernel's initial state made from the kernel's terminals (as `build_harness_compare` does) | node census exact; ExecState 1 |
| **B2** | While loop with input tunnels `Frame Paths` (indexed), `Stop Flags` (indexed) + non-indexed params; `IMAQ ReadFile` and the kernel inside; `exit_while(stop='Stop Flags')` with the tunnel's IndexMode forced to 1 | ExecState 1 before the registers |
| **B3** | `add_shift_reg` ×3; `wire_sr` LeftOutCtl (initial controls) / LeftIn / RightIn ×3; `exit_while(output_names=['x,y,z array out'])` + `set_index_mode(1)` + `tunnel_indicator` → `XYZ` | each register: three wire UIDs match the far ends; ExecState 1; saved |
| **B4** | run: Python fills `Frame Paths` (10,043 paths), `Stop Flags` (F…F,T), initial state from the loader; one COM run; read `XYZ`; diff vs the reference | all frames before the first loss identical (exact float equality); post-loss deviation reported |

Level: B0–B3 structural (censuses) → B4 **functional** (numbers through the real path). The wiring ops' value
semantics across iterations are proven here for the first time.
