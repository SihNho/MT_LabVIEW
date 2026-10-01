r"""selftest_x10_c132_1 - card 132-1 (PD275(a)(b)) self-test of X10's FINAL-READ term. OFFLINE, no LabVIEW, no COM.
PRIOR ART: selftest_x10_c130_1.py (X10 model T1-T5; its T1/T2 peaks re-pinned +17.4 by this card), stage_prerun.x10_probe/x10_gate.
PREDICTION: T1 tools/recipes/stage_d1_ring_p3b1.py (the bytes launched cycle 131) -> one run, predicted peak within 3 MB of the
launch's measured 680.4 (stage_d1_ring_p3b1.log:430), X10 PASS (<= 690); T2 memory_model final_read_mb == 17.4 (the measured
d, stage_d1_ring_p3b1_scratch_pin4.log:447) and fail_above_mb == 690 (PD275(b)); T3 stage_d1_ring_p3b2.py (provisional plan):
its prediction is PRINTED (a measurement, not a gate) - it passes T3 when X10 returns a run at all.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c132_1.log -- py -u tools/bench/selftest_x10_c132_1.py"""
import os, re, sys                                                                   # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                           # noqa: E401,E402
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def measured(log, line_no):
    """the private MB of the METER read line at log:line_no (read from the file, never typed)."""
    ln = open(os.path.join(B, log), encoding="utf-8", errors="replace").read().splitlines()[line_no - 1]
    m = re.search(r"METER read\s+k\s+\d+\s+private ([\d.]+) MB \(d \+([\d.]+)\)", ln)
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)


def x10(path):
    ex = SP.x10_probe(path)
    return SP.x10_gate(path, ex)


launch_mb, _d = measured("stage_d1_ring_p3b1.log", 430)
pin4_mb, pin4_d = measured("stage_d1_ring_p3b1_scratch_pin4.log", 447)
ok, det = x10(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b1.py"))
runs = det.get("runs") or []
gate("T1 stage_d1_ring_p3b1.py: X10 PASS, predicted {0} within 3 MB of the launch's measured {1}".format(
    runs[0]["peak_mb"] if runs else None, launch_mb),
    ok is True and len(runs) == 1 and launch_mb is not None and abs(runs[0]["peak_mb"] - launch_mb) <= 3.0,
    [dict((k, r[k]) for k in ("N", "bind", "R", "peak_mb", "fail_above_mb")) for r in runs] or det)
m = SP.load_memory_model()
gate("T2 memory_model final_read_mb == measured pin4 d {0}; fail_above_mb 690".format(pin4_d),
     m["final_read_mb"]["value"] == pin4_d and m["fail_above_mb"]["value"] == 690.0,
     (m["final_read_mb"]["value"], m["fail_above_mb"]["value"], pin4_mb))
ok, det = x10(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2.py"))
runs = det.get("runs") or []
print("  FACT  X10 P3b-2 (provisional plan): ok {0}, runs {1}, why {2}".format(
    ok, [dict((k, r[k]) for k in ("plan", "N", "bind", "R", "peak_mb", "fail_above_mb")) for r in runs], det.get("why")), flush=True)
gate("T3 stage_d1_ring_p3b2.py: X10 returns a model run (prediction printed above)", len(runs) >= 1, det.get("why"))
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
