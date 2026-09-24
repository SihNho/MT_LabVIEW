r"""dedupe_check_s2b - card chat-S2b: the vigraph load dedupe (vigraph.dedupe_rows, first occurrence wins) changes
NOTHING the 2026-09-23 map bench measured and no computation_diff row. PURE PYTHON, no LabVIEW.

OLD = tools/vigraph.py at git HEAD (before the dedupe), loaded from `git show` into %TEMP%; NEW = the working file.
A1/A2/A3 of docs/connectivity-map-bench.md need LabVIEW (live reads) and are NOT re-run (card labview none); they are
shown unchanged OFFLINE instead: A1 = diff() on edge SETS, so equal edge sets on S1 => equal diff (D1); A2 = the 200
picked wires (raw/bench_map_a23.json a2.picks) carry no duplicated row (D4); A3 = no FS tunnel row is duplicated (D5).
A4 is re-run as its own script (bench_map_a4_s2b.log) and compared with 150/151.
PREDICTION: D1 edge sets equal on S1 / bed / S3, dropped rows 23 / 29 / 29, nonidentical 0, flags drop by the
duplicate-source wires only; D2 cdiff(S1,S3) 0 -> 0; D3 cdiff(S1, chat-S2 end state) rows equal old vs new; D4 0 picks
touched; D5 0 FS rows duplicated.
    MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/dedupe_check_s2b.log -- py -u tools/bench/dedupe_check_s2b.py"""
import collections, importlib.util, json, os, subprocess, sys, tempfile          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import vigraph as VN, jev_candidates as JC, protocol                             # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))            # noqa: E731
GATES = []
def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)  # noqa: E702
src = subprocess.run(["git", "show", "HEAD:tools/vigraph.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
p = os.path.join(tempfile.gettempdir(), "vigraph_old_s2b.py"); open(p, "w", encoding="utf-8").write(src)  # noqa: E702
spec = importlib.util.spec_from_file_location("vigraph_old", p); VO = importlib.util.module_from_spec(spec); spec.loader.exec_module(VO)  # noqa: E702
gate("D0 OLD has no dedupe_rows, NEW has it", not hasattr(VO, "dedupe_rows") and hasattr(VN, "dedupe_rows"))
LAB = JC.node_labels_default()
W1, WB, S3 = J("docs/wiki/subvi/D1_s1_copy.json"), J("docs/wiki/subvi/{0}.json".format(JC.BED_KEY)), J("tools/bench/graph_s3_loop15_20260924.json")
O1, L1 = J("tools/bench/graph_objs_s1_20260923.json")["objects"], J("tools/bench/graph_loops_s1_20260924.json")["loops"]
OB, LB = J("tools/bench/graph_objs_bed_20260923.json")["objects"], J("tools/bench/graph_loops_bed_20260924.json")["loops"]
LM = J("tools/bench/graph_loops_m4b_20260924.json")["loops"]
ARGS = {"S1": (W1["terminals"], O1, L1, LAB, W1["fs_tunnel_pairs"]), "bed": (WB["terminals"], OB, LB, LAB, WB["fs_tunnel_pairs"]),
        "S3": (S3["terminals"], S3["objs"], LM, LAB, WB["fs_tunnel_pairs"])}
G = {}
print("  TABLE graph | edges old/new (list) | edge SET equal | flags old/new | dropped | nonidentical")
for k, a in ARGS.items():
    go, gn = VO.build4(*a), VN.build4(*a); G[k] = (go, gn)
    # keyed by TERMINAL UID (stagekit.uid_edges form): a duplicate row got its own name-key ordinal '|1' under OLD, so
    # a name-keyed set differs by those phantom keys only (run 1 of this script compared name keys - reported below)
    ue = lambda GG: set((e[0], VN.key_parts(e[1])[0], GG["rows"][e[1]]["term_uid"], VN.key_parts(e[2])[0], GG["rows"][e[2]]["term_uid"]) for e in GG["edges"])  # noqa: E731
    eo, en = ue(go), ue(gn)
    phantom = sorted(set(go["rows"]) - set(gn["rows"]))
    dd = gn["method"]["dedupe"]
    print("  TABLE {0} | {1}/{2} | {3} | {4}/{5} | {6} | {7} | phantom name-keys under OLD {8} (all ordinal>0: {9})".format(
        k, len(go["edges"]), len(gn["edges"]), eo == en, len(go["flags"]), len(gn["flags"]), dd["dropped"], dd["nonidentical"],
        len(phantom), all(VN.key_parts(x)[3] > 0 for x in phantom)))
    gate("D1 {0}: uid-edge SET unchanged by the dedupe; no non-identical duplicate; only '|n>0' phantom keys vanish".format(k),
         eo == en and not dd["nonidentical"] and not (set(gn["rows"]) - set(go["rows"])) and all(VN.key_parts(x)[3] > 0 for x in phantom), dd)
gate("D1b dropped rows == 23 / 29 / 29 (S1 / bed / S3, measured by the probe)", [G[k][1]["method"]["dedupe"]["dropped"] for k in ARGS] == [23, 29, 29])
cd = lambda V, A, B: sorted(r["sink"] for r in V.computation_diff(A, B)["rows"])   # noqa: E731
b, a = cd(VO, G["S1"][0], G["S3"][0]), cd(VN, G["S1"][1], G["S3"][1])
print("  TABLE cdiff(S1,S3) rows old {0} new {1}".format(len(b), len(a))); gate("D2 cdiff(S1,S3) rows old == new == 0", b == a == [], (b, a))  # noqa: E702
# the chat-S2 end state (duplicates kept) is REGENERATED: the same plan through stagesim with vigraph's dedupe disabled,
# into %TEMP% (the committed tools/bench/sim/l7_split is not touched)
import stagesim as SS                                                              # noqa: E402
_real = VN.dedupe_rows
VN.dedupe_rows = lambda t: (list(t), {"dropped": 0, "term_uids": [], "nonidentical": []})
tmp = tempfile.mkdtemp(prefix="s2b_d3_")
R0 = SS.simulate(os.path.join(HERE, "stageplan_l7_split.json"), os.path.join(HERE, "graph_s3_loop15_20260924.json"),
                 out_root=tmp, plan_out_dir=tmp, labels=LAB, log=lambda *_a: None)
VN.dedupe_rows = _real
st = R0["_state"]
print("  FACT  D3 regenerated chat-S2 end state: {0} rows, rbw removed {1}".format(len(st["terminals"]), json.load(open(R0["steps"][-1]["file"]["path"], encoding="utf-8"))["effect"]))
E = (st["terminals"], st["objs"], st["loops"], LAB, st["fs_pairs"])
b, a = cd(VO, G["S1"][0], VO.build4(*E)), cd(VN, G["S1"][1], VN.build4(*E))
print("  TABLE cdiff(S1, chat-S2 sim end = the D1_s4 reference) rows old {0} new {1}: {2}".format(len(b), len(a), a))
gate("D3 cdiff(S1, D1_s4 reference) rows unchanged by the dedupe", b == a, (b, a))
dups = set(u for u, n in collections.Counter(r["term_uid"] for r in W1["terminals"]).items() if n > 1)
picks = set(J("tools/bench/bench_map_20260923/raw/bench_map_a23.json")["a2"]["picks"])
hit = sorted(set(r["wire_uid"] for r in W1["terminals"] if r["term_uid"] in dups) & picks)
gate("D4 A2: none of the 200 picked wires carries a duplicated row (so 200/200 cannot move)", len(picks) == 200 and not hit, hit)
fsd = [r["term_uid"] for r in W1["terminals"] if r["term_uid"] in dups and "FlatSequence" in r["owner_class"]]
gate("D5 A3: no flat-sequence tunnel row is duplicated (so 58/58 cannot move)", not fsd, fsd)
exp = J("tools/bench/bench_map_20260923/raw/bench_map_a1.json")["a1"]["expected"]
touch = [e for e in exp if any(VN.key_parts(k)[0] in dups or any(r["term_uid"] in dups for r in W1["terminals"] if VN.node_of(r) == VN.key_parts(k)[0] and r["term_name"] == VN.key_parts(k)[2]) for k in e[2:4])]
gate("D6 A1: the 9 expected mutation rows touch no duplicated terminal (and diff works on edge sets, D1)", len(exp) == 9 and not touch, touch)
n_pass = sum(1 for _l, ok in GATES if ok); n_fail = len(GATES) - n_pass; first = next((l for l, ok in GATES if not ok), None)  # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
