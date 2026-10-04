"""assignbench local chain (card chat-B6): make_cases -> --lock -> stub hit dry run (reps 2, with blind stub) ->
stub miss (scoring sanity: M1 must be 0). No real model cell is started here. Ends with a RESULT line.
PREDICTION: make_cases 21/0, lock 21/0 leak PASS, stub hit PASS (168 arm-runs M1 = 1, F1 = 0, blind present),
stub miss: every M1 = 0."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
steps = [["make_cases.py"], ["assignbench.py", "--lock"],
         ["assignbench.py", "--stub", "hit", "--reps", "2", "--par", "8", "--tag", "stub_hit"],
         ["assignbench.py", "--stub", "miss", "--reps", "1", "--par", "8", "--no-blind", "--tag", "stub_miss"]]
if "--no-miss" in sys.argv:          # chat-B6 follow-up 2026-10-04: re-run make_cases, lock and stub hit only
    steps = steps[:3]
fails, rc_all = [], 0
for st in steps:
    p = subprocess.run([sys.executable, "-u", os.path.join(HERE, st[0])] + st[1:], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    res = [ln for ln in p.stdout.splitlines() if ln.startswith("RESULT ")]
    print("STEP %s rc %d %s" % (" ".join(st), p.returncode, res[-1] if res else "(no RESULT)"), flush=True)
    print("\n".join(ln for ln in p.stdout.splitlines() if ln.startswith(("LOCK", "CASE", "ACTIONS", "REFUSED",
                                                                          "WORKTREES", "INVALID", "BLIND"))), flush=True)
    if p.stderr.strip():
        print("STDERR " + p.stderr[-1500:], flush=True)
    if st[-1] != "stub_miss" and p.returncode:
        fails.append(" ".join(st))
        break
if not fails and len(steps) == 4:
    d = json.load(open(os.path.join(HERE, "results_stub_miss.json"), encoding="utf-8"))
    bad = [r["case"] for r in d["records"] if (r.get("mech") or {}).get("M1")]
    print("STUB MISS M1 hits %d of %d" % (len(bad), len(d["records"])), flush=True)
    if bad:
        fails.append("stub miss scored M1 on %s" % bad[:3])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                              "gates": {"pass": len(steps) - len(fails), "fail": len(fails)},
                              "first_fail": fails[0] if fails else None, "artefacts": []}), flush=True)
sys.exit(1 if fails else 0)
