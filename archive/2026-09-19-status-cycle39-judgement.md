---
type: archive
status: historical
date: 2026-09-19
cycle: 39
tags: [d1, route-b, judgement, zdz, remove-bad-wires]
---

# Cycle 39 — the judgement record: how the `#2222` regression was traced to a VI-wide reaper

Narrative layer for `STATUS.md` (rule 4). STATUS keeps the launch line for run 8 and the two traps; the reasoning
chain lives here. Nothing in this file is current state.

## §1 What the cycle did, in order

1. **Dispatch 1 — run 7 built and RAN** (`tools/recipes/build_d1_routeb_v4.py`,
   `tools/bench/build_d1_routeb_v4_run7.log`, `BGRUN END rc=1 after 1840s`). This satisfied the user's standing
   ordering rule that a cycle's first act is a D1 build dispatch.
2. **Dispatch 2 — the mandatory failed-prediction review** (`archive/peer/2026-09-19-routeb-run7-index-shift.md`,
   ANSWERED, claude/hypothesis opus max, $5.1027, 760 s). It also discharged `guard_peer`'s block on
   `tools/bench/stall_pid7288_023957.log`.
3. **Dispatch 3 — a `log-reader` pass** over run 7's log and v4's source for the ORDER of the temp-sink bracket.
4. **Dispatch 4 — run 8 built as v5, released, and REFUSED** by `guard_cycle`'s retrospective gate. Not run.

## §2 The three decisions judgement took into run 7 (J1–J4), and how they fared

Taken from `archive/peer/2026-09-19-routeb-run6-regression.md`.

| # | decision | outcome |
|---|---|---|
| J1 | invalidate the per-(target, diagram) wire-map cache at the temp-sink create and delete | **REFUTED by measurement.** Both sites fired (`cache hit dropped: True`, `…run7.log:350`, `:357`) and nothing recovered |
| J2 | make the `Z/dZ` verification a measurement: source-terminal uid, wire-count delta, `Is Broken?`, sink read-back | **PAID OFF.** Three of four readings pass; the fourth exposed the −96 |
| J3 | retire the `:181` pre-reparent gate, which asserted the route Pre-decided 13a replaced | **CORRECT.** Run 7 is 80 PASS / 0 FAIL |
| J4 | remove the 70-char message truncation | **PAID OFF.** t5's real message became readable for the first time |

J3's retired text, verbatim, for the record (v3 `:839-840`):
`gate("S3-zdz 'Z/dZ' -> #2222 t0 is wired BEFORE the #403 reparent (cycle15 Pre-decided 3)", bool(zdz_wire), f"sink wire {zdz_wire}")`

## §3 H4, and why judgement's own hypothesis was wrong

After run 7, judgement proposed **H4**: the temp `Equal?` stays alive on Diagram[24] while the sibling `#2222`
rows are wired, so their node indices are +1 and t3/t4 address past the end while t5 addresses the wrong node.

It was killed by a direct file read, not by argument. `OpCreateEqual_v0` is called at
`tools/recipes/build_d1_routeb_v4.py:1521` and `delete_object` at `:1668`, **both inside the single t0 handler
`from_ctl_unnamed` (`:1444-:1747`)**, while every sibling row dispatches from the `for r in rows:` loop at
`:1820` — after that handler returns. The bracket is tight and cannot shift indices under rows that run later.

The peer reached the same verdict from three independent readings: `run7.log:179` prints
`sink #2222 is Diagram[24].Nodes[20]` about 170 lines *before* the temp node is created at `:350`, so the
difference precedes the mechanism; `wire_control`'s destination is (class name, class index, terminal NAME), so
a `Diagram[24].Nodes[]` shift cannot generate `Input Correction Factor not found`; and the shift is not even
uniform — `#8885` is `D[24].N[25]` in both runs.

## §4 The surviving explanation, and the natural control that makes it testable

The mid-loop **VI-wide** `remove_bad_wires_scripted` at v4 `:1669`, run once per row immediately after the temp
node is deleted, reaps the build's own scaffolding rather than debris:

- The restructure deliberately leaves wires cut between S1d/S3 and S3w's rewiring pass — `…run7.log:274-280`
  shows `#2222`'s inputs cut and waiting (`cut #2222 t5 'Correction Factor' IN was w6096 [moved]`).
- The measured damage is a **−96 VI-wide Wire delta** across one row's bracket (`:360`), while the temp node's
  own single wire w29238 demonstrably SURVIVED (`Is Broken? False`, sink read back 29238) — so the temp node
  cannot itself have orphaned 96 wires.
- Afterwards `#2222` t3/t4 read `'<no such terminal>' is_source=None wire=None`, which is `.get()`'s **absent**
  default — the sink is gone, not merely wrong.
- **Run 5 is a natural control.** Its temp `Equal? #10104` returned NO-ROUTE at `build_d1_routeb_v4.py:1606-1609`,
  so the run never reached the `delete_object`/reaper pair at `:1665-1669` — and run 5's `#2222` t2/t3/t4/t5 ALL
  wired. Runs 6 and 7 reached the reaper and those rows failed.

Run 8 tests it by deleting exactly that one line (K1) and changing nothing else.

## §5 Two instrument defects found on the way

- **`gscript.net_map` cannot be used to count wires.** The peer proposed it (Q2) as the per-diagram counter that
  judgement had wrongly said did not exist. It does exist, but `net_map` drops an untyped Invoke on the target
  and then calls `remove_bad_wires_scripted(target)` itself (`tools/gscript.py:2507-2516`, `:2568-2588`) — using
  it for the two readings would have re-fired the reaper K1 removes, twice per row. The material session measured
  this and substituted `build_track_v6_core.walk:84-92`. Judgement accepts the substitution: a peer answer is a
  hypothesis, and this one was checked against the machine and failed.
- **The ledger counted attempts, not wires.** `wire_sr` and plain `wire` rows recorded no uid and no readback,
  and `wire_control`'s `next(..., 0)` collided "unwired" with "no such terminal", so a logged `wire 0 -> 0` was
  never evidence that a terminal exists. Fixed as K3 (`build_d1_routeb_v5.py:1130`, `:2036`, `:2120`).

## §6 What blocked run 8, and why judgement did not clear it

`tools/hooks/guard_cycle.py:661-670` refused the launch: `len(since)=10` against `CYCLE_BUILD_BUDGET=10`,
`hours=3.70` against `CYCLE_HOURS=8.0`, newest retrospective `archive/peer/2026-09-18-retrospective-cycle36.md`.
**Five of the ten `since` logs are `tools/wait_logs.py` WAITER logs** that `logclass.is_build_log` counts as
builds (`wait_priorart_run5`, `wait_priorart_run6`, `wait_c37_selftest`, `wait_c37_b`, `wait_c37_peer`); only
three were recipe builds (runs 5, 6, 7). The budget was consumed by waiters.

Judgement did not repair `logclass.is_build_log` and did not clear the gate. The overdue thing was the cycle's
own close, which is the last act of a session by rule; and the repair is a device, which the user's standing
order of 2026-09-18 08:53 forbids until they lift it. It is recorded as a finding instead.
