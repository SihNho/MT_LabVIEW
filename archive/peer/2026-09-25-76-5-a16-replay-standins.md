# 76-5-a16-replay-standins

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.8384  in 10 / out 5966 / cache-create 77485 / cache-read 380364  (74s, 7 turn(s))
- **date:** 2026-09-25 04:39:26
- **outcome:** ANSWERED (77s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed gate in tools/bench/replay_vis_76d.log (script tools/bench/diag_replay_standins.py, card 76-5).

FAILED GATE (log line 87): "A16 every pane object and the three new controls wired" - the panel_wiring readout showed
'Buffer Number Out' and 'Buffer Number Mode (Next)' on the SAME wire 681 and 'Buffer Number In' bare (wire 0).

CLAIM: this is a bug in OUR script, not a LabVIEW or verb defect. In diag_replay_standins.py (run 1 version) the
pass-through source label was picked by `lab(lambda l: l.startswith(a), False)` with a = "Buffer Number"; the front panel
(fp_labels order) lists the control 'Buffer Number Mode (Next)' before 'Buffer Number In', so the prefix match returned
Mode, and `gscript.connect_ctl_ind` faithfully wired Mode -> Buffer Number Out (log line 86:
"ctl->ind 'Buffer Number Out' <- 'Buffer Number Mode (Next)': None"). The verb did exactly what it was asked.
The patch now names the exact labels ("Buffer Number In" -> "Buffer Number Out", "Session In" -> "Session Out",
"error in" -> "error out") and makes A16 fatal with BN Out's wire == BN In's wire and Mode bare.

Everything else in the run passed (32/33): cal stand-in built (BN Out <- Decrement, BN In bare), both files ExecState 1
COLD, pane per slot == IMAQdx Get Image.vi, replace #529 keeps every wire. Already ruled out: a type mismatch (ES 1 at
B1 with Mode's enum coerced into U32 BN Out); the connect_ctl_ind verb itself (76-4 T1/T2 measured it 20x).

Give the strongest reason the claim is wrong, an alternative explanation, what would falsify it, and the cheapest
discriminating test. Read the log and the script; do not re-explain LabVIEW basics.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the root cause holds, but the claim is incomplete.** Log line 86 shows the script itself asked for `'Buffer Number Mode (Next)'` as the source. So the wrong wire came from our label pick, not from the verb. But calling it "a script bug, and everything else passed (32/33)" hides two more defects and one damaged file on disk.

### 1. Strongest reason the claim is wrong: the gate would have failed even with correct wiring
Run 1's A16 was named "**every pane object** and the three new controls wired". `Buffer Number Mode (Next)` is a pane object. In a correct pass-through, Mode is unused and has no wire, so this gate had to fail whatever the wiring was.

That makes two independent faults, not one: a wrong label selector and a wrong prediction for the gate. Proof is that the new gate at `tools/bench/diag_replay_standins.py:75-76` had to add both `"Mode" not in l` and `not pw[...Mode...]["wire"]`. The patch fixes both, but the claim credits the failure to the selector alone.

I could not check run 1's exact gate code. The script is untracked (`??` in git status), so no older version survives. This point rests on the gate's name in log line 87.

### 2. Alternative reading: the 32 passes are blind to the fault, and a wrong artefact was saved
Run 1's A16 was **not fatal**. The run went on and did this:
- Saved `claudeDev\replay\replay_imaqdx_get_image_buf.vi`, md5 `0d5377256895b548dc6fe41e1bb2cdf0` (log line 91), with **BN Out = Mode**, not BN In. That is a computation error under rule 1a.
- C1 (ExecState 1 cold), C2 (pane matches IMAQdx Get Image) and C3 (replace #529 keeps every wire) all **passed on that wrong file** (log lines 100-103).

So "everything else passed" is not evidence that the rest is right. None of the B and C gates can tell BN Out ← BN In from BN Out ← Mode. The value coerces into U32 and gives ES 1, as the brief itself admits. B2's "BN In bare" check (line 94) also passes trivially, because BN In was never wired.

The file-left-on-disk check H6 reports `added [] removed []` (line 127) although two VIs were saved under `replay\`. Either that folder is outside the check's view, or the files are intended. Either way, the wrong buf file is probably still there, and nothing marks it invalid.

### 3. What would falsify the claim
Either of these, after rerunning with exact labels:
- `panel_wiring` still shows BN Out's wire ≠ BN In's wire, or Mode with a wire.
- `pidx(W, "Buffer Number In")` returns the same index as Mode.

That would mean the fault is in the index path (fp_labels order vs the op's `Panel.Controls[]` order), not in the selector. I think this is unlikely, because Session (675/675) and error (678/678) wired correctly through the same `pidx`/`connect_ctl_ind` path.

Both use `Panel.Controls[]`, which is documented as tabbing order ([LabVIEW Wiki](https://labviewwiki.org/wiki/Panel_class/Controls()_property)). That order changes when controls are created or re-tabbed ([NI forum](https://forums.ni.com/t5/LabVIEW/Way-to-reorder-controls-in-front-panel/td-p/1950859)). The same order-dependent `startswith` pattern is still live at line 69 for `Image`. It is safe today only because there is one Image control and one Image indicator.

### 4. Cheapest discriminating test
No LabVIEW is needed. Read the saved `replay_imaqdx_get_image_buf.vi` (md5 0d53…) with one `panel_wiring` call, or read the JSON `s.R["panel"]` in `tools/bench/replay_vis_76d.json`.
- **Claim confirmed:** `Buffer Number Out.wire == Buffer Number Mode (Next).wire` and `Buffer Number In.wire == 0`.
- **Then:** mark that buf artefact invalid, and fail the rerun if it finds that md5.

Also add one line after the connects in the patched script: `assert pidx(W,"Buffer Number In") != pidx(W,"Buffer Number Mode (Next)")`. It costs nothing and separates the selector bug from an index-path bug.

**Bottom line:** I agree with the selector diagnosis, backed by log line 86. I reject "our bug only; the rest passed". Three corrections are owed:
- Record the gate-prediction fault as its own fault.
- Invalidate the run-1 buf file on disk.
- Accept that B1 and C1–C3 do not check who drives BN Out; only the new A16 does.

I would change my mind only if run 1's A16 already excluded Mode, which the gate's name contradicts.

Sources:
- [Panel class/Controls() property – LabVIEW Wiki](https://labviewwiki.org/wiki/Panel_class/Controls()_property)
- [Way to reorder controls in front panel – NI Community](https://forums.ni.com/t5/LabVIEW/Way-to-reorder-controls-in-front-panel/td-p/1950859)

## Sources

(extract from answer)

## What was done with it

Material session 76-5, 2026-09-25 04:4x (copied here by material session 76-6 from
`tools/bench/cards/disposition_76-5-a16.md`). ACCEPTED in full. (1) Selector fault: `tools/bench/diag_replay_standins.py`
now names every pass-through by exact label (Session/error/Buffer Number In -> Out) and the Image pair by exact label
(the order-dependent `startswith` at the Image line removed); new fatal gate A15 asserts `pidx("Buffer Number In") !=
pidx("Buffer Number Mode (Next)")`. (2) Gate-prediction fault recorded as its own fault: run 1's A16 excluded only labels
starting with "Mode", so it could not pass on a correct build; A16 now excludes Mode, requires Mode bare and BN Out on BN
In's wire, and is FATAL. (3) Run-1 buf artefact (md5 0d5377256895b548dc6fe41e1bb2cdf0, BN Out <- Mode) is INVALID; the
rerun overwrites it and fatal gate B1b refuses to continue if that md5 survives. B1/C1-C3 are acknowledged blind to who
drives BN Out; only A16 and the run tests in diag_replay_gbtest.py (image number == b) check it.
