---
type: facts
status: current
date: 2026-10-08
card: 147-a1-5
---
# Card 147-a1-5 facts: runner `retro-undisposed` entry + gate-fp fp-53

## A. tools/cycle_runner.py
- md5 before `4c7c9be366d67640bf66042ed3e80b2a`, after `72ab9defc2c677ba6504d3d7f68ffdab` (`git diff --numstat`: 56 added, 0 removed).
- New lines `tools/cycle_runner.py:991-1043`, inserted between `gates_due()` and `gates_due_hook()`:
  - `:991-996` comment explaining why: `guard_peer.py:1181-1195` is a PreToolUse hook, and the runner's own child launch of the retrospective never passes through it.
  - `:997-998` `RETRO_DISPOSITION_H` / `RETRO_PLACEHOLDER_RE`, copied from `guard_peer.py:834-835`. It is a copy, not an import, because importing guard_peer also loads logclass/protocol/gateclass at `guard_peer.py:156-158`.
  - `:1001` `retro_undisposed(peer_dir)` uses the same rule as `guard_peer.undisposed()` (`guard_peer.py:838-855`):
    - takes the newest `*retrospective*.md` by mtime;
    - flags it when the disposition heading is missing, or when fewer than 80 characters remain after the placeholder lines are stripped;
    - returns that path, otherwise None.
  - `:1025` `retro_undisposed_item(n, peer_dir, runner_log)`:
    - returns `{"gate":"retro-undisposed","due":true,"detail":"<rel path>: ... (guard_peer.py:1181-1195)"}`;
    - logs `RETRO-UNDISPOSED <path> | <time> | cycle N | ...`;
    - any exception becomes one `RETRO-UNDISPOSED-CHECK error ...` log line and None. It never raises or refuses.
- `tools/cycle_runner.py:1078-1080`: in `gates_due_hook()` the item is appended to `items` before the `GATES-DUE` line. From there it reaches:
  - the cycle prompt's "GATES DUE" text, because `due_now` keeps every entry whose due is not False (`:1755-1759`);
  - the cycle card's `card["gates_due"]` (`:1123` after the shift).
- The item fits the schema: `docs/protocol/cycle.json:27-30` allows only `{gate, due, detail}` (additionalProperties false), so the path goes inside `detail`.
- `py -m py_compile tools/cycle_runner.py`: no output (OK).
- The runner that is running now started cycle 147 at 01:14 (`tools/bench/runner_supervisor.log` last lines), before this edit. It has the OLD code loaded and was not restarted. The new check first applies when a runner process starts after this edit.

## Self-test `tools/bench/selftest_cycle_runner_retro.py` -> `tools/bench/selftest_cycle_runner_retro.log`
Uses temp dirs only. In the gates_due_hook case, `gates_due` and `next_json_reading` are stubbed.
- (i) placeholder: item present with due True (log:4); `RETRO-UNDISPOSED` logged (log:3,5); gates_due_hook list carries it and logs `GATES-DUE ... retro-undisposed=DUE` (log:7-9); a cycle/1 card containing it validates (log:10).
- (ii) filled disposition: no item, nothing logged (log:11).
- (iii) no retrospective file: no item, no exception (log:12). Missing peer dir: no item, no exception (log:13).
- (iv) older placeholder plus newer filled file (newest by mtime decides): no item (log:14).
- log:16 `RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":9,"fail":0},...}`; log:17 `BGRUN END rc=0 after 1s`.

## Existing self-test `tools/bench/selftest_cycle_runner_ff.py` -> `tools/bench/selftest_cycle_runner_ff_c147a15.log`
- It now has 5 modes (`selftest_cycle_runner_ff.py:59-62`), not the 2 the brief expected. All 5 pass:
  - log:3-7 list the modes fail, fail2, samegate, newestpass and otherpass, each PASS;
  - log:8 `5/5 PASS`; log:9 RESULT pass 5 / fail 0; log:10 `BGRUN END rc=0 after 73s`.

## B. gate-fp entry fp-53 (tools/bench/gate_fp_queue.jsonl)
- Command: `py tools/gate_fp.py log --gate guard_assign --card 146-a2-1 ... --log tools/bench/cycle_146_handback_2.log` -> `LOGGED fp-53 gate=guard_assign checker=True`.
  - `checker` is set by `gate_fp.is_checker_gate(gate)` (`gate_fp.py:120`), not by this card.
- Quoted refusal (`handback_146_2.json:6`, `assign/state_146_2.json:34`): "card 146-a2-1: card text changes a memory limit: `memory_model` next to `change` (le changed; md5 old -> new reported; plans, preds, recipes, memory_model.json, s03/s04/s05 files and...), and the purpose does not name it".
- Why it is a false positive:
  - `guard_assign.py:321-328` matched the word "changed" within 60 characters of `memory_model`.
  - `task_146-a2-1.json:18` names memory_model.json as an UNCHANGED invariant.
  - The card's flags.write (`task_146-a2-1.json:22`) does not reach that file.
  - The cycle-146 judgement already reached the same reading (`cycle_146_handback_2.log:261` result text).
- md5 before -> after: guard_assign.py `b9dc09bb935d23b5649e852886e1ebc7` -> same; guard_peer.py `f30355d144a34cc0cffc47b6b3edfd05` -> same.

## Not touched
No LabVIEW, camera or motor. No real archived retrospective. No hook. The runner was not restarted.
