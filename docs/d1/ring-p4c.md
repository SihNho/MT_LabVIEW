---
type: decision
kind: topic
status: current
date: 2026-10-08
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p4, tracking-loop, pre-decided]
---

# Ring buffer P4 (tracking loop 1.2), part c — decisions from 357 on

Continues `docs/d1/ring-p4b.md` (399 lines when this file was opened, at the 400-line cap; PD323–PD356 there stay in
force as listed in `docs/d1/INDEX.md`). Same scope: loop 1.2's reader, and P5/P6 until they get their own file.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

357. **(cycle 147 hand-back 2 judgement, 2026-10-08 — after `tools/bench/cards/handback_147_2.json`, results
     `result_147-b1-1.json` PASS, `result_147-b1-2.json` BLOCKED fp-55, `result_147-b1-3.json` FAIL)** USER-RULES: none apply
     (a test-stub and gate-scope decision; no design, no computation, no loop-coupling change).
     - **(a) Accepted:** PD356(c) done — the stored s06 retry end read re-scored with the 5-rename licence is D/TD/PB ALL PASS
       (`tools/bench/diag_c147_b1_1_rescore2.log:22-30`); w23807 = deleted + reused on source t5171, REUSE-NOTED (`:18-23`). PD356(b)
       done in `tools/stagekit.py` 06b8d844 (`selftest_c147_b1_2.log` 17/0; default call path verbatim == pre-edit, s03/s04/s05 verdicts
       unchanged). The stagekit edit is accepted; no further gate edit this cycle.
     - **(b) J1 in `selftest_stagekit.py` is judged a PRE-EXISTING stale stub, to be MEASURED, not assumed:** the failing call
       `stagekit.py:794 create_local_read` (since cycle 102) lies outside the 147-b1-2 diff (hunks from `:1371` only), and the case-J
       stub (`selftest_stagekit.py:330`) stubs only `diag_s3b_l0_localname_v2`. Discriminator = the prepared card
       `tools/bench/cards/task_147-b1-4.json` (pre-edit 9a3fceaf vs new 06b8d844, every COM function stubbed to raise, per-check
       compare). Same failing checks on both ⇒ pre-existing, proceed; any other difference ⇒ return.
     - **(c) Then fix the stub** (only `selftest_stagekit.py` case J: also stub `create_local_read`, no other line): a pure self-test
       must not reach LabVIEW (it made one COM call that LabVIEW answered with 5507 on 2026-10-08). After the fix, selftest_stagekit
       on the new stagekit = 0 fails AND 0 COM calls with COM blocked.
     - **(d) fp-55 is NOT a false positive:** `selftest_stagekit.py` imports stagekit → gscript, and case J did reach COM, so its
       `labview: read` header is true. Run these self-tests under `labview: read` cards; drain fp-55 as "not a false positive".
     - **(e) Opens closed:** #9503 9505/9508 'Value'→'' renames are licensed (already PD356(d)); PB keeps failing an unlisted
       rename even when cdiff is equal (PD356(b)); created-tunnel name changes (# FD / # DT points) stay with NG (it passed). Keep
       `rename_by_uid` in the licence beside `renames` (`tools/stage_prerun.py:1276` reads only that key).
     - **(f) Remainder unchanged:** PD356(d) licence `renames` (5) → s06 recipe wired to the new API
       (`stage_d1_ring_p4_s06v18.py:127` renames + bind; `:139-144` PB via `pb_rename_rows`) → py_compile + dry + prerun on final
       bytes → PD356(e) ONE scratch (new RETRY_CARD, new byte copy of s05 3f9ac26b, ops 1..21) → adopt by PD354(a) + `load_by_vi`.
