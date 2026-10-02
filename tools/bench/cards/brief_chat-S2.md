# Brief chat-S2 - STOP gates vs LOG-only gates in stage builds (user 2026-10-03: "가, 나 둘 다 적용", "+-1개는 너무 적은듯")

Measured basis: cycles 130-140 dispatched ~76 cards, ~48 ended FAIL/BLOCKED, mostly on prediction mismatches that did
not change the product (tunnel/terminal names, +-1 counts of non-semantic classes, the check script's own arithmetic,
stale self-test fixtures, loose-end counts); each such stop costs a return, a hypothesis review (guard_peer) and a
re-issue. Run only while the runner is STOPPED (the chat dispatches this after cycle 141 ends).

## Rule to implement (user-approved design; the chat may adjust numbers only with the user)
1. **STOP gates (unchanged, fatal):** created-node primitive/function class (prim gate X17 / run-time), Is Broken? /
   ExecState where the plan expects a runnable state, computation_diff / cdiff vs prediction, lost data wires,
   input/bed md5 unchanged, MEMSTOP hard limit, the step-end Error List per-class exactness for every class EXCEPT
   loose ends, any count difference in SEMANTIC classes: function nodes of any kind, wires on a computation path,
   ControlTerminal/indicators, constants (incl. value), structures (While/For/Case/FlatSequence and their frames).
2. **LOG-only (record, continue, no per-mismatch review):** terminal/tunnel/face NAMES; count differences in
   NON-SEMANTIC classes (Terminal rows, Inner/Outer terminals, tunnels' face rows, scripting junk such as Invoke rows,
   loose-end wire counts) within max(5, 25 % of the predicted delta for that class); arithmetic of the check script
   itself (a gate whose own expected number is shown wrong by its own log); stale self-test fixtures.
   Beyond that tolerance a non-semantic difference is a STOP (it means the simulator model is badly wrong).
3. Every LOG-only mismatch is written as one JSON line to `tools/bench/gate_soft_log.jsonl` (cycle, card, script, gate,
   expected, measured, class, rule) and the cycle's judgement agent reviews them in one batch at cycle end.
4. `tools/hooks/guard_peer.py`: a log whose ONLY failures are LOG-only lines does not owe a hypothesis review (it is not
   a failed prediction under this rule). A log with any STOP-gate failure still owes one, as today.

## Do
- Find where gates are declared and evaluated (stagekit gate(), stagexec Executor gates incl. E1/CEN2/TD/FR/NG/FS/FU,
  stage_prerun X-checks, census_predict) and add the STOP/LOG classification in ONE place (a table in a small module
  imported by all), not per recipe. Recipes stay unchanged unless a recipe hard-codes a fatal flag on a LOG-only gate.
- Self-tests: semantic +1 stops; non-semantic +3 logs; non-semantic +40 % stops; a name mismatch logs; a STOP gate
  still stops; guard_peer: soft-only log -> no review owed, mixed log -> review owed. Re-run the existing
  stagekit/stagexec/stage_prerun/guard_peer self-tests (all must stay green or the difference be explained).
- Replay check (offline): classify the FAIL first_fail lines of results 130-141 under the new rule and report how many
  would have continued (facts only).
- Add a short paragraph to docs/d1/tooling.md (new decision, numbered after the last PD there) stating the rule and
  the user's words. Do NOT edit CLAUDE.md (the chat does).

## Limits
Offline only, no LabVIEW. Runner must be stopped (check STATUS STOP line + no cycle_runner process) before editing; if
it is running, return BLOCKED. git commit allowed for the touched tools/docs. Return one result/1 JSON object.
