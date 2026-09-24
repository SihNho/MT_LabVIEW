r"""diag_swap_measure - card 75-4 part B (m8 plan PD14(c)(d)): MEASURE the callee-swap verb `gscript.replace_object`
(OpReplaceGObj_v0, built by diag_swap_build.py) on a dated SCRATCH copy of D1_s1_copy.vi: #6810 -> a byte copy of its
callee under a new name, claudeDev\replay\swapprobe_get_buff.vi. Readers reused: wiki_build.read_live (terms+objs),
gscript.subvis (callee census), vigraph.build4/computation_diff as tools/bench/cdiff_blindspot_74.py builds S1.
PREDICTION (PD14(c)): P1 pins S1/S3/callee orig+copy unchanged; P2 probe md5 == 9aaaef21...; P3 before: #6810 on diagram
uid 639 calls get buff image-lost frames.vi; P4 replace_object returns no error and a new uid (kept/changed = FACT);
P5 callee read back == probe path; P6 wire-edge diff(before, after), swapped node remapped to #6810 == EMPTY;
P7 callee census diff == exactly #6810; P8 ExecState 1; cdiff(S1wiki, after) rows RECORDED (ROT O6); P9 20 swaps
back and forth (orig, probe x10): each returns no error, handle range within +-100; P10 after the 20: edges still ==
before, callee == probe; P11 scripted save as claudeDev\swapprobe_S1_<ts>.vi; P12 LabVIEW gone. No VI is run.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/swap_verb_75.log -- py -u tools/bench/diag_swap_measure.py"""
import os, sys, json, time, shutil, subprocess                                        # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                 # noqa: E402
g, J = K.g, (lambda p: json.load(open(os.path.join(K.ROOT, p), encoding="utf-8")))  # noqa: E731
S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); S3 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi")
GB_ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\get buff image-lost frames.vi"
GB_COPY = os.path.join(K.CLAUDEDEV, "background VIs_COPY", "get buff image-lost frames.vi")
PROBE = os.path.join(K.CLAUDEDEV, "replay", "swapprobe_get_buff.vi"); GBM = "9aaaef21"
PINS = (("S1", S1, "3e3d23cefd3a334001aa9d6156bf1aee"), ("S3", S3, "1a11d92aacabf7ec844d65b8af19f39f"),
        ("gb_orig", GB_ORIG, K.md5(GB_ORIG)), ("gb_copy", GB_COPY, K.md5(GB_COPY)))
s = K.Stage(S1, PINS[0][2], "swap_verb_75", fresh=False, preload=False, deadline_min=27, pins=PINS,
            work_name="swapprobe_S1_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")), task="75-4",
            out_json=os.path.join(K.BENCH, "swap_verb_75.json"))
T = s.work; W1 = J("docs/wiki/subvi/D1_s1_copy.json"); FS = W1["fs_tunnel_pairs"]
V, JC, WB, bp = K.mod("vigraph"), K.mod("jev_candidates"), K.mod("wiki_build"), K.mod("bench_prep")
L1, LAB = J("tools/bench/graph_loops_s1_20260924.json")["loops"], JC.node_labels_default()


def edges(live, remap):
    own = lambda r: remap.get(r["owner_uid"], r["owner_uid"])                    # noqa: E731
    by = {}
    for r in live["terminals"]:
        if r["wire_uid"]:
            by.setdefault(r["wire_uid"], []).append(r)
    return set((own(a), a["term_name"], own(b), b["term_name"]) for rs in by.values() for a in rs if a["is_source"]
               for b in rs if not b["is_source"])


def census(d):
    return dict((int(x["uid"]), x["path"]) for x in g.subvis(T, d))


def main(s):
    s.head("[0] files"); ok = s.pin_check("BEFORE")
    s.gate("P1a pins hold before", ok and PINS[2][2].startswith(GBM) and PINS[3][2] == PINS[2][2], "", fatal=True)
    os.makedirs(os.path.dirname(PROBE), exist_ok=True); shutil.copyfile(GB_COPY, PROBE); shutil.copyfile(S1, T)
    s.gate("P2 probe is a byte copy of the callee", K.md5(PROBE).startswith(GBM), K.md5(PROBE))
    s.head("[1] restart; BEFORE reads"); s.restart(); g.ensure_loaded(T)
    es0 = g.exec_state(T); s.fact("scratch ExecState before {0}".format(es0))
    d = [int(o["uid"]) for o in g.report_all(T, "Diagram")].index(639)
    c0 = census(d); s.fact("diagram 639 = Traverse index {0}; callees {1}".format(d, c0))
    s.gate("P3 #6810 calls get buff image-lost frames.vi", str(c0.get(6810, "")).endswith("get buff image-lost frames.vi"), c0.get(6810))
    L0 = WB.read_live(T, fs_pairs=FS); E0 = edges(L0, {}); s.fact("before: {0} terms, {1} edges".format(len(L0["terminals"]), len(E0)))
    s.head("[2] SWAP #6810 -> probe"); h = [bp.labview_handles()]
    r = g.replace_object(T, 6810, PROBE); s.fact("replace_object -> {0}".format(r)); s.R["swap1"] = r
    s.gate("P4 replace_object: no error, a new-object uid", not r["err_replace"] and not r["err"] and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]; s.fact("NODE UID {0}: {1}".format("KEPT" if nu == 6810 else "CHANGED", (6810, nu)))
    c1 = census(d); s.gate("P5 callee read back == probe", os.path.normcase(str(c1.get(nu))) == os.path.normcase(PROBE), c1.get(nu))
    L1v = WB.read_live(T, fs_pairs=FS); E1 = edges(L1v, {nu: 6810})
    s.gate("P6 wire-edge diff(before, after) == empty (swapped node remapped)", E0 == E1, {"removed": sorted(E0 - E1)[:12], "added": sorted(E1 - E0)[:12]})
    tu0 = set((x["term_uid"], x["wire_uid"]) for x in L0["terminals"]); tu1 = set((x["term_uid"], x["wire_uid"]) for x in L1v["terminals"])
    s.fact("raw (term_uid, wire_uid) rows: -{0} +{1}".format(len(tu0 - tu1), len(tu1 - tu0)))
    dd = dict((k, (c0.get(k), c1.get(k))) for k in set(c0) | set(c1) if c0.get(k) != c1.get(k))
    s.gate("P7 callee census diff == exactly #6810", set(dd) <= {6810, nu} and len(dd) >= 1, dd)
    es1 = g.exec_state(T); s.gate("P8 ExecState 1 after the swap", es1 == 1, es1)
    GS = V.build4(W1["terminals"], J("tools/bench/graph_objs_s1_20260923.json")["objects"], L1, LAB, FS)
    for tag, A in (("S1wiki", GS), ("before-live", V.build4(L0["terminals"], L0["objs"], L1, LAB, FS))):
        cd = V.computation_diff(A, V.build4(L1v["terminals"], L1v["objs"], L1, LAB, FS))
        s.fact("CDIFF({0}, after): {1} rows; comp nodes +{2}/-{3}; rows {4}".format(tag, len(cd["rows"]), len(cd["computation_nodes_added"]),
               len(cd["computation_nodes_removed"]), [V.show(x["sink"]) for x in cd["rows"]][:6]))
        s.R["cdiff_" + tag] = len(cd["rows"])
    s.head("[3] 20 swaps back and forth"); cur, errs = nu, []
    for i in range(20):
        r = g.replace_object(T, cur, GB_ORIG if i % 2 == 0 else PROBE)
        errs += [(i, r)] if (r["err_replace"] or r["err"] or r["new_uid"] <= 0) else []
        cur = r["new_uid"] or cur; h.append(bp.labview_handles())
    s.fact("handles over 20 swaps {0}".format(h)); s.R["handles"] = h
    s.gate("P9 20 swaps clean, handle range within +-100", not errs and max(h[1:]) - min(h[1:]) <= 100, {"errs": errs[:3], "range": max(h[1:]) - min(h[1:])})
    c2 = census(d); L2 = WB.read_live(T, fs_pairs=FS)
    s.gate("P10 after the 20: callee == probe and edges == before", os.path.normcase(str(c2.get(cur))) == os.path.normcase(PROBE)
           and edges(L2, {cur: 6810}) == E0, (cur, c2.get(cur)))
    s.R["final_node_uid"] = cur
    s.head("[4] save"); es2 = g.exec_state(T)
    if es2 == 1:
        g.save(T); g.reset(); s.fact("SAVED {0} md5 {1}".format(T, K.md5(T))); s.R["saved"] = {"path": T, "md5": K.md5(T)}
    s.gate("P11 swapped scratch saved by script", es2 == 1 and os.path.exists(T), es2)


try:
    main(s)
except K.Stop as e:
    s.gate("STOP at gate: {0}".format(e), False)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"])); g.reset()  # noqa: E702
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6); s.gate("P1b pins unchanged after", s.pin_check("AFTER"))  # noqa: E702
s.gate("P12 LabVIEW gone at exit", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout)
s.dump(); sys.exit(s.summary())
