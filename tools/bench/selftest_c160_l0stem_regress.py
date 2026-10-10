# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_160-e4-1.md
# ---
r"""selftest_c160_l0stem_regress - card 160-e4-1 step 3 (OFFLINE): the stagekit-importing self-tests of cycles 155-160, run before
and after the gate_l0 predicate change, counts compared.
WHAT EXISTED FIRST and is CALLED: prep_c156_a1_2_lib.run_suite (child run, PASS/FAIL line counts, last RESULT line); only its
SUITE list is replaced by the 15 tools/bench/selftest_c15*/c16* files that import stagekit (Grep 2026-10-10).
  before : writes tools/bench/diag_c160_e4_1_suite_before.json
  after  : writes ..._after.json and compares with before; per suite, the FAIL lines that differ are printed.
PREDICTION CONTRACT (after): every suite's (rc, PASS-lines, FAIL-lines) == before, EXCEPT suites that pin stagekit's md5 1441bb4c,
whose only new FAIL lines name stagekit's md5 (a pin, not behaviour; listed for OPEN, not re-pinned).
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c160_e4_1_before.log -- py -u tools/bench/selftest_c160_l0stem_regress.py before"""
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import prep_c156_a1_2_lib as L  # noqa: E402
import protocol  # noqa: E402

NAMES = ["c153_compdiff_poskey", "c153_poskey_convert", "c155_basecase_frame", "c155_gatefp73", "c156_b2_2_invcheck", "c156_passwire",
         "c157_innerface", "c158_gates386", "c158_runcheck", "c158_wire0face", "c159_a4_1", "c159_cen2_ends", "c160_delwire",
         "c160_regface", "c160_stagemap"]
L.SUITE = [(n, ["tools/bench/selftest_{0}.py".format(n)]) for n in NAMES]
mode = sys.argv[1] if len(sys.argv) > 1 else "after"
OUTD = os.path.join(tempfile.gettempdir(), "diag_c160_e4_1_" + mode)
os.makedirs(OUTD, exist_ok=True)
rows = {}
for name, rc, npass, nfail, last in L.run_suite(mode, outdir=OUTD):
    out = open(os.path.join(OUTD, "prep_c156_a1_2_suite_{0}_{1}.out".format(mode, name)), encoding="utf-8").read()
    fails = [ln.strip()[:200] for ln in out.splitlines() if re.match(r"^\s*(?:GATE )?FAIL\b", ln)]
    rows[name] = {"rc": rc, "pass": npass, "fail": nfail, "last": last, "fail_lines": fails}
    print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, rc, npass, nfail, last), flush=True)
with open(os.path.join(HERE, "diag_c160_e4_1_suite_{0}.json".format(mode)), "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=1, sort_keys=True)
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, info=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, info), flush=True)


if mode == "before":
    gate("B before json written ({0} suites)".format(len(rows)), len(rows) == len(NAMES))
else:
    bef = json.load(open(os.path.join(HERE, "diag_c160_e4_1_suite_before.json"), encoding="utf-8"))
    for n in NAMES:
        b, a = bef[n], rows[n]
        new = [x for x in a["fail_lines"] if x not in b["fail_lines"]]
        gone = [x for x in b["fail_lines"] if x not in a["fail_lines"]]
        same = (b["rc"], b["pass"], b["fail"]) == (a["rc"], a["pass"], a["fail"]) and not new and not gone
        gate("R {0} (rc, PASS, FAIL) after == before {1}".format(n, (b["rc"], b["pass"], b["fail"])), same,
             {"after": (a["rc"], a["pass"], a["fail"]), "new_fail": new, "gone_fail": gone})
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
