r"""STEP 4b gate - the full graph, offline. NO LabVIEW: it reads what step 4a left on disk.

PASS ROWS (docs/connectivity-map-plan.md step 4, verbatim from the brief)
  G1  diff(S1, S1) == empty, and S1 IS the ORIGINAL's bytes (md5 equality, not a claim)
  G2  diff(S1, bed) == the 11 severed wires + the delivered M3/S2/S3 rows, classified, nothing else
  G3  reach()/sources_of() answer the 4 known endpoints
  G4  computation_diff(S1, bed) under ASSUMPTION A: empty, or every row printed verbatim
  G5  one path through a LOOP TUNNEL and one through a SHIFT REGISTER on the frame loop reproduce
      two functional units named in docs/frame-loop-wire-graph.md
  G6  graph build + diff on the bed < 5 s

    py tools/bench/diag_vigraph_check.py            (offline; writes tools/bench/graph_*.json)
"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import vigraph as V                                                                # noqa: E402

DATE = time.strftime("%Y%m%d")
WIKI = os.path.join(ROOT, "docs", "wiki", "subvi")
S1K, BEDK = "D1_s1_copy", "D1_s3b_m3a3b_rowD_20260922_161040"
SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
ENDPOINTS = [(1731, "src", 4344, "LeftShiftRegister"), (3947, "src", 4274, "LeftShiftRegister"),
             (9635, "src", 9641, "LoopTunnel"), (7337, "sink", 4334, "RightShiftRegister")]
KERNEL, KERNEL_IN = 5058, "cross size"          # frame-loop unit "the tracking kernel call (#5058)"
SR_R_VISA, SR_L_VISA, ASI = 4334, 4344, 48      # state carrier 2 `VISA out` -> ASI_adjust focus-subvi
N = {"pass": 0, "fail": 0}


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    print("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label,
                                 (" | " + str(detail)[:400]) if detail else ""), flush=True)


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def newest(pattern):
    """The newest dated census (was: today's date only, which broke the check on every later day)."""
    return sorted(glob.glob(os.path.join(HERE, pattern)))[-1]


def g10_equal_top():
    """G10 (cycle 68): two LEFT registers at EQUAL TOP in one loop body - the M4b shape (#23796 / #23880 both at
    TOP 2826). Synthetic, no LabVIEW. Equal-TOP alone must leave both rights UNPAIRED; the machine table
    `left_of` must pair them exactly as given, CROSSED against list order, so position cannot be what paired them."""
    def reg(uid, cls, inner_src):
        return [{"term_uid": uid + 1, "owner_uid": uid, "owner_class": cls, "term_class": "InnerTerminal",
                 "term_name": "", "wire_uid": 0, "is_source": inner_src, "frame_diagram": 9},
                {"term_uid": uid + 2, "owner_uid": uid, "owner_class": cls, "term_class": "OuterTerminal",
                 "term_name": "", "wire_uid": 0, "is_source": not inner_src, "frame_diagram": 8}]
    terms = reg(100, V.SR_R, False) + reg(200, V.SR_R, False) + reg(110, V.SR_L, True) + reg(210, V.SR_L, True)
    objs = [{"uid": u, "class": c, "pos": [x, 50]} for u, c, x in
            ((100, V.SR_R, 900), (200, V.SR_R, 900), (110, V.SR_L, 10), (210, V.SR_L, 10))]
    base = [{"loop_uid": 1, "right_uids": [100, 200]}]
    H = V.build4(terms, objs, base)
    M = V.build4(terms, objs, [dict(base[0], left_of={"100": [210], "200": [110]})])
    sr = lambda G: sorted((V.key_parts(a)[0], V.key_parts(b)[0]) for k, a, b, _i in G["edges"] if k == "sr")
    gate("G10a equal TOP, no machine table: both rights UNPAIRED (heuristic refuses to guess)",
         sr(H) == [] and len(H["method"]["sr"]["unpaired"]) == 2, (sr(H), H["method"]["sr"]["unpaired"]))
    gate("G10b equal TOP + machine left_of: pairs exactly 100->210, 200->110 (crossed), paired_machine 2, top 0",
         sr(M) == [(100, 210), (200, 110)] and M["method"]["sr"]["paired_machine"] == 2 and
         M["method"]["sr"]["paired_top"] == 0 and not M["method"]["sr"]["unpaired"],
         (sr(M), {k: M["method"]["sr"][k] for k in ("paired_machine", "paired_top", "unpaired")}))


def g12_diag_term(rec_s1, A):
    """G12 (card 74-2, Pre-decided 176(c)): a Diagram-owned `Terminal` SOURCE (loop `i`) is its own computation node.
    a) every such wired S1 wiki row is the source of a wire edge from node == its term_uid;
    b) S1 #376 'frame index' (w3268) resolves to exactly term #644 (diagram #639's `i`);
    c) synthetic: removing a diagram-terminal -> function wire makes computation_diff report that sink."""
    rows = [r for r in rec_s1["terminals"] if r["owner_class"] in V.DIAGRAM_OWNER]
    census = {}
    for r in rows:
        k = (r["owner_class"], r.get("term_class"), bool(r["is_source"]), bool(r["wire_uid"]))
        census[k] = census.get(k, 0) + 1
    fact("G12 S1 diagram-owned rows by (owner, term_class, source, wired): {0}".format(sorted(census.items())))
    want = set(r["term_uid"] for r in rows if V._is_diag_source(r) and r["wire_uid"])
    got = set(V.key_parts(a)[0] for k, a, _b, _i in A["edges"] if k == "wire" and A["cls"].get(V.key_parts(a)[0]) == V.DIAG_TERM)
    gate("G12a every wired diagram-owned Terminal SOURCE row (S1: {0}) is a wire-edge source node".format(len(want)),
         bool(want) and want == got, {"missing": sorted(want - got)[:10], "extra": sorted(got - want)[:10]})
    ks = V.terminals(A, node=376, name="frame index", is_source=False)
    eff = sorted(V.effective_sources(A, ks[0])) if ks else []
    gate("G12b S1 #376 'frame index' effective source == term #644 (DiagramTerminal)",
         [V.key_parts(x)[0] for x in eff] == [644] and A["cls"].get(644) == V.DIAG_TERM, [V.show(x) for x in eff])
    t = [{"term_uid": 7, "owner_uid": 5, "owner_class": "Diagram", "term_class": "Terminal", "term_name": "",
          "wire_uid": 90, "is_source": True, "frame_diagram": 5},
         {"term_uid": 21, "owner_uid": 20, "owner_class": "Function", "term_class": "ParameterTerminal", "term_name": "x",
          "wire_uid": 90, "is_source": False, "frame_diagram": 5}]
    tb = [t[0], dict(t[1], wire_uid=0)]
    cd = V.computation_diff(V.build4(t), V.build4(tb))
    gate("G12c synthetic: dropping diagram-terminal #7 -> #20 'x' gives exactly one cdiff row (before [#7], after [])",
         [(V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2], [V.key_parts(x)[0] for x in r["before"]], r["after"])
          for r in cd["rows"]] == [(20, "x", [7], [])], cd["rows"])


def load(key):
    rec = json.load(open(os.path.join(WIKI, key + ".json"), encoding="utf-8"))
    tag = "s1" if key == S1K else "bed"
    objs = json.load(open(newest("graph_objs_{0}_*.json".format(tag)), encoding="utf-8"))["objects"]
    lp = newest("graph_loops_{0}_*.json".format(tag))
    loops = json.load(open(lp, encoding="utf-8"))["loops"]
    fact("{0}: loop table {1} (machine left_of on {2} loop(s))".format(
        tag, os.path.basename(lp), sum(1 for L in loops if L.get("left_of"))))
    # node labels (OpNodeLabels_v0, read off the main VI): {diagram index: [{uid, label}]}. ASSUMPTION A
    # needs them only to spot Wait/timing primitives, whose CLASS is the generic `Function`.
    labels = {}
    p = os.path.join(HERE, "main_vi_node_labels.json")
    if os.path.exists(p):
        for _d, rows in json.load(open(p, encoding="utf-8")).get("diagrams", {}).items():
            for x in rows:
                labels[int(x["uid"])] = x.get("label", "")
    HEUR[key] = V.build4(rec["terminals"], objs, loops, labels)          # the fallback, for contrast
    return rec, V.build4(rec["terminals"], objs, loops, labels, rec.get("fs_tunnel_pairs"))


HEUR = {}
# STEP 4b sequence-crossing cases, found in the S1 wiki + tools/bench/diag_fstunnel_pairs.json and checked
# there by hand (face uids from the machine read, wire ends from the wiki's terminal rows):
#   R1 `VISA out`: source of w34418 (outside) -> FSOT #34409 -> FSIT #13215 -> #14818 -> #15027 -> #19673
#      -> the sinks of w20087 (4 frame crossings after the outer border)
#   R2 `refnum out`: source of w59107 -> FSOT #59098 -> FSOT #59090 (a NESTED flat sequence) -> FSIT
#      #59069 -> #59041 -> the sinks of w7255
REACH_CASES = (("R1 VISA out, FSOT + 4 FSIT", 34418, 20087), ("R2 refnum out, 2 nested FSOT + 2 FSIT", 59107, 7255))
# the step-4 diff counts this change must not move (tools/bench/vigraph_check.log, 2026-09-23 08:2x)
# RE-BASELINED 2026-09-25 (card 74-5) 15/42/9 -> 15/39/9: vigraph.dedupe_rows (2026-09-24) collapsed 3
# double-counted sink rows; measured VA/VB/VC in tools/bench/vigraph_g8_edges_74.log:95-98,162-165, accepted in
# archive/peer/2026-09-25-c74-vigraph-g8-keying.md "What was done with it".
DIFF_BEFORE = {"edges_removed": 15, "edges_added": 39, "changed_sinks": 9}


def dump(name, payload):
    if "--no-dump" in sys.argv:                  # card 74-2: offline gate re-run without writing graph_*.json
        return
    p = os.path.join(HERE, "{0}_{1}.json".format(name, DATE))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    fact("wrote {0} ({1:.1f} KB)".format(os.path.basename(p), os.path.getsize(p) / 1024.0))


def main():
    t0 = time.time()
    rec_s1, A = load(S1K)
    t_s1 = time.time() - t0
    t1 = time.time()
    rec_bed, B = load(BEDK)
    t_bed = time.time() - t1
    for tag, G, rec, t in (("s1", A, rec_s1, t_s1), ("bed", B, rec_bed, t_bed)):
        fact("{0}: {1} nodes, {2} terminals, {3} edges ({4} wire, {5} thru, {6} sr, {7} fs) in {8:.2f}s"
             .format(tag, len(G["cls"]), G["n_terminals"], len(G["edges"]), G["method"]["wire_edges"],
                     G["method"]["thru_edges"], sum(1 for e in G["edges"] if e[0] == "sr"),
                     sum(1 for e in G["edges"] if e[0] == "fs"), t))
        fact("{0}: sr {1}".format(tag, json.dumps(G["method"]["sr"])[:300]))
        fact("{0}: fs {1}".format(tag, json.dumps(G["method"]["fs_tunnel"])[:250]))
        dump("graph_" + tag, {"vi": rec["file"], "md5": rec["md5"], "method": G["method"],
                              "cls": dict((str(k), v) for k, v in G["cls"].items()),
                              "flags": G["flags"],
                              "edges": [[k, a, b] for k, a, b, _i in G["edges"] if k != "thru"],
                              "note": "thru edges are DERIVED from the terminal list, not stored"})
    gate("G0 both graphs carry the 7th column",
         all("frame_diagram" in r for r in (rec_bed["terminals"][0], rec_s1["terminals"][0])),
         "frame_diagram present")

    t2 = time.time()
    self_d = V.diff(A, A)
    d = V.diff(A, B)
    t_diff = time.time() - t2
    gate("G1a diff(S1, S1) is empty", not any(self_d["counts"].values()), self_d["counts"])
    orig = json.load(open(newest("graph_objs_s1_*.json"), encoding="utf-8"))
    gate("G1b S1 wiki md5 == the census's md5 of the same file", rec_s1["md5"] == orig["md5"],
         rec_s1["md5"])
    dump("graph_diff_s1_bed", d)
    dump("graph_diff_s1_s1", self_d)

    half_b = set(d["half_wires_only_in_b"])
    gate("G2a the 11 severed wires are exactly the bed's new half/termless wires",
         half_b == set(w for w in SEVERED if w in half_b) and len(half_b) <= len(SEVERED),
         "bed-only half wires {0}".format(sorted(half_b)))
    lost = [w for w in SEVERED if w not in half_b]
    fact("G2b severed wires with no half-wire row in the bed (termless: no terminal at all): {0}"
         .format(lost))
    fact("G2c removed edges {0}, added {1}, changed sinks {2}".format(
        d["counts"]["edges_removed"], d["counts"]["edges_added"], d["counts"]["changed_sinks"]))
    for tag, rows in (("REMOVED", d["edges_removed"]), ("ADDED", d["edges_added"])):
        for e in sorted(set(tuple(x) for x in rows))[:45]:
            fact("  {0} [{1}] {2} -> {3}".format(tag, e[0], V.show(e[1]), V.show(e[2])))
    cnt = {}
    for n in d["nodes_added"]:
        cnt[B["cls"][n]] = cnt.get(B["cls"][n], 0) + 1
    fact("G2d nodes added by class {0}; removed {1}".format(sorted(cnt.items()), d["nodes_removed"]))
    for w in SEVERED:                       # the 11, each accounted for on BOTH sides
        fact("G2g w{0}: S1 {1} | bed {2}".format(
            w, [V.show(k) for k in V.wire_terminals(A, w)] or "no terminal",
            [V.show(k) for k in V.wire_terminals(B, w)] or "no terminal"))
    lab = [n for n in B["cls"] if B["cls"][n] not in V.SCHED_OWNER and V.is_scheduling(B, n)]
    fact("G2f ASSUMPTION A: {0} node(s) called scheduling by LABEL only: {1}".format(
        len(lab), [(n, B["labels"].get(n)) for n in lab][:8]))

    ok3 = []
    for wire, side, uid, cls in ENDPOINTS:
        ks = V.wire_terminals(B, wire)
        got = [k for k in ks if B["rows"][k]["is_source"] == (side == "src")]
        hit = [k for k in got if V.key_parts(k)[0] == uid and B["cls"].get(uid) == cls]
        ok3.append(bool(hit))
        fact("G3 w{0} {1}: {2}".format(wire, side, [V.show(k) for k in got] or "none"))
    gate("G3 all 4 known endpoints answered", all(ok3), "{0}/4".format(sum(ok3)))

    t3 = time.time()
    cd = V.computation_diff(A, B)
    fact("computation_diff in {0:.2f}s".format(time.time() - t3))
    dump("graph_computation_diff_s1_bed", cd)
    gate("G4 computation_diff(S1, bed) under ASSUMPTION A", not cd["rows"],
         "{0} rows, +{1} / -{2} computation nodes".format(
             len(cd["rows"]), len(cd["computation_nodes_added"]), len(cd["computation_nodes_removed"])))
    for r in cd["rows"][:40]:
        fact("  CDIFF #{0} {1} sink {2} before {3} after {4}".format(
            r["node"], r["class"], V.show(r["sink"]),
            [V.show(x) for x in (r["before"] or [])][:3], [V.show(x) for x in (r["after"] or [])][:3]))

    ks = V.terminals(A, node=ASI, name="VISA resource name", is_source=False)
    direct = sorted(V.sources_of(A, ks, kinds=("wire",))) if ks else []
    p = V.path(A, SR_R_VISA, ks[0]) if ks else []
    gate("G5a shift-register path: right #4334 -> left #4344 -> ASI subVI #48 (`VISA out` carrier)",
         bool(p) and any(V.key_parts(x)[0] == SR_L_VISA for x in p) and
         any(V.key_parts(x)[0] == SR_R_VISA for x in p),
         " -> ".join(V.show(x) for x in p[:4]) or "no path")
    fact("G5a direct source of #48 `VISA resource name`: {0}".format([V.show(x) for x in direct]))
    kk = V.terminals(A, node=KERNEL, name=KERNEL_IN, is_source=False)
    dsrc = sorted(V.sources_of(A, kk, kinds=("wire",))) if kk else []
    eff = sorted(V.effective_sources(A, kk[0])) if kk else []
    gate("G5b loop-tunnel path: kernel #5058 `cross size` resolves past the loop border",
         bool(dsrc) and A["cls"].get(V.key_parts(dsrc[0])[0]) in V.TUNNEL_OWNER and bool(eff),
         "direct {0} | effective {1}".format([V.show(x) for x in dsrc],
                                             [V.show(x) for x in eff][:3]))
    gate("G6 build + diff under 5 s on the bed", (t_bed + t_diff) < 5.0,
         "build {0:.2f}s + diff {1:.2f}s".format(t_bed, t_diff))

    # --- STEP 4b gates -----------------------------------------------------------------------------
    for tag, G in (("S1", A), ("bed", B)):
        m = G["method"]["fs_tunnel"]
        gate("G7 {0}: every FSOT paired from the machine faces".format(tag),
             m.get("outer_paired") == m.get("outer") and m.get("outer", 0) > 0 and "machine" in m["rule"],
             json.dumps(m)[:300])
        byrule = {}
        for k, a, b, info in G["edges"]:
            if k == "fs":
                r = str(info).split(":")[0] if str(info).startswith("faces") else "heuristic"
                byrule[r] = byrule.get(r, 0) + 1
        fact("G7 {0}: fs edges by rule {1}; heuristic fallback would give {2}".format(
            tag, byrule, json.dumps(HEUR[S1K if tag == "S1" else BEDK]["method"]["fs_tunnel"])[:200]))
    # G8 - run 1 of 4b (17:06) read 16/43/9, i.e. +1/+1 against step 4, and FAILED the unchanged-count
    # form of this gate. Row by row, the whole delta is ONE physical inner tunnel: FSIT #7468 - the Row D
    # target (M3a-3b, the bed's own name) - whose faces are named 'VISA out' in S1 and 'Outgoing Handle'
    # in the bed. Step 4 carried it only as a `thru` edge, which diff excludes; the exact `fs` edge is
    # a diff kind, so the rename is now SEEN. The gate asserts exactly that and nothing else.
    fsd = [("-",) + tuple(e) for e in d["edges_removed"] if e[0] == "fs"] + \
          [("+",) + tuple(e) for e in d["edges_added"] if e[0] == "fs"]
    rest = {"edges_removed": d["counts"]["edges_removed"] - sum(1 for x in fsd if x[0] == "-"),
            "edges_added": d["counts"]["edges_added"] - sum(1 for x in fsd if x[0] == "+"),
            "changed_sinks": d["counts"]["changed_sinks"]}
    for x in fsd:
        fact("G8 fs edge {0} {1} -> {2}".format(x[0], V.show(x[2]), V.show(x[3])))
    gate("G8 diff(S1, bed) minus the fs edges == 15/39/9 (step 4's 15/42/9 after dedupe_rows), and the fs delta is one -/+ pair on "
         "FSIT #7468 (Row D)",
         rest == DIFF_BEFORE and len(fsd) == 2 and {x[0] for x in fsd} == {"-", "+"} and
         all(V.key_parts(x[2])[0] == 7468 and V.key_parts(x[3])[0] == 7468 for x in fsd),
         "{0}; non-fs {1} vs step 4 {2}".format(d["counts"], rest, DIFF_BEFORE))
    for label, w_src, w_snk in REACH_CASES:
        src = [k for k in V.wire_terminals(A, w_src) if A["rows"][k]["is_source"]]
        snk = [k for k in V.wire_terminals(A, w_snk) if not A["rows"][k]["is_source"]]
        got = V.reach4(A, src, kinds=("wire", "fs")) if src else set()
        H = HEUR[S1K]
        old = V.reach4(H, src, kinds=("wire", "fs")) if src else set()
        oldall = V.reach4(H, src) if src else set()
        p = V.path(A, src[0], snk[0], kinds=("wire", "fs")) if src and snk else []
        gate("G9 {0}: reach(wire+fs) from {1} hits {2}".format(label, [V.show(x) for x in src],
                                                              [V.show(x) for x in snk][:2]),
             bool(snk) and any(x in got for x in snk),
             "path {0} hops: {1}".format(len(p), " -> ".join(V.show(x) for x in p)[:380]))
        fact("G9 {0}: heuristic graph wire+fs reaches it: {1}; heuristic graph with thru: {2}".format(
            label, any(x in old for x in snk), any(x in oldall for x in snk)))
    for tag, G in (("S1", A), ("bed", B)):
        m = G["method"]["sr"]
        fact("G11 {0}: sr paired {1} (machine {2}, top {3}), unpaired {4}, machine mismatches {5}".format(
            tag, m["paired"], m.get("paired_machine"), m.get("paired_top"), len(m["unpaired"]),
            m.get("machine_mismatch")))
    g10_equal_top()
    g12_diag_term(rec_s1, A)
    fact("total {0:.1f}s".format(time.time() - t0))
    print("=== STEP 4b: {0} pass / {1} fail".format(N["pass"], N["fail"]), flush=True)
    import protocol as P                                                           # noqa: E402
    print(P.result_line(P.make_result(N["pass"], N["fail"], None if not N["fail"] else "see FAIL lines")), flush=True)
    return 1 if N["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
