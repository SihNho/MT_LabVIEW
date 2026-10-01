r"""diag_c125_4fsm - card 125-4 STEP B.1 (brief_125-4.md): diag_c125_fsmethods.py (card 125-2, md5 dcdd7bbe, never run) RE-POINTED
at a never-saved byte copy of the P3a bed (claudeDev\D1_ring_p3a_20261001_180540.vi, md5 4dfa44aa): the launch gate's dry run needs a
graph JSON for the input md5 and DonorCase_v0 has none (graph_ring_p3a_20261001_190155.json carries the bed's). Nothing else changed.
MEASURE the VI Scripting method that adds a frame to a Flat Sequence. No method id is recorded anywhere (docs/vi-server-ids.json has
FlatSequence PROPERTIES 3578BC00 Diagrams[] / 3578BC07 Frames[] only); the fact peer (gemini, unsourced) names FlatSequence."Add Frame"
(Frame Index, After?) but NOT its id. Our ids put a class's methods 0x400 below its property base (GObject 632A800 / Move 632A400;
Terminal 634A000 / 6349C0x) -> candidates FlatSequence 3578B800..0F and FlatSequenceFrame 18E76400..0F.
ROUTE (existing op only): gscript.build_invoke (OpBuildInvoke, method by unique id) on the byte copy's top-level diagram; per candidate:
did ONE Invoke appear, and what are its terminal names (node_terms_uids)?
PREDICTION: >= 1 FlatSequence candidate yields an Invoke whose terminals name a frame index / after flag (the frame-add method);
X bed md5 unchanged; scratch deleted; LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c125_4fsm.log -- py -u tools/bench/diag_c125_4fsm.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                         # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c125_4fsm_plan.json"), encoding="utf-8"))
DON, DONM = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
DRY = bool(getattr(g.report_all, "_dry", False))
CANDS = [("VI Server:FlatSequence", "3578B8%02X" % k) for k in range(16)] + [("VI Server:FlatSequenceFrame", "18E764%02X" % k) for k in range(16)]
s = K.Stage(DON, DONM, "scratch_c125_4fsm", preload=False, deadline_min=18, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c125_4fsm.json"), task="card 125-4 B1")


def probe(W, cls, mid, k):
    inv0 = set(g.uids(W, "Invoke"))
    try:
        g.build_invoke(W, cls, mid, (40 + 160 * (k % 8), 300 + 120 * (k // 8)))
        e = ""
    except Exception as ex:                                                                  # noqa: BLE001
        e = str(ex)[:160]
    new = sorted(set(g.uids(W, "Invoke")) - inv0)
    rows = []
    for u in new:
        try:
            ni = g._node_index(W, 0, u)
            _echo, rr = g.node_terms_uids(W, 0, ni)
            rows.append([(str(r["name"]), bool(r["is_source"])) for r in rr])
        except Exception as ex:                                                              # noqa: BLE001
            rows.append("terms read failed: %s" % str(ex)[:120])
    return {"cls": cls, "id": mid, "err": e, "new": new, "terms": rows}


def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    out = []
    for k, (cls, mid) in enumerate(CANDS):
        r = s.safe("probe {0} {1}".format(cls, mid), lambda: probe(W, cls, mid, k), {})[0] or {}
        s.fact("PROBE {0}".format(json.dumps(r, default=str)))
        out.append(r)
        if s.left_s() < 200:
            s.fact("STOP probing: time reserve")
            break
    hit = [r for r in out if r.get("new") and any(isinstance(t, list) and len(t) > 2 for t in r.get("terms") or [])]
    json.dump({"donor": DON, "donor_md5": DONM, "probes": out}, open(os.path.join(HERE, "diag_c125_4fsm_probes.json"), "w", encoding="utf-8"), indent=1)
    s.gate("M1 >= 1 FlatSequence/FlatSequenceFrame candidate id makes an Invoke with method terminals",
           bool(hit), [(r["cls"], r["id"], r["terms"]) for r in hit][:8])
    s.gate("X bed md5 unchanged", K.md5(DON) == DONM, K.md5(DON))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
