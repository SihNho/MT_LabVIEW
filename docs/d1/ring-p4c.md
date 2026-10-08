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

358. **(cycle 148 judgement, 2026-10-08 — after `tools/bench/cards/assign_result_147_3.json` HANDBACK b-same-class-twice, results
     `result_147-b1-4.json` PASS, `result_147-c3-1.json` BLOCKED fp-56, `result_147-c3-2.json` PASS, `result_147-c3-3.json` BLOCKED fp-59)**
     USER-RULES: none apply (gate scope, a test pin and the order of an already-decided build; no design, no computation change).
     - **(a) Accepted:** cycle-147 purpose items 0–6. Case-J stub fixed (`selftest_stagekit.py` 29df9b64, COM blocked 51/0, 0 COM calls,
       `tools/bench/diag_c147_c3_1_facts.md:18`); licence `renames` = the 5 measured keys (licence 7f70bbf9); build recipe on the new gate
       API (d947df5d), both s06 recipes dry 1/0 + prerun 16/0 on final bytes, stored s06 read D/TD/PB ALL PASS
       (`tools/bench/diag_c147_c3_2_facts.md:21-26`). The s06 scratch was never launched; no LabVIEW ran in round 3.
     - **(b) Two gate refusals of one class stopped the round, so the gate-fp queue (fp-51..59, DUE) is drained FIRST, by ONE tooling card
       run ALONE.** Authorised edits: `tools/stage_prerun.py` (fp-56: re-pin `VI_MOD_EXEMPT_PATHS` for `selftest_stagekit.py` to its
       current sha256 0007d034…, and `--dry` must not read a self-test's intentional FAIL rows as DRY FAIL, or the test is routed by its
       header instead), `tools/hooks/guard_cycle.py` (fp-59: re-run exemption log glob), and the other hooks/checkers named by fp-51..58.
       fp-55 is drained as NOT a false positive (PD357(d)). Each entry ends `drained` with a fix + self-test or with a cited
       not-a-false-positive note; every edited hook keeps its existing self-tests green.
     - **(c) The s06 launch does NOT rely on fp-59's fix:** the scratch recipe's gate code changed after the last prior-art review
       (newest `2026-10-03-priorart-c143-p2-p4s03v18.md`), so the DIFF-ONLY prior-art review of its changed lines is owed and is PAID
       (card `flags.peers` includes `priorart`). Any verdict other than `novel` is released only by `REFUTED:`/`FIXED:` in the review file.
     - **(d) Re-pin `tools/bench/selftest_c147_b1_2.py` P0** to the current licence 7f70bbf9 and build recipe d947df5d (the old pins were
       stale by design after 147-c3-2); its 17/0 stays.
     - **(e) Then the PD356(e) scratch as decided:** ONE run, new byte copy of s05 3f9ac26b, ops 1..21 from the start → adopt by PD354(a),
       full final EL, fresh load + graph read, `load_by_vi` only. A new cycle resets the per-cycle retry count; a RETRY_CARD is used only if
       `stage_prerun` asks for one.
     - **(f) Pipeline:** beside the s06 LabVIEW card, ONE offline prep card for P4 session 7 (v18 ops after s06's last op), provisional on
       stagesim's end of s06, X10 at the s06 predicted load, dry + prerun PASS; after s06 is adopted, `--rebase` on the real s06 graph read
       and dry + prerun again. No s07 launch this cycle.

359. **(cycle 148 hand-back 1 judgement, 2026-10-08 — after `tools/bench/cards/handback_148_1.json` (c-outside-purpose, card "p1s-A"),
     `assign_result_148_1.json`, `result_148-a1-1.json` FAIL 3/3, `tools/bench/diag_c148_a1_1_facts.md`)**
     USER-RULES: none apply (test/gate hygiene and test pins; no design, no computation change).
     - **(a) Accepted:** fp-51..54, 56..59 drained with fixes + self-tests that fail on HEAD; fp-55 closed as not a FP (facts :9-17).
       **fp-56's pin is 5708c2d6…, not PD358(b)'s 0007d034…:** `stage_prerun.sha256` hashes the file WITHOUT its scope header
       (`stage_prerun.py:138-148`), so the raw-file sha never matches; the gate's own canonical form is right, PD358(b)'s number was not.
     - **(b) The hand-back is a false positive (fp-60), and the cause is a self-test, not a card:** "p1s-A" is a fixture of
       `tools/bench/selftest_chat_p1.py:113`, run by 148-a1-1's run-all. Working cause, MEASURED FIRST: the self-test calls
       `guard_session.py` as a subprocess with the parent's environment, so inside an assignment session `ASSIGN_STATE` (and
       `CYCLE_ROLE`/`CYCLE_SESSION`) reach `guard_assign`, which judged the fixture against the live purpose and wrote the hand-back into
       the LIVE state (`tools/bench/assign/state_148_1.json:45-50`; the same leak hit livebench A13K, cycle 144 round 3). Discriminating
       test: run the self-test with `ASSIGN_STATE` pointing at a throwaway COPY of a state file — a hand-back written there confirms; none
       written = return with the facts. Fix, authorised: every `tools/bench/selftest_*.py` that spawns `guard_session.py`/`guard_assign.py`
       drops those env vars for the child (census by grep), AND `tools/hooks/guard_assign.py` writes a hand-back only for a card file under
       `tools/bench/cards/` (any other path is logged and ignored). A new self-test reproduces the leak, FAILS on HEAD, passes after;
       existing guard_assign/guard_session/chat_p1 self-tests stay green. fp-60 ends `drained`. This card runs ALONE (it edits hooks).
     - **(c) T0b is a stale premise, like P0:** `selftest_c147_b1_2.py:123` asserts "licence without renames"; licence 7f70bbf9 has the 5
       measured renames by PD357/PD358(a). Authorised: edit T0b to the current licence (expects the 5 rename keys) → 17/0. PD358(d)'s
       "no other line" is amended to "P0 and T0b only".
     - **(d) "Existing self-tests green" means rc 0, OR the same counts as on the pre-fix HEAD blobs** (pre-existing failures are not
       regressions: c125_1 16/4, c133_1_fsroutes, fn_f2 35/1, rebase_uidreuse_c143_4, stage_prerun_c106e 14/1 — facts :24). What is still
       unmeasured runs in prepared card `task_148-a1-2.json` (no edits, `labview: read`), AFTER (b): the plain `selftest_stagekit.py` run,
       the 7 x10 self-tests, t3_regress and the four suites that timed out at 240 s (timeout ≥ 15 min each), each compared with pre-fix.
       A NEW difference from pre-fix on an edited module is a return, not a fix inside that card.
     - **(e) Then PD358(c), (e), (f) unchanged:** DIFF-ONLY prior-art review of the s06 scratch recipe (paid) → ONE s06 scratch on a new
       byte copy of s05 3f9ac26b → adopt + `load_by_vi` → s07 offline prep beside it, rebased after adoption, not launched.

360. **(cycle 148 hand-back 2 judgement, 2026-10-08 — after `tools/bench/cards/handback_148_2.json` (a-unexplained-after-retry, card
     148-a2-3), `assign_result_148_2.json`, `result_148-a2-3.json` FAIL, `tools/bench/diag_c148_a1_2_facts.md`, `diag_c148_a2_3_facts.md`)**
     USER-RULES: none apply (test measurement and order of an already-decided build; no design, no computation change).
     - **(a) Accepted:** round-2 items 0–3 and 5: fp-60 fixed (guard_assign bbaa2325, new self-test fails on HEAD, passes after),
       T0b re-pinned 17/0, s06 prior art ANSWERED `novel`. From 148-a1-2: plain selftest_stagekit 51/0, the 7 x10 self-tests all rc 0.
       **t3_regress 7/3 is accepted as PRE-EXISTING:** the review `archive/peer/2026-10-08-c148-a2-3-t3regress-prefix.md` (claim STANDS)
       shows the same 7/3 with the same three failing children recorded before any cycle-148 edit (`selftest_t5_regress.log:1,15`).
       Its correction holds: `diag_c148_a1_1_facts.md:24` is wrong for E1 (that "pre-fix" run spawned the edited stage_prerun).
     - **(b) The 148-a2-3 crash is OUR SCRIPT'S BUG, not a regression signal:** `diag_c148_a2_3_suites.py:79` ran `git worktree add`
       with its rc and stderr discarded, and `:81` then read a file from the empty tree. No suite ran, so nothing was measured either way.
       **Retry ONCE as the FIRST card, ALONE (no LabVIEW process alive), so that a passing log supersedes the failing one before the s06
       launch is gated:** a fixed wrapper (every git/subprocess rc checked, stderr printed, stop at the first failed step). The pre-fix tree
       is HEAD 07202624 exported into %TEMP% (by `git worktree add` or `git archive HEAD`; the card chooses), with its PRE md5s quoted. It runs
       the four suites that timed out at 240 s (c134_1_a4, c134_2_regress, c_e3_suite, f2_suite; timeout ≥ 15 min each) NOW and on the
       pre-fix tree. "Green" = rc 0, or the same failing children as pre-fix. A NEW difference is a return, not a fix. Stale temp worktrees
       `Temp/e3head_r96iqm4t`, `Temp/f2head_1n3cihvt` and the empty `Temp/c148a23head_*` are removed (`git worktree remove --force` /
       `prune`). The main tree and the `V6_bench\*` worktrees are not touched.
     - **(c) The masking risk (review 2(b)) is MEASURED in the same card, by the review's own test:** a new `tools/bench/diag_c148_a2_3_unmask.py`
       copies `plan_ring_p3b2.json` and `plan_ring_p4_s03v18.json` into %TEMP% with their provisional base restored (`finalized.plan_in`,
       e.g. `plan_ring_p4_s03v18.json:335-337`), runs `SP.rebase` on the copies with the HEAD `stage_prerun` and with the disk copy, and does
       the same for the c106e recipe with X17 skipped. Its output is the per-gate comparison. Equal output closes 2(b); any difference is a return.
     - **(d) Then PD358(e)/(f) as prepared:** the s06 scratch card `tools/bench/cards/task_148-a2-4.json` (re-validated; md5s refreshed only
       where a bench file changed), ONE run → adopt + `load_by_vi`. Beside it, the s07 offline prep, `--rebase`d on the real s06 graph after
       adoption, dry + prerun PASS, not launched. The s07 rebase also exercises the edited provisional-rebase path (`stage_prerun.py:4243`) on
       a live plan.

362. **(cycle 149 hand-back 1 judgement, 2026-10-08 — after `tools/bench/cards/handback_149_1.json` (a-unexplained-after-retry,
     card 149-a1-2), `assign_result_149_1.json`, `result_149-a1-2.json` FAIL 2/1, `tools/bench/diag_c149_a1_2_facts.md`)**
     USER-RULES: none apply (a measurement before an adoption, the Error List reader's launch form and card order; no design, no
     computation change).
     - **(a) Accepted:** the s06 scratch built cleanly: `claudeDev\D1_ring_p4s06_20261008_174730.vi` (569ffbf5), all build gates PASS 22/0
       (`diag_c147_p4s06v18_scratch.log` last segment :1040). The Error List reader works with nothing installed: the LocalCache site is put
       on `sys.path[0]` in-process (`diag_c149_a1_2_probe.log` 5/0). 148-a3-3's provisional dry/prerun "FAIL" is by tool design
       (`stage_prerun.py:2593-2599`); s07 dry + prerun count only after the rebase on a real s06 graph. Nothing is rebuilt; 569ffbf5 is not edited.
     - **(b) The s06 Error List (51 vs predicted 55) is neither accepted nor rejected; s06 is NOT adopted this round.** PD354's advisory
       returned as designed (total off by 4 > 3, no unseen class). The concern is not the count but the new item "source void -> sink I32"
       (read json :322, not in s04/s05) together with op 21's "target BROKEN" line (scratch log :990-994). A type conflict on a wire that this
       session created could change the computation (rule 1a), so it is measured before any adoption. Measurement = the prepared read-only
       card `tools/bench/cards/task_149-a1-3.json` (brief 3810fe03) as written, PLUS the type-conflict wire's source and sink terminals
       (uid, owner node, name, type) from a graph read of a byte copy of 569ffbf5. Facts only; the next judgement decides adoption.
     - **(c) Error List reads keep the per-command wrapper `tools/bench/diag_c149_a1_2_elrun.py`** (unchanged `errorlist_check.py` run with the
       LocalCache site on `sys.path[0]`). No package install, no user/env change, no runner relaunch for this. A permanent fix inside
       `errorlist_check.py` is not authorised this cycle.
     - **(d) fp-62** (launch gate judged the recipe's offline `--el-advisory` by an older failed segment of the appended scratch log) stays
       queued; it is drained when the queue is due, not inside this purpose.
     - **(e) Then PD361(b)+(c) as ONE tooling card, ALONE, unchanged.** It does not depend on the s06 outcome and runs after 149-a1-3 has
       returned with LabVIEW gone. No s06 adoption, no s07 rebase and no `memory_model.json` write this round.

361. **(cycle 149 judgement, 2026-10-08 — after `tools/bench/cards/assign_result_148_3.json` HANDBACK c-outside-purpose "p1s-A" again,
     `result_148-a3-2.json` PASS, `tools/bench/diag_c148_a3_2_facts.md`, `tools/bench/assign/state_148_3.json:51-56`)**
     USER-RULES: none apply (test-harness hygiene, a gate's input validation and the order of an already-decided build; no design, no
     computation change).
     - **(a) Accepted:** PD360(b)/(c) done — unmask 5/0 EQUAL HEAD vs disk (`diag_c148_a2_3_unmask_r2.log`), stale worktrees removed, 4/4
       suites green. The facts file's OPEN is answered: **"NOW failing set ⊆ PRE failing set" is green.** The 5 PRE-only failures (dry_c130_5,
       c103, c106c, c128b, stageplan) are FileNotFoundError on untracked sim files that a HEAD export cannot carry (`diag_c148_a3_2_facts.md:36`);
       requiring them would test git, not the edit. Nothing is re-run for PD360.
     - **(b) The second "p1s-A" hand-back is judged the SAME leak, re-armed by our own baseline, not a failure of the fp-60 fix — to be
       MEASURED, not assumed.** The pre-fix tree (HEAD 07202624) carries the OLD `selftest_chat_p1.py` (8250b3ef) and OLD `guard_assign.py`
       (e9879c20) (`diag_c148_a3_2_facts.md:27`); c_e3/f2 run chat_p1 (`diag_c148_a3_1_suites.log:66,79`), and the PRE runs inherited the
       live `ASSIGN_STATE`. The hand-back time is 2026-10-08 16:47:46 KST (`state_148_3.json:54`, t 1791445665.97). Discriminator: which
       child (tree, suite) was running at that second, from the wrapper's run times. A PRE child ⇒ confirmed. A NOW child ⇒ the fp-60 fix
       leaks, so return (no fix in that card).
     - **(c) Device, because a pre-fix baseline is a recurring pattern here (PD359(d), PD360(b)) and old code cannot be patched:** (1) the
       LIVE `tools/hooks/guard_assign.py` honours a state hand-back only when it carries the provenance the fixed code writes (the dispatched
       card's path under `tools/bench/cards/` and its id). It logs any other entry and ignores it. (2) Any wrapper that runs a pre-fix tree
       removes `ASSIGN_STATE`, `CYCLE_ROLE` and `CYCLE_SESSION` from the children's environment (patch `diag_c148_a3_1_suites.py` as the
       reference copy). A new self-test feeds an old-format hand-back into a state COPY: it FAILS on bbaa2325 and passes after. The existing
       guard_assign / guard_session / chat_p1 / assign_flow / c148_assign_leak self-tests give rc 0 or the same counts as before the edit.
     - **(d) Order (deliverable first):** the s06 scratch runs FIRST, as prepared in `tools/bench/cards/task_148-a2-4.json`. Every
       pinned md5 is re-checked; a card is re-issued under a 149 id only where a pin moved. dry + prerun run on the current bytes, then ONE run,
       adopt by PD354(a), and `load_by_vi` is the only memory_model change. The s07 offline prep runs beside it (PD358(f)) and is rebased on
       the real s06 graph after adoption. (b)+(c) follow as ONE tooling card, ALONE, after both return. None of the s06 cards runs a pre-fix
       tree, so the leak cannot re-arm before (c).

363. **(cycle 149 hand-back 2 judgement, 2026-10-08 — after `tools/bench/cards/handback_149_2.json` (c-outside-purpose, tooling card
     149-a2-1 writes `tools/hooks/guard_assign.py`), `assign_result_149_2.json`, `result_149-a1-3.json` FAIL 4/1,
     `tools/bench/diag_c149_a1_3_facts.md`)** USER-RULES: none apply (adoption of an already-built intermediate, a read-only census, and
     the order of an already-decided tooling card; no design, no computation change).
     - **(a) Accepted:** the facts of 149-a1-3. The header really reads 51 (an image, not OCR). The -6 / -2 / +2 / +1 classes are explained
       by three s05 sourceless wires that s06 sources, and by the two termless outputs of the moved nodes (`diag_c149_a1_3_facts.md:29-38`).
       w23807 is the op-21 wire, 1D I32 at source and both sinks, so it is NOT the type-conflict item. The missing `Is Broken?` read is
       not owed again: its question ("is w23807 the void→I32 wire") is answered by the types.
     - **(b) s06 IS ADOPTED (569ffbf5 → `D1_ring_p4s06_*.vi`, PD354(a) route), with item 6 (source void → sink I32) recorded as
       UNIDENTIFIED.** Why rule 1a is not at stake in the adoption: the build gates are 22/0, and E1 has the real graph == the simulated step
       at all 21 ops (`diag_c147_p4s06v18_scratch.log:999`), so the topology is the planned one. A wire whose source is void is a BROKEN wire.
       It cannot run, so it cannot change a number in silence. It either disappears under the planned wiring of later sessions or blocks
       ExecState 1 at P6. Rule 1a's acceptance stays numeric, at the P6 run. PD354 made the Error List a recorded cross-check, not a gate.
       The expected file for s06 is the 51-item read, including item 6.
     - **(c) Measured in the same LabVIEW card, read-only, facts only:** a census of every wire terminal whose type is Void (or whose
       type string contains Void), taken from the adopted s06 and from a BYTE COPY of s05 3f9ac26b. Each terminal is listed as wire uid,
       terminal uid, owner node uid/class/label, terminal name and type string. The s06-only entries are listed separately. This uses
       plain gscript reads (not the stagekit discard_work path, fp-63), with no edit verb and no `Is Broken?`. **P6 obligation:** item 6's
       wire is identified and gone before P6's ExecState 1. If still unidentified by s07's adoption, that is a judgement item.
     - **(d) s07 is rebased** on the real s06 graph read (`stage_prerun.py --rebase`), then dry + prerun run on the current bytes. It is
       NOT launched in this round.
     - **(e) Then PD361(b)+(c) as ONE tooling card, ALONE, after (b)–(d) have returned with LabVIEW gone.** The edit of
       `tools/hooks/guard_assign.py` (the provenance check) is AUTHORISED by this purpose. So is the patch of the pre-fix wrapper
       `tools/bench/diag_c148_a3_1_suites.py` and the new self-test. The prepared `tools/bench/cards/task_149-a2-1.json` (brief 65243d97)
       is dispatched as written.
     - **(f)** fp-62 and fp-63 stay queued until the queue is due. The `load_by_vi` s06 entry is the only `memory_model.json` change.

364. **(cycle 150 judgement, 2026-10-08 — after `tools/bench/cards/assign_result_149_3.json` HANDBACK a-unexplained-after-retry
     (`result_149-a3-1.json` FAIL, `result_149-a3-2.json` FAIL), `tools/bench/diag_c149_a3_1_facts.md`, `diag_c149_a3_2_facts.md`,
     `diag_c149_a3_void_census.md`, `archive/peer/2026-10-08-retrospective-cycle149.md`, `archive/peer/2026-10-08-outcome-review-20261008.md`,
     `tools/bench/cards/steer_149.json`)** USER-RULES: none apply (acceptance of measured facts, withdrawal of a measurement, a session cut by
     the X10 rule already in force, a repair of a review parser; no design, no computation change). The ORDER question goes to the user as
     D-2026-10-08-01.
     - **(a) Accepted:** cycle-149 round-3 items 0–2. s06 is adopted: `claudeDev\D1_ring_p4s06_20261008_174730.vi` (569ffbf5, adopt record
       19:08:25, `diag_c149_a3_1_adopt.log` 3/0); expected EL file 51 items (`errorlist_expected_D1_ring_p4s06_20261008_174730.json` b47995c8);
       graph `graph_ring_p4s06_20261008_192149.json` a3ecb92b (15/0, E5 PASS once w23807 counts as new: kept_by_key,
       `diag_c149_a3_2_mkgraph.py:46-48`); `load_by_vi` s06 = 593.8 MB (memory_model 8eec443c). Both round-3 failures are faults of our
       scripts, not of the VI: a3-1 ran a graph-plan maker that had never run (fixed in a3-2); a3-2 ran a census whose read rate and Void test
       nobody had measured (`diag_c149_a3_void.py:12-14`; a Void type is named '0x00', `tools/gscript.py:4585-4588`).
     - **(b) The full Void census (PD363(c)) is WITHDRAWN.** Its answer cannot change the next build: s06's graph equals the plan at all 21 ops,
       and a wire with a void source is a compile error that cannot change a number (PD363(b)). The 1112 terminals read hold no type code 0x00
       and cover 14 of the 16 new wires. **Rule for every later measurement card on this path:** check the reader on a known case and its rate
       on ≤ 50 reads before a full run (retrospective-cycle149 counterfactual).
     - **(c) Cycle 150 = P4 session 7, RE-CUT at the measured load.** The prepared s07 (v18 ops 136..149, 14 actions) was cut at the PROVISIONAL
       start 627.7 MB; s06 measured 593.8 MB. The cut rule in force takes the measured load of the input file and the longest prefix (PD320(e),
       PD352(b); limit 680 by PD328), so s07 is RE-MADE on the real s06 graph: v18 ops from 136, longest prefix with MAIN X10 ≤ 680, ≤ 40
       actions, no `of` pair split; plan, pred and MAIN/scratch recipes regenerated with only base/start/cut changed (no stage-tool edit); dry +
       prerun PASS on the final bytes. PD358(f)'s rebase-only route for s07 is superseded, with one fallback decided now so it is not a
       hand-back: if re-making s07 would need a stage-tool edit, the prepared 14-action s07 is rebased on the real s06 graph instead
       (PD358(f)) and the longer cut moves to s08. Then ONE scratch on a new byte copy of s06 569ffbf5
       → adopt by PD354(a) as `D1_ring_p4s07_*.vi` → full final EL written as its expected file (per-class difference against s06's 51; item 6
       present or gone) → fresh load + graph read (graph plan by the `diag_c149_a3_2_mkgraph.py` form; launch gate with the predecessor form
       `--graph graph_ring_p4s06_20261008_192149.json`) → `load_by_vi` s07 only. **s08 is then made directly on the real s07 graph read**
       (not provisional: a provisional plan's dry/prerun fail by design, `tools/stage_prerun.py:2593-2599`) at the measured s07 load with the
       same cut rule; dry + prerun PASS; NOT launched. 67 v18 ops remain after s06, so s08 may be P4's last session.
     - **(d) Item 6 ("source void -> sink I32")** is read again in s07's Error List. Gone ⇒ closed as a transient of the in-between file.
       Present ⇒ it is located by an Error-List-item → selected-object reader (the missing tool retrospective-cycle149 names), built ALONE when
       a judgement orders it, never by a third guess or a census (CLAUDE.md "When a diagnosis is GUESSED twice, build the reader"). PD363(c)'s
       P6 obligation is unchanged.
     - **(e) Device for device-failed (threshold 1, retrospective-cycle149:381).** Four parsers find the disposition heading by its FIRST
       occurrence, and every v2 retrospective prompt quotes that heading mid-line (`retrospective-cycle149.md:147`), so all four read the
       prompt: `tools/hooks/guard_peer.py` undisposed (:849-851), `tools/cycle_runner.py` retro_undisposed (:1017-1019), `tools/audit_cycle.py`
       A4 (:619, also :326) and, found by this session, `tools/violations.py:177`, which has counted no violation of retrospectives 147–149.
       Fix: ONE shared helper that finds `## What was done with it` alone at the start of a line and takes the LAST such heading; the four sites
       use it (these edits, the hook and the runner included, are authorised by this purpose); every other parser of that heading in `tools/`
       (not `tools/bench/`) is listed as using it or as unable to misfire. Self-test on two copies of `retrospective-cycle149.md` (placeholder
       restored / filled): each site misreads the placeholder copy on the current code and reads both right after; `py tools/violations.py`
       then lists retrospectives 148 and 149 with 0 slugs awaiting; edited files py_compile and their existing self-tests give rc 0 or the same
       counts as before. Runs AFTER the s07 LabVIEW card, ALONE (it edits a hook). The refused `gate_fp.py log --cmd` of round 1
       (retrospective-cycle149:374, fp-22 class) is logged to the gate-fp queue in the same card.
     - **(f) PD361(b)+(c) is DEFERRED, not dropped** (`tools/bench/cards/task_149-a2-1.json`): no card in this purpose runs a pre-fix tree, so
       the leak cannot re-arm. It runs ALONE before the next card that runs a pre-fix tree (a HEAD export or an older worktree), or with the
       next gate-fp drain, whichever comes first. retrospective-cycle148 finding 2 (`tools/bgrun.py --material` drops ASSIGN_STATE/CYCLE_ROLE/
       CYCLE_SESSION for every child) is weighed when that card is re-issued.
     - **(g) steer_149 is REFUSED with evidence, and its re-plan question goes to the user (D-2026-10-08-01).** Clauses 1, 2, 3 and 5 are done
       (the question is asked; s07 advances R1 through M3; it is a deliverable build). Clause 4, "RUNS or produces a runnable deliverable",
       cannot be met by any act in the user's plan before P6: the user chose P4 as ONE step built over several sessions whose in-between files
       are not run (D-2026-10-02-04), the chain first runs at P6 (PD238(g)), and no other track is designed before P6 (STATUS `## NEXT`
       parallelism rule, user 2026-09-28). The review's alternative (frame-rate control in a copy of the display-loop VI and a 150 Hz run,
       which is the user's own 09-25 choice D-2026-09-25-05) changes that order, so the user decides. Under the 2026-09-23 ruling the repeated
       verdict does not stop the runner; the escalation is marked in STATUS. A second refusal of this item stops the runner (2026-09-24 rule).
     - **(h) STATUS.md back to about 110 lines:** NEXT paragraphs older than cycle 150 and the history lines move VERBATIM to
       `archive/2026-10-08-status-cycle150-relocate.md`; kept byte-identical: the lock block, the hardware banner and `rig-state:`, the chat's
       STOP line, OPEN, the cycle-150 NEXT paragraph, `current-bed:` and its comment. OPEN 53 and 58 are closed by this judgement (STATUS).

365. **(cycle 150 hand-back 1 judgement, 2026-10-08 — after `tools/bench/cards/handback_150_1.json` (a-unexplained-after-retry,
     card 150-a1-1), `assign_result_150_1.json`, `result_150-a1-1.json` FAIL, `result_150-a1-2.json` PASS, `result_150-a1-3.json` PASS,
     `tools/bench/diag_c150_a1_1_facts.md`, `diag_c150_a1_3_facts.md`)** USER-RULES: none apply (a planning-tool key, a gate licence for
     the terminals a session wires itself, and card order; no VI design, no computation change; `docs/user-rules.md` has no row on
     terminal names).
     - **(a) Accepted:** PD364(h) done (STATUS moved verbatim to 110 lines, 150-a1-2) and the invariants held (107 files, no LabVIEW).
       The s07 cut made by PD364(c)'s rule is ACCEPTED: `plan_ring_p4_s07v18.json` 10a4f59a, v18 ops 136..165, 30 actions, start 599.7
       (= `load_by_vi` 593.8 + op-0 read 5.9), MAIN 678.8 (`diag_c150_a1_1_facts.md:10-16`). Its pred and MAIN/scratch recipes are still
       the 14-action files: they are regenerated, never launched as they are. The `_prov148` copies are history.
     - **(b) The rebase refusal is a TOOL DEFECT, measured, not a VI fault.** The real s06 holds no extra object. The two "extra" nodes
       are the pre-existing #2626 (t2832/t4160/t4165 'array'→'element') and #9503 (t9505/t9508 'Value'→''), renamed by LabVIEW when s06
       wired them (licensed, `plan_ring_p4_s06v18_licence.json:16-30`). `stage_prerun.rebind` files a terminal as OLD only when
       (uid, owner, NAME) is in N's base (`tools/stage_prerun.py:3829`), so a renamed old terminal lands in `real_new` and breaks the
       shape count (:3846-3849). s05→s06 passed only because no old terminal was renamed (`diag_c150_a1_3_facts.md:24-27`). PD364(c)'s
       14-action fallback meets the same check and is void.
     - **(c) Fix, decided now: the old/new split in `rebind` is NAME-FREE.** Old-terminal identity = (term uid, owner uid, term class,
       direction). A pre-existing terminal whose name differs between N's base and the real graph is an INFO line
       (`RENAMED-OLD <uid> #<owner> '<a>'->'<b>'`, `info['renamed_old']`), never a refusal; `rebind` reads no licence. Why: the
       function's own rule is "names are NEVER keyed" (PD278(c), :3788). Card 142-5 (PD330(d)/PD332(a)) added the name to catch LabVIEW
       re-issuing a deleted node's terminal uids to a NEW node, and that case is told apart by the OWNER uid (28004/28979 moved from the
       deleted #27928/#28916 to the new #6942/#6805, `tools/bench/selftest_rebind_c142_5.py:2-5`), not by the name. The user's 2026-10-08
       direction for the result gates (card chat-T6: a renames whitelist is the cause to remove, a name is a report column) fits the same
       fault here. Every other refusal stays (uid_reuse, a named uid on another owner, created-object shape, wires). Edit scope: the key,
       the info list and the docstring of `rebind` only. Proof, new `tools/bench/selftest_rebind_c150.py`: R1 the s06→s07 inputs
       (before = s06 `finalized.base`, prov = eeb22bba, real = a3ecb92b) REFUSE on the current code with the logged list and bind after;
       R2 RENAMED-OLD lists exactly the 5 measured renames; R3 a synthetic term-class change of an old terminal at the same (uid, owner)
       still refuses; R4 the s05→s06 inputs bind to the same node map as before. `selftest_rebind_c142_5` stays 4/0;
       `selftest_rebind_c132_5`, `selftest_rebase_c132_6`, `selftest_rebase_uidreuse_c143_4` give rc 0 or the same counts (PD359(d)).
       This card runs FIRST and ALONE: the deliverable's own gate refuses it (CLAUDE.md 2026-10-08 exception), and it is outside
       `tools/hooks/**`.
     - **(d) Then s07 as PD364(c), on the 30-action plan:** `--rebase` onto `graph_ring_p4s06_20261008_192149.json`; X10 recomputed after
       the rebase ≤ 680 (else the longest prefix ≤ 680, no re-plan); pred + MAIN/scratch recipes regenerated for 30 actions; dry + prerun
       PASS on the final bytes. **Licence `plan_ring_p4_s07v18_licence.json`** (pb-licence/1 in the s06 form, written by script from the
       rebased plan, never typed): `rename_by_uid` for #2626 if X11 flags op 150 `p4_rbB_sel_t4168` (PD352(d) extended to the session
       that carries op 150); `renames` = every BASE sink terminal (uid, owner) that an s07 connect row wires, `from`/`to` unset (= any
       name, `tools/stagekit.py:1412-1421`). That applies the user's chat-T6 rule, for this session only, to the terminals it wires
       itself until chat-T6 merges; no other gate changes. `--scratch-required` quoted; ONE scratch on a NEW byte copy of s06 569ffbf5.
     - **(e) Result routes, decided now:** (1) all gates PASS → adopt by PD354(a) as `D1_ring_p4s07_*.vi`. (2) the ONLY failures are
       TD/PB name changes on BASE terminals (no D / wire / E1 / cdiff / class / count failure) → no rerun: the stored end read is
       re-scored offline with exactly those measured renames added to the s07 licence (PD356(c)/PD357(a) precedent) and adopted on ALL
       PASS. (3) The Error List is a recorded cross-check (PD354(a)): RETURN only on an unseen class or |Δtotal| > 3. (4) Anything else →
       return at the first unexpected result. If `guard_peer` holds the launch on `prep_c150_a1_1_rebase.log` (rc 2), the hypothesis
       review is paid (`-Agent claude -Role hypothesis`, claim = (b)'s measured cause), not routed around. After adoption PD364(c)3/(c)4
       and (d) hold unchanged: full EL as its expected file with item 6 present or gone; fresh load + graph read; `load_by_vi` s07 only.
     - **(f) Parser device (PD364(e)), amended by the user's 2026-10-08 rule** (no runner card changes `tools/hooks/**`, even when the
       purpose names it; `tools/bench/assign/assign_config.json` `never_in_runner_globs`). The shared helper (the LAST line-anchored
       `## What was done with it`) lives in a NON-hook module; the runner card wires the three non-hook sites: `tools/violations.py:177`,
       `tools/cycle_runner.py` retro_undisposed and `tools/audit_cycle.py` A4 (:619, :326). `tools/hooks/guard_peer.py:849-851` is NOT
       edited: it is logged with `tools/gate_fp.py log` for the chat (id quoted). So are PD361(c)(1) (the guard_assign provenance check,
       which no runner card may make now) and the refused `gate_fp.py log --cmd` of retrospective-cycle149:374. Self-test as PD364(e) on
       the three sites; `py tools/violations.py` then lists retrospectives 148 and 149 with 0 awaiting. Runs AFTER the s07 LabVIEW card,
       ALONE.
     - **(g) s08 as PD364(c), made on the REAL s07 graph read** (directly, or provisional + `--rebase`, which (c) now lets bind renamed old
       terminals), at the measured s07 load, same cut rule, licence by (d)'s rule; dry + prerun PASS; NOT launched. If the round runs out
       of time or budget, (g) is what is left and becomes the next cycle's first act.
     - **(h) steer_149 stays REFUSED** with the same evidence plus (b): clause 4 cannot be met before P6 (D-2026-10-08-01 is still open),
       and the first card repairs the deliverable's own refusing gate, so the act is still the s07 build (clause 5).
     - **(i) For the chat's chat-T6 merge after this cycle:** cycle 150 changes the main tree's `tools/stage_prerun.py` (`rebind` key only)
       and the three parser sites in (f). The merge keeps both sides; after chat-T6, later sessions do not need (d)'s `renames` licence.

366. **(cycle 150 hand-back 2 judgement, 2026-10-08 — after `tools/bench/cards/handback_150_2.json` (a-unexplained-after-retry,
     card 150-a2-5), `assign_result_150_2.json`, `result_150-a2-5.json` FAIL, `tools/bench/diag_c150_a2_5_facts.md`,
     `tools/bench/cards/brief_150-a2-6.md`, and the v18 simulation's own rows `tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json:188-243`
     (07bc69e6))** USER-RULES: U1 (relied on: #2626's inputs are named and fed as S1 has them; no v18 action, source or sink changes;
     only an offline plan check in a card-owned script and the wording of a P6 check change); none contradicted.
     - **(a) Accepted:** 150-a2-2 (rebind old-terminal identity = (uid, owner, term class); a changed source flag is an INFO line
       `FLIPPED-OLD`). Its deviation from PD365(c)'s word "direction" is ACCEPTED: the undirected LoopTunnels t29779/t9505/t10179 take
       their direction from wiring, which stagesim already seeds (`tools/stagesim.py:2456-2461`) and the wire comparison still checks;
       R3's class change still refuses. 150-a2-4 (b-shadowing fix, `stage_prerun.py` c739eb86, 8/0) accepted. The s07 rebase PASSES:
       plan 10a4f59a → 08c2ad4d, RENAMED-OLD 5, FLIPPED-OLD 3, completeness PASS, final (`prep_c150_a2_5_rebase.log:80`). X11 flags
       op 150 ⇒ the s07 licence carries `rename_by_uid` #2626 (PD365(d)).
     - **(b) The V18E-R miss is in v18's rows, not in s07 (read from the v18 summary).** S1 names #2626's inputs `array|0` ← #5058
       'x,y,z array out', `element|0` ← #5119 'x-y', `element|1` ← #30117 Value, `element|2` ← #4580 Value (the `before` column,
       summary.json:188-243). The bed, and so every v18 step, carries the broken bed's names 'array'×4, so v18's cdiff holds
       `array|1..3` with `before: null` (keys S1 does not have) beside `element|0..2` with `after: null`: three rows about names, not
       sources. s06's wiring gave t2832/t4160/t4165 their S1 names back, so the rebased s07 has each #2626 input once, under S1's key.
       Cause in code: `computation_diff` keys rows by terminal NAME (`tools/vigraph.py:847-871`) and the old V18E-R compares key sets
       only (`tools/bench/prep_c150_a2_5_pred.py:103-106`).
     - **(c) V18E-R′ in the card's OWN pred script (no stage-tool edit); it replaces brief 150-a2-6 decision 1** (renaming row keys on
       both sides cannot fix rows that only exist because of a name): PASS iff (1) only-s07 is empty; (2) every only-v18 row has
       `before: null` in v18's `cdiff_detail` at the compared step and its node owns a RENAMED-OLD entry read from the rebase output
       (never typed); (3) on each such node, the multiset of sink-terminal names in the real s06 graph a3ecb92b equals S1's (read with
       `stagesim.load_s1`, not typed). Anything else FAILs ⇒ RETURN. The pred prints the three checks and the excluded keys. s08's pred
       uses the same rule.
     - **(d) PD356(d)'s P6 check is CORRECTED (its "'array'" wording is SUPERSEDED):** the first ExecState-1 file must read #2626's
       inputs with S1's names and sources: `element` ← the x-y chain (t2832), `element` ← TransPos (t4160), `element` ← RotPos (t4165),
       `array` ← the x,y,z chain (t4168). The names tell Build Array which inputs are appended as elements and which are concatenated;
       'array'×4 was the broken bed's transient.
     - **(e) Sink gates (brief 150-a2-6 decision 2) ACCEPTED:** the s07 MAIN and scratch recipes declare a sink gate for EVERY s07
       census row that goes through `wire_indicators` (measured 2: n1 `p4_rbA_re2` → [23166,'Pos: Diffraction Pattern'], n28
       `p4_rbD_sel_t25573` → [23166,'autofocus reset count (1.2 to 1.1)'], `prep_c150_a1_1_session.json:395-420`), read from the census
       by script, each with PD355(b)'s pass rule. PD355(b)'s "ONE" was s06's count, not a cap.
     - **(f) X10 on the rebased bytes:** ≤ 680 ⇒ go on; > 680 ⇒ the longest group-respecting prefix ≤ 680 (PD320(e)), re-made and
       re-rebased by the same tools, V18E-R′ on it. Not a hand-back.
     - **(g) Round 3 = PD365(d)–(g) otherwise unchanged:** pred (V18E-R′) + recipes (both sink gates) + licence + dry + prerun +
       `--scratch-required` → ONE s07 scratch on a new byte copy of s06 569ffbf5 → adopt (PD365(e) routes) → full EL (item 6 present
       or gone) + graph read + `load_by_vi` s07 → ALONE the parser device (PD365(f)) → s08 made, not run. If `guard_peer` holds the
       launch on `prep_c150_a2_5_pred.log`, the hypothesis review is paid with claim (b), never routed around.
     - **(h) For the chat (chat-T6) — a gate-fp entry:** name-keyed `computation_diff` rows make phantom rows whenever LabVIEW renames a
       terminal on a broken in-between file; the position key chat-T6 brings to D/TD/PB applies here too. steer_149 stays REFUSED
       (PD365(h)); D-2026-10-08-01 is still open.
