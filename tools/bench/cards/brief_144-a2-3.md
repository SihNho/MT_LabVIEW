---
type: brief
status: current
date: 2026-10-07
---
# Brief 144-a2-3 - TOOLING, run ALONE: fp-34 guard_peer carve-out + stop-record replay (cycle 144 round 2)

The purpose names `tools/hooks/guard_peer.py` as an authorised edit for this card (user rule: a hooks edit is allowed only
because the purpose names it). No LabVIEW card is live; none may start beside this one.

## 1. fp-34 - the carve-out (exact edit, from `tools/bench/diag_c144_3_facts.md`)
In `tools/hooks/guard_peer.py` `log_failure`, after the rc 0/1/2 carve-outs (about line 188) and before
`return bool(v["failed"]) ...` (about line 189), insert the block in `diag_c144_3_facts.md` (section fp-34):
rc 3 + no RESULT line + the command contains `stage_prerun.py --scratch-required` + a `SCRATCH-REQUIRED | ` line in the
log segment => `return False, None` (a decision, not a failed prediction). Re-read the file around those lines first and
keep the variable names the file really uses. Nothing else in the file changes.
Self-test (new file `tools/bench/selftest_guard_peer_scrreq_c144.py`, <= 120 lines, offline): (a) the real log
`tools/bench/prep_c140_2_scrreq_r3.log` is NOT a failure; (b) rc 3 WITHOUT the SCRATCH-REQUIRED line still failed;
(c) rc 3 of another command still failed; (d) rc 1 / rc 2 behaviour unchanged. Then
`py tools/gate_fp.py drain --id fp-34 --fixed tools/hooks/guard_peer.py:<line> --selftest <name>`; quote the PASS lines.

## 2. stop_record classifier
Replay the classifier of `tools/stop_record.py` on the two commands logged at `tools/hooks/material_marker.log:3332` and
`:3333` (read the full lines). Report for each: refused or not, and the rule that decided. Pass: neither is refused, and a
real recipe launch (e.g. `py tools/bgrun.py ... -- py -u tools/recipes/stage_d1_ring_p4_s04v18_scratch.py`) is still
refused/marked as before. If one of the two IS refused: fix `tools/stop_record.py` in this card, with a self-test of the
two commands plus the recipe launch (3 cases), and report the line. A classifier edit must not widen what a recipe launch
is allowed to do.

## Never
edit `docs/**`, STATUS.md, CLAUDE.md, any other hook, `tools/stage_prerun.py` or another stage tool; touch LabVIEW; run a
recipe. Facts -> `tools/bench/diag_c144_a2_3_facts.md`. Return at the first unexpected result.
