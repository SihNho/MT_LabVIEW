# ---
# labview: none
# hardware: none
# evidence: tools/bench/selftest_t6_poskey_postmerge.log:51
# ---
r"""diag_c151_a3_3_rescore - card 151-a3-3 (PD367(f)(h), PD366): RE-SCORE ring P4 v18 session 7's STORED scratch end read OFFLINE
with stagekit 604529e8's POSITION-keyed result gates D / TD / PB. No LabVIEW, no licence (renames=None), no stage-tool / stagekit edit.
PRIOR ART: diag_c147_b1_1_rescore.py / selftest_t6_poskey.py (same offline call of the same stagekit functions; their run under labview
none = the evidence line above). EXISTING (checked first): the s07 recipe tools/recipes/stage_d1_ring_p4_s07v18.py:161-181 calls K.term_identity_gates (D, TD) and
K.pb_rename_rows + vigraph.build4 + vigraph.computation_diff_frame (PB); this file calls the SAME functions with the SAME arguments, taken
from stored files instead of a live run:
  base  = plan finalized.base (sim/ring_p4_s07v18_base_real_fsmap.json), sim end L = the plan's last step file `state`;
  real  = graph_ring_p4s07_20261008_224835.json `terminals` (full rows of the saved s07 file b3f86b32), accepted ONLY if its
          (term_uid, owner_uid, term_name, wire_uid, is_source) projection == the scratch json's `real_end_rows` (the run's end read);
  bind  = obj: union of the stored per-op `bound` dicts; term: {} (needed only for a CREATED front-panel terminal - checked, else MISSING);
  PB objs = the graph file `objs` (the run's be.last_objs was not stored), loops = L's, fs pairs = BASE's, S1 files as the recipe reads them.
PREDICTION: every input md5 == card pin; projection equal; D, TD, PB each print a verdict + counts; invariants md5 before == after.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c151_a3_3_rescore.log -- py -u tools/bench/diag_c151_a3_3_rescore.py"""
import copy, hashlib, json, os, sys                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path.insert(0, TOOLS)
import stagekit as K, vigraph as V, jev_candidates as JC, protocol                 # noqa: E401,E402
B = lambda *p: os.path.join(HERE, *p)                                               # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
md5 = lambda p: hashlib.md5(open(p if os.path.isabs(p) else os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
S07VI = os.path.join(K.CLAUDEDEV, "D1_ring_p4s07_20261008_222709.vi")
PINS = {"tools/bench/diag_c150_p4s07v18_scratch.log": "81078c1353afdcfc33ce8b200d5ef177", "tools/bench/diag_c150_p4s07v18_scratch.json": "1903778b3a8b7f58283b5b3da75cb643",
        "tools/bench/diag_c150_p4s07v18_scratch_sum.json": "926df24807c5fc1419b68398220efc59", "tools/bench/plan_ring_p4_s07v18.json": "08c2ad4d2e6dd4bddd4dd5b18326562c",
        "tools/bench/plan_ring_p4_s07v18_pred.json": "6f46fc3c67b3a7f3c045d07a2fa7163c", "tools/bench/plan_ring_p4_s07v18_licence.json": "aedbe1f168e4cd8c18d300848ce0b788",
        "tools/stagekit.py": "604529e8e9b68b9c4b370b8f3d5c5ee5", "tools/addrcheck.py": "207beb0d09102c78b1e06d1f076eec7e"}
INV = ["tools/stagekit.py", "tools/addrcheck.py", "tools/stagexec.py", "tools/gscript.py", "tools/stage_prerun.py", "tools/vigraph.py", "tools/stagesim.py",
       S07VI, "tools/bench/memory_model.json", "tools/bench/gate_fp_queue.jsonl"]
G = {"pass": 0, "fail": 0, "first": None}
OUT = {}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(detail, default=str)[:900]), flush=True)


def bounds(o, acc):
    if isinstance(o, dict):
        if isinstance(o.get("bound"), dict):
            acc.update(o["bound"])
        for v in o.values():
            bounds(v, acc)
    elif isinstance(o, list):
        for v in o:
            bounds(v, acc)
    return acc


def main():
    inv0 = dict((p, md5(p)) for p in INV)
    gate("P0 card input md5 == pin", all(md5(p) == m for p, m in PINS.items()), dict((p, md5(p)) for p, m in PINS.items() if md5(p) != m))
    P = J(B("plan_ring_p4_s07v18.json")); PRED = J(B("plan_ring_p4_s07v18_pred.json")); SCR = J(B("diag_c150_p4s07v18_scratch.json"))   # noqa: E702
    fb, sf = P["finalized"]["base"], P["finalized"]["step_files"][-1]
    gate("P1 base + sim end step file md5 == the plan's pins", md5(fb["path"]) == fb["md5"] and md5(sf["path"]) == sf["md5"], [fb, sf])
    BASE, L = J(fb["path"]), J(sf["path"])["state"]
    GRP = B("graph_ring_p4s07_20261008_224835.json"); GR = J(GRP)
    proj = lambda rows: [[r["term_uid"], r.get("owner_uid"), r.get("term_name"), r.get("wire_uid"), bool(r.get("is_source"))] for r in rows]   # noqa: E731
    rd = V.dedupe_rows(list(GR["terminals"]))[0]
    eq_raw, eq_dd = proj(GR["terminals"]) == SCR["real_end_rows"], proj(rd) == SCR["real_end_rows"]
    gate("P2 graph file md5 field == s07 saved md5 b3f86b32; its terminal projection == the scratch json real_end_rows (raw {0} / dedupe {1}; rows {2} / {3})".format(
        eq_raw, eq_dd, len(GR["terminals"]), len(SCR["real_end_rows"])), GR.get("md5") == SCR["saves"]["md5"] and (eq_raw or eq_dd), GR.get("md5"))
    real = GR["terminals"] if eq_raw else rd
    OBJ = bounds(SCR.get("stagexec"), {})
    basetu = set(r["term_uid"] for r in BASE["terminals"])
    fpnew = sorted(r["term_uid"] for r in L["terminals"] if r.get("term_class") == V.FP_CLASS and r["term_uid"] not in basetu)
    gate("P3 obj binding from the stored per-op `bound` ({0} entries); no CREATED front-panel terminal needs a term binding (needs: {1})".format(len(OBJ), fpnew),
         bool(OBJ) and not fpnew, OBJ)
    ti = K.term_identity_gates(BASE["terminals"], L["terminals"], real, renames=None, bind={"term": {}, "obj": OBJ})
    OUT["ti"] = ti
    gate("D new wires {0} == sim's {1}; lost {2} == sim's {3}; new on kept nodes real/sim {4}; reuse noted {5} (position keys, stagekit.term_identity_gates)".format(
        ti["d_new"], len(ti["sim_new"]), ti["d_lost"], len(ti["sim_lost_w"]), ti["d_new_kept_nodes"], [n["wire"] for n in ti["reuse_noted"]]), ti["d_ok"],
        {"new": ti["new"], "lost": ti["lost_w"], "sim_new": ti["sim_new"], "sim_lost": ti["sim_lost_w"]})
    gate("TD unwired {0}, moved {1}, lost {2} == plan deletes {3}, recycled {4}, renames {5} (INFO), extra {6} (INFO), key {7}".format(
        len(ti["unwired"]), len(ti["moved"]), len(ti["lost"]), len(ti["gone"]), len(ti["recycled"]), len(ti["renames"]), len(ti["extra"]), ti["td_key"]), ti["td_ok"],
        {"unwired": ti["unwired"][:10], "moved": ti["moved"][:10], "lost": ti["lost"][:10], "gone": ti["gone"][:10], "renames": ti["renames"][:10], "extra": ti["extra"][:10]})
    LAB = JC.node_labels_default(); s1p = J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))   # noqa: E702
    S1o, S1l = JC._newest("graph_objs_s1_*.json"), JC._newest("graph_loops_s1_*.json")
    S1f = V.build4(s1p["terminals"], J(S1o)["objects"], J(S1l)["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    pbr, restored, unlic = K.pb_rename_rows(BASE["terminals"], L["terminals"], real, None)
    FSP = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    G1 = V.build4(pbr, GR["objs"], copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    pairs_ok = set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"])
    OUT["pb"] = {"rows": rk, "extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "restored": restored,
                 "unlicensed": unlic, "pairs_ok": pairs_ok, "s1_files": [os.path.basename(S1o), os.path.basename(S1l)], "stored_run_rows_equal": rk == SCR["ring_p4_s07v18"]["cdiff_rows"]}
    gate("PB cdiff rows {0} == pred's {1}; open pairs == plan's {2}: {3}; restored {4} (INFO); unlicensed {5}; == the run's stored cdiff_rows: {6}".format(
        len(rk), len(PRED["cdiff_rows"]), len(P["open_rows"]), pairs_ok, len(restored), unlic, OUT["pb"]["stored_run_rows_equal"]),
        rk == PRED["cdiff_rows"] and pairs_ok and unlic == [], {k: OUT["pb"][k] for k in ("extra", "missing", "restored")})
    for f, lines in (("diag_c150_p4s07v18_scratch.log", (363, 368, 370)), ("diag_c150_p4s08v18_scratch.log", (267, 272, 274))):
        txt = open(B(f), encoding="utf-8", errors="replace").read().splitlines()
        for n in lines:
            print("  FACT  {0}:{1} {2}".format(f, n, txt[n - 1].strip()[:260]), flush=True)
    inv1 = dict((p, md5(p)) for p in INV)
    gate("INV invariants md5 before == after", inv0 == inv1, dict((os.path.basename(p), inv1[p][:8]) for p in INV))
    OUT.update({"invariants": inv1, "gates": G})
    json.dump(OUT, open(B("diag_c151_a3_3_rescore.json"), "w", encoding="utf-8"), indent=1, default=str)
    print("=== GATES: {0} pass / {1} fail".format(G["pass"], G["fail"]), flush=True)
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": "tools/bench/diag_c151_a3_3_rescore.json",
                                                                                        "md5": md5(B("diag_c151_a3_3_rescore.json"))}])), flush=True)
    return 1 if G["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
