r"""diag_c108b_graph - card 108-2 F1 (PD221(d)): the L2-A2 file's graph, READ-ONLY, and cdiff(S1, L2-A2) measured on it.
The L2-A2 artefact claudeDev\D1_l2_a2_20260927_132125.vi (md5 807c803e...) has NO graph on disk; stagesim needs one as the L2-A3
base and stage_prerun.find_graph needs one by md5.
PRIOR ART (copied, not rebuilt): tools/bench/diag_c107b_bedgraph.py (card 107-2) - read_live + k_contract_79.mloops + owner_of on a
byte copy in claudeDev, kill + delete; same routine, only the input, the pins and the expected rows change. No new op. No VI is run.
OUTPUT tools/bench/graph_l2a2_<date>.json {vi, md5 = the L2-A2 file's, terminals, objs, loops, fs_tunnel_pairs, graph_summary, owners}.
PREDICTION: K md5 807c803e, byte copy equal; O every live Diagram gets an owner; C cdiff_frame(S1, L2-A2) == the 8 rows of
stage_d1_l2a2.log:58-66 (9703 closed); T CT #23541 wire partners == [#10757 t10874 'element'] (stage_d1_l2a2.log:53); H LabVIEW
gone, input md5 unchanged, scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c108b_graph.log -- py -u tools/bench/diag_c108b_graph.py"""
import hashlib, json, os, subprocess, shutil, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V, jev_candidates as JC  # noqa: E401,E402
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_a2_20260927_132125.vi"), "807c803e1cef1dc33cfdc936c87af1ca"
SCR = os.path.join(g.CLAUDEDEV, "D1_l2a2_c108b_read_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2a2_{0}.json".format(time.strftime("%Y%m%d")))
BASE0 = json.load(open(os.path.join(HERE, "graph_l2a1_bed_20260927.json"), encoding="utf-8"))
WANT = sorted([(376, "current frame data array in"), (376, "frame index"), (2626, "array"), (5058, "Image In"),
               (5696, "x,y,z array"), (6085, "x,y,z array"), (10382, "x"), (11529, "x")])
EXTRA_OWN = [10757, 23541, 10969, 17272, 10382, 11529, 10886, 9647, 10445, 23523, 10978, 9703]
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
    return {"vi": BED, "md5": BED_MD5, "source": "tools/bench/diag_c108b_graph.py (read_live + mloops + owner_of, byte copy)",
            "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASE0["fs_tunnel_pairs"],
            "graph_summary": BASE0.get("graph_summary") or {}, "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def offline(gr):
    lab, s1p = JC.node_labels_default(), json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
    S1f = V.build4(s1p["terminals"], json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"],
                   json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"], lab, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]:
        print("  FACT CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())), flush=True)
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    gate("C cdiff_frame(S1, L2-A2) == the 8 rows of stage_d1_l2a2.log:58-66", got == WANT,
         {"extra": sorted(set(got) - set(WANT)), "missing": sorted(set(WANT) - set(got))})
    T = gr["terminals"]
    hit = [r for r in T if r["term_uid"] == 23541]
    part = sorted((r["owner_uid"], r["term_uid"], r["term_name"]) for r in T if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != 23541)
    gate("T CT #23541 wire partners == [#10757 t10874 'element'] (stage_d1_l2a2.log:53)", len(hit) == 1 and part == [(10757, 10874, "element")], part)


def main():
    gate("K1 L2-A2 md5 == pin", md5(BED) == BED_MD5, md5(BED))
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
