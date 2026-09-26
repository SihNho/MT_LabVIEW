r"""diag_c100_6_parity - card 100-6, the review archive/peer/2026-09-26-c100-6-parity.md section 4 "cheapest test",
OFFLINE (no LabVIEW). The real Nodes[] listing of the touched diagrams is REBUILT from the failed run's parity rows
(tools/bench/stage_d1_disp.json stagexec[0].parity): real = SimReader(plan context) listing U only_real - only_sim.
Then SimReader is rebuilt on par1359_95_graph.json under three contexts and compared with it (reader_parity's own
listing): V0 the plan's context (must reproduce the run: 18 real-only); V1 + context.loops =
graph_loops_s1_20260924.json (md5 3e3d23ce = S1); V2 V1 + context.owners = sim/l2a1/graph_k_80_owners.json (D1_k's map,
a STAND-IN - S1 uids are not verified in it). Reported per variant: real-only / sim-only per diagram. PREDICTION gated:
V0 reproduces the run's 18. The V1/V2 numbers are facts for judgement, not gates.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c100_6_parity.log -- py -u tools/bench/diag_c100_6_parity.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P      # noqa: E402
import stagesim as SS     # noqa: E402
import stagexec as SX     # noqa: E402

J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))            # noqa: E731
plan = J("tools/bench/sim/disp/plan_disp.json")
base = J(plan["finalized"]["base"]["path"])
par = J("tools/bench/stage_d1_disp.json")["stagexec"][0]["parity"]
gates, out = [], {}


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def reader(ctx):
    st = SS.base_state(base, ctx)
    return SX.SimReader(SX._StateHolder(st)), SX.classes_of(st["terminals"], st.get("objs")), st


r0, c0, _s0 = reader(plan.get("context"))
REAL = {}
for row in par["rows"]:
    d = row["diagram"]
    REAL[d] = ((SX.listing(r0, d, c0) or set()) | set(tuple(x) for x in row["only_real"])) - set(tuple(x) for x in row["only_sim"])
    print("  FACT real listing rebuilt: D{0} n {1} (run n_real {2})".format(d, len(REAL[d]), row["n_real"]), flush=True)
VARS = (("V0 plan context", plan.get("context")),
        ("V1 + loops S1", dict(plan.get("context") or {}, loops={"path": "tools/bench/graph_loops_s1_20260924.json"})),
        ("V2 + loops S1 + owners D1_k", dict(plan.get("context") or {}, loops={"path": "tools/bench/graph_loops_s1_20260924.json"},
                                             owners={"path": "tools/bench/sim/l2a1/graph_k_80_owners.json"})))
for name, ctx in VARS:
    rd, cl, st = reader(ctx)
    res, tot = {}, 0
    for d in sorted(REAL):
        S = SX.listing(rd, d, cl) or set()
        ru = set(u for _c, u in REAL[d])
        su = set(u for _c, u in S)
        res[d] = {"only_real": sorted(ru - su), "only_sim": sorted(su - ru)}
        tot += len(ru - su) + len(su - ru)
    out[name] = {"total": tot, "per_diagram": res, "loops": len(st.get("loops") or []), "owners": len(st.get("owners") or {})}
    print("  FACT {0}: one-side-only (by uid) {1}; loops {2} owners {3}; {4}".format(
        name, tot, out[name]["loops"], out[name]["owners"], json.dumps(res)), flush=True)
gate("V0 reproduces the failed run's 18 real-only entries", out["V0 plan context"]["total"] == par["n"] == 18,
     (out["V0 plan context"]["total"], par["n"]))
fp = os.path.join(HERE, "facts_c100_parity.json")
json.dump(out, open(fp, "w", encoding="utf-8"), indent=1, default=str)
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
print(P.result_line(P.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(fp, ROOT), "md5": SS.md5_file(fp)}])), flush=True)
sys.exit(0 if ff is None else 1)
