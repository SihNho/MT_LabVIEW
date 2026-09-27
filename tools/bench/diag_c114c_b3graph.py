r"""diag_c114c_b3graph - card 114-2 M1-M4: SAVED L2-B3 graph, READ-ONLY on a byte copy (claudeDev\scratch_c114c_b3_<ts>.vi, deleted), no run/wire/delete/save,
LabVIEW killed at the end; OFFLINE vs graph_l2b2b_20260928.json. PRIOR ART (copied): diag_c114_b2bgraph.py (read_live+mloops+owner_of) + diag_c110_bedgraph.py
(cdiff_frame from a saved graph); no new op. OUT graph_l2b3_20260928.json + diag_c114c_b3graph.json. GATES = measurement integrity only. PRED = review c114b
hypothesis A (src net re-created with ALL old sinks + one new tunnel face; inner wire = face + sink only; 6 new wires = those nets), reported, not gated.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c114c_b3graph.log -- py -u tools/bench/diag_c114c_b3graph.py"""
import collections, hashlib, json, os, subprocess, shutil, sys, time               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V, jev_candidates as JC   # noqa: E401,E402
B3, B3_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b3_20260928_032703.vi"), "1b5c12d71ca48f22e3f4b80316c67e51"
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b2b_20260928_015450.vi"), "4f51fd4cb93e9116dee1bc0b07281f12"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c114c_b3_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT, TAB = os.path.join(HERE, "graph_l2b3_20260928.json"), os.path.join(HERE, "diag_c114c_b3graph.json")
J = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))            # noqa: E731
BASE, PLAN = J("graph_l2b2b_20260928.json"), J("plan_l2b3.json")
GROUPS = [(27635, 28392, 28378, 25870), (5186, 5174, 2996, 25891), (5671, 5336, 3193, 25985)]   # (src term, old wire, B3 sink term, tunnel; log:101)
NEWW = {25782, 25819, 25833, 25911, 26021, 26064}                                  # stage_d1_l2b3.log:103
gates, T = [], {}
OWN = [10170, 23166, 686, 28311, 28343, 5129, 5328, 27605, 5183, 5669, 28370, 2992, 3176, 25870, 25891, 25985]
gate = lambda lab, ok, d="": (gates.append((lab, bool(ok))), print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(d)[:900]), flush=True))   # noqa: E731
fact = lambda m: print("  FACT " + str(m)[:1500], flush=True)                     # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                     # noqa: E731


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        fact("{0} raised {1}".format(label, str(e)[:200])); return default, str(e)   # noqa: E702


def read():
    lv = K.mod("wiki_build").read_live(SCR, fs_pairs=BASE["fs_tunnel_pairs"])
    fact("LIVE {0} terminal rows, {1} objs".format(len(lv["terminals"]), len(lv["objs"])))
    loops, BD, ub = K.mod("k_contract_79").mloops(type("S", (), {"safe": lambda self, *a, **k: safe(*a, **k)})(), SCR), K.mod("build_d1_v0"), set(int(o["uid"]) for o in BASE["objs"])
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo = {}, diags + OWN + [int(o["uid"]) for o in lv["objs"] if int(o["uid"]) not in ub][:60]
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = safe("owner_of #{0}".format(u), lambda: BD.owner_of(SCR, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gate("O every live Diagram uid ({0}) has a resolved owner".format(len(diags)), all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:20])
    return {"vi": B3, "md5": B3_MD5, "source": "tools/bench/diag_c114c_b3graph.py (read_live + mloops + owner_of, byte copy)", "terminals": lv["terminals"],
            "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASE["fs_tunnel_pairs"], "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def offline(gr):
    net = lambda G, w: [(int(r["owner_uid"]), r["owner_class"], int(r["term_uid"]), r["term_name"], bool(r["is_source"])) for r in G["terminals"] if w and int(r["wire_uid"] or 0) == w]   # noqa: E731
    wof = lambda G, t: next((int(r["wire_uid"] or 0) for r in G["terminals"] if int(r["term_uid"]) == t), None); seen = set()   # noqa: E731,E702
    for st, ow, sk, tun in GROUPS:
        old = net(BASE, ow); olds = [x[2] for x in old if not x[4]]; ws, wk = wof(gr, st), wof(gr, sk)   # noqa: E702
        a, b = net(gr, ws), net(gr, wk); seen |= {ws, wk}                           # noqa: E702
        tt = [(int(r["term_uid"]), r["term_name"], r.get("term_class"), int(r["wire_uid"] or 0), r.get("frame_diagram")) for r in gr["terminals"] if int(r["owner_uid"]) == tun]
        onsrc = dict((o, o in [x[2] for x in a]) for o in olds); tsrc = [x for x in a if x[0] == tun]; tsk = [x for x in b if x[0] == tun]   # noqa: E702
        ex_a = [x for x in a if x[2] != st and x[2] not in olds and x[0] != tun]; ex_b = [x for x in b if x[2] != sk and x[0] != tun]   # noqa: E702
        T["M1_M2_t%d" % st] = {"bed_net": [ow, old], "src_wire_b3": ws, "src_net_b3": a, "sink_t": sk, "sink_wire_b3": wk, "sink_net_b3": b, "tunnel": tun,
                               "tunnel_terms": tt, "old_sinks_on_src_wire": onsrc, "tunnel_on_src_wire": tsrc, "tunnel_on_sink_wire": tsk, "extra_src": ex_a, "extra_sink": ex_b}
        fact("M1 t{0}: bed w{1} {2}".format(st, ow, old)); fact("M1 t{0}: B3 src w{1} {2}".format(st, ws, a)); fact("M1 t{0}: B3 sink t{1} w{2} {3}".format(st, sk, wk, b)); fact("M1 tunnel #{0} terms {1}".format(tun, tt))   # noqa: E702
        fact("M2 t{0}: old sinks on src wire {1}; tunnel face on src wire {2}; on sink wire {3}; extras src {4} sink {5}".format(st, onsrc, bool(tsrc), bool(tsk), ex_a, ex_b))
        fact("PRED-A t{0} {1}".format(st, "HOLDS" if all(onsrc.values()) and len(tsrc) == 1 and len(tsk) == 1 and not ex_a and not ex_b and ws not in (0, ow) else "DOES NOT HOLD"))
    wb, w3 = set(int(r["wire_uid"] or 0) for r in BASE["terminals"]) - {0}, set(int(r["wire_uid"] or 0) for r in gr["terminals"]) - {0}
    T["M2_wires"] = {"new_vs_bed": sorted(w3 - wb), "lost_vs_bed": sorted(wb - w3), "six_nets": sorted(seen), "launch_new": sorted(NEWW)}
    fact("M2 wires new vs bed {0}; lost {1}; the 6 nets' wires {2}; equals launch log new set {3}".format(sorted(w3 - wb), sorted(wb - w3), sorted(seen), seen == NEWW == (w3 - wb)))
    ca, cb = collections.Counter(o["class"] for o in BASE["objs"]), collections.Counter(o["class"] for o in gr["objs"])
    ua, ub, own = set(int(o["uid"]) for o in BASE["objs"]), set(int(o["uid"]) for o in gr["objs"]), gr["owners"]
    add = [(int(o["uid"]), o["class"], own.get(str(o["uid"]))) for o in gr["objs"] if int(o["uid"]) not in ua]
    rem = [(int(o["uid"]), o["class"]) for o in BASE["objs"] if int(o["uid"]) not in ub]
    T["M3"] = {"class_delta": dict((k, cb[k] - ca[k]) for k in set(ca) | set(cb) if cb[k] != ca[k]), "added": add, "removed": rem,
               "invoke_b3": sorted(int(o["uid"]) for o in gr["objs"] if o["class"] == "Invoke"), "invoke_bed": sorted(int(o["uid"]) for o in BASE["objs"] if o["class"] == "Invoke")}
    fact("M3 class delta {0}".format(T["M3"]["class_delta"])); fact("M3 added {0}".format(add)); fact("M3 removed {0}".format(rem)); fact("M3 Invoke objs B3 {0} / bed {1}".format(T["M3"]["invoke_b3"], T["M3"]["invoke_bed"]))   # noqa: E702
    lab, s1p = JC.node_labels_default(), json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
    S1f = V.build4(s1p["terminals"], json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"],
                   json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"], lab, s1p["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True))
    [fact("M4 CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items()))) for y in cd["rows"]]
    keys = sorted(set(str(y["sink"]) for y in cd["rows"])); want = sorted(PLAN["finalized"]["end_cdiff_rows"])   # noqa: E702
    pairs = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"])); wp = sorted((int(r["node"]), r["term"]) for r in PLAN["open_rows"])   # noqa: E702
    T["M4"] = {"rows": len(cd["rows"]), "keys": keys, "plan_end_keys": want, "extra_keys": sorted(set(keys) - set(want)), "missing_keys": sorted(set(want) - set(keys)),
               "pairs": pairs, "plan_open_pairs": wp, "pairs_equal": pairs == wp}
    fact("M4 cdiff rows {0}; keys == plan end_cdiff_rows ({1}): {2}; extra {3}; missing {4}; pairs == plan open_rows ({5}): {6}".format(
        len(cd["rows"]), len(want), keys == want, T["M4"]["extra_keys"], T["M4"]["missing_keys"], len(wp), pairs == wp))
    json.dump(T, open(TAB, "w", encoding="utf-8"), default=str, indent=1); fact("WROTE {0} md5 {1}".format(TAB, md5(TAB)))   # noqa: E702


def main():
    gate("K1 B3 md5 == pin; bed md5 == pin", md5(B3) == B3_MD5 and md5(BED) == BED_MD5, (md5(B3), md5(BED)))
    if sys.argv[1:2] == ["offline"]:
        gr = J(os.path.basename(OUT)); offline(gr); return finish(gr)             # noqa: E702
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or not gates[0][1]:
        return finish(None)
    shutil.copyfile(B3, SCR); gate("K2 scratch is a byte copy", md5(SCR) == B3_MD5, SCR)   # noqa: E702
    gr, h = None, []
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3); h.append(bench_prep.labview_handles())   # noqa: E702
        gr = dict(read(), handles=h); h.append(bench_prep.labview_handles()); n = len(g.report_all(SCR, "Wire")); h.append(bench_prep.labview_handles())   # noqa: E702
        fact("HANDLES (recorded, never re-based) after-restart {0} -> after-read {1} -> after 2nd Wire census ({2}) {3}; 2nd-read delta {4}".format(h[0], h[1], n, h[2], (h[2] or 0) - (h[1] or 0)))
    finally:
        g.reset(); subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        os.path.exists(SCR) and os.remove(SCR)
        gate("H LabVIEW gone; B3 + bed md5 unchanged; scratch deleted", gone and md5(B3) == B3_MD5 and md5(BED) == BED_MD5 and not os.path.exists(SCR), (gone, md5(B3), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8")); fact("WROTE {0} md5 {1}".format(OUT, md5(OUT))); offline(gr)   # noqa: E702
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok); ff = next((lab for lab, ok in gates if not ok), None)   # noqa: E702
    arts = [{"path": os.path.relpath(p, os.path.dirname(os.path.dirname(HERE))), "md5": md5(p)} for p in (OUT, TAB) if gr and os.path.exists(p)]
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=arts)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__": sys.exit(main())                                       # noqa: E701
