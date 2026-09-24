r"""cdiff_blindspot_74 - card 74-2 (Pre-decided 176(c)). PURE PYTHON, no LabVIEW: existing on-disk tables only.
OLD = tools/vigraph.py at git HEAD (loaded from `git show` into %TEMP%, the dedupe_check_s2b.py pattern); NEW = the working
file with DIAG_TERM (a Diagram-owned `Terminal` SOURCE row is its own computation node).
BEDS (graph built as the stage recipes' `lg` builds it, from files instead of read_live):
  S3  D1_s3_loop15      tools/bench/graph_s3_loop15_20260924.json (terminals + objs), loops graph_loops_m4b, fs faces rowD wiki
  S4  D1_s4_loop17      tools/bench/opmodels/bed_s4_loop17.json (terms + objs, read of a scratch of md5 4b621946...), loops
                        m4b with #23041 overridden from stage_d1_l7_1a.json sr (stage_d1_l7_r.py:16-21), fs faces rowD wiki
  A7  D1_l7_1a_035656   tools/bench/opmodels/bed_l7_1a.json (extra; the L7-1a artefact, NOT the L7-1b file the card names)
  L71 D1_l7_1_20260924_060431 - NO terminal table on disk (grep: only errorlist/stage logs mention it) -> reported BLOCKED.
PREDICTION: C0 cdiff(S1,S1) empty (old and new); C1 OLD cdiff(S1,S4) == [w4517 row] (reproduces the live L7-R PB, so the
offline S4 graph is faithful); C2 NEW cdiff(S1,S4) == [w4517, w3268] rows; S3 / A7 rows LISTED (new rows are facts).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/cdiff_blindspot_74.log -- py -u tools/bench/cdiff_blindspot_74.py"""
import copy, importlib.util, json, os, subprocess, sys, tempfile, time             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as VN, jev_candidates as JC, protocol as P                          # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))            # noqa: E731
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)  # noqa: E702


def fact(s):
    print("  FACT  " + s, flush=True)


src = subprocess.run(["git", "show", "HEAD:tools/vigraph.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
p = os.path.join(tempfile.gettempdir(), "vigraph_old_74.py"); open(p, "w", encoding="utf-8").write(src)  # noqa: E702
spec = importlib.util.spec_from_file_location("vigraph_old74", p); VO = importlib.util.module_from_spec(spec); spec.loader.exec_module(VO)  # noqa: E702
gate("V0 OLD has no DIAG_TERM, NEW has it", not hasattr(VO, "DIAG_TERM") and hasattr(VN, "DIAG_TERM"))
t0 = time.time()
LAB = JC.node_labels_default()
W1, WB = J("docs/wiki/subvi/D1_s1_copy.json"), J("docs/wiki/subvi/{0}.json".format(JC.BED_KEY))
O1, L1 = J("tools/bench/graph_objs_s1_20260923.json")["objects"], J("tools/bench/graph_loops_s1_20260924.json")["loops"]
LM = J("tools/bench/graph_loops_m4b_20260924.json")["loops"]
SR = J("tools/bench/stage_d1_l7_1a.json")["l7_1a"]["sr"]
L17 = copy.deepcopy(LM)
for L in (x for x in L17 if x["loop_uid"] == 23041):
    L["right_uids"], L["left_of"] = max((v["rights"] for v in SR.values()), key=len), dict((str(v["right"]), [v["left"]]) for v in SR.values())
S3, S4, A7 = J("tools/bench/graph_s3_loop15_20260924.json"), J("tools/bench/opmodels/bed_s4_loop17.json"), J("tools/bench/opmodels/bed_l7_1a.json")
fact("inputs: S3 {0} md5 {1}; S4 dump {2} (of D1_s4_loop17.vi, opmodels_read_bed.json pin 4b621946...); A7 {3} md5 {4}".format(
    os.path.basename(S3["vi"]), S3["md5"], S4["file"], A7["file"], A7["md5"]))
fact("S4 terms carry frame_diagram: {0}; term_class: {1} (build4 joins leaf class from objs)".format(
    "frame_diagram" in S4["terms"][0], "term_class" in S4["terms"][0]))
ARGS = {"S1": (W1["terminals"], O1, L1, LAB, W1["fs_tunnel_pairs"]),
        "S3": (S3["terminals"], S3["objs"], LM, LAB, WB["fs_tunnel_pairs"]),
        "S4": (S4["terms"], S4["objs"], L17, LAB, WB["fs_tunnel_pairs"]),
        "A7": (A7["terms"], A7["objs"], L17, LAB, WB["fs_tunnel_pairs"])}
G = dict((k, (VO.build4(*a), VN.build4(*a))) for k, a in ARGS.items())
for k, (go, gn) in G.items():
    fact("{0}: nodes old/new {1}/{2}; diag_term_sources {3}; flags {4}; sr {5}".format(
        k, len(go["cls"]), len(gn["cls"]), gn["method"]["diag_term_sources"], len(gn["flags"]),
        {x: gn["method"]["sr"][x] for x in ("paired", "paired_machine", "paired_top")} | {"unpaired": len(gn["method"]["sr"]["unpaired"])}))


def rows(V, a, b):
    cd = V.computation_diff(a, b)
    out = []
    for r in cd["rows"]:
        n, _c, name, _o = V.key_parts(r["sink"])
        out.append({"node": n, "sink": name, "S1_wire": a["rows"][r["sink"]]["wire_uid"] if r["sink"] in a["rows"] else None,
                    "before": [V.show(x) for x in (r["before"] or [])][:4], "after": None if r["after"] is None else [V.show(x) for x in r["after"]][:4]})
    return out, cd


RES = {}
for k in ("S1", "S3", "S4", "A7"):
    for tag, V, i in (("OLD", VO, 0), ("NEW", VN, 1)):
        rr, cd = rows(V, G["S1"][i], G[k][i])
        RES[(k, tag)] = rr
        fact("CDIFF {0}(S1,{1}): {2} rows; computation nodes +{3} / -{4}".format(tag, k, len(rr), len(cd["computation_nodes_added"]), len(cd["computation_nodes_removed"])))
        for r in rr:
            fact("   {0} ROW #{1} {2!r} (S1 wire w{3}) before {4} after {5}".format(tag, r["node"], r["sink"], r["S1_wire"], r["before"], r["after"]))
sig = lambda k, t: sorted((r["node"], r["sink"], r["S1_wire"]) for r in RES[(k, t)])  # noqa: E731
gate("C0 cdiff(S1,S1) empty, OLD and NEW", not RES[("S1", "OLD")] and not RES[("S1", "NEW")], (sig("S1", "OLD"), sig("S1", "NEW")))
gate("C1 OLD cdiff(S1,S4) == exactly the w4517 row (reproduces live L7-R PB, stage_d1_l7_r_r2.log:451)",
     sig("S4", "OLD") == [(376, "current frame data array in", 4517)], sig("S4", "OLD"))
gate("C2 NEW cdiff(S1,S4) == exactly two rows: w4517 and w3268",
     sig("S4", "NEW") == [(376, "current frame data array in", 4517), (376, "frame index", 3268)], sig("S4", "NEW"))
for k in ("S3", "A7"):
    fact("DELTA {0}: rows only in NEW {1}; only in OLD {2}".format(k, sorted(set(sig(k, "NEW")) - set(sig(k, "OLD"))), sorted(set(sig(k, "OLD")) - set(sig(k, "NEW")))))
# D: diag_vigraph_check G8's diff(S1, rowD bed) edge counts moved (16/43 -> 16/40): which edges, by TERMINAL UID
OB, LB = J("tools/bench/graph_objs_bed_20260923.json")["objects"], J("tools/bench/graph_loops_bed_20260924.json")["loops"]
BD = (WB["terminals"], OB, LB, LAB, WB["fs_tunnel_pairs"])
tu = lambda G, k: (G["rows"][k]["term_uid"], G["rows"][k]["owner_class"], G["rows"][k]["term_name"])  # noqa: E731
for tag, V, i in (("OLD", VO, 0), ("NEW", VN, 1)):
    A, Bg = G["S1"][i], V.build4(*BD)
    d = V.diff(A, Bg)
    G[("bed", tag)] = (A, Bg, d)
    fact("DIFF {0}(S1,rowD bed) counts {1}".format(tag, d["counts"]))


def by_uid(tag):
    A, Bg, d = G[("bed", tag)]
    return (set((e[0], tu(A, e[1]), tu(A, e[2])) for e in d["edges_removed"]),
            set((e[0], tu(Bg, e[1]), tu(Bg, e[2])) for e in d["edges_added"]))


(ro, ao), (rn, an) = by_uid("OLD"), by_uid("NEW")
for lab, s in (("removed only OLD", ro - rn), ("removed only NEW", rn - ro), ("added only OLD", ao - an), ("added only NEW", an - ao)):
    fact("DIFF-DELTA {0}: {1} {2}".format(lab, len(s), sorted(s)[:8]))
fact("L71 D1_l7_1_20260924_060431: NOT MEASURED - no terminal table on disk (needs a fresh LabVIEW read; card rule 'no LabVIEW')")
fact("elapsed {0:.1f}s".format(time.time() - t0))
nf = sum(1 for _l, ok in GATES if not ok)
print(P.result_line(P.make_result(len(GATES) - nf, nf, next((l for l, ok in GATES if not ok), None))), flush=True)
sys.exit(1 if nf else 0)
