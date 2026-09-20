"""test_oploopcast_v1.py - FUNCTIONAL acceptance of OpLoopCast_v1 (loop_cast with parallelism fields).

Prediction contract (peer archive/peer/2026-09-14-oploopcast-v1-parallelism-plan.md):
  T1 HARNESS_par.vi (the CPU-parallel kernel harness, P=4 by construction): its For loop reports parallel_enabled
     TRUE (and static_instances recorded); HARNESS_copyloop: FALSE. No errors.
  T2 main VI, 17 For loops: v0 fields identical to test_oploopcast.log (uid set, N wires); parallel_enabled FALSE on
     every loop (PREDICTION: the original is sequential); static_instances recorded per loop, not asserted.
  T3 handle audit: 20 runs flat within +-100 (post-idle).
Output tools/bench/main_vi_forloops.json.
  py tools/bgrun.py --max-min 15 --log tools/bench/test_oploopcast_v1.log -- py -u tools/bench/test_oploopcast_v1.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))["vi"]
# Run 1 (test_oploopcast_v1.log 18:0x) targeted HARNESS_par.vi, which has NO For loop of its own (Traverse: 0) -
# it calls PARALLEL_kernel_v3.vi (build_timing_harnesses.py), where the P=4 loop lives. Test-design error, reviewed
# (archive/peer/2026-09-14-oploopcast-v1-t1-harness-par-no-loop.md).
HPAR = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
HCL = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def main():
    g._lv = None
    n_par = len(g.report_all(HPAR, "ForLoop"))
    par = [g.loop_cast(HPAR, i) for i in range(n_par)]
    print(f"T1 PARALLEL_kernel_v3 ({n_par} For loops): {par}", flush=True)
    check("T1 PARALLEL_kernel_v3 has a parallel loop (P=4 by construction)", any(r.get("parallel_enabled") for r in par),
          f"enabled {[r.get('parallel_enabled') for r in par]} P {[r.get('static_instances') for r in par]}")
    cl = g.loop_cast(HCL, 0)
    print(f"T1 HARNESS_copyloop: {cl}", flush=True)
    check("T1 copyloop not parallel, N wire 346", cl.get("parallel_enabled") is False and cl["n_wire_uid"] == 346)
    check("T1 no errors", not any(r["errors"] for r in par + [cl]))
    loops = {o["uid"] for o in g.report_all(MAIN, "ForLoop")}
    rows = []; t0 = time.time()
    for i in range(len(loops)):
        r = g.loop_cast(MAIN, i); rows.append(r)
        print(f"   ForLoop[{i}] uid {r['loop_uid']:6d} N wire {r['n_wire_uid']:6d} regs {len(r['shift_reg_uids'])} parallel {r.get('parallel_enabled')} P {r.get('static_instances')} {r['errors'] or ''}", flush=True)
    print(f"   {time.time() - t0:.1f} s", flush=True)
    check("T2 uid set == Traverse", {r["loop_uid"] for r in rows} == loops)
    check("T2 no errors", not any(r["errors"] for r in rows))
    n_on = sum(1 for r in rows if r.get("parallel_enabled"))
    check("T2 parallelism enabled on 0 loops (prediction)", n_on == 0, f"{n_on} enabled")
    json.dump({"vi": MAIN, "forloops": rows}, open(os.path.join(HERE, "main_vi_forloops.json"), "w", encoding="utf-8"), indent=1)
    for _ in range(3):
        g.loop_cast(MAIN, 0)
    h0 = handles()
    for _ in range(20):
        g.loop_cast(MAIN, 0)
    h1 = handles(); time.sleep(20); h2 = handles()
    check("T3 handles flat (+-100 post-idle)", abs(h2 - h0) <= 100, f"{h0} -> {h1} -> idle {h2}")
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
