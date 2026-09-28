# Brief chat-P1 - acceleration items 1-4, approved by the user 2026-09-28 08:4x

User: "1~4번은 적용하도록 하고. 5번은 어려움 / 지금 싸이클 끝내고 바로 적용해보자" (5 = user hand-editing: refused).
Baseline (cycles 110-115): one saved build step per 1.4-2.8 h cycle, $24-54; ~9 peer reviews/cycle; cards 13/30 PASS.
Design survey (read-only, 2026-09-28, this brief's source): below, verbatim decisions. Line numbers were read on
2026-09-28 ~09:00 and may have moved by a few lines; re-read before editing.

SAFETY GUARDS ARE OUT OF SCOPE AND MUST NOT CHANGE: motor gate / limits / reference, originals protection, LabVIEW
foreground-timeout + bgrun rules, rule 1a, CYCLE/PEER/LV/MATERIAL_GUARD_OFF env bypasses (no new bypass of any kind).

## 1. Pipeline: one LabVIEW card + one offline prep card at a time
- Nothing caps concurrent cards; what breaks it:
  (a) protocol.py:471-474 bind() read-modify-write of active.json, no lock -> add a lock file (os.open O_CREAT|O_EXCL,
      retry 50 x 100 ms) around _load_active/_save_active;
  (b) guard_session.py:141-166 same race on the session state -> same lock; track st["live"]=[{id,labview,t}] read from
      the `CARD <path>` in tool_input.prompt; a card stops being live when result_<id>.json exists or budget.minutes*1.5
      elapsed; refuse a dispatch when 2 are live or when the new card has labview!=none while a live one also has;
      an offline card dispatched while a LabVIEW card is live counts in a separate `prep` budget of 3, not MAX_DISPATCHES;
  (c) guard_cycle.py:406-419 premature_build (a): refuse only when the RUNNING prior-art log's BGRUN START names THIS
      recipe (`--recipe <this recipe>`), not any prior-art in flight;
  (d) guard_peer.py:839-847 newest_failing_log() is global -> exempt a caller bound to a card with flags.labview=="none"
      whose launched scripts all have script_touches_labview()==False (existing, :220); log RULE-OFFLINE-CARD.
- Provisional base for the N+1 plan: docs/protocol/stageplan.json gets base.provisional (bool) and base.sim_of
  {plan, md5}. The prep card plans N+1 on stagesim's end graph of N (tools/bench/sim/<stage>/), gets dry, prerun and
  prior-art PASS on it. stage_prerun._check_units (~:2421) REFUSES a launch whose plan base is provisional. New
  `py tools/stage_prerun.py --rebase <plan> --graph <real graph read of N's saved artefact>`: refuses if the current md5
  of sim_of.plan != sim_of.md5 (N's plan changed -> re-simulate); otherwise re-binds symbolic ids with the existing
  stagexec.translate + before/after terminal-table diff, writes the real path/md5, drops provisional. Plan md5 changes
  on rebase, so dry + prerun re-run (offline, seconds); prior-art stays valid (recipe .py unchanged).
- Prompts: tools/cycle_prompt.md (~:23-24, ~:62-66) PIPELINE paragraph: dispatch launch card N and prep card N+1 as two
  Agent calls in ONE message; prep card flags labview none, peers [priorart], write globs = plan/recipe for N+1.
  .claude/agents/material.md (~:55 "One COM client at a time") -> "a labview:none card never opens LabVIEW and may run
  beside one labview card"; same line in material-opus-max.md, material-fable-low.md, material-fable-medium.md.

## 2a. No prior-art review on a PROVEN pattern
- stage_prerun.proven_pattern(recipe): signature = set of stageplan action ops + create.class over plan_files(recipe)
  UNION the set of K./SX. functions the recipe calls (AST) (+ per-row route class if the dry log carries one). Proven =
  >=2 distinct stage keys in stage_runs.jsonl (by=="bgrun") whose last segment run_verdict is not failed and whose
  signature contains this recipe's signature. Record "pattern" in record_stage_run extras (~:2249-2255); for past runs
  recompute from the plan only when its md5 equals the prerun record's plan_md5s, else not counted (fail closed).
- guard_cycle.py ~:468-497: before the "NO PRIOR-ART REVIEW" refusal, if proven_pattern: log PROVEN-PATTERN, allow.
  Condition (a) and the verdict gate (~:608-648) unchanged.

## 2b. Retrospective every 3rd cycle, or when needed
- New tools/retro_due.py --cycle N (exit 1 = due): due when >=3 cycle cards since the newest answered retrospective;
  or this cycle has no PASS result with a claudeDev .vi artefact; or violations.py shows a slug at threshold-1.
  `--close` closes the session without a retrospective when not due.
- cycle_prompt.md (~:99-115): run retro_due; if due, retrospective as now; else `retro_due.py --cycle N --close`.
- guard_bash.py RETRO_RE (~:36, ~:524-532) also matches `retro_due.py ... --close` so next_gate and mark_retro_done hold.
- cycle_runner.py after land_retrospective (~:1431): if retro_due and none created in the window, run it synchronously.
- guard_cycle.py CYCLE_BUILD_BUDGET 10->30, CYCLE_HOURS 8->24 (backstop); _retro_debt (cycle_runner ~:836-854) reads them.

## 3. Gate false positives, batched
- New tools/gate_fp.py: `log --gate <hook|checker:label> --cmd "<cmd>" --why "<file:line evidence>" --card <id>` ->
  tools/bench/gate_fp_queue.jsonl {t,cycle,gate,cmd,first_refusal_line,why,card,status:"open"}, dedupe on gate+line;
  `drain --id .. --fixed <path:line> --selftest <name>` closes one.
- material*.md (~:71-72): on a refusal shown FALSE: log it, route around ONLY by (i) an equivalent command form the gate
  accepts, (ii) an existing release (FIXED:/REFUTED:, --retry-card), else (iii) BLOCKED with blocked_by.device
  "gate-fp:<id>". Never an env bypass; motor gate / originals / bgrun deadlines untouched.
- guard_peer.py after ~:867: if the failing log is named by an OPEN queue entry, the gate is a CHECKER (stage_prerun /
  stagekit gate label / guard_*; not a LabVIEW observation), and <=1 such entry per gate per cycle: allow, log RULE-GATE-FP.
- cycle_runner gates_due (~:886-914): `gate-fp` item due when >=5 open, oldest >=3 cycles, or one blocking; prompt: spend
  one tooling card to drain.

## 4. Bigger steps
- No code cap exists (prose only). Add advisory X14 in stage_prerun.prerun() (~:1809-1965): prints `rows N, budget 15|25
  (proven: <stages>)` via proven_pattern; WARN only, never FAIL.

## Docs (the chat edits CLAUDE.md itself; you do NOT edit CLAUDE.md or STATUS.md)
- docs/d1-loop12-17-split-plan.md: add a Pre-decided item "rows per step: <=15, up to ~25 on a proven pattern (user
  2026-09-28)" and point :15/:1902/:1937 at it (do not rewrite history lines).

## Self-tests (all green before commit; add the new cases)
selftest_guard_session, selftest_protocol, selftest_protocol_wiring, selftest_guard_cycle_fixed/_offline/_rerun,
selftest_guard_peer_* (all), selftest_c103d_hooks, selftest_stage_prerun_* (all), selftest_launch_gate,
selftest_c110_launchgate, selftest_next_gate_jev, selftest_cycle_runner, selftest_cycle_runner_ladder,
selftest_audit_c7. New cases: two concurrent binds both survive; a 2nd labview card refused; an offline card not blocked
by another card's failing log; provisional base refused at launch and accepted after --rebase; proven/unproven pattern;
retro_due due/not-due; gate_fp log/dedupe/drain + RULE-GATE-FP only for checker gates; X14 WARN.
