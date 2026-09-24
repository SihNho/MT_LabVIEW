---
type: plan
kind: protocol
status: draft
date: 2026-09-24
tags: [protocol, sessions, flags, hooks]
---

# Session protocol v1 — DRAFT for the user's review

User, 2026-09-24: *"세션간의 통신 규약을 규격화하면 시간이나 에러를 크게 줄일 수 있지 않을까 싶은데. 플래그도 적극
활용하고"* → scope **all channels**, format **JSON**. Nothing below is built until the user agrees to this draft.

## Why

- Briefs are 700–900 words of prose that restate CLAUDE.md; prohibitions ("no LabVIEW", "do not edit STATUS") are
  sentences no machine checks.
- Returns are ≤30 lines of prose; the reader infers success, failure or blocked from wording. Cycle 71 lost 57 min
  waiting on a log that never started because a material session had been BLOCKED by a gate and nothing said so in a
  fixed place.
- Script logs mix the verdict into hundreds of FACT/PASS lines; bgrun's body scan then mistook quoted text for
  failures (cycles 70, 71, 73).

## Common rules

1. Every message is ONE JSON object with `"schema": "<name>/1"`. Unknown fields are refused by the validator.
2. Prose is allowed only in fields named `why` (≤ 300 chars) and `note` (≤ 300 chars). Rules are never restated;
   `rules` lists CLAUDE.md section names instead.
3. Every file reference is `{"path": ..., "md5": ...}` when the file is an input or an artefact.
4. Every card lives in `tools/bench/cards/` as `<kind>_<id>.json`; the id is `<cycle>-<seq>` (e.g. `74-03`). The
   prompt that carries a card is one line: `CARD tools/bench/cards/task_74-03.json`.
5. `tools/protocol.py validate <file>` checks a card against `docs/protocol/<schema>.json` (standard-library only).
   An invalid card is not dispatched.

## Channels

| # | from → to | card | replaces |
|---|---|---|---|
| C1 | runner → judgement session | `cycle/1` | the prompt text + STATUS reading for state |
| C2 | judgement → material / log-reader | `task/1` | prose briefs |
| C3 | material / log-reader → judgement | `result/1` | ≤30-line prose summaries |
| C4 | judgement → peer (hypothesis, prior-art, fact, outcome, retrospective) | `review/1` | peer task prose |
| C5 | peer → judgement | `verdict/1` | free answers parsed by regex |
| C6 | script → bgrun, guards, runner, audit | `RESULT` line (`result-line/1`) | bgrun's body scan |
| C7 | judgement session → runner (end of cycle) | `next/1` (`tools/bench/next.json`) | md5 of STATUS `## NEXT` prose |

STATUS.md stays human-readable; `next.json` is the machine copy of its first act.

## C1 `cycle/1` (runner → judgement)

```json
{"schema": "cycle/1", "cycle": 74, "rig_state": "조립", "model": "claude-opus-5-5", "effort": "medium",
 "firefighter": null,
 "bed": {"path": "claudeDev/D1_s4_loop17.vi", "md5": "4b621946492da3d2fbb96b6053e715ec"},
 "errorlist": {"path": "tools/bench/errorlist_D1_s4_loop17_<ts>.json", "verdict": "OK|MISMATCH"},
 "motor_session": "OK", "next": "tools/bench/next.json",
 "budget": {"minutes": 180, "dispatches": 8}, "rules": ["§3 judgement vs material", "Stages are SIMULATED"]}
```

## C2 `task/1` (judgement → material / log-reader)

```json
{"schema": "task/1", "id": "74-03", "kind": "build|measure|diagnose|doc|review-dispatch|read-log",
 "goal": "L2-1 move per plan_l2_1.json", "why": "one line",
 "inputs": [{"path": "tools/bench/plan_l2_1.json", "md5": "..."}],
 "pass": ["prerun PASS", "RESULT gates.fail == 0", "ExecState 1 warm+cold"],
 "outputs": ["claudeDev/D1_l2_1_<ts>.vi", "tools/bench/stage_d1_l2_1.log"],
 "flags": {"labview": "build", "gui": false, "hardware": "none", "run_vi": false,
           "write": ["tools/recipes/stage_d1_l2_*.py", "tools/bench/**"], "status_edit": false,
           "git_commit": true, "peers": ["hypothesis", "priorart"]},
 "budget": {"failures": 2, "minutes": 60}, "rules": ["Stages are SIMULATED", "Reference hygiene"]}
```

### Flags and who enforces them

| flag | values | enforced by |
|---|---|---|
| `labview` | `none` · `read` · `build` | `guard_bash.py`: `none` refuses any LabVIEW-touching command; `read` refuses recipes and saves |
| `gui` | `true` · `false` | `lv_gui.ps1` refuses state-changing actions unless true (on top of its Exception/Evidence gate) |
| `hardware` | `none` · `gate` | `motor_gate.py` refuses unless `gate` (rig state still decides) |
| `run_vi` | `false` (default) · `true` | `guard_bash.py` refuses Run/`ExecState`-changing run calls unless true |
| `write` | glob list | PreToolUse Edit/Write hook refuses paths outside the list |
| `status_edit` | bool | same hook, for `STATUS.md` / `CLAUDE.md` |
| `git_commit` | bool | `guard_bash.py` refuses `git commit` unless true |
| `peers` | list of `peer.ps1` roles | `peer.ps1` refuses other roles |

**OPEN (must be measured before building):** how a hook knows which card is active for a sub-agent. Candidates: the
hook input's agent/session id (if Claude Code exposes one to hooks for sub-agents), else a registry
`tools/bench/cards/active.json` keyed by the id the card's first command writes. Checked against Claude Code's hook
documentation, not assumed.

## C3 `result/1` (material / log-reader → judgement)

```json
{"schema": "result/1", "id": "74-03", "status": "PASS|FAIL|BLOCKED",
 "gates": {"pass": 38, "fail": 0}, "first_fail": null,
 "blocked_by": null,
 "artefacts": [{"path": "claudeDev/D1_l2_1_<ts>.vi", "md5": "..."}],
 "facts": ["≤ 10 items, ≤ 200 chars each"],
 "open": ["≤ 3 questions for the judgement session"],
 "cost": {"usd": 3.1, "minutes": 22, "labview_runs": 1}, "note": ""}
```

`blocked_by` = `{"device": "guard_bash launch gate", "message": "..."}` whenever a hook or gate refused the work. The
sub-agent's final message IS this JSON and the same object is written to `tools/bench/cards/result_<id>.json`.

## C4 `review/1` and C5 `verdict/1` (peers)

```json
{"schema": "review/1", "id": "74-05", "role": "hypothesis|priorart|fact|outcome|retrospective",
 "claim": "one sentence", "predicted": "...", "observed": "...",
 "ruled_out": ["≤ 3"], "attachments": [{"path": "...", "md5": "..."}], "ask": "refute"}
```

```json
{"schema": "verdict/1", "id": "74-05", "verdict": "refuted|supported|unverified|novel|settled-already|none",
 "alternative": "...", "discriminating_test": "...", "violations": [{"slug": "...", "loss_min": 0, "evidence": "file:line"}],
 "sources": ["url or file:line"], "note": ""}
```

`peer.ps1` appends its adversarial instruction set as today; the peer's answer must end with the verdict object.
The archive keeps the full exchange; gates read only the verdict.

## C6 `RESULT` line (script → machinery)

The LAST line a script prints:

```
RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":61,"fail":0},"first_fail":null,"artefacts":[{"path":"...","md5":"..."}]}
```

- bgrun, guard_peer, the runner's FAILED-RECIPES scan and audit_cycle read ONLY this line.
  `status != PASS` or `gates.fail > 0` ⇒ failure. No RESULT line ⇒ the exit code alone decides.
- bgrun's body scan (`rc=N`, leading `FAIL`) is REMOVED. stagekit prints the RESULT line from its gate counts, so
  "gates failed but exit 0" is still caught — by the script's own verdict, not by pattern-matching text.

## C7 `next/1` (end of cycle)

```json
{"schema": "next/1", "cycle": 74, "act": "L2-1 move", "task_kind": "build",
 "plan": {"path": "tools/bench/plan_l2_1.json", "md5": "..."}, "pass": ["..."], "blocked_by": null,
 "stop_requested": false, "note": ""}
```

The runner's "NEXT unchanged twice" stop and `guard_bash next_gate()` compare `next.json`, not prose md5.

## Measurement (before and after)

Baseline from cycles 68–73: brief length (words), return length, number of result-misread incidents (the 57-min
wait class), bgrun false failures, time from a sub-agent's end to the judgement session's next action. The same
numbers after v1 is live decide whether it stays.

## Build order (after agreement)

1. `docs/protocol/*.json` schemas + `tools/protocol.py validate` + self-test.
2. C6 RESULT line in stagekit + bgrun/guards read it; body scan removed (replay on the cycle 68–73 logs: 0 false
   failures, 0 missed real failures).
3. C2/C3 cards: `material.md`, `log-reader.md` rewritten; flag hooks after the OPEN question is measured.
4. C4/C5 in `peer.ps1`, `prior_art_review.py`, `retrospective.py`, `outcome_review.py`.
5. C1/C7 in `cycle_runner.py` + `cycle_prompt.md`.
6. Resume the parked work (launch gate, pre-run, error-list step) written against v1.
