ATTACK the three claims below. They are a MATERIAL session's readings of `tools/bench/diag_c83_connect2x2.log`
(run 1 of cycle 83, `tools/bench/diag_c83_connect2x2.py`, 37 gates pass / 5 fail, rc=1, 173 s) and of
`tools/bench/diag_c83_connect2x2.json`. Both files, the recipe `tools/recipes/build_opfsinnertunnelconnect_v0.py`
and `tools/gscript.py` are in the project directory and readable. Give me the strongest reason each claim is
WRONG, an alternative explanation, what would falsify it, and the cheapest discriminating test.

## What the run did

The subject is `Terminal.Connect Wire` 6349C03 declining SILENTLY on one specific write: attaching a
`FlatSequenceInnerTunnel` LeftTerm (`#7488`, owner FSIT `#7468`) to a While-loop shift-register OUTER terminal
(`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`) on a scratch copy of a 307 KB VI, after deleting wire 7506.
Three explanations survived a prior review (`archive/peer/2026-09-22-c82-bare-source.md`):
 (a) the ROLES are inverted for CREATION (`Wire Source` is documented as the wire's ORIGINAL SOURCE, and the op
     hands it the SINK while the Invoke sits on the SOURCE terminal);
 (b) `Auto Route?` is at its default FALSE and no op in the fleet wires it;
 (c) the Invoke's OWN `error out` may never reach the op's `error out`, so "silent" is so far only "quiet".

Run 1: (i) attached an indicator to the Invoke's error chain in the op; (ii) ran a 2x2 (Invoke on the SINK vs on
the SOURCE) x (Auto Route TRUE vs FALSE) on FOUR fresh TRIVIAL scratch VIs, each holding two bare
`VI Server:GObject` Property nodes, driven through a scratch copy of `OpConnect_v0.vi` carrying a new
`Auto Route?` control; (iii) ran the same four cells on the real pair, each on its own scratch copy of the bed.

## CLAIM 1 - the trivial 2x2 refutes (a) and (b)

All four trivial cells CREATED the wire: `wire_delta` 1, the SAME wire uid 93 on both terminal ends, junk Invoke
0 (`diag_c83_connect2x2.log:49,55,61,67`). Cells A1/A2 put the Invoke on the SINK (`reference`, is_source False)
with the SOURCE (`reference out`, is_source True) as `Wire Source`; B1/B2 put the Invoke on the SOURCE with the
SINK as `Wire Source`. So I claim: 6349C03 creates a wire between two bare terminals in BOTH role assignments and
at BOTH `Auto Route?` values, therefore neither (a) nor (b) can be the reason the real-pair write declines.

## CLAIM 2 - (b) is refuted on the real pair too, and (c) is confirmed in a stronger form than expected

On the real pair, `Auto Route?` TRUE changed nothing: border terminal wire 0, `wire_delta` 0, `UID 2` 0, one junk
`Invoke` minted (`diag_c83_connect2x2.log`, cells S2 B1 and S2 B2). And the op's `error out` indicator, poisoned
with `(True, 999999, "POISON")` before every call, came back STILL CARRYING THE POISON in every cell of both
steps - so that indicator is never written by a run, and cycle 82's evidence "`err=''` on 20/20 calls" was
reading an unwired indicator's saved default, not an absence of errors.

## CLAIM 3 - the new `error 1055` is caused by run 1 itself, not by the machine's answer to the question

The op's three per-stage error columns, which cycle 82 recorded as EMPTY with `term_uid` 7488 and `uid_back` 7468
on the same bed (`tools/bench/build_opfsinnertunnelconnect_v0.log`, gate G4 arm 2), now read
`error 1055: To More Specific Class in UID to GObject Reference.vi->OpFsInnerTunnelConnect_v0.vi` and
`error 1055: Property Node`, with `term_uid` and `uid_back` both stuck at their poison 0
(`diag_c83_connect2x2.json`, cells S2 B1 / S2 B2). Between the two runs exactly two things changed: run 1 EDITED
the op (one `create_indicator` on the `Clear Errors.vi` node's `error out`, md5
`c0d5efe3389b0dea388ee565433fb683` -> `cda1e36ee394ccd6bf0f1c1108d76249`), and run 1 poisoned several of the
op's indicators before each call. I claim the 1055 is an ARTEFACT of one of those two, and that the FSIT uid
7468 is still resolvable on the bed.

## CLAIM 4 - the swapped-roles op copy is repairable

Cells A1/A2 on the real pair could not run: the scratch copy of the op with the Invoke's `reference` and
`Wire Source` feeds EXCHANGED came out `ExecState` 0 even though both new wires verified on both ends
(`diag_c83_connect2x2.log:76-83`). The diagnostic lists `(241, 'reference')` and `(187, 'reference')` among the
unwired non-error sinks. I claim the cause is that the two deleted NETS had OTHER consumers besides the Invoke -
the readback Property nodes - and that re-branching every recorded consumer onto its original source after the
crosswise re-connect will make the swapped copy legal, so the A cells can run.

## Already ruled out, on the machine, not by argument

- Addressing: the loop-node uid echo reads 23032 (MATCH) and the border terminal is asserted wire 0 immediately
  before every call.
- A stale readout: every indicator read is poisoned per call, `Is Broken?` poisoned True.
- The junk node: exactly 1 stray `Invoke` per real-pair call, 0 per trivial call - so the Invoke DID execute.
- "The method declines on a bare `Wire Source`": already refuted in `tools/bench/build_harness_copyloop2.log:31-40`
  and again by run 1's four trivial cells.

## What I want from you

For each claim: the strongest reason it is wrong, an alternative explanation, the observation that would falsify
it, and ONE cheapest discriminating test I can run in a single script on a scratch copy (no new op, no new
method id, nothing saved to the bed). Say explicitly if you think claim 3's 1055 is instead the MACHINE'S REAL
ANSWER - i.e. that deleting wire 7506 makes the FSIT LeftTerm unresolvable - and what in the project's files
would settle it.
