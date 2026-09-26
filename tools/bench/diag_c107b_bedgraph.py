r"""diag_c107b_bedgraph - card 107-2 F1 (PD219(f)(2b)): the L2-A1 BED's graph, READ-ONLY, and cdiff(S1, bed) measured on it.
The bed claudeDev\D1_l2_a1_20260925_235224.vi (md5 51d9b8a3...) has NO graph on disk (the L2-A1 base was D1_k's
sim/l2a1/graph_k_80_owners.json); stagesim needs one as the L2-A2 base and stage_prerun.find_graph needs one by md5.
PRIOR ART (reused, not rebuilt): l2a1_facts_80.py:52-66 (read_live + k_contract_79.mloops + the owner walk) = the routine that
made the L2-A1 base; diag_c101_owners.py (gscript direct, byte copy in claudeDev, kill + delete; no Stage: nothing is edited or
saved, so this is not a stage); stage_d1_l2a1.py:98-104 (frame-keyed cdiff inputs). No new op. No VI is run.
OUTPUT tools/bench/graph_l2a1_bed_<date>.json {vi, md5 = the BED's, terminals, objs, loops, fs_tunnel_pairs, graph_summary, owners}.
PREDICTION: K bed md5 51d9b8a3, byte copy equal; O every live Diagram gets an owner; C cdiff_frame(S1, bed) == the 9 rows that
stage_d1_l2a1_86-5.log:731-739 measured on the same state just before its save (:751 md5 51d9b8a3); T CT #23541 wire partners
== [] (86-5:671); H LabVIEW gone, bed md5 unchanged, scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c107b_bedgraph.log -- py -u tools/bench/diag_c107b_bedgraph.py"""
import hashlib, json, os, shutil, subprocess, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V, jev_candidates as JC  # noqa: E401,E402
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"
SCR = os.path.join(g.CLAUDEDEV, "D1_l2a1_c107b_read_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2a1_bed_{0}.json".format(time.strftime("%Y%m%d")))
BASEK = json.load(open(os.path.join(HERE, "sim", "l2a1", "graph_k_80_owners.json"), encoding="utf-8"))
WANT = sorted([(376, "current frame data array in"), (376, "frame index"), (2626, "array"), (5058, "Image In"),
               (5696, "x,y,z array"), (6085, "x,y,z array"), (9703, "x"), (10382, "x"), (11529, "x")])
GROUP = {"A": {5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541, 10739, 10929, 17272},   # plan §1 + PD181(d)/182(a)(b)
         "B": {1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874}, "C": {10686}, "W": {376}, "K": {5058}}
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


def grp(u):
    return next((k for k, v in GROUP.items() if u in v), "-")


def read():
    lv = K.mod("wiki_build").read_live(SCR, fs_pairs=BASEK["fs_tunnel_pairs"])
    print("  FACT LIVE {0} terminal rows, {1} objs, secs {2}".format(len(lv["terminals"]), len(lv["objs"]), lv["secs"]), flush=True)
    loops = K.mod("k_contract_79").mloops(S(), SCR)
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo, BD = {}, diags + [10757, 23541, 10969, 17272], K.mod("build_d1_v0")
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
    print("  FACT owners #10757 {0} #23541 {1} #10969 {2} #23166 {3} #639 {4}".format(
        O.get(10757), O.get(23541), O.get(10969), O.get(23166), O.get(639)), flush=True)
    return {"vi": BED, "md5": BED_MD5, "source": "tools/bench/diag_c107b_bedgraph.py (read_live + mloops + owner_of, byte copy)",
            "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASEK["fs_tunnel_pairs"],
            "graph_summary": BASEK.get("graph_summary") or {}, "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def offline(gr):
    lab, s1p = JC.node_labels_default(), json.load(open(os.path.join(JC.WIKI, JC.S1_KEY + ".json"), encoding="utf-8"))
    S1f = V.build4(s1p["terminals"], json.load(open(JC._newest("graph_objs_s1_*.json"), encoding="utf-8"))["objects"],
                   json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"], lab, s1p["fs_tunnel_pairs"], frame_keyed=True)
    G1 = V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    for y in cd["rows"]:
        src = [int(str(k).split("|")[0]) for k in (y.get("before") or [])]
        print("  FACT CDIFF ROW group(sink)={0} group(S1 src)={1} {2}".format(grp(int(y["node"])), [grp(int(u)) for u in src],
              dict((k, V.show(v) if k == "sink" else v) for k, v in y.items())), flush=True)
    got = sorted(set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]))
    gate("C cdiff_frame(S1, bed) == the 9 rows of stage_d1_l2a1_86-5.log:731-739", got == WANT,
         {"extra": sorted(set(got) - set(WANT)), "missing": sorted(set(WANT) - set(got))})
    T = gr["terminals"]
    hit = [r for r in T if r["term_uid"] == 23541]
    part = sorted((r["owner_uid"], r["term_uid"], r["term_name"]) for r in T if hit and hit[0]["wire_uid"] and r["wire_uid"] == hit[0]["wire_uid"] and r["term_uid"] != 23541)
    el = [r for r in T if r["owner_uid"] == 10757 and r["term_name"] == "element"]
    print("  FACT #23541 rows {0}; #10757 'element' rows {1}".format(hit, el), flush=True)
    gate("T CT #23541 wire partners on the bed == [] (86-5:671)", len(hit) == 1 and part == [], part)


def main():
    gate("K1 bed md5 == pin", md5(BED) == BED_MD5, md5(BED))
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read (107-1 may run legs)", not running, running)
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
        gate("H LabVIEW gone; bed md5 unchanged; scratch deleted", gone and md5(BED) == BED_MD5 and not os.path.exists(SCR),
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
