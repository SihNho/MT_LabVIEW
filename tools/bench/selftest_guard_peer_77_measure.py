r"""selftest_guard_peer_77_measure - card 77-1 pass 3: READ-ONLY measurement of how the patched guard_peer now treats
tools/bench/selftest_make_default.log. Calls only guard_peer's selection/binding functions (newest_failing_log,
failure_names, newest_bound_peer, same_row_review); does NOT call main(), so it writes nothing, runs no ladder and makes
no API call. NO LabVIEW. Prediction: the log is in the selection (not exempt); whether a review binds it is the FACT.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
for _p in (TOOLS, HERE, os.path.join(TOOLS, "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import guard_peer as gp   # noqa: E402
import protocol           # noqa: E402

NP = NF = 0
FIRST = None


def gate(ok, label, detail=""):
    global NP, NF, FIRST
    NP, NF = NP + bool(ok), NF + (not ok)
    FIRST = FIRST or (None if ok else label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))


log = os.path.join(gp.BENCH, "selftest_make_default.log")
start = gp.logclass.last_bgrun_command(log)
print("FACT last BGRUN START command: %s" % start)
gate(not gp.selftest_exempt(start), "M1 selftest_make_default.log is NOT exempt under the command rule")
with open(log, "r", encoding="utf-8", errors="replace") as f:
    text = f.read()
failed, first = gp.log_failure(text, os.path.getmtime(log))
print("FACT log_failure: failed=%s first=%s" % (failed, first))
nf = gp.newest_failing_log()
print("FACT newest_failing_log -> %s" % (os.path.basename(nf[0]) if nf else None))
last = text.rsplit("BGRUN START", 1)[-1]
names = gp.failure_names(log, last)
print("FACT failure_names -> %s" % sorted(names))
hit, rejected = gp.newest_bound_peer(os.path.getmtime(log), names)
print("FACT newest_bound_peer -> hit=%s rejected=%s" % (hit, rejected))
sr = gp.same_row_review(log, last)
print("FACT same_row_review -> %s" % (sr,))
print("\n=== selftest_guard_peer_77_measure: %d pass / %d fail ===" % (NP, NF))
print(protocol.result_line(protocol.make_result(NP, NF, FIRST)))
sys.exit(0 if NF == 0 else 1)
