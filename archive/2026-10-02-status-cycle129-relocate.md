---
type: archive
date: 2026-10-02
tags: [status-relocation]
---

# STATUS.md text relocated VERBATIM by the cycle-129 judgement session (rule 4: never rewritten, only moved)

## §1 — the cycle 126, 125 and 124 briefs (were STATUS.md `## NEXT` lines 71–91)

- **CYCLE 126 in brief — the hygiene runner is built, Flat Sequence creation works and is in the plan format, the stub wire can be removed, and every P3b crossing kind is measured:**
  - 126-1 PASS 38/0: `gscript.hygiene_run` built (the repeated-failure-class device); `OpFsAddFrame_v0` hygiene PASS (closed-state handles max dev 7 — 125-5's +116 was the never-closed copies); 3-frame FS scratch 15/0.
  - 126-3 PASS 13/0 (offline): FS routes and models; 126-1's "one-terminal wire" is the normal FS tunnel graph shape, not a stub.
  - 126-2 FAIL 3/1 → 126-4 FAIL 13/1: both FAILs were our own gates (method-name literal; OCR'd Error List keys `subvi`/`subvl` — a variant already in 161 recorded Error List files). 126-5's FAIL was the known duplicate-row case that `V.dedupe_rows` has handled since 2026-09-24. Three one-off diagnostics broke the 120-line rule (retrospective cycle 126, `VIOLATION: none`). Measured: `RemoveLooseEnds` on w27378 clears the loose end, `Is Broken?` True → False, terminals kept, Error List 55 → 54 (PD255(a)).
  - 126-6 PASS 48/0: case frame → FS frame, branch to another frame, BufNum / While `i` / pool For exit → FS frame — all by `connect_term_uid`; While-border array tunnel non-indexed (rule 1a holds). Census samples recorded.
  - 126-5 FAIL → 126-7 FAIL → 126-8 PASS 18/0 (offline): P3b plan input written (45 actions + 2 released rows + 14 loose-end removal rows). Rule-1a check: in the ORIGINAL, `#30117`/`#4580` Value feed the per-frame record `#2626` → `save trace.vi`, so PD238(c) holds; `#4580`'s sink was opened by design at L2-B1 (PD257(a)).
  - Carries: `docs/NAMES.md` lacks the measured Wire method ids (`6370C05` CleanUpWire, `6370C08` RemoveLooseEnds, `6370C0B` DeleteJoint, `6370C0D` DisconnectTerminal — `diag_c126_2_op.log:8-16`) and the FS methods; `errorlist_check.py` `norm()` OCR aliases (`vl`↔`vi`); `selftest_fs_c126.py` not in `protocol.OFFLINE_SELFTESTS`; `diag_c126_2_fs.py` still calls the old `g.wire_cleanup` name (superseded by `diag_c126_4_fs.py`).
- **CYCLE 125 in brief — gates cleaned, the 55th item traced, both Flat Sequence ops built (one awaits a hygiene rerun):**
  - 125-1 PASS 38/0: gate false positives fp-10..fp-13 drained (`guard_peer.py:946` RULE-OFFLINE-CMD; `protocol.py:398` OFFLINE_SELFTESTS). New prerun check X16 (`stage_prerun.py:1904`).
  - 125-3 PASS 5/0: the review `archive/peer/2026-10-01-c125-1-x16-hyp.md` showed X16 wrongly refused constants (their class equals the simulator's default); X16 now skips constants (fp-14 drained).
  - 125-2 FAIL 13/1: the real P3a graph is read (`tools/bench/graph_ring_p3a_20261001_190155.json`). My "exactly one new loose wire" prediction failed: terminal counts cannot see the item (review `…c125-2-loose-hyp.md`).
  - 125-4 FAIL 3/3: the 55th item is `w27378`, one dangling segment end left by P3a's `connect_term_uid` row across the case border (`diag_c125_joints.log:26,39`). FlatSequence `Add Frame` = method `3578B800`.
  - 125-5 FAIL 22/2: `OpFsDiagrams_v0` hygiene PASS; `OpFsAddFrame_v0` works but its hygiene failed on handles (+116, the test never closed its copies). The stub did not reproduce on a minimal scratch VI (PD253(d)).
  - Carries: `c125_1_regress.py`'s glob catches three P2b companion files that are not final plans (X1 fail, expected); a card that edits `stagexec.py`/`stagekit.py`/a listed self-test reruns `tools/bench/c125_1_offline_measure.py` (PD252(a)); `diag_c125_5_opfs.py` is 203 lines (one-off).
- **CYCLE 124 in brief — P3a DELIVERED (the new bed); the case-tunnel tools built:**
  - 124-8 PASS 5/0: `claudeDev\D1_ring_p3a_20261001_180540.vi` md5 `4dfa44aa…`. Scratch 22/0, ONE launch 22/0, census == prediction; Error List 55 == pin (54 + 1 new `Wire has loose ends`, the plan's alternative); expected file `tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json` reverdicts OK. STRUCTURAL, ExecState 0 by design, never run. Broken-file count: 2 of 6.
  - 124-7 FAIL 10/2: the scratch stopped at op 1, because the plan left created-node `term_class` undeclared (the simulator said `Terminal`, LabVIEW said `ParameterTerminal`). Fixed in the plan by 124-8; the review kept the cause.
  - 124-5 PASS 25/0: the new op passed its 2,000-call hygiene check. P3a's counter was proven on a scratch: register ↔ case crossings by `connect_term_uid`, the True-frame pass-through, and a second sink that LabVIEW branches.
  - 124-1 / 124-4 FAIL: two bugs in our own build script (an owner check on the top-level diagram, and the op called outside `hygiene_probe`). Both fixed.
  - 124-2 BLOCKED (gate false-positive fp-12) / 124-3 FAIL: the plan-format `frame` field was built. 124-3 found the real gap was the register crossing, which 124-5 closed.
  - Carries: gate false-positives fp-10..fp-13 queued (fp-12/13: census hook-in and stagexec self-tests refused under `labview: none`); the cycle-123 carries below still stand.

## §2 — the cycle-129 FIRST ACT block (were STATUS.md `## NEXT` lines 56–58; superseded by cycle 129's close)

🟢🟢 **FIRST ACT of cycle 129 = build ring step P3b-1 — `docs/d1-loop12-17-split-plan.md` Pre-decided 263(b) (read 261–263).** Pipeline:
   - Card 1 (offline, first): split `tools/bench/plan_ring_p3b_in.json` (md5 `08fa2241…`, 70 actions, replays end to end) into `plan_ring_p3b1.json` / `plan_ring_p3b2.json`, each ≤ 40 actions (user D-2026-10-01-01 = ANSWERED option 1), dependency-closed, IMAQ Copy + the U9 guard (Unbundler `element#0` → Select) in the same half, RLE rows with their loose ends; finalize, predictions, recipes `stage_d1_ring_p3b1.py`/`_p3b2.py`; dry + prerun OUT OF PROCESS; `--scratch-required`; prior-art for P3b-1 (new classes Unbundler, Select). Also: c106e E1 rerun listing every FAIL line, then drain fp-19. ⚠️ `plan_ring_p3b.json` (4003eaa5), its `_pred` and `stage_d1_ring_p3b.py` are STALE — never launch them.
   - Card 2 (LabVIEW, after card 1 PASS): P3b-1 FULL scratch run on a P3a byte copy (prediction: Unbundler's bound output reads back `status` after its wire), ONE Error List read, then ONE launch → `claudeDev\D1_ring_p3b1_*.vi`. Broken-file count becomes 3 of 6; P3b-2, P4, P5 then use 4–6 and P6 must RUN (no slack for another split without asking the user, PD261(d)).
