---
card: 167-a1-5
status: current
date: 2026-10-12
---
# Brief 167-a1-5 (assignment 167-1) - P6-0 tooling notes 2, 6, 7 (OFFLINE; no LabVIEW)

Plan: `docs/d1/ring-p6.md` PD404 "the eight notes" (lines 34-42): notes (2), (6), (7); and (h) (line 91). The LabVIEW and facts cards of this assignment are finished; nothing runs beside this card. NO LabVIEW, no hook edit (`tools/hooks/**` is untouchable), no motor or camera, no VI opened.
Read `docs/script-writing.md` first (rules 1, 4, 7, 9). Do the three parts in this order; a part that fails its self-test returns the card (no second attempt at the same part).

## Part A - note (2): the elcls and JSON-rewrite helpers into the shared module
Copies found by earlier cards: `elcls` inline in `tools/bench/diag_c165_a3_4_elexp.py:50-57`, `diag_c164_a3_5_elexp.py:50-57`, the c150..c163 `*_elexp.py`, the `prep_c147..c154 *_pred.py` and five `tools/recipes/stage_d1_ring_p*_scratch.py` (`tools/bench/diag_c166_a1_2_facts.md:25`);
the JSON-rewrite helper `rewrite_json` in `tools/bench/diag_c166_a1_1_lib.py:31` (own self-test 2/0; one older copy at `prep_c164_a3_7_write.py:53-59`; `tools/bench/diag_c166_a1_1_facts.md:38`).
1. `grep "def " tools/stagekit.py tools/errorlist_check.py` and `docs/toolkit-capabilities.md` FIRST: `stagekit.el_advisory` (:2852) already uses an `elcls` ("the scratch recipes' elcls", :2842) and `errorlist_check.norm_ocr` (:331) is shared. If a shared `elcls` already exists, call it; do not add a second one. Add to the module that OWNS the topic (stagekit for Error List classes / JSON rewrite helpers, or `errorlist_check` if the topic owner is there) ONLY what is missing, each with a first-line docstring naming its self-test (rule 9).
2. Self-test (rule 7) replaying RECORDED data: `elcls` over the 47 items of `tools/bench/errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json` must give the same class per item as the old inline copy (call both, compare; class counts must be the stored ones: looseends 23, notconnected 21, unwiredinput 1, twotypes 1, other 1); the JSON rewrite helper keeps its own two cases (backup made, compare of every other key).
3. Replace the inline copies in the CYCLE-166 scripts that the two facts files name as the copies to move (`diag_c166_a1_2_elexp.py`, `diag_c166_a1_1_lib.py` and the scripts that import it): they now call the shared functions. Re-run what they re-run without LabVIEW (their self-tests / offline compare): output byte-equal to the stored output (md5 quoted). Do NOT rewrite older closed recipes or diagnostics (c150..c165); they stay as the record of what ran (script-writing rule 4). List them as remaining copies (file:line).
4. Quote the self-test result lines. `py -m ruff` / `tools/lint.py` and `tools/dupcheck.py` on the edited files if they take a file argument; quote the result.

## Part B - note (6): re-pin three drifted self-tests
`tools/bench/selftest_c165_innerface.py:250` (pins stagekit `dd57c1ca`), `tools/bench/selftest_c165_prime.py:117` (same stagekit pin), and the `P0` pin of `tools/bench/selftest_c147_b1_2.py`. Part A changes `tools/stagekit.py` (probably), so re-pin AFTER Part A, to the md5 of the files as they stand when Part B runs (hashlib, not a copy from this brief).
For each: run it before the edit (record the failing pin gate and that it is the ONLY failing gate), change ONLY the pin value(s), run it again, quote the pass line. A second failing gate that is not a pin = RETURN with the line (it is a real finding, not a re-pin).

## Part C - note (7): STATUS.md history older than cycle 164
In `STATUS.md` `## NEXT` (from line 67), the bullets starting `- (history)` whose text is about cycles BEFORE 164 (the CYCLE 163, 162, 161 purpose/round bullets and any older history bullet below them) are moved VERBATIM, in order, to a NEW file `archive/2026-10-12-status-cycle167-relocate.md` (front matter like `archive/2026-10-08-status-cycle150-relocate.md` - look at its head), and replaced in STATUS.md by ONE line `- (history) RELOCATED VERBATIM -> archive/2026-10-12-status-cycle167-relocate.md §1 (NEXT history older than cycle 164)`.
Keep: the live CYCLE 167 bullet, and the history bullets of cycles 164, 165, 166. Edit with the editor tools only (never a shell heredoc). Proof: a byte compare script (`tools/bench/diag_c167_a1_5_relocate.py`, scope header, `RESULT {...}`) that reads the moved text from the archive file and from `git show HEAD:STATUS.md`/the pre-edit copy you saved and shows byte equality of every moved bullet; STATUS.md line count before/after; the rest of STATUS.md unchanged (diff shows only the removed bullets and the one added line).
Do NOT touch the `rig-state:` key, the HARDWARE banner, the `labview-lock` block or the STOP/START lines (the machine keys); run `py tools/lint.py`-style or `errorlist_check.current_bed_text()` on the new STATUS text to prove the bed key still parses (as `diag_c166_a1_2` step 4 did).

## Checks
Hash first the inputs (listed in the card) and the seven VIs (75773b0d 7f2582ae 94ffff94 f9ae7751 564d8cbe 6dcd5c3d eb1d0f31; names as in `tools/bench/diag_c166_a1_1_hash.py`); hash again at the end, unchanged. `tasklist` shows no LabVIEW. `git diff --stat` of the files you touched, quoted. Every edited `tools/*.py` has its self-test line quoted. No file under `tools/hooks/**` edited (`git diff --name-only -- tools/hooks` empty, quoted).
Facts `tools/bench/diag_c167_a1_5_facts.md` (<= 40 lines). Do not edit `tools/bench/memory_model.json`, plans, recipes of closed cycles, or `docs/d1/INDEX.md`.
