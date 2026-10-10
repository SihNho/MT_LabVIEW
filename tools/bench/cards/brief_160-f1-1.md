---
card: 160-f1-1
status: current
date: 2026-10-10
---
# Brief 160-f1-1 (assignment 160-1) - OFFLINE: which commit makes `selftest_c134_1_dry` lose the four `2626|Terminal|array|0-3` PB rows (PD390(g), first half)

`labview: read` (a stage dry-run only; no LabVIEW process is started). No `tools/` edit (stage tools, stagekit, recipes), no `tools/hooks` edit.
Another card is editing `tools/stagesim.py` and `tools/stagexec.py` on disk right now, so NEVER import tools from the working tree for this bisect:
extract each candidate tree with `git archive <rev> tools | tar -x -C <tempdir>` (or the equivalent) and run the dry from there; delete the temp dirs at the end.
`docs/script-writing.md` binds you; reuse `tools/bench/diag_c159_f1_2_t2.py` (in-memory finder, same dry command) rather than writing a second harness.

## Facts you start from (`tools/bench/diag_c159_f1_2_facts.md`, read it first)
- The recipe PB gate (`tools/recipes/stage_d1_ring_p3b2a.py:71-74`) compares the cdiff rows with `plan_ring_p3b2a_pred.json` `cdiff_rows` (16) and the plan's 11 open pairs.
- With every `tools/*.py` at commit 421d6108 the dry PASSes (PB PASS, unverified 0); with every `tools/*.py` at a9d0da22 it FAILs PB: extra [], missing
  `2626|Terminal|array|0..3` (12 of 16 rows). Same data files on disk in both. 62 commits lie in 421d6108..a9d0da22.

## Measure
1. Bisect commits 421d6108..a9d0da22 (only those touching `tools/*.py`; `git log --format=... -- tools/*.py`) with the dry command of `diag_c159_f1_2_t2.py` on the
   extracted tree, to the FIRST commit where PB loses the four rows. Quote the commit hash, its full subject line, date, and the changed hunks that decide PB (file:line).
2. State, from that commit's own message/diff and PD366/chat-T6 + chat-T7 text in `docs/d1/`, whether it is the intended **PB-by-position** change (chat-T6 `771a39a1`/`9dbd384b`
   or chat-T7 `676f874f`), i.e. whether the four missing name-keyed rows are rows that the position-keyed PB now (correctly) merges or keys differently - show the position key
   that the same four terminals get in the new PB (quote the rows it now prints instead, or show that they are absent because the position key equals another row).
3. Decision rule (mechanical, nothing else): ONLY IF the first bad commit is the chat-T6 or chat-T7 PB-by-position change AND step 2 shows the pred's 16 name-keyed rows are
   the old keys of the same terminals, re-pin the pred: write a NEW file `tools/bench/plan_ring_p3b2a_pred_c160.json` (the old file stays; copy + changed rows only),
   and report how `selftest_c134_1_dry.py` would point at it; do NOT edit `selftest_c134_1_dry.py` or the recipe. Otherwise write `OPEN:` with the commit and why.
4. T2a: its pin `bb5ba064` is the recipe before the chat-E3 header (header-only change, `diag_c159_f1_2_facts.md:10`). Report the exact one-line edit of the pin in
   `tools/bench/selftest_c134_1_dry.py:82` (old prefix, new prefix `0d1f0c15`) as a proposal in the facts file; do not apply it.

## Report `tools/bench/diag_c160_f1_1_facts.md` (<= 35 lines, facts only)
Bisect table (commit, PB result), first bad commit + subject + decisive hunk, the step-2 answer, the pred file written or the OPEN line, the T2a proposal, the T2 `unverified 0`
OPEN of `diag_c159_f1_2_facts.md:30` carried unchanged. md5 UNCHANGED (before/after): `tools/stagekit.py`, `tools/stage_prerun.py`, `tools/stagesim.py` (read it, it is being edited -
say "edited by a parallel card" if it moved), `tools/recipes/stage_d1_ring_p3b2a.py` 0d1f0c15, `selftest_c134_1_dry.py` 10178208, `plan_ring_p3b2a_pred.json` 45eb0b67.
VIs 94ffff94 / eb1d0f31 / 2482fe7b / 7f2582ae unchanged; `tools/hooks` untouched; temp dirs deleted.
