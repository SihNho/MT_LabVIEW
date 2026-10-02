r"""prep_c139_4_mkv12 - card 139-4 pass 1-2 (offline, no LabVIEW): plan_ring_p4_v12.json = plan_ring_p4_v11.json (e398c447) with
  (1) KSF1 (p4_c_stopall_f) bound to the MEASURED donor DonorBoolF_v0.vi uid 126 (PD315(a), diag_c139_3_facts.md:11-14; was uid 0 SENTINEL);
  (2) p4_t_last group given the WIRED-SOURCE tunnel form of p4_t_n1 / p4_t_pool (route 'cfw'): p4_w_last_gt (wire_sr LeftIn
      SL1L.inner -> GT2.y, the MEASURED P3a wire_sr route) is moved to just BEFORE p4_t_last, so the group's outside end
      SL1L.inner is already wired when the group runs (connect_route: wired source -> 'cfw', stagexec.py:1277-1278) instead of a
      BARE register inner face addressed as a Diagram node (UNROUTABLE, prep_c139_p2_mkv11.log:256). No other action changed.
  (3) p4_w_stop12 is NOT changed: the p4_w_or_cond form ('new:<loop>.cond' -> compile kind 'stop', OpStopFromNode_v0) exists only
      for a WhileLoop THIS plan creates - stagexec.compile_plan:719-720 (created[ds]=='while') and stagesim.cond_target:1364
      (head must be 'new:'); #10170 is a base loop, its cond row t23246 is owned by Diagram #23166 (graph row). Expressing it needs a
      tool edit (forbidden by the card) -> carried UNROUTABLE, reported.
Skeleton copied from prep_c139_p2_mkv11.py (a582a5ca; diff by id, simulate = the finalize path, compile, route compare by action-id
tuple); no tools/*.py edited. Never copies `finalized`.
PREDICTION CONTRACT:
  - inputs md5 as the card; v12 = 185 actions, same id set as v11; modified exactly {p4_c_stopall_f (donor uid 0 -> 126)}; moved
    exactly {p4_w_last_gt} (now immediately before p4_t_last); every other action identical; same meta step for both;
  - replay on the bed graph END (186 steps, no error); end cdiff == v11's 24 rows; per-step cdiff == v11 outside the moved span;
  - fs_routes regenerated, key ids == stored ids, id set == v11's;
  - compile_plan(v12) 167 ops; route compare v11 -> v12: differing ops only on p4_t_last group / p4_w_last_gt;
  - advisory route check: p4_t_last group NOT UNROUTABLE; UNROUTABLE ids == {p4_w_stop12} (carried, tool gap above).
    py tools/bgrun.py --material --max-min 12 --log tools/bench/prep_c139_4_mkv12.log -- py -u tools/bench/prep_c139_4_mkv12.py"""
import copy, hashlib, json, os, shutil, sys, traceback                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V11, G11 = os.path.join(B, "plan_ring_p4_v11.json"), os.path.join(B, "plan_ring_p4_v11_recipe_gates.json")
V12IN, V12, G12 = os.path.join(B, "plan_ring_p4_v12_in.json"), os.path.join(B, "plan_ring_p4_v12.json"), os.path.join(B, "plan_ring_p4_v12_recipe_gates.json")
META, GRAPH = os.path.join(B, "plan_ring_p4_v3_meta.json"), os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
V11SUM = os.path.join(B, "sim", "c139_p2_v11", "ring_p4_v3", "summary.json")
SIMDIR = os.path.join(B, "sim", "ring_p4_v12")
DONOR = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\DonorBoolF_v0.vi"
WANT = {V11: "e398c447c023f1fe9ae9957d39a8548e", G11: "ed85c4f819ca10084c4dca679ddc3499", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        DONOR: "2346e9d83a1caf8f29a9cc594178b247", os.path.join(B, "prep_c139_p2_mkv11.py"): "a582a5ca6fc7e6894e6d1931612e8813"}
KSF, MOVE, GRP = "p4_c_stopall_f", "p4_w_last_gt", ["p4_t_last", "p4_t_last_in", "p4_t_last_out"]
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                         # noqa: E731
sig = lambda o: json.dumps(dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act")), sort_keys=True, default=str)   # noqa: E731


def unroutable(plan):
    rc = ((plan.get("finalized") or {}).get("route_check") or {})
    return rc.get("status"), sorted(set(i for r in (rc.get("rows") or []) if r.get("unroutable") for i in (r.get("ids") or ["?acts"])))


def main():
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(ok, label, detail=""):
        G["pass" if ok else "fail"] += 1
        if not ok and G["first"] is None:
            G["first"] = label
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)

    def done(arts=()):
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], list(arts))), flush=True)
        return 0 if not G["fail"] else 1
    for p, w in WANT.items():
        gate(md5(p) == w, "input md5 " + os.path.basename(p), md5(p))
    v11 = J(V11)
    A11 = v11["actions"]
    ids11 = [a["id"] for a in A11]
    A12 = [copy.deepcopy(a) for a in A11 if a["id"] != MOVE]
    mv = copy.deepcopy(A11[ids11.index(MOVE)])
    mv["why"] = ("ROUTE wire_sr | MEASURED | wire_sr LeftIn (P3a) | card 139-4 (PD315(c)): MOVED before p4_t_last so the register inner face "
                 "SL1L.inner is WIRED when the p4_t_last group runs (group route cfw = p4_t_n1 form); PD293(c) GT2.y = last unchanged")
    A12.insert([a["id"] for a in A12].index(GRP[0]), mv)
    k = A12[[a["id"] for a in A12].index(KSF)]
    gate(k["donor"]["uid"] == 0 and k["donor"]["donor"].lower() == DONOR.lower(), "KSF1 donor in v11 = DonorBoolF_v0 uid 0 SENTINEL", k["donor"])
    k["donor"]["uid"] = 126
    k["why"] = ("ROUTE create const_donor | MEASURED donor | PD313(d)/PD240(b)(c): False constant on FS1 frame #4866 (P2b p2b_c_Num form, "
                "launched); DonorBoolF_v0.vi md5 2346e9d8 BooleanConstant uid 126 value False (card 139-3, diag_c139_3_facts.md:11-14, PD315(a))")
    gate(len(A12) == 185 and sorted(a["id"] for a in A12) == sorted(ids11), "v12 = 185 actions, id set == v11", len(A12))
    d11, d12 = dict((a["id"], a) for a in A11), dict((a["id"], a) for a in A12)
    modified = sorted(i for i in ids11 if d11[i] != d12[i])
    order12 = [a["id"] for a in A12]
    rest11, rest12 = [i for i in ids11 if i != MOVE], [i for i in order12 if i != MOVE]
    print("MOVE", MOVE, "v11 #", ids11.index(MOVE) + 1, "-> v12 #", order12.index(MOVE) + 1, "| p4_t_last v11 #", ids11.index(GRP[0]) + 1,
          "v12 #", order12.index(GRP[0]) + 1)
    gate(modified == sorted([KSF, MOVE]) and rest11 == rest12 and order12.index(MOVE) + 1 == order12.index(GRP[0]),
         "modified = {KSF1 donor, moved wire's why}; order otherwise == v11; moved wire immediately before p4_t_last", modified)
    raw = copy.deepcopy(v11)
    raw["actions"] = A12
    raw["goal"] = ("P4 v12 (card 139-4, PD315): v11 e398c447 with KSF1 bound to DonorBoolF_v0 uid 126 and p4_w_last_gt moved before the "
                   "p4_t_last group (wired-source tunnel = cfw form); p4_w_stop12 unchanged (no base-loop .cond form); never launched")
    raw.pop("finalized", None)
    raw.pop("final", None)
    json.dump(raw, open(V12IN, "w", encoding="utf-8"), indent=1, default=str)
    okv, whyv = protocol.validate_obj(J(V12IN))
    gate(okv, "v12_in validates (stageplan/1)", whyv)
    meta, stepof = J(META), {}

    def walk(o):
        if isinstance(o, dict):
            if "id" in o and "step" in o and "unit" in o:
                stepof[o["id"]] = o["step"]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(meta)
    print("META step of", MOVE, stepof.get(MOVE), "| of", GRP[0], stepof.get(GRP[0]), "| p4_w_stop12", stepof.get("p4_w_stop12"))
    gate(stepof.get(MOVE) is not None and stepof.get(MOVE) == stepof.get(GRP[0]), "moved wire and p4_t_last in the same meta step",
         (stepof.get(MOVE), stepof.get(GRP[0])))
    import stagesim as SS
    import stagexec as SX
    os.makedirs(SIMDIR, exist_ok=True)
    S = None
    try:
        S = SS.simulate(V12IN, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
    except Exception as e:
        print("SIM EXCEPTION", type(e).__name__, e)
        traceback.print_exc()
    gate(S is not None, "simulate returned")
    if S is None:
        return done()
    po = S["plan_out"]["path"]
    po = po if os.path.isabs(po) else os.path.join(ROOT, po)
    shutil.copyfile(po, V12)
    v12 = J(V12)
    gate(v12["actions"] == A12, "v12 actions == maker actions (plan_out of the finalize)")
    fr, fr11 = (v12.get("finalized") or {}).get("fs_routes") or {}, (v11.get("finalized") or {}).get("fs_routes") or {}
    bad = [(kk, r.get("id")) for kk, r in fr.items() if A12[int(kk) - 1]["id"] != r.get("id")]
    print("FS_ROUTES v12", dict((kk, (r["id"], r["how"])) for kk, r in fr.items()))
    gate(fr and not bad and sorted(r["id"] for r in fr.values()) == sorted(r["id"] for r in fr11.values()),
         "v12 fs_routes regenerated: key ids == stored ids, id set == v11's", bad)
    steps = S.get("steps") or []
    errs = [s for s in steps if s.get("error")]
    print("SIM final={0} steps={1} first stop {2}".format(S.get("final"), len(steps), (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:500]) if errs else "none (END)"))
    s11 = J(V11SUM)
    c11 = dict((s.get("id"), s.get("cdiff_rows")) for s in (s11.get("steps") or []))
    lo, hi = order12.index(MOVE) + 1, ids11.index(MOVE) + 1
    dif = [(s.get("n"), s.get("id")) for s in steps if s.get("id") in c11 and c11[s.get("id")] != s.get("cdiff_rows")]
    out = [x for x in dif if not (lo <= (x[0] or 0) <= hi)]
    print("PER-STEP cdiff differs from v11 at", len(dif), "steps (moved span", lo, "..", hi, "); outside the span", out[:10])
    for s in steps:
        if s.get("id") in [MOVE, KSF] + GRP:
            print("STEP", s.get("n"), s.get("op"), s.get("id"), "error" if s.get("error") else "ok", str(s.get("error") or s.get("effect_summary"))[:300])
    gate(not errs and len(steps) == 186, "replay END (base + 185 steps, no error)", len(steps))
    gate(not out, "per-step cdiff == v11 outside the moved span", out[:6])
    end, e11 = set(S.get("end_cdiff_rows") or []), set(s11.get("end_cdiff_rows") or [])
    gate(end == e11 and len(e11) == 24, "end cdiff rows == v11's 24", sorted(end ^ e11)[:6])
    try:
        o11, o12 = SX.compile_plan(v11), SX.compile_plan(v12)
    except SX.ExecStop as e:
        gate(False, "compile_plan v11/v12", e)
        return done()
    print("COMPILE v11", len(o11), "v12", len(o12))
    gate(len(o12) == len(o11) == 167, "compile ops v12 == v11 == 167", (len(o11), len(o12)))
    m11 = dict((tuple(A11[n - 1]["id"] for n in o["acts"]), sig(o)) for o in o11)
    m12 = dict((tuple(A12[n - 1]["id"] for n in o["acts"]), sig(o)) for o in o12)
    diffs = sorted(kk for kk in set(m11) | set(m12) if m11.get(kk) != m12.get(kk))
    other = [kk for kk in diffs if not set(kk) & set(GRP + [MOVE])]
    for kk in diffs:
        print("ROUTE-DIFF", "OTHER" if kk in other else "MOVED/GROUP", kk, "| v11", m11.get(kk), "| v12", m12.get(kk))
    gate(not other, "route compare v11->v12: differing ops only on the p4_t_last group / moved wire", other)
    st11, un11 = unroutable(v11)
    st12, un12 = unroutable(v12)
    rows = ((v12.get("finalized") or {}).get("route_check") or {}).get("rows") or []
    for r in rows:
        if set(r.get("ids") or []) & set(GRP + [MOVE, "p4_w_stop12", KSF]):
            print("ROUTE-ROW", json.dumps(r)[:400])
    print("ROUTE CHECK v11", st11, un11, "| v12", st12, un12)
    gate(not set(un12) & set(GRP), "advisory route check: p4_t_last group NOT UNROUTABLE", un12)
    gate(un12 == [], "advisory route check: 0 UNROUTABLE (card pass 2)", un12)
    g12 = J(G11)
    g12["schema_note"] = str(g12.get("schema_note", "")).replace("v11", "v12") + " | card 139-4 (PD315): KSF1 uid 126, p4_w_last_gt before p4_t_last"
    g12["plan"] = {"path": "tools/bench/plan_ring_p4_v12.json", "md5": md5(V12)}
    if isinstance(g12.get("donor_bind"), dict):
        g12["donor_bind"]["status"] = "BOUND uid 126 (DonorBoolF_v0 md5 2346e9d8, card 139-3)"
    json.dump(g12, open(G12, "w", encoding="utf-8"), indent=1)
    gate(md5(V11) == WANT[V11], "v11 not written")
    return done([{"path": "tools/bench/plan_ring_p4_v12.json", "md5": md5(V12)}, {"path": "tools/bench/plan_ring_p4_v12_in.json", "md5": md5(V12IN)},
                 {"path": "tools/bench/plan_ring_p4_v12_recipe_gates.json", "md5": md5(G12)}])


if __name__ == "__main__":
    sys.exit(main())
