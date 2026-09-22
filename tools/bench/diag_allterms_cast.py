r"""diag_allterms_cast - STEP 1 for OpAllTerms_v0 (judgement D-A/D-B, 2026-09-23 05:0x).

D-A wants, INSIDE a For loop body fed by `Traverse for GObjects`(class `Terminal`): one
`To More Specific Class`(Terminal) -> Terminal properties. D-B forbids the F-side construction
(`copy_by_index` + `move_in` into the body) and demands every body node be CREATED there, the way
`build_opreportall_v1.py` creates its property nodes. A TMSC has **no scripted creator** at all
(SKILL.md rule-0 exception #1; `docs/cycle14-plan.md:63` with its 2026-09-16 correction: only
RETARGETING an existing TMSC is solved). So D-A is buildable W-side only if the cast is not needed.

THIS STAGE MEASURES THAT, AND NOTHING ELSE. It builds no op and saves no VI.

PREDICTION CONTRACT (desk-checked against the preceding steps, Pre-decided 132):
  A1 deleting `OpReport_v3`'s Index Array + both Property nodes leaves IndexArray 0 / Property 0 and
     frees `Traverse.References` - forced by `build_opreportall_v1.py:129-133`, which did exactly this.
  B1 `for_loop` then `report('Diagram')` yields exactly one diagram owned by a ForLoop - same recipe :135-142.
  C1 `build_property("VI Server:Terminal", [Name 634A004, Is Source? 634A003, Connected Wire 634A000,
     UID 632A813, Owner 6327806])` RESOLVES inside that body (error column '', Property 0->1).
     Determined, not free: `docs/NAMES.md:425-426` lists all five as already-wrapped IDs, and
     `build_property` resolved 634A006 and 6355400 the same way (`NAMES.md:399`, `cycle27-plan.md:2185`).
  C2 its data-terminal short names are `Name` / `IsSource` / `Wire` / `UID` / `Owner`
     - measured in `probe_castfree5.log`, quoted at `docs/NAMES.md:369-371`. Read, never guessed.
  D1 **THE DECIDER, and it is predicted to FAIL-CLOSED:** wiring `Traverse.References` (a **GObject**
     array) into that Terminal-class node's `reference` leaves `ExecState` **0**, because GObject ->
     Terminal is a DOWNCAST. `docs/NAMES.md:945` measured the same shape (`Generic.Owner` -> a
     GObject-class node: "ExecState 1 -> 0 ... A downcast needs a To More Specific Class") and
     `docs/cycle27-plan.md:2185-2190` measured it for `Local`. The gate is written as `ExecState == 1`
     so that a PASS is the surprise: a pass means no TMSC is needed and D-A builds W-side.
  E1 no op VI under claudeDev carries a `To More Specific Class` INSIDE a loop-body diagram - free
     prediction; nothing has counted this. It decides whether a donor exists that needs no `move_in`.

WHAT ALREADY EXISTS (checked first: `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`,
docs/toolkit-capabilities.md): `build_property` (gscript:2277), `for_loop` (:1250), `wire` (:1380),
`delete_object` (:2358), `remove_bad_wires_scripted` (:2604), `node_terms` (:910), `net_map` (:2623),
`report`/`report_all`/`count`, `stagekit.Stage`. NOTHING NEW IS WRITTEN HERE - inputs, gates, facts.

Originals untouched (rule 1); the only surface is a dated copy of the OP VI `OpReport_v3.vi`, deleted
at close. No motor, no ASI, no camera; no VI is run.
  MATERIAL=1 py tools/bgrun.py --max-min 22 --log tools/bench/diag_allterms_cast.log -- py -u tools/bench/diag_allterms_cast.py
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpReport_v3.vi")
SRC_MD5 = "0743701a249b6ac20a5dab9ee676c09c"
TERM_PROPS = [("634A004", False), ("634A003", False), ("634A000", False),
              ("632A813", False), ("6327806", False)]
WANT_NAMES = ["Name", "IsSource", "Wire", "UID", "Owner"]


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[A] free Traverse.'References' - delete the Index Array and both Property nodes")
    s.safe("delete IndexArray[0]", lambda: g.delete_object(p, "IndexArray", 0))
    for _ in range(s.count("Property") or 0):
        s.safe("delete Property[0]", lambda: g.delete_object(p, "Property", 0))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    ia, pr = s.count("IndexArray"), s.count("Property")
    s.gate("A1 IndexArray 0 and Property 0 (Traverse.'References' is free)", ia == 0 and pr == 0,
           "IndexArray={0} Property={1}".format(ia, pr))

    s.head("[B] an empty For loop; its body diagram")
    s.safe("for_loop", lambda: g.for_loop(p, (1400, 900)))
    dias, _e = s.safe("report(Diagram)", lambda: [i for i, d in enumerate(g.report(p, "Diagram"))
                                                  if "For" in str(d.get("owner"))], [])
    s.gate("B1 exactly one diagram owned by a ForLoop", len(dias or []) == 1, "dias={0!r}".format(dias))
    if not dias:
        raise K.Stop("no loop body diagram - nothing further is measurable")
    body = dias[0]

    s.head("[C] a VI Server:Terminal property node CREATED inside the body (no copy, no move_in)")
    rec = s._op("build_property", lambda: g.build_property(p, "VI Server:Terminal", TERM_PROPS,
                                                           (1450, 950), diagram_index=body),
                "VI Server:Terminal x5 in the loop body")
    pr = s.count("Property")
    s.gate("C1 build_property('VI Server:Terminal', 5 items) resolves in the body",
           pr == 1 and not rec["err"], "Property={0} err={1!r}".format(pr, rec["err"]))
    terms, _e = s.safe("node_terms(body, 0)", lambda: g.node_terms(p, body, 0), [])
    names = [t.get("name") for t in (terms or [])]
    s.R["terminal_pn_short_names"] = names
    s.fact("C2 the node's terminals, READ off the machine: {0!r}".format(names))
    s.gate("C2 short names contain Name/IsSource/Wire/UID/Owner (docs/NAMES.md:369-371)",
           all(w in names for w in WANT_NAMES), "want {0!r} got {1!r}".format(WANT_NAMES, names))

    s.head("[D] THE DECIDER - GObject[] from Traverse into a Terminal-class `reference`")
    es_before = s.es("before the cast-free wire")
    tun_before = s.count("LoopTunnel")
    rec = s._op("wire", lambda: g.wire(p, "SubVI", 0, "References", "Property", 0, "reference"),
                "Traverse.'References' -> Terminal PN .reference")
    es_after = s.es("after the cast-free wire")
    tun_after = s.count("LoopTunnel")
    s.R["decider"] = {"es_before": es_before, "es_after": es_after, "wire_err": rec["err"],
                      "LoopTunnel": [tun_before, tun_after]}
    s.fact("D1 ExecState {0} -> {1}; LoopTunnel {2} -> {3}; wire err {4!r}".format(
        es_before, es_after, tun_before, tun_after, rec["err"]))
    s.gate("D1 ExecState == 1 with NO To More Specific Class (a PASS means D-A builds W-side; "
           "0 is the prediction, docs/NAMES.md:945)", es_after == 1,
           "ExecState={0} (predicted 0)".format(es_after))

    s.head("[E] is there a donor with a TMSC already INSIDE a loop body? (no move_in needed)")
    cands, carriers = [], []
    for path in sorted(glob.glob(os.path.join(K.CLAUDEDEV, "Op*.vi"))):
        if s.left_s() < 240:
            s.fact("E deadline reserve reached - scanned {0} op VIs".format(len(cands)))
            break
        nf, _e = s.safe("count(Function) " + os.path.basename(path), lambda q=path: g.count(q, "Function"), 0)
        nl, _e = s.safe("count(ForLoop) " + os.path.basename(path), lambda q=path: g.count(q, "ForLoop"), 0)
        cands.append((os.path.basename(path), nf, nl))
        if (nf or 0) > 0 and (nl or 0) > 0:
            carriers.append(os.path.basename(path))
    s.R["op_vi_function_loop_census"] = cands
    s.fact("E op VIs with BOTH a Function node and a ForLoop: {0!r}".format(carriers))
    for name in carriers[:4]:
        q = os.path.join(K.CLAUDEDEV, name)
        dias, _e = s.safe("E report(Diagram) " + name,
                          lambda q=q: [(i, str(d.get("owner"))) for i, d in enumerate(g.report(q, "Diagram"))], [])
        s.fact("E {0} diagrams {1!r}".format(name, dias))
        for i, owner in [d for d in (dias or []) if "Loop" in d[1]][:2]:
            rows, _e = s.safe("E net_map {0} d{1}".format(name, i),
                              lambda q=q, i=i: g.net_map(q, i, max_nodes=30, max_terms=8)[0], [])
            s.fact("E {0} body d{1} nodes {2!r}".format(name, i, rows))
    s.gate("E1 no op VI carries a To More Specific Class inside a loop body (free prediction)",
           not carriers, "carriers={0!r}".format(carriers))


S = K.Stage(SRC, SRC_MD5, "diag_allterms_cast", deadline_min=20.0, reserve_s=200.0,
            out_json=os.path.join(K.BENCH, "diag_allterms_cast.json"),
            task="Does a VI Server:Terminal property node accept Traverse's GObject refs without a "
                 "To More Specific Class? If not, D-A's body cannot be built W-side. Nothing saved.")
sys.exit(K.run(main, S))
