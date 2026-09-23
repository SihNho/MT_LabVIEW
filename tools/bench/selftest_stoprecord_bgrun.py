r"""selftest_stoprecord_bgrun.py - a prior-art review of a stopped recipe must be launchable UNDER BGRUN, while the
recipe itself stays refused (cycle 71 repair of tools/stop_record.py `exempt_program`; the deadlock: the exemption
looked at the program in command position, which under the mandatory bgrun wrapper is bgrun.py).

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stoprecord_bgrun.log -- \
        py -u tools/bench/selftest_stoprecord_bgrun.py [stop_record_new]

PRIOR ART: tools/bench/selftest_stoprecord_eqform.py (temp STORE/MARKER per case, module under test by argv) and
selftest_stoprecord_supersession.py (STOP_RECORD_UNDER_TEST). No LabVIEW.
PREDICTION CONTRACT
  B1 `bgrun ... -- py tools/prior_art_review.py ... --recipe X` (space) is ALLOWED with an unreleased record for X
  B2 the same with `--recipe=X` is ALLOWED
  B3 `bgrun ... -- py -u X` is REFUSED
  B4 `bgrun ... -- py tools/prior_art_review.py --recipe X && py -u X` is REFUSED (second segment)
  B5 `MATERIAL=1 py tools\bgrun.py ... -- py -u tools/prior_art_review.py --recipe X` (env prefix, backslash) ALLOWED
  B6 `bgrun ... -- py tools/other_tool.py --recipe X` is REFUSED (only the named exempt programs pass)
"""
import importlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
MOD = sys.argv[1] if len(sys.argv) > 1 else "stop_record"
sr = importlib.import_module(MOD)
passes, fails = [], []


def gate(ok, label, detail=""):
    (passes if ok else fails).append(label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


X = "tools/recipes/stage_bgrun_fixture.py"
BG = "py tools/bgrun.py --material --max-min 20 --log tools/bench/pa_bg.log -- "
PA = "py tools/prior_art_review.py --plan-file docs/d1-loop12-17-split-plan.md --slug bg --recipe"
CASES = [
    ("B1 bgrun + prior_art_review --recipe X allowed", BG + PA + " " + X, True),
    ("B2 bgrun + prior_art_review --recipe=X allowed", BG + PA + "=" + X, True),
    ("B3 bgrun + py -u X refused", BG + "py -u " + X, False),
    ("B4 review && recipe refused", BG + PA + " " + X + " && py -u " + X, False),
    ("B5 env prefix + backslash bgrun + prior_art allowed",
     "MATERIAL=1 py tools\\bgrun.py --max-min 20 --log tools/bench/pa_bg.log -- py -u tools/prior_art_review.py "
     "--recipe " + X, True),
    ("B6 bgrun + other tool --recipe X refused", BG + "py tools/other_tool.py --recipe " + X, False),
]


def main():
    print("=== selftest_stoprecord_bgrun on %s ===" % sr.__file__, flush=True)
    tmp = tempfile.mkdtemp(prefix="bgrunex_")
    real = (sr.STORE, sr.MARKER)
    try:
        sr.STORE, sr.MARKER = os.path.join(tmp, "stop_records.json"), os.path.join(tmp, "stop_records.marker")
        with open(sr.STORE, "w", encoding="utf-8") as f:
            json.dump([{"recipe_path": X, "review_file": "archive/peer/does-not-exist-bgrun.md",
                        "verdicts": ["contradicted"], "released": None}], f)
        for label, cmd, want in CASES:
            allow, _ = sr._check(cmd)
            gate(allow == want, label, "allow=%s want=%s" % (allow, want))
    finally:
        sr.STORE, sr.MARKER = real
    print("\n=== selftest_stoprecord_bgrun: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
