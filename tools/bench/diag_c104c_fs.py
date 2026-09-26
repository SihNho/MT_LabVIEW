"""card 104-3 follow-up (OFFLINE, read-only): the fs-pair input of each side. F = stagesim.base_state fs_pairs (stagesim.py:206,
from the plan base graph; plan context has no fs_pairs_wiki, :211) vs E = WIKI fs_tunnel_pairs (stage_d1_disp.py:50); base graph
identity; per missing row the E==S1 flag from facts_c104c_e3.json. Prediction: unknown (measurement)."""
import json
import os
import sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import protocol  # noqa: E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))  # noqa: E731
P = J("tools/bench/sim/disp/plan_disp.json")
B = J(P["base"]["path"])
W = J("docs/wiki/subvi", P["context"]["s1_key"] + ".json")
F = J("tools/bench/facts_c104c_e3.json")
k = lambda p: json.dumps(p, sort_keys=True)  # noqa: E731
fb, fw = B.get("fs_tunnel_pairs") or [], W.get("fs_tunnel_pairs") or []
print("base graph", P["base"]["path"], "vi", B.get("vi"), "md5", B.get("md5"), "keys", sorted(B.keys())[:20])
print("wiki", P["context"]["s1_key"], "vi", W.get("vi") or W.get("path"), "md5", W.get("md5"))
print("fs pairs base", len(fb), "wiki", len(fw), "type", type(fb).__name__, type(fw).__name__)
sb, sw = set(map(k, fb)), set(map(k, fw))
print("only_base", len(sb - sw), sorted(sb - sw)[:4])
print("only_wiki", len(sw - sb), sorted(sw - sb)[:4])
print("sample base", k(fb[0]) if fb else None)
print("sample wiki", k(fw[0]) if fw else None)
for r in F["rows"]:
    print("ROWFLAG", r["node"], repr(r["term"]), "E_eq_S1", r["E_eq_S1"], "in_E_added", r["in_E_added"], "in_E_removed", r["in_E_removed"],
          "F_after-before", sorted(set(x["key"] for x in r["F_after_sim"]) - set(x["key"] for x in r["F_before_S1"])),
          "F_before-after", sorted(set(x["key"] for x in r["F_before_S1"]) - set(x["key"] for x in r["F_after_sim"])))
print(protocol.result_line(protocol.make_result(1, 0, None)))
