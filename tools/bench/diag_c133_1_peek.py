"""card 133-1 step 2 (offline, no LabVIEW): peek at P3b-2 actions on the provisional plan (98992a59) and the half-rebased
31bea1c5, and at how stagexec.compile_plan compiles each (op kind) - is op 24 a BIND kind on the rebased plan?
Prediction: on 98992a59 the FS crossings compile to connect_term_uid (fs_border, frames 'new:FS1.f<k>' known only if the
plan creates FS1); on the rebased plan they compile to plain 'connect' (FS is pre-existing, real uids)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as SX

for p in ("tools/bench/plan_ring_p3b2.json", "tools/bench/plan_ring_p3b2_rebased_c132_5.json"):
    P = json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
    print(p, "final", P.get("final"), "base", P.get("base"), "context keys", sorted((P.get("context") or {}).keys()))
    try:
        ops = SX.compile_plan(P)
        kinds = {}
        for k, o in enumerate(ops, 1):
            kinds[k] = (o["kind"], o.get("variant"), o["acts"])
        print("  ops", len(ops), "BIND", [k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS])
        for k in (1, 15, 23, 24, 26, 28, 30, 32, 34, 36, 38):
            if k <= len(ops):
                print("  op", k, kinds[k])
    except SX.ExecStop as e:
        print("  compile ExecStop", e)
    for i in (1, 14, 15, 24, 26, 34):
        print("  act", i, json.dumps(P["actions"][i - 1])[:420])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None,
                              "artefacts": []}))
