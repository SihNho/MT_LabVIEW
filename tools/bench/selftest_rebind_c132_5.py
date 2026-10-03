r"""selftest_rebind_c132_5 - card 132-5 (PD278(c), docs/d1/ring-p3b.md:87-91): stage_prerun.rebind by CONNECTIVITY, names
logged, on the REAL P3b-1 graph (graph_ring_p3b1_20261002_073225.json) vs the provisional base of plan_ring_p3b2.json.
Offline; the real plan file is never written (copies under %TEMP%). Prior art: stagexec.bind_new / bind_fs_tunnel (per-op
runtime binding, name-keyed for primitives) - not reusable here because the rebase binds a whole stage at once.
PREDICTION:
  B1 every created sim node binds; FSIT -42 -> 28333, Unbundler -27 -> 6814, Select -32 -> 10579 (diag_c132_5_rows.log)
  B2 Unbundler status: -29 (the sim output wired to Select 's') binds BY CONNECTIVITY to 28082 'status', and 28082's
     real wire reaches Select 10579
  B3 frames -2/-3/-4 -> 27641/32464/27722 (diag_c132_5_frames.log), -2 by elimination (f0 has no rows)
  B4 label diffs are LOGGED for FSIT ('' vs 'error out') and Unbundler ('element' vs status/code/source), not keyed
  B5 rebase(simulate=False) of a copy of plan_ring_p3b2.json PASSES: diagrams -2/-3/-4 remapped, no unbound uid
  B6 a plan reference to the ambiguous name address {-27, 'element'} REFUSES
  B7 a plan reference to term_uid -30 (bound by position only) REFUSES; one to -29 (connectivity) passes -> 28082
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_rebind_c132_5.log -- py -u tools/bench/selftest_rebind_c132_5.py"""
import json, os, sys, shutil, tempfile                                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP                                           # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
NP, NF = [0], [None]


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:400]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


PLAN = "tools/bench/plan_ring_p3b2.json"
GRAPH = os.path.join(R, "tools/bench/graph_ring_p3b1_20261002_073225.json")
plan = J(PLAN)
if not (plan.get("base") or {}).get("sim_of"):        # card 142-5: plan_ring_p3b2.json was rebased in 133-3 (no sim_of since);
    PLAN = "tools/bench/plan_ring_p3b2_in.json"         # its provisional stage input holds the same 39 actions (selftest_rebase_c133_3 T4)
    plan = J(PLAN)
pv = J(plan["base"]["path"])
pn = J(plan["base"]["sim_of"]["plan"])
bn = (pn.get("finalized") or {}).get("base") or pn.get("base")
bf = J(bn["path"])
rl = J("tools/bench/graph_ring_p3b1_20261002_073225.json")
print("  FACT  before {0}; prov {1}; real {2}".format(bn["path"], plan["base"]["path"], rel := os.path.basename(GRAPH)), flush=True)
info = {}
M, why = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf, info=info)
print("  FACT  why={0} nodes={1} modes={2}".format(why, len(info.get("nodes", {})),
      dict(__import__("collections").Counter(info.get("mode", {}).values()))), flush=True)
N = info.get("nodes", {})
gate("B1 every created node binds; FSIT/Unbundler/Select as measured", M is not None and N.get(-42) == 28333
     and N.get(-27) == 6814 and N.get(-32) == 10579, (why, N.get(-42), N.get(-27), N.get(-32), len(N)))
rr = dict((r["term_uid"], r) for r in rl["terminals"])
w = rr.get(28082, {}).get("wire_uid")
sel = [r["owner_uid"] for r in rl["terminals"] if r.get("wire_uid") == w and r["term_uid"] != 28082]
gate("B2 Unbundler status: -29 -> 28082 'status' by connectivity, wired to Select 10579", M is not None and M.get(-29) == 28082
     and info["mode"].get(-29) == "conn" and rr[28082]["term_name"] == "status" and sel == [10579],
     (M and M.get(-29), info.get("mode", {}).get(-29), sel))
gate("B3 frames -2/-3/-4 -> 27641/32464/27722 (-2 by elimination)", M is not None and [M.get(f) for f in (-2, -3, -4)] ==
     [27641, 32464, 27722] and "elimination" not in str(info["how_frame"].get(-3)) and "left" in str(info["how_frame"].get(-2)),
     ([M and M.get(f) for f in (-2, -3, -4)], info.get("how_frame")))
lab = info.get("labels", [])
for x in lab:
    print("  FACT  LABEL-DIFF {0}".format(x), flush=True)
gate("B4 label diffs logged for FSIT and Unbundler only", set(x[2] for x in lab) == {"FlatSequenceInnerTunnel", "Unbundler"},
     sorted(set(x[2] for x in lab)))
tmp = tempfile.mkdtemp(prefix="c132_5_rebind_")
try:
    def try_plan(extra):
        p = json.loads(json.dumps(plan))
        p["actions"] = list(p["actions"]) + extra
        pp = os.path.join(tmp, "plan_ring_p3b2_t.json")
        json.dump(p, open(pp, "w", encoding="utf-8"), indent=1)
        ok, det = SP.rebase(pp, GRAPH, log=lambda s: print("  LOG   " + s, flush=True), simulate=False)
        return ok, det, json.load(open(pp, encoding="utf-8"))
    ok, det, new = try_plan([])
    dg = sorted(set(a.get("diagram") for a in new["actions"] if "diagram" in a))
    gate("B5 rebase(simulate=False) of a copy PASSES, diagrams remapped", ok and not [d for d in dg if isinstance(d, int) and d < 0],
         (det, dg))
    ok, det, _ = try_plan([{"op": "wire", "src": {"uid": -27, "term": "element"}, "dst": {"uid": -32, "term": "s"}}])
    gate("B6 ambiguous name address {-27,'element'} REFUSES", not ok and "does not bind uniquely" in det, det)
    ok, det, _ = try_plan([{"op": "wire", "src": {"uid": -27, "term_uid": -30}, "dst": {"uid": -32, "term": "s"}}])
    ok2, det2, new2 = try_plan([{"op": "wire", "src": {"uid": -27, "term_uid": -29}, "dst": {"uid": 10579, "term": "s"}}])
    gate("B7 term_uid -30 (position) REFUSES; -29 (connectivity) -> 28082", not ok and "not bound by connectivity" in det and ok2
         and new2["actions"][-1]["src"] == {"uid": 6814, "term_uid": 28082}, (det, det2[:120], new2["actions"][-1]["src"]))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
NT = 7
print(P.result_line(P.make_result(NP[0], NT - NP[0], NF[0])), flush=True)
sys.stdout.flush()
os._exit(0 if NP[0] == NT else 1)
