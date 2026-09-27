"""diag_c112a_b2a_route - card 112-1 T4 (+T1/T3 effects): re-simulate the B2a plan input on the new tools, OFFLINE, into a
SCRATCH output dir (tools/bench/sim/c112a/, never tools/bench/plan_l2b2a.json, card 112-2's pinned input), with the finalize
route check on, and print the per-row route report for the 7 B2a rows. No LabVIEW.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c112a_b2a_route.log -- py -u tools/bench/diag_c112a_b2a_route.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS    # noqa: E402
import protocol          # noqa: E402

OUT = os.path.join(HERE, "sim", "c112a")
os.makedirs(OUT, exist_ok=True)
PIN = os.path.join(HERE, "plan_l2b2a.json")
pin_md5 = SS.md5_file(PIN)
S = SS.simulate(os.path.join(HERE, "plan_l2b2a_in.json"), os.path.join(HERE, "graph_l2b1_20260927.json"),
                out_root=OUT, plan_out_dir=OUT, route_check=True)
print("FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"])
print("END cdiff rows", len(S["end_cdiff_rows"] or []), "(sim of 111-5: 56)")
for st in S["steps"]:
    print("STEP", st["n"], st["op"], st.get("id"), "cdiff", len(st.get("cdiff_rows") or []),
          "unflipped", [u["term_uid"] for u in ((st.get("effect_summary") or {}).get("unflipped") or [])])
print("END ROWS", S["end_cdiff_rows"])
rc = S.get("route_check")
if rc is None:                              # not final (open rows moved): the diagnostic routability run, card 100-3 mode
    print("ROUTE-CHECK not run by finalize (plan not final); diagnostic dry with require_final=False:")
    rc = SS.route_report(S["plan_out"]["path"] if os.path.isabs(S["plan_out"]["path"]) else
                         os.path.join(os.path.dirname(os.path.dirname(HERE)), S["plan_out"]["path"]), require_final=False)
print("ROUTE-CHECK", rc.get("status"), str(rc.get("first_fail"))[:1500])
for r in rc.get("rows") or []:
    print("ROUTE-ROW", json.dumps(r, default=str)[:400])
gates = [("pinned plan_l2b2a.json untouched", SS.md5_file(PIN) == pin_md5 == "b7ca7db6f1933410331ee39d00844dfd"),
         ("route report lists 7 rows", len(rc.get("rows") or []) == 7)]
for g_, ok in gates:
    print("  {0}  {1}".format("PASS" if ok else "FAIL", g_))
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None))))
