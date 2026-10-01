# Brief 125-1 — offline tooling: drain gate-fp queue (fp-10..fp-13) + term_class prerun refusal (PD251(b))

No LabVIEW. No other card is live while this runs (gate edits are allowed only then — PD251(b)).

## Part A — drain the four open gate false positives (cycle card `gates_due`: gate-fp DUE)
Entries: `tools/bench/gate_fp_queue.jsonl` lines 10–13. For each: fix the gate so the entry's command is classified
correctly, add a self-test case that reproduces the entry's command (refused before, allowed after) AND a case that a
really LabVIEW-touching command of the same shape is still refused, then
`py tools/gate_fp.py drain --id fp-N --fixed <path:line> --selftest <name>`.
- fp-10 (guard_peer): the reverse RULE-OFFLINE-CARD — an offline script (no LabVIEW import, hashlib only) under a
  `labview: none` card was refused on ANOTHER card's failing log. Scope: offline command under an offline card is not
  held back by a failing log it did not produce.
- fp-11 (guard_peer): `_IMPORT_RE` + import-following treats function-local imports in stagexec (never executed by a
  pure-Python self-test) as LabVIEW-touching. Measure what the self-test actually executes; do NOT blanket-exempt
  stagexec — a stagexec STAGE launch must still gate.
- fp-12 / fp-13 (guard_bash via `protocol.check_command`, `LV_IMPORT_RE` on the whole source): offline self-tests
  (`selftest_census_hookin_c123.py`, `stagexec.py selftest`) refused under `labview: none`. One fix for the class.
  A recipe/diagnostic that opens COM must still be refused under `labview: none`.
- Prefer one narrow, explicit rule (e.g. a named list of verified-offline self-test entry points, or the `selftest`
  argument of a module whose selftest path is COM-free as MEASURED) over a regex loosening. State which in the result.

## Part B — PD251(b): `stage_prerun.py --prerun` refuses a primitive create whose declared terminals lack `term_class`
- Cause record: `archive/peer/2026-10-01-c124-8-p3a-termclass-hyp.md`; 124-7 failed at op 1 because created-node
  terminals took stagesim's default `Terminal` while LabVIEW gives `ParameterTerminal` (`Increment`'s `x+1` =
  `OverridableParameterTerminal`).
- A new prerun line (next free X-number) FAILs when any create-primitive action's declared terminal list has an entry
  with no `term_class`. Self-test: a plan with one terminal missing `term_class` → FAIL; the same with it → PASS.
- Regression: `tools/bench/plan_ring_p3a.json` / `tools/recipes/stage_d1_ring_p3a.py` prerun still PASS (it declares
  classes row by row); P2b's prerun still PASS if it creates no primitives (record which).

## Existing self-tests that must stay green
launch_gate, stagexec selftest, census hook-in c123, case_frame_c124, guard_peer (all its selftests), any protocol
selftest. Report counts.

## Return
result/1 with: per fp entry → fixed path:line, self-test name + counts, drain status; the new X-line id and its
self-test counts; the regression prerun results. Return at the first unexpected result (finish the step, record facts).
