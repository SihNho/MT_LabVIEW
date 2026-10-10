# ---
# labview: none
# hardware: none
# evidence: tools/bench/selftest_c156_passwire_c160_f3_1.log
# ---
r"""Card 160-f3-2: MEASURE the compile diff of plan_ring_p5s02r_all.json (15da9551) against the before-list
tools/bench/sim/ring_p5s02pw/compile_before.json (7ca1c4c4, 40 ops), op by op, and decide by the measured diff only.
WHAT EXISTED FIRST: the before-list writer = prep_c156_a1_2_lib.compile_all() + json.dump(indent=0, sort_keys=True)
(prep_c156_a1_2_measure.py:108-112); the checkpoint set = stagexec.checkpoint_ops (stagexec.py:2143). Both are CALLED here.
PREDICTION (gates):
 D1 op count equal (40) and checkpoint_ops equal before / after.
 D2 every differing op index carries action t_go or t_ho, same acts, before kind != connect_term_uid, after kind
    connect_term_uid variant register_end_case_border (the 160-a2-1 adopted change, diag_c160_a2_1_facts.md R3).
 D3 the other gate-D plans (p5s02a, p5s01a, p5s01b, p5s01_in) compile equal to the before-list.
 W  only if D1+D2 PASS: the current compile_all() written to compile_before_c160a2.json (new file; old file md5 unchanged).
Usage: py tools/bench/diag_c160_f3_2.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


OLD = os.path.join(L.SIMD, "compile_before.json")
NEW = os.path.join(L.SIMD, "compile_before_c160a2.json")
KEY = "tools/bench/plan_ring_p5s02r_all.json"
old_md5 = L.md5(OLD)
before = L.jload(OLD)
now = L.compile_all()
plan = L.jload(os.path.join(HERE, "plan_ring_p5s02r_all.json"))
ids = [a.get("id") for a in plan["actions"]]
b_ops, a_ops = before[KEY]["ops"], now[KEY].get("ops") or []
print("FACT plan md5 before-list {0} now {1}; ops {2} -> {3}; error now {4}".format(
    before[KEY].get("md5"), now[KEY].get("md5"), len(b_ops), len(a_ops), now[KEY].get("error")), flush=True)


def brief(o):
    return {"kind": o.get("kind"), "acts": o.get("acts"), "ids": [ids[n - 1] for n in o.get("acts") or []],
            "variant": o.get("variant"), "route": o.get("route"), "mode": o.get("mode"), "case": o.get("case"),
            "out_act": o.get("out_act")}


diff = []
for i in range(max(len(b_ops), len(a_ops))):
    b = b_ops[i] if i < len(b_ops) else None
    a = a_ops[i] if i < len(a_ops) else None
    if a != b:
        diff.append((i, b, a))
        print("DIFF op {0}\n   before {1}\n   after  {2}".format(i, json.dumps(b, sort_keys=True), json.dumps(a, sort_keys=True)),
              flush=True)
        print("   brief  before {0}\n   brief  after  {1}".format(brief(b or {}), brief(a or {})), flush=True)
cp_b, cp_a = SX.checkpoint_ops(b_ops), SX.checkpoint_ops(a_ops)
print("FACT checkpoints before {0} after {1}".format(cp_b, cp_a), flush=True)
gate("D1 op count equal ({0} -> {1}) and checkpoint_ops equal".format(len(b_ops), len(a_ops)),
     len(b_ops) == len(a_ops) == 40 and cp_b == cp_a, {"cp_before": cp_b, "cp_after": cp_a})


def adopted(b, a):
    if not b or not a or b.get("acts") != a.get("acts"):
        return False
    tid = set(ids[n - 1] for n in a["acts"])
    return bool(tid & {"t_go", "t_ho"}) and b.get("kind") != "connect_term_uid" and a.get("kind") == "connect_term_uid" \
        and a.get("variant") == "register_end_case_border"


gate("D2 every differing op ({0}) is a t_go / t_ho group: same acts, before not connect_term_uid, after connect_term_uid "
     "register_end_case_border".format([d[0] for d in diff]),
     diff and all(adopted(b, a) for _i, b, a in diff), [(i, brief(b or {}), brief(a or {})) for i, b, a in diff])
others = ("plan_ring_p5s02a.json", "plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s01_in.json")
eq = dict((p, (before.get("tools/bench/" + p) or {}).get("ops") == (now.get("tools/bench/" + p) or {}).get("ops")
           and (now.get("tools/bench/" + p) or {}).get("ops") is not None) for p in others)
gate("D3 other gate-D plans compile equal to the before-list", all(eq.values()), eq)
nd = sorted(k for k in set(before) | set(now) if (before.get(k) or {}).get("ops") != (now.get(k) or {}).get("ops")
            or (before.get(k) or {}).get("error") != (now.get(k) or {}).get("error"))
print("FACT plans before {0} now {1}; entries whose ops/error differ: {2} {3}".format(len(before), len(now), len(nd), nd),
      flush=True)
arts = []
if all(ok for _l, ok in gates):
    if os.path.exists(NEW):
        gate("W new baseline absent before writing", False, NEW)
    else:
        with open(NEW, "w", encoding="utf-8") as f:
            json.dump(now, f, indent=0, sort_keys=True)
        print("FACT W written {0} {1} ({2} plans)".format(os.path.relpath(NEW, ROOT), L.md5(NEW), len(now)), flush=True)
        arts.append({"path": os.path.relpath(NEW, ROOT).replace("\\", "/"), "md5": L.md5(NEW)})
        gate("W new baseline written; compile_before.json md5 unchanged", L.md5(OLD) == old_md5, L.md5(OLD))
else:
    print("FACT W NOT written (a D gate failed: no re-baseline)", flush=True)
npass = sum(1 for _l, ok in gates if ok)
nfail = len(gates) - npass
print(protocol.result_line({"status": "PASS" if not nfail else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": next((l for l, ok in gates if not ok), None), "artefacts": arts}))
sys.exit(1 if nfail else 0)
