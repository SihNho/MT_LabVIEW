ATTACK the four claims below. BUDGET: answer in at most ~70 lines and read AT MOST these files, nothing else -
`tools/bench/diag_c83_connect2x2.log` (173 lines) and, only if you must, `tools/bench/diag_c83_connect2x2.json`.
Do not read the 307 KB VI, do not enumerate the repo. A first dispatch of this question TIMED OUT at 840 s, so
spend your time on the reasoning, not on reading.

SUBJECT. `Terminal.Connect Wire` 6349C03 declines SILENTLY on one write: attach `FlatSequenceInnerTunnel #7468`'s
LeftTerm `#7488` to a While-loop shift-register OUTER terminal (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`)
on a scratch copy of a big VI, after deleting wire 7506. Three explanations survived an earlier review:
(a) the ROLES are inverted for CREATION - `Wire Source` is documented as the wire's ORIGINAL SOURCE, and the op
hands it the SINK while the Invoke sits on the SOURCE terminal; (b) `Auto Route?` is at its default FALSE;
(c) the Invoke's own `error out` never reaches the op's `error out`, so "silent" is only "quiet".

CLAIM 1. The trivial 2x2 refutes (a) and (b). Four FRESH trivial VIs (two bare `VI Server:GObject` Property
nodes each), driven through a scratch copy of `OpConnect_v0.vi` carrying a new `Auto Route?` control:
ALL FOUR cells created the wire - `wire_delta` 1, the SAME wire uid 93 on both ends, 0 junk nodes
(log lines 49, 55, 61, 67). A1/A2 put the Invoke on the SINK (`reference`, is_source False) with the SOURCE
(`reference out`, is_source True) as `Wire Source`; B1/B2 the other way round. So 6349C03 creates a wire between
two BARE terminals in BOTH role assignments and at BOTH `Auto Route?` values.

CLAIM 2. On the real pair `Auto Route?` TRUE changed nothing: border wire 0, `wire_delta` 0, `UID 2` 0, one junk
`Invoke` minted (cells S2 B1 and S2 B2). And the op's `error out` indicator, poisoned with
`(True, 999999, "POISON")` before every call, came back STILL CARRYING THE POISON in every cell of both steps -
so it is never written by a run, and the earlier evidence "`err=''` on 20/20 calls" was reading an unwired
indicator's saved default, not an absence of errors.

CLAIM 3. The NEW `error 1055` is an artefact of my own run, not the machine's answer. Cycle 82 recorded the op's
per-stage error columns EMPTY with `term_uid` 7488 and `uid_back` 7468 on the same bed; run 1 reads
`error 1055: To More Specific Class in UID to GObject Reference.vi->OpFsInnerTunnelConnect_v0.vi` plus
`error 1055: Property Node` on three stages, with `term_uid` and `uid_back` stuck at their poison 0. Exactly two
things changed between the runs: run 1 EDITED the op (ONE `create_indicator` on the `Clear Errors.vi` node's
`error out`; md5 c0d5efe3... -> cda1e36e...), and run 1 POISONS several of the op's indicators before each call.
==> SAY EXPLICITLY whether you think the 1055 is instead the MACHINE'S REAL ANSWER - that deleting wire 7506
makes the FSIT LeftTerm unresolvable - and what single observation would settle it.

CLAIM 4. The swapped-roles op copy is repairable. The scratch copy with the Invoke's `reference` and
`Wire Source` feeds EXCHANGED came out `ExecState` 0 although both new wires verified on both ends (log 76-83);
the diagnostic lists `(241, 'reference')` and `(187, 'reference')` among the unwired non-error sinks. I claim the
deleted NETS had OTHER consumers besides the Invoke (the readback Property nodes), and that re-branching every
recorded consumer onto its original source after the crosswise re-connect makes the copy legal.

ALREADY RULED OUT ON THE MACHINE: addressing (loop-node uid echo 23032 MATCH; the border terminal asserted
wire 0 immediately before every call); stale readouts (every indicator poisoned per call); "the Invoke did not
run" (exactly 1 stray `Invoke` minted per real-pair call); "the method declines on a bare `Wire Source`"
(refuted in `tools/bench/build_harness_copyloop2.log:31-40` and again by the four trivial cells).

FOR EACH CLAIM give: the strongest reason it is WRONG, an alternative explanation, the observation that would
falsify it, and ONE cheapest discriminating test runnable in a single script on a scratch copy (no new op, no
new method id, nothing written to the bed). Rank the tests if you name more than one.
