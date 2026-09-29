"""selftest_guard - offline check of uc_guard.own_session_file on the smoke's real refusals (card chat-B3).

PREDICTION: every refused Read/Grep of the smoke whose path carries the cell's own session_id is now ALLOWED; the same
path presented with ANOTHER arm's session_id is REFUSED; the main-checkout canary and a git command stay REFUSED.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["MATBENCH_WT"] = os.path.join(os.environ.get("TEMP", ""), "ucb", "L3")
os.environ["MATBENCH_LOG"] = os.path.join(os.environ.get("TEMP", ""), "ucb_selftest_calls.jsonl")
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "matbench"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "decbench"))
sys.path.insert(0, HERE)
import uc_guard as UG  # noqa: E402

runs = os.path.join(HERE, "runs", "smoke", "L3")
sids, refused = {}, []
for arm in ("SMX_r1", "SH_r1", "UC_r1"):
    for ln in open(os.path.join(runs, arm, "c0", "cell.log"), encoding="utf-8", errors="replace"):
        if ln.startswith("{") and '"subtype":"init"' in ln:
            sids[arm] = json.loads(ln)["session_id"]
            break
    for ln in open(os.path.join(runs, arm, "c0", "calls.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        if r["decision"] == "REFUSE" and r["tool"] in ("Read", "Grep"):
            refused.append((arm, r["tool"], r["cmd"]))
ok, bad = 0, []
for arm, tool, path in refused:
    own = UG.decide({"tool_name": tool, "tool_input": {"file_path": path}, "session_id": sids[arm]})
    other = next(s for a, s in sids.items() if a != arm)
    oth = UG.decide({"tool_name": tool, "tool_input": {"file_path": path}, "session_id": other})
    if own is None and oth:
        ok += 1
    else:
        bad.append("%s %s own=%s other=%s %s" % (arm, tool, own, oth, path[-60:]))
canary = os.path.join(HERE, "canary_main.txt")
if UG.decide({"tool_name": "Read", "tool_input": {"file_path": canary}, "session_id": sids["UC_r1"]}) is None:
    bad.append("canary read allowed")
if UG.decide({"tool_name": "Bash", "tool_input": {"command": "git log -1"}, "session_id": sids["UC_r1"]}) is None:
    bad.append("git allowed")
print("SELFTEST refused-in-smoke %d, fixed %d; bad %s" % (len(refused), ok, bad))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if bad or not refused else "PASS",
                              "gates": {"pass": ok + 2 - sum(1 for b in bad if "allowed" in b), "fail": len(bad)},
                              "first_fail": bad[0] if bad else None, "artefacts": []}))
