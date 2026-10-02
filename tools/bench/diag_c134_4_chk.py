"""Card 134-4: which of the step-3/5 command forms does protocol.check_command (card flags) accept? Offline, read-only."""
import sys, json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(R)
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as P                                                       # noqa: E402
c = json.load(open("tools/bench/cards/task_134-4.json"))
c["_md5"] = json.load(open("tools/bench/cards/requires_134-4.json")).get("card_md5")
pre = "py tools/bgrun.py --material --max-min 3 --log tools/bench/x.log -- py -u "
for s in ["tools/bench/selftest_c134_2_gates.py", "tools/bench/selftest_c134_1_fsmap.py", "tools/bench/c125_1_offline_measure.py",
          "tools/bench/selftest_c134_1_dry.py", "tools/bench/diag_c134_1_finalize_b.py x.json",
          "tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p3b2b.py",
          "tools/stage_prerun.py --prerun tools/recipes/stage_d1_ring_p3b2b.py"]:
    print(s, "->", P.check_command(c, pre + s))
print(P.result_line(P.make_result(1, 0, None, [])))
