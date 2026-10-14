# ---
# labview: none
# hardware: none
# ---
r"""fr150_legsum - read-only per-leg summary of an fr150 run root (reads the leg folders' p64_leg.json, fr150_rate.json,
fr90_autoreset.json, p64_own.json and leg_child.log; writes nothing).
    py tools/bench/lean_bench/fr150_legsum.py <out-root>"""
import glob, json, os, re, sys                                                             # noqa: E401


def jl(p):
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}


root = sys.argv[1]
for leg in sorted(glob.glob(os.path.join(root, "legs", "leg*"))):
    pl, rt, ar, own = (jl(os.path.join(leg, n)) for n in ("p64_leg.json", "fr150_rate.json", "fr90_autoreset.json", "p64_own.json"))
    F, G = pl.get("facts") or {}, pl.get("gates") or {}
    log = open(os.path.join(leg, "leg_child.log"), encoding="utf-8", errors="replace").read() if os.path.isfile(os.path.join(leg, "leg_child.log")) else ""
    loc = re.search(r"\[fr90 locate\] (locator=[^;]+); (box \([^)]*\)).*?side offsets (\[[^\]]*\]).*?(C2 \w+)", log)
    g0 = re.search(r"STEP 0 G0 .*?(PASS|FAIL) (exit=\d+); (LIMITS TMN=\d+ TMX=\d+)", log)
    g93 = re.search(r"STEP 93 G93 .*?(PASS|FAIL) (TMX\?=[\d.]+).*?(REFSTATE [^\n|]*)", log)
    reads = [(r.get("tag"), r.get("# of Auto-Reset"), r.get("Auto-Reset"), r.get("Total Lost Frames")) for r in ar.get("reads") or []]
    print("=== %s" % os.path.basename(leg))
    print("  run_dir %s" % F.get("run_dir"))
    print("  rows %s lost_col0 %s steps %s" % (F.get("rows"), F.get("lost_col0"), json.dumps(F.get("steps"))))
    print("  frames_delta %s measured_hz %s lost_indicator %s picks_registered_tra %s bandpass %s" % (
        F.get("frames_delta"), F.get("measured_hz"), F.get("lost_indicator"), F.get("picks_registered_tra"), F.get("bandpass_answered")))
    print("  autoreset reads %s" % reads)
    print("  rate lines %s fields %s why %s md5 %s -> %s gate %s" % (rt.get("lines"), rt.get("fields"), rt.get("why"), rt.get("md5"), rt.get("md5_after"), rt.get("gate")))
    print("  locate %r" % ((loc.groups() if loc else None),))
    print("  G0 %r | G93 %r" % ((g0.groups() if g0 else None), (g93.groups() if g93 else None)))
    print("  gates failing %s (of %d)" % ([k for k, v in G.items() if not v], len(G)))
    if own:
        print("  OWN %s" % json.dumps({k: own.get(k) for k in ("verdict", "why", "wrapper_lines", "S", "R", "R_minus_S", "step2", "step3", "step4", "end_lag")}, default=str)[:1500])
