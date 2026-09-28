r"""diag_c116d_j1 - card 116-4 J1 (part 2): SCRATCH-VI CHECK of gscript.wire_joints (OpWireJoints_v0, Wire.Joints[] 6371005) on a
dated byte copy claudeDev\scratch_c116d_j1_<ts>.vi of the small op VI OpLoopCast_v0.vi (graph dump tools/bench/graph_oploopcast_v0_c95.json,
md5 89452a9a: its TMSC `specific class reference` w366 is a known BRANCH to Property #330/#238/#230). The branch is found live, not assumed: a top-level
wire with >= 2 sink terminals, one of them on a Property node. That Property node is deleted (no Remove Bad Wires) -> a KNOWN
DANGLING BRANCH. A second wire with exactly 1 sink has its sink Property node deleted -> a KNOWN LOOSE END. PRIOR ART: the reader
shape is diag_c97's; nothing else reads Joints[]. PREDICTION: every read echoes its uid, err ''; each wire's joints CHANGE after its
sink node is deleted (raw values recorded for the offline decode, diag_c116d_decode.py); a non-wire uid is refused (ValueError);
20 calls handles flat (+-100); scratch deleted; LabVIEW gone. PASS writes tools/bench/scratch_verify/gscript.wire_joints_<ts>.json.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c116d_j1.log -- py -u tools/bench/diag_c116d_j1.py"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(K.BENCH, "diag_c116d_j1_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
SRC = os.path.join(K.CLAUDEDEV, PL["input"]["vi"])
REC = os.path.join(K.BENCH, "scratch_verify")
OUT = {}


def nets(t):
    """{wire: {'src': [(node, i)], 'snk': [(node, i)]}} over the top-level Nodes[] (node_terms_uid)."""
    out = {}
    for n in range(80):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            break
        for r in rows:
            if r["wire"]:
                out.setdefault(int(r["wire"]), {"src": [], "snk": []})["src" if r["is_source"] else "snk"].append((int(uid), r["i"]))
    return out


def read(s, t, w, tag):
    r = g.wire_joints(t, w)
    OUT.setdefault(str(w), {})[tag] = r
    s.fact("JOINTS w{0} [{1}] echo {2} err {3!r} n={4} raw={5}".format(w, tag, r["echo"], r["err"], len(r["joints"] or ()), json.dumps(r["joints"], default=str)[:900]))
    return r


def body(s):
    print(__doc__, flush=True)
    t = s.start(); s.discard_work()                                                   # noqa: E702
    props = set(int(o["uid"]) for o in g.report_all(t, "Property"))
    N = nets(t)
    s.fact("top-level nets {0}".format(dict((w, (len(v["src"]), len(v["snk"]))) for w, v in N.items())))
    br = [(w, v) for w, v in sorted(N.items()) if len(v["src"]) <= 1 and len(v["snk"]) >= 2 and any(n in props for n, _i in v["snk"])]
    s.gate("F1 a top-level branched wire (<= 1 source seen in Nodes[], >= 2 sinks, one sink on a Property node) exists", bool(br), [w for w, _v in br], fatal=True)
    wb, vb = br[0]
    deg = lambda n: sum(1 for v in N.values() for m, _i in v["src"] + v["snk"] if m == n)   # noqa: E731
    pb = min((n for n, _i in vb["snk"] if n in props), key=lambda n: (deg(n), n))   # the leaf-most sink (fewest wired terminals)
    one = [(w, v) for w, v in sorted(N.items()) if w != wb and len(v["src"]) == 1 and len(v["snk"]) == 1 and v["snk"][0][0] in props
           and v["snk"][0][0] != pb and v["src"][0][0] != pb]
    b0 = read(s, t, wb, "branch before")
    o0 = read(s, t, one[0][0], "single before") if one else None
    s.gate("R0 reads before: uid echo ok, err '', joints non-empty", not b0["err"] and b0["joints"] and (o0 is None or (not o0["err"] and o0["joints"])), (b0["err"], o0 and o0["err"]))
    s.delete_object("Property", pb, tag="J1 branch sink")
    b1 = read(s, t, wb, "branch after (sink node #%d deleted)" % pb)
    s.gate("J1a the branched wire survives its sink node's delete and its joints CHANGE (a known dangling branch)",
           not b1["err"] and b1["joints"] and b1["joints"] != b0["joints"], (len(b0["joints"]), len(b1["joints"])))
    if one:
        s.delete_object("Property", one[0][1]["snk"][0][0], tag="J1 single sink")
        live = set(int(o["uid"]) for o in g.report_all(t, "Wire"))
        o1 = read(s, t, one[0][0], "single after (sink deleted)") if one[0][0] in live else None
        s.row("J1b single-sink wire w{0} after its sink's delete".format(one[0][0]), "gone" if o1 is None else (len(o1["joints"]), o1["joints"] != o0["joints"]))
    try:
        g.wire_joints(t, pb); neg = "NOT REFUSED"                                     # noqa: E702
    except ValueError as e:
        neg = str(e)[:120]
    s.gate("N1 a non-wire uid is refused (ValueError before the op runs)", neg != "NOT REFUSED", neg)
    bp = K.mod("bench_prep"); h0, ok = bp.labview_handles(), 0                          # noqa: E702
    idx = g._uid_index(t, "Wire", wb)
    for _k in range(20):
        r = g.wire_joints(t, wb, index=idx)
        ok += int(r["echo"] == wb and not r["err"] and r["joints"] == b1["joints"])
    h1 = bp.labview_handles()
    s.gate("HF 20 calls identical, handles flat (+-100)", bool(getattr(g.report_all, "_dry", False)) or (ok == 20 and abs(h1 - h0) <= 100), (ok, h0, h1))
    s.R["joints"] = OUT
    json.dump(OUT, open(os.path.join(K.BENCH, "diag_c116d_j1_raw.json"), "w", encoding="utf-8"), indent=1, default=str)


if __name__ == "__main__":
    st = K.Stage(SRC, PL["input"]["md5"], "scratch_c116d_j1", preload=False, deadline_min=12, pins=(),
                 out_json=os.path.join(K.BENCH, "diag_c116d_j1.json"), task="card 116-4 J1")
    rc = K.run(body, st)
    DRY = bool(getattr(g.report_all, "_dry", False))
    gone = DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not DRY:
        os.makedirs(REC, exist_ok=True)
        json.dump({"function": "gscript.wire_joints", "status": "PASS", "t": time.time(), "card": "116-4 J1",
                   "op": {"path": os.path.join(K.CLAUDEDEV, "OpWireJoints_v0.vi"), "md5": K.md5(os.path.join(K.CLAUDEDEV, "OpWireJoints_v0.vi"))},
                   "fixture": "scratch byte copy of claudeDev\\OpLoopCast_v0.vi (deleted)", "raw": "tools/bench/diag_c116d_j1_raw.json",
                   "log": "tools/bench/diag_c116d_j1.log"},
                  open(os.path.join(REC, "gscript.wire_joints_{0}.json".format(st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
