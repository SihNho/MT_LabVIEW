r"""l2a1_faces_81 - card 81-8 M1 (docs/d1-loop12-17-split-plan.md Pre-decided 185(1); review archive/peer/2026-09-25-hyp-l2a1-run1-81.md sec.4).
READ-ONLY on a byte copy of the bed D1_k (6cf5b077; stagekit work copy, discarded, never saved). For each SelectorTunnel sink end of the
L2-A1 plan (the plan's wire rows whose dst owner is a SelectorTunnel - #5825 #5702 #10750 #5725 #5967), find the OWNER structure (the owner
of the tunnel's inner frame diagram, base graph `owners`) and read its Diagram.Nodes[k].Terminals[] with gscript.node_terms_uid; count the
faces whose (name, is_source, wire) == the plan terminal's live row; also read whether the TUNNEL uid itself is in that Diagram's Nodes[].
PRIOR ART: build_d1_m3a1.log:1145-1154 (SelectorTunnel #12673 addressed as CaseStructure #12589 Nodes[47] t1); stagexec.LVReader
(node_labels / node_terms_uid / report_all Diagram) - the same reads, reused. No new op.
PREDICTION (the review's discriminating test): every target end has EXACTLY ONE matching face on its owner's Terminals[] (H-owner); the
tunnel uid is NOT in Nodes[] (run-1 log:302). A count != 1 falsifies the owner route for that end -> card rule: STOP before T1.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/l2a1_faces_81.log -- py -u tools/bench/l2a1_faces_81.py"""
import json, os, sys                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX                                 # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
P = J(K.BENCH, "sim/l2a1/plan_l2a1.json"); BASE = J(K.ROOT, P["finalized"]["base"]["path"])   # noqa: E702
T = BASE["terminals"]; OWN = BASE["owners"]; CLS = dict((int(o["uid"]), o["class"]) for o in BASE["objs"])   # noqa: E702
ENDS = [(a["id"], a["dst"]["uid"], a["dst"]["term_uid"]) for a in P["actions"]
        if a["op"] == "wire" and isinstance(a["dst"], dict) and CLS.get(a["dst"]["uid"]) == "SelectorTunnel"]


def owner_of(tun):
    inner = [r for r in T if r["owner_uid"] == tun and r["term_class"] == "InnerTerminal"]
    fr = set(str(r["frame_diagram"]) for r in inner)
    own = set(tuple(OWN[f]) for f in fr if f in OWN)
    return (sorted(own)[0] if len(own) == 1 else None), sorted(fr)


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                    # noqa: E702
    rd = SX.LVReader(g, s.work)
    dl = rd.diagrams()
    s.fact("ENDS {0}".format(ENDS))
    out = {}
    for aid, tun, tu in ENDS:
        row = [r for r in T if r["term_uid"] == tu]
        own, frames = owner_of(tun)
        ocls, ou = own or (None, None)
        orow = [r for r in T if r["owner_uid"] == ou]
        odiag = next((int(r["frame_diagram"]) for r in T if r["owner_uid"] == tun and r["term_class"] == "OuterTerminal"), None)
        s.fact("{0}: tunnel #{1} term {2} row {3}; owner {4} #{5} (frames {6}); outer diagram #{7}".format(
            aid, tun, tu, row and {k: row[0][k] for k in ("term_name", "term_class", "is_source", "wire_uid", "frame_diagram")}, ocls, ou, frames, odiag))
        if not row or ou is None or odiag not in dl:
            s.gate("M1 {0}: owner + outer diagram resolvable from the base graph".format(aid), False, (bool(row), ou, odiag))
            continue
        di = dl.index(odiag)
        uids, _e = s.safe("node_labels D[{0}]".format(di), lambda: rd.node_uids(di), [])
        s.fact("{0}: tunnel #{1} in Diagram[{2}] #{3}.Nodes[]: {4}; owner #{5} in it: {6}".format(aid, tun, di, odiag, tun in uids, ou, ou in uids))
        if ou not in uids:
            s.gate("M1 {0}: owner #{1} listed in Diagram #{2}.Nodes[]".format(aid, ou, odiag), False, len(uids))
            continue
        ni = uids.index(ou)
        (echo, nt), _e = s.safe("node_terms D[{0}].N[{1}]".format(di, ni), lambda: rd.node_terms(di, ni), (None, []))
        r = row[0]
        key = (r["term_name"], bool(r["is_source"]), int(r["wire_uid"] or 0))
        hits = [x["i"] for x in nt if (x["name"], bool(x["is_source"]), int(x["wire"] or 0)) == key]
        s.fact("{0}: owner #{1} echo {2}, {3} terminals {4}".format(aid, ou, echo, len(nt), [(x["i"], x["name"], x["is_source"], x["wire"]) for x in nt][:40]))
        s.gate("M1 {0}: owner #{1} Terminals[] has EXACTLY ONE face == #{2} key {3} (hits {4})".format(aid, ou, tu, key, hits),
               echo == ou and len(hits) == 1, hits)
        out[aid] = {"tunnel": tun, "term": tu, "owner": ou, "owner_class": ocls, "diagram": odiag, "hits": hits, "n_terms": len(nt),
                    "tunnel_in_nodes": tun in uids, "own_rows_base": len(orow)}
    s.R["m1"] = out; s.dump()


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_k_scratch_faces81", preload=False, deadline_min=22,
                 out_json=os.path.join(K.BENCH, "l2a1_faces_81.json"), task="card 81-8 M1")
    sys.exit(K.run(body, st))
