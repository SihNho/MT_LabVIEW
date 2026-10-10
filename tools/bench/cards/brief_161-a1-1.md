---
card: 161-a1-1
status: current
date: 2026-10-10
---
# Brief 161-a1-1 (assignment 161-1) - OFFLINE tool change: every `delete_wire` op is a REQUIRED executor checkpoint (PD393(a)), with a self-test

`labview: none` (no LabVIEW process), no `--launch`, no `tools/hooks` edit. Read `docs/d1/ring-p5b.md` PD393 (lines 207-245) and `docs/script-writing.md`.

## Decision already taken (PD393(a), judgement 2026-10-10) - apply, do not ask
Between checkpoints the executor reuses its last real read (`tools/stagexec.py:2196-2198`). Ops 4 and 8 of the p5s02b plan (`delete_wire dw_go` / `dw_ho`) are not
checkpoints (`checkpoint_ops`, `:2143-2149`; the checkpoint-set validator at the Executor constructor / `run`, message `CHECKPOINT before op 1`), so ops 5 and 9
(`connect_term_uid`) still see w24264 / w24300 on their sinks. Decision: **every op of kind `delete_wire` is a required checkpoint**, same as add_sr / tunnel /
the last op / a move_in run's closing op. Not chosen: adding `connect_term_uid` to `RETRY_KINDS`.

## Do
1. Pin sweep FIRST (retrospective-cycle160 finding 1): list every self-test / maker / card input that pins the md5 of `tools/stagexec.py` (grep the 32-hex of the current file, `ddf23a31`),
   and every file that calls `checkpoint_ops`. Write the list into the facts file BEFORE the edit.
2. In `tools/stagexec.py`: `checkpoint_ops` adds every op whose kind is `delete_wire` (name the kind string as the compiled op list carries it - read `compile_plan`, do not guess);
   the Executor's checkpoint-set validator refuses a set lacking one, with an `ExecStop CHECKPOINT before op 1` message that names the delete_wire op(s) missing. Update the two docstrings that
   state the rule (`checkpoint_ops`, `Executor`). The validator must stay in ONE place; if the move_in-run rule and the new rule share structure, share the code (docs/script-writing.md).
3. Self-test `tools/bench/selftest_c161_delckpt.py` (header per CLAUDE.md `labview: none / hardware: none`), ALL quoted with counts:
   (i) on the p5s02b plan `tools/bench/plan_ring_p5s02b.json` (f4520b10) compiled ops: `checkpoint_ops` now includes ops 4 and 8; quote the set;
   (ii) the Executor (sim / dry backend as the existing c158 runcheck self-test builds it) built with the old p5s02b set WITHOUT op 4 is refused, WITHOUT op 8 is refused, with both is accepted;
   (iii) the stored p5s01a, p5s01b and p5s02a plans' checkpoint sets (the sets their recipes / preds carry): each validates unchanged, or each newly refused set is NAMED with the reason
        (a plan without any delete_wire op validates unchanged by construction; say which of the three have one).
4. Re-run the existing suites that exercise the executor checkpoints (`selftest_c158_runcheck.py`, `selftest_c157_innerface.py`, and every other self-test the pin sweep shows calling `checkpoint_ops` / constructing an Executor with a set)
   and quote pass/fail counts. A pre-existing pin that only drifts because stagexec.py's md5 changed is re-pinned (own-card files only) and reported; a computation failure is a FAIL - report it.
5. Report the new md5 of `tools/stagexec.py`. Do NOT touch `stagesim.py`, `stagekit.py`, `stage_prerun.py`, the plan, the pred, the licence, the EL or the recipes (card 161-a1-2 re-makes them).
6. A hook false positive on your own command text: `py tools/gate_fp.py log ...`, report; never edit a hook, no env bypass. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c161_a1_1_facts.md` (<= 35 lines, facts only)
pin-sweep list (before the edit); new stagexec md5; self-test (i)(ii)(iii) results quoted; suites re-run with counts; md5 UNCHANGED: stagesim 95a162ba, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10; `OPEN:` lines.
