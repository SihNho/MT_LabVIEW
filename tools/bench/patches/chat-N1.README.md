# chat-N1.patch — how to apply it and check it

Card `tools/bench/cards/task_chat-N1.json`. The patch was built and self-tested on COPIES only. `git apply --check` passes against HEAD e5016aa.

## What it changes
- **(2) VI-modifying scripts are gated whatever their name.** `tools/stage_prerun.py` gains `is_vi_modifying(path)` / `vi_modifying_calls(path)`. They parse the file with `ast`: True only when the file imports `stagekit` AND calls a name in `MODIFY_VERBS` (20 names, the mutating `Stage` methods):
  add_shift_reg, add_sr_row, cfw_second_pass, connect, connect_from_wire, const_row, copy_in, create_local_read, delete_object, delete_wire, discard_work, from_decision, fs_inner_tunnel_connect, junk_purge, move_in, plan_rows, save, save_route, wire_indicators, wire_sr.
  Other changes in the same file:
  - `launched_vi_modifying(cmd)` is added.
  - `check_launch` and `record_started` (bgrun) treat those scripts like `tools/recipes/stage_*.py`: dry + prerun PASS records, decision 4, and the same RETRY_CAP all apply.
  - A refusal is prefixed `[classifier stage_prerun.is_vi_modifying ...]`.
  - `guard_bash.prerun_gate` records such a launch as pending too.
- **(4a) `requires` on task/1.**
  - `docs/protocol/task.json` gets an optional `requires: [{kind: op|file|terminal|verb, name, where?}]`.
  - `py tools/protocol.py requires <card>` checks each item OFFLINE:
    - op: a `.vi` under claudeDev/ops or claudeDev, plus a toolkit-capabilities/NAMES citation
    - verb: an ast `def` in gscript/stagekit/stagexec
    - file: the file exists
    - terminal: a `term_name` or connector-pane label in `docs/wiki/subvi/*.json`
  - The check writes `tools/bench/cards/requires_<id>.json` with `{ok, missing, found, card_md5}` and prints a RESULT line.
  - Under a bound card, `protocol.check_command` (reached by guard_bash through guard_card) refuses a bgrun or LabVIEW launch when that file is absent, stale (card md5 changed) or lists anything missing.
  - `tools/cycle_prompt.md` and `.claude/agents/material.md` are updated to match.
- **(4b) The dispatch cap is 6 per session (was 8).** `guard_session.MAX_DISPATCHES = 6`. `COUNTED` now also includes `material-fable-low` and `material-fable-medium`. SendMessage resumes were already counted. The refusal says "WRITE NEXT AND EXIT". `selftest_guard_session.py` is updated: G1-G6 allowed, G7 counter, G8/G9 the 7th is refused.

## Apply
```
git apply tools/bench/patches/chat-N1.patch
```

## Post-apply self-tests (run from the project root)
```
MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_prerun_diag.log -- py -u tools/bench/selftest_prerun_diag.py
MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_requires.log -- py -u tools/bench/selftest_requires.py
MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_guard_session.log -- py -u tools/bench/selftest_guard_session.py
MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_protocol.log -- py -u tools/bench/selftest_protocol.py
MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/selftest_protocol_wiring.log -- py -u tools/bench/selftest_protocol_wiring.py
MATERIAL=1 py tools/bgrun.py --max-min 6 --log tools/bench/selftest_stage_prerun_stageplan.log -- py -u tools/bench/selftest_stage_prerun_stageplan.py
MATERIAL=1 py tools/bgrun.py --max-min 6 --log tools/bench/selftest_stage_prerun_headcmp_79-6.log -- py -u tools/bench/selftest_stage_prerun_headcmp_79-6.py
```

## Results on the copies

| self-test | result |
|---|---|
| prerun_diag | 9/9 |
| requires | 7/7 |
| guard_session | 20/20 |
| protocol | 48/0 |
| stage_prerun_stageplan | 12/0, including launch_gate 28/0, retry_cap 8/0 and stagexec_gate 13/0 |
| headcmp_79-6 | 2/0 |
| protocol_wiring | 64/2 |

protocol_wiring's two failures:
- **F17** fails because the copy lives under %TEMP%, and `check_write` always allows %TEMP%.
- **D3** fails because the copy tree is incomplete.

The unpatched base in the same copy tree gives the same failures, so the patch does not cause them. Re-run protocol_wiring live after applying.

## Note
`selftest_guard_session.py` is inside the patch, not committed live, because the live hook still has cap 8 until the patch is applied.
