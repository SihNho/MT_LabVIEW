# ---
# labview: none
# hardware: none
# ---
r"""selftest_rebind_c150 - card 150-a2-1 (PD365(c), docs/d1/ring-p4c.md:254-283; cause tools/bench/diag_c150_a1_3_facts.md). OFFLINE.
rebind keyed an OLD terminal by (uid, owner, NAME) (stage_prerun.py:3829 @dcd45aba): s06's renamed old terminals (#2626 t2832/t4160/t4165 'array'->
'element'; #9503 t9505/t9508 'Value'->'') fell into real_new, s07 rebase refused (BINDING). Reuses stage_prerun._terms/load_creation_map/plan_named_uids/
rebind (rebase()'s calls). "Old code" = `git show HEAD:tools/stage_prerun.py` (dcd45aba) exec'd IN MEMORY. Writes only selftest_rebind_c150_pre.json (pre).
PREDICTION CONTRACT  --phase pre: R0 HEAD blob dcd45aba; R1 old AND current refuse with BINDING 'BuildArray x0 simulated vs x1 real' + 'LoopTunnel x2
  simulated vs x3 real'; R3 class/direction change refuses; R4 s05->s06 binds, map_nodes == prep_c147_a1_3_rebase.log:4 -> recorded.
  --phase post: R0; R1 old refuses, new binds; R2 renamed_old == the 5 renames; R3a class change of t2813 refuses; R3b (150-a2-2) direction flip of OLD
  t2813 = flipped_old, not a refusal; R4 map_nodes AND M == pre record; prints s06->s07 flipped_old count (3). R5 (card 150-a2-4; post on the working
  file, or alone with --r5-file <py>): in the function holding the 'FLIPPED-OLD ' log string no Store of `b` (for target/assignment; comprehensions
  excluded) lies between the base assignment and the last read of `b` - FAILS on 6208b7b7 (:4303/:4305), passes after the rename.
  py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_rebind_c150_<phase>.log -- py -u tools/bench/selftest_rebind_c150.py --phase <phase>"""
import ast, copy, hashlib, json, os, subprocess, sys, traceback, types                    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP                                                  # noqa: E401,E402
PHASE = sys.argv[sys.argv.index("--phase") + 1] if "--phase" in sys.argv else "post"
R5F = sys.argv[sys.argv.index("--r5-file") + 1] if "--r5-file" in sys.argv else None
PRE = os.path.join(B, "selftest_rebind_c150_pre.json")
S07 = os.path.join(B, "plan_ring_p4_s07v18_prov148.json")
G6 = os.path.join(B, "graph_ring_p4s06_20261008_192149.json")
S06IN = os.path.join(B, "plan_ring_p4_s06v18_in.json")
G5 = os.path.join(B, "graph_ring_p4s05_20261008_013759.json")
MAP4 = {-32: 30240, -30: 30239, -25: 30216, -23: 30215, -18: 30119, -16: 30116, -6: 30194, -1: 30179}   # prep_c147_a1_3_rebase.log:4
REN = {(2832, 2626, "array", "element"), (4160, 2626, "array", "element"), (4165, 2626, "array", "element"),
       (9505, 9503, "Value", ""), (9508, 9503, "Value", "")}
BIND1 = ("BuildArray x0 simulated vs x1 real", "LoopTunnel x2 simulated vs x3 real")
G = {"p": 0, "f": 0, "first": None}
ab = lambda p: p if os.path.isabs(p) else os.path.join(R, p)                              # noqa: E731

def gate(name, ok, val=""):
    G["p" if ok else "f"] += 1
    G["first"] = G["first"] or (None if ok else name)
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:700]), flush=True)

def inputs(mod, plan_path, graph_path):
    """rebase()'s own loading (stage_prerun.py:4260-4286), nothing written."""
    plan = json.load(open(plan_path, encoding="utf-8"))
    b = plan["base"]; so = b["sim_of"]                                                    # noqa: E702
    dn = json.load(open(ab(so["plan"]), encoding="utf-8"))
    bn = (dn.get("finalized") or {}).get("base") or dn.get("base")
    (gb, before), (gp, prov), (gr, real) = mod._terms(ab(bn["path"])), mod._terms(ab(b["path"])), mod._terms(graph_path)
    cmap, cwhy, cmeta = mod.load_creation_map(so, gr, log=lambda s: print("  CMAP " + str(s)[:300], flush=True))
    print("  IN {0}: sim_of md5 ok {1}; cmap {2}".format(os.path.basename(plan_path), hashlib.md5(open(ab(so["plan"]), "rb").read())
          .hexdigest() == so.get("md5"), cmeta.get("path") if cmap else cwhy), flush=True)
    return dict(before=before, prov=prov, real=real, prov_doc=gp, real_doc=gr, before_doc=gb, named=mod.plan_named_uids(plan), cmap=cmap)

def run(mod, k, real=None):
    info, kw = {}, dict(k, real=real if real is not None else k["real"])
    M, why = mod.rebind(kw.pop("before"), kw.pop("prov"), kw.pop("real"), info=info, **kw)
    return M, why, info

def r5(path):
    """(function, line of the first Store of b, line of the last Load of b, [rebinding Store lines in between]) - static, nothing run."""
    fn = next(n for n in ast.walk(ast.parse(open(path, encoding="utf-8").read())) if isinstance(n, ast.FunctionDef) and any(
        isinstance(c, ast.Constant) and str(c.value).startswith("FLIPPED-OLD ") for c in ast.walk(n)))
    comp = set(id(x) for c in ast.walk(fn) if isinstance(c, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) for x in ast.walk(c))
    nb = [x for x in ast.walk(fn) if isinstance(x, ast.Name) and x.id == "b" and id(x) not in comp]
    st, ld = sorted(x.lineno for x in nb if isinstance(x.ctx, ast.Store)), max(x.lineno for x in nb if isinstance(x.ctx, ast.Load))
    return fn.name, st[0], ld, [ln for ln in st[1:] if ln < ld]

def done():
    print("COUNT phase {0}: pass {1} fail {2}".format("r5-file" if R5F else PHASE, G["p"], G["f"]), flush=True)
    print(P.result_line(P.make_result(G["p"], G["f"], G["first"], [])), flush=True)
    os._exit(0 if not G["f"] else 1)

try:
    if PHASE == "post" or R5F:
        p5 = ab(R5F) if R5F else SP.__file__; fn5, l0, l1, bad = r5(p5)                     # noqa: E702
        gate("R5 {0} (md5 {1}): no rebind of `b` between :{2} and its last read :{3}".format(fn5, hashlib.md5(open(p5, "rb").read())
             .hexdigest()[:8], l0, l1), not bad, "rebinding lines {0}".format(bad))
    if R5F: done()                                                                       # noqa: E701
    src = subprocess.run(["git", "show", "HEAD:tools/stage_prerun.py"], cwd=R, capture_output=True, check=True).stdout
    gate("R0 HEAD blob of stage_prerun.py is dcd45aba", hashlib.md5(src).hexdigest() == "dcd45aba9be99dde809800e7f59bb2f7",
         hashlib.md5(src).hexdigest())
    OLD = types.ModuleType("sp_old_c150"); OLD.__file__ = os.path.join(R, "tools", "stage_prerun.py"); sys.modules["sp_old_c150"] = OLD  # noqa
    exec(compile(src, OLD.__file__, "exec"), OLD.__dict__)
    print("  PHASE {0}; working stage_prerun md5 {1}".format(PHASE, hashlib.md5(open(SP.__file__, "rb").read()).hexdigest()), flush=True)
    k1o, k1n = inputs(OLD, S07, G6), inputs(SP, S07, G6)
    (Mo, whyo, _io), (Mn, whyn, i1) = run(OLD, k1o), run(SP, k1n)
    old_ref = Mo is None and "BINDING" in str(whyo) and all(s in str(whyo) for s in BIND1)
    gate("R1 old code refuses with BINDING (BuildArray x0/x1, LoopTunnel x2/x3)", old_ref, whyo)
    if PHASE == "pre":
        gate("R1 current (unedited) code refuses identically", Mn is None and whyn == whyo, whyn)
    else:
        gate("R1 new code binds s07 onto the real s06", Mn is not None, (whyn, i1.get("map_nodes")))
        got = set(tuple(x) for x in i1.get("renamed_old") or [])
        gate("R2 info['renamed_old'] == the 5 measured renames", got == REN, sorted(got))
        print("  FLIPPED-OLD s06->s07 count {0}: {1}".format(len(i1.get("flipped_old") or []), i1.get("flipped_old")), flush=True)
    for lab, fld, val in (("class", "term_class", "XClassC150"), ("direction", "is_source", None)):
        rr = copy.deepcopy(k1n["real"])
        hit = [r for r in rr if r["term_uid"] == 2813 and r.get("owner_uid") == 2626]
        for r in hit: r[fld] = (not r[fld]) if val is None else val                           # noqa: E701
        M3, why3, i3 = run(SP, k1n, real=rr)
        if lab == "class" or PHASE == "pre":
            gate("R3a {0} change of old t2813 at the same (uid, owner #2626) refuses".format(lab), len(hit) >= 1 and M3 is None, why3)
        else:
            fo = [tuple(x)[:2] for x in i3.get("flipped_old") or []]
            gate("R3b direction flip of old non-tunnel t2813 (#2626 BuildArray) = flipped_old info, not a refusal",
                 len(hit) >= 1 and M3 is not None and (2813, 2626) in fo, (why3, fo))
    M4, why4, i4 = run(SP, inputs(SP, S06IN, G5))
    mn = dict((int(a), int(b)) for a, b in (i4.get("map_nodes") or {}).items())
    Mj = sorted((int(a), int(b)) for a, b in (M4 or {}).items())
    if PHASE == "pre":
        Mo4, _w, io4 = run(OLD, inputs(OLD, S06IN, G5))
        gate("R4 s05->s06 binds, map_nodes == prep_c147_a1_3_rebase.log:4 (recorded)", M4 is not None and mn == MAP4 and
             sorted((Mo4 or {}).items()) == Mj, (why4, mn))
        json.dump({"map_nodes": sorted(mn.items()), "M": Mj, "why": why4}, open(PRE, "w", encoding="utf-8"))
    else:
        pre = json.load(open(PRE, encoding="utf-8"))
        same = M4 is not None and [list(x) for x in sorted(mn.items())] == pre["map_nodes"] and [list(x) for x in Mj] == pre["M"]
        gate("R4 s05->s06 new map_nodes AND M == pre-edit record", same and mn == MAP4, (len(Mj), len(pre["M"]), mn))
        print("  R4 renamed_old {0}".format(i4.get("renamed_old")), flush=True)
except Exception as e:                                                                      # noqa: BLE001
    traceback.print_exc(); gate("selftest ran", False, repr(e))                              # noqa: E702
done()
