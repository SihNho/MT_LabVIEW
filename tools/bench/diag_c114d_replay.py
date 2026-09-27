"""card 114-3 C3/C5 - OFFLINE replay of finalized stage plans through tools/stagesim.py (no LabVIEW, no COM).

    py tools/bench/diag_c114d_replay.py <tag>

For each plan: simulate(plan, its base graph) into tools/bench/sim/c114d_<tag>/<stage>/ (plan_out_dir the same folder,
so tools/bench/plan_<stage>.json is NEVER overwritten), then print final / failed / end rows / open_rows_match / route
check and the wire-uid delta the launch gate D computes (stage_d1_l2b3.py:56: new = wires(last) - wires(base), lost =
wires(base) - wires(last)), plus every step effect that re-created a source wire.

Prediction contract (after the 114-3 change): l2b3 -> final True, 6 new, lost [5174, 5336, 28392] (= the real launch
log's D line, stage_d1_l2b3.log:103); l2b2a / l2b2b -> same final / route verdict as the 'pre' run.
Existed first: stagesim.simulate / main (used, not edited here); stage_d1_l2b3.py wires() (re-stated: 3 lines).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS          # noqa: E402
import protocol                # noqa: E402

PLANS = ["tools/bench/plan_l2b3.json", "tools/bench/plan_l2b2b.json", "tools/bench/plan_l2b2a.json"]


def wires(T):
    return set(int(r["wire_uid"]) for r in T if r["wire_uid"])


def main(tag):
    out = os.path.join(ROOT, "tools", "bench", "sim", "c114d_" + tag)
    os.makedirs(out, exist_ok=True)
    npass, nfail, first, res = 0, 0, None, {}
    for rp in PLANS:
        p = os.path.join(ROOT, rp)
        plan = json.load(open(p, encoding="utf-8"))
        gp = os.path.join(ROOT, plan["base"]["path"])
        try:
            S = SS.simulate(p, gp, out_root=out, plan_out_dir=out, log=lambda *_a: None)
        except Exception as e:                                                        # noqa: BLE001
            print("REPLAY {0}: EXCEPTION {1}: {2}".format(rp, type(e).__name__, e))
            nfail += 1
            first = first or rp
            continue
        base = SS.base_state(json.load(open(gp, encoding="utf-8")), plan.get("context"))
        last = S["_state"]
        new, lost = wires(last["terminals"]) - wires(base["terminals"]), wires(base["terminals"]) - wires(last["terminals"])
        rec = []
        for s in S["steps"][1:]:
            eff = json.load(open(s["file"]["path"], encoding="utf-8"))["effect"] or {}
            if eff.get("recreated_from"):
                rec.append((s["n"], s.get("id"), eff.get("recreated_from"), eff.get("wire"), eff.get("rewired")))
        rc = (S.get("route_check") or {}).get("status")
        r = {"final": S["final"], "failed": S["failed"], "n_end_rows": len(S["end_cdiff_rows"] or []),
             "open_rows_match": S["open_rows_match"], "route_check": rc, "n_new": len(new), "lost": sorted(lost),
             "model_wire": next((s.get("model_source") for s in S["steps"][1:] if s["op"] == "wire"), None)}
        res[rp] = r
        print("REPLAY {0}: {1}".format(rp, json.dumps(r, default=str)))
        for x in rec:
            print("  RECREATED step {0} {1}: old w{2} -> w{3}, other terminals re-wired {4}".format(*x))
        npass += 1
    with open(os.path.join(out, "replay_summary.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    print(protocol.result_line(protocol.make_result(npass, nfail, first)))
    return 0 if not nfail else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "run"))
