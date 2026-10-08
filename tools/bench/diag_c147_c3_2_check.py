# ---
# labview: none
# hardware: none
# offline-args: --before
# evidence: tools/bench/cards/task_147-c3-2.json
# ---
r"""diag_c147_c3_2_check - card 147-c3-2 (PD356(d), PD357(e)(f)): OFFLINE checks of the s06 licence `renames` and of the build recipe's new
D / TD / PB call path on the STORED s06 retry read (tools/bench/diag_c147_p4s06v18_scratch.json). No LabVIEW, no COM call: stagekit / stagexec /
vigraph / jev_candidates / stage_prerun are imported inside main() for their PURE functions only.
PRIOR ART: tools/bench/selftest_c147_b1_2.py (T1 = the same rules with the licence typed as L5, :27, :126-161) and
tools/bench/diag_c147_b1_1_rescore.py (reconstruction of the full real rows + term binding, :154-182) - copied here; the only differences are
that the licence is READ FROM THE FILE (stagekit.licence_renames) and the calls are the recipe's (stage_d1_ring_p4_s06v18.py D/TD/PB lines).
--before: print pb_licences + licence_renames of today's file only (run before the licence edit).
PREDICTION (after the edit): C1 licence_renames(file) == the 5 measured keys {(2832|4160|4165, 2626): (array, element), (9505|9508, 9503): (Value, '')};
C2 pb_licences(plan) == {2626: licence file} (same as --before); C3 rename_by_uid unchanged; R1 binding complete; D, TD, PB PASS, unlicensed []."""
import collections, copy, hashlib, json, os, sys                                  # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCH = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
LICF = os.path.join(BENCH, "plan_ring_p4_s06v18_licence.json")
PLAN = os.path.join(BENCH, "plan_ring_p4_s06v18.json")
PINS = {"tools/stagekit.py": "06b8d844", "tools/stagexec.py": "1bab9cf9", "tools/gscript.py": "1a80236e", "tools/elrule.py": "a5ee7d5c",
        "tools/bench/memory_model.json": "88eeb037", "tools/bench/plan_ring_p4_s06v18.json": "cfbd9823",
        "tools/bench/plan_ring_p4_s06v18_pred.json": "c4a6a35a", "tools/bench/plan_ring_p4_s06v18_in.json": "db72d8af"}
WANT = {(2832, 2626): ("array", "element"), (4160, 2626): ("array", "element"), (4165, 2626): ("array", "element"),
        (9505, 9503): ("Value", ""), (9508, 9503): ("Value", "")}
OLD_RBU = [{"node": 2626, "term_uids": [2832, 4160, 4165]}]                       # rename_by_uid node / uids before the edit (licence 7dce79aa)
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def fact(s):
    print("  FACT  " + s, flush=True)


def main(before):
    import stagekit as K, stage_prerun as SP                                     # noqa: E401  pure functions only
    md0 = dict((p, md5(p)) for p in PINS)
    gate("P0 pins before: " + ", ".join("{0} {1}".format(os.path.basename(p), m[:8]) for p, m in md0.items()), all(md0[p].startswith(v) for p, v in PINS.items()))
    LF = J(LICF)
    pbl = SP.pb_licences(PLAN)
    ren = K.licence_renames(LF)
    fact("licence md5 {0}; pb_licences(plan) {1}; licence_renames {2}".format(md5(os.path.relpath(LICF, ROOT)), pbl, ren))
    gate("C2 stage_prerun.pb_licences(plan) == {2626: the licence file}", list(pbl) == [2626] and os.path.normcase(pbl[2626]).endswith("plan_ring_p4_s06v18_licence.json"), pbl)
    gate("C3 rename_by_uid node/term_uids unchanged", [{"node": e["node"], "term_uids": e["term_uids"]} for e in LF["rename_by_uid"]] == OLD_RBU, LF["rename_by_uid"])
    if before:
        return
    import py_compile                                                            # byte-compile only (fp-54: a bare py_compile command naming a recipe is refused)
    for rp in ("tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py"):
        try:
            py_compile.compile(os.path.join(ROOT, rp), doraise=True, cfile=os.path.join(os.environ.get("TEMP", BENCH), "c147c32_" + os.path.basename(rp) + "c"))
            gate("PC py_compile {0} md5 {1}".format(rp, md5(rp)), True)
        except py_compile.PyCompileError as e:
            gate("PC py_compile {0}".format(rp), False, e.msg)
    gate("C1 licence_renames(file) == exactly the 5 measured renames ({0} keys)".format(len(ren or {})), ren == WANT, ren)

    import stagexec as SX, vigraph as V, jev_candidates as JC                   # noqa: E401  pure functions only
    P = J(PLAN); BASE = J(ROOT, P["finalized"]["base"]["path"]); A = P["actions"]   # noqa: E702  == recipe :27-28
    PRED = J(BENCH, "plan_ring_p4_s06v18_pred.json")
    _p, steps = SX.load_final_plan(PLAN, True)
    sp = steps[len(A)]
    L = J(sp if os.path.isabs(sp) else os.path.join(ROOT, sp))["state"]           # == x.step(len(A))["state"]
    S = J(BENCH, "diag_c147_p4s06v18_scratch.json")
    RE = [dict(term_uid=a, owner_uid=b, term_name=c, wire_uid=d, is_source=e) for a, b, c, d, e in S["real_end_rows"]]
    OB = {}
    for e in S.get("stagexec") or []:
        for k, v in (e.get("bound") or {}).items():
            OB[int(k)] = int(v)
    B, SIM = BASE["terminals"], L["terminals"]
    # ---- full real rows + term binding (copied from selftest_c147_b1_2.py:127-140); x.bind is not stored by the run, so it is rebuilt
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
    real = [dict(r, term_uid=re_by[TB[u]]["term_uid"], owner_uid=re_by[TB[u]]["owner_uid"], term_name=re_by[TB[u]]["term_name"], wire_uid=re_by[TB[u]]["wire_uid"],
                 is_source=re_by[TB[u]]["is_source"]) for u, r in sim_by.items()]
    xbind = {"obj": OB, "term": dict((k, v) for k, v in TB.items() if k != v), "diag": {}}   # the shape of Executor.bind (stagexec.py:1931)

    # ---- the recipe's calls (stage_d1_ring_p4_s06v18.py, card 147-c3-2 lines), verbatim apart from x.bind -> xbind
    ti = K.term_identity_gates(BASE["terminals"], L["terminals"], real, renames=ren, bind={"term": xbind["term"], "obj": xbind["obj"]})
    gate("D new {0} == sim {1}; lost {2} == sim {3}; reuse_noted {4}; reuse_bad {5}".format(ti["d_new"], len(ti["sim_new"]), ti["d_lost"], len(ti["sim_lost_w"]),
         [n["wire"] for n in ti["reuse_noted"]], [n["wire"] for n in ti["reuse_bad"]]), ti["d_ok"])
    gate("TD lost {0} == gone {1}; unwired {2}; renames {3}; unlicensed {4}".format(ti["lost"], ti["gone"], ti["unwired"], ti.get("renames"), ti.get("unlicensed_renames")),
         ti["td_ok"] and ti.get("unlicensed_renames") == [])
    LAB, FSPAIRS = JC.node_labels_default(), BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
    s1p = J(JC.WIKI, JC.S1_KEY + ".json")
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    objs = [dict(o, uid=OB.get(int(o["uid"]), int(o["uid"]))) for o in L["objs"]]   # stands for be.last_objs / be.st["objs"] (rescore.py:198)
    pbr, restored, unlic = K.pb_rename_rows(BASE["terminals"], L["terminals"], real, ren)
    G1 = V.build4(pbr, objs, copy.deepcopy(L["loops"]), LAB, FSPAIRS, frame_keyed=True)
    cd = V.computation_diff_frame(S1f, G1)
    rk = sorted(str(y["sink"]) for y in cd["rows"])
    gate("PB cdiff == pred {0} rows and the plan's {1} open pairs; unlicensed == []".format(len(PRED["cdiff_rows"]), len(P["open_rows"])),
         rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == set((int(y["node"]), y["term"]) for y in P["open_rows"]) and unlic == [],
         {"extra": sorted(set(rk) - set(PRED["cdiff_rows"])), "missing": sorted(set(PRED["cdiff_rows"]) - set(rk)), "restored": restored, "unlicensed": unlic})
    md1 = dict((p, md5(p)) for p in PINS)
    gate("P1 pins after == before", md1 == md0)


if __name__ == "__main__":
    import protocol
    main("--before" in sys.argv[1:])
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
