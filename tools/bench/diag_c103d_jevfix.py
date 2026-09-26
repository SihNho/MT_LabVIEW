"""card 103-4: the discriminating test of archive/peer/2026-09-27-c103d-guard-bash-jev.md s7 (offline, no hook, no LabVIEW):
selftest_guard_bash_jev's fixture BG is refused by the stage launch gate (chat-N1 classifier) independent of the 103-4 edits."""
import os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T); os.chdir(os.path.dirname(T))
import stage_prerun as s, protocol
BG = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/bench/diag_c88_brokenwires.py"
c1 = s.vi_modifying_calls("tools/bench/diag_c88_brokenwires.py"); r1 = s.check_launch(BG)
s.VI_MOD_EXEMPT_PATHS = {}
r2 = s.check_launch(BG)
print("CALLS", c1); print("LAUNCH", r1[0], r1[1][:200].replace("\n", " | ")); print("LAUNCH no-exemption", r2[0], r2[1][:200].replace("\n", " | "))
ok = c1 == ["discard_work"] and r1[0] is False and "chat-N1" in r1[1] and r1 == r2
print("CLAIM", "HOLDS" if ok else "NOT SHOWN")
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "claim not shown")))
