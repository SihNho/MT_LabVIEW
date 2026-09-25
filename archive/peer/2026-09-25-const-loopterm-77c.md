# const-loopterm-77c

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0177  in 20 / out 6831 / cache-create 85153 / cache-read 877955  (85s, 15 turn(s))
- **date:** 2026-09-25 06:08:57
- **outcome:** ANSWERED (89s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about tools/bench/const_loopterm_77c.log (script tools/bench/build_op_const_loopterm_77.py).

The run passed all 15 measurement gates (T1-T4 warm, H1-H2 handles/refs, C0-C4 COLD after save + LabVIEW restart)
and FAILED only "X no unhandled exception": LabVIEW error 1149 (0x47D) "Cannot close or set the state of a closed front
panel" raised by the teardown call g.close_panel(S) at the end of main(), after gate C4.

Claim: this is a defect of OUR script's teardown, not of the verb under test (gscript.create_const_loop_term). After
restart_labview() the cold instance opened S only by VI reference (exec_state / read_const / loop_end_ref / report_all),
never FP.Open, so FP.Close on a closed panel raises 1149. The patch wraps that one call in try/except
(build_op_const_loopterm_77.py:108-109). Planned action: rerun the patched script once to get a clean record.

Attack it: the strongest reason this is wrong (e.g. does any cold reader open the panel, so 1149 signals something
else; could the exception mask a later failure such as a lost value or a leaked reference); an alternative explanation;
what would falsify it; the cheapest discriminating test. Read the log and the script (lines 90-125).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the proximate cause is ours, but the patch is wrong as written.** The 1149 does come from our teardown, not from `create_const_loop_term`. But the bare `except Exception` at `build_op_const_loopterm_77.py:114-115` catches every exception, not just 1149, so the rerun it is meant to produce would not prove what it claims.

**1. Strongest reason the claim is wrong: the patch swallows everything, not 1149.**
- `g.close_panel` goes through `vi_ref` → `GetVIReference` → `_invoke`, with a poison check first (`gscript.py:263-264`, `1331-1332`). An RPC failure, a watchdog poison or a failed reload of S would all be caught and turned into a PASS on gate X.
- The fixed rerun can therefore never fail at that line, whatever LabVIEW does. It records "no exception" without discriminating.
- The call is also pointless. The panel was never opened cold, and the `finally` kills LabVIEW and deletes S (lines 122-125). Deleting the call is cleaner than guarding it.

**2. Did the exception hide a later failure? No, as far as our own tools can see.**
- `close_panel(S)` was the last statement of `main()`. Every measurement gate (C0-C4) ran and passed before it (`const_loopterm_77c.log:10-14`).
- The `finally` ran completely:
  - Both Z gates passed (`log:17-18`).
  - `ref_counts_end` shows opened 11, closed 11, live 0 (`const_loopterm_77.json:191-195`); `vi_ref` counts the close on the exception path too (`gscript.py:268-270`).
- Caveat: that counter cannot see refnums leaked inside an op VI (`gscript.py:247-249`). The handle-flatness gate H1 ran only on the warm instance (line 101), not after the restart. "No leak" holds at the COM level and warm only.

**3. Do any cold readers open the panel? No.**
- After `restart_labview()` and `g.reset()` (which clears `_loaded`, `gscript.py:280`), S is touched only by `exec_state`, `C.read_const`, `C.walk`, `loop_end_ref` and `report_all`.
- None of these calls `ensure_loaded` or `open_panel` (`build_opcreateconstonterm_v0.py:127-157`, `392-414`; `build_d1_v0.py:820-840`). Only the editing verbs call `ensure_loaded`.
- NI documents 1149 as exactly this condition: closing or setting the state of a front panel that is not open.

**Alternative explanation of the same evidence.** The panel may have been opened cold and then closed again, for example by an op VI that loads S by reference and unloads it on close, with `close_panel`'s own `GetVIReference` re-loading a fresh copy of S with no panel. The error would be identical. It matters little for teardown, but the log cannot tell the two apart.

**What would falsify the claim:**
- The panel reads as open just before the close in the cold instance.
- The caught text is anything other than `0x47D`.

**Cheapest discriminating test (no extra LabVIEW run needed to design it):**
- In the rerun you already plan, narrow the guard: catch the exception, re-raise unless its text contains `0x47D`, and store the text in `R`. That makes the patch able to fail.
- Optionally read the VI's front-panel-open property just before the call and record it. The exact ActiveX property name (`FPWinOpen` in older docs) is unverified here; check it first.
- One run then separates "1149 because the panel was never opened" from "some other failure hidden by the guard".
- A process note: this would be at least the fourth run of this script in cycle 77 (two in `const_loopterm_77.log`, plus 77c). Confirm whether `RETRY_CAP` applies to this bench before rerunning.

**What would change my mind:** a rerun where the narrowed guard catches a non-1149 error, or cold handles jumping when read around C0-C4.

Sources:
- [NI forum: Error 1149 and Error 1000 at Invoke Node](https://forums.ni.com/t5/LabVIEW/Error-1149-and-Error-1000-occurred-at-Invode-Node-vi/td-p/4426143)
- [NI forum: Maximizing/minimizing clone VI front panel windows (1149 from a reference to a panel that is not open)](https://forums.ni.com/t5/LabVIEW/Maximizing-minimizing-clone-VI-front-panel-windows/td-p/731175)
- [LabVIEW Wiki: Front Panel Window.Open property](https://labviewwiki.org/wiki/VI_class/Front_Panel_Window.Open_property)

## Sources

(extract from answer)

## What was done with it

Written 2026-09-25 by card chat-L2 from the record already committed (3701ba5, "Cycle 77: session outputs"); no new
judgement. ACCEPTED: finding 1 (the bare `except Exception` around the cold `close_panel` swallowed everything) — the
teardown guard was NARROWED to error 0x47D (1149) only and the stage re-run passed 16/0, its C5 catching exactly 1149
(`tools/bench/cards/result_77-4.json:14-15`, `const_loopterm_77d.log:14-18`). Findings 2-3 (no hidden later failure; no
cold reader opens the panel) matched the run's own gates C0-C4 and Z (`result_77-3.json:2`); nothing further done.
