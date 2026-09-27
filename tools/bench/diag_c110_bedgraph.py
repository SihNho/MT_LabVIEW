r"""diag_c110_bedgraph - card 110-1 P1+P2 (brief_110-1.md M): the L2-A3 bed's graph + the Property Value targets of #30117/#4580,
READ-ONLY, on a SCRATCH byte copy (claudeDev\scratch_c110_bed_<ts>.vi), no VI run, LabVIEW killed and scratch deleted at the end.
PRIOR ART (copied): tools/bench/diag_c108b_graph.py (read_live + k_contract_79.mloops + owner_of on a byte copy) - only the input, the
pins and the expected rows change; gscript.node_labels (OpNodeLabels_v0, 88/88 on the main VI, docs/camera-acquisition-facts.md:310-314:
an IMPLICIT property node's header IS its linked control's label) for P2. `Property.Linked Control` 636F806 is NOT built (NAMES.md:785),
so the target control is identified by LABEL: the ControlTerminal row(s) of the bed whose term_name == the node's label. No new op.
OUTPUT tools/bench/graph_l2a3_bed_<date>.json {vi, md5, terminals, objs, loops, fs_tunnel_pairs, owners, prop_labels}.
PREDICTION: K md5 14337cfd; K2 byte copy; O every Diagram owned; C cdiff_frame(S1, bed) == plan_l2a3's 6 open_rows (stage_d1_l2a3_c109b.log PB);
P #30117 label 'Trans Pos (mm)', #4580 label 'Rot pos (deg)' (frame-loop-wire-graph.md:78,129 on the original); H LabVIEW gone, input md5
unchanged, scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c110_bedgraph.log -- py -u tools/bench/diag_c110_bedgraph.py"""
import hashlib, json, os, subprocess, shutil, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V, jev_candidates as JC  # noqa: E401,E402
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_a3_20260927_151224.vi"), "14337cfda5780cb39d12deb5fe0d3db9"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c110_bed_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2a3_bed_{0}.json".format(time.strftime("%Y%m%d")))
BASE0 = json.load(open(os.path.join(HERE, "graph_l2a2_20260927.json"), encoding="utf-8"))
PLAN3 = json.load(open(os.path.join(HERE, "plan_l2a3.json"), encoding="utf-8"))
WANT = sorted(set((int(r["node"]), r["term"]) for r in PLAN3["open_rows"]))
PROPS = {30117: "Trans Pos (mm)", 4580: "Rot pos (deg)"}
EXTRA_OWN = [1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874, 403, 9306, 28170, 29091, 47, 9289, 28148, 28996, 8323, 28786,
             8038, 30117, 4580, 10068, 5119, 11608, 29240, 5058, 376, 9018, 9025, 29505, 29512, 637, 10170]
gates = []


class S(object):                                                                   # k_contract_79.mloops needs .safe only
    def safe(self, label, fn, default=None):
        try:
            return fn(), ""
        except Exception as e:                                                     # noqa: BLE001
            print("  FACT {0} raised {1}".format(label, str(e)[:200]), flush=True)
            return default, str(e)


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def prop_labels():
    """node_labels over Traverse 'Diagram' indices until both property uids are seen (or 6 empty+error indices in a row)."""
    got, miss = {}, 0
    for di in range(0, 400):
        rows, err = g.node_labels(SCR, di, strict=False)
        for r in rows:
            if int(r["uid"]) in PROPS:
                got[int(r["uid"])] = (di, r["label"])
        if set(got) == set(PROPS):
            break
        miss = miss + 1 if (not rows and err) else 0
        if miss >= 6:
            break
    print("  FACT PROP LABELS {0}".format(got), flush=True)
    return got


def read():
    lv = K.mod("wiki_build").read_live(SCR, fs_pairs=BASE0["fs_tunnel_pairs"])
    print("  FACT LIVE {0} terminal rows, {1} objs, secs {2}".format(len(lv["terminals"]), len(lv["objs"]), lv["secs"]), flush=True)
    loops = K.mod("k_contract_79").mloops(S(), SCR)
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo, BD = {}, diags + EXTRA_OWN, K.mod("build_d1_v0")
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        try:
            v = BD.owner_of(SCR, u, strict=False)
        except Exception as e:                                                     # noqa: BLE001
            v = ("?", 0); print("  FACT owner_of #{0} raised {1}".format(u, str(e)[:120]), flush=True)   # noqa: E702
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gate("O every live Diagram uid ({0}) has a resolved owner".format(len(diags)), all(O[d][0] != "?" for d in diags),
         sorted(d for d in diags if O[d][0] == "?")[:20])
    print("  FACT owners " + " ".join("#{0} {1}".format(u, O.get(u)) for u in EXTRA_OWN), flush=True)
    pl = prop_labels()
    return {"vi": BED, "md5": BED_MD5, "source": "tools/bench/diag_c110_bedgraph.py (read_live + mloops + owner_of + node_labels, byte copy)",
            "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASE0["fs_tunnel_pairs"],
            "graph_summary": BASE0.get("graph_summary") or {}, "owners": dict((str(k), list(v)) for k, v in sorted(O.items())),
            "prop_labels": dict((str(k), {"diagram_index": v[0], "label": v[1]}) for k, v in pl.items())}


def offline(gr):
    lab, s1p = JC.node_labels_default(), json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
    S1f = V.build4(s1p["terminals"], json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"],
                   json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"], lab, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]:
        print("  FACT CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())), flush=True)
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    gate("C cdiff_frame(S1, L2-A3 bed) == plan_l2a3's {0} open_rows".format(len(WANT)), got == WANT,
         {"extra": sorted(set(got) - set(WANT)), "missing": sorted(set(WANT) - set(got))})
    for u, want in PROPS.items():
        lb = (gr.get("prop_labels") or {}).get(str(u), {}).get("label")
        cts = sorted(set((r["owner_uid"], r["term_uid"]) for r in gr["terminals"] if r.get("term_name") == lb
                         and int(r["term_uid"]) in set(int(o["uid"]) for o in gr["objs"] if o["class"] == "ControlTerminal")))
        gate("P #{0} label == {1!r} (original's); ControlTerminal(s) with that label: {2}".format(u, want, cts), lb == want and len(cts) >= 1, lb)


def main():
    gate("K1 L2-A3 bed md5 == pin", md5(BED) == BED_MD5, md5(BED))
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or md5(BED) != BED_MD5:
        return finish(None)
    shutil.copyfile(BED, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == BED_MD5, SCR)
    gr = None
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        gr = read()
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        try:
            os.remove(SCR)
        except OSError as e:
            print("  FACT scratch not removed: {0}".format(e), flush=True)
        gate("H LabVIEW gone; input md5 unchanged; scratch deleted", gone and md5(BED) == BED_MD5 and not os.path.exists(SCR),
             (gone, md5(BED), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8"))
        print("  FACT WROTE {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
        offline(gr)
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=[{"path": OUT, "md5": md5(OUT)}] if gr and os.path.exists(OUT) else [])), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
