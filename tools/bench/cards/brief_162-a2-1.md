---
card: 162-a2-1
status: current
date: 2026-10-10
---
# Brief 162-a2-1 - TOOLING (offline, no LabVIEW): ONE pin sweep, then drain fp-82 / fp-84 / fp-85 with `tools/gate_fp.py drain`

Context: the LabVIEW card 162-a1-2 is done (adopted `D1_ring_p5s02b_20261010_105511.vi` f9ae7751). This is tooling AFTER it (`docs/d1/ring-p5b.md` PD393(e), lines 238-242). Offline only: no LabVIEW, no VI, no motor or camera. Read `docs/script-writing.md` (call shared functions, never copy).

## Steps (in this order)
1. **ONE pin sweep, run BEFORE any edit** (retrospective-cycle160 finding 1, `archive/peer/2026-10-10-retrospective-cycle160.md:545`): one script lists, for every selftest / prep script that pins an md5 of `tools/stagekit.py`, `stagexec.py`, `stagesim.py`, `stage_prerun.py`,
   `plan_ring_p5s02b*.json`, or `docs/d1/ring-p5b.md`, the pinned value vs the file's current md5 (hashlib). Scope = the scripts that cards 162-a2-1 and 162-a2-2 will edit or call: `selftest_c157_innerface.py`, `selftest_c160_regface.py`, `selftest_c160_l0stem.py`, `selftest_chat_p1.py`,
   `prep_c156_a1_1_licence.py`, `prep_c156_a1_1_pred.py`, plus every `selftest_c15*` / `selftest_c16*` that imports one of them (grep). Output a table: script, pin label, pinned, current, equal. Save the table and its script (`prep_c162_a2_1_pinsweep.py` / `.log`). This is a measurement: the stale pins are listed, not yet fixed.
2. **fp-85** (`tools/bench/gate_fp_queue.jsonl` line 85): `selftest_c157_innerface.py:72` pins stagesim eb99c6ba, the file is 95a162ba (`selftest_c158_runcheck.py:24` re-pinned the same drift). Edit that one pin line (Edit tool, one pin only, comment says why), re-run the self-test, expect green with the 12 content gates unchanged.
   Then `py tools/gate_fp.py drain --id fp-85 --fixed tools/bench/selftest_c157_innerface.py:<line> --selftest selftest_c157_innerface`.
3. **fp-82**: its fix is already in `tools/stagekit.py` (`gate_l0`, the `<plan stem>_in` suffix, PD393(e) says "fixed by stagekit 0b5bb678, `selftest_c160_l0stem` 14/0"). Re-run `selftest_c160_l0stem.py` on the current bytes (pins from the sweep); if green, drain with `--fixed tools/stagekit.py:<line of the gate_l0 clause>` and `--selftest selftest_c160_l0stem`.
   If the self-test fails only on a stale pin, fix that pin the way step 2 does and say so; any content-gate failure = RETURN with facts.
4. **fp-84**: PD393(e) says "real defect, fixed by (a)" (the executor now reads at every `delete_wire` checkpoint). Find the fixing line in `tools/stagexec.py` (grep `delete_wire` in `checkpoint_ops`) and its self-test (`selftest_c161_delckpt.py`, 11/0 at `tools/bench/selftest_c161_delckpt_c161_a3_2.log`), re-run it on current bytes, then drain with `--fixed tools/stagexec.py:<line>`.
   Peer note: the self-test log of the 09:45 suite run (`prep_c161_a3_1_suite_after.log`) showed delckpt 9 pass / 2 fail BEFORE 161-a3-2 rewrote D2 and the P pin (peer archive `archive/peer/2026-10-10-c162-delckpt-stale-pin.md`: the fails pre-dated the re-pin, D2 was rewritten, the `checkpoint_ops` equality in D2 is partly circular). Do not claim "stale pin after the run"; state what the current-bytes run shows.
   Also fill the disposition (`## What was done with it`, as the other archive/peer files do) of that review file: the conclusion (rule not defective) held, its correction of the explanation is adopted.
5. **Hooks:** `tools/hooks/**` entries (fp-75, fp-80, fp-81, fp-83) are left for the chat; do not touch them and do not drain them. No other queue row is changed. `git_commit` false, STATUS not edited.

## Report `tools/bench/diag_c162_a2_1_facts.md` (<= 35 lines)
The sweep table (counts equal / stale and which); each drained row: id, path:line, self-test name and its pass/fail counts, queue status before -> after (a jsonl read); the self-test logs; files edited (list, one-line reason each) with md5 before -> after; `OPEN:` lines (measurements only).
A failing self-test or a stale pin outside the named ones = RETURN with the facts, do not widen the edit.
