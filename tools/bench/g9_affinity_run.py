"""g9_affinity_run.py - G9 core budget: the three-way kernel timing at all cores and at one physical core fewer, A-B-A.

Conditions (LabVIEW.exe process affinity set from PowerShell, no restart; restored to all cores in `finally`):
    A  all logical processors          (mask from cpu_topology.py)
    B  minus one physical core         (both HT siblings of the last core removed - topology-derived, not assumed)
    A' all logical processors again    (drift check)
Each condition = tools/bench/run_timing.py --harness=base --harness=par --harness=gpuk --n=200 (the accepted method,
INDEX rows 15-18): kernel ms = harness - base, interleaved frames, outputs checked against the reference.
Gate (peer review archive/peer/2026-09-14-g9-five-core-plan.md): G9 FAILS if B's paired par-kernel p90 regresses by
> 10 % against the mean of A and A'. Output tools/bench/g9_affinity_results.json + printed table.
  py tools/bgrun.py --max-min 40 --log tools/bench/g9_affinity_run.log -- py -u tools/bench/g9_affinity_run.py [n]
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
N = sys.argv[1] if len(sys.argv) > 1 else "200"
RESULTS = os.path.join(HERE, "run_timing_results.json")


def ps(cmd):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=30)
    return (r.stdout or "").strip() + (("\nERR " + r.stderr.strip()) if r.stderr.strip() else "")


def set_affinity(mask):
    out = ps(f"$p = Get-Process LabVIEW | Select-Object -First 1; $p.ProcessorAffinity = [IntPtr]{mask}; "
             f"'set 0x{{0:X}}' -f [int64](Get-Process LabVIEW | Select-Object -First 1).ProcessorAffinity")
    print(f"   affinity -> {out}", flush=True)
    return out


def clocks(tag):
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=clocks.sm,clocks.mem,pstate,utilization.gpu,temperature.gpu",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        out = f"(nvidia-smi failed: {e})"
    print(f"   clocks {tag}: {out}", flush=True)
    return out


def main():
    topo = json.loads(subprocess.run([sys.executable, os.path.join(HERE, "cpu_topology.py")], capture_output=True, text=True).stdout)
    all_mask, minus = int(topo["all_mask"], 16), int(topo["minus_one_core_mask"], 16)
    print(f"topology: {len(topo['cores'])} cores {[c['lps'] for c in topo['cores']]}; all 0x{all_mask:X}; minus one core 0x{minus:X} "
          f"(removed LPs {topo['removed_core_lps']})", flush=True)
    conds = [("A_all", all_mask), ("B_minus1", minus), ("A2_all", all_mask)]
    rows = []
    try:
        for tag, mask in conds:
            print(f"\n===== {tag} mask 0x{mask:X}", flush=True)
            set_affinity(mask)
            time.sleep(2)
            before = clocks("before")
            if os.path.exists(RESULTS):
                os.remove(RESULTS)
            t0 = time.time()
            rc = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_timing.py"), f"--n={N}",
                                 "--harness=base", "--harness=par", "--harness=gpuk"], cwd=ROOT, timeout=1800).returncode
            row = {"cond": tag, "mask": hex(mask), "rc": rc, "seconds": round(time.time() - t0), "clocks_before": before, "clocks_after": clocks("after")}
            if os.path.exists(RESULTS):
                d = json.load(open(RESULTS))
                row["stats_ms"] = {k: [round(x, 2) for x in v] for k, v in d["stats_ms"].items()}
                row["kernel_ms"] = {k: round(v, 2) for k, v in d["kernel_ms"].items()}
                row["worst_dev"] = d.get("worst_dev")
            print("   ", json.dumps(row)[:600], flush=True)
            rows.append(row)
    finally:
        set_affinity(all_mask)
    print("\n===== G9 SUMMARY (stats_ms = [median, ...] per harness; kernel = harness - base)", flush=True)
    for r in rows:
        print(f"  {r['cond']:9s} mask {r['mask']:>6s}: base {r.get('stats_ms', {}).get('base')} par {r.get('stats_ms', {}).get('par')} "
              f"gpuk {r.get('stats_ms', {}).get('gpuk')} | kernel {r.get('kernel_ms')} | dev {r.get('worst_dev')}", flush=True)
    try:
        a = [r["kernel_ms"]["par"] for r in rows if r["cond"].startswith("A")]
        b = next(r["kernel_ms"]["par"] for r in rows if r["cond"] == "B_minus1")
        ref = sum(a) / len(a)
        print(f"\nG9 gate (par kernel median, B vs mean(A, A')): {b:.2f} vs {ref:.2f} ms = {100 * (b - ref) / ref:+.1f} % "
              f"-> {'FAIL (> +10 %)' if b > 1.10 * ref else 'PASS'}", flush=True)
    except Exception as e:
        print("gate not computed:", e, flush=True)
    json.dump({"topology": topo, "rows": rows}, open(os.path.join(HERE, "g9_affinity_results.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
