---
card: 159-f1-2
status: current
date: 2026-10-10
---
# Brief 159-f1-2 (assignment 159-3, retry of 159-f1-1) - MEASURE why `selftest_c134_1_dry` reads 9/2 (T2a, T2) instead of 11/0

Read `tools/bench/diag_c159_f1_1_facts.md` and `tools/bench/selftest_c134_1_dry_c159_f1_1.log` first. No stage-tool, `tools/hooks`, recipe or
`selftest_c134_1_dry.py` edit in this card - MEASURE only; the decision on a re-pin belongs to the judgement session. `labview: read` as before; no
LabVIEW process is started. `docs/script-writing.md` binds you (call shared functions, no pasted blocks).

Questions, each answered with a command + result + file:line:
1. **T2a**: diff `tools/recipes/stage_d1_ring_p3b2a.py` at the pinned md5 `bb5ba064` (find it via `git log --follow` / `git show <rev>:...`; quote the
   revision) against the current file (`0d1f0c15`). Are ALL changed lines the chat-E3 scope header (`# --- ... # ---` block, comment lines only)? Quote
   the diff stat and every non-comment changed line, or say there is none.
2. **T2**: does the PB failure (`first_fail=GATE PB frame-keyed cdiff(S1, real end) == bed's 16 rows and plan's 11 open pairs, coverage 63/81, unverified 1`)
   reproduce with today's `tools/stagekit.py` ac3a8f57 replaced by the pre-edit copy `tools/bench/selftest_c159_cen2_ends_stagekit_9cd8822e.txt`
   (md5 9cd8822e)? Do it WITHOUT touching `tools/stagekit.py`: run the suite from a scratch copy of the needed `tools/*.py` under a temp directory with the
   9cd8822e bytes as `stagekit.py`, or the equivalent import redirect you can justify; quote how, and the T2 outcome (PASS/FAIL, first_fail).
3. If T2 still fails with 9cd8822e: which earlier change is the cause? Test the two candidates the files already name - the PD387(e) dry repair
   (`addrcheck.pos_table` stub finding, `tools/bench/diag_c159_a4_1_facts.md`, `stage_prerun.py` md5 `7605116f` vs the md5 at the last passing run
   `tools/bench/selftest_c134_1_dry_c136_p2_measure.log`, 2026-10-02 - find that stage_prerun/addrcheck revision by git) - by running T2 with the older
   `addrcheck.py`/`stage_prerun.py` in the same scratch directory. Quote which single swap turns T2 back to PASS, or "none of them".
4. What T2 asserts (`selftest_c134_1_dry.py:82-84` and the T2 body): list the numbers it expects (bed rows, open pairs, coverage, unverified) and the
   numbers it gets; say whether the expected numbers are properties of the bed (unchanged) or of the old stub-based dry.

## Report: append to `tools/bench/diag_c159_f1_1_facts.md` is NOT allowed (card 159-f1-1's file); write `tools/bench/diag_c159_f1_2_facts.md`
(<= 30 lines, facts only): answers 1-4, md5 after of stagekit/stage_prerun/stagesim/stagexec (all unchanged), `tools/hooks` untouched,
VIs 94ffff94 / s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae unchanged. `OPEN:` lines with file:line. Scratch directories you create are deleted at the end.
