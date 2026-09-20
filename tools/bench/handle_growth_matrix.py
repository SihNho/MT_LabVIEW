"""handle_growth_matrix.py - WHERE do the ~+1 handle per op run on the main VI come from? (OPEN item, peer matrix
archive/peer/2026-09-14-opsubvis-v1-donor-netinfo.md s3).

Blocks, each 50 runs on the MAIN VI (reference only, never opened), LabVIEW HandleCount sampled every 10 runs and
30 s after the block (deferred disposal check):
    A  exec_state(main)            - the smallest op that opens a VI reference (OpExecState) and closes it
    B  report_all(main, 'Wire')    - one traverse, no element refs kept
    C  subvis(main, 43)            - SubVIs[] elements (6 refs) per run
    D  node_terms(main, 43, 5)     - one node's terminals
    E  exec_state(HARNESS_disp0)   - the same minimal op on a SMALL VI (control)
Reading: growth in A and E alike = per-run cost of the op mechanism; A but not E = the big VI's load/unload;
growth only in C/D = element references. Post-idle drop = deferred disposal, not a leak.
  py tools/bgrun.py --max-min 15 --log tools/bench/handle_growth_matrix.log -- py -u tools/bench/handle_growth_matrix.py
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
SMALL = os.path.join(g.CLAUDEDEV, "HARNESS_disp0.vi")
g._run.__defaults__ = (6.0, 120.0)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def block(name, fn, n=50):
    for _ in range(3):
        fn()
    time.sleep(2); samples = [(0, handles())]; t0 = time.time()
    print(f"   {name}: start {samples[0][1]}", flush=True)                      # progress lines: the stall detector
    for k in range(1, n + 1):                                                    # trusts the job log's freshness
        fn()
        if k % 10 == 0:
            samples.append((k, handles())); print(f"   {name}: run {k}/{n} handles {samples[-1][1]}", flush=True)
    t_run = time.time() - t0
    print(f"   {name}: idle wait 30 s", flush=True)
    time.sleep(30); idle = handles()
    xs = [k for k, _ in samples]; ys = [h for _, h in samples]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
    row = {"block": name, "samples": samples, "slope_per_run": round(slope, 3), "post_idle_30s": idle,
           "idle_minus_last": idle - ys[-1], "seconds": round(t_run, 1)}
    print("  ", json.dumps(row), flush=True)
    return row


def main():
    g._lv = None
    rows = [block("A exec_state(main)", lambda: g.exec_state(MAIN)),
            block("B report_all(main,'Wire')", lambda: g.report_all(MAIN, "Wire")),
            block("C subvis(main,43)", lambda: g.subvis(MAIN, 43)),
            block("D node_terms(main,43,5)", lambda: g.node_terms(MAIN, 43, 5)),
            block("E exec_state(small)", lambda: g.exec_state(SMALL))]
    print("\nSUMMARY slope handles/run | post-idle change:", flush=True)
    for r in rows:
        print(f"   {r['block']:28s} {r['slope_per_run']:+.2f}   idle {r['idle_minus_last']:+d}   ({r['seconds']} s)", flush=True)
    json.dump(rows, open(os.path.join(HERE, "handle_growth_matrix.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
