"""card 131-1 Part A helper (read-only): the tunnels the simulator created at P3b-1 crossing steps 16/20/22/24/26
(tools/bench/sim/ring_p3b1/step_NN_wire.json, plan 6934a0ed) and their face names = what the pin3 binder compared against.
PREDICTION: steps 20/22 FSOT '' ; 24 FSOT+Selector 'current image number'; 26 FSOT+Selector ''."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim", "ring_p3b1")


def find(o, key):
    if isinstance(o, dict):
        if key in o:
            return o[key]
        for v in o.values():
            r = find(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, key)
            if r is not None:
                return r
    return None


n = 0
for k in (16, 20, 22, 24, 26):
    fn = [f for f in os.listdir(D) if f.startswith("step_{0:02d}_".format(k))][0]
    j = json.load(open(os.path.join(D, fn), encoding="utf-8"))
    eff = find(j, "effect") or {}
    print("STEP", k, fn, "how", eff.get("how"), "variant", eff.get("variant"), "tunnels", eff.get("tunnels") or eff.get("tunnel"),
          "src", eff.get("src_term_uid"), "recreated", eff.get("recreated_from"))
    tl = eff.get("tunnels") or ([eff["tunnel"]] if eff.get("tunnel") else [])
    terms = find(j, "terminals") or []
    for r in terms:
        if r.get("owner_uid") in tl:
            n += 1
            print("   FACE", r["owner_uid"], r["owner_class"], r["term_class"], r["is_source"], repr(r["term_name"]), r["frame_diagram"])
print(protocol.result_line(protocol.make_result(1 if n else 0, 0 if n else 1, None if n else "no faces")))
