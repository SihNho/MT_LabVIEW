"""Self-test, card 106-3: stage_prerun X9 (verb preconditions) and X10 (memory margin from the recorded per-op meter), plus
the <=120-line recipe tools/recipes/stage_d1_disp.py (helpers moved into tools/stagexec.py) still pre-running green.

Existing pieces used (nothing new built): stage_prerun.prerun (the gates under test), the recipe with its own `--stop-after`
/ `--from-step --base` modes, the Part-A JSON tools/bench/stage_d1_dispA.json (its partA.file is the Part-B base), the
cycle-102 plan tools/bench/sim/disp/fixture_c106c_plan_disp_r7.json (git fe07299 - the plan r7 ran: op 41 r7_wait = copy_in),
the recorded run logs stage_d1_dispA_r1.log (103-2) and stage_d1_disp_c104B*.log (104). Each case is a separate child
process (the dry run installs COM stubs process-wide). No LabVIEW, no VI opened; the dry reads the base VI's md5 only.

PREDICTION CONTRACT (all must hold):
  C1 Part-B prerun (--from-step 33 --base <dispA>): X1 dry PASS, every gate X1..X10 PASS (X9 no copy_in; X10 same-mode record)
  C2 NEGATIVE Part-A prerun to op 40 (--stop-after 40): X1 PASS, X9 PASS, X10 FAIL - the 103-2 r1 record predicts >= 700 MB
  C3 Part-A prerun to op 33 (--stop-after 33, the PD216(f) cut): X10 PASS (r2's same-mode record)
  C4 NEGATIVE X9: the recipe's plan replaced by r7's plan (fixture) -> X9 FAIL naming op 41 copy_in r7_wait
  C5 the same fixture with the dry Stage's work == gscript.MOVE_DST -> X9 PASS (the precondition, not the plan, refuses in C4)
  C6 (review archive/peer/2026-09-27-c106c-selftest-x1.md s1; INVERTED by card 106-5, PD219(c) "find_graph uses the plan's
     own base graph"): Part-A 40 with NO graph argument -> X1 PASS on tools/bench/par1359_95_graph.json (plan_disp's base).
     Until 106-5 this case pinned the X1 FAIL ("DRY graph JSON for input md5"); C2/C3 now also run with NO graph argument.
Usage: py tools/bgrun.py --material --max-min 12 --log tools/bench/selftest_stage_prerun_c106c.log -- py -u tools/bench/selftest_stage_prerun_c106c.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py")
FIX = os.path.join(ROOT, "tools", "bench", "sim", "disp", "fixture_c106c_plan_disp_r7.json")
PARTA = os.path.join(ROOT, "tools", "bench", "stage_d1_dispA.json")
# case: (recipe argv, stop_after, from_step, fixture plan, work := MOVE_DST, {gate prefix: expected ok}, text in X9/X10 detail)
CASES = {"C1": ("B", None, 33, False, False, dict((("X%d" % i), True) for i in range(1, 11)), ""),
         "C2": ("A40", 40, None, False, False, {"X1": True, "X9": True, "X10": False}, "703.8"),
         "C3": ("A33", 33, None, False, False, {"X1": True, "X9": True, "X10": True}, ""),
         "C4": ("B", None, 33, True, False, {"X1": True, "X9": False}, "op 41 copy_in"),
         "C5": ("B", None, 33, True, True, {"X1": True, "X9": True}, ""),
         "C6": ("A40-nograph", 40, None, False, False, {"X1": True}, "graph tools/bench/par1359_95_graph.json")}


def child(case):
    import stage_prerun as SP
    mode, sa, fs, fix, mdst, _want, _txt = CASES[case]
    base = json.load(open(PARTA, encoding="utf-8"))["partA"]["file"]
    argv = {"B": ["--from-step", "33", "--base", base], "A40": ["--stop-after", "40"], "A33": ["--stop-after", "33"],
            "A40-nograph": ["--stop-after", "40"]}[mode]
    sys.argv = ["stage_prerun.py", "--prerun", RECIPE] + argv
    if fix:
        real_pf = SP.plan_files
        SP.plan_files = lambda recipe: ([FIX], real_pf(recipe)[1])
    if mdst:
        real_dry = SP.dry

        def dry_w(recipe, graph=None):
            tr = real_dry(recipe, graph)
            tr["works"] = [getattr(sys.modules.get("gscript"), "MOVE_DST", None)]
            return tr
        SP.dry = dry_w
    out = sys.stdout
    # card 106-5 (PD219(c)): NO case passes a graph any more - find_graph takes the plan's own base graph
    # (par1359_95_graph.json) for the S1 input of the Part-A cases, and the dispA step-33 graph for Part-B
    tr = SP.prerun(RECIPE, None, stop_after=sa, from_step=fs)
    sys.stdout = out
    g = dict((x[0].split(" ")[0], [x[1], x[2]]) for x in tr["prerun"]["gates"])
    g["X1"] = [g.get("X1", [None])[0], "dry {0}: {1} graph {2}".format(tr["status"], tr.get("first_fail"), tr.get("graph"))]
    print("CASEOUT " + json.dumps({"case": case, "x1": tr["status"], "gates": g, "mem": tr.get("mem_margin")}, default=str),
          flush=True)


def main():
    import protocol as P
    npass, nfail, first = 0, 0, None
    for case, (_m, _sa, _fs, _fx, _md, want, txt) in CASES.items():
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--case", case], cwd=ROOT,
                           capture_output=True, text=True, timeout=400)
        line = [ln for ln in p.stdout.splitlines() if ln.startswith("CASEOUT ")]
        r = json.loads(line[-1][8:]) if line else {"x1": None, "gates": {}, "err": (p.stderr or p.stdout)[-600:]}
        g = r.get("gates") or {}
        got = dict((k, (g.get(k) or [None])[0]) for k in want)
        det = " | ".join("{0}: {1}".format(k, (g.get(k) or [None, ""])[1]) for k in ("X1", "X9", "X10") if k in want)
        ok = bool(g) and got == want and (not txt or txt in det)
        npass, nfail = npass + ok, nfail + (not ok)
        lab = "{0} expected {1}{2}".format(case, want if case != "C1" else "X1..X10 all PASS", " with '{0}'".format(txt) if txt else "")
        first = first or (None if ok else lab)
        print("  {0}  {1}  -> got {2} | {3} | mem {4}{5}".format("PASS" if ok else "FAIL", lab, got, det[:700],
              json.dumps(r.get("mem"), default=str)[:400], "" if line else " | " + str(r.get("err"))), flush=True)
    print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
    print(P.result_line(P.make_result(npass, nfail, first, status="PASS" if not nfail else "FAIL")), flush=True)
    return 0 if not nfail else 1


if __name__ == "__main__":
    if "--case" in sys.argv:
        child(sys.argv[sys.argv.index("--case") + 1])
    else:
        sys.exit(main())
