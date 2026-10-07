# Brief chat-T3 - fix three tool faults every bench arm hit (user 2026-10-07: "세 가지 다 고치도록")

Basis: tools/bench/livebench/report_4arms.md - all four arms lost time to the same faults; each arm fixed some inside
its own worktree (V6_bench\A, B, A13, A13K) and the next arm met them again. Fix them ONCE in the main repo.
OFFLINE ONLY: an experiment is running (STATUS rig-state 실험중) - no LabVIEW, no runner, keep CPU use light.

## 1. Adopt checker reads structured lines only (user: such flags belong in a fixed format, not in free text)
The adopt checker (gateclass HARD_MARK_RE / stagexec adopt_verdict) searched the whole run log for words like 'ExecStop'
and hit the script's own docstring echoed at the top of the log. Protocol already says scripts end with one
`RESULT {...}` line and machinery never scans log text. Make the executor write a structured `STOP {json}` line on every
real stop (ExecStop, MEMSTOP, traceback, STALL), and make adopt read ONLY RESULT / STOP lines. Then sweep tools/ for other
gates that grep free log text for a verdict and list them (fix the ones in the adopt / launch path; list the rest).
Reuse, after review, what the arms built (V6_bench\A, A13, A13K: the fp-43 / hard-mark work, gate_flips_*.json) - do not
copy blindly. Self-tests: docstring echo -> not a stop; real STOP line -> refused; no RESULT -> refused; the 20+ old logs
whose verdict would flip are listed with the reason (gate-flip report).

## 2. Created-object identity by record, not by inference
Today a plan names created objects by simulator ids (e.g. -28) and the rebase step guesses the real uid from shape,
connectivity and position; identical objects (two shift-register pairs) cannot be told apart - a fault that has recurred
for weeks. Change:
(a) CREATION MAP: when the executor creates an object, write `symbolic id -> real uid (+ class, owner)` to a per-stage
    creation-map file immediately; rebase binds created objects from that map first and falls back to inference only for
    objects that have no map entry (log every fallback).
(b) IN-VI TAG (prepare, do not enable): code path that writes the plan id into each created node's Description property
    and reads it back, behind a config switch default OFF - whether Description is scriptable for every class we create
    must be measured in LabVIEW after the experiment (write that test plan as an fn_records plan; terminals have no
    Description, so terminals are found as tagged node + terminal index).
Self-tests on recorded graphs: the s03->s04 case that every arm failed must bind with the map; identical-shape pairs bind
correctly; missing map entry -> inference fallback logged.

## 3. Simulator-only While loop
Measured by arm A13 (V6_bench\A13\tools\bench\cards\result_145-a3-1.json): a row-less While (#16483) gets loop_parent None
(stagexec.py:1270-1284), so node_uids lists it on every diagram (:3249-3253) - it appears inside body 29699 in the
simulation only. Fix: when a loop has no terminal rows, take its owner from the recorded owners map. Self-test with the
recorded graphs (diag_c145_a3_1_probe logs in that worktree) and the existing stagesim/stagexec self-tests.

## Do / limits
Existing self-tests green or explained. Record the decision as the next PD in docs/d1/tooling.md + INDEX. Commit by
explicit path. Edit tool only (no heredoc patches). labview none, hardware none. Return one result/1 JSON object, and
list what still needs a LabVIEW check after the experiment.

## 4. Bench cost collector counted old sessions (found 2026-10-07 by the chat's offline check)
tools/bench/livebench/lb_collect.py:124-135 takes every `"total_cost_usd"` line in any worktree log whose FILE mtime is
after t0. The A13 self-test log selftest_c144_a3_2_adopt.log echoed old cycle logs (cycle_86/91/131 of 09-26 / 10-02), so
$111.12 of main-tree spending was counted as A13's (corrected A13 total $123.11, not $234.23). Fix: count a session only
if its transcript started inside [t0, t1] (or its transcript is in the arm's own project folder), and ignore cost lines
inside echoed text; keep the log label of the session's own log. Re-collect all four arms and update the A13 row and the
"Rules 1-3" bullet in tools/bench/livebench/report_4arms.md.
