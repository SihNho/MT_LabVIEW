"""diag_c130_2_baseline - card 130-2: is a self-test NEGATIVE that stop_gate now allows also allowed by stop_record ALONE
(i.e. a pre-existing hole, not a regression of the fp-22 filter)? Offline, store stubbed, nothing executed.
PREDICTION: N10 (cd tools/recipes && py <basename>) allowed by stop_record alone too (path token without a separator);
an unquoted absolute path with spaces is not a runnable command; the QUOTED absolute forms are refused by both."""
import os, sys                                                                     # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")]
os.chdir(ROOT)
import protocol as P, stop_record as SR, guard_bash as GB                         # noqa: E401,E402
R = "tools/recipes/stage_d1_ring_p3b1.py"
SR.load_records = lambda: [{"recipe_path": R, "reviewed_sha256": "0" * 64, "review_file": "archive/peer/none.md",
                            "verdict": ["x"], "released": None}]
SR.save_records = lambda r: None
GB.note = lambda *a, **k: None
sys.stderr = open(os.devnull, "w")
RT = ROOT.replace("\\", "/")
rows = [("N10", "cd tools/recipes && py stage_d1_ring_p3b1.py"), ("N20u", "py -u %s/%s" % (RT, R)),
        ("N20q", 'py -u "%s/%s"' % (RT, R)), ("N20qb", 'py tools/bgrun.py --log x -- py -u "%s/%s"' % (RT, R))]
for k, c in rows:
    print("%-6s stop_record_alone_allows=%s stop_gate_rc=%d  %s" % (k, SR.check_command(c)[0], GB.stop_gate(c, "Bash"), c[:80]),
          flush=True)
print(P.result_line(P.make_result(len(rows), 0)), flush=True)
