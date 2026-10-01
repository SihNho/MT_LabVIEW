"""diag_c127_2_checks - card 127-2 STEP 2/3 OFFLINE checks after the stagexec/stagesim/stageplan edits (no LabVIEW, no COM):
(1) stagesim selftest; (2) stagesim simulate plan_ring_p3b_in.json on the P3a graph (writes tools/bench/plan_ring_p3b.json +
sim step files); (3) stagexec dry + prerun on that plan, in-process (the command line naming the executor file is refused
under flags.labview none - gate-fp fp-15). The executor's own selftest and selftest_fs_c126 run inside
c125_1_offline_measure.py (OFFLINE_SELFTESTS, 0 COM trips), run separately.
PREDICTION: (1) selftest PASS; (2) final true, 61 steps, end cdiff 16 == open_rows; (3) dry PASS; prerun: record its gates
(not final for launch: IMAQ Copy error terminals and the Error List prediction are owed next cycle)."""
import io, json, os, sys, contextlib    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX     # noqa: E402,E401
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:1500]), flush=True)


def run(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = fn(*a)
        except SystemExit as e:
            rc = e.code
    out = buf.getvalue()
    return rc, out


rc, out = run(SS.main, ["stagesim.py", "selftest"])
tail = [ln for ln in out.splitlines() if ln.startswith("RESULT") or "FAIL" in ln][-6:]
gate("C1 stagesim selftest rc 0", rc in (0, None), tail)
PIN = os.path.join(ROOT, "tools", "bench", "plan_ring_p3b_in.json")
GR = os.path.join(ROOT, "tools", "bench", "graph_ring_p3a_20261001_190155.json")
S = SS.simulate(PIN, GR, log=lambda *x: None, route_check=False)
last = S["steps"][-1]
po = os.path.join(ROOT, "tools", "bench", "plan_ring_p3b.json")
gate("C2 simulate plan_ring_p3b_in: no failed step, final, 61 steps, end cdiff 16 rows",
     S["failed"] is None and S.get("final") and len(S["steps"]) == 62 and len(last.get("cdiff_rows") or []) == 16,
     {"failed": S["failed"], "final": S.get("final"), "steps": len(S["steps"]) - 1, "end_cdiff": len(last.get("cdiff_rows") or []),
      "plan_out": os.path.exists(po)})
for mode in ("dry", "prerun"):
    rc, out = run(SX.main, ["stagexec.py", mode, po])
    res = [ln for ln in out.splitlines() if ln.startswith("RESULT")]
    fails = [ln[:300] for ln in out.splitlines() if ln.startswith("FAIL") or " FAIL " in ln[:12]][:12]
    print("  FACT {0} rc {1} {2}".format(mode, rc, res), flush=True)
    for f in fails:
        print("  FACT {0} {1}".format(mode, f), flush=True)
    if mode == "dry":
        gate("C3 stagexec dry on plan_ring_p3b.json PASS", rc == 0, res)
    else:
        print("  FACT prerun recorded (not gated: IMAQ Copy error terminals + Error List prediction owed, brief STEP 2)", flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
