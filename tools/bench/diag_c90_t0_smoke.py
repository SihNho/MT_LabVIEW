r"""diag_c90_t0_smoke - card 90-5 smoke: ONE short real leg of the instrumented D1_s1_t0_<ts>.vi through drive_m8 (leg
replay_s1 --src <vi>: a dated run copy beside it, v5's L1..L13 with the bead-pick GUI, stop by the VI's own control, LabVIEW
gone, motor TMX re-read), with T0STAMP_DIR = a FRESH per-run directory (PD197(d)) set in THIS process and LabVIEW started
from it by bench_prep.restart_labview (Start-Process inherits the environment; a COM-launched LabVIEW would not).
FOUND FIRST: drive_m8.py (thin wrapper, argv parsed at import), drive_m8_panelmin89_leg.py (the same wrapping shape),
bench_prep.restart_labview, t0stamp.c record format (int64 LE: [0] = QPC frequency, then stamps; file t0_site<SS>_pid<PID>.bin).
PREDICTION CONTRACT: K1 drive_m8 gates all PASS (M1..M8); K2 T0STAMP_DIR holds a file for sites 00, 10 and 20 (>= 1 stamp
each); K3 the default fallback dir <claudeDev>\t0stamp_out gained NO file during this run (the env reached LabVIEW);
counts per site reported. RESULT line last.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c90_t0_smoke.log -- py -u tools/bench/diag_c90_t0_smoke.py <vi> [--run-s 30]
"""
import glob, os, struct, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
VI = os.path.normpath(sys.argv[1]); RUN_S = sys.argv[sys.argv.index("--run-s") + 1] if "--run-s" in sys.argv else "30"
TS = time.strftime("%Y%m%d_%H%M%S"); OUT = os.path.join(HERE, "t0_legs", "smoke_%s" % TS); os.makedirs(OUT, exist_ok=True)
os.environ["T0STAMP_DIR"] = OUT
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"; DEF = os.path.join(CD, "t0stamp_out")
def_before = set(glob.glob(os.path.join(DEF, "*.bin")))
print("T0STAMP_DIR", OUT, "vi", VI, "run-s", RUN_S, flush=True)
import bench_prep                                                               # noqa: E402
bench_prep.restart_labview()                                                    # LabVIEW started WITH the env var
sys.argv = [sys.argv[0], "--leg", "replay_s1", "--src", VI, "--run-s", RUN_S]
import drive_m8                                                                 # noqa: E402  (argv parsed here)
ok = drive_m8.main()
G = {"K1 drive_m8 leg gates all PASS": bool(ok)}
counts = {}
for p in sorted(glob.glob(os.path.join(OUT, "t0_site*.bin"))):
    b = open(p, "rb").read(); n = len(b) // 8
    counts[os.path.basename(p)] = max(0, n - 1)
print("STAMP FILES", counts, flush=True)
have = lambda z: any(("site%02d_" % z) in k and v >= 1 for k, v in counts.items())              # noqa: E731
G["K2 files for sites 00/10/20 with >= 1 stamp"] = all(have(z) for z in (0, 10, 20))
new_def = sorted(set(glob.glob(os.path.join(DEF, "*.bin"))) - def_before)
G["K3 no file landed in the default dir (env reached LabVIEW)"] = not new_def
print("DEFAULT DIR NEW FILES", new_def, flush=True)
for k, v in G.items():
    print("GATE %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                  [{"path": os.path.relpath(p, ROOT), "md5": drive_m8.md5(p)} for p in sorted(glob.glob(os.path.join(OUT, "*.bin")))][:12])), flush=True)
sys.stdout.flush(); os._exit(0 if not bad else 1)
