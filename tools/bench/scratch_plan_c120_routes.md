# Scratch-VI check plan for the card 120-3 routes (Dequeue, Case in a loop body) — PLAN ONLY, NOT RUN

Card 120-3 (PD237(k), `labview: none`) added the offline routes; this is the <=120-line scratch check a LATER
LabVIEW card runs before any QRT-W stage uses them (CLAUDE.md "Scratch-VI verification before a third try";
record under `tools/bench/scratch_verify/`). Offline evidence so far: `tools/bench/selftest_c120_routes.log` 29/0,
`selftest_stagexec_c120.log` 124/0, `selftest_stagesim_c120.log` 77/0.

## What the script builds (one scratch VI, unique name, created and deleted in the same run)

- `scratch_c120_<stamp>.vi` under `user.lib\claudeDev`, from a blank VI (never an original). Front panel:
  Boolean controls `Sel` and `Stop`; top-level diagram: one Obtain Queue (element type from an I32 constant).
- Driven through `stagexec` itself (a stageplan/1 on the scratch VI's graph read, simulated, then `lv_run`),
  so the ROUTES are what is tested, not hand calls. Plan rows (the self-test plan's shape, `selftest_c120_routes.py` ACTS):
  1. `create WhileLoop DL1` on the top diagram.
  2. `create CaseStructure C1` in `new:DL1.body`, `label: "Sel"`, `selector_as: S1`, `frames: ["False","True"]`.
  3. `create Local LR1` (read `Stop`) in the body; `wire new:LR1.value -> new:S1.outer` (the selector).
  4. `create` a node in `new:C1.f1` (a copy_in of a scratch Add node, or a primitive); `tunnel T1` (dir in, body
     `new:C1.f1`) + its two wires from a body source into that node.
  5. `create Local LR3` in `new:C1.f0`; `tunnel T2` (dir out, body `new:C1.f0`) + wires to a Local write in the body.
  6. `create Function DQ1` `queue_kind: dequeue` in `new:DL1.body`, `src` = the Obtain's `queue out` on the top
     diagram (the auto-tunnel case), `data_stream: true`; `create DQ2` dequeue on the top diagram (same-diagram case).
- The VI is NEVER run (a `Dequeue(-1)` with no producer is a COM hang, docs/NAMES.md:912-913); only read back.
- Needs the widened schema: install `tools/bench/selftest_c120_stageplan_proposed.json` over
  `docs/protocol/stageplan.json` first (a card with that write flag), or the plan does not validate.

## What it reads back (machine reads only, no GUI)

| # | read | reader | UNMEASURED item it settles |
|---|---|---|---|
| M1 | DQ1/DQ2 terminal rows: names, directions, **term_class**, **Terminals[] order** | `wiki_build.read_live` rows + `node_terms_uid` | Dequeue term_class / order (stagesim `QUEUE_TERM_UNMEASURED`) |
| M2 | new LoopTunnel count after DQ1 (1) and DQ2 (0); its indexing mode | `uids(W,"LoopTunnel")`, `gscript.tunnels` | the auto tunnel for Dequeue (Enqueue measured, build_track_v6_queue.py:202) |
| M3 | `case_in` return: owner = DL1 body, `names` = `["False","True"]` for a BOOLEAN selector | `gscript.case_in` / `case_frames` | build_case frame names on a boolean selector (contract names `0, Default`/`1`) |
| M4 | the `Sel` control terminal's wire after the move (0 = no stub) and the case selector's rows | read_live rows of CT `Sel` and the new `Tunnel` | the severed-wire stub (stagesim `CASE_ASSUMED` 1-2) |
| M5 | `uids(W,"Tunnel")` diff after case_in = exactly the selector (not the For-N / other subclasses) | gscript.uids | the LVBackend 'case' branch's selector detection |
| M6 | T1/T2: ONE SelectorTunnel each, one inner face per frame, the other frame's inner unwired | read_live rows | case tunnel creation by a border-crossing connect |
| M7 | T2 'Use Default If Unwired' value and the VI's ExecState with f1's inner unwired | `tunnel_use_default_at` read-only form if it casts, else ExecState only | stagesim `use_default_if_unwired` ASSUMED False / `broken_unless_wired` |
| M8 | stagexec per-step diff (sim vs real) at every op, and BINDING of the case, frames, selector, T1, T2 | `lv_run` report | `bind_case_faces` against real uids |

## Pass criteria (each a gate line; the script ends with the C6 RESULT line)

- P1 every plan op dispatched; step diff 0 at every op (M8) — or each diff names one UNMEASURED item above.
- P2 M1: the 7 Dequeue names/directions equal `stagesim.QUEUE_TERM_TABLE['dequeue']`; term_class and order RECORDED.
- P3 M2: DQ1 -> exactly 1 new non-indexed LoopTunnel, DQ2 -> 0.
- P4 M3: owner == body uid, frames == 2, names == requested (else record the names LabVIEW gave — a FACT, not a failure
  of the check).
- P5 M4/M5: selector found as the single new `Tunnel`; `Sel` stub state recorded.
- P6 M6/M7: shapes as modelled; T2's default flag and ExecState recorded.
- P7 handle count flat (±100) across the run; scratch VI deleted; LabVIEW closed and verified gone at the end.

## Where a failure goes

A mismatch on an UNMEASURED item is a model correction in `stagesim.py` (the constant named in the table), not a
route change; a mismatch on a MEASURED item (names, case shape) is a failed prediction -> the Jev ladder / review.
