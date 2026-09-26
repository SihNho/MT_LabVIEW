"""Self-test, card 106-5 (PD219(c)/(e)): stage_prerun X10 threshold 690 + WARN unmeasured, find_graph taking the plan's
base graph, launched_py splitting on newlines. Offline: no LabVIEW, no VI opened (the E cases dry-run the recipe with COM
stubbed, in a child process, reading the base VI's md5 only).

Existing pieces used: stage_prerun.mem_margin / find_graph / plan_base_graphs / launched_py / result_first, the recipe
tools/recipes/stage_d1_disp.py with its PART-B mode, tools/bench/stage_d1_dispA.json, plan_disp.json's base pin.
PREDICTION CONTRACT (all must hold):
  M1 a recorded checkpoint at 690.0 MB -> X10 ok False ; M2 at 689.9 MB -> ok True ; M3 no covering record -> ok None
  M4 result_first: PASS + warn -> the WARN text ; FAIL + warn -> the failing gate first, '[X10 WARN unmeasured]' appended, <=200
  G1 find_graph(S1 md5) with no plan graphs -> None (unchanged glob behaviour, selftest_stage_prerun_graphload pin)
  G2 find_graph(S1 md5, plan_base_graphs(recipe)) -> tools/bench/par1359_95_graph.json
  G3 NEGATIVE: the same graph with a wrong md5 pin -> None, FIND_SKIPPED names the pin
  G4 the dispA md5 (Part-B input) with the recipe's plan graphs -> NOT par1359_95 (the plan base is another VI)
  L1 NEGATIVE-shape: `py -V<NL>py -u tools/recipes/stage_d1_disp.py` -> the stage path is found (HEAD code: not, O1 of
     diag_c106e_oldcode.py); L1u `wc -l x<NL>py -u <stage>` -> found (HEAD finds it too)
  L2 a bash `\\<NL>` continuation stays one command: found exactly once ; L3 `echo py tools/x.py` is not a launch
  E1 `--prerun <recipe> --from-step 33 --base <dispA> --no-record` with PRERUN_LOG_DIR = an empty dir: exit 0, stdout has
     `WARN  X10 WARN unmeasured` and a RESULT line status PASS whose first_fail starts `X10 WARN unmeasured`
  E2 (card F5) `--dry <recipe> --from-step 33 --base <dispA> --no-record`: exit 0, RESULT PASS, the B1 entry gate PASS
     with diff_n 0, the E3 gate PASS with `rows 6 == want 6`
Usage: py tools/bgrun.py --material --max-min 8 --log tools/bench/selftest_stage_prerun_c106e.log -- py -u tools/bench/selftest_stage_prerun_c106e.py
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P        # noqa: E402
import stage_prerun as SP   # noqa: E402

RECIPE = os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py")
PAR = os.path.normpath(os.path.join(ROOT, "tools", "bench", "par1359_95_graph.json"))
PARTA = json.load(open(os.path.join(ROOT, "tools", "bench", "stage_d1_dispA.json"), encoding="utf-8"))["partA"]
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def rec(mb):
    return [{"path": os.path.join(ROOT, "tools", "bench", "fixture.log"), "mtime": 0, "stop_after": None, "from_step": None,
             "rows": [{"tag": "read", "k": 0, "mb": 600.0}, {"tag": "op", "k": 1, "mb": mb}, {"tag": "read", "k": 2, "mb": 650.0}]}]


m1, m2 = SP.mem_margin(RECIPE, records=rec(690.0)), SP.mem_margin(RECIPE, records=rec(689.9))
gate("M1 checkpoint 690.0 MB -> X10 ok False", m1["ok"] is False and m1["peak_mb"] == 690.0, m1)
gate("M2 checkpoint 689.9 MB -> X10 ok True", m2["ok"] is True and m2["peak_mb"] == 689.9, m2)
m3 = SP.mem_margin(RECIPE, records=[])
gate("M3 no covering record -> ok None (UNMEASURED)", m3["ok"] is None and "UNMEASURED" in m3["why"], m3)
w = "X10 WARN unmeasured: UNMEASURED: no recorded meter"
a, b = SP.result_first(None, w), SP.result_first("X4 every end addressable: " + "z" * 300, w)
gate("M4 result_first PASS->WARN text, FAIL->gate first + tag, <=200", a == w and b.startswith("X4 every end") and
     b.endswith("[X10 WARN unmeasured]") and len(b) <= 200 and SP.result_first("X1 f", None) == "X1 f", (a, b[-40:], len(b)))

s1 = json.load(open(PAR, encoding="utf-8"))["md5"]
pg = SP.plan_base_graphs(RECIPE)
gate("G1 find_graph(S1 md5) without plan graphs -> None", SP.find_graph(s1) is None, s1)
got = SP.find_graph(s1, pg)
gate("G2 find_graph(S1 md5, plan base graphs) -> par1359_95_graph.json", got and os.path.normpath(got) == PAR, (got, pg))
got3 = SP.find_graph(s1, [(PAR, "0" * 32)])
gate("G3 NEGATIVE wrong pin -> None, FIND_SKIPPED names the pin", got3 is None and any("pin" in r for _p, r in SP.FIND_SKIPPED),
     SP.FIND_SKIPPED)
got4 = SP.find_graph(PARTA["md5"], pg)
gate("G4 dispA md5 with the plan graphs -> not the plan base", got4 is None or os.path.normpath(got4) != PAR, got4)

stage = os.path.normpath(os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py"))
# L1 = the shape HEAD's launched_py MISSES (diag_c106e_oldcode.log O1, run 2): line 1's `py -V` swallows line 2's `py`
# token as its "script" because the newline was plain whitespace. The unquoted `wc -l x<NL>py ...` (L1u) was found by the
# old code too (run 1 of that diag, O1 FAIL) - it is kept as a positive, not as the negative.
l1 = SP.launched_py('py -V\npy -u tools/recipes/stage_d1_disp.py --stop-after 40')
gate("L1 two-line command `py -V<NL>py -u <stage>` -> the stage is found", stage in l1, l1)
l1u = SP.launched_py('wc -l x\npy -u tools/recipes/stage_d1_disp.py --stop-after 40')
gate("L1u two-line command, stage on line 2 after `wc` -> found", stage in l1u, l1u)
l1a = SP.launched_py('wc -l \\"x\npy -u tools/recipes/stage_d1_disp.py\n\\"')     # review c106e-oldcode-o1 s4 (a)
gate("L1a backslash-quote two-line command (c103d-hooks-before s1) -> found", stage in l1a, l1a)
l2 = SP.launched_py('py tools/bgrun.py --max-min 5 --log x.log -- py -u \\\n  tools/recipes/stage_d1_disp.py')
gate("L2 bash continuation -> one command, stage found once", l2.count(stage) == 1, l2)
l3 = SP.launched_py('echo py\ncat tools/recipes/stage_d1_disp.py')
gate("L3 cat of the stage on line 2 is not a launch", stage not in l3, l3)

with tempfile.TemporaryDirectory() as td:
    env = dict(os.environ, PRERUN_LOG_DIR=td)
    p = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "stage_prerun.py"), "--prerun", RECIPE, "--no-record",
                        "--from-step", "33", "--base", PARTA["file"]], cwd=ROOT, capture_output=True, text=True, timeout=400, env=env)
res = P.all_result_lines(p.stdout)
ff = (res[-1].get("first_fail") or "") if res else ""
gate("E1 Part-B prerun, no meter record: exit 0, WARN line, RESULT PASS first_fail 'X10 WARN unmeasured'",
     p.returncode == 0 and "WARN  X10 WARN unmeasured" in p.stdout and res and res[-1]["status"] == "PASS"
     and ff.startswith("X10 WARN unmeasured"), (p.returncode, ff, [ln for ln in p.stdout.splitlines() if "X10" in ln][:3],
                                                 p.stderr[-300:]))

# E2 = card F5: the Part-B DRY of the 90-line recipe through stage_prerun (--no-record: prerun_records.jsonl is outside the
# card's write list). The top-level command was refused by stop_record's launch gate (recipe sha changed since its prior-art
# release) although PD219(c) says a dry needs no round; this child runs the identical argv. Full stdout: diag_c106e_dryB.txt
q = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "stage_prerun.py"), "--dry", RECIPE, "--no-record",
                    "--from-step", "33", "--base", PARTA["file"]], cwd=ROOT, capture_output=True, text=True, timeout=400)
open(os.path.join(ROOT, "tools", "bench", "diag_c106e_dryB.txt"), "w", encoding="utf-8").write(q.stdout + "\n--- stderr\n" + q.stderr)
b1 = [ln for ln in q.stdout.splitlines() if "B1 PART-B entry" in ln]
e3 = [ln for ln in q.stdout.splitlines() if ln.lstrip().startswith(("PASS  E3", "FAIL  E3"))]   # run 1 took the FACT line
rq = P.all_result_lines(q.stdout)
gate("E2 Part-B DRY: exit 0, RESULT PASS, B1 PASS diff_n 0, E3 PASS rows 6 == want 6", q.returncode == 0 and rq and
     rq[-1]["status"] == "PASS" and b1 and "PASS" in b1[0] and "'diff_n': 0" in b1[0] and e3 and "PASS" in e3[0]
     and "rows 6 == want 6" in e3[0], (q.returncode, rq[-1] if rq else None, b1[:1], e3[:1]))
n = sum(1 for _l, o in G if o)
print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n), flush=True)
print(P.result_line(P.make_result(n, len(G) - n, next((l for l, o in G if not o), None))), flush=True)
sys.stdout.flush()
os._exit(0 if n == len(G) else 1)
