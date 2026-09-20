# c58-typepair-a1-nonresult

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9606  in 30 / out 35183 / cache-create 201779 / cache-read 2025033  (483s, 22 turn(s))
- **date:** 2026-09-21 00:12:47
- **outcome:** ANSWERED (484s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm it.

## The claim under attack

> The line `FAIL  A1 diag_index(#639) resolves to an int  None (the historical 43 / 46 are NOT reused)` at
> `tools/bench/diag_s57_typepair.log:33` is a **NON-RESULT with an external cause**, not a defect in the
> measurement, in the gate `A1`, or in `gscript.diag_index`. The cause asserted: a second launch of the same
> batch (`tools/bench/diag_s57_typepair.py`) was started while the FIRST launch was still alive, and the second
> launch's own mandatory pre-batch LabVIEW restart killed the first run's COM link mid-phase-A, so
> `diag_index(#639)` returned `None` because the LabVIEW server had gone away under it
> (`com_error (-2147023170, ...)` / `(-2147023174, 'RPC ...')` in the same log). The asserted evidence that the
> instrument itself is sound: **run 2, in the SAME append-mode log, on the same script, same target, resolved
> `diag_index(#639) = 46` LIVE and ended `GATES 35 pass / 0 fail`, `BGRUN END rc=0 after 242s`.**
>
> Consequence asserted: the next cycle (58) may reuse the identical live-index-resolution pattern
> (`diag_index(uid)` resolved at run time, nothing cached) in a new diagnostic
> `tools/bench/diag_s58_boolcarrier.py` without changing gate `A1` or `diag_index`, provided only that the batch
> is never launched twice concurrently.

## What you must do

1. Give the **strongest reason the claim is wrong**. In particular: is "two concurrent launches" actually
   established by the log, or merely consistent with it? Could `diag_index` return `None` for reasons that have
   nothing to do with a dead COM link — e.g. the uid genuinely not being in the Traverse list at that moment,
   a class-filter difference, a load-state difference (`ensure_loaded`), or a silent swallow inside the wrapper?
2. Give an **alternative explanation** of the `A1` failure that survives the same evidence, and say what
   observable would separate it from the claim.
3. Say **what would falsify** the claim.
4. Name the **cheapest discriminating test** that cycle 58's diagnostic could carry as an extra gate, costing at
   most a few seconds, that would tell a dead-COM `None` apart from a real "uid not found" `None`.
5. Say explicitly whether reusing the pattern unchanged is defensible on this evidence, and if not, what the
   minimum change is.

## Files you may read (read-only; this project's directory)

- `tools/bench/diag_s57_typepair.log` — the log in question. It holds BOTH runs, appended. Run 1's failure is at
  line 33; run 2's summary is the last three lines.
- `tools/bench/diag_s57_typepair.py` — the script that produced both runs (unchanged between them).
- `tools/gscript.py` — `diag_index` and its neighbours; `_run`, `_err`, `ensure_loaded`, `report`, the poison /
  deadline machinery.
- `tools/bgrun.py` — how a run is deadlined and killed.
- `STATUS.md` — the cycle-57 lock keys record both runs and the handle/restart sequence.

## Already ruled out (do not spend your answer on these)

- "The gate threshold was wrong": `A1` asserts only that the returned value is an `int`; `None` is not an int on
  any reading.
- "The historical index 43/46 should have been hard-coded": the project rule (34(h)) forbids reusing a cached
  diagram index; run 2 resolved 46 live and that is the value used.
- "LabVIEW was never restarted": both runs restart LabVIEW themselves before doing anything (rule 44(e)); the
  handle counts for both restarts are in STATUS.

## Output contract

Plain text. No file writes. Lead with your verdict line in the form
`VERDICT: REFUTED — <what specifically does not hold>` or `VERDICT: SURVIVES — <the narrowest statement that survives>`,
then the five numbered answers above.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**VERDICT: REFUTED — the causal half (a dead COM link, not an addressing failure) survives; the two load-bearing clauses do not. "Not a defect in the measurement/gate" is false — gate `A1`, its log line, the run's `rc`, and the run's JSON all render a dead instrument and a genuine refutation identically, and this log contains three demonstrable instrument defects. And "provided only that the batch is never launched twice concurrently" is not a control: nothing in the fleet enforces single-flight, and "this batch launched twice" is one instance of a hazard class with at least four name-wide kill paths.**

---

**1. Strongest reason the claim is wrong**

Not the diagnosis — the *consequence*. Take the causal story as fully granted and the conclusion still does not follow.

First, on your specific sub-questions, I have to give the claim its due, because the code settles them:

- `diag_index` is `[o["uid"] for o in g.report_all(target,"Diagram")].index(uid)` (`tools/recipes/build_d1_v0.py:357-358`). A uid genuinely absent from the Traverse list raises **`ValueError`**, never `None`. The `None` in the log is manufactured by the script's own `except Exception` (`tools/bench/diag_s57_typepair.py:413-419`), and the captured text is `com_error`, not `ValueError`. So "the uid wasn't in the list", "a class-filter difference" and "an `ensure_loaded` state difference" are excluded **by type**, not by plausibility.
- The error *sequence* is the textbook signature of a server vanishing mid-call: `-2147023170` = 0x800706BE `RPC_S_CALL_FAILED` (channel established, the in-flight call failed) on the first uid, then `-2147023174` = 0x800706BA `RPC_S_SERVER_UNAVAILABLE` (cannot reach the server at all) on the next two (`log:30-32`).
- "The first launch was still alive when the second ran" **is** established, by interleaving: run 2's lines 21-29 were appended before run 1's lines 30-69, and each `print` is flushed per line through `bgrun`'s pump (`tools/bgrun.py:159-171, 219-224`).
- `gscript._recover_poison` — the one in-process path that kills LabVIEW by name (`tools/gscript.py:157-168`) — did **not** fire: it writes `POISONED:` / `RECOVERING from poison` to stderr, `bgrun` folds stderr into the log, and the log contains zero such lines.

What is **not** established, and what the proviso therefore cannot protect:

- **No single-flight mechanism exists.** `tools/hooks/guard_bash.py` has no lock, no concurrency check, nothing. AGENTS.md's "only one execution path may touch LabVIEW at a time" and the `labview-lock:` block are prose — in a STATUS.md that is now ~37k tokens, i.e. far past CLAUDE.md's own ~100-line threshold. A proviso enforced by intention is exactly the rule CLAUDE.md says to move into a hook after the second breach.
- **The hazard class is wider than "launched twice".** Every restart in this fleet kills **by process name**: `tools/lv_restart.py:13`, `tools/bench/bench_prep.py:76`, `tools/gscript.py:167`, plus each recipe's own `fresh()`. `bench_prep.main` additionally kills stray python COM clients by command-line match (`bench_prep.py:93,:100`). Any of these, in any process, ends every concurrent run's link. So does CLAUDE.md rule 2 — the user reclaiming LabVIEW — which leaves no log line at all.
- **The state the run was in is itself out of spec and unaddressed.** The instance was at **63,313 handles** when run 2 read it (`log:23`) against this fleet's own `HANDLE_LIMIT = 12000` (`tools/bench/bench_prep.py:61`) and a ~31,500 fresh baseline. Run 1 drove 30,700 → 63,313 in ~75 s of stage-1 work (`log:12` → `log:23`). A cycle-58 diagnostic that repeats stage 1 will do it again. "Never launch twice" says nothing about that.
- **And the failure is silent at every level a reader trusts.** `A1`'s gate line carries only `None` (`diag_s57_typepair.py:422-423`); the `com_error` text is on a separate FACT line. `bgrun`'s scanner turns any `FAIL` line into `rc=1` irrespective of cause (`tools/bgrun.py:215-217, 249-253`). So the next occurrence will look identical to a genuine refutation of the S3a addressing route — which is the expensive mistake this cycle is trying not to make.

On "not a defect in the measurement", three defects are in this very log:

1. **The swallow.** `except Exception → None` at the gate boundary, with the discriminating information demoted to prose. This project repaired precisely this class one cycle earlier in `gscript.create_indicator` (STATUS "THE SWALLOW IS REPAIRED AND THE REPAIR IS PROVEN"); the same standard applied here does not return "no defect".
2. **A canned false statement.** `log:37` reads *"PHASES F..I NOT ATTEMPTED: phase E did not save (ExecState None)"*. Run 1 stopped at `A1` and never reached phase E; no ExecState was ever read as `None`. It is the `else:` branch at `diag_s57_typepair.py:1080-1082` printing an unconditioned reason.
3. **Run 1's machine-readable record was destroyed.** `OUT` is a fixed path with no stamp (`diag_s57_typepair.py:164`), so run 2 overwrote it. On disk today `tools/bench/diag_s57_typepair.json` reads `"stamp": "20260920_234341"`, `"stopped_at": null`, `"fail": 0`. The "non-result" survives only as log prose; the artefact an auditor would read says the run passed 35/0.

Finally, **run 2 is not a replication.** It began from a *fresh* instance at 30,688 handles with no second launcher present. It shows the pattern works when nothing kills LabVIEW — which nobody disputed and which is not what `A1` failed on.

**2. Alternative explanation that survives the same evidence**

LabVIEW died in that window from something other than run 2's `D.fresh()`: a crash under handle pressure (>5× the fleet's own limit, and this project has a documented history of that instance degrading), or the user reclaiming LabVIEW, or any other name-wide kill. The evidence is byte-identical — BE then BA, `close_panel` raising (`log:34`), and `handles = 0` (`log:57`), which is **not** proof of death: `bench_prep.labview_handles` returns `0` on *any* unparsable result, and reads only `Select-Object -First 1`, so it cannot even report whether two LabVIEW processes existed (`bench_prep.py:64-71`).

The timing does not separate the two. Run 1 = `23:42:25` + `76 s` → `23:43:41`; run 2's START = `23:43:41`. The entire ordering rests on line interleaving, because **no timestamp in either run resolves finer than one second**, and run 2 must fit a `labview_handles` PowerShell call, three hash probes and a PowerShell `Stop-Process` spawn inside that same second for the claim's sequence to hold. It may well have; the log cannot say.

Separating observable: **the identity of the LabVIEW process** — PID and StartTime before and after. Under the claim there is a kill inside run 2's `D.fresh()` and the replacement PID's StartTime lands within a second or two of `log:70`. Under the alternative the process was already gone before that kill ran, and Windows will hold an Application Error / WER record for `LabVIEW.exe` at 23:43:4x — a `Stop-Process -Force` (TerminateProcess) leaves none. Neither was recorded. The Event Log check is still available today and costs seconds.

**3. What would falsify the claim**

- A PID/StartTime record showing the LabVIEW process run 1 was bound to was still alive after run 1 exited ⇒ run 2's restart did not kill it.
- A WER / Application Error event for `LabVIEW.exe` timestamped *before* run 2's `T2b` restart ⇒ it crashed; the second launch is innocent and the proviso is treating a coincidence as a cause.
- The same `A1` `com_error` recurring in a run that is demonstrably the only LabVIEW-touching process on the machine ⇒ the proviso is refuted outright.
- Conversely: `A1` returning `None` whose captured text is `ValueError: 639 is not in list` ⇒ the whole "external cause" framing collapses and it *is* an addressing defect.

**4. Cheapest discriminating gate for cycle 58**

Two changes, seconds in total, both reusing what exists:

- **Free — classify the exception instead of flattening it.** In the phase-A helper, record `type(e).__name__` and put it *in the gate detail*: `A1 diag_index(#639) resolves to an int | exc=<none|ValueError|com_error>`. Because `diag_index` is `.index()`, `ValueError` ⇒ a real "uid not found" and a real refutation; `com_error` ⇒ NON-RESULT, decided by type rather than by a story written afterwards. Zero new code paths, zero seconds.
- **~0.3 s — a process-identity witness.** At `T2b`, right after this run's own restart, record `(Get-Process LabVIEW).Id` and `.StartTime`; re-read both at the first failing gate. Add `A0 the LabVIEW process is the same PID/StartTime as this run's own restart`. Same shape as `bench_prep.labview_handles:64-71`, one PowerShell call — and make it `Select-Object Id,StartTime,HandleCount` (dropping `-First 1`) so the same call also reveals whether more than one LabVIEW process exists, which today's reader structurally cannot see. This one discriminator covers the whole hazard class: a second launch, a crash, the user reclaiming the instance, poison recovery.

Structural, also cheap, and the one I would argue is required before another overnight cycle: have `bgrun.py` take `tools/bench/.labview.lock` via `os.open(..., O_CREAT|O_EXCL)` holding pid + log name, and refuse with `BGRUN SINGLEFLIGHT held_by=<pid> log=<...>`. Milliseconds. It turns the proviso into a mechanism, and it is what AGENTS.md ("only one execution path may touch LabVIEW at a time") has always asserted without ever enforcing.

**5. Is reusing the pattern unchanged defensible?**

The **verb** is: `diag_index(uid)` resolved live, nothing cached, is correct and rule 34(h) requires it — run 2 resolved 46 live and again on the cold reopen (`log:79`, `log:158`). Keep it.

The **gate** is not. Minimum change before cycle 58 runs `diag_s58_boolcarrier.py`: (a) the exception class on the `A1` gate line, and (b) the PID/StartTime witness as `A0`. Also give the JSON a stamped filename so a second run cannot erase the first's readings, and delete the unconditioned "phase E did not save (ExecState …)" line at `diag_s57_typepair.py:1080-1082` — a log that states a reason which did not happen is worse than one that says nothing.

**What would change my mind:** a PID/StartTime pair, or a WER record, tying the death to run 2's `Stop-Process` rather than to the second in which it happened to occur. That would settle attribution — but it would not rescue the consequence, which fails on the absence of any enforcement, not on the attribution.

Sources: [0x800706BA RPC_S_SERVER_UNAVAILABLE](https://learn.microsoft.com/en-us/answers/questions/743186/the-rpc-server-is-unavailable-0x800706ba-win32-172) · [0x800706BE RPC_S_CALL_FAILED](https://learn.microsoft.com/en-us/answers/questions/2121043/remote-procedure-call-failed-hresult-0x800706be) · [0x800706BE "the remote procedure call failed"](https://docs.actian.com/openroad/6.2/ServerRef/Error_3a_0x800706BE__22The_remote_procedure_call_fai.htm)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (Pre-decided 41(b)). NOTHING IN IT WAS ACTED ON.** Deciding what to
take from a review is a JUDGEMENT act (CLAUDE.md §3, "What to accept from a review"); this was a material
session, dispatched only because `guard_peer.py` blocked the cycle-58 diagnostic over
`tools/bench/diag_s57_typepair.log:33` (`FAIL  A1 diag_index(#639) resolves to an int  None`). The block is
lifted by this exchange (claude / hypothesis, opus effort max + web, **ANSWERED 484 s, `$3.9606`**, in 30 /
out 35,183 / cache-create 201,779 / cache-read 2,025,033, 22 turns; `BGRUN END rc=0 after 484s`, runner log
`tools/bench/peer_c58_typepair_a1.log`).

**ORDERING, for the record, exactly as cycle 57 recorded its own:** `tools/bench/diag_s58_boolcarrier.py` was
written in full **before this review was dispatched**, and it was **NOT changed afterwards**. Its phase list is
the brief's, run unedited.

**Its verdict in one line:** `REFUTED — the causal half (a dead COM link, not an addressing failure) survives;
the two load-bearing clauses do not.`

**What it does NOT dispute:** that `diag_index(uid)` resolved LIVE with nothing cached is the correct verb and
that 34(h) requires it (§5: *"Keep it."*), and that run 2 resolved 46 live twice (`log:79`, `log:158`).

**What it refutes, and the three instrument defects it names on disk** (none repaired here):
1. *The swallow* — `except Exception → None` at the gate boundary flattens a dead instrument and a genuine
   refutation into the same `None`, the same log line, the same `rc` and the same JSON; it cites cycle 56's own
   repair of exactly this class in `gscript.create_indicator` as the standard.
2. *A canned false statement* — `diag_s57_typepair.log:37` reads "PHASES F..I NOT ATTEMPTED: phase E did not save
   (ExecState None)" although run 1 stopped at `A1` and never reached phase E; the `else:` branch at
   `diag_s57_typepair.py:1080-1082` prints an unconditioned reason.
3. *Run 1's machine-readable record was destroyed* — `OUT` is a fixed path with no stamp
   (`diag_s57_typepair.py:164`), so run 2 overwrote it; `tools/bench/diag_s57_typepair.json` today reads
   `"stamp": "20260920_234341"`, `"stopped_at": null`, `"fail": 0`, i.e. the artefact an auditor reads says 35/0.
It further refuses the consequence clause *"provided only that the batch is never launched twice concurrently"*
as **not a control**: nothing in the fleet enforces single-flight, and a second launch is one instance of a
hazard class with at least four name-wide kill paths (second launch, crash, the user reclaiming the instance,
poison recovery).

**Its falsifiers** (recorded, not run): a PID/StartTime record showing run 1's LabVIEW process outlived run 1;
a WER/Application-Error event for `LabVIEW.exe` stamped BEFORE run 2's `T2b` restart; the same `A1` `com_error`
in a run demonstrably alone on the machine; and — conversely — an `A1` `None` whose captured text is
`ValueError: 639 is not in list`, which would collapse the external-cause framing entirely.

**Its four proposals, ALL RECORDED AND NONE IMPLEMENTED:** (a) put `type(e).__name__` in the `A1` gate DETAIL so
`ValueError` (a real "uid not found") and `com_error` (a non-result) are separated by type; (b) an `A0`
process-identity witness recording `(Get-Process LabVIEW).Id` / `.StartTime` / `HandleCount` at the restart and
re-reading it at the first failing gate, shaped like `bench_prep.labview_handles:64-71` and without `-First 1` so
a second LabVIEW process becomes visible; (c) a stamped JSON filename so a second run cannot erase the first's
readings; (d) structurally, `bgrun.py` taking `tools/bench/.labview.lock` with `O_CREAT|O_EXCL` and refusing with
`BGRUN SINGLEFLIGHT held_by=<pid>`. **`bgrun.py`, `gscript.py`, `bench_prep.py` and
`tools/bench/diag_s57_typepair.py` were NOT touched, no `A0` gate was added, the cycle-58 JSON path was left as
written, and no lock file was created.** One fact worth stating flatly because it is a measurement and not a
concession: `diag_s58_boolcarrier.py`'s phase A already writes `"%s: %s" % (type(e).__name__, str(e)[:250])` into
a FACT line printed immediately before the `A1` gate — that was written before the review existed, and the gate
DETAIL still carries only the value, exactly as the review says.

Disposing these four proposals — and the `judgement-in-material` question of whether a material session should
have been the one to answer them — is left to the judgement session.
