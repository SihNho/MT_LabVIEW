r"""prep_c142_p1_q1 - card 142-P1 (OFFLINE, read-only query, no LabVIEW, no COM). Dumps plan v17's actions compactly so the
decomposition table (pass 1) can be computed from the plan's own fields. Existing tools checked: prep_c141_p1_mk.py (the
v17/s02 maker), stagexec.compile_plan, stagesim - none prints a per-action wire table; this is a read-only listing.
PREDICTION CONTRACT: M0 v17 md5 == e19d7e14...; every action has id+op; p4_rp* count == 50; non-repair == 185.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_p1_q1.log -- py -u tools/bench/prep_c142_p1_q1.py"""
import collections, hashlib, json, os, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V17 = os.path.join(B, "plan_ring_p4_v17.json")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


m = hashlib.md5(open(V17, "rb").read()).hexdigest()
gate("M0 v17 md5", m == "e19d7e142fef66f9e118ae4061e9e718", m)
p = json.load(open(V17, encoding="utf-8"))
A = p["actions"]
print("TOP keys", sorted(p.keys()), "finalized keys", sorted((p.get("finalized") or {}).keys()))
print("OPS", dict(collections.Counter(a["op"] for a in A)))
keys = collections.defaultdict(set)
for a in A:
    keys[a["op"]].update(a.keys())
for k, v in keys.items():
    print("KEYS", k, sorted(v))
rp = [a for a in A if a["id"].startswith("p4_rp")]
gate("C counts p4_rp {0} non-repair {1}".format(len(rp), len(A) - len(rp)), len(rp) == 50 and len(A) - len(rp) == 185)
SKIP = ("why", "terminals")
for n, a in enumerate(A, 1):
    d = dict((k, v) for k, v in a.items() if k not in SKIP)
    print("A{0:03d} {1}".format(n, json.dumps(d, default=str)[:420]))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
