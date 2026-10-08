# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c147_b1_1_rescore2.log:3
# ---
r"""selftest_c147_b1_2 - card 147-b1-2 (PD356(b)): offline test of the new stagekit D / TD / PB rules (stagekit.term_identity_gates
renames= / bind=, licence_renames, rename_check, pb_rename_rows). No LabVIEW, no COM call: stagekit / stagexec / vigraph / jev_candidates are
imported inside main() for their PURE functions only - the same imports and reconstruction as tools/bench/diag_c147_b1_1_rescore.py:126-186
(run offline, diag_c147_b1_1_rescore2.log:1-33). PRIOR ART: selftest_td_key_c141_3.py (TD key, old_td reference) - the old functions are
copied here verbatim (stagekit.py 9a3fceaf :1355-1395) as the reference for "no new input = today's verdict".
PREDICTION: T0 default call == the pre-edit code on s06 (dict equal); T1 147-a1-8 rows + 5-rename licence: D, TD, PB PASS; T2 licence of
2832/4160/4165 only: TD FAIL naming 9505/9508; T3 w23807 keeps sink 9519: D FAIL (reuse_bad 23807); T4 licensed 2832 changes owner: TD FAIL;
T4b licensed 2832 under a name other than 'to': TD FAIL; T5 s03/s04/s05 stored end reads: new default == old == the run's stored verdict;
F1/F2 stagekit format safety (selftest_stagekit.py:150-163 copied); P pins unchanged."""
import ast, collections, copy, hashlib, json, os, sys                             # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
PINS = {"tools/stagexec.py": "1bab9cf9", "tools/gscript.py": "1a80236e", "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "88eeb037",
        "tools/bench/plan_ring_p4_s06v18.json": "cfbd9823", "tools/bench/plan_ring_p4_s06v18_pred.json": "c4a6a35a",
        "tools/bench/plan_ring_p4_s06v18_licence.json": "7dce79aa", "tools/bench/plan_ring_p4_s06v18_in.json": "db72d8af",
        "tools/recipes/stage_d1_ring_p4_s06v18.py": "9150f15b", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py": "31009bfc"}
T5 = (("s03", "plan_ring_p4_s03v18.json", "diag_c143_p4s03v18_scratch.json", "282301ca"), ("s04", "plan_ring_p4_s04v18.json", "diag_c144_p4s04v18_scratch.json", "95e408ff"),
      ("s05", "plan_ring_p4_s05v18.json", "diag_c145_p4s05v18_scratch.json", "3f9ac26b"))
L5 = {"renames": [{"node": 2626, "term_uids": [2832, 4160, 4165], "from": "array", "to": "element"}, {"node": 9503, "term_uids": [9505, 9508], "from": "Value", "to": ""}]}
L3 = {"renames": L5["renames"][:1]}
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def fact(s):
    print("  FACT  " + s, flush=True)


# ---- the PRE-EDIT code, verbatim (stagekit.py 9a3fceaf :1348-1395), the reference for the default call
def _iv(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return str(v)


def old_term_key(r):
    return (_iv(r["term_uid"]), _iv(r.get("owner_uid")), str(r.get("term_name") or ""))


def old_wire_keys(rows):
    src = {}
    for r in rows:
        w = _iv(r.get("wire_uid") or 0)
        if w in (0, "", "0", "None"):
            continue
        src.setdefault(w, set())
        if r.get("is_source"):
            src[w].add(old_term_key(r))
    return set((w, frozenset(s)) for w, s in src.items())


def old_tig(base, sim, real):
    wv = lambda rows: dict((old_term_key(r), _iv(r.get("wire_uid") or 0)) for r in rows)   # noqa: E731
    on = lambda w: w not in (0, "", "0", "None")                                       # noqa: E731
    bk, sk, rk = wv(base), wv(sim), wv(real)
    lost, gone = set(bk) - set(rk), set(bk) - set(sk)
    unw = sorted(k for k, w in bk.items() if on(w) and k not in gone and on(sk.get(k, 0)) and not on(rk.get(k, 0)))
    ru = set(k[0] for k in rk)
    bw, sw, rw = old_wire_keys(base), old_wire_keys(sim), old_wire_keys(real)
    new, lost_w, sim_new, sim_lost = rw - bw, bw - rw, sw - bw, bw - sw
    return {"td_ok": not unw and lost == gone, "unwired": unw, "lost": sorted(lost), "gone": sorted(gone),
            "recycled": sorted(k[0] for k in lost if k[0] in ru), "raw_lost": sorted(set(k[0] for k in bk) - ru),
            "d_ok": len(new) == len(sim_new) and len(lost_w) == len(sim_lost),
            "new": sorted(str(k[0]) for k in new), "lost_w": sorted(str(k[0]) for k in lost_w),
            "sim_new": sorted(str(k[0]) for k in sim_new), "sim_lost_w": sorted(str(k[0]) for k in sim_lost)}


jn = lambda x: json.loads(json.dumps(x, sort_keys=True, default=list))          # noqa: E731  tuples -> lists, as the run's json stores them
verdict = lambda t: (t["d_ok"], t["td_ok"], len(t["new"]), len(t["sim_new"]), len(t["lost_w"]), len(t["sim_lost_w"]), len(t["lost"]), len(t["unwired"]))   # noqa: E731


def load(plan_name, scratch):
    import stagexec as SX
    P = J(BENCH, plan_name)
    BASE = J(ROOT, P["finalized"]["base"]["path"])
    _p, steps = SX.load_final_plan(os.path.join(BENCH, plan_name), True)
    sp = steps[len(P["actions"])]
    L = J(sp if os.path.isabs(sp) else os.path.join(ROOT, sp))["state"]
    S = J(BENCH, scratch)
    RE = [dict(term_uid=a, owner_uid=b, term_name=c, wire_uid=d, is_source=e) for a, b, c, d, e in S["real_end_rows"]]
    OB = {}
    for e in S.get("stagexec") or []:
        for k, v in (e.get("bound") or {}).items():
            OB[int(k)] = int(v)
    return P, BASE, L, S, RE, OB


def find_md5(x, pre):
    if isinstance(x, dict):
        return any(find_md5(v, pre) for v in x.values())
    if isinstance(x, list):
        return any(find_md5(v, pre) for v in x)
    return isinstance(x, str) and x.startswith(pre)


def main():
    import stagekit as K, vigraph as V, jev_candidates as JC                     # noqa: E401  pure functions only
    md0 = dict((p, md5(p)) for p in PINS)
    gate("P0 pins before == card inputs: " + ", ".join("{0} {1}".format(os.path.basename(p), m[:8]) for p, m in md0.items()), all(md0[p].startswith(v) for p, v in PINS.items()))
    fact("stagekit md5 {0}".format(md5("tools/stagekit.py")))
    P, BASE, L, S, RE, OB = load("plan_ring_p4_s06v18.json", "diag_c147_p4s06v18_scratch.json")
    PRED = J(BENCH, "plan_ring_p4_s06v18_pred.json")
    B, SIM = BASE["terminals"], L["terminals"]

    # ---- T0: default call == pre-edit code == the run's stored verdict; today's licence file (no `renames`) -> None
    new0, old0 = K.term_identity_gates(B, SIM, RE), old_tig(B, SIM, RE)
    gate("T0 s06 default call == pre-edit code (whole dict) == explicit renames=None, bind=None == run's stored term_identity",
         new0 == old0 == K.term_identity_gates(B, SIM, RE, renames=None, bind=None) and jn(new0) == jn(S["term_identity"]), verdict(new0))
    LF = J(BENCH, "plan_ring_p4_s06v18_licence.json")
    gate("T0b today's licence file (rename_by_uid only) -> licence_renames None (today's verdicts); pb_rename_rows(.., None) returns the rows untouched",
         K.licence_renames(LF) is None and K.pb_rename_rows(B, SIM, RE, None) == (RE, [], []))

    # ---- full real rows for PB + the term binding (copied from diag_c147_b1_1_rescore.py:155-182)
    sim_by, re_by = dict((int(r["term_uid"]), r) for r in SIM), dict((int(r["term_uid"]), r) for r in RE)
    TB = dict((u, u) for u in sim_by if u in re_by)
    grp = collections.defaultdict(list)
    for r in (r for u, r in re_by.items() if u not in set(TB.values())):
        grp[(int(r["owner_uid"]), bool(r["is_source"]))].append(r)
    for r in sorted((r for u, r in sim_by.items() if u not in TB), key=lambda x: -int(x["term_uid"])):
        cand = [x for x in grp.get((OB.get(int(r["owner_uid"]), int(r["owner_uid"])), bool(r["is_source"])), []) if int(x["term_uid"]) not in set(TB.values())]
        pick = [x for x in cand if x["term_name"] == r["term_name"]] or cand
        if pick:
            TB[int(r["term_uid"])] = int(sorted(pick, key=lambda x: int(x["term_uid"]))[0]["term_uid"])
    gate("R1 every sim end row binds to one real end row", len(TB) == len(sim_by) == len(re_by) == len(set(TB.values())), (len(TB), len(sim_by), len(re_by)))
    REAL = [dict(r, term_uid=re_by[TB[u]]["term_uid"], owner_uid=re_by[TB[u]]["owner_uid"], term_name=re_by[TB[u]]["term_name"], wire_uid=re_by[TB[u]]["wire_uid"],
                 is_source=re_by[TB[u]]["is_source"]) for u, r in sim_by.items()]
    BIND = {"term": dict((k, v) for k, v in TB.items() if k != v), "obj": OB}
    LAB, FSP = JC.node_labels_default(), BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    objs = [dict(o, uid=OB.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]
    want = set((int(y["node"]), y["term"]) for y in P["open_rows"])

    def pb(ren):
        rows, restored, bad = K.pb_rename_rows(B, SIM, REAL, ren)
        cd = V.computation_diff_frame(S1f, V.build4(rows, objs, copy.deepcopy(L["loops"]), LAB, FSP, frame_keyed=True))
        rk = sorted(str(y["sink"]) for y in cd["rows"])
        ok = rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == want and not bad
        return ok, {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "restored": restored, "unlicensed": bad}

    # ---- T1 / T2: the 147-a1-8 rows under L5 / L3
    r5 = K.licence_renames(L5)
    t1 = K.term_identity_gates(B, SIM, RE, renames=r5, bind=BIND)
    p1 = pb(r5)
    gate("T1 L5 (5 renames) D PASS: new {0} == sim {1}, lost {2} == sim {3}, reuse_noted {4}, reuse_bad {5}".format(t1["d_new"], len(t1["sim_new"]), t1["d_lost"], len(t1["sim_lost_w"]),
         [n["wire"] for n in t1["reuse_noted"]], [n["wire"] for n in t1["reuse_bad"]]), t1["d_ok"] and [n["wire"] for n in t1["reuse_noted"]] == [23807])
    gate("T1 L5 TD PASS: lost {0} == gone {1}, unwired {2}, renames {3}, unlicensed {4}".format(t1["lost"], t1["gone"], t1["unwired"], len(t1["renames"]), t1["unlicensed_renames"]), t1["td_ok"])
    gate("T1 L5 PB PASS: cdiff == pred {0} rows, open pairs, no unlicensed rename".format(len(PRED["cdiff_rows"])), p1[0], p1[1])
    r3 = K.licence_renames(L3)
    t2 = K.term_identity_gates(B, SIM, RE, renames=r3, bind=BIND)
    named = sorted(x[0][0] for x in t2["unlicensed_renames"])
    gate("T2 L3 (2832/4160/4165 only) TD FAILS naming 9505/9508: td_ok {0}, unlicensed {1}".format(t2["td_ok"], t2["unlicensed_renames"]), not t2["td_ok"] and named == [9505, 9508])
    fact("T2 L3 D {0}; PB {1}".format(t2["d_ok"], pb(r3)))

    # ---- T3: w23807 keeps a sink the simulator removed (9519)
    RE3 = [dict(r, wire_uid=23807, is_source=False) if int(r["term_uid"]) == 9519 else r for r in RE]
    t3 = K.term_identity_gates(B, SIM, RE3, renames=r5, bind=BIND)
    gate("T3 w23807 keeps sink 9519 -> D FAILS: d_ok {0}, reuse_bad {1}".format(t3["d_ok"], [(n["wire"], n["real_sinks"]) for n in t3["reuse_bad"]]),
         not t3["d_ok"] and [n["wire"] for n in t3["reuse_bad"]] == [23807])
    t3b = K.term_identity_gates(B, SIM, RE3)
    fact("T3 same rows, today's call (no bind): d_ok {0} new {1}/{2} lost {3}/{4}".format(t3b["d_ok"], len(t3b["new"]), len(t3b["sim_new"]), len(t3b["lost_w"]), len(t3b["sim_lost_w"])))

    # ---- T4: a licensed uid also changes OWNER; T4b: a licensed uid under another name than the licence's `to`
    RE4 = [dict(r, owner_uid=9503) if int(r["term_uid"]) == 2832 else r for r in RE]
    t4 = K.term_identity_gates(B, SIM, RE4, renames=r5, bind=BIND)
    gate("T4 licensed 2832 changes owner 2626 -> 9503: TD FAILS (lost {0} != gone {1})".format(t4["lost"], t4["gone"]), not t4["td_ok"] and (2832, 2626) in [tuple(k) for k in t4["lost"]])
    RE4b = [dict(r, term_name="index") if int(r["term_uid"]) == 2832 else r for r in RE]
    t4b = K.term_identity_gates(B, SIM, RE4b, renames=r5, bind=BIND)
    gate("T4b licensed 2832 renamed 'array'->'index' (licence says 'element'): TD FAILS, unlicensed {0}".format(t4b["unlicensed_renames"]), not t4b["td_ok"])

    # ---- T5: s03 / s04 / s05 stored end reads, default call == pre-edit code == the run's stored verdict
    for tag, plan, scr, m in T5:
        Px, Bx, Lx, Sx, REx, OBx = load(plan, scr)
        n, o = K.term_identity_gates(Bx["terminals"], Lx["terminals"], REx), old_tig(Bx["terminals"], Lx["terminals"], REx)
        gate("T5 {0} ({1}, adopted {2} named in it: {3}) new default == pre-edit == stored run verdict {4}".format(tag, scr, m, find_md5(Sx, m), verdict(n)),
             n == o and jn(n) == jn(Sx["term_identity"]))
        x = K.term_identity_gates(Bx["terminals"], Lx["terminals"], REx, renames={}, bind={"term": {}, "obj": OBx})
        fact("T5 {0} under the new rules with an EMPTY licence + obj binding (info): D {1} TD {2} renames {3} reuse_noted {4} reuse_bad {5}".format(
            tag, x["d_ok"], x["td_ok"], x["renames"][:6], [y["wire"] for y in x["reuse_noted"]], [y["wire"] for y in x["reuse_bad"]]))

    # ---- F: stagekit format safety (copied from selftest_stagekit.py:150-163)
    path = os.path.join(ROOT, "tools", "stagekit.py")
    src = open(path, encoding="utf-8").read()
    bad = ["line {0}".format(nd.lineno) for nd in ast.walk(ast.parse(src, path)) if isinstance(nd, ast.BinOp) and isinstance(nd.op, ast.Mod)
           and isinstance(getattr(nd, "left", None), (ast.Constant, ast.JoinedStr)) and (not isinstance(nd.left, ast.Constant) or isinstance(nd.left.value, str))]
    gate("F1 stagekit builds no message with the `%` operator", not bad, bad[:3])
    gate("F2 stagekit's own source carries no bold-FAIL marker", ("*" * 2 + "FAIL" + "*" * 2) not in src.replace("`" + "*" * 2 + "FAIL" + "*" * 2 + "`", ""))
    md1 = dict((p, md5(p)) for p in PINS)
    gate("P1 pins after == before", md1 == md0)


if __name__ == "__main__":
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
