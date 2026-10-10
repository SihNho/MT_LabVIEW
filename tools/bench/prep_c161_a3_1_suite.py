# ---
# labview: none
# hardware: none
# offline-args: <tag> <selftest name> ...
# evidence: tools/bench/prep_c161_a2_1_measure.log
# ---
"""prep_c161_a3_1_suite - card 161-a3-1: run offline self-tests one after another (child processes of this bgrun) and print each one's
RESULT line / gate counts, for the pin sweep's before/after counts. Each test's stdout goes to tools/bench/prep_c161_a3_1_<tag>_<name>.out.
PREDICTION: every listed test prints a RESULT line; counts are reported, not judged here."""
import os, sys, re, subprocess, json                                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol                                                                            # noqa: E402

B = os.path.dirname(os.path.abspath(__file__))
tag, names = sys.argv[1], sys.argv[2:]
ok, bad = 0, []
for n in names:
    outp = os.path.join(B, "prep_c161_a3_1_{0}_{1}.out".format(tag, n))
    with open(outp, "w", encoding="utf-8") as f:
        rc = subprocess.call([sys.executable, "-u", os.path.join(B, n + ".py")], stdout=f, stderr=subprocess.STDOUT, timeout=900,
                             cwd=os.path.dirname(B).rsplit(os.sep, 1)[0])
    txt = open(outp, encoding="utf-8", errors="replace").read()
    res = [ln for ln in txt.splitlines() if ln.startswith("RESULT ")]
    g = None
    if res:
        try:
            g = json.loads(res[-1][7:]).get("gates")
        except ValueError:
            g = None
    fails = [ln[:200] for ln in txt.splitlines() if "GATE FAIL" in ln or ln.startswith("FAIL")][:4]
    print("SUITE {0} rc={1} gates={2} fails={3}".format(n, rc, g, fails), flush=True)
    if rc == 0 and g and g.get("fail") == 0:
        ok += 1
    else:
        bad.append(n)
print(protocol.result_line(protocol.make_result(ok, len(bad), ("not green: " + ", ".join(bad)) if bad else None, [])), flush=True)
