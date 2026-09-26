r"""par1359_95_pre.py - card 95-2 PD202(d)1: READ-ONLY precondition on For #1359 (body diagram #7911) of D1_s1_copy.vi,
on a unique scratch BYTE COPY (stagekit work copy, discard_work, never saved, no VI run).
EXISTING READERS ONLY (docs/toolkit-capabilities.md rows 23-27): report_all (OpReportAll_v0), node_labels (OpNodeLabels_v0,
Diagram.Nodes[] of ONE diagram), subvis (OpSubVIs_v1), loop_cast (OpLoopCast_v1), count (OpReport), COM VirtualInstrument
ReentrancyType/IsReentrant (read in tools/bench/replay_vis_76d_defaults.log:4). Offline prior: docs/wiki/subvi/D1_s1_copy.json
terminals with frame_diagram 7911 = 12 nodes (8566 8764 8634 8741 8775 8795 11310 27716 28083 28180 28233 29009), no
Local/Global/FeedbackNode/structure; graph_s1_20260924.json has no FeedbackNode class at all.
PREDICTION: live Nodes[] of #7911 == those 12 uids; FeedbackNode/Local/Global/structure uids on #7911 = 0; #1359 SR = 0;
subVI calls = 4 (Median Filter.vi, FIR Filter (DBL).vi + 2); callee reentrancy/state RECORDED (not asserted), unreadable
-> NOT READABLE. Callee md5 unchanged. Ends with LabVIEW killed.
    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/par1359_95_pre.log -- py -u tools/bench/par1359_95_pre.py"""
import json, os, sys, time                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                                     # noqa: E402
g = K.g
from build_d1_v0 import owner_of                                                         # noqa: E402  (as diag_c94c_f7911.py:17)
S1 =os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"  # noqa: E702
PLAN = json.load(open(os.path.join(HERE, "par1359_95_plan.json"), encoding="utf-8"))   # decision 8: uids from the plan only
BODY, LOOP, OFF = int(PLAN["body_diagram"]), int(PLAN["loop"]), set(int(u) for u in PLAN["offline_nodes"])  # noqa: E702
STATE = ("FeedbackNode", "Local", "Global")
STRUCT = ("ForLoop", "WhileLoop", "CaseStructure", "FlatSequence", "Sequence", "EventStructure", "TimedLoop", "FormulaNode")
CALLEE_CLS = ("FeedbackNode", "Global", "Local", "LeftShiftRegister", "SubVI", "Diagram", "Node")
s = K.Stage(S1, S1_MD5, "par1359_95_pre", work_name="scratch_c95_pre_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=20, reserve_s=180, preload=False, task="95-2")


def uids_of(cls):
    v, err = s.safe("report_all(%s)" % cls, lambda: [o["uid"] for o in g.report_all(s.work, cls)])
    return (set(v) if v is not None else None), err


def callee(path, depth):
    rec = {"path": path, "md5_before": K.md5(path) if os.path.exists(path) else "MISSING"}
    try:
        with g.vi_ref(path) as v:
            for p in ("ReentrancyType", "IsReentrant", "ExecState"):
                try:
                    rec[p] = getattr(v, p)
                except Exception as e:                                                   # noqa: BLE001
                    rec[p] = "NOT READABLE (%s)" % type(e).__name__
    except Exception as e:                                                               # noqa: BLE001
        rec["ref_err"] = str(e)[:150]
    for c in CALLEE_CLS:
        n, err = s.safe("count(%s,%s)" % (os.path.basename(path), c), lambda c=c: g.count(path, c))
        rec[c] = n if not err else "NOT READABLE"
    kids = []
    nd = rec.get("Diagram") if isinstance(rec.get("Diagram"), int) else 1
    for k in range(max(1, nd)):
        rows, err = s.safe("subvis(%s,%d)" % (os.path.basename(path), k), lambda k=k: g.subvis(path, k, strict=False))
        if rows:
            kids += [r["path"] for r in rows[0]]
    rec["subvis"] = sorted(set(kids))
    s.fact("CALLEE d%d %s: %s" % (depth, os.path.basename(path), {k: v for k, v in rec.items() if k not in ("path", "subvis")}))
    s.fact("CALLEE d%d %s subVIs: %s" % (depth, os.path.basename(path), [os.path.basename(x) for x in rec["subvis"]]))
    if depth < 2:
        rec["children"] = [callee(x, depth + 1) for x in rec["subvis"][:8]]
    rec["md5_after"] = K.md5(path) if os.path.exists(path) else "MISSING"
    s.gate("CM %s md5 unchanged by the read" % os.path.basename(path), rec["md5_after"] == rec["md5_before"])
    return rec


def body(_):
    s.start(); s.discard_work()                                                          # noqa: E702
    di = s.uid_index("Diagram", BODY)
    s.gate("A diagram #7911 on report_all('Diagram')", di is not None, "index %r" % di, fatal=True)
    rows, err = s.safe("node_labels(7911)", lambda: g.node_labels(s.work, di))
    live = set(r["uid"] for r in rows or []) - {BODY}     # the diagram's own uid is not a node (the dry stub lists it)
    s.R["nodes_7911"] = sorted(live)
    s.fact("NODES on #7911 (Diagram.Nodes[]): %d %s ; not in offline set %s ; offline not live %s" % (
        len(live), sorted(live), sorted(live - OFF), sorted(OFF - live)))
    for cls in STATE + STRUCT:
        u, e = uids_of(cls)
        hit = sorted(u & live) if u is not None else None
        s.R.setdefault("classes", {})[cls] = {"in_vi": None if u is None else len(u), "on_7911": hit, "err": e}
        s.fact("CLASS %-14s in VI %s ; on #7911 %s%s" % (cls, "NOT READABLE" if u is None else len(u), hit, (" err " + e[:80]) if e else ""))
        if cls in STATE:
            s.gate("B %s nodes on #7911 == 0" % cls, hit == [], repr(hit))
    cand = sorted(x for c in STRUCT for x in (s.R["classes"][c]["on_7911"] or []))
    s.row("A2 live non-structure Nodes[] of #7911 vs the 12 offline uids (symmetric diff)", sorted((live - set(cand)) ^ OFF), [])
    nested = []                     # a structure listed in Nodes[] is NESTED only if its owner IS diagram #7911 (OpOwnerChain_v1)
    for u in cand:
        o, err = s.safe("owner_of(%d)" % u, lambda u=u: owner_of(s.work, u, strict=True))
        if err or not o or int(o[1]) == BODY:
            nested.append((u, o, err[:60]))
    s.R["nested"] = nested
    s.gate("B2 no nested structure owned by #7911 (the subtree is #7911 alone)", nested == [], repr(nested)[:300])
    li = s.uid_index("ForLoop", LOOP)
    lc, err = s.safe("loop_cast(1359)", lambda: g.loop_cast(s.work, li, "ForLoop"))
    s.R["loop_cast"] = lc
    s.gate("C #1359 shift registers == 0 (loop_cast echo 1359)", bool(lc) and lc["loop_uid"] == LOOP and not lc["shift_reg_uids"], repr(lc))
    sv, err = s.safe("subvis(7911)", lambda: g.subvis(s.work, di))
    s.R["subvis_7911"] = sv
    for r in sv or []:
        s.fact("SUBVI #%d %s | %s" % (r["uid"], r["name"], r["path"]))
    s.gate("D subVI calls on #7911 read (uid echo within the node set)", bool(sv) and all(r["uid"] in live for r in sv), "%d" % len(sv or []))
    s.R["callees"] = [callee(p, 1) for p in sorted(set(r["path"] for r in sv or []))]
    s.fact("HANDLES after reads: %r" % K.mod("bench_prep").labview_handles())


sys.exit(K.run(body, s))     # LabVIEW is stopped and verified gone by the calling session after BGRUN END (dry blocks subprocess here)
