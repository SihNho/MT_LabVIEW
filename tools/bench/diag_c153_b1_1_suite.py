# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-b1-1.md
# ---
"""diag_c153_b1_1_suite - card 153-b1-1: run the existing stagesim self-tests (each as its own subprocess, offline) and print the
RESULT counts of each, plus the md5 of every invariant file in the brief. Run BEFORE and AFTER the stagesim edit; the two logs are
compared. Writes nothing (the self-tests write only to their own temp dirs).
PREDICTION: every self-test exits with the same pass/fail counts before and after; invariants identical except tools/stagesim.py."""
import hashlib, json, os, re, subprocess, sys                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                         # noqa: E402
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
INV = ["tools/stagesim.py", "tools/stagekit.py", "tools/addrcheck.py", "tools/stagexec.py", "tools/gscript.py",
       "tools/stage_prerun.py", "tools/vigraph.py", "tools/card_clock.py", "tools/bench/fs_tunnel_naming_table.json",
       "tools/bench/plan_ring_p4_s09v18.json", "tools/bench/graph_ring_p4s08_20261009_033522.json",
       "tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json", "tools/bench/graph_ring_p4s09_20261009_062044.json",
       os.path.join(CLAUDEDEV, "D1_ring_p4s09_20261009_060515.vi")]
INV += ["tools/bench/sim/ring_p4_s09v18/" + f for f in sorted(os.listdir(os.path.join(HERE, "sim", "ring_p4_s09v18")))
        if os.path.isfile(os.path.join(HERE, "sim", "ring_p4_s09v18", f))]
TESTS = [["tools/stagesim.py", "selftest"]] + [["tools/bench/" + n] for n in (
    "selftest_stagesim_k79.py", "selftest_stagesim_pin.py", "selftest_stagesim_l2a1_80.py", "selftest_stagesim_unflip_81.py",
    "selftest_stagesim_fsexit_c138_1.py", "selftest_stagesim_tunnel_naming.py", "selftest_c152_fsowner.py")]


def md5(p):
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


for p in INV:
    print("  MD5  {0}  {1}".format(md5(p)[:8], os.path.basename(p) if os.path.isabs(p) else p), flush=True)
res = []
for t in TESTS:
    r = subprocess.run([sys.executable, "-u"] + t, cwd=ROOT, capture_output=True, text=True, timeout=600)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("RESULT ")]
    g = json.loads(lines[-1][7:])["gates"] if lines else None
    fails = [ln.strip()[:200] for ln in r.stdout.splitlines() if re.match(r"\s*FAIL\b", ln)]
    print("  TEST  {0:<48} rc={1} gates={2} fails={3}".format(" ".join(t), r.returncode, g, fails[:3]), flush=True)
    res.append(g is not None)
print(P.result_line(P.make_result(res.count(True), res.count(False), None if all(res) else "a self-test printed no RESULT")))
