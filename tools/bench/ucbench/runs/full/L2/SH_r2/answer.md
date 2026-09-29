I found 24 citations in the active docs that point to files that don't exist. I scanned `CLAUDE.md`, `STATUS.md` and all 71 `docs/*.md` files with a read-only script using the stated rules, and spot-checked several of the hits with Glob/Grep.

CLAIM 1: CLAUDE.md cites `.claude/agents/reporter.md`, which does not exist (only bench-*, log-reader, material and motor-limit-checker agent files are present) | EVIDENCE: CLAUDE.md:318
CLAIM 2: docs/cycle14-plan.md cites missing `tools/recipes/build_opflatseqdiagrams_v0.py` | EVIDENCE: docs/cycle14-plan.md:95
CLAIM 3: docs/cycle14-plan.md cites missing `tools/bench/opflatseqdiagrams_labels.json` | EVIDENCE: docs/cycle14-plan.md:106
CLAIM 4: docs/cycle14-plan.md cites missing `tools/recipes/build_opflatseqdiagrams_v0.py` | EVIDENCE: docs/cycle14-plan.md:168
CLAIM 5: docs/cycle14-plan.md cites missing `tools/bench/build_opflatseqdiagrams_v0.log` | EVIDENCE: docs/cycle14-plan.md:169
CLAIM 6: docs/cycle14-plan.md cites missing `tools/bench/opflatseqdiagrams_labels.json` | EVIDENCE: docs/cycle14-plan.md:169
CLAIM 7: docs/cycle14-plan.md cites missing `tools/bench/diag_a3_complete.py` | EVIDENCE: docs/cycle14-plan.md:170
CLAIM 8: docs/cycle14-plan.md cites missing `tools/bench/diag_a3_complete.log` | EVIDENCE: docs/cycle14-plan.md:171
CLAIM 9: docs/cycle14-plan.md cites missing `tools/bench/frame_loop_a4.json` | EVIDENCE: docs/cycle14-plan.md:171
CLAIM 10: docs/cycle27-plan.md cites missing `tools/bench/s2a_legality.json` | EVIDENCE: docs/cycle27-plan.md:705
CLAIM 11: docs/cycle27-plan.md cites missing `tools/bench/s2a_legality.json` | EVIDENCE: docs/cycle27-plan.md:799
CLAIM 12: docs/cycle27-plan.md cites missing `tools/bench/s2a_legality.json` | EVIDENCE: docs/cycle27-plan.md:829
CLAIM 13: docs/cycle27-plan.md cites missing `tools/bench/s2a_legality.json` | EVIDENCE: docs/cycle27-plan.md:870
CLAIM 14: docs/d1-build-plan.md cites missing `archive/peer/2026-09-17-priorart-d1-build-rev4.md` | EVIDENCE: docs/d1-build-plan.md:45
CLAIM 15: docs/d1-loop12-17-split-plan.md cites missing `docs/wiki/subvi/D1_s3_loop15.json` | EVIDENCE: docs/d1-loop12-17-split-plan.md:62
CLAIM 16: docs/d1-route-b-plan.md cites missing `tools/recipes/build_d1_route_b.py` | EVIDENCE: docs/d1-route-b-plan.md:391
CLAIM 17: docs/m3a1-severed-rows.md cites missing `tools/bench/m3a1_severed_arith.json` | EVIDENCE: docs/m3a1-severed-rows.md:87
CLAIM 18: docs/m3a1-severed-rows.md cites missing `tools/bench/m3a1_severed_rows.log` | EVIDENCE: docs/m3a1-severed-rows.md:89
CLAIM 19: docs/m8-real-run-plan.md cites missing `tools/bench/m8_run1.log` | EVIDENCE: docs/m8-real-run-plan.md:43
CLAIM 20: docs/m8-real-run-plan.md cites missing `tools/bench/m8_run1.json` | EVIDENCE: docs/m8-real-run-plan.md:46
CLAIM 21: docs/m8-real-run-plan.md cites missing `tools/bench/m8_numbers.log` | EVIDENCE: docs/m8-real-run-plan.md:48
CLAIM 22: docs/motor-limit-assurance-plan.md cites missing `tools/bench/selftest_motor_gate.py` (only `selftest_motor_gate2.py` and the `.log` exist) | EVIDENCE: docs/motor-limit-assurance-plan.md:105
CLAIM 23: docs/session-protocol.md cites missing `tools/bench/steer_state.json` | EVIDENCE: docs/session-protocol.md:167
CLAIM 24: docs/t0-instrumentation-plan.md cites missing `docs/per-frame-path.md` | EVIDENCE: docs/t0-instrumentation-plan.md:38
CLAIMS: 24