ATTACK the claim below. It is the explanation formed under pressure for the ONE failing gate in
`tools/bench/diag_s3b_l0_localname_v2.log` (`BGRUN END rc=1 after 101s`, 29 pass / 1 fail). Your job is to
find the strongest reason it is WRONG, to name an alternative explanation, to say what would falsify it, and
to name the CHEAPEST discriminating test. Do not confirm it.

Files you may read (read-only): `tools/bench/diag_s3b_l0_localname_v2.log`,
`tools/bench/diag_s3b_l0_localname_v2.py` (the diagnostic; the function at issue is `_s2_body()`),
`tools/bench/diag_s3b_l0_localname_v2.json`, `tools/recipes/build_oploopcast_v0.py` (the fleet's seed
mechanism of record, lines 4-8 and steps 6-7), `tools/recipes/build_opnodelabels_v0.py` (the donor's own
builder), `tools/gscript.py` (`create_control` :2360, `wire_control` :1928, `wire` :1340, `build_property`
:2194, `delete_object` :2240, `loop_cast` :626, `connect_terminals` :2415), `docs/toolkit-capabilities.md`,
`docs/NAMES.md`, `docs/cycle27-plan.md` Pre-decided 49 and 50.

== THE FAILING GATE, VERBATIM FROM THE LOG
  FAIL  S2_b10 ExecState == 1 after the indicator  *** THE OP'S PASS CRITERION ***  0

== WHAT WAS BUILT, in order, each line a reading from the same log
  S2_b1 build_property('VI Server:Local', [('6355400', False)]) -> Property #1025, error column '',
        Property census 7 -> 8; its terminal table carries `CtrlName` at i=4 as a SOURCE.
  S2_b3 create_control(Nodes[13].Terminals[0] = the `reference` SINK) -> ControlTerminal #1076, label read
        off the machine as 'reference', ControlTerminal 19 -> 20, ExecState still 1.
  S2_b4 that control was born WIRED (wire 1086 on `reference`); the wire was deleted by uid
        (gone [1086], no collateral).  *** ExecState reads 0 HERE, before the TMSC is touched at all. ***
  S2_b5 the TMSC's original `target class` wire 772 deleted by uid (gone [772], no collateral). ExecState 0.
  S2_b6 wire_control(['reference'] -> Function[0].`target class`): Wire 29 -> 30, error column '',
        `target class` row afterwards {'i': 2, 'wire': 1030}. ExecState 0.
  S2_b7 the cast output wire 645 fed exactly ONE sink (#235 Property Node `reference`); 645 deleted by uid;
        create_control on that orphaned sink -> ControlTerminal #1083, label 'reference 2'. ExecState 0.
  S2_b8 wire Function[0].`specific class reference` -> Property[0].`reference`: Wire 30 -> 31, error column
        '', `reference` row afterwards {'i': 0, 'wire': 1085}; the `CtrlName` row SURVIVED the wire.
        ExecState 0.
  S2_b9 create_indicator on `CtrlName` -> ControlTerminal #1102, one new panel label 'Control Name'.
        ExecState 0.  Final census: Node 16, Wire 32, Property 8, ControlTerminal 22.
  Nothing was saved, nothing was repaired, the unsaved copy was removed, the donor is byte-unchanged.

== THE CLAIM UNDER ATTACK
"The ExecState 0 is not evidence against the cast. It first appears at S2_b4 - before the TMSC is touched -
and is fully explained there by the new `VI Server:Local` property node standing with a BARE `reference`
input, which is a broken node in LabVIEW. Every later step left it at 0 simply because the graph was
unfinished until S2_b9. What is left unexplained is only the LAST reading: after b8 and b9 every terminal
this run touched is wired, so the VI should have returned to ExecState 1 and did not. The most likely
remaining cause is that a front-panel refnum CONTROL of class `Local` does not legally type
`To More Specific Class`'s `target class` - because the donor's own seed is NOT a control: this run
measured that NO node on that diagram produces wire 772 (0 producers) and that NO front-panel object carries
it either (`panel_wiring` returned 19 rows, none with wire 772), leaving a diagram CONSTANT as the only
remaining kind of object - i.e. the class-specifier constant `docs/toolkit-capabilities.md` calls 'the one
missing seed', which this fleet cannot create. On that reading the seed mechanism of record
(`build_oploopcast_v0.py:4-8`, 'any refnum WIRE of the wanted class types it') was reproduced only in form,
not in substance, and the `Local` cast is not reachable from a control."

== WHAT THE BUILD IS FOR (context, not part of the claim)
The deliverable is `claudeDev\OpLocalName_v0.vi`, a ONE-PROPERTY READER of a Local Variable's binding
(Traverse `Local` by index -> `Local.Control Name` 6355400 -> string out). No reader of a Local's binding
exists in this fleet at all; the eight pre-existing Locals in the main VI all return the VI's FILE NAME
through `Node.Label` 6359001, which is why the reader is being built.

== ALREADY RULED OUT (do not spend your answer on these)
1. "The donor is the wrong file / was modified": `OpNodeLabels_v0.vi` md5 `376ff12569008ebac25a524e0887030b`
   before AND after; the copy opened at `ExecState` 1 before any edit.
2. "The property ID does not resolve": `build_property('VI Server:Local', [('6355400', False)])` returned
   error column '' and produced a `CtrlName` SOURCE row, twice now (this run and
   `tools/bench/diag_s3b_l0_localname_run2.log:50-56`).
3. "Something was silently declined": every step above was verified BY EFFECT (uid sets, wire uids on named
   terminals, census diffs), not by a return code.
4. "The originals were touched / references leaked": four md5 pins unchanged before and after, refs
   12 opened / 12 closed / 0 live, the scratch deleted in the same run, `tools/recipes/` unchanged (158
   files before and after).
5. "Just run Remove Bad Wires": forbidden by the brief and by the project's standing rules; not called, not
   imported. Do not propose it.

== WHAT THIS SESSION MAY NOT DO WITH YOUR ANSWER
It is a MATERIAL session under this project's judgement/material split: it may not choose a route, switch
donors, or build an alternative op. So aim your answer at the DIAGNOSIS and at the cheapest DISCRIMINATING
TEST a later session could run, not at a redesign.
