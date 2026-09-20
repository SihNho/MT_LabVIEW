---
type: archive
status: archived
date: 2026-09-18
tags: [status, relocation, cycle37, d1, route-b]
---

# STATUS narrative relocated at the cycle-37 material session (rule 4, STATUS.md was 137 lines)

Nothing here is rewritten. Each section is the VERBATIM text that stood in `STATUS.md` before the relocation;
`STATUS.md` keeps one line and a pointer per item.

## §1 — cycle-35 dispatches 1 + 2 (was the `✅ Cycle-35 dispatches 1 + 2` block)

✅ **Cycle-35 dispatches 1 + 2, VERBATIM in `archive/2026-09-18-status-cycle36-d1-run4.md` §5.** In one line each:
`Count` is CONTROL uid 28051 written by the event structure, **never a bead count** (Pre-decided 15,
`docs/NAMES.md` §`Count`); and D1's two authorisation flags stay **False permanently** (Pre-decided 13), the three
NO-ROUTE rows being decided by `docs/cycle15-plan.md` Pre-decided 1/2/3. ⚠️ **Run 4 measured that the `Z/dZ` half
of that disposition cannot be executed as written** — the registers half held.

## §2 — D1 route-B v1 run 4, the open construction question, and the failed-prediction review with judgement's four answers

🔴 **D1 ROUTE-B v1 RUN 4 IS THE CYCLE-36 BUILD LOG** — `tools/bench/build_d1_routeb_v1_run4.log`, 80 PASS / 1 FAIL
then `error 2` (memory full) inside `settle_index_modes`. **The ONE open construction question**: `Z/dZ` → `#2222`
t0 has **no by-index route** — `ControlTerminal #403`'s node index on `Diagram[56]` is `None`, and
`OpConnectNested_v1` addresses `Diagram[].Nodes[].Terminals[]` (`…run4.log:163-164`, MEASURED not inferred), so
cycle15 Pre-decided 3's REORDER cannot be executed as written. Every other fact of the run (baseline UNREAD 0,
preloaded live copy **1**, both shift registers moved with their nodes, md5 unchanged, handles) is VERBATIM in
**`archive/2026-09-18-status-cycle36-d1-run4.md` §4**.
🔴 **THE MANDATORY FAILED-PREDICTION REVIEW LANDED AND REFUTED BOTH OF THOSE CLAIMS** — `archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md` (claude/hypothesis opus-max, ANSWERED 566 s, $3.9657, `tools/bench/peer_routeb_run4.log`). (1) The SAME `count(LoopTunnel)` call **succeeded at 51,284 handles** at S1 (`…run4.log:26-27`), so the handle count is the control, not the cause; no reading brackets the failing call, and the **66 `s3w` rows that ran before the crash lost their whole ledger** because the print (`build_d1_routeb_v1.py:1529`) sits AFTER `settle_index_modes()` (`:1517`). (2) The `Z/dZ` route **is already coded in the recipe** at `:1257-1278` from built ops only and was skipped solely because `TEMP_SINK_AUTHORISED = False` (`:285`); and the **node moves at `s3():617-631` cut w730, not the `#403` reparent**. ✅ **ALL FOUR ANSWERED — cycle-36 judgement. Apply without re-asking.** **(a)** The review is **ACCEPTED IN FULL**: both refutations are read off our own log lines, not asserted. **(b) Pre-decided 13 is REVISED FOR ROW 3 ONLY.** `SR_QUEUE_AUTHORISED` stays **False permanently** — rows 1+2 did exactly what it decided, so its grounds are now *confirmed*, not merely assumed. `TEMP_SINK_AUTHORISED` becomes **True for the `Z/dZ` row, as the discriminating test**, because the premise of its refusal is measured false twice over: the REORDER has no by-index route (`…run4.log:163`) and it was aimed at the wrong cut (the moves at `s3():617-631` cut w730, not the `#403` reparent). The temp-sink path uses only ALREADY-BUILT ops (`OpCreateEqual_v0` → `wire_control` → `OpConnectFromWire_v0` → delete + `remove_bad_wires_scripted`), so this authorises **no new op and no new device** — Pre-decided 2 is untouched. Read the discriminator the recipe already prints at `:1288-1290`/`:1306`. **(c) YES to both instrumentation lines**: `fact(labview_handles())` immediately before `:1170`, and move the `done/failed/noroute` ledger print (`:1529`) **ABOVE** `settle_index_modes()` (`:1517`) — a run that loses 66 rows of ledger to an exception is the whole argument. **(d) YES, SCOPED**: on the **exception** path `finally:` (`:1793-1795`) **renames the copy aside** instead of deleting it — Pre-decided 14's "measure before you delete" means nothing if a crash erases the state first; the normal path still deletes, and the renamed copy is removed by the next run.

## §3 — STEP 0 of cycle 36 (the two machinery repairs)

✅ **STEP 0 WAS DONE IN CYCLE 36 — do NOT redo it** (the earlier "none done in cycle 36" line was wrong; the user's 21:3x order arrived *after* STEP 0 had run). Both repairs green (`tools/bench/repair_c36_selftest.log`, 5/0): `lv_stallcheck.ps1` identity-bound to `(pid, CreationDate)` + skips leaves with no bgrun log; `bgrun.py` sets `BGRUN_LOG`. F1–F4 RUN — F1 not evaluable, **F2/F3/F4 False**, so the cycle-35 stall record is a measured false positive that repair (i) would NOT have prevented. `bgrun.py` now has the `try/finally` its docstring always promised: green record **`tools/bench/c36_close_runner.log:13-14`** (8/0) — ⚠️ do NOT cite `selftest_bgrun_final_line.log`, whose last line is `BGRUN END rc=1`. `wait_logs.py`'s cp949 crash-on-success fixed (its flag is `--seconds`, not `--timeout-min`). ⚠️ **(e) is NOT closed and the class is narrower**: `wait_runner_exit` was never a failure; the other three were **external kills**, which no in-process handler reaches (test T1, `archive/peer/2026-09-18-c36-bgrun-finalline-selftest.md`).

## §4 — the cycle-36 retrospective and its three carried-forward findings

✅ **RETROSPECTIVE-CYCLE36 IS IN AND BOTH ITS VIOLATIONS ARE DISPOSED** — `archive/peer/2026-09-18-retrospective-cycle36.md`
(fable/medium, ANSWERED 424 s, $4.4824, `tools/bench/retro_c36.log`). `VIOLATION: wrong-ordering | loss_min=41 |
loss_usd=2.7466` and `VIOLATION: device-failed | loss_min=0` (threshold **1**) — both answered `DECISION: no-device`
in `docs/violation-decisions.md` at 23:09, so **`py tools/violations.py --due` is SILENT and `guard_cycle` will not
block run 5.** Three findings carried forward, none a gate: (i) a fresh stall record fired **during run 4**
(`tools/bench/stall_pid11424_221324.log:1`) and was discharged only incidentally, because `peer_routeb_run4` happens
to be newer — do not rely on that next time; (ii) 🔴 **`audit_cycle`'s C3/C5 cost figures are PHANTOM** — 649 of the
758 claimed minutes are impossible inside a 143-minute window, so **quote no cost number from this cycle's audit
until that is measured**; (iii) the bad `selftest_bgrun_final_line.log` citation, fixed above.

## §5 — the run-5 instruction block as cycle 36 wrote it (superseded by the cycle-37 dispatch)

🔵 **FIRST ACT OF THE NEXT SESSION — RUN 5, one material dispatch, one runner, one log.** Everything it needs is
decided; nothing below is a question. Patch `tools/recipes/build_d1_routeb_v1.py` with the FOUR changes judgement
answered this cycle (the ✅ block under run 4): (1) `TEMP_SINK_AUTHORISED = True` at `:285` — `Z/dZ` row only;
(2) `fact(labview_handles())` immediately before `:1170`; (3) move the ledger print `:1529` **above**
`settle_index_modes()` `:1517`; (4) `finally:` `:1793-1795` renames the copy aside on the **exception** path only.
Then run `py tools/bgrun.py --material --max-min 40 --log tools/bench/build_d1_routeb_v1_run5.log -- py -u
tools/recipes/build_d1_routeb_v1.py`. **What run 5 must return**: the S3w ledger (it survives the crash now), the
handle count bracketing `settle_index_modes()`, the `Z/dZ` discriminator at `:1288-1290`/`:1306`, and the S5/S6
`ExecState` with the preloaded re-read. A prior-art review is owed on the patched recipe before it launches
(`tools/stop_record.py` gates it) — run it in the SAME dispatch, do not make it a separate cycle.

---

# Relocated at the CLOSE of cycle 37 (dispatch 4, 2026-09-19) — the lock block's cycle-37 prose

Nothing below is rewritten. Each section is the VERBATIM text of one `labview-lock` key in `STATUS.md` before
the close-of-cycle relocation; `STATUS.md` keeps one line and a pointer per item.

## §6 — the `status:` line's RUN 5 prose (was the whole first half of `labview-lock: status:`)

> 🆕 **D1 ROUTE-B v2 RUN 5 RAN, cycle-37 MATERIAL, 2026-09-18 23:50 → 2026-09-19 00:18** — `tools/bench/build_d1_routeb_v2_run5.log`, `BGRUN END rc=1 after 1668s`, **80 PASS / 1 FAIL** (`:165`, the same `S3-zdz` row as run 4) then the SAME `error 2` crash, now at `:406` — but this time the instrumentation held. ✅ **THE S3w LEDGER SURVIVED (`:338`): attempted 66, WIRED 57, FAILED 6, NO-ROUTE 3** — the 66 rows run 4 lost. ✅ The handle control ran: **38,824 immediately before the failing `g.count(LoopTunnel)`** (`:405`) versus 51,284 when the same call SUCCEEDED in run 4 ⇒ handle pressure is refuted as the cause a second time. ✅ **`Z/dZ` REACHED THE TEMP SINK**: the RETRY logged and fell through (`:331`), the `Equal?` was created WELL-FORMED — `#10104`, census `{0:('x = y?',True,0),1:('y',False,0),2:('x',False,0)}` (`:332`), so the predicted silent-default-refnum failure did NOT occur — and the row then died one step later at **`wire_control ['Z/dZ'] -> Function.['x']: error 5001 LV-Scripting.lvlib:Get Controls.vi`** (`:402`). The 6 FAILED rows are all `report_all(Diagram) error 2` (`:396-401`), i.e. the same memory-full class arriving EARLIER than in run 4. ✅ S1 BASELINE `ExecState` 0 COLD ⇒ **UNREAD** (`:26`); the LIVE copy read **`ExecState 1` PRELOADED** (`:411`). ✅ Original md5 `2a78e17c449cacdaf5da389818526859` UNCHANGED before and after (`:4`, `:414`). ✅ The crash copy was **RENAMED ASIDE, not deleted**: `…\claudeDev\SCRATCH_routeb_235020_crash_001808.vi` (`:413`) — delete it in the next run's S0. Handles 33,956 → 54,610 (copy open) → 38,824 (pre-crash) → 30,687 (post-restart) → 48,792 (`:8,:27,:405,:409,:415`); LabVIEW is now pid 7412, up 00:17, 34,143 handles. ⚠️ A THIRD stall record of the known class fired ON THE BUILD CLIENT during the run: `tools/bench/stall_pid3792_235020.log:1` (00:00:36, pid 3792, 357 s of log silence while alive) — **`guard_peer` will hold the NEXT build until a review names it**.

🔴 **ONE SENTENCE OF THE ABOVE IS WITHDRAWN AS UNMEASURED, not refuted** — "handle pressure is refuted as the
cause a second time". `tools/bench/bench_prep.py:64-71` reads the KERNEL handle count
(`Get-Process LabVIEW … HandleCount`), which cannot see VI Server refnums, GDI objects or USER objects; and run
4's 51,284 and run 5's 38,824 were read from **two different LabVIEW processes**. The comparison never measured
the quantity it named. See `STATUS.md`'s replacement lines and
`archive/peer/2026-09-19-zdz-wirecontrol-5001.md`, which raised it.

## §7 — `purpose_run5b:` (run-5 prep) VERBATIM

> 🔵 **RUN 5 PREP, cycle 37.** The prior-art review is DISPOSED: six `FIXED:` release lines are written under `## What was done with it` in `archive/peer/2026-09-18-priorart-d1-routeb-run5.md`, the plan carries `docs/cycle27-plan.md` Pre-decided 13a, and `tools/recipes/build_d1_routeb_v2.py` has the six code changes (RETRY = logged control that FALLS THROUGH `:1311-1320`; A2 grounds restated `:332-342`/`:1340-1345`; A2 reader `:1360-1372`; `OUT`→`build_d1_routeb_v2.json` `:268` + label `:1940`; docstring citation `:219`; authorisation gate restated `:1666-1671`). **`tools/stop_record.py` now PASSES** — the refusal that remains is `guard_peer` on `tools/bench/stall_pid18476_232310.log` (fired on the session's own `wait_logs.py` waiter), so the mandatory hypothesis peer `stall-waitlogs-c37` is in flight (`tools/bench/peer_stall_waitlogs_c37.log`, started 23:42). LabVIEW pid 7280 up 22:43, **33,957 handles** (baseline ~31,500; 33,958 at 22:43 — unchanged, no restart). Prior text: 🔴 **RUN 5 DID NOT LAUNCH — the prior-art review STOPPED it, 2026-09-18 23:28.** `archive/peer/2026-09-18-priorart-d1-routeb-run5.md`, six slugs (`contradicted, settled-already, refuted-already, unread-evidence, already-measured, helper-exists`), `tools/bench/priorart_routeb_run5.log` `BGRUN END rc=0 after 420s`; a stop record is armed on `tools/recipes/build_d1_routeb_v2.py` sha `e4fc5bb197ef`. **Load-bearing finding A3: `TEMP_SINK_AUTHORISED = True` is INERT** — the v1/B2 RETRY at `v2:1267-1295` runs first whenever the sink is bare (`PREWIRED[ZDZ_SINK]["ct"]` is always set, `v2:720`, `…run4.log:162`), its `node_index_on` returns `None` for ControlTerminal `#403`, and it `return False`s at `:1278`, so `:1296` and the temp sink are never reached. No LabVIEW was driven; no VI was opened; the original was never addressed. Handles 33,958 (pid 7280, up 22:43). ⚠️ A fresh stall record `tools/bench/stall_pid18476_232310.log:1` fired on the session's OWN `wait_logs.py` waiter (it sleeps by design) — the same false-positive class as cycle 35. Prior text of this line: 🔵 **RUN 5 IN FLIGHT.** The four cycle-36 changes could NOT be applied to `build_d1_routeb_v1.py`: `tools/stop_record.py` keys its release to PATH+HASH and, by design (`docs/cycle18-plan.md` Pre-decided 2), a changed hash means UNREVIEWED — so after the edit EVERY command naming v1 was refused, the prior-art dispatch and `py_compile` included. v1 was therefore restored byte-for-byte to its released hash `9ff90ded8f01` (the launch gate itself confirmed this by allowing the next command that named it) and the four changes live in a byte copy, **`tools/recipes/build_d1_routeb_v2.py`**, prior-art reviewed on its own bytes (`tools/bench/priorart_routeb_run5.log`) before it launches. Handles before the build: 33,958 (instance 7280, up 22:43, baseline ~31,500 — no restart needed).

## §8 — `purpose_c37_peer:` (the run-5 failed-prediction review) VERBATIM

> ✅ **THE MANDATORY run-5 FAILED-PREDICTION REVIEW IS IN, ANSWERED 640 s / $3.9728** — `archive/peer/2026-09-19-zdz-wirecontrol-5001.md` (single claude/hypothesis arm, opus max; dispatch log `tools/bench/peer_zdz_5001.log`). It **REFUTES** judgement's claim: `Get Controls.vi` is the SOURCE-side resolver, so the name not found at `…run5.log:402` is `'Z/dZ'`, NOT `'x'`, and `Wire Inputs.vi` never ran — the `:332` census and the `:402` error address different objects, so there is no contradiction and no by-index fix is implied. Its alternative is a REPEAT of run 9's six 5001s: `build_d1_routeb_v2.py:1376-1377` searches `FRAME_BODY_UID = 639` (the STAY diagram) while `ControlTerminal #403` was already reparented to `Diagram#567` (`…run5.log:171`) and the sink was created on `Diagram[24]` (`:332`); the five sibling labels used the two-index retry at `:1567-1584` and all succeeded on 24. ⚠️ It also finds the `error 2` refutation in this file UNSOUND (`bench_prep.labview_handles()` reads KERNEL handles, `tools/bench/bench_prep.py:64-71`, which cannot see VI Server refnums / GDI / USER, and the two readings are from two different processes) and warns that `wire_source_owner` has never been measured on a `ControlTerminal` source (`:1386-1389`, which already killed a row at `…run5.log:404`). Nothing was patched: the route call is judgement's.

## §9 — `purpose_c37_repair:` (the stall watchdog repair, dispatch 3) VERBATIM

> ✅ **STALL WATCHDOG REPAIRED, cycle-37 MATERIAL dispatch 3, 2026-09-19 00:25** — the ONE clause the cycle-37 peer named (`archive/peer/2026-09-18-stall-waitlogs-c37.md` §5) is in `tools/lv_stallcheck.ps1:154-176`: the freshness skip now also reads EVERY `.log` path on the LEAF's own bound command line, so a waiter whose watched file is growing is skipped, while a waiter on a dead job and a real client still fire. Self-test `tools/bench/repair_c37_stall_selftest.py` **4 PASS / 0 FAIL** (`tools/bench/repair_c37_selftest.log`, `BGRUN END rc=0 after 19s`); G3 proves coverage for the real-client shape (`stall_pid11424_221324.log:3`, `stall_pid3792_235020.log:3` name no `.log`). ⚠️ Run 1 of the self-test FAILED G1/G4 and is the first section of the same log — a single `"([^"]+\.log)"|(\S+\.log)` regex swallowed the whole quoted `-c` blob; fixed by collecting candidates with two patterns. No new device; `tools/bench/stall_selftest_c37_*.log` scratch logs created and deleted in the same run. 🔴 **AND THE CLASS STILL FIRED — a FOURTH record, `tools/bench/stall_pid1556_002547.log:1` (00:28:39), on this session's own waiter, and `guard_peer` NOW BLOCKS THE NEXT BUILD ON IT** (probed, its own words: "latest failing log : tools\bench\stall_pid1556_002547.log"). The clause behaved EXACTLY as specified — both logs on that waiter's command line were stale (`repair_c37_selftest.log` 157 s, `peer_zdz_5001.log` 353 s, against the production `$LogFreshSeconds = 90`) — because the job it was watching was a `claude -p` peer cell, which is ALIVE and writes NOTHING to its bgrun log for its whole 640 s. **The residual class is "watched job alive but silent > 90 s", which the peer itself named as what its minimal clause would still get wrong; no further device was built (user's 08:53 order) and no further peer was dispatched — judgement's call.**

## §10 — what dispatch 4 did to that residual class (the ONE clause judgement authorised)

`tools/lv_stallcheck.ps1` gained a second, narrower clause immediately after the matrix-driver skip: a leaf whose
bound command line invokes `tools/wait_logs.py` is skipped unconditionally, because a waiter holds no LabVIEW
client at all and the watchdog's own sentence cannot be true of it. `$LogFreshSeconds` was NOT raised, no
liveness probe was added, and `guard_peer` was not touched — the build-client half of the class
(`stall_pid3792_235020.log`) keeps firing and keeps being discharged by the mandatory review, which is what the
rule intends.
