r"""diag_allterms_retarget - the DECISIVE test of the only construction left for OpAllTerms_v0.

WHERE THIS SITS. Two runs have now closed three of the four routes, by measurement, not argument:
  `tools/bench/diag_allterms_cast.log` D1  - Traverse's GObject[] into a `VI Server:Terminal` node
      inside a For body leaves `ExecState` 0 (a DOWNCAST), and a `To More Specific Class` has no
      scripted creator (SKILL.md rule-0 exception 1).
  `tools/bench/diag_allterms_donor.log`    - A1 `copy_by_index` has NO destination-diagram parameter
      (route (c) would need a NEW op); A2 `loop_in` creates an EMPTY loop (route (b) cannot enclose);
      B1 the SAME wire into a `VI Server:GObject` node in the same body reads `ExecState` **1**, so
      the node's CLASS is the only variable and the border tunnel is not the confound.
  `tools/bench/diag_allterms_donor2.log`   - R1/R2 repaired run 1's invalid half (the 6503s were an
      identity collision with LIVE op VIs: 16/16 scratch copies load ExecState 1 and net_map returns
      rows for 20/20 diagrams), and R3 then answered the census over the FULL 26 candidates:
      **0 op VIs carry a TMSC inside a loop body** - route (a) has no donor.

WHAT IS LEFT is the brief's own constraint read literally - "start from a donor that ALREADY OWNS the
TMSC and get the loop around the cast by a route that is NOT move_in of a copied node": put the cast
in a ONE-ROW SUBVI whose own ROOT diagram holds it, and call that subVI from inside the loop with
`drop_subvi` (any diagram) + `conpane_assign` (239A8000, verified 2026-09-10) + `exit_loop`
(node_class defaults to "SubVI" - gscript.py:1761). The cast then never has to enter a loop at all.

That route has ONE unmeasured link, and this stage measures exactly it and nothing else:

        CAN AN EXISTING TMSC BE RE-TARGETED TO `Terminal` AND FEED A Terminal-CLASS NODE?

PREDICTION CONTRACT (desk-checked, Pre-decided 132):
  T1 `OpLoopCast_v0.vi`'s root diagram carries exactly one TMSC, identified by its own terminal names
     (`target class` / `specific class reference`, docs/NAMES.md:832), and its `target class` is fed
     by a WIRE from a front-panel refnum CONTROL - the typed-control seed, measured live at
     `tools/bench/diag_c60_castseed_probe.log:50` (wire 333, control uid 297, 0 node producers).
  T2 deleting the donor's Property nodes frees the TMSC's output; `remove_bad_wires_scripted` leaves
     `Function` unchanged (the TMSC itself is never a bad wire).
  T3 `build_property("VI Server:Terminal", [Name 634A004, Is Source? 634A003, Connected Wire 634A000,
     UID 632A813, Owner 6327806])` resolves on the ROOT diagram - determined: it already resolved
     INSIDE a loop body (`diag_allterms_cast.log:32`), and the root is the easier case.
  T4 `create_control` on that node's own `reference` input yields a front-panel control whose class is
     that node's BY CONSTRUCTION - docs/toolkit-capabilities.md:87-94, the route
     `build_opconnectfromwire_v0.py` used for `Wire`. Panel object count +1.
  T5 **THE DECIDER:** after cutting the old seed wire, wiring that new control into the TMSC's
     `target class` and the TMSC's `specific class reference` into the Terminal node's `reference`,
     the VI reads `ExecState` **1**. A 1 means the whole subVI-in-loop construction is sound and the
     recipe can be written; a 0 means the last permitted route is closed too, and Pre-decided 139's
     "stop and report - no third construction without the user" applies.

WHAT ALREADY EXISTS (checked first - `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`,
docs/toolkit-capabilities.md): `net_map`, `report`, `build_property`, `create_control`, `wire`,
`wire_control`, `delete_object`, `remove_bad_wires_scripted`, `node_terms`, `stagekit.Stage`.
NOTHING NEW IS WRITTEN HERE, and NOTHING IS SAVED - a deliverable op is built by a recipe under
`tools/recipes/`, never by a diagnostic.

NO RESTART (`fresh=False`): a parallel material session may be driving LabVIEW's GUI. Originals
untouched (rule 1); the only writable surface is a dated scratch copy of the OP VI `OpLoopCast_v0.vi`,
deleted at close. No motor, no ASI, no camera; no VI is run.
  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_allterms_retarget.log -- py -u tools/bench/diag_allterms_retarget.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpLoopCast_v0.vi")
TERM_PROPS = [("634A004", False), ("634A003", False), ("634A000", False),
              ("632A813", False), ("6327806", False)]
TMSC_MARKS = ("target class", "specific class reference")


def find_tmsc(rows):
    """(node_index, uid, terminals) of the one node whose terminal names are a TMSC's."""
    for idx in sorted(rows):
        terms = rows[idx][2]
        if any(m in [t[1] for t in terms] for m in TMSC_MARKS):
            return idx, rows[idx][0], terms
    return None, None, None


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[T1] the donor's root diagram, READ - where is the TMSC and what feeds its target class?")
    rows, _e = s.safe("net_map(root)", lambda: g.net_map(p, 0, max_nodes=60, max_terms=14)[0], {})
    idx, tmsc_uid, terms = find_tmsc(rows or {})
    s.R["root_nodes"] = dict((k, [v[0], v[1], v[2]]) for k, v in (rows or {}).items())
    s.fact("T1 TMSC node index={0!r} uid={1!r} terminals={2!r}".format(idx, tmsc_uid, terms))
    tc_wire = next((t[2] for t in (terms or []) if t[1] == "target class"), None)
    s.R["tmsc"] = {"node_index": idx, "uid": tmsc_uid, "terminals": terms, "target_class_wire": tc_wire}
    s.gate("T1 exactly one TMSC on the donor's ROOT diagram, its `target class` fed by a wire",
           tmsc_uid is not None and bool(tc_wire),
           "uid={0!r} target class wire={1!r}".format(tmsc_uid, tc_wire), fatal=True)

    s.head("[T2] free the TMSC's OUTPUT - delete the donor's ForLoop-class Property nodes")
    f0 = s.count("Function")
    for _ in range(s.count("Property") or 0):
        s.safe("delete Property[0]", lambda: g.delete_object(p, "Property", 0))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    f1, pr = s.count("Function"), s.count("Property")
    s.gate("T2 Property -> 0 and the TMSC survives (Function unchanged)", pr == 0 and f1 == f0,
           "Property={0} Function {1} -> {2}".format(pr, f0, f1))

    s.head("[T3] a VI Server:Terminal property node on the ROOT diagram")
    rec = s._op("build_property", lambda: g.build_property(p, "VI Server:Terminal", TERM_PROPS,
                                                           (1500, 1000), diagram_index=0),
                "VI Server:Terminal x5 on the root")
    pn = s.count("Property")
    s.gate("T3 build_property('VI Server:Terminal', 5 items) resolves on the root",
           pn == 1 and not rec["err"], "Property={0} err={1!r}".format(pn, rec["err"]))

    s.head("[T4] the TYPED SEED - create_control on that node's own `reference`")
    rows2, _e = s.safe("net_map(root) again", lambda: g.net_map(p, 0, max_nodes=60, max_terms=14)[0], {})
    pn_idx = next((k for k in sorted(rows2 or {})
                   if "Name" in [t[1] for t in rows2[k][2]] and "IsSource" in [t[1] for t in rows2[k][2]]), None)
    ref_i = None
    if pn_idx is not None:
        ref_i = next((t[0] for t in rows2[pn_idx][2] if t[1] == "reference"), None)
    s.fact("T4 Terminal PN node index={0!r}, its `reference` terminal index={1!r}".format(pn_idx, ref_i))
    ctl0 = s.count("ControlTerminal")
    made, err4 = s.safe("create_control(Terminal PN.reference)",
                        lambda: g.create_control(p, pn_idx, ref_i), (None, None))
    new_ctls, seed_label = (made or (None, None))
    ctl1 = s.count("ControlTerminal")
    s.R["seed"] = {"pn_node_index": pn_idx, "reference_terminal": ref_i, "created": new_ctls,
                   "label": seed_label, "ControlTerminal": [ctl0, ctl1], "err": err4}
    s.fact("T4 create_control -> label {0!r}, new {1!r}; ControlTerminal {2} -> {3}".format(
        seed_label, new_ctls, ctl0, ctl1))
    s.gate("T4 a Terminal-class refnum CONTROL exists (ControlTerminal +1, LabVIEW names it)",
           ctl1 == ctl0 + 1 and bool(seed_label),
           "{0} -> {1}, label {2!r}, err {3!r}".format(ctl0, ctl1, seed_label, err4), fatal=True)

    s.head("[T5] THE DECIDER - retarget the cast to Terminal and feed a Terminal-class node")
    if tc_wire:
        s.delete_wire(tc_wire, tag="T5 old seed wire")
    tmsc_i, _e = s.safe("Function index of the TMSC",
                        lambda: [o["uid"] for o in g.report(p, "Function")].index(tmsc_uid), None)
    s.fact("T5 the TMSC is Function[{0!r}]; the new seed control label is {1!r}".format(tmsc_i, seed_label))
    if seed_label is not None and tmsc_i is not None:
        s._op("wire_control", lambda: g.wire_control(p, [seed_label], "Function", tmsc_i, ["target class"]),
              "seed control -> TMSC 'target class'")
    pn_i, _e = s.safe("Property index", lambda: 0, 0)
    if tmsc_i is not None:
        s._op("wire", lambda: g.wire(p, "Function", tmsc_i, "specific class reference",
                                     "Property", pn_i, "reference"),
              "TMSC 'specific class reference' -> Terminal PN 'reference'")
    es = s.es("after the retarget")
    s.R["decider"] = {"exec_state": es, "seed_label": seed_label, "tmsc_function_index": tmsc_i}
    s.gate("T5 ExecState 1 - a re-targeted TMSC feeds a Terminal-class node, so the subVI-in-loop "
           "construction is sound (0 closes the last route permitted by Pre-decided 139)", es == 1,
           "ExecState={0!r}".format(es))


S = K.Stage(SRC, "", "diag_allterms_retarget", fresh=False, deadline_min=18.0, reserve_s=150.0,
            out_json=os.path.join(K.BENCH, "diag_allterms_retarget.json"),
            task="Can an existing To More Specific Class be re-targeted to `Terminal` with a "
                 "create_control seed and feed a Terminal-class property node? The last construction "
                 "Pre-decided 139 permits turns on this. Scratch only; nothing saved.")
S.input_md5 = K.md5(SRC)          # the donor's CURRENT bytes are the pin; it is never written
sys.exit(K.run(main, S))
