# ---
# labview: none
# hardware: none
# ---
r"""selftest_c153_compdiff_poskey - card 153-b2-1 (gate-fp fp-70, docs/d1/ring-p4d.md PD370(d)): vigraph.computation_diff keys sinks and
sources by POSITION (node, index, term class, is_source), not by name. PRIOR ART: selftest_vigraph_frame_80.py (fixtures = mutated copies of a
stored terminal table, offline), selftest_t6_poskey.py (the position key in stagekit). Fixture = the stored s09 graph read
tools/bench/graph_ring_p4s09_20261009_062044.json (md5 22f967b5), default mode; one computation node whose LAST row is a wired, sourced sink.
PREDICTION:
  C0 identity A vs A: 0 rows, 0 renames;
  C1 rename-only (that sink's term_name changed): 0 rows, its node in `renames`;
  C2 rename of the SOURCE terminal feeding it (name only): 0 rows;
  C3 real removal (the sink row deleted): exactly 1 row, sink = A's key, after None;
  C4 real new terminal (a sink row appended on the same node, same wire): exactly 1 row, before None;
  C5 unwired (the sink's wire_uid 0): exactly 1 row, after [] ;
  C6 row shape unchanged: keys node/class/sink/before/after, sink a 'node|class|name|ordinal' string.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c153_compdiff_poskey.log -- py -u tools/bench/selftest_c153_compdiff_poskey.py"""
import copy, hashlib, json, os, sys                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import vigraph as V, protocol as PR                                                 # noqa: E401,E402
N = {"pass": 0, "fail": 0, "first": None}
GF = os.path.join(HERE, "graph_ring_p4s09_20261009_062044.json")


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    if not ok and N["first"] is None:
        N["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(detail, default=str)[:700]), flush=True)


GR = json.load(open(GF, encoding="utf-8"))
T0, OBJS = V.dedupe_rows(GR["terminals"])[0], GR.get("objs")
build = lambda rows: V.build4(rows, OBJS)                                           # noqa: E731
GA = build(T0)
pick = None
for n in sorted(GA["by_node"]):
    rs = GA["by_node"][n]
    last = rs[-1]
    if V.is_scheduling(GA, n) or GA["cls"].get(n) == V.FP_CLASS or len(rs) < 2:
        continue
    if not last["is_source"] and last["wire_uid"] and last["term_name"] and V.effective_sources(GA, last["key"]):
        pick = last
        break
gate("F fixture: graph md5 22f967b5, a computation node with a wired sourced last sink", hashlib.md5(open(GF, "rb").read()).hexdigest()
     == "22f967b5" + hashlib.md5(open(GF, "rb").read()).hexdigest()[8:] and pick is not None, pick and {k: pick[k] for k in ("node", "key", "wire_uid")})
U, W = pick["term_uid"], pick["wire_uid"]
src = next(r for r in T0 if r["wire_uid"] == W and r["is_source"])


def mut(fn):
    rows = [copy.deepcopy(r) for r in T0]
    fn(rows)
    return V.computation_diff(GA, build(rows))


cd = V.computation_diff(GA, GA)
gate("C0 identity: 0 rows, 0 renames", not cd["rows"] and not cd["renames"], len(cd["rows"]))
cd = mut(lambda rows: [r.update(term_name=r["term_name"] + " RENAMED") for r in rows if r["term_uid"] == U])
gate("C1 rename-only sink: 0 rows; node {0} in renames".format(pick["node"]), not cd["rows"] and any(x["node"] == pick["node"] for x in cd["renames"]),
     {"rows": cd["rows"][:3], "renames": cd["renames"][:3]})
cd = mut(lambda rows: [r.update(term_name=(r["term_name"] or "") + " RENAMED") for r in rows if r["term_uid"] == src["term_uid"]])
gate("C2 rename-only SOURCE #{0}: 0 rows".format(src["term_uid"]), not cd["rows"], cd["rows"][:3])
cd = mut(lambda rows: rows.__setitem__(slice(None), [r for r in rows if r["term_uid"] != U]))
gate("C3 real removal: exactly 1 row, sink == A's key, after None", len(cd["rows"]) == 1 and cd["rows"][0]["sink"] == pick["key"]
     and cd["rows"][0]["after"] is None, cd["rows"][:3])
NU = max(r["term_uid"] for r in T0) + 1
cd = mut(lambda rows: rows.insert(rows.index(next(r for r in rows if r["term_uid"] == U)) + 1, dict(copy.deepcopy(pick), term_uid=NU, term_name="extra in")))
gate("C4 real new terminal: exactly 1 row, before None", len(cd["rows"]) == 1 and cd["rows"][0]["before"] is None, cd["rows"][:3])
cd = mut(lambda rows: [r.update(wire_uid=0) for r in rows if r["term_uid"] == U])
gate("C5 unwired: exactly 1 row, after []", len(cd["rows"]) == 1 and cd["rows"][0]["after"] == [], cd["rows"][:3])
r0 = cd["rows"][0] if cd["rows"] else {}
gate("C6 row shape node/class/sink/before/after, sink 'node|class|name|ordinal'", set(r0) == {"node", "class", "sink", "before", "after"}
     and isinstance(r0.get("sink"), str) and V.key_parts(r0["sink"])[0] == pick["node"], r0)
print("=== selftest_c153_compdiff_poskey: {0} pass / {1} fail".format(N["pass"], N["fail"]), flush=True)
print(PR.result_line(PR.make_result(N["pass"], N["fail"], N["first"])), flush=True)
sys.exit(1 if N["fail"] else 0)
