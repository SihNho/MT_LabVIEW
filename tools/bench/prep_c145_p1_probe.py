# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_p1_probe - card 145-a1-P1 (OFFLINE, read-only, no LabVIEW). COPIED from prep_c144_p1_probe.py (s03v18 -> s04v18, op 78 -> 97).
Reads plan_ring_p4_s04v18.json's finalized block and its END step state's sym/neg, and lists the `new:` symbols referenced by v18 actions
after s04's last op with the session that creates them (s01 / s02 / s03 / s04 / later); for each s01..s03 symbol, the value the s04v18
(rebased) plan holds in the same field of the same action (how the rebase bound it). PREDICTION CONTRACT: P1 inputs on the card md5;
P2 s04v18 last step file has a state with 'sym'; facts printed only.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c145_p1_probe.log -- py -u tools/bench/prep_c145_p1_probe.py"""
import collections, hashlib, json, os, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                     # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V18, S04, S03, S02, S01 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s04v18.json", "plan_ring_p4_s03v18.json",
                                                         "plan_ring_p4_s02v18.json", "plan_ring_p4_s01.json"))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


gate("P1 inputs on the card md5", md5(V18) == "2ea6cafa7d368dc7a054346d398daa3e" and md5(S04) == "9ff46b0ece1f238c831d7786616c4f05", (md5(V18), md5(S04)))
s04, v18, s03, s02, s01 = J(S04), J(V18), J(S03), J(S02), J(S01)
fz = s04.get("finalized") or {}
sf = fz.get("step_files") or []
print("FACT step_files", len(sf), "first", sf[:1], "last", sf[-1:], "| on-disk md5 last", sf and md5(os.path.join(ROOT, sf[-1]["path"])), flush=True)
last = J(sf[-1]["path"]) if sf else {}
st = last.get("state") or {}
gate("P2 last step file has a state with sym", "sym" in st, sorted(last)[:20])
print("FACT END state keys", sorted(st), flush=True)
print("FACT END sym", json.dumps(st.get("sym")), "| neg", st.get("neg"), "| vi", st.get("vi"), "| md5", st.get("md5"), flush=True)
st0 = J(sf[0]["path"])["state"]
print("FACT step0 sym", json.dumps(st0.get("sym")), "| neg", st0.get("neg"), flush=True)
print("FACT s04 open_rows", len(s04.get("open_rows") or []), "base", s04.get("base"), flush=True)
A = v18["actions"]
OPS = SX.compile_plan(v18)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
maker = {}
for n, a in enumerate(A, 1):
    if a.get("as"):
        maker["new:" + a["as"]] = (act2op[n], a["id"])
ids = [a["id"] for a in A]
prev = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]] + [x["id"] for x in s04["actions"]]
S4N = max(act2op[n] for n in range(1, len(prev) + 1))
S3N = max(act2op[n] for n in range(1, len(prev) - len(s04["actions"]) + 1))
print("FACT v18 actions", len(A), "ops", len(OPS), "| s01..s04 ids", len(prev), "== v18 prefix", ids[:len(prev)] == prev, "| last op of s03", S3N, "s04", S4N, flush=True)
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
s04by = dict((x["id"], x) for x in s04["actions"])
refs = collections.defaultdict(set)
bound = collections.defaultdict(set)
for n, a in enumerate(A, 1):
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        m = maker.get(root) or maker.get(root[:-1])
        sess = "s01" if m and m[0] <= 24 else "s02" if m and m[0] <= 58 else "s03" if m and m[0] <= S3N else "s04" if m and m[0] <= S4N else "later" if m else "unknown"
        if S3N < act2op[n] <= S4N and sess in ("s01", "s02", "s03") and a["id"] in s04by:
            bound[s].add(json.dumps(s04by[a["id"]].get(f)))
        if act2op[n] <= S4N:
            continue
        refs[sess].add((s, m and m[0], a["id"], f))
for k in sorted(refs):
    print("FACT refs from ops>{0} to symbols made in".format(S4N), k, len(refs[k]), sorted(refs[k], key=str)[:80], flush=True)
for s in sorted(bound):
    print("FACT s04 rebased binding of", s, "->", sorted(bound[s]), flush=True)
for k in range(S4N - 2, min(len(OPS), S4N + 45) + 1):
    o = OPS[k - 1]
    print("OP {0} {1} acts {2}".format(k, o["kind"], [(A[n - 1]["id"], A[n - 1].get("of")) for n in o["acts"]]), flush=True)
print("FACT kinds of ops {0}..".format(S4N + 1), dict(collections.Counter(o["kind"] for o in OPS[S4N:])), "BIND_KINDS", sorted(SX.BIND_KINDS), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
