# ---
# labview: none
# hardware: none
# ---
"""card 155-a1-1 regression record: stagexec.compile_plan over EVERY stored plan (tools/bench/plan_*.json).

  py tools/bench/prep_c155_a1_1_regress.py before   -> tools/bench/prep_c155_a1_1_compile_before.json (op lists or errors)
  py tools/bench/prep_c155_a1_1_regress.py after    -> same read with the edited stagexec; compares to the before file

Prediction contract (after): every plan's compile result (op list, kinds/order/args, or the ExecStop text) is EQUAL to
before, except plans whose compile depends on a BASE-graph Case (none expected among the stored plans; any listed
difference is reported, not accepted). P5-1a's plan (plan_ring_p5s01a.json, ed62e8d6) is checked by name.
Existing prior art: stagexec.compile_plan is the one entry point the recipes / stagekit use (stagekit.py:1927)."""
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

OUT = os.path.join(HERE, "prep_c155_a1_1_compile_before.json")
P5 = "tools/bench/plan_ring_p5s01a.json"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def compile_all():
    res = {}
    for p in sorted(glob.glob(os.path.join(HERE, "plan_*.json"))):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        try:
            plan = json.load(open(p, encoding="utf-8"))
            if not isinstance(plan, dict) or "actions" not in plan:
                res[rel] = {"skip": "no actions"}
                continue
            res[rel] = {"md5": md5(p), "ops": SX.compile_plan(plan)}
        except Exception as e:  # noqa: BLE001 - the error text IS the record
            res[rel] = {"md5": md5(p), "error": "{0}: {1}".format(type(e).__name__, e)}
    return res


mode = sys.argv[1] if len(sys.argv) > 1 else "before"
now = compile_all()
n_ops = sum(1 for v in now.values() if "ops" in v)
n_err = sum(1 for v in now.values() if "error" in v)
print("FACT stagexec md5", md5(os.path.join(ROOT, "tools", "stagexec.py")), "stagesim md5",
      md5(os.path.join(ROOT, "tools", "stagesim.py")))
print("FACT plans", len(now), "compiled", n_ops, "refused", n_err, "skipped", len(now) - n_ops - n_err)
print("FACT P5-1a", P5, now.get(P5, {}).get("md5"), "ops", len(now.get(P5, {}).get("ops") or []),
      [o["kind"] for o in now.get(P5, {}).get("ops") or []])
gates = {"pass": 0, "fail": 0}
first = None
if mode == "before":
    json.dump(now, open(OUT, "w", encoding="utf-8"), indent=0, sort_keys=True, default=str)
    print("FACT before list written", os.path.relpath(OUT, ROOT), md5(OUT))
    gates["pass"] += 1
else:
    before = json.load(open(OUT, encoding="utf-8"))
    now_j = json.loads(json.dumps(now, sort_keys=True, default=str))
    diff = sorted(k for k in set(before) | set(now_j) if before.get(k) != now_j.get(k))
    for k in diff:
        print("DIFF", k, "\n  before", json.dumps(before.get(k))[:600], "\n  after ", json.dumps(now_j.get(k))[:600])
    ok = not diff
    print("GATE {0} | every stored plan compiles EQUAL to before ({1} plans, {2} differ) | {3}".format(
        "PASS" if ok else "FAIL", len(now_j), len(diff), diff[:10]))
    gates["pass" if ok else "fail"] += 1
    if not ok:
        first = "every stored plan compiles EQUAL to before"
    p5 = before.get(P5) == now_j.get(P5) and P5 in before and "ops" in before[P5]
    print("GATE {0} | P5-1a plan {1} ({2}) recompiles EQUAL: {3} ops before, {4} after".format(
        "PASS" if p5 else "FAIL", P5, (before.get(P5) or {}).get("md5"), len((before.get(P5) or {}).get("ops") or []),
        len((now_j.get(P5) or {}).get("ops") or [])))
    gates["pass" if p5 else "fail"] += 1
    if not p5 and first is None:
        first = "P5-1a plan recompiles EQUAL"
print(protocol.result_line({"status": "PASS" if not gates["fail"] else "FAIL", "gates": gates, "first_fail": first,
                            "artefacts": []}))
