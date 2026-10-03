r"""prep_c142_p2_q1 - card 142-P2, read-only dump (OFFLINE, no LabVIEW). Prints v17's top-level keys, and every action that
belongs to S1 (G2 minus p4_or_w1) or S2 (G5's scalar core) or names one of their aliases, compactly, so v18 can be written
from the plan's own text (never re-typed). PREDICTION: v17 md5 e19d7e14; G2 has 20 actions, G5 27 (prep_c142_p1_subvi_table.md).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_p2_q1.log -- py -u tools/bench/prep_c142_p2_q1.py"""
import hashlib, json, os, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V17 = os.path.join(B, "plan_ring_p4_v17.json")
TAB = os.path.join(B, "prep_c142_p1_subvi_table.json")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


m = hashlib.md5(open(V17, "rb").read()).hexdigest()
gate("v17 md5", m == "e19d7e142fef66f9e118ae4061e9e718", m)
v = json.load(open(V17, encoding="utf-8"))
print("KEYS", sorted(v.keys()))
for k in sorted(v.keys()):
    if k != "actions":
        print("TOP", k, json.dumps(v[k])[:700])
tab = json.load(open(TAB, encoding="utf-8"))
print("TABKEYS", sorted(tab.keys()) if isinstance(tab, dict) else type(tab))
grp = {}
for g in (tab.get("groups") or []):
    grp[g.get("name") or g.get("id")] = g.get("actions")
print("GROUPS", dict((k, len(x or [])) for k, x in grp.items()))
S1 = ["p4_gt_last", "p4_f_min", "p4_sel_mask", "p4_k_max", "p4_k_max_found", "p4_amm", "p4_lt_found"]
S2 = ["p4_eq_seq", "p4_gt_n1", "p4_and", "p4_dec", "p4_sel_last", "p4_sel_disc", "p4_inc_disc"]
A = v["actions"]
alias = {}
for n, a in enumerate(A, 1):
    if a["id"] in S1 + S2:
        alias[a.get("as")] = a["id"]
print("ALIASES", alias)
for n, a in enumerate(A, 1):
    s = json.dumps(a)
    hit = a["id"] in S1 + S2 or any(("new:" + al + ".") in s or ("new:" + al + '"') in s for al in alias if al)
    if hit:
        print("ACT #{0} {1}".format(n, json.dumps(dict((k, x) for k, x in a.items() if k != "why"))))
        print("   why:", (a.get("why") or "")[:300])
gate("G2 20 / G5 27 in table", len(grp.get("G2") or []) == 20 and len(grp.get("G5") or []) == 27, dict((k, len(x or [])) for k, x in grp.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
