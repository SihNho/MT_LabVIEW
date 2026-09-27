"""Self-test, card 110-7 (F1/F2, decided by judgement): stage_prerun X9 checks a decisions-row `copy` ONLY when the
recipe's AST calls stagekit.run_rows / from_decision (recipe_dispatches_rows). Offline, no LabVIEW, no COM.
FOUND FIRST: selftest_stage_prerun_c106c.py (X9 on stageplan/1 ops, C4/C5) - kept and re-run for regressions; this file
adds only the decisions-row branch.
PREDICTION (8 gates):
  G1 recipe_dispatches_rows(stage_replay_swap.py) is False (shutil byte copy, no run_rows/from_decision call)
  G2 X9 with that recipe's verdict over plans 78, 95, 110 (work = a claudeDev\\replay copy, != MOVE_DST) -> [] (pass)
  G3 the OLD behaviour (rows_dispatched=True) on the same plans/work -> 3 failures, one per plan R01 (the fix is what moved)
  G4 every tools/recipes/*.py that calls run_rows/from_decision (stage_d1_l7_1, l7_1b, m3a4, m4a, m4b) -> True
  G5 NEGATIVE: a fixture recipe calling `s.run_rows(...)` -> True, and X9 on plan 110 with work != MOVE_DST FAILS on R01
  G6 the same fixture with work == gscript.MOVE_DST -> X9 [] (the precondition refuses in G5, not the recipe)
  G7 a fixture that only NAMES run_rows (string + comment, no call) -> False
  G8 plan 110 R01 action is 'copy' again; plans 78/95 R01 still 'copy' (not relabelled)
Usage: py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stage_prerun_c110g.log -- py -u tools/bench/selftest_stage_prerun_c110g.py
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP                                                                   # noqa: E402
import protocol as P                                                                        # noqa: E402

PL = dict((t, os.path.join(ROOT, "tools", "bench", "plans", "plan_replay_swap_{0}.json".format(t))) for t in ("78", "95", "110"))
SWAP = os.path.join(ROOT, "tools", "recipes", "stage_replay_swap.py")
WORK = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\replay\D1_s1_disp_replay_dry.vi"
ROWREC = ["stage_d1_l7_1.py", "stage_d1_l7_1b.py", "stage_d1_m3a4.py", "stage_d1_m4a.py", "stage_d1_m4b.py"]


def main():
    import gscript                                                                          # MOVE_DST only; no COM call
    mdst = gscript.MOVE_DST
    res = []

    def gate(lab, ok, det=""):
        res.append((lab, bool(ok)))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:500]), flush=True)
    plans = [PL["78"], PL["95"], PL["110"]]
    rd = SP.recipe_dispatches_rows(SWAP)
    gate("G1 stage_replay_swap.py dispatches no decisions row", rd is False, rd)
    vp = SP.verb_preconditions(plans, [], WORK, mdst, rows_dispatched=rd)
    gate("G2 X9 plans 78/95/110 under stage_replay_swap -> no failure", vp == [], vp)
    old = SP.verb_preconditions(plans, [], WORK, mdst, rows_dispatched=True)
    gate("G3 old behaviour (rows_dispatched=True) -> 3 R01 failures", len(old) == 3 and all("row R01 copy" in x for x in old), old)
    rr = dict((r, SP.recipe_dispatches_rows(os.path.join(ROOT, "tools", "recipes", r))) for r in ROWREC)
    gate("G4 run_rows/from_decision recipes -> True", all(rr.values()), rr)
    tmp = tempfile.mkdtemp(prefix="c110g_")
    fx = os.path.join(tmp, "stage_fixture_rows.py")
    with open(fx, "w", encoding="utf-8") as f:
        f.write("import stagekit as K\n\ndef body(s):\n    s.run_rows(P['decisions'])\n")
    f5 = SP.recipe_dispatches_rows(fx)
    v5 = SP.verb_preconditions([PL["110"]], [], WORK, mdst, rows_dispatched=f5)
    gate("G5 NEGATIVE run_rows fixture, work != MOVE_DST -> X9 FAIL on R01", f5 is True and len(v5) == 1 and "R01 copy" in v5[0], (f5, v5))
    v6 = SP.verb_preconditions([PL["110"]], [], mdst, mdst, rows_dispatched=f5)
    gate("G6 same fixture, work == MOVE_DST -> X9 pass", v6 == [], v6)
    fx7 = os.path.join(tmp, "stage_fixture_named.py")
    with open(fx7, "w", encoding="utf-8") as f:
        f.write("# s.run_rows(P) is not called here\nNOTE = 'from_decision run_rows'\nrun_rows = None\n")
    f7 = SP.recipe_dispatches_rows(fx7)
    gate("G7 a recipe that only names run_rows -> False", f7 is False, f7)
    acts = dict((t, [r.get("action") for r in json.load(open(p, encoding="utf-8"))["decisions"] if r.get("id") == "R01"]) for t, p in PL.items())
    gate("G8 R01 action 'copy' in plans 78/95/110", all(a == ["copy"] for a in acts.values()), acts)
    for p in (fx, fx7):
        os.remove(p)
    os.rmdir(tmp)
    npass = sum(1 for _l, ok in res if ok)
    nfail = len(res) - npass
    first = next((l for l, ok in res if not ok), None)
    print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
    print(P.result_line(P.make_result(npass, nfail, first, status="PASS" if not nfail else "FAIL")), flush=True)
    return 0 if not nfail else 1


if __name__ == "__main__":
    sys.exit(main())
