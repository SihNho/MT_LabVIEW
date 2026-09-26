# c103-wait-donor-closepanel

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1291  in 18 / out 6971 / cache-create 99323 / cache-read 855851  (84s, 17 turn(s))
- **date:** 2026-09-27 02:06:27
- **outcome:** ANSWERED (88s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed read-only diagnostic (card 103-1 P3).

Script: tools/bench/diag_c103_wait_donor.py ; log: tools/bench/diag_c103_wait_donor.log (run 1).
Prediction: the script scans claudeDev\OpPrimDonor_v0.vi (report_all Diagram + node_labels + report_all Node), then byte-copied NI
example candidates, for a node labelled `Wait (ms)`; no exception.
Observed (log line 4): after the D0 scan (0 hits) the call `g.close_panel(prim)` raised com_error 0x47D "Cannot close or set the
state of a closed front panel. The front panel must already be open before you close it". The whole try block aborted -> gate X FAIL.

MY CLAIM: this is a bug in MY script, not in LabVIEW or the ops. gscript.report_all / node_labels load the target VI through
VI Server WITHOUT opening its front panel, so FP.Close on it is illegal (0x47D). The fix is to treat close_panel as best-effort
(try/except) - the patched script now wraps every close_panel in `shut()`. Prior art: diag_c100_verbs_build.py:224-227 wrapped the
same call in try/except for the Max & Min donor, which supports the claim.

Please give: the strongest reason this claim is wrong; an alternative explanation (e.g. the panel WAS open and something else
closed it, or the reference was stale); what would falsify it; the cheapest discriminating test. Relevant code: tools/gscript.py
def close_panel (~line 1351), def report_all (~513), def node_labels (~612).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: your diagnosis holds, but the fix has a flaw.** I could not break the explanation for the 0x47D error. The fix, though, swallows more than the one error it was written for, and the calls it guards do nothing useful.

**1. Strongest reason the claim is wrong: the fix, not the diagnosis**
- `shut()` (`tools/bench/diag_c103_wait_donor.py:55-60`) catches every exception. That includes "RPC server unavailable" and the watchdog's modal-dialog `RuntimeError` (`tools/gscript.py:454`).
- This project already settled how to handle this error. `tools/bench/build_op_const_loopterm_77.py:114-118` swallows only `0x47D` and re-raises anything else. It was narrowed that way after the peer review in `archive/peer/2026-09-25-const-loopterm-77c.md`.
- The prior art you cited, `diag_c100_verbs_build.py:224-227`, is the weaker precedent. Its catch-all left no trace: `diag_c100_verbs_build4.log:6-10` shows no close_panel line at all. So it neither supports nor refutes anything.
- The close calls have no job in this script:
  - It kills LabVIEW before the re-copy (`K1`, line 98) and at exit, so no unload is needed.
  - `close_panel` opens a new reference with `GetVIReference` (`gscript.py:264`). If the VI had already left memory, that call loads it again. It can only load the VI, never usefully unload it.
- The better fix is to delete those calls, or to swallow only `0x47D`, as the loopterm_77 script does.

**2. Alternative explanation (same outcome, different mechanism)**
- The read ops never opened a panel and never held the target. Once each op's own reference closed, `OpPrimDonor_v0.vi` probably dropped out of memory. `close_panel` then loaded a fresh, panel-less copy and asked it to close its panel, which raised `0x47D`.
- Your wording, "loaded without opening its front panel", doesn't separate these two cases. It doesn't need to: in both, the panel was closed and the error is expected.
- "The panel was open and something closed it" has no support:
  - Nothing in `report_all` or `node_labels` (`gscript.py:513-543`, `612-643`) calls `OpenFrontPanel` or `ensure_loaded`.
  - The log shows no modal-dialog line.
  - `vi_ref` is a new reference on every call (`gscript.py:255-271`), so a stale reference is ruled out.
- External check: NI documents error 1149 as exactly "the panel was never open" (NI error-code list; the Error 1149 NI forum thread below).

**3. What would falsify it**
Either of these would:
- `0x47D` on a VI whose panel you opened with `open_panel()` just before, or
- the panel-open property reading True right before the failing close.

Against that, the machine has recorded this error many times after read-only ops. Examples: `tools/bench/allterms_s3.log:265`, `bench_map_a1.log:97`, `build_d1_m3a3b_d3.log:382-385`, `build_opfsinnertunnelconnect_v0.log:346-347`. None of those runs showed any other failure mode.

**4. Cheapest test that separates the two**
This is optional, since nothing in the card depends on the answer. Run it in a fresh LabVIEW on `OpPrimDonor_v0.vi`:
- **Arm A:** `report_all` → `close_panel`. Expect `0x47D`.
- **Arm B:** `open_panel` → `close_panel`. Expect no exception.

If Arm B also raises, the claim is wrong. Otherwise the claim stands, and the only change I'd make before the rerun is the narrower catch or deleting the calls.

**What would change my mind:** Arm B raising `0x47D`, or any logged `0x47D` on a VI that `open_panel` had just opened.

Sources:
- [General LabVIEW Error Codes (NI)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/general-labview-error-codes.html)
- [Error 1149 and Error 1000 at Invoke Node (NI Community)](https://forums.ni.com/t5/LabVIEW/Error-1149-and-Error-1000-occurred-at-Invode-Node-vi/td-p/4426143)
- [Maximizing/minimizing clone VI front panel windows (NI Community)](https://forums.ni.com/t5/LabVIEW/Maximizing-minimizing-clone-VI-front-panel-windows/td-p/731175)

## Sources

(extract from answer)

## What was done with it

ACCEPTED (card 103-1 material session, 2026-09-27): the diagnosis stands (read ops never open the panel; 0x47D expected), and the
review's better fix was taken over my catch-all `shut()`: every `close_panel` call in `tools/bench/diag_c103_wait_donor.py` is
DELETED (LabVIEW is killed before the re-copy and at exit, so no unload is needed; nothing is swallowed). The optional Arm A/B
test was not run — nothing in the card depends on it. Rerun: `tools/bench/diag_c103_wait_donor2.log`.
