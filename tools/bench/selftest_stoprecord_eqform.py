r"""selftest_stoprecord_eqform.py - `--recipe <path>` and `--recipe=<path>` must meet the same stop record
(docs/violation-decisions.md `## device-failed - 2026-09-24 03:53`, the stop-record token-shape FINDING; the live
case: cycle 70 at 03:21:57 was refused on `--recipe tools/recipes/stage_d1_l7_1.py` and 03:22:42 went through on
`--recipe=tools/recipes/stage_d1_l7_1.py`).

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stoprecord_eqform.log -- \
        py -u tools/bench/selftest_stoprecord_eqform.py [stop_record_new]

PRIOR ART: tools/bench/selftest_stoprecord_supersession.py (isolated STORE/MARKER per case; re-run here on the same
module through STOP_RECORD_UNDER_TEST). No LabVIEW.
PREDICTION CONTRACT
  Q1 the path tokens of `... --recipe X` and `... --recipe=X` give the same keys
  Q2 with an unreleased record for X in a temp store, BOTH spellings of the launch are refused
  Q3 a command that does not name X is allowed
  Q4 `--log=tools/bench/y.log` still yields its path (an `=` argument is not lost, only its `--opt=` prefix)
  R1 selftest_stoprecord_supersession.py passes on the same module
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
MOD = sys.argv[1] if len(sys.argv) > 1 else "stop_record"
sr = importlib.import_module(MOD)
passes, fails = [], []


def gate(ok, label, detail=""):
    (passes if ok else fails).append(label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


def keys(cmd):
    out = set()
    for t in sr.PATH_TOKEN_RE.findall(cmd):
        out |= sr.keys_for(t)
    return out


X = "tools/recipes/stage_eqform_fixture.py"
BASE = ("py tools\\bgrun.py --material --max-min 20 --log tools/bench/priorart_eq.log -- "
        "py tools/other_tool.py --plan-file docs/d1-loop12-17-split-plan.md --slug eq --recipe")
# The fixture program was prior_art_review.py until cycle 71; under bgrun that program is now EXEMPT
# (selftest_stoprecord_bgrun.py), so a non-exempt program carries the token-shape test instead.
SPACE, EQ = BASE + " " + X, BASE + "=" + X


def main():
    print("=== selftest_stoprecord_eqform on %s ===" % sr.__file__, flush=True)
    kx = sr.keys_for(X)
    gate(kx <= keys(SPACE) and kx <= keys(EQ), "Q1 both spellings carry the recipe's keys",
         "space %s / eq %s" % (kx <= keys(SPACE), kx <= keys(EQ)))
    tmp = tempfile.mkdtemp(prefix="eqform_")
    real = (sr.STORE, sr.MARKER)
    try:
        sr.STORE, sr.MARKER = os.path.join(tmp, "stop_records.json"), os.path.join(tmp, "stop_records.marker")
        with open(sr.STORE, "w", encoding="utf-8") as f:
            json.dump([{"recipe_path": X, "review_file": "archive/peer/does-not-exist-eqform.md",
                        "verdicts": ["contradicted"], "released": None}], f)
        a1, _ = sr._check(SPACE)
        a2, _ = sr._check(EQ)
        gate(not a1 and not a2, "Q2 both spellings are refused by the same record", "allow space=%s eq=%s" % (a1, a2))
        a3, _ = sr._check("py tools\\bgrun.py --material --max-min 5 --log tools/bench/z.log -- py -u tools/recipes/other.py")
        gate(a3, "Q3 a launch of another recipe is allowed", "allow=%s" % a3)
    finally:
        sr.STORE, sr.MARKER = real
    gate(sr.keys_for("tools/bench/y.log") <= keys("py x.py --log=tools/bench/y.log"),
         "Q4 an `--opt=<path>` argument still yields its path")
    env = dict(os.environ, STOP_RECORD_UNDER_TEST=MOD)
    p = subprocess.run([sys.executable, "-u", os.path.join(HERE, "selftest_stoprecord_supersession.py")], env=env,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    tail = [ln.strip() for ln in (p.stdout or "").splitlines() if ln.strip()][-1:] or [""]
    gate(p.returncode == 0, "R1 selftest_stoprecord_supersession.py passes on %s" % MOD,
         "exit %d; last line: %s" % (p.returncode, tail[0][:140]))
    print("\n=== selftest_stoprecord_eqform: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
