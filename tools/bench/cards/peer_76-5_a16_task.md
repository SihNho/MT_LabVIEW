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
