---
card: 151-a3-4
status: current
date: 2026-10-09
---
# Brief 151-a3-4 - drain gate false positive fp-61 (errorlist_check count_read) + dry/prerun re-run; OFFLINE

OFFLINE, no LabVIEW. `tools/bench/gate_fp_queue.jsonl` line 61 (id fp-61, gate `checker:errorlist_check:count_read`, cause: comtypes / OCR engine missing in the Python env at the time of card 148-a2-4; log `diag_c148_a2_4_el.log`). Purpose item: drain ONLY fp-61 as a measured drain; leave fp-62..70 open.

Steps:
1. Read fp-61 and `tools/gate_fp.py` (`drain --id ID --fixed FIXED --selftest SELFTEST`). Establish by MEASUREMENT whether the cause is gone: `py -c "import comtypes, rapidocr_onnxruntime"` (no LabVIEW), and the errorlist_check self-test / dry mode that does not touch LabVIEW (read `tools/errorlist_check.py --help`; do NOT run its LabVIEW-reading path). Save the output to `tools/bench/diag_c151_a3_4_selftest.log`.
2. If the measurement shows the cause is fixed: `py tools/gate_fp.py drain --id fp-61 --fixed "<what fixed it, measured>" --selftest tools/bench/diag_c151_a3_4_selftest.log`. If it does NOT: do not drain; install nothing, edit no tool; report the missing module and RETURN with facts.
3. Re-run, with bgrun as the hooks require, the s08 scratch recipe's `--dry` and `--prerun` (`tools/recipes/stage_d1_ring_p4_s08v18_scratch.py`; last session: dry 1/0, prerun 16/0, X10 651.6) - these are offline modes. NEVER `--launch`. If the adopted-scratch launch gate refuses the command text, do not route around it: quote the refusal and RETURN (the chat owns hook false positives).
4. Show fp-62..70 still `open` (`py tools/gate_fp.py list`).
5. Invariants md5 before = after: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, errorlist_check 2b466a89, elrule a5ee7d5c, s07 b3f86b32, s08 f99e8414; no tools/hooks edit; tasklist LabVIEW count 0.

Report `tools/bench/diag_c151_a3_4_facts.md` (<= 30 lines): measurement, drain command + rc (or why not), dry/prerun numbers, fp-62..70 status, invariants, `OPEN:` line. Facts only.
