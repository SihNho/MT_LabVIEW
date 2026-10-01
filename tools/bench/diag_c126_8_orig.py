r"""diag_c126_8_orig - card 126-8 STEP 1 (OFFLINE, read-only): PD256(e) on the ORIGINAL's existing headless dump.
Source: tools/bench/main_vi_nodeterms.json (headless node-terminal read of `Min_Track N beads V6_ParallelLoop.vi`, the S1 source,
docs/d1-build-plan.md:31 md5 2a78e17c; nothing is opened here - the original's md5 is only hashed). Cross-checked against the S1
edge dump graph_s1_20260924.json (D1_s1_copy.vi) and the bed chain in diag_c126_8_probe.log / diag_c126_8_transrot.log.
Writes tools/bench/facts_c126_8_transrot.json.
PREDICTION: in the original #2626 Build Array takes element|1 <- #30117 Value and element|2 <- #4580 Value, appended array -> #376
(save trace.vi) 'current frame data array in'; #4580 Value's wire has exactly that one sink; #3097/#3160 locals feed only globals.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c126_8_orig.log -- py -u tools/bench/diag_c126_8_orig.py"""
import collections, hashlib, json, os, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P    # noqa: E402
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:900]), flush=True)


ORIG = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
om = hashlib.md5(open(ORIG, "rb").read()).hexdigest() if os.path.exists(ORIG) else None
D = json.load(open(os.path.join(B, "main_vi_nodeterms.json"), encoding="utf-8"))
gate("O0 dump is of the original; original md5 unchanged (2a78e17c...)", D["vi"].endswith("Min_Track N beads V6_ParallelLoop.vi")
     and om == "2a78e17c449cacdaf5da389818526859", (D["vi"], om))
node, byw = {}, collections.defaultdict(list)
for dk, dg in D["diagrams"].items():
    for nd in dg.get("nodes", []):
        node[nd["uid"]] = (dk, dg.get("owner"), nd)
        for t in nd.get("terms", []):
            if t.get("wire"):
                byw[t["wire"]].append((nd["uid"], t["name"], t["is_source"], t["i"], dk))
LAB = {}
try:
    L = json.load(open(os.path.join(B, "main_vi_node_labels.json"), encoding="utf-8"))
    for x in (L if isinstance(L, list) else L.get("nodes", L.get("labels", []))):
        if isinstance(x, dict) and "uid" in x:
            LAB[int(x["uid"])] = x.get("label") or x.get("name")
except Exception as e:  # noqa: BLE001
    print("labels unread:", e)


def terms(u):
    if u not in node:
        return None
    dk, ow, nd = node[u]
    return [(t["i"], t["name"], t["is_source"], t.get("wire"), [x for x in byw.get(t.get("wire"), []) if x[0] != u]) for t in nd["terms"]]


facts = {"schema": "facts/1", "card": "126-8", "original": {"path": ORIG, "md5": om, "dump": "tools/bench/main_vi_nodeterms.json"}}
for u in (2626, 30117, 4580, 3097, 3160, 376, 11608):
    tt = terms(u)
    print("ORIG #{0} label={1!r} diagram={2}".format(u, LAB.get(u), node[u][0] if u in node else None), flush=True)
    for r in tt or []:
        print("     ", r, flush=True)
    facts["#%d" % u] = {"label": LAB.get(u), "diagram": node[u][0] if u in node else None, "terms": tt}
t26 = terms(2626) or []
el = dict((r[0], r) for r in t26)
src_of = lambda r: [(x[0], x[1]) for x in r[4] if x[2]]  # noqa: E731
srcs = [(r[0], r[1], src_of(r)) for r in t26 if not r[2]]
print("ORIG #2626 inputs (index, name, source):", srcs, flush=True)
gate("O1 original #2626 Build Array: an input from #30117 Value and one from #4580 Value (trans/rot of the per-frame record)",
     any(s == [(30117, "Value")] for _i, _n, s in srcs) and any(s == [(4580, "Value")] for _i, _n, s in srcs), srcs)
out = [r for r in t26 if r[2]]
gate("O2 original #2626 appended array -> #376 'current frame data array in' (save trace.vi)",
     len(out) == 1 and [(x[0], x[1]) for x in out[0][4] if not x[2]] == [(376, "current frame data array in")], out)
r45 = [r for r in (terms(4580) or []) if r[1] == "Value"]
s45 = [(x[0], x[1]) for x in r45[0][4] if not x[2]] if r45 else None
gate("O3 original #4580 Value wire has a sink: exactly #2626", s45 == [(2626, "element")], (r45, s45))
r30 = [r for r in (terms(30117) or []) if r[1] == "Value"]
s30 = sorted(set((x[0], x[1]) for x in r30[0][4] if not x[2])) if r30 else None
print("ORIG #30117 Value sinks:", s30, flush=True)
gate("O4 original #30117 Value sinks include #2626 element", bool(s30) and (2626, "element") in s30, s30)
facts["answers"] = {
    "record_build": "#2626 Build Array -> #376 save trace.vi 'current frame data array in' (per #637 iteration)",
    "inputs_2626": srcs, "sinks_30117_value": s30, "sinks_4580_value": s45,
    "first_bed_without_4580_sink": "D1_l2_b1_20260927_193100.vi (graph_l2b1_20260927.json); last with it: D1_l2_a3_20260927_151224.vi (graph_l2a3_bed_20260927.json)",
    "held_as": "plan_ring_p3a.json open_rows: (2626,'element') 'carried from R2: QRT (PD182(c)/D5)', (2626,'array') licensed rename (plan_l2b1_licence.json)"}
json.dump(facts, open(os.path.join(B, "facts_c126_8_transrot.json"), "w", encoding="utf-8"), indent=1, default=str)
print("  FACT WROTE facts_c126_8_transrot.json md5", hashlib.md5(open(os.path.join(B, "facts_c126_8_transrot.json"), "rb").read()).hexdigest(), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
