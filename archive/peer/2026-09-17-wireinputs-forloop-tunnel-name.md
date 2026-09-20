# wireinputs-forloop-tunnel-name

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (179s)
- **why asked:** mandatory review of the FAILED PREDICTION at gate B2 of `tools/bench/diag_connectfromwire_facts.log` (the newline-labelled control wired with the correct source diagram index still raised 5001)
- **verdict:** REFUTED - my experiment could not support the conclusion I drew from it

## Question

LabVIEW VI Scripting (LabVIEW 2026, VI Server over COM), using the erdosmiller `lv-scripting` library. Attack the
reading below of a FAILED PREDICTION.

## The prediction that failed
`tools/bench/diag_connectfromwire_facts.log` gate B2 predicted: "with the correct source diagram index, wiring a
front-panel control to a node terminal BY NAME succeeds for both a label containing literal newlines and a label
without one." Observed: the no-newline case succeeded; the newline case failed.

## The raw machine facts
The helper is `wire_control` -> our op `OpWireCtl_v0.vi`, which calls the library's `Get Controls.vi` (control
LABELS on a given diagram -> terminal refnums) and then `Wire Inputs.vi` (those refnums + destination terminal
NAMES on a target node). Four calls on a fresh copy of a real VI, same VI, same run:

    label 'Auto-Reset' (no newline),    src_diagram_index=0   -> error 5001: LV-Scripting.lvlib:Get Controls.vi
    label 'Auto-Reset' (no newline),    src_diagram_index=43  -> NO error; sink wire 0 -> 1231   (SUCCESS)
    label 'Force\nsmoothing\nhalf-width' (two real newlines), src_diagram_index=0
                                                              -> error 5001: LV-Scripting.lvlib:Get Controls.vi
    label 'Force\nsmoothing\nhalf-width',  src_diagram_index=43
                                                              -> error 5001: LV-Scripting.lvlib:Wire Inputs.vi

Diagram index 43 is the diagram that owns BOTH control terminals (uid 17472 and uid 28148); both were confirmed
present on the panel with those exact labels, newlines included, by a separate reader. The destination in the
failing case is terminal index 7 of a `ForLoop` (uid 1359) whose terminal NAME, as recorded by our terminal
census, is the same string `'Force\nsmoothing\nhalf-width'`. The destination in the succeeding case is terminal
`'y'` of a Comparison primitive. One more measured detail: before the failing call we deleted the wire on that
ForLoop terminal to bare it, and the terminal came back reading a NON-ZERO wire (31059 -> 31166), i.e. it was not
actually bare.

## OUR READING, which you must try to destroy
"`Get Controls.vi` matched the newline label fine (the error moved past it to `Wire Inputs.vi`), so the newline is
not the problem on the SOURCE side; the remaining 5001 is `Wire Inputs.vi` failing to match the DESTINATION
terminal name on a ForLoop tunnel."

## Already ruled out here (do not spend your answer on these)
* Not a missing control: the same label, on the same diagram index, was found by `Get Controls.vi` in this run
  (the error moved to the next VI in the chain).
* Not a wrong diagram index: index 43 is the diagram that owns the control terminal, proven by the succeeding row.
* Not a newline-escaping bug in our Python: the string carries real newline bytes; the log prints its repr.

## What we need from you
1. The strongest reason our reading is WRONG.
2. At least one alternative explanation. In particular: does a `ForLoop`/structure TUNNEL terminal expose a
   matchable NAME to `Wire Inputs.vi` at all, or does that VI enumerate only a NODE's connector-pane / primitive
   terminal names? Does `Wire Inputs.vi` raise 5001 for a destination that exists but is ALREADY WIRED, rather
   than only for a missing name?
3. What observation would falsify our reading.
4. The cheapest discriminating test through VI Server scripting, naming properties/methods (and numeric ids where
   you know them).
Cite the erdosmiller lv-scripting source, NI documentation or forum threads by URL where you have them.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. Strongest reason the claim is wrong

The destination was not bare. Therefore the experiment cannot attribute error 5001 to terminal-name matching.

`Wire Inputs.vi` appearing in the error source establishes only that the error originated or propagated there—not which internal operation failed. Error 5001 has no universal LabVIEW meaning: codes 5000–9999 are reserved for user-defined errors, so this library can use 5001 for lookup failure, connection failure, or several conditions. [NI error-code reference](https://download.ni.com/support/manuals/321526b.pdf)

Thus the inference “5001 at `Wire Inputs.vi` ⇒ destination name was not found” is invalid, especially when the post-test `Connected Wire` value was nonzero.

2. Alternative explanations

The strongest alternative is: the name matched, but connection failed because the tunnel was already wired. `Terminal.Connected Wire` explicitly returns the attached wire (property ID `0x634A000`), while `Terminal.Connect Wire` is a separate operation (method ID `0x6349C03`). A failure after lookup would therefore still be reported from `Wire Inputs.vi`. [Terminal API](https://labviewwiki.org/wiki/Terminal_class)

A second alternative is tunnel-side identity. A For Loop tunnel is not one ordinary connector-pane terminal. It comprises a `LoopTunnel`, one outside `OuterTerminal`, and an inside `InnerTerminal`; structure tunnels may require selecting the correct inner or outer reference. [For Loop scripting anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html), [NI forum example](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/m-p/3945608)

Consequently:

- The census reading `Terminal.Name == "Force\nsmoothing\nhalf-width"` proves that one terminal object exposes that name; `Terminal.Name` is property `0x634A004`. [Terminal Name property](https://labviewwiki.org/wiki/Terminal_class/Name_property)
- It does not prove that `Wire Inputs.vi` selected that exact terminal reference or the correct tunnel side.
- `Node.Connect Wires` accepts source/sink terminal-name pairs (method `0x6358C00`), but structure-specific inner/outer resolution remains a separate issue. `Node.Terminals[]` is property `0x6359000`. [Node API](https://labviewwiki.org/wiki/Node_class)

I cannot establish from the public lv-scripting README whether `Wire Inputs.vi` calls `Node.Connect Wires`, manually searches `Node.Terminals[]`, or remaps connection errors to 5001; the repository documents the library at a high level but not that VI’s error contract. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting) A reporter listing of `Wire Inputs.vi` would settle that.

3. Observation that would falsify the claim

Either observation would falsify “destination-name matching failed”:

- With terminal 7 verified bare immediately before the call, the unchanged `Wire Inputs.vi` call succeeds using the same newline-containing name.
- Instrumentation/reporting shows that `Wire Inputs.vi` obtained the exact terminal-7 reference, after which `Connect Wire` produced the error.

The first would implicate occupancy. The second would directly prove that matching had already succeeded.

4. Cheapest discriminating test

On a disposable copy, through VI Server:

1. Read ForLoop `Node.Terminals[]` (`0x6359000`) and select index 7.
2. Log that terminal’s:
   - `Name` (`0x634A004`)
   - `Is Source?` (`0x634A003`)
   - `Diagram` (`0x634A002`)
   - `Connected Wire` (`0x634A000`)
3. If `Connected Wire` is valid, inspect its `Wire.Terminals[]` (`0x6371003`), delete that actual wire, reacquire the terminal reference, and verify `Connected Wire` is now null/invalid. [Wire terminal-list property](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property)
4. Call the unchanged `Wire Inputs.vi` once with the original newline name.
5. If it still returns 5001, bypass name matching and call terminal `Connect Wire` directly (`0x6349C03`) using the source terminal reference.

Interpretation:

- Bare `Wire Inputs.vi` succeeds: the original failure was occupancy, not name matching.
- Bare `Wire Inputs.vi` fails but direct `Connect Wire` succeeds: the library’s name/terminal-selection path cannot address that tunnel correctly.
- Both fail: investigate wrong inner/outer terminal, direction, diagram ownership, or datatype—not name matching alone.

## Sources

(extract from answer)

## What was done with it

**verdict: REFUTED, accepted in full. My own experiment was invalid for the question I asked of it, and the peer
found the defect in the log I sent it.**

The decisive line is in my own FACT row: `T2 sink #1359 t7 ... wire 31059 -> 31166 after baring`. **The
destination was NOT bare when `Wire Inputs.vi` was called** - my `bare_sink()` deleted the wire, ran Remove Bad
Wires, re-read the terminal, and got a *different non-zero* wire back, and I called it bared anyway. So error 5001
from `Wire Inputs.vi` cannot be attributed to destination-name matching: the peer's point is that 5001 is in
LabVIEW's user-defined range (5000-9999), the library may raise it for a lookup failure OR a connection failure,
and an occupied sink is a perfectly good reason for the latter.

**What SURVIVES from `diag_connectfromwire_facts.log`, unchanged:**
* `src_diagram_index` is the cause of run 9's 5001s at `Get Controls.vi`. `'Auto-Reset'` with index 43 wired
  cleanly, sink wire **0 -> 1231**, no error. That row's sink WAS bare (`wire 9806 -> 0 after baring`).
* The **newline is not the cause**: three of run 9's six failing labels carry no newline, and the newline label
  got past `Get Controls.vi` once the diagram index was right.

**What is WITHDRAWN:** the sentence "the remaining 5001 is `Wire Inputs.vi` failing to match the DESTINATION
terminal name on a ForLoop tunnel". `docs/d1-build-plan.md` §11u.2 is corrected to say the three ForLoop rows are
UNDIAGNOSED, with two live causes: an occupied sink, and the peer's second alternative - a For Loop tunnel is a
`LoopTunnel` with an *outside* and an *inside* terminal, so a name-addressed helper may resolve the wrong side
(`rajsite.github.io/unofficial-lvdocs` anatomy; NI forum 3945608).

**Carried into the next run as a method fix, not a note:** any "bare the sink" step must ASSERT the terminal reads
wire 0 afterwards and stop if it does not. `tools/recipes/build_opconnectfromwire_v0.py`'s T2 already reads the
terminal back after baring and prints both values; its gate T2c is `after and after != bare`, which is weaker than
it should be and is tightened to require `bare == 0`.

**Not adopted:** the peer's step 5 (bypass name matching and call `Terminal.Connect Wire` 6349C03 directly on that
tunnel) is exactly what `OpConnectNested_v1` already does, so it is not a new test - it is the route those three
rows are re-assigned to in `docs/d1-route-b-plan.md` §4. Whether it works on a ForLoop tunnel is measured when
route B's re-wire runs, not before.
