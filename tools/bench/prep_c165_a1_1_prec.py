# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_165-1-1.json
# ---
"""Card 165-1-1 step 3: was the SOURCE #3934 of the adopted `connect_term_uid #24139 <- #3934` (diag_c161_p5s02b_scratch.log:97)
already WIRED when that op ran? Read from plan_ring_p5s02b.json's own predicted step state just before the op's first action
(finalized.step_files, md5-checked) - the state the scratch run compared diff 0 against (STEPX 05, :102).

Prediction contract: the op's acts are [9, 10, 11] (t_go, w_gout, w_gr); in the step-8 state row #3934 is_source True with a
non-zero wire_uid; the plan action naming #3934 is printed."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

P = os.path.join(HERE, "plan_ring_p5s02b.json")
pl = json.load(open(P, encoding="utf-8"))
print("PLAN md5", hashlib.md5(open(P, "rb").read()).hexdigest())
for i, a in enumerate(pl["actions"], 1):
    if a.get("id") in ("dw_go", "t_go", "w_gout", "w_gr"):
        print("ACT", i, json.dumps(a)[:400])
G = [0, 0, None]
sf = dict((int(s["n"]), s) for s in pl["finalized"]["step_files"])
for n in (8, 11):
    s = sf.get(n)
    p = os.path.join(ROOT, s["path"]) if s else None
    if not p or not os.path.isfile(p) or hashlib.md5(open(p, "rb").read()).hexdigest() != s["md5"]:
        print("STEP", n, "missing or md5 differs", s)
        G[1] += 1
        continue
    st = json.load(open(p, encoding="utf-8"))["state"]
    rs = [r for r in st["terminals"] if r["term_uid"] in (3934, 24139)]
    print("STEP {0} {1} md5 {2}".format(n, s["path"], s["md5"]))
    for r in rs:
        print("   ", json.dumps(r))
    if n == 8:
        r = next((x for x in rs if x["term_uid"] == 3934), None)
        ok = bool(r and r["is_source"] and r["wire_uid"])
        G[0 if ok else 1] += 1
        print("  {0}  #3934 is a WIRED source before the op".format("PASS" if ok else "FAIL"))
print(protocol.result_line(protocol.make_result(G[0], G[1], None if not G[1] else "precedent", [])), flush=True)
sys.exit(1 if G[1] else 0)
