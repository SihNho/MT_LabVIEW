r"""selftest_stage_prerun_c128 - card 128-3 Step 2.1: stage_prerun.main restores builtins.open after an IN-PROCESS --dry/--prerun.
PURE PYTHON, no LabVIEW (COM stubbed by stage_prerun.install).
Existed first: selftest_stage_prerun_c115c.py (shape copied; it runs stage_d1_l2r1.py in a SUBPROCESS, which never saw the bug).
The bug: install() sets builtins.open = dry_open (stage_prerun.py:601) and nothing restored it, so diag_c128_1_checks.py's later
json.dump(pred, open(<tools/bench/...>, "w")) landed in the SINK, not on disk (result_128-1.json fact 8).
Prediction contract: T1-T3 PASS -
  T1 NEGATIVE CONTROL: a bare install() replaces builtins.open (the condition the test must be able to see); restored by hand
  T2 in-process main(["--dry", stage_d1_l2r1.py, "--no-record"]) -> afterwards builtins.open IS the original open
  T3 a write to tools/bench/selftest_stage_prerun_c128_probe.txt (outside %TEMP%) after T2 lands on disk with its content
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_stage_prerun_c128.log -- py -u tools/bench/selftest_stage_prerun_c128.py
"""
import builtins, contextlib, io, os, sys, time                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)  # noqa: E702
sys.path.insert(0, TOOLS)
import stage_prerun as SP, protocol                                                  # noqa: E401,E402
ORIG = builtins.open
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:500]), flush=True)


saved = builtins.open
SP.install()
t1 = builtins.open is not ORIG
builtins.open = saved
gate("T1 negative control: a bare install() replaces builtins.open (restored by hand)", t1, builtins.open)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        rc = SP.main(["--dry", os.path.join(TOOLS, "recipes", "stage_d1_l2r1.py"), "--no-record"])
    except SystemExit as e:
        rc = e.code
gate("T2 in-process main --dry stage_d1_l2r1.py: builtins.open is the original afterwards", builtins.open is ORIG,
     (rc, builtins.open, [x for x in buf.getvalue().splitlines() if x.startswith(("RESULT", "==="))][:2]))
probe = os.path.join(HERE, "selftest_stage_prerun_c128_probe.txt")
tok = "c128 probe {0}".format(time.time())
with open(probe, "w", encoding="utf-8") as f:
    f.write(tok)
on_disk = os.path.isfile(probe) and ORIG(probe, encoding="utf-8").read() == tok
gate("T3 a write outside %TEMP% after the in-process dry lands on disk", on_disk, probe)
np_, nf = sum(1 for _l, c in G if c), sum(1 for _l, c in G if not c)
print(protocol.result_line(protocol.make_result(np_, nf, next((l for l, c in G if not c), None))), flush=True)
os._exit(1 if nf else 0)
