r"""diag_swap_build - card 75-4 part A (m8 plan PD14(d)): build OpReplaceGObj_v0.vi = the subVI callee-swap op.
PRIOR ART (checked first): no Replace op exists (grep 632A402/635E001 in gscript.py, docs/toolkit-capabilities.md: only
docs/vi-server-ids.json:117 records SubVI.Replace UNVERIFIED). Donor = OpOwnerChain_v1.vi (built+tested:
tools/recipes/build_opownerchain_v1.py) - it already holds `vi path` -> Open VI Reference -> `UID to GObject Reference.vi`
(#990, source `GObject`) with `UID 2` as the uid input. Added by existing verbs only: build_invoke (GObject.Replace
632A402, docs/vi-server-ids.json route), connect_terminals (OpConnect_v0, no junk Invoke), create_control/_indicator,
build_property (GObject.UID 632A813), copy_by_index (Close Reference #157 from KernelBuilder_v1.vi, docs/REFERENCES.md:159).
PREDICTION: B1 donor copy ES 1; B2 exactly one new Invoke whose terminals include a Path sink; B3 its `reference` reads the
#990 GObject wire; B4 a Path control + indicators (new UID, Replace error out) are created; B5 ES 1 -> scripted save; B6
Close Reference copied (uid guard 157) with its `reference` fed by the UID property's `reference out`, ES 1 after; B7 cold
ES 1 in a fresh LabVIEW; labels JSON written. No target VI is edited here; nothing is run except op VIs.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/swap_verb_75_build.log -- py -u tools/bench/diag_swap_build.py"""
import os, sys, json, shutil                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                 # noqa: E402
g = K.g
DONOR = os.path.join(K.CLAUDEDEV, "OpOwnerChain_v1.vi"); KB = os.path.join(K.CLAUDEDEV, "KernelBuilder_v1.vi")
OP = os.path.join(K.CLAUDEDEV, "OpReplaceGObj_v0.vi")
LAB = os.path.join(K.BENCH, "swap_verb_75_oplabels.json")
s = K.Stage(DONOR, None, "swap_verb_75_build", fresh=False, preload=False, deadline_min=22, pins=(),
            out_json=os.path.join(K.BENCH, "swap_verb_75_build.json"), task="75-4")


def sweep(t=OP):
    out = {}
    for n in range(60):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def term(by, uid, name=None, src=None, pick=None):
    for r in by[uid][1]:
        if (name is None or r["name"] == name) and (src is None or r["is_source"] == src) and (pick is None or pick(r)):
            return r
    return None


def main(s):
    s.head("[0] restart + donor copy"); s.restart()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copy2(DONOR, OP)
    s.gate("B1 donor copy ExecState 1", g.exec_state(OP) == 1, "", fatal=True)
    fp0 = [l for _i, l, _ind in g.fp_labels(OP)]
    by = sweep(); u2g = [u for u in by if term(by, u, "GObject", True)]
    s.fact("donor nodes {0}; U2G candidates {1}".format(sorted(by), u2g))
    s.gate("B0 exactly one node with a `GObject` source (UID to GObject Reference)", len(u2g) == 1, u2g, fatal=True)
    u2g = u2g[0]
    s.head("[1] Invoke GObject.Replace 632A402")
    new = g.build_invoke(OP, "VI Server:GObject", "632A402", (1500, 40))
    rep = int(new[0]["uid"]); by = sweep()
    s.fact("Replace node #{0} terminals {1}".format(rep, [(r["i"], r["name"], r["is_source"]) for r in by[rep][1]]))
    p = term(by, rep, src=False, pick=lambda r: "path" in r["name"].lower())
    s.gate("B2 the Replace node has a Path sink", p is not None, "", fatal=True)
    ref = term(by, rep, "reference", False)
    out = term(by, rep, src=True, pick=lambda r: r["name"] not in ("reference out", "error out") and r["name"])
    s.fact("Replace: reference sink {0}, path sink {1}, return source {2}".format(ref and ref["i"], p["i"], out and out["name"]))
    g.connect_terminals(OP, by[rep][0], ref["i"], by[u2g][0], term(by, u2g, "GObject", True)["i"])
    by = sweep()
    s.gate("B3 Replace.reference reads the #990 GObject wire", term(by, rep, "reference", False)["wire"] ==
           term(by, u2g, "GObject", True)["wire"] != 0, (term(by, rep, "reference", False)["wire"]))
    s.head("[2] Path control, UID property on the returned ref, indicators")
    _c, plab = g.create_control(OP, by[rep][0], p["i"]); s.fact("Path control label {0!r}".format(plab))
    pn = int(g.build_property(OP, "VI Server:GObject", [("632A813", False)], (1750, 40))[0]["uid"]); by = sweep()
    s.fact("UID property #{0} terminals {1}".format(pn, [(r["i"], r["name"], r["is_source"]) for r in by[pn][1]]))
    out = term(by, rep, out["name"], True)
    g.connect_terminals(OP, by[pn][0], term(by, pn, "reference", False)["i"], by[rep][0], out["i"])
    added = [plab]
    for node, pick in ((pn, lambda r: r["name"] not in ("reference out", "error out")), (rep, lambda r: r["name"] == "error out"),
                       (pn, lambda r: r["name"] == "error out")):
        by = sweep(); seen = set(l for _i, l, _ind in g.fp_labels(OP))
        g.create_indicator(OP, by[node][0], term(by, node, src=True, pick=pick)["i"])
        added += [l for _i, l, _ind in g.fp_labels(OP) if l not in seen][:1] or [None]
    s.fact("front-panel labels added [path, new uid, replace err, uid err] = {0}".format(added))
    s.gate("B4 one control + three indicators added", None not in added and len(set(added)) == 4, added)
    es = g.exec_state(OP); s.gate("B5 ExecState 1 before the save", es == 1, es, fatal=True)
    g.save(OP); pn_by = sweep()
    s.head("[3] Close Reference from KernelBuilder_v1 #157 (copy_by_index), fed by UID property `reference out`")
    s.restart()
    idx = next((i, c) for c in ("Node", "Function") for i, o in enumerate(g.report(KB, c)) if int(o["uid"]) == 157)
    s.fact("KB #157 = {0}[{1}]".format(idx[1], idx[0])); g.reset(); s.restart()

    def finish(dst, added_objs):
        b = sweep(dst); cr = [u for u in b if u in set(int(o["uid"]) for o in added_objs)]
        s.fact("finish: new nodes on target {0}".format(cr))
        g.connect_terminals(dst, b[cr[0]][0], term(b, cr[0], "reference", False)["i"], b[pn][0],
                            term(b, pn, "reference out", True)["i"])
        s.fact("finish: close ref reference wire {0}, ES {1}".format(term(sweep(dst), cr[0], "reference", False)["wire"],
                                                                      g.exec_state(dst)))
    add, sel = g.copy_by_index(KB, idx[1], idx[0], OP, expect_uid=157, finish=finish)
    s.gate("B6 Close Reference copied into the op (uid guard 157)", sel == 157, (sel, len(add)))
    s.head("[4] cold re-read"); s.restart()
    es2 = g.exec_state(OP); s.gate("B7 ExecState 1 COLD in a fresh LabVIEW", es2 == 1, es2)
    fp2 = g.fp_labels(OP); by = sweep()
    s.fact("final nodes {0}; fp {1}".format(sorted(by), fp2))
    lab = {"vi_path": "vi path", "uid_in": "UID 2", "path": plab, "new_uid": added[1], "err_replace": added[2],
           "err_uid": added[3], "class_name": "Class Name", "index": "index", "replace_node": rep, "uid_prop_node": pn}
    json.dump(lab, open(LAB, "w", encoding="utf-8"), indent=1); s.fact("labels {0}".format(lab))
    s.R["op"] = {"path": OP, "md5": K.md5(OP), "labels": lab, "fp_final": fp2, "nodes_before_close": sorted(pn_by)}


try:
    main(s)
except K.Stop as e:
    s.gate("STOP at gate: {0}".format(e), False)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"])); g.reset()  # noqa: E702
import subprocess, time                                                              # noqa: E401,E402
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6); s.fact("LabVIEW gone at exit: {0}".format("LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout))  # noqa: E702
s.dump(); sys.exit(s.summary())
