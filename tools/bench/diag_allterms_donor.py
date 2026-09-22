r"""diag_allterms_donor - STEP 1 ROUTE-FINDER for OpAllTerms_v0 (docs/connectivity-map-plan.md step 1).

`tools/bench/diag_allterms_cast.log` (2026-09-23 04:44, 12/2) measured that a `VI Server:Terminal`
property node IS creatable inside a For-loop body, but that `Traverse.'References'` (a **GObject**
array) wired into it leaves `ExecState` 0 - a DOWNCAST. A `To More Specific Class` has no scripted
creator, and Pre-decided 139 FORBIDS the `copy_by_index` + `move_in` construction (4 failures / 0
successes). So the whole build turns on ONE question this stage answers, and nothing else:

        HOW DOES A `To More Specific Class` GET INSIDE A LOOP BODY WITHOUT `move_in`?

Three candidate routes, each measured here BEFORE any recipe is written:
  (a) a DONOR op VI that already carries a TMSC inside a loop-body diagram -> copy the donor, retarget
      its `target class` (typed-control seed, docs/toolkit-capabilities.md:87-94), rebuild the body;
  (b) `loop_in('for', ...)` placing a loop AROUND an existing TMSC;
  (c) `copy_by_index` landing the TMSC DIRECTLY on a nested body diagram (no move_in).

PREDICTION CONTRACT (desk-checked, Pre-decided 132):
  A1 DETERMINED: `copy_by_index(donor, cls, index, target, expect_uid, finish)` exposes no destination
     diagram at all - route (c) needs a NEW op, not a new argument. gscript.py:1519-1598 drops the copy
     on the substituted Move-example Target's TOP-LEVEL diagram.
  A2 DETERMINED: `loop_in` takes a `diagram_index` but its docstring (gscript.py:1195-1200) says it
     CREATES a loop whose input tunnels come from an existing node's OUTPUT terminals - an empty body.
     Route (b) is refuted at the source; the gate asserts the signature so the claim is machine-checked.
  A3 DETERMINED: `drop_subvi` (any diagram) + `conpane_assign` (239A8000, verified 2026-09-10) +
     `create_control` all exist -> a FOURTH route (S) is available if (a) fails: the cast lives on a
     one-row subVI's OWN ROOT diagram and the loop body holds only a subVI call.
  B1 DETERMINED, ONE VARIABLE: the same `Traverse.'References'` wire into a `VI Server:GObject`
     property node in the same body reads `ExecState` **1**. diag_allterms_cast D1 read 0 with a
     `VI Server:Terminal` node; `build_opreportall_v1.log:25-26` read 1 with GObject but on ANOTHER
     VI. Measuring both on ONE copy makes the node's CLASS the only difference, and rules out the
     confound that the border tunnel is simply not auto-indexed (array into a scalar refnum).
  C1 FREE: at least one op VI under claudeDev carries a TMSC INSIDE a loop-body diagram.
     `diag_allterms_cast` E1 counted "Function + ForLoop" carriers (26) but `Index Array` IS a
     `Function`, so that census was uninformative, and it then inspected only carriers[:4]. This one
     detects the TMSC by its own terminal names (`target class` / `specific class reference`,
     docs/NAMES.md:832) on EVERY loop-owned diagram of EVERY candidate.

WHAT ALREADY EXISTS (checked first - `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`,
docs/toolkit-capabilities.md): `report`, `report_all`, `net_map`, `count`, `for_loop`, `loop_in`,
`build_property`, `wire`, `delete_object`, `remove_bad_wires_scripted`, `drop_subvi`, `conpane`,
`conpane_assign`, `create_control`, `copy_by_index`, `stagekit.Stage`. NOTHING NEW IS WRITTEN HERE.

NO RESTART: a parallel material session may be driving LabVIEW's GUI (tools/lv_errorlist.py), so
`fresh=False` - the handle count is recorded instead. Originals untouched (rule 1); the only writable
surface is a dated copy of the OP VI `OpReport_v3.vi`, deleted at close. No motor, no ASI, no camera;
no VI is run.
  MATERIAL=1 py tools/bgrun.py --max-min 24 --log tools/bench/diag_allterms_donor.log -- py -u tools/bench/diag_allterms_donor.py
"""
import glob
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpReport_v3.vi")
SRC_MD5 = "0743701a249b6ac20a5dab9ee676c09c"
TMSC_MARKS = ("target class", "specific class reference")


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[A] SOURCE FACTS - what the fleet's copier and loop-creator can address")
    sig_copy = "copy_by_index" + str(inspect.signature(g.copy_by_index))
    sig_loop = "loop_in" + str(inspect.signature(g.loop_in))
    s.fact(sig_copy)
    s.fact(sig_loop)
    s.R["signatures"] = {"copy_by_index": sig_copy, "loop_in": sig_loop}
    s.gate("A1 copy_by_index exposes NO destination-diagram parameter (route (c) needs a NEW op, "
           "gscript.py:1519-1598)", "diagram" not in sig_copy, sig_copy)
    s.gate("A2 loop_in takes diagram_index but creates an EMPTY loop (route (b) cannot enclose)",
           "diagram_index" in sig_loop, sig_loop)
    have = dict((n, hasattr(g, n)) for n in ("drop_subvi", "conpane", "conpane_assign",
                                             "create_control", "build_property", "wire"))
    s.R["route_s_helpers"] = have
    s.gate("A3 route (S) subVI-in-loop helpers all exist in gscript", all(have.values()), repr(have))

    s.head("[B] ONE VARIABLE - the same Traverse wire into a GObject-class node in a loop body")
    s.safe("delete IndexArray[0]", lambda: g.delete_object(p, "IndexArray", 0))
    for _ in range(s.count("Property") or 0):
        s.safe("delete Property[0]", lambda: g.delete_object(p, "Property", 0))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    s.safe("for_loop", lambda: g.for_loop(p, (1400, 900)))
    dias, _e = s.safe("report(Diagram)", lambda: [i for i, d in enumerate(g.report(p, "Diagram"))
                                                  if "For" in str(d.get("owner"))], [])
    if not dias:
        raise K.Stop("no loop body diagram - the control is not measurable")
    body = dias[0]
    rec = s._op("build_property", lambda: g.build_property(p, "VI Server:GObject", [("632A813", False)],
                                                           (1450, 950), diagram_index=body),
                "VI Server:GObject UID in the loop body")
    es0 = s.es("before the GObject wire")
    rec2 = s._op("wire", lambda: g.wire(p, "SubVI", 0, "References", "Property", 0, "reference"),
                 "Traverse.'References' -> GObject PN .reference")
    es1 = s.es("after the GObject wire")
    tun = s.count("LoopTunnel")
    s.R["one_variable"] = {"es_before": es0, "es_after": es1, "LoopTunnel": tun,
                           "build_err": rec["err"], "wire_err": rec2["err"]}
    s.gate("B1 ExecState 1 with a GObject-class node on the SAME wire (diag_allterms_cast D1 read 0 "
           "with a Terminal-class node; the node's CLASS is the only difference)", es1 == 1,
           "ExecState {0} -> {1}, LoopTunnel={2}, wire err {3!r}".format(es0, es1, tun, rec2["err"]))

    s.head("[C] THE DECIDER - does any op VI carry a To More Specific Class INSIDE a loop body?")
    cands = []
    for path in sorted(glob.glob(os.path.join(K.CLAUDEDEV, "Op*.vi"))):
        if s.left_s() < 400:
            s.fact("C deadline reserve reached while counting - scanned {0} op VIs".format(len(cands)))
            break
        name = os.path.basename(path)
        nf, _e = s.safe("count(Function) " + name, lambda q=path: g.count(q, "Function"), 0)
        if not nf:
            continue
        nl, _e = s.safe("count(ForLoop) " + name, lambda q=path: g.count(q, "ForLoop"), 0)
        if not nl:
            nl, _e = s.safe("count(WhileLoop) " + name, lambda q=path: g.count(q, "WhileLoop"), 0)
        if nl:
            cands.append(name)
    s.R["candidates"] = cands
    s.fact("C {0} op VI(s) have >=1 Function AND >=1 loop: {1!r}".format(len(cands), cands))

    hits, scanned = [], []
    for name in cands:
        if s.left_s() < 120:
            s.fact("C deadline reserve reached while walking bodies - scanned {0}".format(len(scanned)))
            break
        q = os.path.join(K.CLAUDEDEV, name)
        dias, _e = s.safe("C report(Diagram) " + name,
                          lambda q=q: [(i, str(d.get("owner"))) for i, d in enumerate(g.report(q, "Diagram"))], [])
        for i, owner in [d for d in (dias or []) if "Loop" in d[1]]:
            rows, _e = s.safe("C net_map {0} d{1}".format(name, i),
                              lambda q=q, i=i: g.net_map(q, i, max_nodes=40, max_terms=10)[0], {})
            scanned.append((name, i, owner, len(rows or {})))
            for _idx, row in (rows or {}).items():
                uid, label, terms = row[0], row[1], row[2]
                tnames = [t[1] for t in terms]
                if any(m in tnames for m in TMSC_MARKS):
                    hits.append({"vi": name, "diagram_index": i, "diagram_owner": owner,
                                 "node_uid": uid, "label": label, "terminals": terms})
                    s.fact("C HIT {0} diagram[{1}] owner={2} node uid={3} terms={4!r}".format(
                        name, i, owner, uid, terms))
    s.R["loop_bodies_scanned"] = scanned
    s.R["tmsc_in_loop_body"] = hits
    s.fact("C scanned {0} loop-body diagram(s) across {1} op VI(s); {2} TMSC hit(s)".format(
        len(scanned), len(set(x[0] for x in scanned)), len(hits)))
    s.gate("C1 at least one op VI carries a To More Specific Class INSIDE a loop body (free "
           "prediction; a PASS makes route (a) the construction)", bool(hits),
           "hits={0!r}".format([(h["vi"], h["diagram_index"], h["node_uid"]) for h in hits]))


S = K.Stage(SRC, SRC_MD5, "diag_allterms_donor", fresh=False, deadline_min=22.0, reserve_s=180.0,
            out_json=os.path.join(K.BENCH, "diag_allterms_donor.json"),
            task="How does a To More Specific Class get inside a loop body without move_in? "
                 "Routes (a) donor / (b) loop_in / (c) copy_by_index-to-nested / (S) subVI-in-loop. "
                 "Read-only apart from one dated scratch copy of OpReport_v3.vi. Nothing saved.")
sys.exit(K.run(main, S))
