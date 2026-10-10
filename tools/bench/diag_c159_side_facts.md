---
type: facts
status: current
date: 2026-10-10
card: 159-a2-1
---
# Card 159-a2-1 - cause lines of two cycle-158 oddities (offline, read-only)

## 1. diag_c158_a2_3_probe - TypeError
- log: `tools/bench/diag_c158_a2_3_probe.log:48` `TypeError: result_line() takes 1 positional argument but 3 were given` (call quoted at :47; BGRUN END rc=1 at :50).
- cause: `tools/bench/diag_c158_a2_3_probe.py:39` - `protocol.result_line("PASS", 1, 0)` passes three positionals; `tools/protocol.py:285` is `def result_line(d)` (one dict); the (n_pass, n_fail) form belongs to `make_result` at `tools/protocol.py:302`.
- validity: every measurement print ran before line 39 (`diag_c158_a2_3_probe.log:3-43`: step/state keys, base, open_rows 27, real_end_rows 6143, 8 bound ops) - the probe's output is valid; only its RESULT line is lost, and the wrapper's line `:49` records FAIL 0/1 for it. The follow-on `diag_c158_a2_3_measure.py:205` uses the correct dict form.
- affects: the probe log reads as a failing run (rc=1, RESULT FAIL) for guard_peer / audit counting; no measurement depends on it.
- repair (outside this card's write flags): `tools/bench/diag_c158_a2_3_probe.py:39` -> `protocol.result_line(protocol.make_result(1, 0))`.

## 2. diag_c158_a3_2_pascope - "no scope"
- log: `tools/bench/diag_c158_a3_2_pascope.log:3` `null`, `:4` RESULT FAIL `first_fail "no scope"`.
- printing code: `tools/bench/diag_c158_a3_2_pascope.py:17-18` maps a falsy `priorart_diff.scope(...)` to FAIL "no scope".
- cause: `tools/priorart_diff.py:116-117` returns None because `sibling()` (`:74-87`) found no APPROVED file with the same digit-masked name `stage_d#_ring_p#s##a_scratch.py`. The only candidate in tools/recipes is `stage_d1_ring_p5s01a_scratch.py`; `tools/bench/stop_records.json` has no record for it (p5s01 entries at `:1847/:1860` are the non-scratch `stage_d1_ring_p5s01a.py`, `:1873` is p5s01b), so `approved()` (`:59-71`) is False.
- class: by design (`tools/priorart_diff.py:20` "No sibling -> None: the full review rule applies unchanged"); the script's PREDICTION (`diag_c158_a3_2_pascope.py:6` "a sibling is found") was wrong and its FAIL mapping turns a legitimate None into a failing log. Not a missing input, not a gate refusal.
- affects: a full prior-art review was owed for the scratch recipe (taken: record `tools/bench/stop_records.json:1910-1920`, released novel 2026-10-09T17:29Z, after the 02:25 local run); the pascope log counts as a failing run.
- repair (outside this card's write flags): `tools/bench/diag_c158_a3_2_pascope.py:17-18` could report None as PASS with a "no sibling" fact; whether to is judgement.

Neither is a gate false positive (no gate refused a correct input); nothing logged to gate_fp_queue.jsonl.
OPEN: should a diagnostic whose only fault is its own RESULT line (probe :39) or a None-means-FAIL mapping (pascope :17) be excluded from failing-log counts, or the scripts patched?
