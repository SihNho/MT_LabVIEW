"""diag_c112c_plan - card 112-3 W0 (offline, no LabVIEW): the SCRATCH plan for the T1/T2 check (reviews
archive/peer/2026-09-27-c112c-fixture.md s2 and -c112c-rows.md s5 last line: run wire_sr directly on SRB1 in a scratch copy of the bed).
Rows COPIED from tools/bench/plan_l2b2a_in.json (never re-typed): b2_10 (wire_sr RightIn into SRB1 R.inner - Void register,
Shift Registers[4] of #10170), b2_11 (wire_sr LeftIn out of SRB1 L.inner -> LoopTunnel #9087 outer), b2_15 (ctltun: CT #403 ->
case-selector Tunnel #2276 outer). Same base graph and S1 as B2a. open_rows: B2a's, then re-declared from the simulated end
(the rows b2_09/12/13/14 would close stay open in this scratch) and simulated again - the plan is final only if the end == them.
PREDICTION: route check PASS 3 rows (wire_sr:RightIn, wire_sr:LeftIn, ctltun); FINAL True on the second simulation.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c112c_plan.log -- py -u tools/bench/diag_c112c_plan.py"""
import json, os, sys                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS, protocol                                                         # noqa: E401,E402
OUT = os.path.join(HERE, "sim", "c112c")
os.makedirs(OUT, exist_ok=True)
src = json.load(open(os.path.join(HERE, "plan_l2b2a_in.json"), encoding="utf-8"))
keep = ("b2_10", "b2_11", "b2_15")
pin = dict(src, stage="c112c_bed", goal="card 112-3 W0 SCRATCH (never saved): T1 wire_sr on the EXISTING Void register SRB1 "
           "(b2_10 RightIn, b2_11 LeftIn) and T2 ctltun (b2_15) on a scratch copy of the bed; rows copied from plan_l2b2a_in.json",
           actions=[a for a in src["actions"] if a.get("id") in keep])
PIN = os.path.join(OUT, "plan_c112c_bed_in.json")
GR = os.path.join(HERE, "graph_l2b1_20260927.json")
S = None
for rnd in (1, 2):
    json.dump(pin, open(PIN, "w", encoding="utf-8"), indent=1)
    S = SS.simulate(PIN, GR, out_root=OUT, plan_out_dir=OUT, route_check=True)
    end = sorted(set(tuple(x) for x in (S.get("end_cdiff_rows") and
                                         [(SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in S["end_cdiff_rows"]] or [])))
    print("ROUND", rnd, "FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"], "end pairs", len(end),
          "declared", len(pin["open_rows"]), flush=True)
    if S["final"] or S["failed"]:
        break
    have = set((int(r["node"]), r["term"]) for r in pin["open_rows"])
    pin["open_rows"] = [r for r in pin["open_rows"] if (int(r["node"]), r["term"]) in set(end)] + \
        [{"node": n, "term": t, "why": "scratch c112c: left for B2a (closed there by b2_09/12/13/14), from the simulated end"}
         for n, t in end if (n, t) not in have]
    print("  DROPPED", sorted(have - set(end)), "ADDED", sorted(set(end) - have), flush=True)
rc = S.get("route_check") or {}
rows = rc.get("rows") or []
for r in rows:
    print("ROUTE-ROW", r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"), flush=True)
gates = [("FINAL and open_rows_match", bool(S["final"] and S["open_rows_match"])),
         ("route check PASS, 3 rows = wire_sr:RightIn, wire_sr:LeftIn, ctltun", rc.get("status") == "PASS" and len(rows) == 3
          and not any(r.get("unroutable") for r in rows))]
for g_, ok in gates:
    print("  {0}  {1}".format("PASS" if ok else "FAIL", g_), flush=True)
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None),
                                                [{"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]}])))
