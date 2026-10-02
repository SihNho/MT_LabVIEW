r"""prep_c141_1_mkv16 - card 141-1 item 3 (offline, no LabVIEW, no COM). PD322(b) + PD323(a): P4 plan v16 = FIRST the repair of the
five bed slot-write nodes that are Insert Into Array (#27928 #28916 #29048 #29265 #29316, in that order; census
tools/bench/diag_c140_4_facts.md), each replaced by a Replace Array Subset copied from claudeDev\DonorRAS1D_v0.vi uid 175
(e8a9417c, run-verified tools/bench/diag_c140_5_facts.md), its 4 terminals reconnected BY NAME to the endpoints recorded from the
bed graph graph_ring_p3b2b_20261002_133824.json (nothing re-typed); THEN v15 (eb4ffb6e) with p4_ras_bufdiff's donor -> uid 175.
EDIT ORDER per node (create-first; the end graph is PD323(a)'s): create RAS; branch its array / index / new element/subarray from
the SAME source terminals the old node reads (each source still WIRED -> stagexec.connect_route 'cfw', stagexec.py:1301-1302);
delete_wire the old output wire; delete_object the old node; wire_remove_loose_ends on each old input wire (each keeps the new
sink, so PD321's whole-wire 1055 case cannot occur); wire the new output to the old output's sink. Why not PD323(a)'s literal
order (delete_wire every input whose only sink is the node, THEN create): it leaves FlatSequenceOuterTunnel inner faces UNWIRED
(5 of the 20 endpoints: #28395 t28398, #29235 t29239, #29243 t29252, #29408 t29410, #29411 t29414); an unwired source goes to the
'nested' route (connect_nested_v1 by Diagram.Nodes[] index) and a FlatSequenceOuterTunnel is not a Node (stagexec.py:1153); the
fs_border_inner_branch route needs a WIRED face (stagexec.py:3425). Item L below simulates the literal order on #29316 as evidence.
Prior art: prep_c140_3_mkv15.py (this file's skeleton: finalize by stagesim.simulate, replay/end/per-step/compile/route-diff gates,
meta walk - copied); prep_c141_1_census*.py (the endpoints).
PREDICTION CONTRACT:
  M0 input md5 == card;  N each node: 4 rows (array, output array, index, new element/subarray) on one frame, every sink's wire has
     exactly one source, the output wire exactly one other sink;  L literal PD323(a) order on #29316 alone: route check names the
     unwired-face row UNROUTABLE (evidence only, not used);  A16 v16 = 50 repair actions + v15's 185, v15 ids identical except
     p4_ras_bufdiff.donor -> uid 175;  V v16_in validates;  S simulate returned; R replay END (236 steps);  E end cdiff rows ==
     v15's 24;  PS per-step cdiff: every v15 id == v15's, every repair step == step 0's rows;  RC route_check PASS;  C compile ALL,
     ops == v15 ops + 50;  RD route compare v15->v16 differs only on repair ids;  FR fs_routes regenerated (key ids == stored ids);
  PG X17 (stage_prerun.x17_gate) over v16 refuses ONLY p4_eq_seq (pre-existing in v15: $work donor #10171 deleted by p4_do_10171);
  MT meta16 written, every v16 id stepped;  U v15/meta15 untouched.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/prep_c141_1_mkv16.log -- py -u tools/bench/prep_c141_1_mkv16.py"""
import copy, hashlib, json, os, shutil, sys, traceback                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                 # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
V15, META15 = os.path.join(B, "plan_ring_p4_v15.json"), os.path.join(B, "plan_ring_p4_v15_meta.json")
V16IN, V16, META16 = os.path.join(B, "plan_ring_p4_v16_in.json"), os.path.join(B, "plan_ring_p4_v16.json"), os.path.join(B, "plan_ring_p4_v16_meta.json")
LITIN = os.path.join(B, "sim", "ring_p4_v16_lit", "plan_ring_p4_v16_lit_in.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
DONOR = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\DonorRAS1D_v0.vi"
SIMDIR, LITDIR = os.path.join(B, "sim", "ring_p4_v16"), os.path.join(B, "sim", "ring_p4_v16_lit")
WANT = {V15: "eb4ffb6e2a27993a372064470c1c325b", META15: "d012bd2c2d065aed1e16ddab394010e7", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        DONOR: "e8a9417ce4b75d27e8fd2f172a5dc9cd"}
NODES = [27928, 28916, 29048, 29265, 29316]                      # PD323(a), in that order
TN = ("array", "output array", "index", "new element/subarray")
IN = ("array", "index", "new element/subarray")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


def sig(o):
    return json.dumps(dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act")), sort_keys=True, default=str)


def by_ids(ops, A):
    return dict((tuple(A[n - 1]["id"] for n in o["acts"]), sig(o)) for o in ops)


gate("M0 input md5 == card (v15, meta15, bed graph, DonorRAS1D_v0)", all(md5(p) == w for p, w in WANT.items()),
     dict((os.path.basename(p), md5(p)) for p in WANT))
if G["fail"]:
    done()
gr = J(GRAPH)
T = gr["terminals"]
by_w = {}
for r in T:
    if r.get("wire_uid"):
        by_w.setdefault(int(r["wire_uid"]), []).append(r)
addr = lambda r: {"uid": int(r["owner_uid"]), "term_uid": int(r["term_uid"])}            # noqa: E731
DECL = [{"name": n, "is_source": n == "output array", "term_class": "Terminal"} for n in ("array", "output array", "index", "new element/subarray")]
REC, bad = {}, []
for n in NODES:
    rows = dict((r["term_name"], r) for r in T if r["owner_uid"] == n)
    fr = set(int(r["frame_diagram"]) for r in rows.values())
    rec = {"frame": fr.pop() if len(fr) == 1 else None, "in": {}, "in_w": {}}
    for nm in IN:
        r = rows.get(nm)
        srcs = [x for x in by_w.get(int((r or {}).get("wire_uid") or 0), []) if x["is_source"]]
        if r is None or len(srcs) != 1:
            bad.append((n, nm, "sources", len(srcs)))
            continue
        rec["in"][nm], rec["in_w"][nm] = srcs[0], int(r["wire_uid"])
    ro = rows.get("output array")
    snk = [x for x in by_w.get(int((ro or {}).get("wire_uid") or 0), []) if not x["is_source"] and x["owner_uid"] != n]
    if ro is None or len(snk) != 1:
        bad.append((n, "output array", "sinks", len(snk)))
    else:
        rec["out_w"], rec["out_dst"] = int(ro["wire_uid"]), snk[0]
    REC[n] = rec
    print("NODE #{0} frame {1} | in {2} | out w{3} -> #{4} {5} t{6}".format(
        n, rec["frame"], dict((k, (v["owner_uid"], v["owner_class"], v["term_uid"], rec["in_w"][k])) for k, v in rec["in"].items()),
        rec.get("out_w"), (rec.get("out_dst") or {}).get("owner_uid"), (rec.get("out_dst") or {}).get("owner_class"), (rec.get("out_dst") or {}).get("term_uid")))
gate("N each node: 4 named rows on one frame, one source per input wire, one other sink on the output wire", not bad
     and all(REC[n]["frame"] and len(REC[n]["in"]) == 3 for n in NODES), bad)
if G["fail"]:
    done()
CITE = ("PD322(b)/PD323(a) repair of bed #{0} (Insert Into Array, diag_c140_4_facts.md) on frame #{1}; endpoints from "
        "graph_ring_p3b2b_20261002_133824.json (prep_c141_1_census.log)")


def repair(n, k):
    R, al, fid = REC[n], "RX{0}".format(k), "p4_rp{0}".format(n)
    c = CITE.format(n, R["frame"])
    out = [{"op": "create", "id": fid + "_c", "class": "GrowableFunction", "diagram": R["frame"], "as": al, "prim": "Replace Array Subset",
            "donor": {"donor": DONOR, "uid": 175}, "terminals": copy.deepcopy(DECL),
            "why": "ROUTE create primitive | MEASURED donor | DonorRAS1D_v0.vi uid 175 label 'Replace Array Subset' run 0..19/3/99 -> len 20 "
                   "(diag_c140_5_facts.md:11-21); external-donor create_primitive_nested route as DonorErrSel #529 (P3b-1); " + c}]
    for nm, tag in (("array", "arr"), ("index", "idx"), ("new element/subarray", "new")):
        s = R["in"][nm]
        out.append({"op": "wire", "id": "{0}_{1}".format(fid, tag), "src": addr(s), "dst": "new:{0}.{1}".format(al, nm),
                    "why": "ROUTE cfw same-diagram BRANCH | {0} | source #{1} {2} t{3} is WIRED (w{4} -> old #{5}) -> connect_route "
                           "'cfw' (OpConnectFromWire_v0); same-diagram cfw branch keeps the wire (140-3 scratch op 7 p4_w_stopall_639, "
                           "diag_c140_3_facts.md:22); {6}".format("UNMEASURED (FS tunnel face source)" if s["owner_class"].endswith("Tunnel")
                                                                 else "MEASURED", s["owner_uid"], s["owner_class"], s["term_uid"],
                                                                 R["in_w"][nm], n, c)})
    out.append({"op": "delete_wire", "id": fid + "_dwo", "wire_uid": R["out_w"],
                "why": "ROUTE delete_wire | MEASURED | the old node's output wire (its only other end #{0} t{1}); delete_wire = p4_dw_23310 "
                       "(launched P2a); {2}".format(R["out_dst"]["owner_uid"], R["out_dst"]["term_uid"], c)})
    out.append({"op": "delete_object", "id": fid + "_do", "uid": n,
                "why": "ROUTE delete_object | MEASURED | old Insert Into Array #{0}; every input wire now also feeds {1} (no wire loses its "
                       "last sink, PD321); delete_object = p4_do_10171 (140-3 scratch op 3)".format(n, al)})
    for nm, tag in (("array", "arr"), ("index", "idx"), ("new element/subarray", "new")):
        out.append({"op": "wire_remove_loose_ends", "id": "{0}_rle_{1}".format(fid, tag), "wire_uid": R["in_w"][nm],
                    "why": "ROUTE wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0 on a wire that KEEPS a sink "
                           "({0}.{1}) - the P3b form (PD256(b)); PD323(a)".format(al, nm)})
    out.append({"op": "wire", "id": fid + "_out", "src": "new:{0}.output array".format(al), "dst": addr(R["out_dst"]),
                "why": "ROUTE connect same-diagram (connect_nested_v1, bare node source) | MEASURED | P3b p3b_w_*_out pattern; sink = the old "
                       "output's sink #{0} {1} t{2}; {3}".format(R["out_dst"]["owner_uid"], R["out_dst"]["owner_class"], R["out_dst"]["term_uid"], c)})
    return out


REP = [a for k, n in enumerate(NODES, 1) for a in repair(n, k)]
for a in REP:
    a["why"] = a["why"][:400]                       # stageplan/1: why <= 400 chars
v15 = J(V15)
A15 = v15["actions"]
d15 = dict((a["id"], a) for a in A15)
gate("A0 repair ids and aliases new to v15", not set(a["id"] for a in REP) & set(d15)
     and not set(a.get("as") for a in REP if a.get("as")) & set(a.get("as") for a in A15 if a.get("as")), len(REP))
# ---- L: the literal PD323(a) order on #29316 alone (evidence only)
R5 = REC[29316]
lit = [{"op": "delete_wire", "id": "L_dw_" + t, "wire_uid": R5["in_w"][nm]} for nm, t in (("array", "arr"), ("new element/subarray", "new"))]
lit += [{"op": "delete_wire", "id": "L_dwo", "wire_uid": R5["out_w"]}, {"op": "delete_object", "id": "L_do", "uid": 29316},
        {"op": "wire_remove_loose_ends", "id": "L_rle_idx", "wire_uid": R5["in_w"]["index"]},
        dict(REP[-10], id="L_c", **{"as": "RL1"})]
lit += [{"op": "wire", "id": "L_" + t, "src": addr(R5["in"][nm]), "dst": "new:RL1." + nm} for nm, t in (("array", "arr"), ("index", "idx"), ("new element/subarray", "new"))]
lit += [{"op": "wire", "id": "L_out", "src": "new:RL1.output array", "dst": addr(R5["out_dst"])}]
os.makedirs(LITDIR, exist_ok=True)
json.dump({"schema": v15["schema"], "stage": "ring_p4_v16_lit", "goal": "card 141-1 evidence: PD323(a) literal order on #29316", "context": v15.get("context"),
           "base": {"path": v15["base"]["path"], "md5": v15["base"]["md5"]}, "actions": lit}, open(LITIN, "w", encoding="utf-8"), indent=1)
try:
    SL = SS.simulate(LITIN, GRAPH, out_root=LITDIR, plan_out_dir=LITDIR, route_check=True, log=lambda m: None)
    rcl = SL.get("route_check") or {}
    print("LIT failed {0} | route {1} | first_fail {2}".format(SL.get("failed"), rcl.get("status"), str(rcl.get("first_fail"))[:400]))
    for x in rcl.get("rows") or []:
        if x.get("unroutable"):
            print("LIT UNROUTABLE", json.dumps(x, default=str)[:400])
    gate("L literal PD323(a) order on #29316: not routable (route check FAIL or sim stop) - evidence for the create-first order",
         SL.get("failed") is not None or rcl.get("status") != "PASS", {"failed": SL.get("failed"), "route": rcl.get("status")})
except Exception as e:                                                                          # noqa: BLE001
    print("LIT EXCEPTION", type(e).__name__, str(e)[:400])
    gate("L literal PD323(a) order on #29316: not routable (simulator refused)", True, "{0}: {1}".format(type(e).__name__, str(e)[:300]))
# ---- v16
A16 = copy.deepcopy(REP) + copy.deepcopy(A15)
bd = next(a for a in A16 if a["id"] == "p4_ras_bufdiff")
bd["donor"] = {"donor": DONOR, "uid": 175}
bd["why"] = ("ROUTE create primitive | MEASURED donor | card 141-1 (PD322(b)): donor DonorRAS1D_v0.vi uid 175 'Replace Array Subset' "
             "(diag_c140_5_facts.md:11-21) replaces $work #29157 = Insert Into Array (diag_c140_4_facts.md); same frame 32464")
chg = [a["id"] for a in A16[len(REP):] if a != d15[a["id"]]]
gate("A16 {0} actions = {1} repair + v15's {2}; v15 ids in order, identical except p4_ras_bufdiff".format(len(A16), len(REP), len(A15)),
     len(REP) == 50 and [a["id"] for a in A16[len(REP):]] == [a["id"] for a in A15] and chg == ["p4_ras_bufdiff"], chg)
raw = copy.deepcopy(v15)
raw["actions"] = A16
raw["base"] = {"path": v15["base"]["path"], "md5": v15["base"]["md5"]}
raw["goal"] = ("P4 v16 (card 141-1, PD322(b)(d) + PD323(a)): the 5 bed slot-write Insert Into Array nodes replaced by Replace Array Subset "
               "(DonorRAS1D_v0 uid 175) FIRST, then v15 eb4ffb6e with p4_ras_bufdiff on uid 175; fs_routes regenerated; never launched")
raw.pop("finalized", None)
raw.pop("final", None)
json.dump(raw, open(V16IN, "w", encoding="utf-8"), indent=1, default=str)
okv, whyv = protocol.validate_obj(J(V16IN))
gate("V v16_in validates (stageplan/1)", okv, whyv)
if G["fail"]:
    done()
os.makedirs(SIMDIR, exist_ok=True)
S = None
try:
    S = SS.simulate(V16IN, GRAPH, out_root=SIMDIR, plan_out_dir=SIMDIR)
except Exception as e:                                                                          # noqa: BLE001
    print("SIM EXCEPTION", type(e).__name__, e)
    traceback.print_exc()
gate("S simulate returned", S is not None)
if S is None:
    done()
po = S["plan_out"]["path"]
po = po if os.path.isabs(po) else os.path.join(ROOT, po)
shutil.copyfile(po, V16)
v16 = J(V16)
fz = v16.get("finalized") or {}
fr = fz.get("fs_routes") or {}
badr = [(k, r.get("id"), A16[int(k) - 1]["id"]) for k, r in fr.items() if A16[int(k) - 1]["id"] != r.get("id")]
print("SIM plan_out", rel(po), md5(po), "| FS_ROUTES v16", dict((k, (r["id"], r["how"])) for k, r in fr.items()))
gate("FR v16 actions == A16; fs_routes regenerated (every key's action id == stored id); base not provisional",
     v16["actions"] == A16 and bool(fr) and not badr and not (v16.get("base") or {}).get("provisional"), {"bad": badr})
steps = S.get("steps") or []
errs = [s for s in steps if s.get("error")]
print("SIM final={0} failed={1} steps={2} first stop {3}".format(S.get("final"), S.get("failed"), len(steps),
      (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:500]) if errs else "none (END)"))
gate("R replay END (base + {0} steps, no error)".format(len(A16)), not errs and len(steps) == len(A16) + 1, len(steps))
end, end15 = set(S.get("end_cdiff_rows") or []), set((v15.get("finalized") or {}).get("end_cdiff_rows") or [])
gate("E end cdiff rows == v15's ({0})".format(len(end15)), end == end15 and len(end15) == 24, sorted(end ^ end15))
s15 = J((v15.get("finalized") or {}).get("summary", {}).get("path"))
c15 = dict((s.get("id"), s.get("cdiff_rows")) for s in (s15.get("steps") or []))
row0 = steps[0].get("cdiff_rows") if steps else None
rep_ids = set(a["id"] for a in REP)
dif = [(s.get("n"), s.get("id"), len(c15.get(s.get("id")) or []), len(s.get("cdiff_rows") or [])) for s in steps[1:]
       if (s.get("id") in rep_ids and s.get("cdiff_rows") != row0) or (s.get("id") in c15 and c15[s.get("id")] != s.get("cdiff_rows"))]
gate("PS per-step cdiff: every v15 id == v15's; every repair step == step 0's rows ({0})".format(len(row0 or [])), not dif, dif[:6])
rc = fz.get("route_check") or {}
print("FINALIZED final", v16.get("final"), "open_rows_match", fz.get("open_rows_match"), "route_check", rc.get("status"), str(rc.get("first_fail"))[:300])
for x in rc.get("rows") or []:
    if x.get("id") in rep_ids or (isinstance(x.get("ids"), list) and set(x["ids"]) & rep_ids):
        print("ROUTE-REPAIR", json.dumps(x, default=str)[:260])
gate("RC route_check PASS", rc.get("status") == "PASS", rc.get("first_fail"))
try:
    o15, o16 = SX.compile_plan(v15), SX.compile_plan(v16)
except SX.ExecStop as e:
    gate("C compile_plan v15/v16", False, e)
    done()
m15, m16 = by_ids(o15, A15), by_ids(o16, A16)
diffs = sorted(set(k for k in set(m15) | set(m16) if m15.get(k) != m16.get(k)))
other = [k for k in diffs if not set(k) & rep_ids]
for k in diffs:
    if k in other:
        print("ROUTE-DIFF OTHER", k, "| v15", m15.get(k), "| v16", m16.get(k))
gate("C compile ALL: v16 ops ({0}) == v15 ops ({1}) + {2}; every action compiled once".format(len(o16), len(o15), len(REP)),
     len(o16) == len(o15) + len(REP) and sorted(n for o in o16 for n in o["acts"]) == list(range(1, len(A16) + 1)), (len(o15), len(o16)))
gate("RD route compare v15->v16: every differing route holds a repair id", not other, other[:6])
print("COMPILE repair kinds", [(o["kind"], o.get("route")) for o in o16[:len(REP)]][:12])
okp, detp = SPR.x17_gate([v16])
ids_p = sorted(x["action"] for x in (detp if isinstance(detp, list) else []))
gate("PG X17 over v16 refuses ONLY p4_eq_seq (pre-existing: $work donor #10171 deleted by p4_do_10171); the 5 repairs + bufdiff pass",
     ids_p == ["p4_eq_seq"], detp)
meta = J(META15)
mrep = [{"id": a["id"], "group": "R0 slot-write repair (PD322(b)/PD323(a))", "unit": "U00 repair #{0}".format(a["id"].split("_")[1][2:]),
         "xkind": a["op"] if a["op"] != "wire" else ("cfw" if isinstance(a["src"], dict) else "connect"), "route_level": "MEASURED",
         "level": "UNMEASURED" if a["op"] == "wire" and isinstance(a["src"], dict) and "UNMEASURED" in a["why"] else "MEASURED",
         "measured_by": None, "cite": a["why"][:300] + " [v16]", "step": 1, "session": "R"} for a in REP]
meta16 = copy.deepcopy(meta)
meta16["actions"] = mrep + meta["actions"]
meta16["recut_c141_1"] = {"from_md5": md5(META15), "plan": "plan_ring_p4_v16.json", "added_first": [a["id"] for a in REP],
                          "changed": ["p4_ras_bufdiff (donor -> DonorRAS1D_v0 uid 175)"],
                          "why": "PD322(b)/PD323(a): the 5 Insert Into Array slot writes replaced by Replace Array Subset; session cut by X10 (PD319(b))"}
json.dump(meta16, open(META16, "w", encoding="utf-8"), indent=1)
st = {}


def walk(o):
    if isinstance(o, dict):
        if "id" in o and "step" in o and "unit" in o:
            st[o["id"]] = (o["step"], o.get("session"))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(J(META16))
gate("MT meta16: every v16 id stepped", all(a["id"] in st for a in A16), [a["id"] for a in A16 if a["id"] not in st][:6])
gate("U v15 / meta15 untouched", md5(V15) == WANT[V15] and md5(META15) == WANT[META15])
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (V16, V16IN, META16))
print("V16 actions {0} ops {1} repair {2}".format(len(A16), len(o16), len(REP)))
done()
