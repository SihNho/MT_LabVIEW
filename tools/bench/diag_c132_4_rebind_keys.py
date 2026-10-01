r"""diag_c132_4_rebind_keys - card 132-4: RECORD (not diagnose) the terminal-key signatures behind the --rebase refusal
'BINDING: the created objects differ' (stage_prerun.rebind :2906-2916) for the unmatched groups. Offline, read only.
PREDICTION: K1 the unmatched groups are exactly FlatSequenceInnerTunnel and Unbundler (as the refusal says); their sim and real
terminal-key tuples are printed side by side.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c132_4_rebind_keys.log -- py -u tools/bench/diag_c132_4_rebind_keys.py"""
import json, os, sys                                                                # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, vigraph as V                                                 # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(os.path.dirname(os.path.dirname(B)), p), encoding="utf-8"))   # noqa: E731
plan = J("tools/bench/plan_ring_p3b2.json")
base = plan["base"]
prov = J(base["path"]).get("terminals") or J(base["path"]).get("state", {}).get("terminals")
before = J("tools/bench/graph_ring_p3a_20261001_190155.json")["terminals"]
real = J("tools/bench/graph_ring_p3b1_20261002_073225.json")["terminals"]
print("  FACT  plan base {0} md5 {1} provisional {2}".format(base.get("path"), base.get("md5"), base.get("provisional")), flush=True)
tkey = lambda r: (r.get("term_class", ""), bool(r["is_source"]), r.get("term_name", ""))   # noqa: E731
sim_new, real_new, old_t = {}, {}, set(r["term_uid"] for r in before)
for r in prov:
    V.node_of(r) < 0 and sim_new.setdefault(V.node_of(r), []).append(r)                    # noqa: E701
for r in real:
    r["term_uid"] not in old_t and real_new.setdefault(V.node_of(r), []).append(r)       # noqa: E701
classes = set()
for nm, d in (("SIM", sim_new), ("REAL", real_new)):
    for u, rows in sorted(d.items()):
        c = V.node_class(rows[0])
        if c in ("FlatSequenceInnerTunnel", "Unbundler"):
            classes.add(c)
            print("  FACT  {0} {1} #{2}: {3}".format(nm, c, u, sorted(tkey(r) for r in rows)), flush=True)
ok = classes == {"FlatSequenceInnerTunnel", "Unbundler"}
print("{0}  K1 unmatched groups FSIT + Unbundler printed  {1}".format("PASS" if ok else "FAIL", sorted(classes)), flush=True)
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "K1")), flush=True)
sys.stdout.flush()
os._exit(0 if ok else 1)
