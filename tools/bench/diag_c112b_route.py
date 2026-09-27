"""diag_c112b_route - card 112-2 S4 (offline, no LabVIEW): re-simulate the B2a plan input on the tools with (v) the LoopTunnel
owner route and D2 uid addressing, into a SCRATCH dir (tools/bench/sim/c112b/, never the pinned plan), finalize route check
on, then print the per-row route report and the end cdiff vs the declared open rows, row by row (closed / still open).
Prior art: tools/bench/diag_c112a_b2a_route.py (same calls; its run = diag_c112a_b2a_route2.log, 1/7 routed).
PREDICTION: every one of the 7 rows routes (0 UNROUTABLE); end cdiff 54 rows; declared-open rows the sim closes = the two
flipped-inner rows (8634 'array', 29625 'array', b2_11/b2_14 unflip 9089/29923, diag_c112a_b2a_route2.log:23,26).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c112b_route.log -- py -u tools/bench/diag_c112b_route.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS    # noqa: E402
import protocol          # noqa: E402
import vigraph as V      # noqa: E402

OUT = os.path.join(HERE, "sim", "c112b")
os.makedirs(OUT, exist_ok=True)
PIN = os.path.join(HERE, "plan_l2b2a.json")
pin_md5 = SS.md5_file(PIN)
PIN_IN = os.path.join(HERE, "plan_l2b2a_in.json")
S = SS.simulate(PIN_IN, os.path.join(HERE, "graph_l2b1_20260927.json"), out_root=OUT, plan_out_dir=OUT, route_check=True)
print("FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"])
end = S["end_cdiff_rows"] or []
print("END cdiff rows", len(end))
rc = S.get("route_check") or {}
print("ROUTE-CHECK", rc.get("status"), "advisory" if rc.get("advisory") else "", str(rc.get("first_fail"))[:1500])
for r in rc.get("rows") or []:
    print("ROUTE-ROW", json.dumps(r, default=str)[:420])
end_pairs = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in end))
declared = json.load(open(PIN_IN, encoding="utf-8")).get("open_rows") or []
dp = sorted(set((int(r["node"]), r["term"]) for r in declared))
for n, t in dp:
    why = next((r.get("why", "") for r in declared if int(r["node"]) == n and r["term"] == t), "")
    print("OPEN-ROW {0:<7} {1:<36} {2}  | {3}".format(n, t, "still open" if (n, t) in end_pairs else "CLOSED by the sim",
                                                     why[:110]))
for n, t in end_pairs:
    if (n, t) not in dp:
        print("END-ROW-NOT-DECLARED", n, t)
unr = [r for r in rc.get("rows") or [] if r.get("unroutable")]
gates = [("pinned plan_l2b2a.json untouched", SS.md5_file(PIN) == pin_md5),
         ("route report lists 7 rows", len(rc.get("rows") or []) == 7),
         ("all 7 B2a rows route (0 UNROUTABLE)", len(rc.get("rows") or []) == 7 and not unr and rc.get("status") == "PASS")]
for g_, ok in gates:
    print("  {0}  {1}".format("PASS" if ok else "FAIL", g_))
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None))))
