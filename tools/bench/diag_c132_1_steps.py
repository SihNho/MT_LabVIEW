r"""diag_c132_1_steps - card 132-1: per sim step of a stage (argv[1] = tools/bench/sim/<stage>), the action, effect.how,
effect.tunnels and the NEW tunnel-owned rows (owner_class, term_class, is_source, name). Offline, read-only."""
import glob, json, os, sys                                                         # noqa: E401
d = sys.argv[1]
fs = sorted(glob.glob(os.path.join(d, "step_*.json")))
prev = None
for f in fs:
    s = json.load(open(f, encoding="utf-8"))
    t = s["state"]["terminals"]
    if prev is not None:
        seen = set(int(r["term_uid"]) for r in prev)
        new = [(r["owner_uid"], r["owner_class"], r["term_class"], bool(r["is_source"]), r["term_name"]) for r in t
               if int(r["term_uid"]) not in seen and str(r.get("owner_class")).endswith("Tunnel")]
        e = s.get("effect") or {}
        a = s.get("action") or {}
        print("STEP {0:02d} {1} {2} how={3} tunnels={4} newtun={5}".format(s["n"], a.get("op"), a.get("id"), e.get("how"),
                                                                          e.get("tunnels"), new))
    prev = t
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
