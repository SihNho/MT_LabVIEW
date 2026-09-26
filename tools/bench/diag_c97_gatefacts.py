r"""diag_c97_gatefacts.py - card 97-1 (A): READ-ONLY machine read of every node LABEL of D1_s1_copy.vi on a unique
scratch BYTE COPY (claudeDev\scratch_c97_<ts>.vi, deleted by close()). Existing ops only: OpNodeLabels_v0
(g.node_labels, docs/toolkit-capabilities.md:26 - an implicit property/invoke node's label IS its bound panel
object's name), OpOwnerChain_v1 (build_d1_v0.owner_of, :65). Offline prior (diag_c97_gatefacts_off2.log): of 145
Property/Invoke/CtlRefConst/Local/Global/EventStructure nodes, the 2026-09-14 sweep of a SIBLING VI labels exactly one
with 'Force (pN) vs Extension (nm) ': Invoke #10313 'Reinit To Dflt' on diagram 3628, every terminal unwired.
PREDICTION CONTRACT: G1 labels read for all Traverse('Diagram') indices with op error ''; G2 all 145 candidate uids
found; G3 the labels of the 145 equal the 09-14 sweep; G4 the set of nodes labelled 'Force (pN) vs Extension (nm)' is
exactly {10313}; owners: 10313 -> Diagram 3628, 639 -> WhileLoop 637, 11261 -> Diagram 639. Nothing saved, no VI run.
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K
g = K.g
from build_d1_v0 import owner_of

S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
GRAPH = json.load(open(os.path.join(HERE, "par1359_95_graph.json"), encoding="utf-8"))
OLD = {}
for d, lst in json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))["diagrams"].items():
    for n in lst:
        OLD[n["uid"]] = n["label"]
CAND = {o["uid"]: o["class"] for o in GRAPH["objs"] if o["class"] in
        ("Property", "Invoke", "ControlReferenceConstant", "Local", "Global", "EventStructure")}
KEY = "Force (pN) vs Extension"
s = K.Stage(S1, S1_MD5, "diag_c97_gatefacts", work_name="scratch_c97_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=20, reserve_s=180, task="97-1")


def body(_):
    s.start(); s.scratches.append(s.work)
    bp = K.mod("bench_prep"); s.fact("HANDLES before reads: %r" % bp.labview_handles())
    diags = [o["uid"] for o in g.report_all(s.work, "Diagram")]
    s.fact("Traverse('Diagram') = %d diagrams" % len(diags))
    lab, errs = {}, {}
    for i, du in enumerate(diags):
        rows, err = g.node_labels(s.work, i, strict=False)
        if err:
            errs[i] = err[:120]
        for r in rows:
            lab[r["uid"]] = {"label": r["label"], "diag_index": i, "diag_uid": du}
    s.R["labels"] = {str(k): v for k, v in lab.items()}
    s.gate("G1 node_labels on every diagram, op error ''", not errs, "errors %r" % dict(list(errs.items())[:5]))
    miss = sorted(u for u in CAND if u not in lab)
    s.gate("G2 all %d candidate uids read" % len(CAND), not miss, "missing %r" % miss[:20])
    diff = [(u, OLD.get(u), lab[u]["label"]) for u in sorted(CAND) if u in lab and lab[u]["label"] != OLD.get(u)]
    s.gate("G3 candidate labels == 2026-09-14 sweep", not diff, "diffs %r" % diff[:10])
    hits = sorted(u for u, v in lab.items() if KEY in (v["label"] or ""))
    s.R["hits"] = hits
    for u in hits:
        s.fact("LABEL HIT #%d class %s label %r on diagram index %d uid %d" % (
            u, CAND.get(u, "?"), lab[u]["label"], lab[u]["diag_index"], lab[u]["diag_uid"]))
    s.gate("G4 nodes labelled '%s' == {10313}" % KEY, hits == [10313], repr(hits))
    for u, want in ((10313, 3628), (639, 637), (11261, 639), (3628, None), (7921, None), (644, None)):
        v, err = s.safe("owner_of(%d)" % u, lambda u=u: owner_of(s.work, u, strict=True))
        s.fact("OWNER #%d -> %s" % (u, "NOT READABLE (%s)" % err[:100] if err else "%s#%s" % tuple(v)))
        if want is not None:
            s.gate("O owner of #%d is #%d" % (u, want), bool(v) and int(v[1]) == want, repr(v))
    s.fact("HANDLES after reads: %r" % bp.labview_handles())


rc = K.run(body, s)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
               capture_output=True)
time.sleep(4)
gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
s.gate("Z LabVIEW gone after the run", gone); s.dump(); rc = s.summary()
sys.exit(rc)
