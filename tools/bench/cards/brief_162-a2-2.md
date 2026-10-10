---
card: 162-a2-2
status: current
date: 2026-10-10
---
# Brief 162-a2-2 - RETRY of 162-a2-1: re-pin ONE stale pin in selftest_c161_delckpt, drain fp-84 (offline, no LabVIEW)

Read `tools/bench/diag_c162_a2_1_facts.md` (md5 79a4e855c4a523a698fd92acb8c97974). Card 162-a2-1 drained fp-82 and fp-85, and returned on fp-84: `selftest_c161_delckpt.py` ran 10/1; D1, D2, V1-V5 and S PASS, only `P pins unchanged` FAILed on
`plan_ring_p5s02b_pred.json` a1fd43fb. That file is 4cef0a8c on purpose: card 162-a1-2 wrote the measured census into it (`diag_c162_a1_2_facts.md:39`, only the census keys changed, which is what cycle-162 pass item 7 required). So the pin is stale by a required change, not a defect.

## Steps
1. Confirm from the pin sweep log (`tools/bench/prep_c162_a2_1_pinsweep.log`) and a fresh hashlib read that the only unequal pin in `selftest_c161_delckpt.py` is `selftest_c161_delckpt.py:138` (pred a1fd43fb vs current 4cef0a8c). Confirm by JSON compare against `tools/bench/sim/ring_p5s02b_c162/pred_before_a1_2.json` that only `census`, `census_overall`, `census_source` differ (quote it).
2. Edit that ONE pin (Edit tool, one line, comment names card 162-a1-2). Re-run `selftest_c161_delckpt.py`: expect 11/0 with the same content gates. Any other result = RETURN with the facts.
3. `py tools/gate_fp.py drain --id fp-84 --fixed tools/stagexec.py:<line of the checkpoint rule, the facts say 2125 REREAD_KINDS - check it holds the delete_wire reread> --selftest selftest_c161_delckpt`. Quote the row before -> after.
4. Do NOT touch `selftest_c159_a4_1.py:300` (stale stagexec pin 7a712ccb): it is not in this card; list it as an OPEN line only. No other file edit.

Report `tools/bench/diag_c162_a2_2_facts.md` (<= 20 lines): the pin check, the JSON compare, the self-test counts, the drained row, md5 before -> after of the one edited file, `OPEN:` lines (measurements only).
