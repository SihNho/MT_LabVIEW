# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c153_b2_1_pre_t6.log:51
# ---
r"""diag_c153_b2_1_rescore - card 153-b2-1 (gate-fp fp-70, docs/d1/ring-p4d.md PD370(d)): RE-SCORE the STORED end reads of ring P4 v18
sessions s06..s09 (PB: frame-keyed computation_diff(S1, real end after pb_rename_rows)) and S1-vs-s09 (same, WITHOUT pb_rename_rows, i.e. the
raw names of the s09 graph read) with the OLD name-keyed vigraph.computation_diff (git HEAD tools/vigraph.py, md5 13be0847, loaded from
`git show`, checked by md5) and the NEW position-keyed one, on the SAME built graphs.
PRIOR ART: diag_c151_a3_3_rescore.py (the PB call shape copied: plan finalized base + last step file state, graph file terminals/objs,
L loops, BASE fs pairs, S1 files as the recipes read them; stagekit.pb_rename_rows). No LabVIEW, nothing written but the log + json.
PREDICTION: OLD rows == each scratch's stored cdiff_rows (PB stages); NEW rows == OLD rows minus rename-only rows: no new sink, and every
removed sink is listed in NEW's `renames` (a position whose sources are equal on position keys); stage-tool + s09 VI + graph md5 unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c153_b2_1_rescore.log -- py -u tools/bench/diag_c153_b2_1_rescore.py"""
import copy, hashlib, json, os, subprocess, sys, types                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path.insert(0, TOOLS)
import stagekit as K, vigraph as V, jev_candidates as JC, protocol                 # noqa: E401,E402
B = lambda *p: os.path.join(HERE, *p)                                               # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
md5 = lambda p: hashlib.md5(open(p if os.path.isabs(p) else os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
STAGES = [("s06", "plan_ring_p4_s06v18.json", "diag_c147_p4s06v18_scratch.json", "graph_ring_p4s06_20261008_192149.json"),
          ("s07", "plan_ring_p4_s07v18.json", "diag_c150_p4s07v18_scratch.json", "graph_ring_p4s07_20261008_224835.json"),
          ("s08", "plan_ring_p4_s08v18.json", "diag_c150_p4s08v18_scratch.json", "graph_ring_p4s08_20261009_033522.json"),
          ("s09", "plan_ring_p4_s09v18.json", "diag_c152_p4s09v18_scratch.json", "graph_ring_p4s09_20261009_062044.json")]
INV = ["tools/stagekit.py", "tools/addrcheck.py", "tools/stagexec.py", "tools/gscript.py", "tools/stage_prerun.py",
       os.path.join(K.CLAUDEDEV, "D1_ring_p4s09_20261009_060515.vi"), "tools/bench/graph_ring_p4s09_20261009_062044.json"]
G = {"pass": 0, "fail": 0, "first": None}
OUT = {"table": []}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(detail, default=str)[:1200]), flush=True)


def old_vigraph():
    src = subprocess.run(["git", "show", "HEAD:tools/vigraph.py"], cwd=ROOT, capture_output=True, check=True).stdout
    m = types.ModuleType("vigraph_old"); m.__file__ = os.path.join(TOOLS, "vigraph.py")   # noqa: E702
    exec(compile(src, "vigraph_old", "exec"), m.__dict__)
    return m, hashlib.md5(src).hexdigest()


def score(tag, VO, S1f, G1, stored=None):
    o, n = VO.computation_diff_frame(S1f, G1), V.computation_diff_frame(S1f, G1)
    ok_, nk = sorted(str(r["sink"]) for r in o["rows"]), sorted(str(r["sink"]) for r in n["rows"])
    ren = set()
    for r in n["renames"]:
        ren.update(str(x) for x in (r["sink"], r["sink_b"]) if x is not None)
    removed, added = sorted(set(ok_) - set(nk)), sorted(set(nk) - set(ok_))
    unexplained = [k for k in removed if k not in ren]
    row = {"pair": tag, "old_rows": len(ok_), "new_rows": len(nk), "removed": removed, "added": added, "unexplained": unexplained,
           "renames": len(n["renames"]), "stored_rows": None if stored is None else len(stored), "old_eq_stored": None if stored is None else ok_ == sorted(stored),
           "old_lost_new": [sum(1 for r in o["rows"] if r["after"] is None), sum(1 for r in o["rows"] if r["before"] is None)],
           "new_lost_new": [sum(1 for r in n["rows"] if r["after"] is None), sum(1 for r in n["rows"] if r["before"] is None)]}
    OUT["table"].append(row)
    gate("{0}: old {1} rows (lost/new {2}){3}; new {4} rows (lost/new {5}); removed {6} all rename-only: {7}; added {8}".format(
        tag, len(ok_), row["old_lost_new"], "" if stored is None else " == stored {0}: {1}".format(len(stored), row["old_eq_stored"]), len(nk),
        row["new_lost_new"], len(removed), not unexplained, len(added)),
        (stored is None or row["old_eq_stored"]) and not added and not unexplained, {"removed": removed, "added": added, "unexplained": unexplained})
    return o, n


def main():
    inv0 = dict((p, md5(p)) for p in INV)
    VO, om = old_vigraph()
    gate("P0 old vigraph = git HEAD tools/vigraph.py md5 13be0847; new vigraph md5 differs ({0})".format(md5("tools/vigraph.py")),
         om == "13be0847aad910571d1de5af1e2071f2" and md5("tools/vigraph.py") != om, om)
    LAB = JC.node_labels_default(); s1p = J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))   # noqa: E702
    S1o, S1l = JC._newest("graph_objs_s1_*.json"), JC._newest("graph_loops_s1_*.json")
    S1f = V.build4(s1p["terminals"], J(S1o)["objects"], J(S1l)["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    print("  FACT  S1 files {0} {1}".format(os.path.basename(S1o), os.path.basename(S1l)), flush=True)
    gate("P1 identity: new computation_diff(S1, S1) == 0 rows, 0 renames", not V.computation_diff_frame(S1f, S1f)["rows"]
         and not V.computation_diff_frame(S1f, S1f)["renames"])
    for st, pf, sf, gf in STAGES:
        P, SCR, GR = J(B(pf)), J(B(sf)), J(B(gf))
        fb, last = P["finalized"]["base"], P["finalized"]["step_files"][-1]
        BASE, L = J(fb["path"]), J(last["path"])["state"]
        stored = next((v["cdiff_rows"] for k, v in SCR.items() if isinstance(v, dict) and "cdiff_rows" in v), None)
        print("  FACT  {0}: plan {1} base {2} graph {3} md5 field {4} scratch saves md5 {5}".format(st, md5(B(pf))[:8], md5(fb["path"])[:8],
              md5(B(gf))[:8], (GR.get("md5") or "")[:8], ((SCR.get("saves") or {}).get("md5") or "")[:8]), flush=True)
        real = GR["terminals"]
        pbr, restored, _u = K.pb_rename_rows(BASE["terminals"], L["terminals"], real, None)
        FSP = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
        G1 = V.build4(pbr, GR["objs"], copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True)
        score("S1 vs {0} PB (pb_rename_rows restored {1})".format(st, len(restored)), VO, S1f, G1, stored)
        if st == "s09":
            G9 = V.build4(real, GR["objs"], copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True)
            o, n = score("S1 vs s09 raw names (no pb_rename_rows)", VO, S1f, G9)
            OUT["s1_s09_renames"] = n["renames"][:40]
    inv1 = dict((p, md5(p)) for p in INV)
    gate("INV stage tools + s09 VI + s09 graph md5 before == after", inv0 == inv1, dict((os.path.basename(p), inv1[p][:8]) for p in INV))
    OUT.update({"invariants": inv1, "gates": G, "vigraph_new": md5("tools/vigraph.py")})
    json.dump(OUT, open(B("diag_c153_b2_1_rescore.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("=== GATES: {0} pass / {1} fail".format(G["pass"], G["fail"]), flush=True)
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": "tools/bench/diag_c153_b2_1_rescore.json",
                                                                                        "md5": md5(B("diag_c153_b2_1_rescore.json"))}])), flush=True)
    return 1 if G["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
