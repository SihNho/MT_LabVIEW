---
card: 155-a1-1
status: current
date: 2026-10-09
---
# Brief 155-a1-1 - base-case frame addressing `#<diagram uid>` in stagexec + stagesim (docs/d1/ring-p5.md PD378(a)); OFFLINE, LabVIEW 0

Why: card 154-a4-1 could not compile P5-1b. Its actions 21 (`w_false_pass`) and 32 (`w_q_false`) address False-frame faces of
Case `#30726`, which P5-1a created and which is a BASE case now. The stage tools give frame names only to a case made by the
same plan (`stagexec.py:613-615` `case_frame_op`, `stagesim.py:797-800` `resolve_addr`), and the SR-face -> case-tunnel route
(`connect_term_uid` register_end_case_border, R1/R2) falls back to a plain `tunnel` on a base case (`stagexec.py:781`, needs
`created[loop] == "case"`). Read `tools/bench/diag_c154_a4_1_facts.md` (facts, 28 lines) and
`docs/d1/ring-p5.md` item 378 (decision) first. Nothing else.

## What to build (stagexec.py + stagesim.py ONLY; reuse what exists, add no new route family)
1. A `CaseStructure` that is in the REAL base graph is addressed like a plan-made case for `frame`: `frame: "#<diagram uid>"`
   names the frame by its MEASURED diagram uid (FS faces already do this: `stagexec.py:661-662`; follow that code path and call
   its helper rather than writing a second one - `docs/script-writing.md` rule 1). A uid that is not a frame of that case in the
   graph is a refusal with the case uid and the frames it does have.
2. The frame INDEX that the route needs is the position of that diagram uid in the graph's frame list for that case. MEASURE
   that this order is LabVIEW's frame index before relying on it and cite the measurement in the code comment (one line) and
   in the facts file. Evidence already on disk: P5-1a's Enqueue was planned on 'True' = index 1 and landed on `#30922`, the 2nd
   entry of `[30914, 30922]` of Case `#30726` in `tools/bench/graph_ring_p5s01a_20261009_103621.json` (bd67a511). Find one more
   case in a stored graph with a known frame content (e.g. the three cases cited at `stagesim.py:1315` /
   `tools/bench/selftest_c120_caseshape.log`, graph_qrt_pool_20260928.json #2222/#2857/#3826) and check the order there too.
   If the two disagree, STOP and return with both rows. Frame NAMES for base cases are not inferred.
3. `connect_term_uid` choosing the register_end_case_border (R1/R2) and `case_frame_wire` variants: the choice must treat a base
   case (in the graph) like a plan-made one, in BOTH stagexec (`stagexec.py:781` neighbourhood) and stagesim, so the same two
   groups that compiled to ops 20/21 and 15/22 in the whole-P5-1 compile do so on the base case too. Nothing about a
   plan-made case may change.
4. NEW self-test (a `tools/bench/selftest_c155_basecase_frame.py`, scope header `labview: none`, `hardware: none`, calls the
   shared stagekit/stagexec/stagesim functions; no copy of another self-test's logic). It replays RECORDED data: P5-1a's graph
   bd67a511 and the two refused actions as the brief of 154-a4-1 mapped them (CQ1 `#30726`, `#30914` False frame, TC1 `#31175`,
   TC2 `#31186`, SN1R `#30996`, QO1 `#31258`, EQ1 `#30756`; mapping in `tools/bench/prep_c154_a4_1_mk.log:7-15`; row content
   from `tools/bench/plan_ring_p5s01_in.json` actions 21 and 32). Cases: (a) `#30914` accepted and compiles to the same op
   kinds the whole-P5-1 compile had (`case_frame_wire`, `connect_term_uid` register_end_case_border); (b) a uid that is not a
   frame of that case is refused; (c) `frame: "False"` on a base case is still refused (no name inference); (d) a plan-made
   case behaves exactly as before.

## Regression the card must show (quote counts)
- `tools/bench/plan_ring_p5s01a.json` (ed62e8d6) recompiles to the SAME ops as before: compare the op list (kinds, order,
  args) before your edit and after, store the before-list first. Use the same entry point the P5-1a recipe used.
- Existing self-tests PASS with the same counts as their last logs: `py tools/stagexec.py selftest`,
  `py tools/stagesim.py selftest`, `tools/bench/selftest_c120_caseshape.py`, `selftest_case_frame_c124.py`,
  `selftest_stagexec_gate.py`, `selftest_stagesim_tunnel_naming.py`, `selftest_fs_c126.py`, `selftest_t6_regress.py`. Quote
  each (pass/fail). A pin-drift failure in a FROZEN cycle self-test is not yours: name it, do not re-pin it.
- Pins that must NOT change: stagekit aec03c6c, stage_prerun 9decb20f, vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e.
  Report the new md5 of stagexec.py and stagesim.py.

## Rules
Offline, no LabVIEW process before or after (check `tasklist`). No `tools/hooks/**` edit. No edit to any stored recipe, plan,
pred, or P5-1a file. A gate false positive in a hook: `py tools/gate_fp.py log ...` and go on. Every new public function gets a
docstring (first line: what it does and returns, names its self-test). Run the self-tests under `bgrun --material`.
If a change of the route cannot be shown to leave plan-made cases untouched, RETURN with the row - rule 1a / tool lift.

## Return conditions
The two frame-order measurements disagree; a plan-made case's compile changes; P5-1a's plan recompiles differently; an existing
self-test regresses; a protected md5 moved; a second failure at the same place.

## Report `tools/bench/diag_c155_a1_1_facts.md` (<= 40 lines)
The two frame-order measurements (file:line, case uid, frame list, expected vs observed); what changed (function, file:line);
new self-test counts; each existing self-test count; P5-1a recompile comparison (before/after op count + equal?); new md5 of
stagexec/stagesim; pins unchanged; `OPEN:` line. Facts only.
