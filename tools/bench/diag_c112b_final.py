"""diag_c112b_final - card 112-2 S4 (offline, no LabVIEW): FINALIZE tools/bench/plan_l2b2a.json on graph_l2b1_20260927.json
with the finalize route check on (stagesim.simulate, the same call that made plan_l2b2a.json md5 b7ca7db6; step files back into
tools/bench/sim/l2b2/l2b2a/). Input change (diag_c112b_route.log OPEN-ROW lines): plan_l2b2a_in.json no longer declares
8634 'array' / 29625 'array' open - the sim now CLOSES both (card 112-1 T3 base-flip seeding; their own 'why' said they were
open only because stagesim reverted same-simulation flips only).
PREDICTION: FINAL True, open_rows_match True, route check PASS with 7 rows / 0 UNROUTABLE, end cdiff 54 rows.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c112b_final.log -- py -u tools/bench/diag_c112b_final.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS    # noqa: E402
import protocol          # noqa: E402

S = SS.simulate(os.path.join(HERE, "plan_l2b2a_in.json"), os.path.join(HERE, "graph_l2b1_20260927.json"),
                out_root=os.path.join(HERE, "sim", "l2b2"), plan_out_dir=HERE, route_check=True)
rc = S.get("route_check") or {}
rows = rc.get("rows") or []
print("FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"], "end rows", len(S["end_cdiff_rows"] or []))
for r in rows:
    print("ROUTE-ROW", r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"))
print("PLAN", S["plan_out"])
gates = [("FINAL and open_rows_match", S["final"] and S["open_rows_match"]),
         ("route check PASS, 7 rows, 0 UNROUTABLE", rc.get("status") == "PASS" and len(rows) == 7 and not any(r.get("unroutable") for r in rows)),
         ("end cdiff 54 rows", len(S["end_cdiff_rows"] or []) == 54)]
for g_, ok in gates:
    print("  {0}  {1}".format("PASS" if ok else "FAIL", g_))
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None),
                                                [{"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]}])))
