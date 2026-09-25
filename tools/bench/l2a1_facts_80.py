r"""l2a1_facts_80 - card 80-5 (docs/d1-loop12-17-split-plan.md 178(e)(i), 179; STATUS NEXT cycle 80 (1)). Facts for stage
L2-A1 on the bed claudeDev\D1_k_20260925_100155.vi (md5 6cf5b077...) in k_facts_79.py's shape, from a LIVE read (no D1_k
graph was on disk). Two modes, one LabVIEW launch each; NOTHING saved, every copy deleted, no VI run, no motor/camera/GUI.
  facts   : dated work copy -> wiki_build.read_live + k_contract_79.mloops + build_d1_v0.owner_of (every Diagram + every
            structure owning one) -> F1 group A, F2 ControlTerminals, F3 SR pairs, F4 K open rows + w10990, F5 Case frames +
            a computation_diff merge example -> l2a1_graph_k_80.json (sim base) + l2a1_facts_80.json.
  tunflip : per candidate move, stagesim.op_move_in on that graph with nodes = the uid + everything inside its frames
            (stagesim moves only the named uids; reported, NOT changed) -> tunnel flips classed by branch -> moves executed
            on a FRESH dated scratch of D1_k (stagekit.move_in) -> read_live -> per-branch predicted vs real + stagexec.compare.
PRIOR ART: k_facts_79.py, k_contract_79.py (read_live/mloops), k_op3_read_79.py (move on scratch -> read vs sim),
stagexec.compare, stagesim.op_move_in/_flip_orphaned_output_tunnels (:310-340), vigraph.computation_diff. No new op.
PREDICTIONS: P1 cdiff(S1, D1_k) == 178(c)'s 10 PB rows on nodes {376,2626,5058,5696,6085,10757,10969}; P2 every named uid
owns >= 1 terminal row; P3 bed md5 unchanged, refs opened==closed, copies deleted, LabVIEW gone. Branch outcomes REPORTED.
  MATERIAL=1 py tools/bgrun.py --material --max-min 45 --log tools/bench/l2a1_facts_80.log -- py -u tools/bench/l2a1_facts_80.py facts
  MATERIAL=1 py tools/bgrun.py --material --max-min 55 --log tools/bench/l2a1_tunflip_80.log -- py -u tools/bench/l2a1_facts_80.py tunflip"""
import collections, json, os, subprocess, sys, time                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, vigraph as V, jev_candidates as JC, stagesim as SS, stagexec as SX  # noqa: E401,E402
B, MODE = K.BENCH, (sys.argv[1] if len(sys.argv) > 1 else "facts")
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
GA, CT, SRP, BODY = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757], [17487, 5634], [(1147, 1142), (5796, 5805), (7311, 11001)], 23166
GP, FJ = os.path.join(B, "l2a1_graph_k_80.json"), os.path.join(B, "l2a1_facts_80.json")
WIKI = json.load(open(os.path.join(K.ROOT, "docs", "wiki", "subvi", JC.BED_KEY + ".json"), encoding="utf-8"))
KF = dict((r["t"], r) for r in json.load(open(os.path.join(B, "k_facts_79.json"), encoding="utf-8"))["rows"])
MEASURED = {("LoopTunnel", "OuterTerminal"), ("SelectorTunnel", "InnerTerminal")}   # flipped side; stagesim.py:313-316
PB = {376, 2626, 5058, 5696, 6085, 10757, 10969}


def loop_of(O, d):
    for _n in range(14):
        c, u = O.get(d, ("?", 0))
        if c in ("WhileLoop", "ForLoop"):
            return "{0}#{1}".format(c, u)
        if not u or c not in V.STRUCT_OWNER:
            return "top(D{0}:{1})".format(d, c)
        d = O.get(u, ("?", 0))[1]
    return "?"


def closure(O, T, S):
    D, grow = set(), {S}
    while grow:
        f = set(d for d, (c, u) in O.items() if u in grow) - D
        D |= f
        grow = set(u for u, (c, d) in O.items() if d in f and c == "Diagram" and u not in D) - {S}
    return {S} | set(V.node_of(r) for r in T if int(r.get("frame_diagram") or 0) in D), D


def facts(s):
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); BD = K.mod("build_d1_v0")    # noqa: E702
    s.fact("HANDLES after open {0!r}".format(bp.labview_handles()))
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=WIKI["fs_tunnel_pairs"]); loops = K.mod("k_contract_79").mloops(s, s.work)  # noqa: E702
    T, CL = V.dedupe_rows(lv["terminals"])[0], dict((int(o["uid"]), o["class"]) for o in lv["objs"])
    gr = {"vi": BED, "md5": BED_MD5, "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": lv["fs_tunnel_pairs"], "graph_summary": WIKI["graph_summary"]}
    json.dump(gr, open(GP, "w", encoding="utf-8")); s.fact("LIVE {0} rows {1} -> {2} md5 {3}".format(len(T), lv["secs"], GP, K.md5(GP)))  # noqa: E702
    O, t0 = {}, time.time()
    todo = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"] + GA + CT + [u for p in SRP for u in p]
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        O[u] = tuple(s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(s.work, u, strict=False), ("?", 0))[0])
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    s.fact("OWNERS {0} objects resolved in {1:.0f} s".format(len(O), time.time() - t0))
    by, WI = collections.defaultdict(list), collections.defaultdict(list)
    for r in T:
        by[V.node_of(r)].append(r); WI[r["wire_uid"]].append(r)                    # noqa: E702
    fd = lambda r: int(r.get("frame_diagram") or 0)                                # noqa: E731
    end = lambda r, x: {"uid": V.node_of(x), "cls": V.node_class(x), "term": x["term_name"], "src": x["is_source"],   # noqa: E731
                        "frame": fd(x), "loop": loop_of(O, fd(x))}
    row = lambda r: {"term_uid": r["term_uid"], "name": r["term_name"], "tcls": r["term_class"], "src": r["is_source"],  # noqa: E731
                     "wire": r["wire_uid"], "frame": fd(r), "loop": loop_of(O, fd(r)),
                     "ends": [end(r, x) for x in WI[r["wire_uid"]] if x is not r] if r["wire_uid"] else []}
    def dump(tag, u):
        clo, D = closure(O, T, u)
        rs = by[u] + [r for r in T if V.node_of(r) in clo - {u} and r["term_class"] == "OuterTerminal" and fd(r) not in D]
        out = {"uid": u, "class": V.node_class(by[u][0]) if by[u] else CL.get(u), "owner": O.get(u),
               "loop": loop_of(O, O.get(u, ("?", 0))[1]), "frames": sorted(D), "rows": [row(r) for r in rs]}
        s.fact("{0} #{1} {2} owner {3} loop {4} frames {5} rows {6}".format(tag, u, out["class"], out["owner"], out["loop"], len(D), len(rs)))
        for x in out["rows"]:
            s.fact("   t{0} {1!r} {2} {3} w{4} F{5} [{6}] -> {7}".format(x["term_uid"], x["name"], x["tcls"], "OUT" if x["src"] else "IN",
                   x["wire"], x["frame"], x["loop"], [(e["uid"], e["cls"], e["term"], e["loop"]) for e in x["ends"]]))
        return out
    s.head("F1 group A / F2 control terminals / F3 SR pairs")
    tab = {"F1": [dump("F1", u) for u in GA], "F2": [dump("F2", u) for u in CT], "F3": [[dump("F3", a), dump("F3", b)] for a, b in SRP]}
    allu = [x["uid"] for x in tab["F1"] + tab["F2"] + [y for p in tab["F3"] for y in p] if x["rows"]]
    s.gate("P2 every named uid owns >= 1 terminal row (a structure: >= 1 border row of its tunnels)",
           len(allu) == len(GA + CT) + 6, sorted(set(GA + CT + [x for p in SRP for x in p]) - set(allu)))
    s.head("F4 K open rows t0 t3 t4 t7 t8 + w10990")
    tab["F4"] = {}
    for t in (0, 3, 4, 7, 8):
        r = next((x for x in by[5058] if x["term_uid"] == KF[t]["term_uid"]), None)
        tab["F4"]["t%d" % t] = row(r) if r else None
        s.fact("F4 t{0} {1!r} term {2}: {3}".format(t, KF[t]["name"], KF[t]["term_uid"], tab["F4"]["t%d" % t] and
               (tab["F4"]["t%d" % t]["wire"], [(e["uid"], e["cls"], e["term"], e["loop"]) for e in tab["F4"]["t%d" % t]["ends"]])))
    tab["F4"]["w10990"] = [end(None, x) for x in WI[10990]]
    s.fact("F4 w10990 rows: {0}".format([(e["uid"], e["cls"], e["term"], e["src"], e["loop"]) for e in tab["F4"]["w10990"]]))
    s.head("F5 Case frames + computation_diff keying (vigraph.py:244-245,301-306 key=node|class|name|ordinal, no frame; "
           ":332-346 thru joins every per-frame inner of one tunnel; :709-729,:749 cdiff compares SETS of sources)")
    G = JC.from_parts({"terminals": lv["terminals"], "graph_summary": WIKI["graph_summary"]}, lv["objs"], loops,
                      JC.node_labels_default(), lv["fs_tunnel_pairs"], "k80")
    tab["F5"] = {}
    for S in (5540, 10445):
        clo, D = closure(O, T, S)
        st = sorted(set(V.node_of(r) for r in T if V.node_of(r) in clo and r["owner_class"] == "SelectorTunnel"))
        ex = []
        for tu in st:
            ok_ = [r for r in by[tu] if r["term_class"] == "OuterTerminal" and fd(r) not in D]
            for r in ok_[:1]:
                k = next((k for k, x in G["rows"].items() if x["term_uid"] == r["term_uid"] and x["term_class"] == r["term_class"]), None)
                if k is None:
                    s.fact("   ST #{0} outer term {1} has no graph key".format(tu, r["term_uid"]))
                    continue
                es =V.sources_of(G, k, collapse=True) if r["is_source"] else SS.effective_consumers(G, k)
                ex.append({"tunnel": tu, "outer_src": r["is_source"], "key": k, "inner_frames": sorted(fd(x) for x in by[tu] if fd(x) in D),
                           "collapsed": sorted((V.show(q), int(G["rows"][q].get("frame_diagram") or 0)) for q in es)})
        tab["F5"][str(S)] = {"frames": sorted(d for d in D if O.get(d, ("?", 0))[1] == S), "all_nested": sorted(D), "selector_tunnels": ex}
        s.fact("F5 #{0} frames {1}; {2} selector tunnels".format(S, tab["F5"][str(S)]["frames"], len(ex)))
        for e in ex:
            s.fact("   ST #{0} outer {1} inner frames {2} -> collapsed {3}".format(e["tunnel"], "SRC" if e["outer_src"] else "SNK", e["inner_frames"], e["collapsed"][:8]))
    cd = V.computation_diff(JC.load(JC.S1_KEY), G)
    tab["cdiff"] = [dict((k, V.show(v) if k == "sink" else v) for k, v in r.items()) for r in cd["rows"]]
    for r in tab["cdiff"]:
        s.fact("CDIFF {0}".format(r))
    s.gate("P1 cdiff(S1, D1_k) == 10 rows on {0}".format(sorted(PB)), len(cd["rows"]) == 10 and set(r["node"] for r in cd["rows"]) == PB,
           (len(cd["rows"]), sorted(set(r["node"] for r in cd["rows"]))))
    s.R.update({"table": tab, "owners": dict((str(k), v) for k, v in O.items()), "graph": {"path": GP, "md5": K.md5(GP)}})
    s.fact("HANDLES end {0!r}".format(bp.labview_handles()))


def tunflip(s):
    s.start(); s.discard_work(); bp = K.mod("bench_prep"); BD = K.mod("build_d1_v0")    # noqa: E702
    F, gr = json.load(open(FJ, encoding="utf-8")), json.load(open(GP, encoding="utf-8"))
    O = dict((int(k), tuple(v)) for k, v in F["owners"].items()); T = V.dedupe_rows(gr["terminals"])[0]    # noqa: E702
    s.gate("T0 sim base graph is D1_k's read (md5 field) and l2a1_facts_80 recorded its file md5", gr["md5"] == BED_MD5 and F["graph"]["md5"] == K.md5(GP))
    S1, lab, P = JC.load(JC.S1_KEY), JC.node_labels_default(), SS.model_for("move_in", SS.load_models())[0]
    B0, cands = dict((r["term_uid"], r) for r in T), []
    for key, us in [("single{0}".format(u), [u]) for u in GA + CT] + [("joint", GA + CT)]:
        clo = set().union(*[closure(O, T, u)[0] for u in us])
        st = SS.base_state(gr); res, _c = SS.op_move_in(st, {"nodes": sorted(clo), "dest_diagram": BODY}, P, S1, lab)
        br = collections.Counter((SS.obj_class(st, f["tunnel"]), f["side"]) for f in res["tunnel_flips"])
        um = dict((str(b), n) for b, n in br.items() if b not in MEASURED)
        s.fact("SIM {0}: closure {1} nodes, cut {2}, flips {3}, UNMEASURED branches {4}".format(key, len(clo), res["n_cut"], dict((str(b), n) for b, n in br.items()), um))
        if key == "joint" or um:
            cands.append((len(um), key, [u for u in us if not any(u != v and u in closure(O, T, v)[0] for v in us)], st, res))
    cands = [c for c in cands if c[1] == "joint"] + sorted([c for c in cands if c[1] != "joint"], key=lambda c: -c[0])[:4]
    s.R["runs"] = []
    for _n, key, tops, st, res in cands:
        p = s.scratch(key[:10], BED); w0, s.work = s.work, p                        # noqa: E702
        for i, u in enumerate(tops):
            s.move_in(u, BD.diag_index(p, BODY), (4700 + 160 * i, 6300)); s.junk_purge("mv{0}".format(u))   # noqa: E702
        real = SX.dedupe(K.mod("wiki_build").read_live(p, fs_pairs=gr["fs_tunnel_pairs"])["terminals"]); s.work = w0   # noqa: E702
        R = dict((r["term_uid"], r) for r in real); pred = set(f["term_uid"] for f in res["tunnel_flips"])    # noqa: E702
        rflip = [r for r in real if r["owner_class"] in SS.TUN_FLIP and r["term_class"] in SS.TUN_SIDES and (B0.get(r["term_uid"]) or {}).get("is_source") and not r["is_source"]]
        tab = collections.defaultdict(lambda: {"pred": 0, "pred_seen": 0, "real_unpredicted": 0})
        for f in res["tunnel_flips"]:
            b = str((SS.obj_class(st, f["tunnel"]), f["side"])); tab[b]["pred"] += 1                        # noqa: E702
            tab[b]["pred_seen"] += int(bool(R.get(f["term_uid"])) and not R[f["term_uid"]]["is_source"])
        for r in rflip:
            if r["term_uid"] not in pred:
                tab[str((r["owner_class"], r["term_class"]))]["real_unpredicted"] += 1
        d = SX.compare(st["terminals"], real, {"term": {}, "obj": {}}, res["allow_either"])
        s.fact("RUN {0} moved {1}: per-branch {2}".format(key, tops, dict(tab)))
        s.fact("RUN {0} compare n={1} {2}".format(key, d["n"], json.dumps(dict((k, v[:8]) for k, v in d.items() if k not in ("n", "who") and v))[:900]))
        s.R["runs"].append({"key": key, "moved": tops, "branches": dict(tab), "compare": d,
                            "unpredicted": [(r["owner_uid"], r["term_uid"], r["term_class"], r["wire_uid"]) for r in rflip if r["term_uid"] not in pred]})
        s.drop_scratch(p, "H4 " + key)
    s.fact("HANDLES end {0!r}".format(bp.labview_handles()))


if __name__ == "__main__":
    st_ = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "scratch_l2a1_80", work_name="D1_k_scratch_l2a1_{0}_{1}.vi".format(MODE, st_), preload=False,
                pins=tuple(K.DEFAULT_PINS) + (("K bed", BED, BED_MD5),), deadline_min=40 if MODE == "facts" else 50,
                out_json=FJ if MODE == "facts" else os.path.join(B, "l2a1_tunflip_80.json"), task="card 80-5 " + MODE)
    K.run(facts if MODE == "facts" else tunflip, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
    s.gate("F7 LabVIEW process gone at the end", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    sys.exit(s.summary())
