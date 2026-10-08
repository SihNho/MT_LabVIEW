---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-5 — runner `retro-undisposed` gates_due entry + one gate-fp entry — OFFLINE tooling, ALONE (docs/violation-decisions.md:1935-1947)

No LabVIEW, camera or motor. Nothing else runs beside this card (it edits a gate/runner tool).

## A. `tools/cycle_runner.py` — undisposed-retrospective check (violation decision 2026-10-08 01:16, `docs/violation-decisions.md:1935-1947`)
Background: `tools/hooks/guard_peer.py:1181-1195` refuses a retrospective launch while the newest archived retrospective's `## What was done with it` section is still the
placeholder ("(Claude fills in)" or whatever that hook tests). It is a PreToolUse hook, so the runner's own child-process retrospective launch
(`tools/cycle_runner.py:633-637`) never runs it. The runner must run the SAME test itself.
1. Read the guard_peer test (:1181-1195) and reuse its definition of "placeholder" (import the function if it is importable without side effects, else copy the
   regex and cite the line; do NOT edit guard_peer.py). Newest archived retrospective = the newest `archive/peer/*retrospective*.md` by its date/cycle (same rule as the hook).
2. Add a function in `cycle_runner.py` that returns the newest retrospective's path when its disposition is still the placeholder, else None.
3. At the point where `gates_due` (`cycle_runner.py:952` `gates_due()`, `:991` `gates_due_hook`, `:1067` `card["gates_due"]`) builds the next cycle card's list: when the check
   returns a path, add an entry `retro-undisposed` with `due: true`, the path, and one sentence, in the same shape as the existing entries; and print/log a
   `RETRO-UNDISPOSED <path>` line to the runner log. It must NOT refuse, raise or stop the runner in any case (a refusal would stall an unattended runner); an error inside
   the check is swallowed into one log line.
4. Self-test (a new `tools/bench/selftest_cycle_runner_retro.py`, modelled on `selftest_cycle_runner_ff.py`, using a temp directory, touching no real archive file):
   (i) placeholder file -> entry present, due true, RETRO-UNDISPOSED logged, no exception; (ii) filled file -> entry absent, nothing logged. Plus (iii) no retrospective
   file at all -> no entry, no exception. Run it; quote the result line. Then run the existing `selftest_cycle_runner_ff.py` (expected 2/2) and a `py -m py_compile`
   of cycle_runner.py to show nothing else broke. The runner process that is running now has already loaded the old code: say so; do not restart it.
5. Report the diff of `cycle_runner.py` by file:line and its md5 before/after.

## B. gate-fp entry for the 146-a2-1 refusal (ONE `tools/gate_fp.py` entry, no hook edited for it)
`tools/hooks/guard_assign.py:321-328` refused card 146-a2-1 in cycle 146 (assignment guard; see `tools/bench/cards/handback_146_2.json`, `tools/bench/cycle_146_handback_2.log`,
`tools/bench/assign/state_146_2.json` for the exact refusal text). The cycle-147 purpose says it is a false positive of the gate and that it is logged, not fixed. Read how
`tools/gate_fp.py` is used (usage line, previous rows in `tools/bench/gate_fp_queue.jsonl`, e.g. fp-51 and fp-52 from this cycle for the shape) and add exactly ONE entry:
the gate, the card id, the quoted refusal, why it was a false positive (one sentence, from the evidence in those files), and the cite `guard_assign.py:321-328`.
If those files show the refusal was NOT a false positive, log nothing and RETURN with what they show. `guard_assign.py` stays byte-identical (md5 before/after).

## Never
LabVIEW, camera, motor; editing guard_peer.py, guard_assign.py or any other hook; refusing/stopping the runner from the new check; touching a real archived retrospective;
restarting the runner. A tool fault you cannot fix inside cycle_runner.py = RETURN with the file:line.

## Return
`result/1` and facts `tools/bench/diag_c147_a1_5_facts.md`: the cycle_runner diff by file:line + md5 before/after, the three self-test cases + result lines, the existing
selftest result, the gate-fp entry id + text, guard_assign / guard_peer md5 before/after.
