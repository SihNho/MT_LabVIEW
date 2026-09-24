r"""sim_l7_split - card chat-S2 REAL CASE: replay the loop-1.7 split (L7-1a -> L7-1b -> L7-R) through tools/stagesim.py
from graph_s3_loop15_20260924.json and compare with what LabVIEW actually produced. PURE PYTHON, no LabVIEW.

WHAT EXISTED FIRST: the three stage records (stage_d1_l7_1a.json, stage_d1_l7_1b.json, stage_d1_l7_r.json) and
l7_r_prediction.json - every action row below is READ from them or derived from the graph (RULE-CHAIN-S1 via
jev_candidates.s1_chains for the register rows); nothing is re-typed except the destination body #23405 and loop
#23041 (stage_d1_l7_1a.log D0 "#376 now owned by #23405").
NO terminal-level graph of D1_s4_loop17.vi exists on disk (only its md5 and errorlists), so the REFERENCE end graph is
RECONSTRUCTED from the recorded, gate-verified uid-edge diffs:
  S3 edges - (every edge touching #376 + PD3's 3 extra removed edges, stage_d1_l7_1a.log:97)
           + the 12 edges added by L7-1b (stage_d1_l7_1b_r3.log:347)
           - / + the L7-R removed/added lists (l7_r_prediction.json; PC1/PC2 PASS in stage_d1_l7_r_r2.log:454-455)
and compared up to new-uid naming (stagesim.canon: a new object is its class).
PREDICTION: base cdiff 0 rows; every action applies; move cut set = #376's 12 wires; new half-wires after the move ==
the 12 diag_c71 observed; canon diff 0 at L7-1a / L7-1 / end; L7-1 cdiff == the recorded 8 rows; end cdiff == the
recorded 1 row (#376 'current frame data array in', left open by design) => plan NOT final, first divergent step = 1.
    MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/sim_l7_split.log -- py -u tools/bench/sim_l7_split.py"""
import ast, json, os, re, sys                                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import stagesim as S, vigraph as V, jev_candidates as JC, protocol                # noqa: E401,E402
J = lambda f: json.load(open(os.path.join(HERE, f), encoding="utf-8"))            # noqa: E731
rel = lambda f: "tools/bench/" + f                                                 # noqa: E731
GATES = []
def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)  # noqa: E702
def fact(t): print("  FACT  " + str(t)[:900], flush=True)                         # noqa: E704

GRAPH, LOOPS, WIKI = "graph_s3_loop15_20260924.json", "graph_loops_m4b_20260924.json", "docs/wiki/subvi/{0}.json".format(JC.BED_KEY)
L7A, L7B, L7R, PRED = J("stage_d1_l7_1a.json"), J("stage_d1_l7_1b.json"), J("stage_d1_l7_r.json"), J("l7_r_prediction.json")
LOOP, BODY = 23041, 23405
MOVED = int(re.search(r"#(\d+)", next(o["detail"] for o in L7A["ops"] if o["verb"] == "move_in")).group(1))
S1 = JC.load(JC.S1_KEY)
g3 = J(GRAPH); st0 = S.base_state(g3, {"loops": {"path": rel(LOOPS)}, "fs_pairs_wiki": {"path": WIKI}}); G3 = S.graph(st0)
def src_on(G, w):
    return [r for r in G["rows"].values() if r["wire_uid"] == w and r["is_source"]]
def addr(r): return {"uid": V.node_of(r), "term": r["term_name"], "term_uid": r["term_uid"]}  # noqa: E704

A = [{"op": "move_in", "id": "l7_1a_move", "nodes": [MOVED], "dest_diagram": BODY}]
chains = JC.s1_chains(S1, MOVED); fact("RULE-CHAIN-S1 chains of #{0}: {1}".format(MOVED, [(c["chain"], c["out"], c["in"], c["init"]) for c in chains]))  # noqa: E702
sym = {}
for c in sorted(chains, key=lambda c: c["chain"] != "err"):                         # err first, as the stage did (reg 0 = err)
    n = len(sym) + 1; sym[c["chain"]] = "SR{0}".format(n)                          # noqa: E702
    A.append({"op": "add_shift_reg", "id": "l7_1a_sr_" + c["chain"], "loop": LOOP, "body": BODY, "as": sym[c["chain"]],
              **({"checkpoint": "L7-1a"} if n == len(chains) else {})})
for c in sorted(chains, key=lambda c: c["chain"] != "err"):
    s = sym[c["chain"]]
    A += [{"op": "wire", "id": c["chain"] + "_R", "src": {"uid": MOVED, "term": c["out"]}, "dst": "new:{0}R.inner".format(s)},
          {"op": "wire", "id": c["chain"] + "_L", "src": "new:{0}L.inner".format(s), "dst": {"uid": MOVED, "term": c["in"]}}]
for c in sorted(chains, key=lambda c: c["chain"] != "err"):
    A.append({"op": "wire", "id": c["chain"] + "_init", "src": {"uid": c["init"][0], "term": c["init"][1]}, "dst": "new:{0}L.outer".format(sym[c["chain"]])})
old_tun = [int(re.search(r"owned by #(\d+)", r["observed"]["how"][1]).group(1)) for r in L7B["rows"] if r["label"].split()[-1].startswith("tun_")]
fact("L7-1b tunnel rows replace old tunnels {0} (stage_d1_l7_1b.json rows 'owned by #')".format(old_tun))
for i, t in enumerate(old_tun, 1):
    outer = [r for k, r in G3["rows"].items() if V.node_of(r) == t and r["term_class"] == "OuterTerminal" and not r["is_source"]]
    inner = [r for k, r in G3["rows"].items() if V.node_of(r) == t and r["term_class"] == "InnerTerminal" and r["is_source"]]
    feed = src_on(G3, outer[0]["wire_uid"])
    sink = [r for r in G3["rows"].values() if r["wire_uid"] == inner[0]["wire_uid"] and V.node_of(r) == MOVED and not r["is_source"]]
    fact("old tunnel #{0}: outer feed {1} -> #{2} {3!r}".format(t, [(V.node_of(x), x["term_uid"]) for x in feed], MOVED, [x["term_name"] for x in sink]))
    A += [{"op": "tunnel", "id": "tun_{0}".format(t), "loop": LOOP, "body": BODY, "dir": "in", "as": "T{0}".format(i)},
          {"op": "wire", "id": "tun_{0}_out".format(t), "src": addr(feed[0]), "dst": "new:T{0}.outer".format(i)},
          {"op": "wire", "id": "tun_{0}_in".format(t), "src": "new:T{0}.inner".format(i), "dst": {"uid": MOVED, "term": sink[0]["term_name"]}}]
A[-1]["checkpoint"] = "L7-1"
# ---- L7-R, from l7_r_prediction.json (the rows stage_d1_l7_r.py executed, in its order)
realsym = {L7A["l7_1a"]["sr"][c]["right"]: "new:{0}R".format(sym[c]) for c in sym}
A += [{"op": "delete_wire", "id": "del_w{0}".format(w), "wire_uid": w} for w in PRED["del_w"]]
A += [{"op": "move_in", "id": "move_{0}".format(u), "nodes": [u], "dest_diagram": BODY} for u, _p in PRED["moves"]]
added = [e for e in PRED["added"]]
def e_src(e): return realsym.get(e[1], e[1]) if not isinstance(e[1], str) else "new:" + e[1]   # noqa: E704
TUN = {}
for tag in ("TFP", "TFN"):                                                           # a new out-tunnel per recorded TFP/TFN
    TUN[tag] = "T{0}".format(len(old_tun) + len(TUN) + 1)
    feed = next(e for e in added if e[3] == tag)
    A += [{"op": "tunnel", "id": "tun_" + tag, "loop": LOOP, "body": BODY, "dir": "out", "as": TUN[tag]},
          {"op": "wire", "id": tag + "_in", "src": {"uid": feed[1], "term_uid": feed[2]}, "dst": "new:{0}.inner".format(TUN[tag])}]
    for e in [e for e in added if e[1] == tag]:
        A.append({"op": "wire", "id": "{0}_to_{1}".format(tag, e[3]), "src": "new:{0}.outer".format(TUN[tag]), "dst": {"uid": e[3], "term_uid": e[4]}})
for e in [e for e in added if not isinstance(e[1], str) and not isinstance(e[3], str)]:
    src = {"uid": realsym[e[1]], "side": "outer"} if e[1] in realsym else {"uid": e[1], "term_uid": e[2]}
    A.append({"op": "wire", "id": "r_{0}_{1}".format(e[1], e[3]), "src": src, "dst": {"uid": e[3], "term_uid": e[4]}})
A += [{"op": "delete_object", "id": "retire_{0}".format(u), "uid": u, "missing_ok": True} for _c, u in PRED["retire"]]
A += [{"op": "remove_bad_wires", "id": "rbw", "checkpoint": "L7-R"}]
plan = {"schema": "stageplan/1", "stage": "l7_split", "goal": "replay loop 1.7 split (L7-1a, L7-1b, L7-R) from D1_s3_loop15",
        "base": {"path": rel(GRAPH), "md5": S.md5_file(os.path.join(HERE, GRAPH))},
        "context": {"loops": {"path": rel(LOOPS)}, "fs_pairs_wiki": {"path": WIKI}, "s1_key": JC.S1_KEY}, "actions": A}
pp = os.path.join(HERE, "stageplan_l7_split.json"); json.dump(plan, open(pp, "w", encoding="utf-8"), indent=1)  # noqa: E702
gate("C0 plan validates as stageplan/1 ({0} actions)".format(len(A)), protocol.validate_obj(plan)[0], protocol.validate_obj(plan)[1])
R = S.simulate(pp, os.path.join(HERE, GRAPH), labels=JC.node_labels_default())
gate("C1 base (S3) computation_diff(S1) == 0 rows (promote_d1_s3_loop15.log)", R["steps"][0]["cdiff_rows"] == [], R["steps"][0]["cdiff_rows"])
gate("C2 every action applied", R["failed"] is None, R["failed"])
st1 = json.load(open(R["steps"][1]["file"]["path"], encoding="utf-8"))
w376 = sorted(set(r["wire_uid"] for r in st0["terminals"] if r["owner_uid"] == MOVED and r["wire_uid"]))
gate("C3 move cut set == every wire of #376 ({0})".format(len(w376)), st1["effect"]["cut_set"] == w376, (st1["effect"]["cut_set"], w376))
f0 = set(f["wire_uid"] for f in G3["flags"]); f1 = set(f["wire_uid"] for f in S.graph(st1["state"])["flags"])  # noqa: E702
OBS = [464, 541, 1397, 1581, 3497, 3629, 4337, 4517, 4880, 5056, 5073, 5274]      # diag_c71_l7_1a_tunnels.log 'half_wires_only_in_b'
gate("C4 new half-wires after the move == the 12 LabVIEW showed (diag_c71)", sorted(f1 - f0) == OBS, {"sim_only": sorted((f1 - f0) - set(OBS)), "obs_only": sorted(set(OBS) - (f1 - f0))})
# ---- reference edges
base_nodes = set(V.node_of(r) for r in st0["terminals"]); E3 = S.uid_edges(G3)
pd3 = ast.literal_eval(re.search(r"\((\[.*\]), \[\]\)\s*$", open(os.path.join(HERE, "stage_d1_l7_1a.log"), encoding="utf-8").read().splitlines()[96]).group(1))
ref = {"L7-1a": set(e for e in E3 if MOVED not in (e[1], e[3])) - set(pd3)}
a1b = ast.literal_eval(re.search(r"uid edges removed \[\] added (\[.*\])\s*$", open(os.path.join(HERE, "stage_d1_l7_1b_r3.log"), encoding="utf-8").read().splitlines()[346]).group(1))
ref["L7-1"] = ref["L7-1a"] | set(a1b)
ref["L7-R"] = (ref["L7-1"] - set(tuple(e) for e in PRED["removed"])) | set(tuple(e) for e in PRED["added"])
CLS = {"TFP": "LoopTunnel", "TFN": "LoopTunnel"}
for v in L7A["l7_1a"]["sr"].values(): CLS[v["right"]], CLS[v["left"]] = "RightShiftRegister", "LeftShiftRegister"   # noqa: E701
for u in L7B["l7_1b"]["tunnels"]: CLS[u] = "LoopTunnel"                            # noqa: E701
REC_CD = {"L7-1": 8, "L7-R": [tuple(x) for x in L7R["l7_r"]["cdiff_rows"]]}
for cp in ("L7-1a", "L7-1", "L7-R"):
    s = next(x for x in R["steps"] if x.get("checkpoint") == cp)
    stc = json.load(open(s["file"]["path"], encoding="utf-8"))["state"]
    Gs = S.graph(stc); cls_new = dict((u, S.obj_class(stc, u)) for u in stc["sym"].values())   # noqa: E702
    d = S.canon_diff(S.canon(S.uid_edges(Gs), base_nodes, cls_new.get), S.canon(ref[cp], base_nodes, CLS.get))
    fact("{0} (step {1}) canon diff n={2} only_sim={3} only_ref={4}".format(cp, s["n"], d["n"], d["only_sim"][:8], d["only_ref"][:8]))
    gate("C5 {0}: simulated uid-edges == recorded reference up to new-uid naming (diff count {1})".format(cp, d["n"]), d["n"] == 0, d["n"])
    rows = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in s["cdiff_rows"]))
    fact("{0} simulated cdiff rows: {1}".format(cp, rows))
    if cp in REC_CD:
        want = REC_CD[cp]
        gate("C6 {0}: simulated computation_diff rows == recorded ({1})".format(cp, want if isinstance(want, int) else want),
             (len(rows) == want) if isinstance(want, int) else rows == sorted(want), rows)
rbw = json.load(open(R["steps"][-1]["file"]["path"], encoding="utf-8"))["effect"]
gate("C8 remove_bad_wires clears only #376's real half-wires [1581, 3629, 4517] (review chat-s2-rbw; chat-S2b dedupe)",
     rbw.get("removed_wires") == [1581, 3629, 4517], rbw)
gate("C7 plan NOT final (1 row left open by design) and first divergent step == 1 (the move)",
     not R["final"] and (R["first_divergent"] or {}).get("n") == 1, (R["final"], R["first_divergent"]))
fact("candidates (cut rows with >1 legal mechanism): {0}; model sources: {1}".format(R["n_candidates"], sorted(set(x.get("model_source") for x in R["steps"][1:]))))
fact("plan_out {0}; summary {1}".format(R["plan_out"], S._rel(R["summary_path"])))
n_pass = sum(1 for _l, ok in GATES if ok); n_fail = len(GATES) - n_pass; first = next((l for l, ok in GATES if not ok), None)  # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [{"path": R["plan_out"]["path"], "md5": R["plan_out"]["md5"]}])))
