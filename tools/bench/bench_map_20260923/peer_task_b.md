FAILED PREDICTION (connectivity-map plan step 5b, bench B: end-to-end repair, zero LLM turns, on a dated scratch of S1 =
`claudeDev\D1_s1_copy.vi`, the original's bytes). Attack the DIAGNOSIS below; find the strongest reason it is wrong.

WHAT RAN (`tools/bench/bench_map_20260923/b_endtoend.py`, log `tools/bench/bench_map_b.log`, JSON
`tools/bench/bench_map_b.json`, record `tools/bench/decision_bench_map_b.json`). 9 of the 11 M3a-1 wires exist in S1 (23502
/23540 were created later by S3b), each one source -> one sink on the frame-loop body (diagram uid 639); all 9 deleted
whole (`stagekit.delete_wire`, by uid via the live Wire traverse). Then: live re-read (OpAllTerms_v1 + GObject census; S1's
flat-sequence faces and Shift Registers[] reused) -> `jev_candidates.candidates` -> `jev_pairs.decide(by_rule=True,
risk_gates=False)` with PAIR NOT acting (bench A5 failed its held-out criterion) -> `stagekit.from_decision` -> ARM 2 with the
KNOWN S1 pair as verdict and the same op rule -> re-read -> `vigraph.diff` / `computation_diff` against S1.

PREDICTED: the damage read back = exactly the 9 S1 edges removed (0 added). OBSERVED: edges_removed 20, edges_added 6,
changed_sinks 14 (gate B0). After ARM 2: 6 of 9 restored (1893, 2819, 3947, 4833, 7388, 11232), ExecState 0, repaired diff
10 removed / 6 added, computation_diff 3 rows (#48 'VISA resource name', #9243 'x', #29815 'VISA resource name' unsourced).
Remaining diff rows: the VISA carrier (right register #4334 / left #4344 / FSIT #7468) appears in S1 with terminal name
'VISA out' and in the repaired scratch as 'Outgoing Handle' (6 edges - / 6 edges +: sr #4334->#4344, fs #7468, wires #4194->
#4344 outer, #4334 outer->#7468, #7468->#29815, #7468[3]->#7468[1]); `- wire #11263 'VISA out' -> #4334` (w7337);
`- wire #4344 'VISA out' -> #48` (w1731); `- wire #9641 -> #9623 outer` (w9635); `- wire #9623 InnerTerminal '# slices in
stack' [1] -> #9243 'x'` (a wire NOT deleted).

DIAGNOSIS UNDER ATTACK: (a) w1731 and w7337 failed at the CANDIDATE layer only because graph keys include the terminal NAME
(Pre-decided 137): cutting both wires of the VISA shift-register carrier makes LabVIEW rename the whole carrier's terminals
'VISA out' -> 'Outgoing Handle' (the name follows the remaining wire from #4194), so the S1 truth key no longer exists and
the 6 renamed edges are the extra -6/+6 of B0; (b) w9635 failed at the OP layer: Pre-decided 143's rule has no entry for a
LoopTunnel INNER source (no wire left on it, not node-addressable) and Jev's OP menu does not act; (c) the other extra
removed edges of B0 (and the lingering `#9623 inner -> #9243`) are INPUT TUNNELS whose feeding wire was cut: the tunnel's
direction becomes undetermined, its inner terminal is no longer read as a source, the inner wire has 0 sources and build4
emits no edge; restoring the feed (7388 -> #11348, 11232 -> #11220) brought theirs back. (c) is INFERRED - the severed
graph's flags were not dumped.

QUESTIONS: (1) Is there an alternative to (c) - e.g. the delete-by-traverse-index verb (`build_opfsinnertunnelconnect_v0.
del_wire`: uid -> index in report_all('Wire') -> gscript.delete_object) deleting a DIFFERENT wire, or the reader mis-keying
ordinals ([1]) after a rename? (2) Is (a) really a key-identity problem, or did LabVIEW change the carrier's TYPE (a VISA
refnum becoming a generic handle) - which would make it a computation change? (3) The cheapest discriminating test for (c)
and for (1).
