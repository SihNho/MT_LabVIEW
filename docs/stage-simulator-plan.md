---
type: plan
kind: stage-plan
status: current
date: 2026-09-25
tags: [simulator, stage, prerun, jev]
---

# Stage simulator and offline pre-run — plan

Decided by the user in the 2026-09-24 structure discussion (item 1, "repeated failures"). The rules themselves
are in `CLAUDE.md` §3 "Stages are simulated and pre-run offline"; this page is the design and the build order.

## Why

Loop-1.7 split, 2026-09-24 02:37–07:29: 6 of 9 stage runs failed, about 49 min of LabVIEW time and two to three times
that in diagnosis, reviews and two firefighter cycles. Every failure was knowable without LabVIEW:

| run | failure | knowable offline by |
|---|---|---|
| `stage_d1_l7_1.log`, `_r2` | Jev undecided on error / accumulator chain rows | chain rule (no Jev) + pre-run "every row decided" |
| `stage_d1_l7_1a.log` | observed cut set ≠ hand-written prediction | cut set computed from the graph |
| `stage_d1_l7_1b.log` | owner and direction swapped while the recipe re-typed a row | rows only from the plan file |
| `stage_d1_l7_1b_r2.log` | unwired terminal unreachable by wire-walking uid lookup | pre-run addressability check |
| `stage_d1_l7_r.log` | Python `'<'` between str and int after 11 min | dry run |

Jev's picks matched S1 on every row it decided (`stage_d1_l7_1b.log:35-40`); both addressing failures were LLM
hand-assembly in the recipe.

## The method (user: "Sequential하게 각 단계들을 시뮬레이션 하여 temporary 파일로 저장한 후에 각 사이클의 finalized 플랜을 두는게 맞는듯")

1. **Plan** (LLM): which node sets move into which structure; which structures, shift registers and tunnels are made.
2. **Predict and simulate** (Python): apply each action in order to the graph JSON — move, create, delete, wire —
   and save each step as `tools/bench/sim/<stage>/step_NN_<action>.json`. The next action reads the previous
   step's simulated graph. For a move, the cut set is the set of wires crossing the moved set's boundary; the
   reconnect table maps every cut terminal to its S1 partner. New objects carry symbolic ids (`new:SR1.right`).
3. **Decide per row** (Jev): only the mechanism where more than one is legal (tunnel / shift register / indexing)
   and ambiguous pairs without an S1 partner. Error-cluster and accumulator chains are copied from S1's chain order
   (`RULE-CHAIN-S1`), never asked. Low-confidence rows go to the LLM.
4. **Finalize**: the plan file `tools/bench/plan_<stage>.json` is final only when the last simulated graph gives
   `computation_diff(S1, ·)` = 0 rows.
5. **Offline pre-run** (no LabVIEW): dry run of the whole script with the COM layer stubbed; every row decided;
   every terminal addressable from the graph (unwired terminals via owner node → terminal list → uid echo);
   rows to execute == plan rows; no literal uids / terminal names re-typed in the recipe.
6. **Execute once** in LabVIEW: after each action read the real graph (≈ 5 s) and compare with that step's
   simulated graph; stop at the first difference. Created objects are BOUND by diffing the terminal table right
   before and right after the create action (the new uids are the created object); count or class different from
   the simulation ⇒ stop. Positional addressing is a cross-check only.

## Op effect models (to be MEASURED, not assumed)

Each op the simulator uses gets one scratch measurement on a copy of the bed before it is trusted:

| op | effect to measure |
|---|---|
| `move_in` | exact cut set; any tunnels LabVIEW makes by itself; stray invokes left (P6d) |
| `add_shift_reg` | new uids (right/left, inner/outer terminals), names (empty), wire counts |
| create primitive / constant | new node + terminals |
| `delete_wire` / `delete_object` | leftovers; what Remove Bad Wires then deletes |
| `connect_from_wire` / `wire_sr` / `fs_inner_tunnel_connect` | edges added, tunnels created |

A model that disagrees with a later real execution is corrected from that execution's diff, and the disagreement
is the stage's stop reason.

## Enforcement (what is code, not prose)

| decision | where |
|---|---|
| 1 dry run · 2 offline pre-run · 4 re-pre-run after a failure · 7 finalized plan | `tools/hooks/guard_bash.py` launch gate: a LabVIEW stage run needs dry + pre-run PASS records for the script's current sha256, newer than its last failing log (`tools/bench/prerun_records.jsonl`) |
| 3 chain rule | `tools/jev_candidates.py` `RULE-CHAIN-S1`; pre-run checks no Jev row on a chain terminal |
| 5 Error List at cycle start | `tools/cycle_runner.py` `errorlist_hook` + `tools/errorlist_check.py` |
| 6 predicted cut set · 7 step-by-step comparison · binding | stagekit gates in the executor |
| 8 rows only from the plan | executor reads the plan file; pre-run compares and lints the recipe |

## Build order

1. Launch gate + dry run + pre-run + chain rule (material, no LabVIEW) — dispatched 2026-09-24.
2. Error List check at cycle start (material, LabVIEW + GUI) — dispatched 2026-09-24.
3. Op effect measurements on scratch copies (LabVIEW), one per op above. **DONE** (chat-S1 132/0,
   `tools/bench/opmodels/*.json`; chat-S3 adds the `sim` parameter block to each and the only-sink measurement,
   `tools/bench/opmodels_onlysink.log` 64/0, 15 samples: fate stays AMBIGUOUS - constant 3 deleted/2 kept on delete,
   1/1 on move; node 1/4; tunnel 0/2; R1/R2 reproduce the earlier fates on fresh scratches, so edit history is not
   the cause - and the executor accepts either fate on those terminals, `allow_either`).
4. Simulator core (`tools/stagesim.py`): graph transforms per op, step files, symbolic ids, finalize check. **DONE**
   (chat-S2/S2b; chat-S3: every step on a measured model, `open_rows` finalize rule - a plan is final iff its end
   rows are exactly the rows it declares open; `tools/bench/sim_l7_split.log` 13/0, `tools/bench/plan_l7_split.json`
   final; `tools/bench/selftest_stagesim.log` 39/0).
5. Executor on the plan file with per-step comparison and binding (stagekit). **DONE** (chat-S3,
   `tools/stagexec.py`: compile plan -> real ops, per-op graph read + compare to the step file, binding by terminal
   diff, register outer faces addressed by unique live name else tracked loop index; `selftest_stagexec.log` 15/0;
   launch gate: `py tools/stage_prerun.py --dry|--prerun <plan.json>` records keyed on stagexec's sha256 + plan md5,
   `selftest_stagexec_gate.log` 7/0).
6. Bench: replay loop 1.7's split through the simulator from `D1_s3_loop15.vi` and compare the simulated end graph
   with the real `D1_s4_loop17.vi`. Pass = identical up to new-uid naming. **DONE** (chat-S3,
   `tools/bench/stagexec_l7_bench_r2.log` 14/0: 45 actions -> 35 real ops, every op diff 0 against its step file,
   ExecState 1 warm, end cdiff == the declared open row, canon diff 0 against `D1_s4_loop17.vi`, scratch deleted,
   both beds unchanged. Run 1 `stagexec_l7_bench.log` stopped at op 8 on our own face-index tracking bug, review
   `archive/peer/2026-09-24-chatS3-stagexec-r1.md`).
