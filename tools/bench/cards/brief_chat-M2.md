# Brief chat-M2 - X10 release for a declared memory-ceiling probe, then run chat-M1's probe (user 2026-10-03 approved (나))

chat-M1 (tools/bench/cards/result_chat-M1.json) was BLOCKED before LabVIEW opened: stage_prerun X10 counts a looped
whole-VI read as UNMEASURED = FAIL (tools/stage_prerun.py:2043-2111, cards 132-4/136-2/138-2), but a ceiling probe must
loop its reads and is meant to cross 690 MB. Gate false positive fp-35. The probe script is ready:
tools/bench/diag_chat_m1_mem.py (+ diag_chat_m1_mem_plan.json), dry PASS, prerun 14/1 (only X10).

## Part A - release (offline)
Add to stage_prerun X10 ONE narrow release: a script that declares itself a memory-ceiling probe (a module-level
literal, e.g. `X10_PROBE = "memory ceiling, scratch only"`) passes X10 as `PROBE-EXEMPT` ONLY IF the dry run shows all of:
it works on a byte copy (input md5 gate K-style) and never saves or edits the bed/original; no save op at all except
scratch deletion; a warn-only meter is active. Anything else with that literal still FAILs X10. Self-test: probe with
those properties -> PROBE-EXEMPT; same literal on a script that saves -> FAIL; no literal -> unchanged behaviour.
Re-run the X10 self-tests (selftest_x10_*) green. Drain fp-35 in gate_fp_queue (tools/gate_fp.py) citing the change.

## Part B - run the probe (LabVIEW, scratch only)
Re-run --dry and --prerun for diag_chat_m1_mem.py (unchanged except the X10_PROBE literal), then launch it under
bgrun --material and WAIT IN-TURN until BGRUN END. Report: peak private MB, the first error (code/text/MB/op) or none
up to the cap, MB per read and per edit cycle, handles/GDI/USER, lv_gui ping, memory after closing the scratch, LabVIEW
gone at the end, bed md5 unchanged. Suggest a safe ceiling with the stated margin. Do not change memory_model.json,
fail_above or MEMSTOP (the chat proposes new limits to the user).

## Limits
Runner is stopped; no other card is live. Never save the bed or any original. Edit tool only (no py heredoc patches).
git commit allowed for the stage_prerun change + self-test. Return one result/1 JSON object.
