---
card: 155-a5-1
status: current
date: 2026-10-09
---
# Brief 155-a5-1 - drain fp-73: `stage_prerun.is_vi_modifying` must not call a discard-only hygiene diag a stage (OFFLINE tooling card, LabVIEW 0)

PD378(d). Runs AFTER the LabVIEW cards (all done); no LabVIEW card is live. This is the ONLY card in cycle 155 allowed to change `tools/stage_prerun.py`.

## The false positive (`tools/bench/gate_fp_queue.jsonl` line 73, id fp-73)
`guard_bash` refused a launch of `tools/bench/diag_c153_a2_2_queue_hygiene.py` because `stage_prerun.is_vi_modifying` (`tools/stage_prerun.py:3187`, built on `vi_modifying_calls` at 3161, `MODIFY_VERBS` at 3137) saw the script import stagekit and call `discard_work`. `Stage.discard_work` (`tools/stagekit.py:577`) does the OPPOSITE of modifying: it marks the dated work copy a scratch so `close()` deletes it ("THIS STAGE SAVES NOTHING"). The diag's work copy was an NI example; `gscript.hygiene_run` (`tools/gscript.py:366`) touches only never-saved scratch copies. The earlier hygiene diag `tools/bench/diag_c126_4_op.py:65` ran the same runner without stagekit and was not gated.

## What to do
1. Decide the narrowest fix and write it in the facts file with the reason. Preferred: a script whose ONLY `MODIFY_VERBS` hit is `discard_work` is not VI-modifying (any other MODIFY_VERBS name in the same file keeps it classified; the stagekit import test stays). Take another form only if a measured reason shows this one lets a real stage through - e.g. every real stage script in `tools/recipes/` and `tools/bench/` that calls `discard_work` also calls another verb; MEASURE that with `vi_modifying_calls` over all `tools/**/*.py` before and after, list files whose class changes (expected: only discard-only files).
2. Edit `tools/stage_prerun.py` (Edit tool, no heredoc patch), nothing else in tools/. Quote the before/after classification counts. Do NOT touch `tools/hooks/**`, stagexec, stagesim, stagekit, vigraph, addrcheck, gscript.
3. New self-test `tools/bench/selftest_c155_gatefp73.py` (stagekit NOT imported by the test itself; it writes temp .py files, so the test is itself never classified): discard-only script -> `[]`/False; discard_work + `save` -> still True; discard_work + `plan_rows` -> True; no stagekit import -> False; `diag_c153_a2_2_queue_hygiene.py` -> False; `tools/recipes/stage_d1_ring_p5s01b.py` and `stage_d1_ring_p5s02.py` -> True. Header per CLAUDE.md scope-header rule (labview: none, hardware: none).
4. Re-run the existing self-tests that call `is_vi_modifying` and quote counts before/after on identical commands: `selftest_c103d_hooks.py`, `selftest_c121_3_gatefp.py`, `selftest_fn_f2.py`, `selftest_guard_bash_jev.py`, `selftest_prerun_diag.py` (note any that fail BEFORE your edit as pre-existing). A count that gets worse is a RETURN, not a fix-up.
5. Re-run `py tools/stage_prerun.py` dry/prerun for `tools/recipes/stage_d1_ring_p5s02.py` and `stage_d1_ring_p5s01b.py` with no `--launch` and quote that results (16/0, X17 PASS, `--scratch-required` rc 3, `--check-launch` ALLOW for s02) are unchanged. Check `stage_prerun.py` md5 pins used by other stored artefacts: `grep -rl 9decb20f tools/bench` and list the files that carry the old md5 (they become stale; list them, do not edit stored P4 files).
6. Mark fp-73 drained with `py tools/gate_fp.py` (look up its subcommands first) citing the self-test; if the tool refuses, RETURN with the refusal text.
7. Facts file `tools/bench/diag_c155_a5_1_facts.md` (<= 35 lines): the diff (lines changed), classification before/after, self-test counts before/after, the new `stage_prerun.py` md5, the stale-pin list, `OPEN:` line.

## Pins (must not change)
stagexec 53e17623, stagesim eb99c6ba, stagekit aec03c6c, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e; all `tools/hooks/**`; P5-1a/P5-1 VI files; stored P4 recipes/plans/preds; plan_ring_p5s02* and recipes written by 155-a4-1 (md5 unchanged); `docs/d1/ring-p5.md`. `stage_prerun.py` itself changes - report its new md5.

## Return conditions
A real stage script would stop being classified; an existing self-test count gets worse; the fix needs a hook edit; a second failure at the same place.
