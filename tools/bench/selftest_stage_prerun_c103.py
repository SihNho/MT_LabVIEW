"""Self-test, card 103-2 (PD216(b)): stage_prerun X5 in PART-A mode counts only the wiring ops <= stop_after.

Existing pieces used (nothing new built): stage_prerun.prerun (the gate under test), the recipe
tools/recipes/stage_d1_disp.py with its own `--stop-after 40` (card 103-1) and the graph tools/bench/par1359_95_graph.json
the 103-1 pre-runs used. Each case is a separate child process (the dry run installs COM stubs process-wide).

PREDICTION CONTRACT (4 cases, all must hold):
  P1 Part-A dry (recipe argv --stop-after 40), prerun(stop_after=40)          -> X5 PASS, "ops 18 vs ... 18 among ops 1..40"
  P2 NEGATIVE Part-A dry, prerun(stop_after=None) (a full run that skips op 45) -> X5 FAIL, 18 vs 19 (the 103-1 failure)
  P3 full dry (no --stop-after), prerun(stop_after=None)                     -> X5 PASS, 19 vs 19 (unchanged behaviour)
  P4 NEGATIVE Part-A dry with ONE dispatched wiring op dropped from the trace, prerun(stop_after=40) -> X5 FAIL 17 vs 18
Usage: MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/selftest_stage_prerun_c103.log -- py -u tools/bench/selftest_stage_prerun_c103.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py")
GRAPH = os.path.join(ROOT, "tools", "bench", "par1359_95_graph.json")
CASES = {"P1": (True, 40, False, True, "18 among ops 1..40"), "P2": (True, None, False, False, "ops 18 vs"),
         "P3": (False, None, False, True, "ops 19 vs"), "P4": (True, 40, True, False, "ops 17 vs")}


def child(case):
    import stage_prerun as SP
    part_a, sa, drop, _ok, _txt = CASES[case]
    sys.argv = ["stage_prerun.py", "--prerun", RECIPE, "--graph", GRAPH] + (["--stop-after", "40"] if part_a else [])
    if drop:
        real_dry = SP.dry

        def dry_drop(recipe, graph=None):
            tr = real_dry(recipe, graph)
            i = next(i for i, v in enumerate(tr["ops"]) if SP.WIRE_VERB_RE.search(v))
            tr["ops"] = tr["ops"][:i] + tr["ops"][i + 1:]
            return tr
        SP.dry = dry_drop
    out = sys.stdout
    tr = SP.prerun(RECIPE, GRAPH, stop_after=sa)
    sys.stdout = out
    x5 = [g for g in tr["prerun"]["gates"] if g[0].startswith("X5")][0]
    print("CASEOUT " + json.dumps({"case": case, "x1": tr["status"], "x5": x5[1], "detail": x5[2]}), flush=True)


def main():
    import protocol as P
    npass, nfail, first = 0, 0, None
    for case, (_pa, _sa, _dr, want, txt) in CASES.items():
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--case", case], cwd=ROOT,
                           capture_output=True, text=True, timeout=300)
        line = [ln for ln in p.stdout.splitlines() if ln.startswith("CASEOUT ")]
        r = json.loads(line[-1][8:]) if line else {"x1": None, "x5": None, "detail": (p.stderr or p.stdout)[-400:]}
        ok = r["x1"] == "PASS" and r["x5"] is want and txt in str(r["detail"])
        npass, nfail = npass + ok, nfail + (not ok)
        lab = "{0} X5 expected {1} with '{2}'".format(case, "PASS" if want else "FAIL", txt)
        first = first or (None if ok else lab)
        print("  {0}  {1}  -> x1 {2} x5 {3} | {4}".format("PASS" if ok else "FAIL", lab, r["x1"], r["x5"], r["detail"]),
              flush=True)
    print(P.result_line(P.make_result(npass, nfail, first, status="PASS" if not nfail else "FAIL")), flush=True)
    return 0 if not nfail else 1


if __name__ == "__main__":
    if "--case" in sys.argv:
        child(sys.argv[sys.argv.index("--case") + 1])
    else:
        sys.exit(main())
