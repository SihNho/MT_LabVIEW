# ---
# labview: none
# hardware: none
# ---
r"""selftest_c148_guard_fp - card 148-a1-1: the hook fixes for gate-fp fp-53 (guard_assign.card_outside memory-token window)
and fp-57 (guard_write.open_card_pins counting a killed-and-resumed card as open). No LabVIEW, no COM, no subprocess; reads
two real cards, writes only temp files.

WHAT EXISTED: selftest_assign_flow.py (guard_assign end to end) and selftest_c_e3.py (guard_write checks); neither covers a
memory token in a clause next to another clause's verb, nor a resumed card. This file adds those cases.

PREDICTION CONTRACT
  A1 fp-53: the REAL card task_146-a2-1.json under a purpose that names no memory token -> card_outside == '' (was the
     'card text changes a memory limit: memory_model next to change' refusal)
  A2 negative: a card whose goal says "raise the X10 limit to 700" -> still refused (memory limit)
  A3 negative: "change X10 and keep memory_model unchanged" (verb in the SAME clause) -> still refused
  W1 fp-57: temp cards dir - task_K (no result, pins file F at a stale md5) + task_R (has result, goal "RESUME of killed card K")
     -> open_card_pins(F) == []
  W2 negative: same without task_R's result file -> the stale pin IS reported (one line naming card K)
  W3 negative: a task_R with result whose goal names ANOTHER card -> K's stale pin still reported
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import guard_assign as GA  # noqa: E402
import guard_write as GW  # noqa: E402
import protocol as P  # noqa: E402

G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:240]), flush=True)


cfg = json.load(open(os.path.join(TOOLS, "bench", "assign", "assign_config.json"), encoding="utf-8"))
purpose = {"act": "build P4 session 6", "pass": ["s06 adopted"], "note": ""}
card = json.load(open(os.path.join(TOOLS, "bench", "cards", "task_146-a2-1.json"), encoding="utf-8"))
card = dict(card, advances=[], unblocks=None)          # scope is not under test here
r1 = GA.card_outside(card, purpose, cfg)
gate("A1 fp-53: real task_146-a2-1 card not refused as a memory-limit change", r1 == "", r1)
base = {"goal": "", "pass": [], "flags": {"write": ["tools/bench/diag_x*"]}}
r2 = GA.card_outside(dict(base, goal="raise the X10 limit to 700 for s06"), purpose, cfg)
gate("A2 negative: 'raise the X10 limit' still refused", "memory limit" in r2, r2)
r3 = GA.card_outside(dict(base, goal="change X10 and keep memory_model unchanged"), purpose, cfg)
gate("A3 negative: verb in the same clause still refused", "memory limit" in r3, r3)

tmp = tempfile.mkdtemp(prefix="c148gw_")
F = os.path.join(tmp, "pinned.json")
open(F, "w", encoding="utf-8").write('{"v": 2}\n')


def put(name, obj):
    with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
        json.dump(obj, f)


put("task_K.json", {"schema": "task/1", "id": "K", "goal": "edit things", "inputs": [{"path": F, "md5": "0" * 32}],
                    "flags": {"write": ["tools/bench/other*"]}})
GW.CARDS = tmp
put("task_R.json", {"schema": "task/1", "id": "R", "goal": "RESUME of killed card K (brief_K.md): finish it", "inputs": []})
put("result_R.json", {"schema": "result/1", "id": "R", "status": "FAIL"})
w1 = GW.open_card_pins(F)
gate("W1 fp-57: card K resumed by R (R has a result) -> no open pin", w1 == [], w1)
os.remove(os.path.join(tmp, "result_R.json"))
w2 = GW.open_card_pins(F)
gate("W2 negative: R has no result -> K's stale pin reported", len(w2) == 1 and "card K " in w2[0], w2)
put("task_R.json", {"schema": "task/1", "id": "R", "goal": "RESUME of killed card Z: other", "inputs": []})
put("result_R.json", {"schema": "result/1", "id": "R", "status": "PASS"})
w3 = GW.open_card_pins(F)
gate("W3 negative: R resumes another card -> K's stale pin reported", len(w3) == 1 and "card K " in w3[0], w3)

n_pass = sum(1 for _l, ok in G if ok)
n_fail = len(G) - n_pass
first = next((lb for lb, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, n_fail))
print(P.result_line(P.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
