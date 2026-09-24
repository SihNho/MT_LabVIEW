# chatb3-samerow

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1834  in 24 / out 10032 / cache-create 92582 / cache-read 1115261  (110s, 21 turn(s))
- **date:** 2026-09-24 19:02:06
- **outcome:** ANSWERED (114s)
- **verdict-card:** VERDICT-CARD chatb3-samerow verdict=supported -> tools\bench\cards\verdict_chatb3-samerow.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id chatb3-samerow, role hypothesis) ---
CLAIM: run_selftests_chat_b2.log: selftest_guard_peer_samerow 4/10 (and budget R4, jev_ladder_action) failed ONLY because its fixture START line quotes `py tools/bgrun.py ... -- py <script>` and the new guard_peer.in_prediction_scope took bgrun.py as the script.
PREDICTED: all self-tests green after the session-protocol wiring (guard_peer scope limited to tools/recipes + tools/bench scripts, Jev and tools/*.py utilities exempt)
OBSERVED: samerow S0-S6b: the gate never blocked (rc 0) on a fixture log it must block on; budget R4 and jev_ladder_action fail because they re-run samerow
ALREADY RULED OUT: guard_peer_failre E1 is pre-existing: identical failure in tools/bench/selftest_c6_final_selftest_guard_peer_failre.log:38
ALREADY RULED OUT: the c6 baseline passed samerow 14/0 (tools/bench/selftest_c6_new_selftest_guard_peer_samerow.log) before this change
ATTACHMENT: tools/bench/run_selftests_chat_b2.log (md5 None)
ATTACHMENT: tools/bench/selftest_chatb2_selftest_guard_peer_samerow.log (md5 None)
ATTACHMENT: tools/bench/selftest_guard_peer_samerow.py (md5 None)
ATTACHMENT: tools/hooks/guard_peer.py (md5 None)
ATTACHMENT: tools/hooks/guard_peer.py.new (md5 None)
--- END REVIEW CARD ---

ATTACK this claim about run_selftests_chat_b2.log / run_selftests_chat_b2.py.

Context: tools/hooks/guard_peer.py gained `in_prediction_scope(start_line)` (session protocol v1 wiring): a bgrun log
arms the failed-prediction gate only when its LAST run's command runs a tools/recipes/*.py or tools/bench/*.py script
(not Jev). The live version takes the FIRST `.py` token of the START line's command. The fixture in
tools/bench/selftest_guard_peer_samerow.py:53 writes a START line whose command is
`py tools/bgrun.py --material --max-min 10 ... -- py ...stage...py`, so the first token is `tools/bgrun.py`.

The proposed fix is in tools/hooks/guard_peer.py.new: skip `bgrun.py` tokens and judge the first remaining script.

Questions: is the fixture's quoted-bgrun START line the ONLY cause of samerow S0-S6b not blocking? Could the scope
rule (or the C6 SWITCH_TS / RESULT-line verdict path in guard_peer.log_failure) also stop the gate from arming on
this fixture? Does real bgrun ever write a START line that begins with `py tools/bgrun.py` (read tools/bgrun.py's
`out(f"BGRUN START ...")` line)? Is exempting tools/*.py utilities and non-python commands from the gate a hole
(e.g. a PowerShell-driven build, motor_gate runs, gscript one-liners `py -c "import gscript"`)?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"chatb3-samerow","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**The claim holds as a cause, but I don't accept it as the whole diagnosis.** The quoted-bgrun START line is enough to explain samerow's 10 failures, and I found no second cause in this fixture. The bigger problem is that neither the live scope rule nor the `.new` fix does what the claim assumes, and the fix repairs a shape that real bgrun never writes.

**1. Strongest reason the claim is wrong: the fix is aimed at the wrong thing.**
- `tools/bgrun.py:192` writes `BGRUN START … min: {' '.join(cmd)}`, and `cmd` is the child command after `--`. I counted START lines under `tools/bench/*.log` that begin with `py tools/bgrun.py`: there are **0**.
- So `.new`'s extra rule, "skip bgrun.py tokens" (`guard_peer.py.new:216-219`), handles a shape that only exists in a test fixture (`selftest_guard_peer_samerow.py:53-54`).
- The same false belief appears in `log_script`'s docstring (`guard_peer.py:435-437`). S9 passes only because `log_script` takes the last match, not the first.
- The "first `.py` token" rule in `in_prediction_scope` (`guard_peer.py:213-220`) also misses real recipe runs. `build_d1_v0_run4.log:1` is `powershell … -Command py -u tools/lv_restart.py; py -u tools/recipes/build_d1_v0.py`. Its first token is a `tools/*.py` utility, so a failed D1 build would never arm the gate, with the live file or with `.new`.

**2. Other runs the new scope exempts that used to arm the gate**
- `py -c` gscript and LabVIEW one-liners have no `.py` token at all: `open_main_fp.log:1`, `close_main_fp.log:1`, `inspect_opnodeinfo.log:1`, `autonics_configure.log:1`.
- PowerShell scripts that move hardware: `p2_asi_set_limits.log:1`, `p2_pi_softlimit_test.log:1` (`tools/bench/*.ps1`).
- `tools/*.py` utilities such as `motor_gate.py` and `hash_probe.py` (e.g. `c68_pins.log:1`).

All of these are predictions about the machine or the rig. Before this change they armed the gate through FAILURE_RE or rc. Under the new rule they never do. The claim's "Jev and tools/*.py utilities exempt" treats this as intended. I'd count it as a silent loosening of CLAUDE.md §5 (a failed prediction triggers a mandatory peer review).

**3. Could something else explain samerow's failures? No.**
- **SWITCH_TS / RESULT verdict path:** the fixture's START time is 2026-09-22 18:00, earlier than `SWITCH_TS` 2026-09-24 18:25 (`protocol.py:58`). So `is_legacy` is True (`protocol.py:305-307`), there is no RESULT line, and the legacy FAILURE_RE path matches `STOP:` (`guard_peer.py:162-166`). Even after the switch, `BGRUN END rc=1` would fail it through `run_verdict` (`protocol.py:293`). Not a cause.
- **RUNNER_RE** (`guard_peer.py:97`): does not match the fixture.
- **SELFTEST_LOG_RE:** the fixture log is named `stage_row.log`, so it isn't excluded as a self-test log.
- **MAX_AGE_S:** the fixture file is fresh.
- **The backslash-newline in LOG_TMPL:** in a non-raw Python string it joins the two lines ("Ignored end of line", https://docs.python.org/3/reference/lexical_analysis.html). So the START line really is a single line.

The failure counts line up with the claim:
- `selftest_guard_peer_budget.py:172` runs samerow as R4: 1 failure (`run_selftests_chat_b2.log:7`).
- `selftest_jev_ladder_action.py:41` runs samerow as one of its suites: 10 failures, the same 10 (`run_selftests_chat_b2.log:12`).
- The ladder and jev suites passed, so their fixtures don't have the quoted-bgrun shape.

One limit: S0 prints only `rc=0` (`selftest_chatb2_…samerow.log:4`). It doesn't show whether `newest_failing_log()` returned None or something else returned 0. The code path makes None the only plausible reading, but the log doesn't prove it.

**4. What would falsify the claim:** force `in_prediction_scope` to always return True, run samerow, and still see S0 at rc=0.

**5. Cheapest test that separates the claim from the alternatives:** a Python REPL, no LabVIEW.
- `guard_peer.in_prediction_scope(<fixture START line>)` should give False on the live file and True on `.new`.
- Then patch `guard_peer.in_prediction_scope = lambda s: True` and re-run the samerow self-test. It should come back 14/0.
- Also call `in_prediction_scope` on `build_d1_v0_run4.log` line 1 and `open_main_fp.log` line 1. If they return False on both the live file and `.new`, the scope holes are confirmed.

What I'd do instead of `.new`: change the fixture to the real bgrun shape (`… min: py -u tools/recipes/X.py`). Then decide scope by any `tools/recipes|bench` script anywhere in the command (matching `log_script`'s last-match rule). Keep non-python and `py -c` runs in scope unless they are Jev or peer runs. Widening the exemption this way needs its own peer-reviewed decision; it shouldn't come in as a side effect of fixing a test.

VERDICT {"schema":"verdict/1","id":"chatb3-samerow","verdict":"supported","alternative":"The cause is right, but the first-.py scope rule, with or without .new, also exempts real prediction runs: a recipe behind a utility prefix (build_d1_v0_run4.log:1), py -c LabVIEW probes, and .ps1 motor scripts. Real bgrun never writes a START line with bgrun.py in it.","discriminating_test":"REPL: in_prediction_scope(fixture START) False live/True .new; patch it to lambda s: True and re-run samerow (expect 14/0); then call it on build_d1_v0_run4.log:1 and open_main_fp.log:1 (expect False on both = the holes).","violations":[],"sources":["tools/bgrun.py:192","tools/hooks/guard_peer.py:213-220","tools/hooks/guard_peer.py.new:216-219","tools/protocol.py:58","tools/protocol.py:305-307","tools/bench/build_d1_v0_run4.log:1","tools/bench/open_main_fp.log:1","tools/bench/p2_asi_set_limits.log:1","https://docs.python.org/3/reference/lexical_analysis.html"],"note":"Fix the fixture to real bgrun output rather than teaching the guard a fixture-only shape; judge scope by any recipes/bench script in the command, as log_script does; the py -c/.ps1/tools/*.py exemption needs its own reviewed decision."}

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

SAME-ROW: run_selftests_chat_b2.log (2026-09-24 19:04:42)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
