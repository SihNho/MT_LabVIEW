r"""selftest_stage_prerun_c115c - card 115-3 F1/F2: stage_prerun X5 NARROWED (delete ops counted against plan delete rows).
PURE PYTHON, no LabVIEW.

Existed first: selftest_stage_prerun_c115a.py (shape copied); stage_prerun X5 was inline in prerun() and is now
stage_prerun.x5_count (same wire-count arithmetic; the delete count is the one addition, JUDGEMENT card 115-3).
FAILURES ON RECORD BEFORE F1 (PD229(c)): none - tools/bench/diag_c115c_regress_before.log 11/0; the one X5 failure on
record is the one F1 targets: stage_d1_l2r1_prerun.log 'ops 11 vs plan wire rows 0' (115-2 BLOCKED).
Prediction contract: T1-T9 PASS -
  T1 plan_l2r1 (17 actions) + the verbs it compiles to (11 delete_wire, 6 delete_object) -> X5 ok, delete 11/6 == 11/6
  T2 same + ONE unplanned delete_wire -> FAIL          T3 same + ONE unplanned connect -> FAIL
  T4 one delete_object missing -> FAIL                 T5 a delete_wire swapped for a delete_object -> FAIL (per kind)
  T6 decision-row path: rows [delete_wire] + verb delete_wire -> ok; no verb -> FAIL
  T7 PART-A window stop_after=5: the first 5 verbs -> ok; all 17 -> FAIL
  T8 unchanged wire rule: an unplanned remove_bad_wires still counts as a wiring op -> FAIL; empty plan, no verbs -> ok
  T9 `stage_prerun.py --prerun tools/recipes/stage_d1_l2r1.py --no-record`: an X5 PASS line naming delete 6/11, rc 0
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stage_prerun_c115c.log -- py -u tools/bench/selftest_stage_prerun_c115c.py
"""
import os, subprocess, sys                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)  # noqa: E702
sys.path.insert(0, TOOLS)
import stage_prerun as SP, protocol                                                  # noqa: E401,E402
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:500]), flush=True)


P = os.path.join(HERE, "plan_l2r1.json")
chk = SP.stageplan_check(P)
spc = {P: chk}
V = [o["kind"] for o in chk[3]]
gate("T0 plan_l2r1 stageplan_check ok, 17 compiled ops = 11 delete_wire + 6 delete_object",
     chk[0] and len(V) == 17 and V.count("delete_wire") == 11 and V.count("delete_object") == 6, (chk[1], V))
r1 = SP.x5_count(V, [], spc)
gate("T1 plan_l2r1 + its own 17 verbs -> X5 ok", r1[0], r1[1])
r2 = SP.x5_count(V + ["delete_wire"], [], spc)
gate("T2 + one unplanned delete_wire -> FAIL", not r2[0], r2[1])
r3 = SP.x5_count(V + ["connect"], [], spc)
gate("T3 + one unplanned connect -> FAIL", not r3[0], r3[1])
V4 = list(V); V4.remove("delete_object")                                             # noqa: E702
r4 = SP.x5_count(V4, [], spc)
gate("T4 one delete_object missing -> FAIL", not r4[0], r4[1])
V5 = list(V); V5[V5.index("delete_wire")] = "delete_object"                         # noqa: E702
r5 = SP.x5_count(V5, [], spc)
gate("T5 a delete_wire swapped for a delete_object (same total 17) -> FAIL", not r5[0], r5[1])
r6a, r6b = SP.x5_count(["delete_wire"], [{"action": "delete_wire"}], {}), SP.x5_count([], [{"action": "delete_wire"}], {})
gate("T6 decision row delete_wire: verb present -> ok; absent -> FAIL", r6a[0] and not r6b[0], (r6a[1], r6b[1]))
r7a, r7b = SP.x5_count(V[:5], [], spc, stop_after=5), SP.x5_count(V, [], spc, stop_after=5)
gate("T7 PART-A stop_after=5: first 5 verbs -> ok; all 17 -> FAIL", r7a[0] and not r7b[0], (r7a[1], r7b[1]))
r8a, r8b = SP.x5_count(["remove_bad_wires"], [], {}), SP.x5_count([], [], {})
gate("T8 unplanned remove_bad_wires still a wiring op -> FAIL; empty -> ok", not r8a[0] and r8b[0], (r8a[1], r8b[1]))
p = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--prerun",
                    os.path.join(TOOLS, "recipes", "stage_d1_l2r1.py"), "--no-record"], cwd=ROOT, capture_output=True,
                   text=True, timeout=600)
x5 = [l for l in p.stdout.splitlines() if " X5 " in l]
gate("T9 --prerun stage_d1_l2r1.py --no-record: X5 PASS with delete {'delete_object': 6, 'delete_wire': 11} both sides, rc 0",
     p.returncode == 0 and x5 and x5[0].lstrip().startswith("PASS") and
     x5[0].count("{'delete_object': 6, 'delete_wire': 11}") == 2, (p.returncode, x5[:2], p.stdout.splitlines()[-3:]))
n = sum(1 for _l, ok in G if ok)
first = next((l for l, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n, len(G) - n, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
sys.exit(0 if first is None else 1)
