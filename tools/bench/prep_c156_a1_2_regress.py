# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-2.md
# ---
r"""prep_c156_a1_2_regress - card 156-a1-2 regression (OFFLINE). Calls prep_c156_a1_2_lib.compile_all / run_suite.

  py tools/bench/prep_c156_a1_2_regress.py suite <tag>   -> run the stage-tool self-test suite, one SUITE line each
  py tools/bench/prep_c156_a1_2_regress.py after         -> compile every stored plan with the EDITED tools and compare with
                                                            tools/bench/sim/ring_p5s02pw/compile_before.json (measure script)
PREDICTION CONTRACT (after): every stored plan's compile result (op list or ExecStop text) is EQUAL to before; the named
plans p5s01a (ed62e8d6), p5s01b (75a77a00), p5s01_in, p5s02a (4284c22a) and the 155 step plans plan_ring_p5s02*.json are
listed one by one. (suite): the after counts equal the before counts per self-test.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/prep_c156_a1_2_suite_before.log -- py -u tools/bench/prep_c156_a1_2_regress.py suite before"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402

NAMED = ["plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s01_in.json", "plan_ring_p5s02a.json",
         "plan_ring_p5s02a_in.json", "plan_ring_p5s02.json", "plan_ring_p5s02_all.json", "plan_ring_p5s02_in.json",
         "plan_ring_p5s02r_all.json", "plan_ring_p5s02r_in.json"]
G = {"pass": 0, "fail": 0}
FIRST = []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and not FIRST:
        FIRST.append(label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


mode = sys.argv[1] if len(sys.argv) > 1 else "after"
print("FACT md5 stagexec {0} stagesim {1}".format(L.md5(os.path.join(ROOT, "tools", "stagexec.py")),
                                                 L.md5(os.path.join(ROOT, "tools", "stagesim.py"))), flush=True)
if mode == "suite":
    tag = sys.argv[2] if len(sys.argv) > 2 else "before"
    for name, rc, npass, nfail, last in L.run_suite(tag):
        print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, rc, npass, nfail, last), flush=True)
        G["pass" if rc == 0 else "fail"] += 1
        if rc and not FIRST:
            FIRST.append("{0} rc {1}".format(name, rc))
else:
    before = L.jload(os.path.join(L.SIMD, "compile_before.json"))
    now = L.compile_all()
    diff = sorted(k for k in set(before) | set(now) if before.get(k) != now.get(k))
    for k in diff:
        print("DIFF", k, "\n  before", json.dumps(before.get(k))[:600], "\n  after ", json.dumps(now.get(k))[:600], flush=True)
    print("FACT plans {0} compiled {1} refused {2} skipped {3}".format(len(now), sum(1 for v in now.values() if "ops" in v),
          sum(1 for v in now.values() if "error" in v), sum(1 for v in now.values() if "skip" in v)), flush=True)
    gate("A every stored plan compiles EQUAL to before ({0} plans, {1} differ)".format(len(now), len(diff)), not diff, diff[:10])
    for p in NAMED:
        k = "tools/bench/" + p
        b, a = before.get(k) or {}, now.get(k) or {}
        gate("N {0} ({1}) before == after: {2} ops / {3} ops{4}".format(p, (b.get("md5") or "")[:8], len(b.get("ops") or []),
             len(a.get("ops") or []), " (refused both: {0})".format((a.get("error") or "")[:120]) if a.get("error") else ""),
             k in before and b == a)
print(protocol.result_line({"status": "PASS" if not G["fail"] else "FAIL", "gates": G, "first_fail": FIRST[0] if FIRST else None,
                            "artefacts": []}))
sys.exit(1 if G["fail"] else 0)
