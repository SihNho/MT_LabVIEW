ATTACK the claim below. It is the explanation formed under pressure for the ONE failing gate in
`tools/bench/diag_s3b_l0_localname.log` (run 1, `BGRUN END rc=1 after 112s`, 17 pass / 1 fail). Your job is
to find the strongest reason it is WRONG, to name an alternative explanation, to say what would falsify it,
and to name the CHEAPEST discriminating test. Do not confirm it.

Files you may read (read-only): `tools/bench/diag_s3b_l0_localname.log`, `tools/bench/diag_s3b_l0_localname.py`
(the diagnostic itself; the function at issue is `_r0_body()`), `tools/bench/diag_s3b_l0_localname.json`,
`tools/recipes/build_opnodelabels_v0.py` (the donor's own builder), `tools/gscript.py`
(`node_labels` :587, `report` :455, `build_property` :2194, `wire` :1340, `connect_terminals` :2410,
`loop_cast` :626), `docs/cycle27-plan.md` Pre-decided 49.

== THE FAILING GATE, VERBATIM FROM THE LOG
  FAIL  R0_a3 exactly ONE IndexArray on the copy's diagram, carrying a terminal named `element`  3 IndexArray(s); element None

== THE CLAIM UNDER ATTACK
"R0_a3 is a defect in the GATE, not a fact about the donor. The gate was copied from cycle 60 attempt 1,
whose donor `OpFPLabels_v0.vi` happens to carry exactly one Index Array; the donor of record here,
`OpNodeLabels_v0.vi`, carries THREE (uids 239, 236, 308), so `ia_uid` was left None, no terminal table was
read, and `element` reported None BY CONSTRUCTION - the machine was never asked anything. The same run's own
shape dump names the right one unambiguously: `Traverse for GObjects.vi` (uid 124) has a SOURCE terminal
`References` on wire 600, and Index Array uid 308 has `array` on wire 600 and `element` on wire 605, which
feeds `To More Specific Class` uid 683. Replacing the count test with 'the IndexArray whose `array` terminal
carries the Traverse node's `References` wire' is the whole repair, and the build should then proceed to the
measurement it exists for: wire that `element` into a `VI Server:Local` property node reading
`Local.Control Name` 6355400, and read ExecState."

== WHAT THE BUILD IS FOR (context, not part of the claim)
The deliverable is `claudeDev\OpLocalName_v0.vi`, a ONE-PROPERTY READER of a Local Variable's binding. No
reader of a Local's binding exists in this fleet at all. The known hazard, written into the script before the
run: `Traverse for GObjects.vi` returns GENERIC GObject references, and every class-specific property node in
the donor is fed by a TYPED source (`Node.Terminals[]` -> Terminal; `Terminal.Wire` -> Wire) or through
`To More Specific Class`, whose `target class` type comes from a wire no node on that diagram produces
(a panel object or a constant). `tools/gscript.py:2415` says "Type mismatches make a broken wire".

== ALREADY RULED OUT (do not spend your answer on these)
1. "The donor is the wrong file / was modified": `OpNodeLabels_v0.vi` md5 `376ff12569008ebac25a524e0887030b`
   before AND after the run, and the copy opened at `ExecState` 1 before any edit (gate R0_a1 PASS).
2. "Nothing was measured": the run dumped all 13 top-level nodes with full terminal tables (gate R0_a2 PASS)
   and that dump is where the wire numbers above come from.
3. "The originals were touched": gates T1/T2/T3/Z1 all PASS, four md5 pins unchanged before and after, refs
   3 opened / 3 closed / 0 live, and the unsaved copy was removed.
