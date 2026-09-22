r"""diag_allterms_retarget2 - run 1's T5 failed on MY sequence, not on the machine. Same question.

RUN 1 (`tools/bench/diag_allterms_retarget.log`, 12 pass / 1 fail, rc=1, 65 s) reached T4 cleanly -
TMSC #683 found on `OpLoopCast_v0`'s root with `target class` <- wire 333 (T1), Property nodes deleted
and the TMSC intact (T2), a `VI Server:Terminal` 5-property node created on the root (T3), and
`create_control` on its `reference` returning a control LabVIEW named `'reference 2'` (T4). T5 then
read `ExecState` 0 - but **neither wire was ever made**: both calls were refused by gscript's own
post-condition with `Wire 9 -> 9` (`:73`, `:76`), which is the harness saying "nothing changed", not
LabVIEW saying "illegal".

THE CAUSE IS ON DISK AND WAS NOT READ BEFORE THE RUN. `tools/recipes/build_opconnectfromwire_v0.py`
built this exact seed for class `Wire` and records the behaviour in its own gate text:
  W6  `create_control` on that node's `reference` -> the WIRE-TYPED SEED, **arriving wired**  (:69)
  W9  in `finish`: **delete the seed's wire**, seed -> new TMSC `target class`, ... new TMSC
      `specific class reference` -> the `Terms[]` node's `reference`                            (:72-74)
So the control is born WIRED into the property node's `reference`; that input is therefore occupied
(second wire refused) and the control is already a source (first wire would be a BRANCH, refused).
Run 1 skipped W9's first clause. This run does not.

PREDICTION CONTRACT (desk-checked; T1-T4 are re-measured, not assumed, because every index is re-read
after every mutation - NAMES.md's rule):
  U1 as run 1's T1: one TMSC on the root, `target class` fed by a wire.
  U2 as run 1's T2/T3: Property -> 0 with the TMSC intact; the Terminal 5-property node resolves.
  U3 as run 1's T4 AND ITS MISSING HALF: `create_control` yields one new control AND that control
     arrives WIRED - the property node's `reference` terminal reads a NON-ZERO wire straight after.
     This is the fact run 1 did not check and the reason it failed.
  U4 with the seed's birth wire deleted and the TMSC's old output wire cleared, both connections land:
     seed -> `target class` (+1 wire) and `specific class reference` -> `reference` (+1 wire).
  U5 **THE DECIDER, unchanged:** `ExecState` **1**. A 1 says a re-targeted TMSC feeds a Terminal-class
     node, so the subVI-in-loop construction (cast on a one-row subVI's ROOT diagram, `drop_subvi` +
     `conpane_assign` + `exit_loop` at the call site) is sound and the recipe can be written. A 0
     closes the last route Pre-decided 139 permits and the answer goes back to the user.

WHAT ALREADY EXISTS: `net_map`, `report`, `build_property`, `create_control`, `wire`, `wire_control`,
`delete_object`, `remove_bad_wires_scripted`, `stagekit.Stage.delete_wire`. NOTHING NEW IS WRITTEN
HERE and NOTHING IS SAVED - a deliverable op is built by a recipe under `tools/recipes/`.

NO RESTART (`fresh=False`): a parallel material session may be driving LabVIEW's GUI. Originals
untouched (rule 1); the only writable surface is a dated scratch copy of `OpLoopCast_v0.vi`, deleted
at close. No motor, no ASI, no camera; no VI is run.
  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_allterms_retarget2.log -- py -u tools/bench/diag_allterms_retarget2.py
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


def walk(s, p, tag):
    rows, _e = s.safe("net_map({0})".format(tag), lambda: g.net_map(p, 0, max_nodes=60, max_terms=14)[0], {})
    return rows or {}


def find(rows, *names):
    """(node_index, uid, terminals) of the first root node carrying every one of `names`."""
    for i in sorted(rows):
        tn = [t[1] for t in rows[i][2]]
        if all(n in tn for n in names):
            return i, rows[i][0], rows[i][2]
    return None, None, None


def term_wire(terms, name):
    return next((t[2] for t in (terms or []) if t[1] == name), None)


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[U1] the donor's root diagram - locate the TMSC by its own terminal names")
    rows = walk(s, p, "U1")
    t_i, tmsc_uid, t_terms = find(rows, *TMSC_MARKS)
    tc_wire, out_wire = term_wire(t_terms, "target class"), term_wire(t_terms, "specific class reference")
    s.R["tmsc"] = {"node_index": t_i, "uid": tmsc_uid, "terminals": t_terms,
                   "target_class_wire": tc_wire, "output_wire": out_wire}
    s.fact("U1 TMSC uid={0!r} at Nodes[{1!r}]; target class w{2!r}; output w{3!r}".format(
        tmsc_uid, t_i, tc_wire, out_wire))
    s.gate("U1 one TMSC on the root, its `target class` fed by a wire", bool(tmsc_uid and tc_wire),
           "uid={0!r} w{1!r}".format(tmsc_uid, tc_wire), fatal=True)

    s.head("[U2] free the TMSC's output and create the Terminal-class property node")
    f0 = s.count("Function")
    for _ in range(s.count("Property") or 0):
        s.safe("delete Property[0]", lambda: g.delete_object(p, "Property", 0))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    rec = s._op("build_property", lambda: g.build_property(p, "VI Server:Terminal", TERM_PROPS,
                                                           (1500, 1000), diagram_index=0),
                "VI Server:Terminal x5 on the root")
    f1, pn = s.count("Function"), s.count("Property")
    s.gate("U2 Property 0 -> 1 (only the new Terminal node), Function unchanged, build err ''",
           pn == 1 and f1 == f0 and not rec["err"],
           "Property={0} Function {1}->{2} err={3!r}".format(pn, f0, f1, rec["err"]), fatal=True)

    s.head("[U3] the TYPED SEED - and the fact run 1 never checked: it arrives WIRED")
    rows = walk(s, p, "U3-before")
    pn_i, pn_uid, pn_terms = find(rows, "Name", "IsSource", "Wire")
    ref_i = next((t[0] for t in (pn_terms or []) if t[1] == "reference"), None)
    ctl0 = s.count("ControlTerminal")
    made, err3 = s.safe("create_control(Terminal PN.reference)",
                        lambda: g.create_control(p, pn_i, ref_i), (None, None))
    new_ctls, seed = (made or (None, None))
    ctl1 = s.count("ControlTerminal")
    rows = walk(s, p, "U3-after")
    pn_i, pn_uid, pn_terms = find(rows, "Name", "IsSource", "Wire")
    seed_wire = term_wire(pn_terms, "reference")
    s.R["seed"] = {"label": seed, "new": new_ctls, "ControlTerminal": [ctl0, ctl1],
                   "birth_wire": seed_wire, "pn_uid": pn_uid, "err": err3}
    s.fact("U3 seed label={0!r}; ControlTerminal {1}->{2}; the PN's `reference` now reads w{3!r}".format(
        seed, ctl0, ctl1, seed_wire))
    s.gate("U3 one new control AND it arrives WIRED into `reference` (build_opconnectfromwire_v0.py:69)",
           ctl1 == ctl0 + 1 and bool(seed) and bool(seed_wire),
           "label={0!r} birth wire={1!r} err={2!r}".format(seed, seed_wire, err3), fatal=True)

    s.head("[U4] W9's sequence - cut the birth wire and the old cast output, then wire both ends")
    if seed_wire:
        s.delete_wire(seed_wire, tag="U4 seed birth wire")
    rows = walk(s, p, "U4-mid")
    t_i, tmsc_uid2, t_terms = find(rows, *TMSC_MARKS)
    tc_wire, out_wire = term_wire(t_terms, "target class"), term_wire(t_terms, "specific class reference")
    for w, why in ((tc_wire, "U4 old seed -> target class"), (out_wire, "U4 old cast output")):
        if w:
            s.delete_wire(w, tag=why)
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    w0 = s.count("Wire")
    tm_fi, _e = s.safe("Function index of the TMSC",
                       lambda: [o["uid"] for o in g.report(p, "Function")].index(tmsc_uid2), None)
    r1 = s._op("wire_control", lambda: g.wire_control(p, [seed], "Function", tm_fi, ["target class"]),
               "seed {0!r} -> TMSC 'target class'".format(seed))
    w1 = s.count("Wire")
    pn_fi, _e = s.safe("Property index of the Terminal node",
                       lambda: [o["uid"] for o in g.report(p, "Property")].index(pn_uid), 0)
    r2 = s._op("wire", lambda: g.wire(p, "Function", tm_fi, "specific class reference",
                                      "Property", pn_fi, "reference"),
               "TMSC 'specific class reference' -> Terminal PN 'reference'")
    w2 = s.count("Wire")
    s.R["wiring"] = {"Wire": [w0, w1, w2], "seed_err": r1["err"], "cast_err": r2["err"],
                     "tmsc_function_index": tm_fi, "pn_property_index": pn_fi}
    s.gate("U4 both wires land: Wire {0} -> {1} -> {2}, both op errors ''".format(w0, w1, w2),
           w1 == w0 + 1 and w2 == w1 + 1 and not r1["err"] and not r2["err"],
           "seed err {0!r}; cast err {1!r}".format(r1["err"], r2["err"]))

    s.head("[U5] THE DECIDER")
    rows = walk(s, p, "U5")
    s.R["root_nodes_final"] = dict((k, [v[0], v[1], v[2]]) for k, v in rows.items())
    es = s.es("after the retarget")
    s.R["decider"] = {"exec_state": es}
    s.gate("U5 ExecState 1 - a re-targeted To More Specific Class feeds a Terminal-class node, so the "
           "subVI-in-loop construction is sound (0 closes the last route Pre-decided 139 permits)",
           es == 1, "ExecState={0!r}".format(es))


S = K.Stage(SRC, "", "diag_allterms_retarget2", fresh=False, deadline_min=18.0, reserve_s=150.0,
            out_json=os.path.join(K.BENCH, "diag_allterms_retarget2.json"),
            task="Re-target an existing To More Specific Class to `Terminal` with a create_control "
                 "seed, following build_opconnectfromwire_v0.py's W6/W9 sequence, and feed a "
                 "Terminal-class property node. Scratch only; nothing saved.")
S.input_md5 = K.md5(SRC)          # the donor's CURRENT bytes are the pin; it is never written
sys.exit(K.run(main, S))
