# Cloud run - assignment-agent bench (card chat-B6, branch `assign-bench-20261004`)

You are running a benchmark in a cloud container (Linux). No LabVIEW, no hardware, no GUI exist here; nothing below
touches them. Work only on branch `assign-bench-20261004`; push only that branch.

## What is measured

21 known-answer decision points from runner cycles 130-143 (`tools/bench/assignbench/cases.json`, built by
`make_cases.py`; evidence for every answer is in the case's `known_answer`). Each decision point = cycle purpose +
the task cards already done in that cycle (their result/1 objects) + minutes used; the answer is the next action
from a fixed menu (ISSUE / RETRY / ESCALATE / PREP / CLOSE / HANDBACK). Four arms:

| arm | model | effort |
|---|---|---|
| OM | claude-opus-5-5 | medium |
| OH | claude-opus-5-5 | high (today's judgement agent = baseline) |
| SM | claude-sonnet-5-5 | medium |
| SH | claude-sonnet-5-5 | high |

Scoring is mechanical (ACTION line + content regexes) plus one blind Opus-high scorer cell per case; USD and
minutes per arm-run come from each cell's JSON envelope.

## Steps (do them in order, stop and report if one fails)

1. `git fetch --unshallow || true` then `git fetch origin assign-bench-20261004 && git checkout assign-bench-20261004`.
   The case base commits (e.g. `689c565e`, `eed09beb`) must exist: `git cat-file -e eed09beb^{commit}`.
2. `which claude && claude --version` (the nested `claude -p` cells need the CLI). Use `python3`.
3. Stub proof (no model calls, ~1 min):
   `python3 -u tools/bench/assignbench/assignbench.py --stub hit --reps 1 --par 6 --tag stub_cloud`
   It must end with `RESULT {... "status": "PASS" ...}`. It does not need a new lock: `cases_lock.json` is committed
   and its rubric md5s must match (the run refuses otherwise - do NOT re-lock or edit cases.json or the rubrics).
4. Smoke (real cells, 1 case x 4 arms x 1 rep, no blind, ~$2):
   `python3 -u tools/bench/assignbench/assignbench.py --cases A21-c143-purpose-met --reps 1 --par 4 --no-blind --tag smoke_cloud`
   Check that each `tools/bench/assignbench/runs/smoke_cloud/A21-c143-purpose-met/*/answer.md` starts with
   `ACTION:` and that `meta.json` shows a non-zero `usd` and the arm's model in `cells[0].models_used`.
5. Full run (21 cases x 4 arms x 2 reps = 168 arm-runs + 21 blind scorer cells; expected ~$60-110, ~1-2 h):
   `python3 -u tools/bench/assignbench/assignbench.py --reps 2 --par 6 --guard-usd 150 --tag cloud 2>&1 | tee tools/bench/assignbench/cloud.log`
   A rate-limit / overload cell is re-queued from the start by the harness (<= 3 attempts); do not resume half-runs
   by hand. If the platform usage limit stops the run, wait for the renewal, then rerun step 5 from the beginning with
   a new `--tag` (half-run numbers never enter the report).
6. Write `tools/bench/assignbench/report_cloud.md`: start from the generated `report_cloud.md` (the harness writes it
   for `--tag cloud`) and ADD, facts only, no recommendation:
   - per arm: action match rate, forbidden-action rate, blind mean, usd / run, min / run (already in the table);
   - the cases where OH (baseline) and another arm differ in the answered ACTION, one line each;
   - validity: invalid arm-runs, re-queues, timeouts, arm-runs without a blind score, models seen in the envelopes;
   - wall-clock of the run and the total spend (arm-runs + blind scorers + smoke).
7. Commit to `assign-bench-20261004` only: `tools/bench/assignbench/report_cloud.md`, `results_cloud.json`,
   `results_smoke_cloud.json`, `results_stub_cloud.json`, `report_smoke_cloud.md`, `report_stub_cloud.md`, `cloud.log`
   and `tools/bench/assignbench/runs/` (answers + meta; `cell.log` files may be skipped if large). Message:
   `assignbench: cloud run (OM/OH/SM/SH, 21 cases x 2 reps)`. Then `git push origin assign-bench-20261004`.

## Limits

- Do not edit `cases.json`, `cases_lock.json`, the rubrics, `make_cases.py` or the scoring code (`tools/bench/decbench/`).
  A harness defect that blocks the run: fix the smallest thing, say exactly what changed in the report, rerun from step 3.
- Do not push any other branch, do not open a PR, do not touch `master`.
- Final message: the per-arm table and the total spend, nothing else.
