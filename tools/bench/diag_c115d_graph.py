r"""diag_c115d_graph - card 115-4 M2/M5: SAVED R1 graph, READ-ONLY on a byte copy (claudeDev\scratch_c115d_r1_<ts>.vi, deleted),
no run/wire/delete/save, LabVIEW killed at the end; OFFLINE vs graph_l2b3_20260928.json. PRIOR ART (copied, no new op):
diag_c114c_b3graph.py (read_live + restart + handle reads + kill). OUT graph_l2r1_20260928.json + diag_c115d_graph.json.
PRED (reported, not gated): the 12 retired SR uids own 0 terminal rows in R1; every wire that had an SR terminal in B3 and
another terminal too keeps its source and all other sinks in R1 (M5); R1 has no source-only / sink-only wire among them.
GATES = measurement integrity only (K0 no LabVIEW before, K1 md5 pins, K2 byte copy, H gone+md5+scratch deleted, HF handles).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c115d_graph.log -- py -u tools/bench/diag_c115d_graph.py"""
import collections, hashlib, json, os, subprocess, shutil, sys, time               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K                      # noqa: E401,E402
R1, R1_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_r1_20260928_055441.vi"), "f465196bb5016638b146e771ba54c5af"
B3, B3_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b3_20260928_032703.vi"), "1b5c12d71ca48f22e3f4b80316c67e51"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c115d_r1_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT, TAB = os.path.join(HERE, "graph_l2r1_20260928.json"), os.path.join(HERE, "diag_c115d_graph.json")
J = lambda p: json.load(open(os.path.join(HERE, p), encoding="utf-8"))            # noqa: E731
BASE = J("graph_l2b3_20260928.json")
SR = [9018, 9025, 29505, 29512, 1147, 1142, 5796, 5805, 119, 2972, 7311, 11001]  # plan_l2r1.json actions (pairs)
STUBS = [9215, 9097, 29591, 28039, 505, 1681, 5859, 6041, 121, 7429, 10763]       # plan_l2r1.json delete_wire rows
gates, T = [], {}
gate = lambda lab, ok, d="": (gates.append((lab, bool(ok))), print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(d)[:900]), flush=True))   # noqa: E731
fact = lambda m: print("  FACT " + str(m)[:1500], flush=True)                     # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                     # noqa: E731


def nets(G):
    n = collections.defaultdict(list)
    for r in G["terminals"]:
        w = int(r["wire_uid"] or 0)
        if w:
            n[w].append((int(r["owner_uid"]), r["owner_class"], int(r["term_uid"]), r["term_name"], bool(r["is_source"])))
    return n


def offline(gr):
    nb, nr = nets(BASE), nets(gr)
    srrows = [r for r in BASE["terminals"] if int(r["owner_uid"]) in SR]
    T["sr_rows_b3"] = [(int(r["owner_uid"]), r["owner_class"], int(r["term_uid"]), r["term_name"], r["is_source"], int(r["wire_uid"] or 0)) for r in srrows]
    T["sr_rows_r1"] = [r for r in gr["terminals"] if int(r["owner_uid"]) in SR]
    fact("SR rows B3 {0}; R1 {1}".format(len(T["sr_rows_b3"]), len(T["sr_rows_r1"])))
    ws = sorted({int(r["wire_uid"] or 0) for r in srrows} - {0})
    T["nets"] = []
    for w in ws:
        b = nb.get(w, []); rr = nr.get(w, [])                                        # noqa: E702
        live_b = [x for x in b if x[0] not in SR]
        srt = [x for x in b if x[0] in SR]
        kind = "stub" if w in STUBS else ("shared" if live_b else "sr-only")
        src_b, src_r = sorted(x[2] for x in live_b if x[4]), sorted(x[2] for x in rr if x[4])
        snk_b, snk_r = sorted(x[2] for x in live_b if not x[4]), sorted(x[2] for x in rr if not x[4])
        eq = (src_b, snk_b) == (src_r, snk_r)
        row = {"wire": w, "kind": kind, "b3": b, "r1": rr, "sr_terms_b3": srt, "src_b3": src_b, "src_r1": src_r, "sinks_b3": snk_b,
               "sinks_r1": snk_r, "m5_equal": eq, "r1_present": w in nr}
        T["nets"].append(row)
        fact("NET w{0} {1}: SR terms {2}; B3 live src {3} sinks {4}; R1 present {5} src {6} sinks {7}; M5 equal {8}".format(
            w, kind, [(x[0], x[3], "src" if x[4] else "snk") for x in srt], src_b, snk_b, w in nr, src_r, snk_r, eq))
    one = lambda n: sorted(w for w, t in n.items() if all(x[4] for x in t) or not any(x[4] for x in t))   # noqa: E731
    T["one_sided_b3"], T["one_sided_r1"] = one(nb), one(nr)
    T["one_sided_new_in_r1"] = sorted(set(T["one_sided_r1"]) - set(T["one_sided_b3"]))
    T["one_sided_gone_in_r1"] = sorted(set(T["one_sided_b3"]) - set(T["one_sided_r1"]))
    fact("one-sided wires (all-source or all-sink) B3 {0} / R1 {1}; new in R1 {2}; gone {3}".format(
        len(T["one_sided_b3"]), len(T["one_sided_r1"]), T["one_sided_new_in_r1"], T["one_sided_gone_in_r1"]))
    wb, wr = set(nb), set(nr)
    T["wires_gone"], T["wires_new"] = sorted(wb - wr), sorted(wr - wb)
    T["nets_changed_other"] = sorted(w for w in wb & wr if sorted(nb[w]) != sorted(nr[w]) and w not in ws)
    fact("wires gone {0}; new {1}; other nets whose terminal list changed {2}".format(T["wires_gone"], T["wires_new"], T["nets_changed_other"]))
    json.dump(T, open(TAB, "w", encoding="utf-8"), default=str, indent=1); fact("WROTE {0} md5 {1}".format(TAB, md5(TAB)))   # noqa: E702


def main():
    gate("K1 R1 md5 == pin; B3 md5 == pin", md5(R1) == R1_MD5 and md5(B3) == B3_MD5, (md5(R1), md5(B3)))
    if sys.argv[1:2] == ["offline"]:
        gr = J(os.path.basename(OUT)); offline(gr); return finish(gr)             # noqa: E702
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or not gates[0][1]:
        return finish(None)
    shutil.copyfile(R1, SCR); gate("K2 scratch is a byte copy", md5(SCR) == R1_MD5, SCR)   # noqa: E702
    gr, h = None, []
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3); h.append(bench_prep.labview_handles())   # noqa: E702
        lv = K.mod("wiki_build").read_live(SCR, fs_pairs=BASE["fs_tunnel_pairs"]); h.append(bench_prep.labview_handles())   # noqa: E702
        n = len(g.report_all(SCR, "Wire")); h.append(bench_prep.labview_handles())                          # noqa: E702
        gr = {"vi": R1, "md5": R1_MD5, "source": "tools/bench/diag_c115d_graph.py (read_live, byte copy)", "terminals": lv["terminals"],
              "objs": lv["objs"], "fs_tunnel_pairs": BASE["fs_tunnel_pairs"], "handles": h, "wire_census": n}
        fact("LIVE {0} terminal rows, {1} objs, Wire census {2}; HANDLES restart {3} -> read {4} -> 2nd census {5}".format(
            len(lv["terminals"]), len(lv["objs"]), n, *h))
        gate("HF handle count flat over the 2nd read (+-100)", h[2] is not None and h[1] is not None and abs(h[2] - h[1]) <= 100, h)
    finally:
        g.reset(); subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        os.path.exists(SCR) and os.remove(SCR)
        gate("H LabVIEW gone; R1 + B3 md5 unchanged; scratch deleted", gone and md5(R1) == R1_MD5 and md5(B3) == B3_MD5 and not os.path.exists(SCR), (gone, md5(R1), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8")); fact("WROTE {0} md5 {1}".format(OUT, md5(OUT))); offline(gr)   # noqa: E702
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok); ff = next((lab for lab, ok in gates if not ok), None)   # noqa: E702
    arts = [{"path": os.path.relpath(p, os.path.dirname(os.path.dirname(HERE))), "md5": md5(p)} for p in (OUT, TAB) if gr and os.path.exists(p)]
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=arts)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__": sys.exit(main())                                       # noqa: E701
