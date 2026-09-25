ATTACK this claim (failed prediction, card 90-6, log tools/bench/diag_c90_t0_step3b_r2.log, script tools/bench/diag_c90_t0_step3b.py, run 2 = the eight While-body sites only).

CONTEXT: per site the script does build_clfn (top level) -> junk_purge -> ExecState read -> move_in(uid -> Diagram[d]) ->
find_node(uid) gives Nodes index n -> ExecState read -> OpCreateConstOnTerm_v0 on WhileLoop[i].Diagram.Nodes[n].Terms[6]
-> junk_purge (deletes the one zero-wired Invoke that move_in leaves) -> node_terms(d, n) reads t6 -> gate S.3 (t6 wire != 0)
-> connect_from_wire(sink d, n, t8 <- site wire) -> ExecState read. Run 1 (diag_c90_t0_step3b.log) passed all of this on
While-body sites 0 and 2 with ExecState 1 after each.

OBSERVED in run 2 (diag_c90_t0_step3b_r2.log):
 - ExecState is 0 right after build_clfn while the new CLFN sits BARE at top level (:42, and at every site :84,:143,...) and
   still 0 after move_in (:45). In run 1 ExecState came back to 1 after site 0's constant + branch (step3b.log:79) and after
   site 2 (:135).
 - Site 0: move_in's junk Invoke #22989 lives at Diagram[43] Nodes[73] (:48), find_node put the CLFN #22968 at N[74]; the
   constant #23202 was created on WhileLoop[1].N[74].t6 (err '' :61) BEFORE the purge; the purge deleted the Invoke at N[73]
   (:57); node_terms(43, 74) then read t6 wire 0 (:62) -> gate S00.3 FAIL -> no branch -> ExecState 0 after the site (:63).
 - Site 11: the same shape - Invoke #23543 at Diagram[99] N[23] (:268), CLFN at N[24], constant #23801 on N[24].t6 (:280),
   purge, node_terms(99, 24) t6 wire 0 (:281). Site 12's CLFN was then found at N[24] (:322) and site 13's at N[25].
 - Sites 2, 8, 10, 12, 13, 20: constant, t6 wired, branch Is Broken? False, sink +1, t8 == site wire - all PASS, but
   ExecState 0 after each (:124,:183,:242,:342,:401,:460). Final: 6/8 sites, ExecState 0, cdiff rows 0 added 16 (8 CLFN +
   8 constants, :465), not saved.
 - In run 1 the junk Invoke landed AFTER the CLFN in Nodes[] (Nodes[78] with the CLFN at 76, step3b.log:41-ish), so no shift.

MY EXPLANATION (the claim to attack):
 1. A CLFN with an unwired input (`site` I32 and/or `any` Adapt-to-Type, both pass-by-value) BREAKS the VI: ExecState is 0
    the moment it exists bare at top level, and returns to 1 only when both inputs are wired (run 1 sites 0/2). So the
    ExecState 0 after sites 2..20 in run 2 is INHERITED from site 0's CLFN, whose t8 was never branched.
 2. Site 0's and site 11's "t6 wire 0" are a READER fault of my script, not a creation failure: the constant WAS created on
    the CLFN (N[74] was the CLFN when the op ran), then the purge deleted the Invoke at a LOWER Nodes index, the CLFN shifted
    to N[73], and node_terms read the node now at N[74] (an original node), whose t6 is unwired. Fix: re-run find_node after
    every purge and use the fresh index for node_terms and connect_from_wire.
 3. Whether the junk Invoke sorts before or after the CLFN in Diagram.Nodes[] depends on position (Invoke at (2639,933) or
    (-14936,658) vs the CLFN at (1400+30k, 900+60(k%4))), so run 1 was lucky, not different.

ALREADY RULED OUT: the moves failing (err '', find_node uid echo on the site diagram); junk left behind (every purge deleted
exactly one Invoke; cdiff adds no Invoke); the constant op erroring (err '' / '' at both sites); Adapt-to-Type refusal on
w3268/w5859/w541/w19372/w19468/w19429/w34066 (branches landed, Is Broken? False, and run 1 read ExecState 1 after sites 0/2).

Give: the strongest reason any of 1-3 is wrong; an alternative explanation for ExecState 0 after a bare CLFN and for the
t6-wire-0 reads; what would falsify each; the cheapest discriminating test. Also: with a third LabVIEW run (~7 min), is
"re-find after every purge, then read t6 and branch" enough for all eight While-body sites to end ExecState 1, or is there
another index hazard in the sequence above?
