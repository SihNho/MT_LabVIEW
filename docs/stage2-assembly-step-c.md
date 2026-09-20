---
type: reference
status: current
date: 2026-09-15
tags: [docs, stage2]
---

# Stage 2 — assembly step C (v2): the producer/consumer core in REPLAY (overnight cycle 5, 2026-09-15 03:0x)

Parents: [stage2-plan.md](stage2-plan.md) items 1, 2, 4, 8; [step B](stage2-assembly-step-b.md) = the numeric
reference harness `Track_v6_CPU_core_v0.vi` (INDEX row 40: bit-identical on all 10,018 pre-loss frames). Step C moves
the SAME kernel path into the pool-queue structure. **v1 was rejected** (`archive/peer/2026-09-15-stage2-step-c-
queue-core-plan.md`): its tracker stopped on a Dequeue timeout, which is not end-of-stream, would process a phantom
default slot on the timed-out iteration, and rested on a backwards "Q_img can never be full" invariant.

## v2 design — replay = three FOR loops over the known N, parallel through queues, no stop logic, no timeouts

```
[pool]  For i over Pool Names[8] (String[] auto-indexed): IMAQ Create(name = Pool Names[i]) → auto-indexed → pool[8]
        Q_free (I32, max 8) ← For k over Slots[0..7] (I32[] auto-indexed): Enqueue(Q_free, k)
        Q_img (I32, max 8) · Q_meta (String) · Q_res (DBL[]) · Q_good (Bool[]) · Q_pos (I32[]) · Q_rmeta (String)
[ACQ]   For i over Frame Paths (String[] auto-indexed, N = its length):
        slot ← Dequeue(Q_free, -1) → Index Array(pool, slot) → IMAQ ReadFile(path_i, image = that slot)
        → Enqueue(Q_img, slot, -1) ; Enqueue(Q_meta, path_i, -1)
[TRK]   For n in 0..N-1 (N = Frame Paths length, via the same auto-indexed input tunnel):
        slot ← Dequeue(Q_img, -1) ; meta ← Dequeue(Q_meta, -1) → Index Array(pool, slot) → kernel (3 registers)
        → Enqueue(Q_res / Q_good / Q_pos, kernel outs) ; Enqueue(Q_rmeta, meta) ; Enqueue(Q_free, slot)
[sink]  For n in 0..N-1: Dequeue(Q_res/Q_good/Q_pos/Q_rmeta, -1) → auto-indexed → XYZ / GOOD / POS / META
        then Release ×7 ; final census: Q_free holds 8 (slot invariant), every other queue empty
```

Why this is safe where v1 was not (v2 review `…-queue-core-plan-v2.md`, conditions stated as the reviewer required):
**on the no-error path**, with all three loops executing exactly N iterations and every queue operation completing
once, the queue graph has no circular wait — ownership F + A + I + T = 8 (free / held by ACQ / in `Q_img` / held by
TRK), and at the instant before ACQ enqueues A ≥ 1 so I ≤ 7: `Q_img` (capacity 8) is never full for the producer.
No timeout, no end-of-stream signal, no Case. **Any operation error or transaction-count mismatch is an
intentional hang** caught by the bgrun deadline — so the recipe gates: all three iteration counts == N, no queue
error, TRK parallelism explicitly off, and the final `Q_free` drained == exactly the permutation {0..7} (count 8
alone would miss a duplicated/lost slot). The paired queues are FIFO and produced/consumed once per iteration by a
single producer/consumer; their enqueues are **error-chained** (second `error in` ← first `error out`) so a
failed first enqueue cannot publish a partial pair; the sink's `META[n] == Frame Paths[n]` for every n is the
alignment gate for the metadata stream (plan item 8), and the exact-once/FIFO facts carry the result triple.

Live mode (step D) is where the While tracker, an end-of-stream token and a timeout-gated Case are unavoidable;
none of that is built here.

## Rule-1a gate before assembly: the pool images must be the working image

`IMAQ ReadFile` into a pool image (created by `IMAQ Create` with the same defaults as step B's working image) is
gated, not assumed: scratch = step-B core with the working image replaced by pool slot k (k = 0..7) for ONE frame
→ XYZ/GOOD/POS bit-identical to the reference for each k. (Vision reallocates storage on size change; decoded
pixels should be unaffected, but type/border equality is what makes the kernel input identical.)

## v2.1 construction simplification (03:3x, after the loop-node census `census_loop_node_terms.log`)

**The pool is a queue of IMAGE REFNUMS, not of slot integers.** `Q_free` / `Q_img` carry the IMAQ image refnum
itself (typed from a top-level `IMAQ Create.New Image` sample): the pool For loop creates 8 images (names from
`Pool Names[i]`) and **enqueues each into `Q_free` inside the same loop** (seeding = creation); ACQ dequeues an
image, reads the frame into it, enqueues it to `Q_img`; TRK dequeues it, runs the kernel on it, enqueues it back
to `Q_free`. No `Slots` array, no pool array, no `Index Array` (which the fleet can only place at top level) —
and plan item 1's ownership discipline is unchanged. The slot-identity gate becomes: after the sink, 8 dequeues
of `Q_free` succeed (count 8; refnum identity is not readable over COM — recorded as the residual gap).
Also measured: a loop NODE's `Terminals[]` lists its tunnels' outer terminals by name (NAMES.md), so loop outputs
are wireable by `wire()` — not needed after this simplification, but recorded.
Type samples for the result queues: a **top-level kernel instance kept as a type source** (its outputs sample
DBL[] / Bool[] / I32[]); the recipe gates whether its unwired inputs leave the VI runnable and, if not, wires them
from the head (one extra kernel call per run, harmless). Strings: `PathToStr.vi` (one-node sub-VI copied by index
from `save N xyz traces.vi` uid 160) dropped at top level. Loop counts: TRK / sink / drain loops get an
auto-indexed input tunnel from `Frame Paths` (or `Pool Names` for the 8-drain) whose inner wire is then deleted —
an unwired indexed input tunnel still sets N (gated by ExecState and by the row counts).

## Toolkit facts used (all functional, rows 32–40)

- typed `Obtain` samples from node OUTPUTS: I32 = `IMAQ GetImageSize.X Resolution` (row 34); DBL[]/Bool[]/I32[] =
  the kernel's three outputs; String = `Path To String.string` (copied by index from `save N xyz traces.vi` uid 160,
  fed from `StrToPath.path`) — no new sub-VI.
- element wiring into `Enqueue` from a node output / tunnel element: `wire(...,'element')`, and the auto-indexed
  tunnel route (wire then flip, row 40 D).
- `Dequeue.element` → `Index Array.index`; `pool` (a 1-D image-refnum array from the pool loop's auto-indexed
  output tunnel) → `Index Array.array` through a non-indexed tunnel (gate IndexMode 0, row 40 L4).
- the kernel's registers on the TRK **For** loop: the ForLoop-seed ops (row 39) exactly as in step B.
- I32[] `Slots` and String[] `Pool Names` / `Frame Paths` controls: the create-then-cut trick (rows 39–40).

## Phases (fatal gates; one runner)

C0 pool-image gate (8 scratch runs) · C1 pool loop + 7 Obtains + seeding loop (census; a scratch drain of `Q_free`
returns 0..7 in order) · C2 ACQ loop · C3 TRK loop with registers · C4 sink loop + releases; ExecState 1 → save ·
C5 numeric gates 1 → 2 → 200 → `--full`, plus `META == Frame Paths` and `Q_free` == 8 at the end.
