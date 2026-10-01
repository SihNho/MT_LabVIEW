"""diag_c127_4_dryrow - card 127-4 FACT RECORD (no retry, no fix): the stagexec dry on plan_ring_p3b.json with its log printed, to
name the op/row behind 'BINDING: 2 new LoopTunnel objects in one op - ambiguous' (diag_c127_4_checks.log C2). Offline, no COM.
PREDICTION: FAIL at one connect_term_uid fs_border row whose crossing passes a loop border (census LoopTunnel 2)."""
import os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagexec as SX     # noqa: E402,E401
plan = os.path.join(ROOT, "tools", "bench", "plan_ring_p3b.json")
st, ff, ex = SX.dry_run(plan, log=lambda m: print("  LOG " + str(m)[:700], flush=True))
cur = getattr(ex, "cur", None)
print("  FACT status {0} | cur {1} | first_fail {2}".format(st, cur, str(ff)[:600]), flush=True)
if cur and cur.get("acts"):
    for n in cur["acts"]:
        a = ex.plan["actions"][n - 1] if hasattr(ex, "plan") else None
        print("  FACT act {0}: {1}".format(n, a), flush=True)
print(P.result_line(P.make_result(int(st == "PASS"), int(st != "PASS"), ff)), flush=True)
sys.exit(0 if st == "PASS" else 1)
