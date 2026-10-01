---
type: archive
date: 2026-10-01
tags: [status-relocation]
---
# STATUS.md relocation, cycle 126 (rule 4 — verbatim, nothing rewritten)

## §1 The CYCLE 123 brief (moved out of STATUS.md `## NEXT` when STATUS reached 119 lines)

- **CYCLE 123 in brief — P2b DELIVERED (the new bed); the image types match; P3 is designed; three tools built:**
  - 123-1 PASS 7/0: `claudeDev\D1_ring_p2b_20261001_140658.vi` md5 `652b1447…`. ONE launch 41/0; Error List 54 == pin; the expected file reverdicts OK (PD246(a)). Broken-file count: 1 of 6. All three `IMAQ Create` Image Type rings read 0, so the slot copy converts no pixels (PD246(b)).
  - 123-2 BLOCKED (offline): P3 facts and step list (`tools/bench/ring_p3_steps.md`). P3 is about 74 rows, and two routes were missing. The design is decided in PD246(c): flat-sequence order, local read-modify-write, initialised registers, `Equal?`, and the counter in the new-frame frame.
  - 123-3 PASS 6/0: a shift register's initial value can now come from a constant, built on existing ops (`gscript.sr_init_const`, route `const_sr`, donor `claudeDev\DonorSRInit_v0.vi`). Also measured: the `Equal?`/`Increment`/`Quotient & Remainder` donors, and the For exit gives an indexing tunnel (PD247).
  - 123-4 PASS 14/0 (offline) + 123-7 PASS 7/0: the census device from the violation decision of 2026-10-01 13:56 is BUILT.
    - Files: `tools/census_predict.py` + `tools/bench/census_samples.json`.
    - `stage_prerun --prerun` line X15 fails a declared class count that differs from the measured samples. An unmeasured count forces the scratch run. stagekit's dry-mode census line prints `UNVERIFIED-DRY`.
    - Cycle 122's +1 now fails offline; P2b's prerun passes 14/0.
  - 123-5 FAIL 12/1 → 123-7 PASS: the case creator with a wired selector (`gscript.case_wired`, route `case_wired`, donor `claudeDev\DonorCase_v0.vi`) works and can be used in plans. The FAIL was a wire-count gate on a branch (review `archive/peer/2026-10-01-c123-5-s1a-branch.md`, ACCEPTED). The Flat Sequence creator is NOT built (PD248(c)).
  - 123-6 PASS 5/0: STATUS.md 601 → 95 lines; the history is VERBATIM in `archive/2026-10-01-status-cycle123-relocate.md`.
  - 123-8 FAIL 1/1: the real P2b graph is read (`tools/bench/graph_ring_p2b_20261001_154542.json`; BufNum is I32) and the P3a plan input has 25 actions. Its stagesim check failed on a TOOL GAP: the counter's pass-through wire in the case's True frame cannot be written in the plan format. Decided in PD249(c): keep the design and build the tool, because P4 needs it too.
  - 123-9 FAIL 13/1 (a time-boxed tool card): input and output tunnels on the case were measured (`Is Broken?` False), but no existing function reaches a tunnel's inner face in a given frame. Decided in PD249(f): build that op (P4 needs it too) rather than redesign the counter. No code was half-changed (the code step was not started).
  - Carries:
    - `docs/d1-build-plan.md` is still `status: current` (lint L5);
    - `decisions_pending.json` item 13 (D-2026-09-28-01, the chat's) still breaks the 300-character limit;
    - cycle 122's carries: stagekit donor declaration, `_check_units`, the reverse direction of RULE-OFFLINE-CARD, `requires` for routes/donors, fp-10.
  - **User decision open: D-2026-10-01-01** (the 6-file limit vs 15–25 rows per step). Recommendation: keep 6 and allow ~40 rows per step for P3b/P4, each with a full scratch run.
