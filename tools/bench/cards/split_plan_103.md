---
title: display-stage split plan (PD215(b)) - Part A ops 1-40 / Part B ops 41-47
date: 2026-09-27
card: task_103-1.json
source: docs/d1-loop12-17-split-plan.md:1817-1821 (PD215(b))
status: plan
---
# Display stage split — cycle 103 (one page)

**AMENDED 2026-09-27 (card 103-3, PD216(f)): Part A = ops 1–33 → `claudeDev\D1_s1_dispA_<ts>.vi`; Part B = ops 34–47 from that file in a fresh LabVIEW.** ~~Part A = ops 1–40 / Part B = ops 41–47~~ (r1 MEMSTOP 703.8 MB at the op-40 read, `tools/bench/stage_d1_dispA_r1.log:799`; text below kept as written).

**Why split.** Run r7 (`tools/bench/stage_d1_disp_r7.log`) executed ops 1–40 of 47 at step-diff 0 (k12 WARN only)
and stopped IN op 41 (`r7_wait` through `stagekit.copy_in`, MOVE_DST-only). Private memory at op 40 was 690.4 MB
against MEMSTOP 700 (`r7.log:804`); ops 41–47 carry 6 more required reads, so one LabVIEW session cannot finish the
stage. CLAUDE.md "Big or blocked work is SPLIT …": each part saves a file, the next part starts from that file.

**Input (both parts' anchor):** `claudeDev\D1_s1_copy.vi` (md5 pinned by `plan_disp.json` `finalized.base`),
never modified. Rows come only from `tools/bench/sim/disp/plan_disp.json` (FINAL, 21 open rows).

| step | what | saved file | pass criterion |
|---|---|---|---|
| 0 (this card, offline) | Wait (ms) donor byte-copied from an NI example into `claudeDev\OpWaitDonor_v0.vi`, node uid/class/diagram/terminals MEASURED, md5 pinned, registered in `facts_c100_oplabels.json` `OpPrimCopyNested_v0.donors["Wait (ms)"]`; `r7_wait` row → `"prim": "Wait (ms)"` (route `create_primitive_nested`); re-sim FINAL, re-dry, `stage_prerun` | `OpWaitDonor_v0.vi`, `facts_c103_donor.json`, `plan_disp.json` (new md5) | donor node found and 2 terminals read (1 sink `milliseconds to wait`, 1 source `millisecond timer value`); re-sim same 21 open rows, 0 unclassified; dry 0 unroutable; pre-run all PASS; `protocol.py requires` green |
| A (card 103-2, one LabVIEW session) | `stage_d1_disp.py --stop-after 40`: fresh LabVIEW, copy of S1, ops 1–40 exactly as r7 (checkpoints = binding ops ∪ {4, 5, 12, 40}); after op 40 the real read is compared with simulated step 40; NO op > 40 is dispatched | `claudeDev\D1_s1_dispA_<ts>.vi` via `gui_save` (`-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"`; broken by design — rows 41–47 missing; never run, never cold-loaded) | E1 through op 40 with WARN-class diffs only (`stagexec.classify_step_diff`); step-40 real == sim; artefact md5 recorded; binding after op 40 (`bind.obj/term/diag`, `sym_real`, `loop_of`) written to `tools/bench/stage_d1_dispA.json`; S1 md5 unchanged; LabVIEW gone at exit |
| B (later card, fresh LabVIEW) | `stagexec` `--from-step 40` entry: load `D1_s1_dispA_<ts>.vi` (memory baseline = one VI load), bind Part A's recorded uids from its JSON instead of re-executing, verify the real read == simulated step 40, then ops 41–47 | `claudeDev\D1_s1_disp_<ts>.vi` saved BY SCRIPT at ExecState 1 | base read == step 40 (bound); E1 ops 41–47 warns only; W1 RBW removes pre-existing uids only, no lost edge; E2 ExecState 1; E3 cdiff == the 21 PD213(d) open rows + added objects; `#25261` gate False; PS md5 ≠ input |

**Not in this plan (PD215(b)):** `stagekit.copy_in` is not used or changed; the S1 file is not a donor (+≈300 MB under
the same ceiling). Part B's `--from-step` entry is built only if card 103-1's budget allows; it is not a pass line.

**Risks named up front.** (1) The dispA file is broken by design → `gui_save` is the only save route
(`stagekit.save_route`), and the saved file must never be opened headless cold (recompile spin). (2) Part B binds uids
recorded in a different LabVIEW session; uids persist in the saved file, so the step-40 compare at Part B's start is
the check. (3) The memory ceiling's cause (reads vs accumulation) is still unmeasured; Part A's meter lines at 26–40
repeat r7's and Part B's give the fresh-session data point.
