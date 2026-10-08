# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a2_2_measure - card 150-a2-2 FIRST MEASURE, OFFLINE, read-only (writes nothing but its log).
Reuses selftest_rebind_c150.inputs()-style loading (stage_prerun._terms / load_creation_map / plan_named_uids, :4241-4260).
For the s06->s07 inputs (plan_ring_p4_s07v18_prov148.json onto graph_ring_p4s06_20261008_192149.json): every REAL row whose
150-a2-1 key (uid, owner, term_class, is_source) is NOT in N's base `before` but whose (uid, owner) IS - print the before row(s)
and the real row and the set of fields that differ. Also every real LoopTunnel row in that set, node by node.
PREDICTION CONTRACT: 3 LoopTunnel terminals (+ t9505 #9503) appear; for each, the ONLY differing field besides term_name /
wire fields is is_source. Anything else differing => STOP (card rule)."""
import collections, json, os, sys                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP, vigraph as V                                    # noqa: E401,E402
ab = lambda p: p if os.path.isabs(p) else os.path.join(R, p)                              # noqa: E731
plan = json.load(open(os.path.join(B, "plan_ring_p4_s07v18_prov148.json"), encoding="utf-8"))
so = plan["base"]["sim_of"]
dn = json.load(open(ab(so["plan"]), encoding="utf-8"))
bn = (dn.get("finalized") or {}).get("base") or dn.get("base")
_gb, before = SP._terms(ab(bn["path"]))
_gr, real = SP._terms(os.path.join(B, "graph_ring_p4s06_20261008_192149.json"))
before, _ = V.dedupe_rows(before)
real, _ = V.dedupe_rows(real)
k4 = lambda r: (r["term_uid"], r.get("owner_uid"), r.get("term_class", ""), bool(r["is_source"]))   # noqa: E731
k2 = lambda r: (r["term_uid"], r.get("owner_uid"))                                         # noqa: E731
old4 = set(k4(r) for r in before)
byk2 = collections.defaultdict(list)
for r in before:
    byk2[k2(r)].append(r)
IGN = {"wire_uid", "term_name"}
hits, other = [], 0
for r in real:
    if k4(r) in old4 or k2(r) not in byk2:
        continue
    for b in byk2[k2(r)]:
        diff = sorted(f for f in set(b) | set(r) if f not in IGN and b.get(f) != r.get(f))
        hits.append((r, b, diff))
        print("ROW t{0} #{1} class {2} node {3}: differs {4} | before {5} | real {6}".format(
            r["term_uid"], r.get("owner_uid"), r.get("term_class"), V.node_class(r),
            diff, dict((f, b.get(f)) for f in diff + ["term_name"]), dict((f, r.get(f)) for f in diff + ["term_name"])), flush=True)
        if set(diff) - {"is_source"}:
            other += 1
lt = sorted(set(r.get("owner_uid") for r, _b, _d in hits if V.node_class(r) == "LoopTunnel"))
print("LOOPTUNNEL owners among them: {0}; rows {1}; non-is_source diffs {2}".format(lt, len(hits), other), flush=True)
fails = (0 if other == 0 else 1)
print(P.result_line(P.make_result(1 - fails, fails, None if not fails else "attribute other than is_source differs", [])), flush=True)
