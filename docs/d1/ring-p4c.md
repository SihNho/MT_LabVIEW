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
