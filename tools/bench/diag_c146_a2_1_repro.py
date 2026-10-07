# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_repro - card 146-a3-1 (OFFLINE): reproduce the s05 Error List prediction 57 with the CURRENT tools/elrule.py
exactly as the pred was made (prep_c146_a1_3_pred.py:105-111: predict(st0, last, 58, made, extra_owner_states=(base,), subvis)),
and print per-class counts of the prediction and of the READ file (06a59001), plus the start/end rows of the base nodes
#5058 and #29843 and the s04 recorded file's per-class counts.
PREDICTION CONTRACT: predicted_total == 57; read item_count == 55.
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_repro.log -- py -u tools/bench/diag_c146_a2_1_repro.py"""
import collections, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
from tools import elrule as ELR  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


def textcls(x):
    t = "{0} {1}".format(x.get("raw", ""), x.get("detail", ""))
    c = ELR.item_class(t)
    if c:
        return c
    if "unwired or bad terminal" in t.lower():
        return "input:" + (x.get("raw", "").split(":")[0][:40] if ":" in x.get("raw", "") else x.get("raw", "")[:40])
    return "other:" + x.get("raw", "")[:60]


def rec(path):
    it = J(path).get("items") or []
    return len(it), collections.Counter(textcls(x) for x in it), it


p = J("tools/bench/plan_ring_p4_s05v18.json")
fz = p["finalized"]
bp = fz.get("base") or p.get("base") or {}
base = J(bp["path"])
sf = fz["step_files"]
st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
made = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - \
    set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
sv = ELR.subvis_from_plan(p, st0, last)
P = ELR.predict(st0, last, 58, made, extra_owner_states=(base,), subvis=sv)
print("FACT base {0}; steps {1} -> {2}; created {3}; subvis {4}".format(bp.get("path"), sf[0]["path"], sf[-1]["path"], sorted(made), sv), flush=True)
nb = collections.Counter(k[0] for k in P["new_items"])
cb = collections.Counter(k[0] for k in P["closed_items"])
print("PRED total {0}; new {1}; closed {2}; per-class new {3} closed {4}".format(P["predicted_total"], P["new_items"], P["closed_items"], dict(nb), dict(cb)), flush=True)
print("PRED open_at_start {0}".format(P["open_at_start"]), flush=True)
print("PRED open_at_end {0}".format(P["open_at_end"]), flush=True)
print("PRED detail_end {0}; uncertain base {1}; uncertain subvi {2}".format(P["detail_end"], P["uncertain_base_newly_unwired_inputs"], P["uncertain_subvi_terminals"]), flush=True)
gate("REPRO predicted_total == 57 (pred d083ff5f)", P["predicted_total"] == 57, P["predicted_total"])
n5, c5, it5 = rec("tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json")
n4, c4, it4 = rec("tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json")
print("READ s05 n {0} classes {1}".format(n5, dict(sorted(c5.items()))), flush=True)
print("READ s04 n {0} classes {1}".format(n4, dict(sorted(c4.items()))), flush=True)
diff = dict((k, c5.get(k, 0) - c4.get(k, 0)) for k in sorted(set(c4) | set(c5)) if c5.get(k, 0) != c4.get(k, 0))
print("READ s04->s05 per-class change {0}".format(diff), flush=True)
gate("READ item_count == 55", n5 == 55, n5)
for k in range(min(3, len(it5))):
    print("READ item {0}: {1}".format(k, json.dumps(it5[k])[:400]), flush=True)
for u in (5058, 29843):
    for nm, s in (("start", st0), ("end", last)):
        rs = [r for r in s.get("terminals") or [] if int(r["owner_uid"]) == u]
        print("ROWS #{0} {1}: {2}".format(u, nm, [(r.get("owner_class"), r.get("term_name"), r.get("term_class"), r.get("is_source"), r.get("wire_uid")) for r in rs]), flush=True)
# s04 prediction's open A items (carry candidates) as recorded in the s04 pred and the s05 sim sym map
print("SYM st0 (first 40) {0}".format(sorted((st0.get("sym") or {}).items())[:40]), flush=True)
json.dump({"pred": P, "read_s05": dict(c5), "read_s04": dict(c4)}, open(os.path.join(ROOT, "tools", "bench", "diag_c146_a2_1_repro.json"), "w", encoding="utf-8"), indent=1)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
